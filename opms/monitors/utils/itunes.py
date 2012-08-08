from __future__ import print_function
import time
import random
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.utils.encoding import smart_unicode
import urllib2
import plistlib
from xml.parsers import expat
from lxml import etree, html
from lxml.html.clean import *
from dateutil.parser import *

import settings


#from BeautifulSoup import BeautifulSoup

# First, Apple-store-front is sensitive to use of comma to separate values
# Default language code appears to be 0, which returns XHTML. Apart from on homepage which gives a redirect plist
# As does: 5,6,7,12 (The iTunes App default from Wireshark data), 15-20
# 1 = XML data view
# 2 = Plist data. iOS iPhone and iPod Touch VIEW!
# 3,10 = Request could not be completed (Errors)... yet Lang 3 on homepage gave useful plist view, but fails for Top listings
# 4 = ??? Looks like 2...
# 8,11,14 = HTML 3.2 page with a redirecting to iTunes Store content
# 9 = Mostly HTML, iPad display version, content hard to view
# 13 = XHTML page, but much much shorter than the rest. Suggest it simulates iOS 5 styling. TBD
# [12,1,2]

def get_page(url, APPLE_STORE_LANGUAGE = 1, hurry = False):
    if settings.WAIT_GET and not hurry:
        time.sleep(random.random() * 5)
    USER_AGENT = 'iTunes/10.5.1 (Macintosh; Intel Mac OS X 10.6.8) AppleWebKit/534.51.22'
    APPLE_STORE_FRONT = '143444'
    APPLE_TZ = '0'
    ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    HOST = 'itunes.apple.com'
    ACCEPT_LANGUAGE = 'en-us, en;q=0.50'
#    print("Requesting " + url)
    request = urllib2.Request(url)
    request.add_header('User-Agent', USER_AGENT)
    request.add_header('X-Apple-Store-Front','%s,%s' % (APPLE_STORE_FRONT, APPLE_STORE_LANGUAGE))
    request.add_header('X-Apple-Tz',APPLE_TZ)
    request.add_header('Accept', ACCEPT)
    request.add_header('Accept-Language', ACCEPT_LANGUAGE)
    request.add_header('Host',HOST)
    opener = urllib2.build_opener()
    data = opener.open(request).read()
    #print "g_p:1"
    if data.find('<!DOCTYPE plist PUBLIC') > 0 and data.find('<!DOCTYPE plist PUBLIC') < 60:
        #print "g_p:2"
        try:
            #print "g_p:3.1"
            plist = plistlib.readPlistFromString(data)
            #print "g_p:3.2"
            try:
                #print "g_p:4.1"
                action = plist.get('action')
                #print "g_p:4.1"
                if action.get('kind') == 'Goto':
                    url = action.get('url')
                    print('URL Redirection, please goto: %s' % url)
                    return get_page(url, hurry=True)
                else:
                    print('Unrecognised action: %s' % action.get('kind'))
                    print(plist)
                    return None
                #print "g_p:4.2"
            except AttributeError:
                #print "g_p:4.3"
                pass
            #print "g_p:3.3"
            try:
                # This is a valid plist, is it an error message?
                #print "g_p:5.1"
                message = plist.get('dialog').get('message')
                #print "g_p:5.2"
                explanation = plist.get('dialog').get('explanation')
                #print "g_p:5.3"
                print("WARNING: Attempting to download " + url + " returned the following message(s):")
                print("%s %s" % (message, explanation))
                return None
            except AttributeError: # If not allow next function to address decoding it
                #print "g_p:5.4"
                return data
            #print "g_p:3.4"
        except expat.ExpatError: # Plist barfed on something...
            print("ExpatError: What sort of plist is this?")
            print(data)
            return None
    return data


def write_page(url, language = 1, filename=''):
    if filename == '':
        filename = url.replace('http://','').replace('/','_') + '-Lang_' + str(language) + '.xml'
    f = open('./' + filename, 'w')
    f.write(get_page(url, language, hurry=True))
    print('Output written to ./' + filename)
    return None

def get_institutions():
    institutions = []
    for url in ('http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=EDU','http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=ORG','http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=K12'): #Handle three pages of institutions: "Universities & Colleges", "Beyond Campus" and "K-12"
        #Throw away lots of junk, and make sure all the tags are properly closed.
        xml = clean_html(get_page(url,12, hurry=True)).replace('class="badge"></a>','class="badge"/></a>').replace('Choose Store">','Choose Store"/>')
        root = etree.fromstring(xml)
        items = root.xpath('/div/body/div/div/div/div/div/div/ul/li/a')
        print(str(len(items)) + ' items found.')
        for item in items: # Now have a mix of HBoxViews and Views, around 100 of each...
            item_dict = {}
            item_dict['text'] = smart_unicode(item.text)
            item_dict['url'] = item.get('href')
            item_dict['itu_id'] = item_dict['url'].split('id=')[1]
            institutions.append(item_dict)
    return institutions

# Get Collection info
def get_collection_info(url, hurry=False):
    # print "get_collection_info(%s) called" % url
    info = {}
    try:
        xml = get_page(url, hurry=hurry)
    except ValueError: # If there's a bad URL, skip this link
        return info
    except AttributeError: # If there's no URL, skip this link
        return info
    if xml == None:
        return get_collection_info_arty(url, hurry=hurry)
    root = etree.fromstring(xml)

    #Detect whether any of the items is a movie. If so, set contains_movies to True for this collection.
    items = root.xpath('.//itms:TrackList/itms:plist/itms:dict/itms:array/itms:dict/itms:string',
        namespaces={'itms':'http://www.apple.com/itms/'})
    contains_movies=False
    for i, item in enumerate(items):
        if item.text == 'movie':
            contains_movies=True
    info['contains_movies']=contains_movies

    # Get the Genre (x2), Institution, and Series Name from the Breadcrumb trail for this collection
    items = root.xpath('.//itms:Test/itms:HBoxView/itms:VBoxView/itms:TextView/itms:Color/itms:GotoURL',
                         namespaces={'itms':'http://www.apple.com/itms/'})
    #print items
    #for item in items:
    #    info[item.text] = item.get("url")
    info['genre'] = items[-3].text
    info['genre_url'] = items[-3].get("url")
    info['genre_id'] = info['genre_url'].split('/')[-1].split('?')[0][2:] # e.g. (id)NNNNNNNN
    info['institution'] = items[-2].text
    info['institution_url'] = items[-2].get("url")
    info['institution_id'] = info['institution_url'].split('/')[-1].split('?')[0][2:]
    info['series'] = items[-1].text
    info['series_url'] = items[-1].get("url")
    info['series_id'] = info['series_url'].split('/')[-1].split('?')[0][2:]
    items = root.xpath('.//itms:VBoxView/itms:VBoxView/itms:MatrixView/itms:GotoURL/itms:PictureView',
                         namespaces={'itms':'http://www.apple.com/itms/'})
    info['series_img_170'] = items[0].get('url')
    # Get the Language and last modified
    items = root.xpath('.//itms:VBoxView/itms:VBoxView/itms:MatrixView/itms:VBoxView/itms:TextView/itms:SetFontStyle',
                         namespaces={'itms':'http://www.apple.com/itms/'})
    for i in items:
        try:
            k,v = i.text.strip().split(":")
            info[k.lower()] = v.strip()
        except ValueError:
            pass

    items = root.xpath('.//itms:VBoxView/itms:MatrixView[@columnFormat="*,*,*"]/itms:VBoxView/itms:HBoxView',
        namespaces={'itms':'http://www.apple.com/itms/'})
    info['ratings'] = []
    for i in items:
        rating_text = i.get("alt")
        stars = int(rating_text.split(', ')[0].split(' ')[0])
        count = int(rating_text.split(', ')[-1].split(' ')[0])
        info['ratings'].append({'stars': stars, 'count': count})

    info['comments'] = []
#    try:
    review_url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?pageNumber=0&type=Podcast&id=' + str(info['series_id']) #This page (unlike the first) contains the complete text of longer, more interesting, comments.
    review_xml = unicode(get_page(review_url, hurry=hurry), encoding='utf-8', errors='replace')
    xmls = review_xml.split(u'<View rightInset=\"0\" topInset=\"10\" bottomInset=\"15\" leftInset=\"10\" height=\"1\" stretchiness=\"1\" backColor=\"4c6d99\"></View>')
    xmls[0] = ''
    xmls[len(xmls) - 1] = ''
    for x in xmls:
        if x:
            try:
                try:
                    try: #Necessary to deal with anonymous reviews...
                        source = x.split(u'<b>')[3].split(u'</b>')[0].split(u'\n')[1].split(u'  ')[-1]
                        date = parse(x.split(u'</GotoURL>')[3].split(u'</SetFontStyle>')[0].split(u'\n')[3].split(u'  ')[-1]).date()
                    except:
                        source = u'Anonymous'
                        date = None
                    detail = x.split(u'<SetFontStyle normalStyle=\"textColor\">')[4].split(u'</SetFontStyle>')[0].replace(u"&amp;", u"&").replace(u"&lt;", u"<").replace(u"&gt;", u">").replace(u"&#39;", u"'").replace(u'&quot;', u'"').replace(u"&#34;", u"\"")
                    rating = int(x.split(u'<HBoxView topInset="1" alt=\"')[1].split(u' star')[0])
                        #            print('Source: ' + source + ' date: ' + str(date) + ' detail: ' + detail + ' rating: ' + rating + '*')
                    info['comments'].append({'source': source, 'date': date, 'detail': detail, 'rating': rating})
                except:
                    print("WARNING: Failed to parse comment XML properly when scanning " + review_url)
            except:
                print('WARNING: Couldn\'t get reviews.')

    return info

def get_collection_info_arty(url, hurry=False): #Workaround for pages (typically related to drawing and painting...) which don't work with lang=1 or lang=12. This is non-ideal, but better than nothing.
    # print "get_collection_info(%s) called" % url
    info = {}
    try:
        xml = get_page(url,17, hurry=hurry)
    except ValueError: # If there's a bad URL, skip this link
        return info
    except AttributeError: # If there's no URL, skip this link
        return info
    except urllib2.HTTPError:
        return info
    if xml == None:
        return info
    xml = clean_html(xml).replace('png">','png"/>').replace('Store">','Store"/>')
    root = etree.fromstring(xml)

    #Detect whether any of the items is a movie. If so, set contains_movies to True for this collection.
    items = root.xpath('/div/body/div/div/div/div/div/div/table/tbody/tr/td/span/span/span')
    contains_movies=False
    for i, item in enumerate(items):
        if item.text == 'Video':
            contains_movies=True
    info['contains_movies']=contains_movies

    info['language'] = "Unknown"
    info['genre'] = "Unknown"
    for li in root.xpath('/div/body/div/div/div/div/ul/li'):
        found_genre = False
        found_language = False
        for text_extract in li.itertext(): #Get round a nasty <span> which masks the text to its right...
            if found_language:
                info['language'] = text_extract
            elif found_genre:
                info['genre'] = text_extract
            elif text_extract == 'Category: ':
                found_genre = True
            elif text_extract == 'Language: ':
                found_language = True

    info['genre_url'] = "Unkown"
    info['genre_id'] = 666
    info['institution'] = root.xpath('/div/body/div/div/ul/li/a')[1].text
    info['institution_url'] = root.xpath('/div/body/div/div/ul/li/a')[1].get("href")
    info['institution_id'] = info['institution_url'].split('/id')[len(info['institution_url'].split('/id')) - 1]
    info['series'] = root.xpath('/div/body/div/div/div/div/div/h1/a')[0].text
    info['series_url'] = root.xpath('/div/body/div/div/div/div/div/h1/a')[0].get("href")
    info['series_id'] = info['series_url'].split('/id')[len(info['series_url'].split('/id')) - 1]
#    info['series_img_170'] = root.xpath('/div/body/div/div/div/div/a/div/img')[0].get("src")
    info['series_img_170'] = "Unknown" #When this last-ditch attempt is used to extract category info, the image given in the html is not the right one, and changes every time the page is accessed...


    info['last modified'] = None
#    for i in items:
#        try:
#            k,v = i.text.strip().split(":")
#            info[k.lower()] = v.strip()
#        except ValueError:
#            pass

#    items = root.xpath('.//itms:VBoxView/itms:MatrixView[@columnFormat="*,*,*"]/itms:VBoxView/itms:HBoxView',
#        namespaces={'itms':'http://www.apple.com/itms/'})
    info['ratings'] = []
#    for i in items:
#        rating_text = i.get("alt")
#        stars = int(rating_text.split(', ')[0].split(' ')[0])
#        count = int(rating_text.split(', ')[-1].split(' ')[0])
#        info['ratings'].append({'stars': stars, 'count': count})

    info['comments'] = []
    #    try:
    review_url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewContentsUserReviews?pageNumber=0&type=Podcast&id=' + str(info['series_id']) #This page (unlike the first) contains the complete text of longer, more interesting, comments.
    review_xml = unicode(get_page(review_url, hurry=hurry), encoding='utf-8', errors='replace')
    xmls = review_xml.split(u'<View rightInset=\"0\" topInset=\"10\" bottomInset=\"15\" leftInset=\"10\" height=\"1\" stretchiness=\"1\" backColor=\"4c6d99\"></View>')
    xmls[0] = ''
    xmls[len(xmls) - 1] = ''
    for x in xmls:
        if x:
            try:
                try:
                    try: #Necessary to deal with anonymous reviews...
                        source = x.split(u'<b>')[3].split(u'</b>')[0].split(u'\n')[1].split(u'  ')[-1]
                        date = parse(x.split(u'</GotoURL>')[3].split(u'</SetFontStyle>')[0].split(u'\n')[3].split(u'  ')[-1]).date()
                    except:
                        source = u'Anonymous'
                        date = None
                    detail = x.split(u'<SetFontStyle normalStyle=\"textColor\">')[4].split(u'</SetFontStyle>')[0].replace(u"&amp;", u"&").replace(u"&lt;", u"<").replace(u"&gt;", u">").replace(u"&#39;", u"'").replace(u'&quot;', u'"').replace(u"&#34;", u"\"")
                    rating = int(x.split(u'<HBoxView topInset="1" alt=\"')[1].split(u' star')[0])
                    #            print('Source: ' + source + ' date: ' + str(date) + ' detail: ' + detail + ' rating: ' + rating + '*')
                    info['comments'].append({'source': source, 'date': date, 'detail': detail, 'rating': rating})
                except:
                    print("WARNING: Failed to parse comment XML properly when scanning " + review_url)
            except:
                print('WARNING: Couldn\'t get reviews.')

    return info

# Base iTunes U URLS
# GENRE = http://itunes.apple.com/gb/genre/(BLAH)/id(GENRE-ID)
# INSTITUTION = http://itunes.apple.com/gb/institution/(BLAH)/id(INSTITUTION-ID)
# SERIES = http://itunes.apple.com/gb/itunes-u/(BLAH)/id(SERIES-ID)
# ITEM (in a series) = http://itunes.apple.com/gb/podcast/(BLAH)/id(SERIES-ID)?i=(ITEM-ID)

# Show Top Downloads
def get_topdownloads():
    collections = []
    url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&popId=40&genreId=40000000'
#    xml = get_page(url)
#    root = etree.fromstring(xml)
#    items = root.xpath('.//itms:MatrixView/itms:HBoxView',namespaces={'itms':'http://www.apple.com/itms/'})
#    for item in items: # Now have a mix of HBoxViews and Views, around 100 of each...
#        item_dict = {}
#        item_dict['chart_position'] = int(float(item[0][0].text)) # Somewhat hacky...
#        subtree = item.xpath('.//itms:VBoxView/itms:MatrixView/itms:GotoURL/itms:View/itms:PictureView',
#                             namespaces={'itms':'http://www.apple.com/itms/'}) # item[2][0].getchildren()
#        item_dict['series_img_75'] = subtree[0].get("url")
#        subtree = item.xpath('.//itms:TextView/itms:SetFontStyle/itms:GotoURL',
#                             namespaces={'itms':'http://www.apple.com/itms/'})
#        item_dict['item'] = subtree[0].text.strip()
#        item_dict['item_url'] = subtree[0].get("url")
#        item_dict['item_id'] = item_dict['item_url'].split('/')[-1].split('?')[-1].split('&amp;')[0].split('=')[-1]
#        # item_dict['item_info'] = get_collection_info(item_dict.get('item_url'))
#        item_dict = dict(item_dict.items() + get_collection_info(item_dict.get('item_url')).items())
#        collections.append(item_dict)
#        url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&popId=36&genreId=40000000'
    xml = get_page(url,12)
    xml = clean_html(xml).replace('png">','png"/>').replace('Store">','Store"/>')
    root = etree.fromstring(xml)
    items = root.xpath('/div/body/div/div/div/div/div/div')
    for i,item in enumerate(items):
        item_dict = {}
        item_dict['chart_position'] = int(item.xpath('span/span')[0].text.split('.')[0])
        item_dict['series_img_75'] = item.xpath('a/div/img')[0].get('src')
        item_dict['item'] = item.xpath('ul/li/a')[0].text
        item_dict['item_url'] = item.xpath('ul/li/a')[0].get('href')
        item_dict['item_id'] = item_dict['item_url'].split('/')[-1].split('?')[-1].split('&')[0].split('=')[-1]
        # item_dict['item_info'] = get_collection_info(item_dict.get('item_url'))
        print('Scanning position ' + str(item_dict['chart_position']) + '...')
        item_dict = dict(item_dict.items() + get_collection_info(item_dict.get('item_url')).items())
        collections.append(item_dict)
        url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&popId=36&genreId=40000000'
    return collections


# Show Top Collections
def get_topcollections():
    collections = []
#    url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&popId=36&genreId=40000000'
#    xml = get_page(url)
#    root = etree.fromstring(xml)
#    items = root.xpath('.//itms:MatrixView/itms:HBoxView',namespaces={'itms':'http://www.apple.com/itms/'})
#    for i,item in enumerate(items): # Now have a mix of HBoxViews and Views, around 100 of each...
#        # print i
#        # print int(float(item[0][0].text))
#        item_dict = {}
#        sub = item.xpath('.//itms:TextView/itms:SetFontStyle/itms:GotoURL',
#                         namespaces={'itms':'http://www.apple.com/itms/'})
#        item_dict['chart_position'] = int(float(item[0][0].text)) # Somewhat hacky...
#        item_dict['series_img_75'] = item[2][0][0][0][0].get("url")
#        item_dict['publisher_name'] = sub[1].text.strip()
#        item_dict = dict(item_dict.items() + get_collection_info(sub[0].get("url")).items())
#        collections.append(item_dict)
    url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&popId=36&genreId=40000000'
    xml = get_page(url,12)
    xml = clean_html(xml).replace('png">','png"/>').replace('Store">','Store"/>')
    root = etree.fromstring(xml)
    items = root.xpath('/div/body/div/div/div/div/div/div')
    for i,item in enumerate(items):
        item_dict = {}
        item_dict['chart_position'] = int(item.xpath('span/span')[0].text.split('.')[0])
        item_dict['series_img_75'] = item.xpath('a/div/img')[0].get('src')
        item_dict['publisher_name'] = item.xpath('ul/li/a')[1].text
        print('Scanning position ' + str(item_dict['chart_position']) + '...')
        item_dict = dict(item_dict.items() + get_collection_info(item.xpath('ul/li/a')[0].get('href')).items())
        collections.append(item_dict)
    return collections


## Parse Oxford Collections
## Show Oxford Top Collections (aka list all Oxford feeds in order of downloads)
#url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=381699182' # Redirects to --->
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?id=381699182"
## Ox results sorted by video? It isn't just video results, it's all results (link from xml of the above page)
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?id=381699182&subMediaType=Video"
## Ox results sorted by audio? (link from xml of the above page) ... but then, the pagination urls suggest this query isn't fully supported
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?id=381699182&subMediaType=Audio"
#
## Sort by:
## Album Name - Duff URL
#url="http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=0&amp;id=381699182&amp;mt=10"
## Bestsellers - DEFAULT for Top Collections
#url="http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=1&amp;id=381699182&amp;mt=10"
## Release Date - Duff URL
#url="http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=2&amp;id=381699182&amp;mt=10"
#
## Data is paginated (21 results per xml page), so followup URLS look like...
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=1&id=381699182&batchNumber=1&mt=10" # First follow-on call... Note SortMode
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=1&id=381699182&batchNumber=2&mt=10"
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=1&id=381699182&batchNumber=12&mt=10"
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=1&id=381699182&batchNumber=13&mt=10"
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?sortMode=1&id=381699182&batchNumber=14&mt=10" # For a 15 page result, batchNumber 14 is last call

def get_institution_collections(i, hurry=False):
    collections = []
#    try:
#        url = i.url
#        next_page = True
#        while next_page:
#            xml = get_page(url)
#            if not xml:
#                raise ValueError("Empty page at " + url)
#            root = etree.fromstring(xml)
#            items = root.xpath('.//itms:MatrixView/itms:VBoxView/itms:TextView/itms:SetFontStyle/itms:GotoURL',
#                               namespaces={'itms':'http://www.apple.com/itms/'})
#            if not items:
#                raise ValueError("No collections found at " + url)
#            for i,item in enumerate(items): # Now have a mix of HBoxViews and Views, around 100 of each...
#                #print item.text.lower().strip()
#                #print(item.get('url'))
#                if not item.text.lower().strip().startswith('category'):
#                    collection = get_collection_info(item.get('url'))
#                    if collection:
#                        collections.append(collection)
#
#            items = root.xpath('.//itms:VBoxView/itms:VBoxView/itms:VBoxView/itms:HBoxView/itms:VBoxView/itms:GotoURL/itms:PictureButtonView[@alt="next page"]/../@url',namespaces={'itms':'http://www.apple.com/itms/'}) # Looking for the follow on page links...
#            if len(items) == 1:
#                url = items[0]
#            #        print 'Next URL is: %s' % url
#            else:
#                next_page = False
#    except ValueError: #Institutions with courses give a ValueError, so we have to use a different method to get the links to their collection pages.
    try:
        page = 1
        added_collections = True
        while added_collections:
            url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=' + str(i.itu_id) + '&page=' + str(page)
    #            print(xml)
            xml = get_page(url,12,hurry=hurry)
            if xml:
                #Throw away lots of junk, and make sure all the tags are properly closed.
                xml = clean_html(xml).replace('png"></div>','png"/></div>').replace('<img width="30" height="30" alt="My Store: United Kingdom, Choose Store"></a>','<img width="30" height="30" alt="My Store: United Kingdom, Choose Store"/></a>')
                root = etree.fromstring(xml)
                items = root.xpath('/div/body/div/div/div/div/div/div/ul/li[@class="name"]/a')
                if not items:
                    added_collections = False
                for item in items:
                    print(item.text)
                    collection = get_collection_info(item.get('href'), hurry=hurry)
                    if collection:
                        collections.append(collection)
                page += 1
            else:
                added_collections = False
    except:
        raise CommandError("Failed to parse XML.")
    return collections


def get_collection_items(url, hurry=False):
    try:
        xml = get_page(url, hurry=hurry)
        lang = 1
    except ValueError: # If there's a bad URL, skip this link
        return None
    # Get the tracklisting for this collection
    if xml:
        root = etree.fromstring(xml)
        items = root.xpath('.//itms:TrackList',namespaces={'itms':'http://www.apple.com/itms/'})
    else:
        try:
            print("Trying lang=2 instead...")
            xml = get_page(url,2,hurry=hurry)
            lang = 2
        except ValueError: # If there's a bad URL, skip this link
            return None
        if xml:
            root = etree.fromstring(xml)
            items = root.xpath('.')
        else:
            return None
    plist = plistlib.readPlistFromString(etree.tostring(items[0]))
    if lang == 2:
        #Get rid of all non-podcast-episode plist elements from the list of items to be returned.
        tobereturned = plist.get('items')
        tobereturned_norubbish = []
        for i in tobereturned:
            if i['type'] == 'podcast-episode':
                tobereturned_norubbish.append(i)
        return tobereturned_norubbish
    else:
        return plist.get('items')


# Get data about a single collection, in this instance Critical Reasoning for Begineers (Audio)
url = 'http://itunes.apple.com/gb/itunes-u/critical-reasoning-for-beginners/id387875756'
def get_collection_statistics(url):
    stats = {}
    try:
        xml = get_page(url)
    except ValueError: # If there's a bad URL, skip this link
        return None
    if xml == None:
        return None
    root = etree.fromstring(xml)
    # Get the tracklisting for this collection
    items = root.xpath('.//itms:TrackList',namespaces={'itms':'http://www.apple.com/itms/'})
    plist = plistlib.readPlistFromString(etree.tostring(items[0]))
    stats['total_duration_in_seconds'] = 0
    stats['total_number_of_items'] = len(plist.get('items'))
    stats['item_counts_by_kind'] = {}
    stats['item_counts_by_fileExtension'] = {}
    stats['item_counts_by_genre'] = {}
    stats['total_number_of_explicit_items'] = 0
    stats['longest_duration_in_seconds'] = 0
    stats['shortest_duration_in_seconds'] = 1000000000000000 # Shortest non-Zero duration!
    stats['list_of_durations'] = []
    stats['list_of_nonzero_durations'] = []
    for item in plist.get('items'):
        duration = int(item.get('duration',0))/1000
        stats['list_of_durations'].append(duration)
        if duration > 0:
            stats['list_of_nonzero_durations'].append(duration)
        stats['total_duration_in_seconds'] += duration
        stats['item_counts_by_kind'][str(item.get('kind','na'))] = int(stats['item_counts_by_kind'].get(str(item.get('kind','na')),0)) + 1
        stats['item_counts_by_fileExtension'][str(item.get('fileExtension','na'))] = int(stats['item_counts_by_fileExtension'].get(str(item.get('fileExtension','na')),0)) + 1
        stats['item_counts_by_genre'][str(item.get('genre','na'))] = int(stats['item_counts_by_genre'].get(str(item.get('genre','na')),0)) + 1
        stats['total_number_of_explicit_items'] += item.get('explicit',0)
    # print "This url (%s) has a total duration of %s seconds" % (url,duration_in_seconds)
    stats['list_of_durations'].sort()
    stats['list_of_nonzero_durations'].sort()
    try: # For series with only ebooks in, there will be no data in this array
        stats['longest_duration_in_seconds'] = stats['list_of_nonzero_durations'][-1]
        stats['shortest_duration_in_seconds'] = stats['list_of_nonzero_durations'][0]
    except IndexError:
        pass
    # print stats
    print("Feed duration: %s seconds across %s (non-zero) items (Max:%s sec ; Min:%s sec) %s Items in total. " % (
        stats['total_duration_in_seconds'],
        len(stats['list_of_nonzero_durations']),
        stats['longest_duration_in_seconds'],
        stats['shortest_duration_in_seconds'],
        stats['total_number_of_items']
    ))
    return stats

def get_overall_statistics(url):
    '''
    Scan an institutional URL collection range and add up all the stats for material available
    '''
    tc = get_institution_collections(url)
    stats = {}
    stats['total_duration_in_seconds'] = 0
    stats['longest_duration_in_seconds'] = 0
    stats['shortest_duration_in_seconds'] = 1000000000000000 # Shortest non-Zero duration!
    stats['list_of_durations'] = []
    stats['list_of_nonzero_durations'] = []
    stats['total_number_of_items'] = 0
    stats['item_counts_by_kind'] = {}
    stats['item_counts_by_fileExtension'] = {}
    stats['item_counts_by_genre'] = {}
    stats['total_number_of_explicit_items'] = 0
    stats['mean_average_duration_of_items'] = 0
    print('Analysing %s series' % len(tc))
    for i, series in enumerate(tc):
        print("Analysing: %s) %s" % (i, series.get('series_name')))
        collection_stats = get_collection_statistics(series.get('series_url'))
        stats['total_duration_in_seconds'] += int(collection_stats.get('total_duration_in_seconds',0))
        stats['list_of_durations'] += collection_stats.get('list_of_durations',[])
        stats['list_of_nonzero_durations'] += collection_stats.get('list_of_nonzero_durations',[])
        stats['total_number_of_items'] += int(collection_stats.get('total_number_of_items',0))
        for k, v in collection_stats.get('item_counts_by_kind',0).iteritems():
            # print 'Kind %s was: %s' % (k, stats['item_counts_by_kind'][k])
            stats['item_counts_by_kind'][k] = stats['item_counts_by_kind'].get(k,0) + int(v)
            # print 'Kind %s now: %s' % (k, stats['item_counts_by_kind'][k])
        for k, v in collection_stats.get('item_counts_by_fileExtension',0).iteritems():
            stats['item_counts_by_fileExtension'][k] = stats['item_counts_by_fileExtension'].get(k,0) + int(v)
        for k, v in collection_stats.get('item_counts_by_genre',0).iteritems():
            stats['item_counts_by_genre'][k] = stats['item_counts_by_genre'].get(k,0) + int(v)
        stats['total_number_of_explicit_items'] += int(collection_stats.get('total_number_of_explicit_items',0))
    stats['list_of_durations'].sort()
    stats['list_of_nonzero_durations'].sort()
    try:
        stats['shortest_duration_in_seconds'] = stats['list_of_nonzero_durations'][0]
        stats['longest_duration_in_seconds'] = stats['list_of_nonzero_durations'][-1]
    except IndexError:
        stats['shortest_duration_in_seconds'] = None
        stats['longest_duration_in_seconds'] = None
    stats['mean_average_duration_of_items'] = int(stats['total_duration_in_seconds'] / len(stats['list_of_nonzero_durations']))
    hours = int(stats['total_duration_in_seconds']/60/60)
    minutes = int((stats['total_duration_in_seconds'] - (hours*60*60))/60)
    print("There were %s items across %s feeds" % (stats['total_number_of_items'], len(tc)))
    print("Total duration is %s Hours and %s Minutes" % (hours, minutes))
    print("Average duration for an item is %s seconds" % stats['mean_average_duration_of_items'])
    print("Durations ranged from %s to %s throughout the collection" % (stats['longest_duration_in_seconds'], stats['shortest_duration_in_seconds']))
    perc = float(
        float(len(stats['list_of_durations'])-len(stats['list_of_nonzero_durations'])) /
        len(stats['list_of_durations'])
    ) * 100
    print("%s%% of the collection have a zero duration" % str(perc)[:4])
    print("Breakdown of collection by Genre:")
    print(stats.get('item_counts_by_genre',{}))
    #for k,v in stats.get('item_counts_by_genre',{}):
    #    print "%s : %s" % (k,v)
    print("Breakdown of collection by File Extension:")
    print(stats.get('item_counts_by_fileExtension',{}))
    #for k,v in stats.get('item_counts_by_fileExtension',{}):
    #    print "%s : %s" % (k,v)
    print("Breakdown of collection by Kind:")
    print(stats.get('item_counts_by_kind',{}))
    #for k,v in stats.get('item_counts_by_kind',{}):
    #    print "%s : %s" % (k,v)
    # print stats
    return None

### Institutional Collections
## Oxford University
#url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=381699182'
## Open University
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=380206132"
## UCL
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=390402969"
## Cambridge
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=380451095"
## Warwick
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=407474356"
## Nottingham
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=396415869"
#
## UC Berkeley - Most of their feeds don't report all the data!
#url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=354813951'
## MIT
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=341593265"
## Yale
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=341649956"
## Stanford
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=384228265"
#
#
#{
#    'anonymous': True,
#    'artistName': 'Marianne Talbot',
#    'buyParams': 'http://deimos.apple.com/WebObjects/Core.woa/DownloadTrack/ox-ac-uk-public-dz.4486656253.04486656255.4486656318',
#    'description': 'Part six of a six-part series on critical reasoning. In this final lecture we will look at fallacies. These are bad arguments that can easily be mistaken for good arguments. Creative Commons Attribution-Non-Commercial-Share Alike 2.0 UK: England & Wales;',
#    'duration': 3423000,  # Value in Milliseconds!
#    'explicit': 0,
#    'feedURL': 'https://deimos.apple.com/WebObjects/Core.woa/Feed/ox-ac-uk-public-dz.4486656253.04486656255',
#    'fileExtension': 'mp3',
#    'genre': 'Philosophy',
#    'isEpisode': False,
#    'itemId': 86181490,
#    'kind': 'unknown',
#    'longDescription': 'Part six of a six-part series on critical reasoning. In this final lecture we will look at fallacies. These are bad arguments that can easily be mistaken for good arguments. Creative Commons Attribution-Non-Commercial-Share Alike 2.0 UK: England & Wales; http://creativecommons.org/licenses/by-nc-sa/2.0/uk/',
#    'playlistId': 387875756,
#    'playlistName': 'Critical Reasoning for Beginners',
#    'popularity': '0.0',
#    'previewLength': 3423,
#    'previewURL': 'http://deimos.apple.com/WebObjects/Core.woa/DownloadRedirectedTrackPreview/ox-ac-uk-public-dz.4486656253.04486656255.4486656318.mp3',
#    'price': 0,
#    'priceDisplay': 'Free',
#    'rank': 11,
#    'releaseDate': '2010-03-18T11:02:29Z',
#    's': 1000000,
#    'songName': 'Evaluating Arguments Part Two',
#    'url': 'http://itunes.apple.com/gb/itunes-u/evaluating-arguments-part/id387875756?i=86181490'
#}
#
#{
#    'anonymous': True,
#    'artistName': 'Marianne Talbot',
#    'buyParams': 'http://deimos.apple.com/WebObjects/Core.woa/DownloadTrack/ox-ac-uk-public-dz.4486656253.04486656255.4486656324',
#    'description': 'Part six of a six-part series on critical reasoning. In this final lecture we will look at fallacies. These are bad arguments that can easily be mistaken for good arguments. Creative Commons Attribution-Non-Commercial-Share Alike 2.0 UK: England & Wales;',
#    # DURATION MISSING
#    'explicit': 0,
#    'feedURL': 'https://deimos.apple.com/WebObjects/Core.woa/Feed/ox-ac-uk-public-dz.4486656253.04486656255',
#    'fileExtension': 'pdf',
#    'genre': 'Philosophy',
#    'isEpisode': False,
#    'itemId': 86181487,
#    'kind': 'pdf',
#    'longDescription': 'Part six of a six-part series on critical reasoning. In this final lecture we will look at fallacies. These are bad arguments that can easily be mistaken for good arguments. Creative Commons Attribution-Non-Commercial-Share Alike 2.0 UK: England & Wales; http://creativecommons.org/licenses/by-nc-sa/2.0/uk/',
#    'playlistId': 387875756,
#    'playlistName': 'Critical Reasoning for Beginners',
#    'popularity': '0.0',
#    'previewLength': 0,
#    'previewURL': 'http://deimos.apple.com/WebObjects/Core.woa/DownloadRedirectedTrackPreview/ox-ac-uk-public-dz.4486656253.04486656255.4486656324.pdf',
#    'price': 0,
#    'priceDisplay': 'Free',
#    'rank': 12,
#    'releaseDate': '2010-03-18T11:02:29Z',
#    's': 1000000,
#    'songName': 'Evaluating Arguments Part Two (slides)',
#    'url': 'http://itunes.apple.com/gb/itunes-u/evaluating-arguments-part/id387875756?i=86181487'
#}
#
#
#
## Universities and Colleges Listing
#url = "http://itunes.apple.com/WebObjects/DZR.woa/wa/viewiTunesUProviders?id=EDU" # -->
#url = "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGrouping?id=27753&mt=10&s=143444" # ??? This is the front page
#
## iTunes U Homepage
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000000' # PList returned sometimes, redirecting to...
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGrouping?id=27753&mt=10&s=143444' # xml data???
#
## Noteworthy - See All link
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=433198506&amp;genreIdString=40000000&amp;mediaTypeString=iTunes+U'
#
## Show Oxford on iTunes U (Homepage)
#url = 'http://itunes.apple.com/gb/institution/oxford-university/id381699182'
#
#
#
#
## Show an Oxford Series (New Depression)
#url = 'http://itunes.apple.com/gb/itunes-u/the-new-psychology-depression/id474787597' # Redirects to...
#url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewPodcast?cc=gb&id=474787597'
## Looking for rating of Series...
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/customerReviews?displayable-kind=4&id=474787597'
#
## View "For History Buffs" . Note, these seem to be called "Rooms"
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=433198516&amp;genreIdString=40000000&amp;mediaTypeString=iTunes+U'
##... same but Language Learning with Emory University
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=433198510&amp;genreIdString=40000000&amp;mediaTypeString=iTunes+U'
#
## Block adverts ("Bricks") - Second set
## Intro College Courses
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewMultiRoom?fcId=451295083&amp;s=143444'
## Business
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000001&amp;mt=10'
## Language
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000056&amp;mt=10'
## Health and Medicine
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000026&amp;mt=10'
## STEM Education
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewMultiRoom?fcId=421972407&amp;s=143444'
#
## Block adverts/Bricks - First set
## William Shakespeare
#url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewMultiRoom?fcId=473868067&amp;s=143444'
## The Middle East
#url = 'http://itunes.apple.com/gb/collection/the-middle-east/id27753?fcId=439695493&amp;mt=10'
## Ancient Greece and Rome
#url = 'http://itunes.apple.com/gb/collection/ancient-greece-rome/id27753?fcId=395458516&amp;mt=10'




# Test what all the STORE LANGUAGE values do for us...
def test_responses(url):
    print("test_responses(%s) called" % url)
    USER_AGENT = 'iTunes/10.5.1 (Macintosh; Intel Mac OS X 10.6.8) AppleWebKit/534.51.22'
    APPLE_STORE_FRONT = '143444'
    APPLE_TZ = '0'
    ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    HOST = 'itunes.apple.com'
    ACCEPT_LANGUAGE = 'en-us, en;q=0.50'
    for i in [12,1,2]:
        APPLE_STORE_LANGUAGE = i
        request = urllib2.Request(url)
        request.add_header('User-Agent', USER_AGENT)
        request.add_header('X-Apple-Store-Front','%s,%s' % (APPLE_STORE_FRONT, APPLE_STORE_LANGUAGE))
        request.add_header('X-Apple-Tz',APPLE_TZ)
        request.add_header('Accept', ACCEPT)
        request.add_header('Accept-Language', ACCEPT_LANGUAGE)
        request.add_header('Host',HOST)
        opener = urllib2.build_opener()
        data = opener.open(request).read()
        output = ''
        if data.find('<!DOCTYPE plist PUBLIC') > 0 and data.find('<!DOCTYPE plist PUBLIC') < 60:
            try:
                plist = plistlib.readPlistFromString(data)
                try:
                    action = plist.get('action')
                    if action.get('kind') == 'Goto':
                        print("1.1")
                        url = action.get('url')
                        output = 'URL Redirection, please goto: %s ' % url
                        output += str(test_responses(url))
                        print("1.2")
                        return None
                    else:
                        print("2.1")
                        output = 'Unrecognised action: %s \n' % action.get('kind')
                        output += repr(plist)
                        print("2.2")
                except AttributeError:
                    print("3.1")
                    output = "AttributeError: What sort of plist is this?\n" + str(data)
                    print("3.2")
            except expat.ExpatError:
                # Plist barfed on something...
                print("4.1")
                output = "ExpatError: What sort of plist is this?\n" + str(data)
                print("4.2")
        else:
            # Assume HTML and send that back out...
            print("5.1")
            output = str(data)
            print("5.2")
        filename = url.replace('http://','').replace('/','_') + '-Lang_' + str(i) + '.xml'
        f = open('./' + filename, 'w')
        f.write(output)
        print('Output written to ./' + filename)
    return None

#urls = [
#    'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000000', # iTU Home
#    # redirects to: http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGrouping?id=27753&mt=10&s=143444
#    'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=433198506&amp;genreIdString=40000000&amp;mediaTypeString=iTunes+U', # iTU Noteworthy
#    "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?genreId=40000000&id=27753&popId=36", # iTU Top Collections
#    'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&popId=40&genreId=40000000', # iTU Top Downloads
#    "http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewiTunesUInstitution?id=381699182", # Oxford iTU Homepage
#    # redirects to: http://itunes.apple.com/WebObjects/DZR.woa/wa/viewArtist?id=381699182
#    ]
#for url in urls:
#    test_responses(url)