#getlink.py
import urllib, urllib2, json as simplejson
lastfm_apikey = "95a1d5bc95ed37748166009c90251866"

def get_thumb_url(data, id_type):
        
        thumb_url = None
        
        try:
            images = data[id_type]['image']
        except KeyError:
            return None
        
        for image in images:
            if image['size'] == 'medium':
                thumb_url = image['#text']
                break
                
        return thumb_url

def get_image_links(ArtistID=None, AlbumID=None):
	'''
	Here we're just going to open up the last.fm url, grab the image links and return them
	Won't save any image urls, or save the artwork in the cache. Useful for search results, etc.
	'''
	if ArtistID:
		
		id_type = 'artist'
		
		params = {  "method": "artist.getInfo",
		"api_key": lastfm_apikey,
		"mbid": ArtistID,
		"format": "json"
		}
		
		url = "http://ws.audioscrobbler.com/2.0/?" + urllib.urlencode(params)
		pass#print "logger.debug('Retrieving artist information from: ' + url)"
			
		try:
			result = urllib2.urlopen(url, timeout=20).read()
		except:
			print "logger.warn('Could not open url: ' + url)"
			return
		
		if result:
			
			try:
				data = simplejson.JSONDecoder().decode(result)
			except:
				print "logger.warn('Could not parse data from url: ' + url)"
				return

			try:
				image_url = data['artist']['image'][-1]['#text']
			except Exception:
				print "logger.debug('No artist image found on url: ' + url)"
				image_url = None
			
			thumb_url = get_thumb_url(data, id_type)

			if not thumb_url:
				print "logger.debug('No artist thumbnail image found on url: ' + url)"
				
	else:
		id_type = 'album'
		
		params = {  "method": "album.getInfo",
		"api_key": lastfm_apikey,
		"mbid": AlbumID,
		"format": "json"
		}
		
		url = "http://ws.audioscrobbler.com/2.0/?" + urllib.urlencode(params)
		pass#print "logger.debug('Retrieving album information from: ' + url)"

		try:
			result = urllib2.urlopen(url, timeout=20).read()
		except:
			pass#print "logger.warn('Could not open url: ' + url)"
			return
			
		if result:
		
			try:
				data = simplejson.JSONDecoder().decode(result)
			except:
				pass#print "logger.warn('Could not parse data from url: ' + url)"
				return
			
			try:
				image_url = data['artist']['image'][-1]['#text']
			except Exception:
				pass#print "logger.debug('No artist image found on url: ' + url)"
				image_url = None
			
			thumb_url = get_thumb_url(data, id_type)
			
			if not thumb_url:
				pass#print "logger.debug('No artist thumbnail image found on url: ' + url)"
			
	image_dict = {'artwork' : image_url, 'thumbnail' : thumb_url }
	return image_dict
#print get_image_links(AlbumID='d592a035-bb92-45d4-b3c3-00f46bc89f85')  
#print get_image_links(ArtistID='00705dbc-c5b4-4ec9-8bc8-cd770d8b5b99')        