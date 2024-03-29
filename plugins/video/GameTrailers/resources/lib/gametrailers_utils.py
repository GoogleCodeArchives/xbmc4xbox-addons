import zlib
import httplib
import urllib
import urllib2
import gzip
import StringIO
import urlparse

#
#
#
class HTTPCommunicator :
    #
    # POST
    #
    def post( self, host, url, params ):
        parameters  = urllib.urlencode( params )
        headers     = { "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Accept-Encoding" : "gzip" }
        connection  = httplib.HTTPConnection("%s:80" % host)
        
        connection.request( "POST", url, parameters, headers )
        response = connection.getresponse()
        
        # Compressed (gzip) response...
        if response.getheader( "content-encoding" ) == "gzip" :
            htmlGzippedData = response.read()
            stringIO       = StringIO.StringIO( htmlGzippedData )
            gzipper        = gzip.GzipFile( fileobj = stringIO )
            htmlData       = gzipper.read()
        # Plain text response...
        else :
            htmlData = response.read()

        # Cleanup
        connection.close()

        # Return value
        return htmlData

    #
    # GET
    #
    def get( self, url ):
        h = urllib2.HTTPHandler(debuglevel=0)
        
        request = urllib2.Request( url )
        request.add_header( "Accept-Encoding", "gzip" ) 
        opener = urllib2.build_opener(h)
        f = opener.open(request)

        # Compressed (gzip) response...
        if f.headers.get( "content-encoding" ) == "gzip" :
            htmlGzippedData = f.read()
            stringIO        = StringIO.StringIO( htmlGzippedData )
            gzipper         = gzip.GzipFile( fileobj = stringIO )
            htmlData        = gzipper.read()
            
            # Debug
            # print "[HTTP Communicator] GET %s" % url
            # print "[HTTP Communicator] Result size : compressed [%u], decompressed [%u]" % ( len( htmlGzippedData ), len ( htmlData ) )
            
        # Plain text response...
        else :
            htmlData = f.read()
        
        # Cleanup
        f.close()

        # Return value
        return htmlData

    #
    # Check if URL exists
    #
    def exists( self, url ):
        try :
            #urllib2.install_opener(
            #    urllib2.build_opener(
            #        urllib2.ProxyHandler({'http': 'http://localhost:9999'})
            #    )
            #)
            request            = urllib2.Request( url )
            request.get_method = lambda : 'HEAD'
            response           = urllib2.urlopen( request )
            response.close()
            return True
        except :
            return False