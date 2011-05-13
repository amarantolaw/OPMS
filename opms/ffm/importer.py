import re
import urllib
import random
import email
from lxml import etree
from xml.etree import ElementTree as ET
from datetime import datetime
import dateutil.parser
import logging
import traceback

from django.template.defaultfilters import slugify

from .models import Podcast, PodcastItem, PodcastEnclosure, PodcastCategory

logger = logging.getLogger(__name__)

class Namespace(object):
    def __init__(self, ns):
        self.ns = ns
    def __call__(self, local):
        return '{%s}%s' % (self.ns, local)

class RSSPodcastsProvider(object):
    @property
    def PODCAST_ATTRS(self):
        atom = self.atom
        return (
            ('guid', ('guid', atom('id'),)),
            ('title', ('title', atom('title'),)),
            ('author', ('{itunes:}author',)),
            ('duration', ('{itunes:}duration',)),
            ('published_date', ('pubDate', atom('published'),)),
            ('description', ('description', atom('summary'),)),
    #       ('itunesu_code', '{itunesu:}code'),
        )

    def __init__(self, podcasts, medium=None):
        self.podcasts = podcasts
        self.medium = medium
    
    @property
    def atom(self):
        return Namespace('http://www.w3.org/2005/Atom')

    def import_data(self, metadata, output):
        for slug, url in self.podcasts:
            podcast, url = Podcast.objects.get_or_create(
                provider=__name__,
                rss_url=url,
                defaults={'slug': slug})
            if self.medium: 
                podcast.medium = self.medium
                
            podcast.slug = slug
            self.update_podcast(podcast)
            
    def determine_license(self, o):
        license = o.find('{http://purl.org/dc/terms/}license') or \
                  o.find('{http://backend.userland.com/creativeCommonsRssModule}license')
        
        return getattr(license, 'text', None)
        
    def update_podcast(self, podcast):
        atom = self.atom
        def gct(node, names):
            for name in names:
                if node.find(name) is None:
                    continue
                value = node.find(name).text
                if name == 'pubDate':
                    value = datetime.fromtimestamp(
                        email.utils.mktime_tz(
                            email.utils.parsedate_tz(value)))
                elif name == atom('published'):
                    value = dateutil.parser.parse(value)
                elif name == '{itunes:}duration':
                    value = int(value)
                return value
            return None

        xml = etree.parse(urllib.urlopen(podcast.rss_url)).getroot()

        try:
            podcast.title = xml.find('.//channel/title').text
            podcast.description = xml.find('.//channel/description').text
        except AttributeError:
            podcast.title = xml.find(atom('title')).text
            podcast.description = xml.find(atom('subtitle')).text
        
        podcast.license = self.determine_license(xml.find('.//channel'))
        if self.medium is not None:
            podcast.medium = medium

        logo = xml.find('.//channel/image/url')
        podcast.logo = logo.text if logo is not None else None

        ids = []
        for item in xml.findall('.//channel/item') or xml.findall(atom('entry')):
            id = gct(item, ('guid', atom('id'),))
            if not id:
                continue
            
            try:
                podcast_item, created = PodcastItem.objects.get_or_create(podcast=podcast, guid=id)
            except PodcastItem.MultipleObjectsReturned:
                PodcastItem.objects.filter(podcast=podcast, guid=id).delete()
                podcast_item, created = PodcastItem.objects.get_or_create(podcast=podcast, guid=id)

            old_order = podcast_item.order
            try:
                podcast_item.order = int(item.find('{http://ns.ox.ac.uk/namespaces/oxitems/TopDownloads}position').text)
            except (AttributeError, TypeError):
                pass

            require_save = old_order != podcast_item.order
            for attr, x_attrs in self.PODCAST_ATTRS:
                if getattr(podcast_item, attr) != gct(item, x_attrs):
                    setattr(podcast_item, attr, gct(item, x_attrs))
                    require_save = True
            license = self.determine_license(item)
            if require_save or podcast_item.license != license:
                podcast_item.license = license
                podcast_item.save()

            enc_urls = []
            for enc in item.findall('enclosure') or item.findall(atom('link')):
                attrib = enc.attrib
                url = attrib.get('url', attrib.get('href'))
                podcast_enc, updated = PodcastEnclosure.objects.get_or_create(podcast_item=podcast_item, url=url)
                try:
                    podcast_enc.length = int(attrib['length']) 
                except ValueError:
                    podcast_enc.length = None
                podcast_enc.mimetype = attrib['type']
                podcast_enc.save()
                enc_urls.append(url)

            encs = PodcastEnclosure.objects.filter(podcast_item = podcast_item)
            for enc in encs:
                if not enc.url in enc_urls:
                    enc.delete()

            ids.append( id )

        for podcast_item in PodcastItem.objects.filter(podcast=podcast):
            if not podcast_item.guid in ids:
                podcast_item.podcastenclosure_set.all().delete()
                podcast_item.delete()

        #podcast.most_recent_item_date = max(i.published_date for i in PodcastItem.objects.filter(podcast=podcast))
        podcast.save()

class OPMLPodcastsProvider(RSSPodcastsProvider):
    def __init__(self, 
                 url = 'http://rss.oucs.ox.ac.uk/metafeeds/podcastingnewsfeeds.opml',
                 rss_re = r'http://rss.oucs.ox.ac.uk/(.+-(.+?))/rss20.xml'):
        self.url = url
        self.medium = None
        self.rss_re = re.compile(rss_re)
        self._category = None

    CATEGORY_ORDERS = {}

    CATEGORY_RE = re.compile('/([^\/]+)/([^,]+)')
    
    def extract_slug(self, url):
        match_groups = self.rss_re.match(url).groups()
        return match_groups[0]
    
    def extract_medium(self, url):
        # There are four podcast feed relics that existed before the
        # -audio / -video convention was enforced. These need to be
        # hard-coded as being audio feeds.
        match_groups = self.rss_re.match(url).groups()
        medium = {
            'engfac/podcasts-medieval': 'audio',
            'oucs/ww1-podcasts': 'audio',
            'philfac/uehiro-podcasts': 'audio',
            'offices/undergrad-podcasts': 'audio',
        }.get(self.extract_slug(url), match_groups[1])
        return medium
    
    def decode_category(self, attrib):
        category = attrib['category']
        category = dict(self.CATEGORY_RE.match(s).groups() for s in category.split(','))
        slug, name = category['division_code'], category['division_name']
        name = urllib.unquote(name.replace('+', ' '))

        podcast_category, created = PodcastCategory.objects.get_or_create(slug=slug,name=name)

        try:
            podcast_category.order = self.CATEGORY_ORDERS[slug]
        except KeyError:
            self.CATEGORY_ORDERS[slug] = len(self.CATEGORY_ORDERS)
            podcast_category.order = self.CATEGORY_ORDERS[slug]

        podcast_category.save()
        return podcast_category

    def parse_outline(self, outline):
        attrib = outline.attrib
        podcast, created = Podcast.objects.get_or_create(
            provider=__name__,
            rss_url=attrib['xmlUrl'])
        
        podcast.medium = self.extract_medium(attrib['xmlUrl'])
        podcast.category = self.decode_category(attrib)
        podcast.slug = self.extract_slug(attrib['xmlUrl'])
        
        self.update_podcast(podcast)

    def import_data(self, metadata, output):
        
        self._category = None

        xml = ET.parse(urllib.urlopen(self.url))

        rss_urls = []

        podcast_elems = xml.findall('.//body/outline')

        failure_logged = False

        for outline in podcast_elems:
            if 'xmlUrl' in outline.attrib:
                try:
                    self.parse_outline(outline)
                    rss_urls.append(outline.attrib['xmlUrl'])
                except Exception, e:
                    output.write("Update of podcast %r failed." % outline.attrib['xmlUrl'])
                    traceback.print_exc(file=output)
                    if not failure_logged:
                        logger.exception("Update of podcast %r failed.", outline.attrib['xmlUrl'])
                        failure_logged = True
            else:
                self._category = outline.attrib['text']
                # Assume this is an outline which contains other outlines
                for outline in outline.findall('./outline'):
                    if 'xmlUrl' in outline.attrib:
                        try:
                            self.parse_outline(outline)
                            rss_urls.append(outline.attrib['xmlUrl'])
                        except Exception, e:
                            output.write("Update of podcast %r failed." % outline.attrib['xmlUrl'])
                            traceback.print_exc(file=output)
                            if not failure_logged:
                                logger.exception("Update of podcast %r failed.", outline.attrib['xmlUrl'])
                                failure_logged = True
                self._category = None

        for podcast in Podcast.objects.filter(provider=__name__):
            if not podcast.rss_url in rss_urls:
                podcast.delete()
        
        return metadata
