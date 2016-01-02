import os
import io
import re
import sys
import glob
import threading
import datetime
import traceback
import urllib
import base64
from qrcode import QRCode
from collections import defaultdict
from multiprocessing import Queue
import tornado.ioloop
import tornado.web
import Utils
from ParseHtmlPayload import ParseHtmlPayload
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
from StringIO import StringIO

reCrossMgrHtml = re.compile( r'^\d\d\d\d-\d\d-\d\d-.*\.html$' )
futureDate = datetime.datetime( datetime.datetime.now().year+20, 1, 1 )
with io.open( os.path.join(Utils.getImageFolder(), 'CrossMgr.ico'), 'rb' ) as f:
	favicon = f.read()

with io.open( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), 'rb' ) as f:
	DefaultLogoSrc = "data:image/png;base64," + base64.b64encode( f.read() )
	
with io.open( os.path.join(Utils.getImageFolder(), 'QRCodeIcon.png'), 'rb' ) as f:
	QRCodeIcon = f.read()

PORT_NUMBER = 8765

def validContent( content ):
	return content.strip().endswith( '</html>' )
	
class ContentBuffer( object ):
	Unchanged = 0
	Changed = 1
	ReadError = 2
	ContentError = 3
	
	def __init__( self ):
		self.fileCache = {}
		self.folder = None
		
	def updateFile( self, fname, forceUpdate=False ):
		if not self.folder:
			return None
		if not reCrossMgrHtml.match(os.path.basename(fname)):
			return None
		
		fnameFull = os.path.join( self.folder, fname )
		try:
			mtime = os.path.getmtime( fnameFull )
		except Exception as e:
			self.fileCache.pop( fname, None )
			return None
			
		cache = self.fileCache.get( fname, {} )
		if not forceUpdate and (cache.get('mtime',None) == mtime and cache.get('content',None)):
			cache['status'] = self.Unchanged
			return cache
			
		cache['status'] = self.Changed
		try:
			with io.open(fnameFull, encoding='utf-8') as f:
				content = f.read()
		except Exception as e:
			cache['status'] = self.ReadError
			return cache
			
		if not validContent(content):
			cache['status'] = self.ContentError
			content = ''
			
		cache['mtime'] = mtime
		cache['content'] = content
		result = ParseHtmlPayload( content=content )
		cache['payload'] = result['payload'] if result['success'] else {}
		self.fileCache[fname] = cache
		return cache
	
	def reset( self ):
		if self.folder:
			self.setFolder( self.folder )
	
	def setFolder( self, folder ):
		self.folder = folder
		self.fileCache = {}
		for f in glob.glob( os.path.join(folder, '*.html') ):
			self.updateFile( os.path.basename( f ) )
	
	def getFiles( self ):
		return [fname for fname, cache in sorted(
			self.fileCache.iteritems(),
			key=lambda x: (x[1]['payload'].get('raceScheduledStart',futureDate), x[0])
		)]
	
	def getCache( self, fname, checkForUpdate=True ):
		if checkForUpdate:
			cache = self.updateFile( fname )
		else:
			try:
				cache = self.fileCache[fname]
			except KeyError:
				cache = self.updateFile( fname, True )
		return cache
		
	def getContent( self, fname, checkForUpdate=True ):
		cache = self.getCache( fname, checkForUpdate=True )
		return cache.get('content', '') if cache else ''
		
	def getIndexInfo( self ):
		files = self.getFiles()
		result = {}
		for data in ('logoSrc', 'organizer'):
			result[data] = None
		for f in reversed(files):
			for key in result.iterkeys():
				if not result[key]:
					result[key] = self.fileCache[f]['payload'].get(key,None)
			if all( result.itervalues() ):
				break
		
		info = []
		for fname in files:
			cache = self.getCache( fname, False )
			if not cache:
				continue
			payload = cache.get('payload', {})
			info.append( (
					payload.get('raceScheduledStart',None),
					os.path.splitext(os.path.basename(fname))[0].strip('-')[11:],
					[(c['name'], urllib.pathname2url(c['name'])) for c in payload.get('catDetails',[]) if c['name'] != 'All'],
					urllib.pathname2url(fname),
					payload.get('raceIsRunning',False),
				)
			)
		result['info'] = info
		return result

#-----------------------------------------------------------------------

resourceLock = threading.Lock()
contentBuffer = ContentBuffer()
with io.open('Index.html', encoding='utf-8') as f:
	indexTemplate = tornado.template.Template( f.read() )

def queueListener( q ):
	resourceCmds = { 'results', 'tt_start' }
	while 1:
		message = q.get()
		cmd = message.get('cmd', None)
		if cmd == 'folder':
			with resourceLock:
				contentBuffer.setFolder( message['folder'] )
		elif cmd == 'results' or cmd == 'tt_start':
			with resourceLock:
				contentBuffer.updateFile( message['file_name'] )

'''
class HtmlHandler( tornado.web.RequestHandler ):
	def get( self, type=None, file_name=None ):
		if not type or type == 'Index':
			with resourceLock:
				return indexTemplate.generate( **contentBuffer.getIndexInfo() )
		else:
			with resourceLock:
				return contentBuffer.getContent( file_name )
'''

def getQRCodePage( url ):
	qr = QRCode()
	data = 'http://{}:{}{}'.format( Utils.GetDefaultHost(), PORT_NUMBER, url)
	qr.add_data( data )
	qr.make()
	qrcode = '["' + '",\n"'.join(
		[''.join( '1' if v else '0' for v in qr.modules[row] ) for row in xrange(qr.modules_count)]
	) + '"]'
	
	result = StringIO()
	def w( s ):
		result.write( s )
		result.write( '\n' )
	
	w( '<html>' )
	w( '<head>' )
	w( '''<style type="text/css">
body {
  font-family: sans-serif;
  text-align: center;
  }
</style>''' )
	w( '''<script>
function Draw() {
	var qrcode={qrcode};
	var c = document.getElementById("idqrcode");
	var ctx = c.getContext("2d");
	ctx.fillStyle = '#000';
	var s = Math.floor( c.width / qrcode.length );
	for( var y = 0; y < qrcode.length; ++y ) {
		var row = qrcode[y];
		for( var x = 0; x < row.length; ++x ) {
			if( row.charAt(x) == '1' )
				ctx.fillRect( x*s, y*s, s, s );
		}
	}
}
'''.replace('{qrcode}', qrcode) )
	w( '</script>' )
	w( '</head>' )
	w( '<body onload="Draw();">' )
	w( '<h1>Race Results Share</h1>' )
	w( '<canvas id="idqrcode" width="360" height="360"></canvas>' )
	w( '<h2>{}</h2>'.format(data) )
	w( '<br/>' )
	w( 'Powered by <a href="http://www.sites.google.com/site/crossmgrsoftware">CrossMgr</a>.' )
	w( '</body>' )
	w( '</html>' )
	return result.getvalue().encode( 'utf8' )

def getIndexPage( share=True ):
	with resourceLock:
		info = contentBuffer.getIndexInfo()
	info['share'] = share
	return indexTemplate.generate( **info ).encode('utf8')
#---------------------------------------------------------------------------

class CrossMgrHandler( BaseHTTPRequestHandler ):
	
	#Handler for the GET requests
	def do_GET(self):
		up = urlparse.urlparse( self.path )
		content_type = 'text/html; charset=utf-8'
		try:
			if up.path=="/":
				content = getIndexPage()
			elif up.path=='/favicon.ico':
				content_type = 'image/x-icon'
				content = favicon
			elif up.path=='/qrcode.png':
				content_type = 'image/png'
				content = QRCodeIcon
			elif up.path=='/qrcode.html':
				content = getQRCodePage( '/' )
			else:
				file = urllib.url2pathname(os.path.basename(up.path))
				with resourceLock:
					content = contentBuffer.getContent( file ).encode('utf8')
		except Exception as e:
			self.send_error(404,'File Not Found: {} {}\n{}'.format(self.path, e, traceback.format_exc()))
			return
		
		self.send_response( 200 )
		self.send_header('Content-type',content_type)
		self.end_headers()
		self.wfile.write( content )

'''
try:
	#Create a web server and define the handler to manage the
	#incoming request
	server = HTTPServer(('', PORT_NUMBER), CrossMgrHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	
	#Wait forever for incoming htto requests
	server.serve_forever()

except KeyboardInterrupt:
	print '^C received, shutting down the web server'
	server.socket.close()
'''

#--------------------------------------------------------------------------

def WebServer( queue ):
	thread = threading.Thread( target=queueListener, name='queueListener', args=(queue,) )
	thread.daemon = True
	thread.start()
	
	server = HTTPServer(('', PORT_NUMBER), CrossMgrHandler)
	print 'Started httpserver on port ' , PORT_NUMBER
	server.serve_forever()

if __name__ == '__main__':
	q = Queue()
	q.put( {'cmd':'folder', 'folder':'Gemma'} )
	WebServer( q )
	
