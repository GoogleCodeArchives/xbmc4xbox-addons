#
# Imports
#
from BeautifulSoup      import BeautifulSoup, SoupStrainer
from gametrailers_const import __settings__, __language__
from gametrailers_utils import HTTPCommunicator
import os
import re
import sys
import urllib
import xbmc
import xbmcgui
import xbmcplugin

#
# Main class
#
class Main:
	#
	# Init
	#
	def __init__( self ) :
		# Constants
		self.DEBUG         = False
		self.IMAGES_PATH   = xbmc.translatePath( os.path.join( os.getcwd(), 'resources', 'images' ) )
		self.ENTRY_LIST_RE = re.compile( "(\d+) to (\d+) of \d+" )
		
		# Parse parameters...
		params = dict(part.split('=') for part in sys.argv[ 2 ][ 1: ].split('&'))
		self.plugin_category  = params[ "plugin_category" ] 
		self.current_page     = int ( params.get( "page", "1" ) )
		self.entries_par_page = 10

		# Settings
		self.video_quality   = __settings__.getSetting ("video_quality")

		#
		# Get the videos...
		#
		self.getVideos()
	
	#
	# Get videos...
	#
	def getVideos( self ) :
		# 
		# Get HTML page...
		#
		url              = "http://www.gametrailers.com/feeds/line_listing_results/video_hub/6bc9c4b7-0147-4861-9dac-7bfe8db9a141/?sortBy=most_recent&category=Review&currentPage=%d" % ( self.current_page )
		httpCommunicator = HTTPCommunicator()
		htmlData         = httpCommunicator.get( url )

		# Parse response...
		beautifulSoup = BeautifulSoup( htmlData )
		
		#
		# Parse movie entries...
		#
		lis = beautifulSoup.findAll ( "div", { "class" : "video_information" } )
		for li in lis :
			div_holder = li.find ( "div", { "class" : "holder" } )
			
			# Title
			h3    = div_holder.find ( "h3" )
			h4    = div_holder.find ( "h4" )
			title = "%s - %s" % ( h3.a.string.strip(), h4.a.string.strip() )
			
			# Thumbnail
			a_thumbnail      = div_holder.find ( "a", { "class" : "thumbnail" } )
			a_thumbnail_imgs = a_thumbnail.findAll ( "img" )
			thumbnail_url    = a_thumbnail_imgs[ -1 ] [ "src" ]
			
			# Video page...
			video_page_url = a_thumbnail[ "href" ]
			
			# Add to list...
			listitem        = xbmcgui.ListItem( title, iconImage="DefaultVideo.png", thumbnailImage=thumbnail_url )
			listitem.setInfo( "video", { "Title" : title, "Studio" : "GameTrailers" } )
			plugin_play_url = '%s?action=play&video_page_url=%s' % ( sys.argv[ 0 ], urllib.quote_plus( video_page_url ) )
			xbmcplugin.addDirectoryItem( handle=int(sys.argv[ 1 ]), url=plugin_play_url, listitem=listitem, isFolder=False)

		# Next page entry...
		listitem = xbmcgui.ListItem ( __language__(30503), iconImage = "DefaultFolder.png", thumbnailImage = os.path.join(self.IMAGES_PATH, 'next-page.png'))
		xbmcplugin.addDirectoryItem( handle = int(sys.argv[1]), url = "%s?action=list-reviews&plugin_category=%s&page=%i" % ( sys.argv[0], self.plugin_category, self.current_page + 1 ), listitem = listitem, isFolder = True)

		# Disable sorting...
		xbmcplugin.addSortMethod( handle = int( sys.argv[ 1 ] ), sortMethod = xbmcplugin.SORT_METHOD_NONE )
		
		# End of directory...
		xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded = True )
