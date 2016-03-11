import os
import io
import re
import sys
import glob
import time
import threading
import datetime
import traceback
import urllib
import base64
from collections import defaultdict
from Queue import Queue
import socket
try:
    # Python 2.x
    from SocketServer import ThreadingMixIn
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
except ImportError:
    # Python 3.x
    from socketserver import ThreadingMixIn
    from http.server import SimpleHTTPRequestHandler, HTTPServer

from qrcode import QRCode
from tornado.template import Template
from ParseHtmlPayload import ParseHtmlPayload
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import urlparse
from StringIO import StringIO
import Utils
import Model
from Synchronizer import syncfunc

from ThreadPoolMixIn import ThreadPoolMixIn
class CrossMgrServer(ThreadPoolMixIn, HTTPServer):
    pass

reCrossMgrHtml = re.compile( r'^\d\d\d\d-\d\d-\d\d-.*\.html$' )
futureDate = datetime.datetime( datetime.datetime.now().year+20, 1, 1 )

with io.open( os.path.join(Utils.getImageFolder(), 'CrossMgr.ico'), 'rb' ) as f:
	favicon = f.read()
with io.open( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), 'rb' ) as f:
	DefaultLogoSrc = "data:image/png;base64," + base64.b64encode( f.read() )
with io.open( os.path.join(Utils.getImageFolder(), 'QRCodeIcon.png'), 'rb' ) as f:
	QRCodeIconSrc = "data:image/png;base64," + base64.b64encode( f.read() )
with io.open( os.path.join(Utils.getImageFolder(), 'stopwatch-32px.png'), 'rb' ) as f:
	StopwatchIconSrc = "data:image/png;base64," + base64.b64encode( f.read() )
with io.open(os.path.join(Utils.getHtmlFolder(), 'Index.html'), encoding='utf-8') as f:
	indexTemplate = Template( f.read() )

PORT_NUMBER = 8765

def validContent( content ):
	return content.strip().endswith( '</html>' )

@syncfunc
def getCurrentHtml():
	return Model.getCurrentHtml()
	
@syncfunc
def getCurrentTTStartHtml():
	print 'getCurrentTTStartHtml: called'
	return Model.getCurrentTTStartHtml()
	
def coreName( fname ):
	return os.path.splitext(os.path.basename(fname).split('?')[0])[0].replace('_TTStart','').strip('-')

class Generic( object ):
	def __init__( self, **kwargs ):
		self.__dict__.update( kwargs )

class ContentBuffer( object ):
	Unchanged = 0
	Changed = 1
	ReadError = 2
	ContentError = 3

	def __init__( self ):
		self.fileCache = {}
		self.fnameRace = None
		self.dirRace = None
		self.lock = threading.Lock()
	
	def _updateFile( self, fname, forceUpdate=False ):
		if not self.fnameRace:
			return None
		fnameBase = os.path.basename(fname).split('?')[0]
		if not (reCrossMgrHtml.match(fnameBase) or fnameBase == 'Simulation.html' or fnameBase == 'Simulation_TTStart.html'):
			return None
		
		cache = self.fileCache.get( fname, {} )
		
		fnameFull = os.path.join( self.dirRace, fname )
		race = Model.race
		if race and self.fnameRace and coreName(self.fnameRace) == coreName(fnameFull):
			if race.lastChangedTime <= cache.get('mtime',0.0):
				return cache
			
			content = getCurrentTTStartHtml() if '_TTStart' in fname else getCurrentHtml()
			if content:
				cache['mtime'] = time.time()
				result = ParseHtmlPayload( content=content )
				cache['payload'] = result['payload'] if result['success'] else {}
				cache['content'] = content.encode('utf-8')
				self.fileCache[fname] = cache
				return cache
			
		try:
			mtime = os.path.getmtime( fnameFull )
		except Exception as e:
			self.fileCache.pop( fname, None )
			return None
			
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
		result = ParseHtmlPayload( content=content )
		cache['payload'] = result['payload'] if result['success'] else {}
		cache['content'] = content.encode('utf-8')
		self.fileCache[fname] = cache
		return cache
	
	def reset( self ):
		if self.fnameRace:
			self.setFolder( self.fnameRace )
	
	def setFNameRace( self, fnameRace ):
		with self.lock:
			self.fnameRace = fnameRace
			self.dirRace = os.path.dirname( fnameRace )
			self.fileCache = {}
			newRace = True
			for f in glob.glob( os.path.join(self.dirRace, '*.html') ):
				self._updateFile( os.path.basename(f) )
				if coreName(fnameRace) == coreName(f):
					newRace = False
			if newRace:
				self._updateFile( '/' + os.path.basename(fnameRace) )
	
	def _getFiles( self ):
		return [fname for fname, cache in sorted(
			self.fileCache.iteritems(),
			key=lambda x: (x[1]['payload'].get('raceScheduledStart',futureDate), x[0])
		) if not fname.endswith('_TTStart.html')]
	
	def _getCache( self, fname, checkForUpdate=True ):
		if checkForUpdate:
			cache = self._updateFile( fname )
		else:
			try:
				cache = self.fileCache[fname]
			except KeyError:
				cache = self._updateFile( fname, True )
		return cache
		
	def getContent( self, fname, checkForUpdate=True ):
		with self.lock:
			cache = self._getCache( fname, checkForUpdate )
			return cache.get('content', '') if cache else ''
		
	def getIndexInfo( self ):
		with self.lock:
			race = Model.race
			result = {
				'logoSrc': race.headerImage or DefaultLogoSrc,
				'organizer': race.organizer,
			}
			
			files = self._getFiles()
			info = []
			for fname in files:
				cache = self._getCache( fname, False )
				if not cache:
					continue
				payload = cache.get('payload', {})
				fnameShow = os.path.splitext(os.path.basename(fname))[0].strip('-')
				if fnameShow != 'Simulation':
					fnameShow = fnameShow[11:]
				g = Generic(
					raceScheduledStart = payload.get('raceScheduledStart',None),
					name = fnameShow,
					categories = [(c['name'], urllib.pathname2url(c['name']))
						for c in payload.get('catDetails',[]) if c['name'] != 'All'],
					url = urllib.pathname2url(fname),
					isTimeTrial = payload.get('isTimeTrial',False),
					raceIsRunning = payload.get('raceIsRunning',False),
					raceIsFinished = payload.get('raceIsFinished',False),
				)
				if g.isTimeTrial:
					g.urlTTStart = urllib.pathname2url(os.path.splitext(fname)[0] + '_TTStart.html')
				info.append( g )
			
			result['info'] = info
			return result

#-----------------------------------------------------------------------

contentBuffer = ContentBuffer()
DEFAULT_HOST = None
def SetFileName( fname ):
	if fname.endswith( '.cmn' ):
		fname = os.path.splitext( fname )[0] + '.html'
	q.put( {'cmd':'fileName', 'fileName':fname} )

def getQRCodePage( urlPage ):
	qr = QRCode()
	qr.add_data( urlPage )
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
	w( '<h1 style="margin-top: 32px;">Share Race Results</h1>' )
	w( '<canvas id="idqrcode" width="360" height="360"></canvas>' )
	w( '<h2>Scan the QRCode.<br/>Follow it to the Race Results page.</h2>' )
	w( '<h2>{}</h2>'.format(urlPage) )
	w( 'Powered by <a href="http://www.sites.google.com/site/crossmgrsoftware">CrossMgr</a>.' )
	w( '</body>' )
	w( '</html>' )
	return result.getvalue().encode( 'utf-8' )

def getIndexPage( share=True ):
	info = contentBuffer.getIndexInfo()
	info.update( {
		'share': share,
		'QRCodeIconSrc':  QRCodeIconSrc,
		'StopwatchIconSrc': StopwatchIconSrc,
	} )
	return indexTemplate.generate( **info ).encode('utf-8')

#---------------------------------------------------------------------------

def WriteHtmlIndexPage():
	fname = os.path.join( os.path.dirname(Utils.getFileName()), 'index.html' )
	try:
		with io.open(fname, 'rb') as f:
			previousContent = f.read()
	except Exception as e:
		previousContent = ''
	
	content = getIndexPage(share=False)
	if content != previousContent:
		with io.open(fname, 'wb') as f:
			f.write( getIndexPage(share=False) )
	return fname

class CrossMgrHandler( BaseHTTPRequestHandler ):
	html_content = 'text/html; charset=utf-8'
	
	def do_GET(self):
		up = urlparse.urlparse( self.path )
		try:
			if up.path=="/":
				content = getIndexPage()
				content_type = self.html_content
			elif up.path=='/favicon.ico':
				content = favicon
				content_type = 'image/x-icon'
			elif up.path=='/qrcode.html':
				urlPage = GetCrossMgrHomePage()
				content = getQRCodePage( urlPage )
				content_type = self.html_content
			else:
				file = urllib.url2pathname(os.path.basename(up.path))
				content = contentBuffer.getContent( file )
				content_type = self.html_content
		except Exception as e:
			self.send_error(404,'File Not Found: {} {}\n{}'.format(self.path, e, traceback.format_exc()))
			return
		
		self.send_response( 200 )
		self.send_header('Content-type',content_type)
		if content_type == self.html_content:
			self.send_header( 'Cache-Control', 'no-cache, no-store, must-revalidate' )
			self.send_header( 'Pragma', 'no-cache' )
			self.send_header( 'Expires', '0' )
		self.end_headers()
		self.wfile.write( content )
	
	def log_message(self, format, *args):
		return

#--------------------------------------------------------------------------
def GetCrossMgrHomePage( ip=None ):
	if ip is None:
		ip = not sys.platform.lower().startswith('win')
	
	if ip:
		hostname = DEFAULT_HOST
	else:
		hostname = socket.gethostname()
		try:
			socket.gethostbyname( hostname )
		except:
			hostname = DEFAULT_HOST
	return 'http://{}:{}'.format(hostname, PORT_NUMBER)

server = None
def WebServer():
	global server
	while 1:
		try:
			server = CrossMgrServer(('', PORT_NUMBER), CrossMgrHandler)
			server.init_thread_pool()
			server.serve_forever( poll_interval = 2 )
		except Exception as e:
			server = None
			time.sleep( 5 )

def queueListener( q ):
	global DEFAULT_HOST, server
	
	DEFAULT_HOST = Utils.GetDefaultHost()
	keepGoing = True
	while keepGoing:
		message = q.get()
		cmd = message.get('cmd', None)
		if cmd == 'fileName':
			DEFAULT_HOST = Utils.GetDefaultHost()
			contentBuffer.setFNameRace( message['fileName'] )
		
		if cmd == 'exit':
			keepGoing = False
		q.task_done()
	
	if server:
		server.shutdown()
		server = None

q = Queue()
qThread = threading.Thread( target=queueListener, name='queueListener', args=(q,) )
qThread.daemon = True
qThread.start()

webThread = threading.Thread( target=WebServer, name='WebServer' )
webThread.daemon = True
webThread.start()

if __name__ == '__main__':
	SetFileName( os.path.join('Gemma', '2015-11-10-A Men-r4-.html') )
	print 'Started httpserver on port ' , PORT_NUMBER
	try:
		time.sleep( 10000 )
	except KeyboardInterrupt:
		q.put( {'cmd':'exit'} )

