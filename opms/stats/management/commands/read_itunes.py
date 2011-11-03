import urllib2, plistlib
from BeautifulSoup import BeautifulSoup

def getpage(url):
    USER_AGENT = 'iTunes/10.5 (Macintosh; Intel Mac OS X 10.6.8) AppleWebKit/534.51.22'
    APPLE_STORE_FRONT = '143444,12'
    APPLE_TZ = '0'
    request = urllib2.Request(url)
    request.add_header('User-Agent', USER_AGENT)
    request.add_header('X-Apple-Store-Front',APPLE_STORE_FRONT)
    request.add_header('X-Apple-Tz',APPLE_TZ)
    opener = urllib2.build_opener()
    return opener.open(request).read()

xml_data = getpage(url)

plistlib.readPlistFromString(xml_data)

soup = BeautifulSoup(xml_data)
print soup.prettify()

# iTunes U Homepage
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGrouping?id=27753&mt=10&s=143444'

# Show Top Collections
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&amp;popId=36&amp;genreId=40000000'
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?genreId=40000000&id=27753&ign-mscache=1&popId=36'

# Show Top Downloads
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewTop?id=27753&amp;popId=40&amp;genreId=40000000'

# Show Oxford on iTunes U
url = 'http://itunes.apple.com/gb/institution/oxford-university/id381699182'
# Show Oxford Top Downloads
url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewTopCollections?id=381699182'
# Show an Oxford Series (New Depression)
url = 'http://itunes.apple.com/gb/itunes-u/the-new-psychology-depression/id474787597' # Redirects to...
url = 'http://itunes.apple.com/WebObjects/DZR.woa/wa/viewPodcast?cc=gb&id=474787597'
# Looking for rating of Series...
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/customerReviews?displayable-kind=4&id=474787597'

# View "For History Buffs" . Note, these seem to be called "Rooms"
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=433198516&amp;genreIdString=40000000&amp;mediaTypeString=iTunes+U'
#... same but Language Learning with Emory University
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewRoom?fcId=433198510&amp;genreIdString=40000000&amp;mediaTypeString=iTunes+U'

# Block adverts ("Bricks") - Second set
# Intro College Courses
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewMultiRoom?fcId=451295083&amp;s=143444'
# Business
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000001&amp;mt=10'
# Language
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000056&amp;mt=10'
# Health and Medicine
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewGenre?id=40000026&amp;mt=10'
# STEM Education
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewMultiRoom?fcId=421972407&amp;s=143444'

# Block adverts/Bricks - First set
# William Shakespeare
url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wa/viewMultiRoom?fcId=473868067&amp;s=143444'
# The Middle East
url = 'http://itunes.apple.com/gb/collection/the-middle-east/id27753?fcId=439695493&amp;mt=10'
# Ancient Greece and Rome
url = 'http://itunes.apple.com/gb/collection/ancient-greece-rome/id27753?fcId=395458516&amp;mt=10'