import getlink, headphones

TITLE = L('Headphones')

PREFIX = "/applications/headphones"

ART     	= "art-default.jpg"
ICON 		= "icon-default.png"
PREFS_ICON  = "icon-prefs.png"
SEARCH_ICON = "icon-search.png"
NO_ARTIST_ART = "no-cover-art.png"
NO_ALBUM_ART  = "no-album-art.png"
UPCOMING    = "icon-upcoming.png"
WANTED  	= "icon-wanted.png"
HISTORY 	= "icon-history.png"

#thumb=Resource.ContentsOfURLWithFallback(url='http://vimcasts.org/images/posters/show_invisibles.png', fallback=R('icon-default.png'))
#next page object: https://forums.plexapp.com/index.php/topic/77227-best-practice-for-populating-directoryobjects-with-remote-metadata/
#xpath technique: https://forums.plexapp.com/index.php/topic/69850-two-divs-with-same-class-names-how-to-distingish-via-xpath/
#		https://forums.plexapp.com/index.php/topic/49086-xpath-coding/
# I can
#   1) create 2 differnet channels: 1 that searches albums, & 1 that searches artists OR
#   2) create a version that accept your query and by default lists (artist/album) and then presents you with an object to query the opposite, and returns this each time
#   3) Create a version that does a query (limit=50) on both artist and album for your text, then interpolates the results, sorting by score

def Start():
	"""
	called by the PMS framework to initialize the plug-in
	
	This includes setting up
	the Plug-in static instance along with the displayed artwork. These setting below are pretty standard
	You first set up the containers and default for all possible objects.  You will probably mostly use Directory Objects
	and Videos Objects. But many of the other objects give you added entry fields you may want to use and set default thumb
	and art for. For a full list of objects and their parameters, refer to the Framework Documentation.
	"""

	#Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
	#Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

	HTTP.CacheTime = 0

	ObjectContainer.title1 	= TITLE
	ObjectContainer.art		= R(ART)

	DirectoryObject.thumb 	= R(ICON)
	DirectoryObject.art 	= R(ART)

	#PopupDirectoryObject.thumb = R(ICON)

	
@route('%s/validate' % PREFIX)
def ValidatePrefs():
    """
    This function is called when the user modifies their preferences.

    The developer can check the newly provided values 
    to ensure they are correct (e.g. attempting a login 
    to validate a username and password), and optionally 
    return a MessageContainer to display any error information to the user.
    """
    if Prefs['hpUsername'] and Prefs['hpPassword']:
        Log("Username and Password preferences found.")
        try:
            Dict['API_K'] = headphones.getAPI_K()
            Log("HP API key stored for future use.")
            return
        except:
            return ObjectContainer(header="Unable to retrieve API key", message="Please confirm that your settings are correct.")


####################################################################################################
@handler(PREFIX, TITLE, thumb=ICON, art=ART)
def MainMenu(view_group="InfoList", no_cache=True):
	"""
	First function and main menu for your channel

	Display Main Menu if API_K was retrieved
	TODO: make search compatible in Plex/Web
	"""
	oc = ObjectContainer()
	Log("Loading Preferences, Username: %s" % Prefs['hpUsername'])
	Log("Loading Preferences, Password: %s" % Prefs['hpPassword'])
	Log("Loading Preferences, https: %s" % Prefs['https'])
	Log("Loading Preferences, Host IP: %s" % Prefs['hpIP'])

	API_KEY = False
	Log('API_KEY bool is: %s' % API_KEY)
	Log('Dict[API_K] is holding: %s' % Dict['API_K'])
	if Dict['API_K']:
		API_KEY = True
		Dict['settings_modified'] = False
	else:
		try:
			Dict['HP_URL'] = headphones.HP_URL(Prefs['https'], Prefs['hpIP'], Prefs['hpPort'], Prefs['hpURLBase'])
			Log("Saved %s into Dict['HP_URL']" % Dict['HP_URL'])
			Dict['API_URL'] = headphones.API_URL()
			Log("Saved %s into Dict['API_URL']" % Dict['API_URL'])
			Dict['API_K'] = headphones.getAPI_K()
			Log("Saved %s into Dict['API_K']" % Dict['API_K'])
		except:
			pass

	

	if API_KEY:		
		Log('API_K retrieved: %s' % API_KEY)
		oc.add(DirectoryObject(key=Callback(GetIndex), title="Manage Your Music Catalog", summary="View and edit your existing music library"))
		oc.add(DirectoryObject(key=Callback(GetUpcoming), title="Future Releases", summary="See which artists in your catalog have future releases", thumb=R(UPCOMING)))
		oc.add(DirectoryObject(key=Callback(GetHistory), title="History", summary="See which albums have been snatched/downloaded recently", thumb=R(HISTORY)))
		# an InputDO in the MainMenu of a channel will work ( in web) when only in the main menu, but anywhere else subsequent, it fails
		#oc.add(InputDirectoryObject(key=Callback(SearchMenu), title="search", summary="Results of search", prompt="Search for:", thumb=R(SEARCH_ICON)))
		#oc.add(InputDirectoryObject(key=Callback(SearchMenu), title="Plex/Web search", summary="Results of search", prompt="Search for:", thumb=R(SEARCH_ICON)))
		oc.add(DirectoryObject(key=Callback(SearchMenu), title="Search", summary="Album or Artist Search for Plex Home Theater client", thumb=R(SEARCH_ICON)))
		oc.add(PrefsObject(title="Preferences", summary="Set Headphones preferences", thumb=R(PREFS_ICON)))
		oc.add(DirectoryObject(key=Callback(Suggestions), title="Suggestions",
	            summary="Artists suggested by Headphones app", thumb=R(ICON)))
	else:
		oc.add(PrefsObject(title="Preferences", summary="PLUGIN IS CURRENTLY UNABLE TO CONNECT TO HEADPHONES.\nSet Headphones plugin preferences to allow it to connect to Headphones server",
            thumb=R(PREFS_ICON)))
	return oc


@route(PREFIX + '/getindex', offset=int)
def GetIndex(offset=0):
	"""
	Headphones library index

	my 'headphones.*() functions + no 'DirectoryObject' fuck this display grid up (in plex\web)
	TODO: finalize 'pagination' and produce compatability for plex/web and PHT
	"""
	oc = ObjectContainer(title2="Artist Catalog")

	# w/o including one of these oc.add()'s underneath this comment, my thumbs will not display on this menu (in plex/web)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="Contents of getUpcoming", thumb=R(NO_ALBUM_ART)))
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="Contents of getHistory", thumb=R(HISTORY)))
	#oc.add(InputDirectoryObject(key=Callback(DoNothing), title="null", summary="Results of search", prompt="Search for:", thumb=R(SEARCH_ICON)))
	#oc.add(PrefsObject(title="Preferences", summary="Set Headphones preferences", thumb=R(PREFS_ICON)))
	#return oc
	
	results = headphones.getIndex()
	#Log("results: %s" % results)
	
	for result in results:
			title="%s (%s/%s) [%s]" % (result['ArtistName'], str(result['HaveTracks']), str(result['TotalTracks']), result['Status'])
			summary = "Latest Album: %s (%s)" % (result['LatestAlbum'], result['ReleaseDate'])
			oc.add(DirectoryObject(key=Callback(ArtistPage, ArtistID=result['ArtistID']), 
			title=title, 
			summary=summary, 
			thumb=Resource.ContentsOfURLWithFallback(url=result['ThumbURL'], fallback=R(NO_ARTIST_ART))))
	if len(results) > (offset+99):
		oc.add(NextPageObject(key=Callback(GetIndex, offset=offset+20)))
	return oc


@route(PREFIX + '/getupcoming')
def GetUpcoming():
	"""
	Fetch upcoming albums

	Return 
	Status, AlbumASIN, DateAdded, AlbumTitle, 
	ArtistName, ReleaseDate, AlbumID, ArtistID, Type)
	"""
	oc = ObjectContainer(title2="Future Releases", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))
	results = headphones.getUpcoming()
	Log("results: %s" % results)

	i=0
	for result in results:
		i+=1
		if i<100: # >= 100 oc.add's will not display thumbs (in plex/web)
			title="%s" % (result['ArtistName'])
			summary = "%s: %s (%s) [%s]" % (result['Type'], result['ArtistName'], result['ReleaseDate'], result['Status'])
			oc.add(DirectoryObject(key=Callback(DoNothing),
				title=title,
				summary=summary,
				thumb=Resource.ContentsOfURLWithFallback(url=result['ThumbURL'], fallback=R(NO_ARTIST_ART))))
	return oc


@route(PREFIX + '/gethistory')
def GetHistory():
	"""
	Return Headphones history

	Return: 
	Status, DateAdded, Title, URL (nzb), 
	FolderName, AlbumID, Size (bytes)
	"""
	oc = ObjectContainer(title2="History", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder"))#, thumb=R(NO_ALBUM_ART)))
	
	results = headphones.getHistory()
	Log("results: %s" % results)

	i=0
	for result in results:
		i+=1
		if i<100: # >= 100 oc.add's will not display thumbs (in plex/web)
			title="%s" % (result['Title'])
			summary = "%s\n %s (%d MB) [%s]" % (result['FolderName'], result['DateAdded'], int(int(result['Size']/1024)/1024), result['Status'])
			oc.add(PopupDirectoryObject(key=Callback(DoNothing),
				title=title,
				summary=summary))
	return oc


@route(PREFIX + '/suggestions')
def Suggestions():
	"""
	Returns similar artists  - with a higher "Count" being more likely to be similar. 
	
	Return: 
	Count, ArtistName, ArtistID
	"""
	oc = ObjectContainer(title2="Suggestions", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))
	
	results = headphones.getSimilar()

	i=0
	for result in results:
		Log("results: %s" % results)
		i+=1
		if i<100: # >= 100 oc.add's will not display thumbs (in plex/web)
			title="%s" % (result['ArtistName'])
			summary=""
			#Dict['ArtistID'] = result['ArtistID']
			oc.add(DirectoryObject(key=Callback(ShowArtist, ArtistID=result['ArtistID']),
			#oc.add(DirectoryObject(key=Callback(ShowArtist),
				title=title,
				summary=summary,
				thumb=R(NO_ARTIST_ART)))
	return oc


@route(PREFIX + '/searchmenu')
def SearchMenu():
	"""
	Display options to select query type, Artists or Albums

	"""
	oc = ObjectContainer(title2="Search Menu", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))

	oc.add(DirectoryObject(key=Callback(SearchPage, ARTIST=True), title="Add Artist", summary="Search for an Artist", thumb=R(SEARCH_ICON)))
	oc.add(DirectoryObject(key=Callback(SearchPage, ALBUM=True), title="Add Album", summary="Search for an album", thumb=R(SEARCH_ICON)))    

	return oc


@route(PREFIX + '/search')
def SearchPage(ARTIST=False, ALBUM=False):
	"""
	Display page to perform the query after selecting the type on SearchMenu()

	"""
	Log('ARTIST: %s, ALBUM: %s' % (ARTIST, ALBUM))

	oc = ObjectContainer(title2="Search Page", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))
	

	if ARTIST:
		oc.add(InputDirectoryObject(key=Callback(QueryArtist), title="Search", summary="Results of search", prompt="Search for:", thumb=R(SEARCH_ICON)))
	else:
		oc.add(InputDirectoryObject(key=Callback(QueryAlbum), title="Search", summary="Results of search", prompt="Search for:", thumb=R(SEARCH_ICON)))
	return oc


@route(PREFIX + '/queryartist')
def QueryArtist(query):
	"""
	Query method for Artist

	"""
	#Log('ARTIST: %s, ALBUM: %s' % (ARTIST, ALBUM))
	Log.Debug('Search term(s): ' + query)

	oc = ObjectContainer(title2="Search Result", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))
	
	#if ARTIST:
		#oc.add(InputDirectoryObject(key=Callback(Query), title="search", summary="Results of search", prompt="Search for:", thumb=R(SEARCH_ICON)))
	results = headphones.findArtist(query, LIMIT=100)
	for result in results:
		title=result['uniquename']
		summary=result['score']
		thumb=getlink.get_image_links(ArtistID=result['id'])['thumbnail']
		oc.add(PopupDirectoryObject(key=Callback(ShowArtist, ArtistID=result['id']),
			title=title,
			summary=summary,
			thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(NO_ARTIST_ART))))	

	if len(oc) < 1:
		return ObjectContainer(header="No items to display", message="No results.")
	else:
		return oc


@route(PREFIX + '/queryalbum')
def QueryAlbum(query):
	"""
	Query method for Album

	"""
	#Log('ARTIST: %s, ALBUM: %s' % (ARTIST, ALBUM))
	Log.Debug('Search term(s): ' + query)

	oc = ObjectContainer(title2="Search Result", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))

	results = headphones.findAlbum(query, LIMIT=100)
	for result in results:
		title=result['uniquename']
		summary="Score: %s\n" % result['score']
	#	try:
	#		thumb=getlink.get_image_links(AlbumID=result['albumid'])['thumbnail']
	#	except:
	#		thumb=R(NO_ALBUM_ART)
		oc.add(PopupDirectoryObject(key=Callback(ShowAlbum, AlbumID=result['albumid']),
			title=title,
			summary=summary,
			thumb=Resource.ContentsOfURLWithFallback(url=getlink.get_image_links(AlbumID=result['albumid'])['thumbnail'], fallback=R(NO_ARTIST_ART))))

	if len(oc) < 1:
		return ObjectContainer(header="No items to display", message="No results.")
	else:
		return oc


@route(PREFIX + '/showartist')
def ShowArtist(ArtistID):
	"""
	Display Artists "Context-Menu"

	"""
	oc = ObjectContainer(title2="Add Artist", no_cache=True)
	#oc.add(PopupDirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder"))#, thumb=R(NO_ALBUM_ART)))

	oc.add(PopupDirectoryObject(key=Callback(AddArtist, ArtistID=ArtistID), title="Add this artist"))
	#oc.add(PopupDirectoryObject(key=Callback(AddArtist), title="Add this artist"))
	return oc


@route(PREFIX + '/showalbum')
def ShowAlbum(AlbumID):
	"""
	Display Album "Context-Menu"
	
	"""
	oc = ObjectContainer(title2="Add Album", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))

	oc.add(PopupDirectoryObject(key=Callback(AddAlbum, AlbumID=AlbumID), title="Add this album"))
	return oc


@route(PREFIX + '/addartist')
def AddArtist(ArtistID):
	if headphones.addArtist(ArtistID):
		return ObjectContainer(header="Headphones", message="Artist Added to Index")


@route(PREFIX + '/addalbum')
def AddAlbum(AlbumID):
	if headphones.addAlbum(AlbumID):
		return ObjectContainer(header="Headphones", message="Album Added to Wanted List")


@route(PREFIX + '/artistpage')
def ArtistPage(ArtistID):

	#title2=headphones.getArtist['ArtistID']['albums']['ArtistName']
	oc = ObjectContainer(title2="Artist Page", no_cache=True)
	#oc.add(DirectoryObject(key=Callback(DoNothing), title="null", summary="placeholder", thumb=R(NO_ALBUM_ART)))

	#Refresh, delete, pause, remove extras, modify extras
	oc.add(DirectoryObject(key=Callback(AlbumPage, ArtistID=ArtistID),
		title="Albums"))
	oc.add(PopupDirectoryObject(key=Callback(RefreshArtist, ArtistID=ArtistID),
		title="Refresh"))
	oc.add(PopupDirectoryObject(key=Callback(DeleteArtist, ArtistID=ArtistID),
		title="Delete"))
	oc.add(PopupDirectoryObject(key=Callback(PauseArtist, ArtistID=ArtistID),
		title="Pause"))
	#oc.add(PopupDirectoryObject(key=Callback(DoNothing, ArtistID),
	#	title="Remove Extras"))
	#oc.add(PopupDirectoryObject(key=Callback(DoNothing, ArtistID),
	#	title="Modify Extras"))
	return oc


@route(PREFIX + '/refresh')
def RefreshArtist(ArtistID):
	if headphones.refreshArtist(ArtistID):
		return ObjectContainer(header="Headphones", message="Artist Refrshed")


@route(PREFIX + '/delete')
def DeleteArtist(ArtistID):
	if headphones.delArtist(ArtistID):
		return ObjectContainer(header="Headphones", message="Deleted Artist")


@route(PREFIX + '/pause')
def PauseArtist(ArtistID):
	if headphones.pauseArtist(ArtistID):
		return ObjectContainer(header="Headphones", message="Paused Artist")


@route(PREFIX + '/albumpage')
def AlbumPage(ArtistID):
	oc = ObjectContainer(title2="Albums", no_cache=True)

	results = headphones.getArtist(ArtistID)
	Log("results: %s" % results)

	for result in results['albums']:
		title="%s [%s]" % (result['AlbumTitle'], result['Status'])
		summary="%s (%s)\n%s" % (result['DateAdded'], result['ReleaseDate'], result['Type'])
		thumb=result['ThumbURL']
		oc.add(DirectoryObject(key=Callback(DoNothing),
			title=title,
			summary=summary,
			thumb=Resource.ContentsOfURLWithFallback(url=thumb, fallback=R(NO_ARTIST_ART))))

		pass

	return oc

@route(PREFIX + '/donothing')
def DoNothing():
	"""
	Pseudo-Callback

	"""