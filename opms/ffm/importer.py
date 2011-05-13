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
import simplejson

from django.template.defaultfilters import slugify

from .models import Feed, Item, File

logger = logging.getLogger(__name__)

def oxpoints_lookup(unit_code):
    if unit_code == 'smith':
        unit_code = 'smth'
    result = simplejson.load(urllib.urlopen('http://oxpoints.oucs.ox.ac.uk/oucs:%s.json' % unit_code))
    return result[0]['uri'].split('/')[-1]

class Namespace(object):
    def __init__(self, ns):
        self.ns = ns
    def __call__(self, local):
        return '{%s}%s' % (self.ns, local)

class RSSImporter(object):
    @property
    def PODCAST_ATTRS(self):
        atom = self.atom
        return (
            ('guid', ('guid', atom('id'),)),
            ('title', ('title', atom('title'),)),
            ('publish_date', ('pubDate', atom('published'),)),
            ('description', ('description', atom('summary'),)),
        )

    def __init__(self, podcasts, service, medium=None):
        self.podcasts = podcasts
        self._service = service
        self.medium = medium
    
    @property
    def atom(self):
        return Namespace('http://www.w3.org/2005/Atom')

    def import_data(self, metadata, output):
        for slug, url in self.podcasts:
            podcast, url = Podcast.objects.get_or_create(
                provider=self._service,
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

        xml = etree.parse(urllib.urlopen(podcast.source_url)).getroot()

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
        logo_url = logo.text
        if logo_url is not None:
            item, created = Item.objects.get_or_create(guid=logo_url,
                                                       defaults={
                                                        'owning_unit': podcast.owning_unit,
                                                       })
            if created:
                item.save()
            logo, created = File.objects.get_or_create(url=logo_url,
                                                       item = item,
                                                       function='FeedArt')
            if created:
                logo.save()
            podcast.feedart = logo
        else:
            podcast.feedart = None
        
        ids = []
        for item in xml.findall('.//channel/item') or xml.findall(atom('entry')):
            files = []
            id = gct(item, ('guid', atom('id'),))
            if not id:
                continue
            
            try:
                podcast_item, created = Item.objects.get_or_create(guid=id,
                                                                   owning_unit=podcast.owning_unit)
            except Item.MultipleObjectsReturned:
                Item.objects.filter(guid=id).delete()
                podcast_item, created = Item.objects.get_or_create(guid=id,
                                                                   owning_unit=podcast.owning_unit)
            
            require_save = False
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
                podcast_enc, updated = File.objects.get_or_create(item=podcast_item, url=url)
                try:
                    podcast_enc.size = int(attrib['length']) 
                except ValueError:
                    podcast_enc.size = None
                podcast_enc.mimetype = attrib['type']
                podcast_enc.save()
                enc_urls.append(url)
            
            if len(enc_urls) == 0:
                enc = File().save()
                enc_link = FileInFeed(feed=podcast, file=enc).save()
            
            ids.append( id )

        #podcast.most_recent_item_date = max(i.published_date for i in PodcastItem.objects.filter(podcast=podcast))
        podcast.save()

class OPMLImporter(RSSImporter):
    def __init__(self, 
                 url = 'http://rss.oucs.ox.ac.uk/metafeeds/podcastingnewsfeeds.opml',
                 rss_re = r'http://rss.oucs.ox.ac.uk/(.+-(.+?))/rss20.xml',
                 service='oxpoints'):
        self.url = url
        self.medium = None
        self.rss_re = re.compile(rss_re)
        self._category = None
        self._service = service

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
        slug = self.extract_slug(attrib['xmlUrl'])
        podcast, created = Feed.objects.get_or_create(
            source_service=self._service,
            source_url=attrib['xmlUrl'],
            owning_unit = oxpoints_lookup(slug.split('/')[0]))
        
        podcast.slug = slug
        podcast.save()
        
        self.update_podcast(podcast)

    def import_data(self):
        
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
                    print "Update of podcast %r failed." % outline.attrib['xmlUrl']
                    traceback.print_exc()
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
                            print "Update of podcast %r failed." % outline.attrib['xmlUrl']
                            traceback.print_exc()
                            if not failure_logged:
                                logger.exception("Update of podcast %r failed.", outline.attrib['xmlUrl'])
                                failure_logged = True
                self._category = None

        for podcast in Feed.objects.filter(source_service=self._service):
            if not podcast.source_url in rss_urls:
                podcast.delete()
