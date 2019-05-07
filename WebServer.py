import os
import io
import re
import six
import sys
import gzip
import glob
import time
import json
import base64
urllib = six.moves.urllib
from six.moves.urllib.parse import quote
from six.moves.urllib.request import url2pathname
import socket
import datetime
import traceback
import threading
from collections import defaultdict
from six.moves.queue import Queue, Empty
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
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
StringIO = six.StringIO
import Utils
import Model
from GetResults import GetResultsRAM, GetResultsBaseline, GetRaceName
from Synchronizer import syncfunc

from ThreadPoolMixIn import ThreadPoolMixIn
class CrossMgrServer(ThreadPoolMixIn, HTTPServer):
    pass

now = datetime.datetime.now
reCrossMgrHtml = re.compile( r'^\d\d\d\d-\d\d-\d\d-.*\.html$' )
futureDate = datetime.datetime( now().year+20, 1, 1 )

with io.open( os.path.join(Utils.getImageFolder(), 'CrossMgr.ico'), 'rb' ) as f:
	favicon = f.read()

def readBase64( fname ):
	with io.open( os.path.join(Utils.getImageFolder(), fname), 'rb' ) as f:
		return "data:image/png;base64," + base64.b64encode( f.read() ).decode('ascii')

with io.open( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), 'rb' ) as f:
	DefaultLogoSrc = readBase64('CrossMgrHeader.png')

icons = {
	'QRCodeIconSrc': readBase64('QRCodeIcon.png'),
	'CountdownIconSrc': readBase64('countdown.png'),
	'StartListIconSrc': readBase64('tt_start_list.png'),
	'LapCounterIconSrc':  readBase64('lapcounter.png'), 
	'ResultsCurrentIconSrc': readBase64('results_current.png'),
	'ResultsPreviousIconSrc': readBase64('results_previous.png'),
	'AnnouncerIconSrc': readBase64('announcer.png'),
}

with io.open(os.path.join(Utils.getHtmlFolder(), 'Index.html'), encoding='utf-8') as f:
	indexTemplate = Template( f.read() )

PORT_NUMBER = 8765

def gzipEncode( content ):
	if six.PY2:
		out = StringIO()
		with gzip.GzipFile( fileobj=out, mode='w', compresslevel=5 ) as f:
			f.write( content.encode(encoding='utf-8') )
		return out.getvalue()
	else:
		out = io.BytesIO()
		with gzip.GzipFile( fileobj=out, mode='wb', compresslevel=5 ) as f:
			f.write( content.encode() if not isinstance(content, bytes) else content )
		return out.getbuffer()

def validContent( content ):
	return content.strip().endswith( '</html>' )

@syncfunc
def getCurrentHtml():
	return Model.getCurrentHtml()
	
@syncfunc
def getCurrentTTCountdownHtml():
	return Model.getCurrentTTCountdownHtml()
	
@syncfunc
def getCurrentTTStartListHtml():
	return Model.getCurrentTTStartListHtml()
	
with io.open(os.path.join(Utils.getHtmlFolder(), 'LapCounter.html')) as f:
	lapCounterTemplate = f.read().encode()
def getLapCounterHtml():
	return lapCounterTemplate
	
with io.open(os.path.join(Utils.getHtmlFolder(), 'Announcer.html')) as f:
	announcerHTML = f.read().encode()
def getAnnouncerHtml():
	return announcerHTML
	
def coreName( fname ):
	return os.path.splitext(os.path.basename(fname).split('?')[0])[0].replace('_TTCountdown','').replace('_TTStartList','').strip('-')

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
			
		if '_TTCountdown' in fname:		# Force update the countdown so we get a valid timestamp.
			forceUpdate = True
		
		fnameBase = os.path.basename(fname).split('?')[0]
		race = Model.race
		if 'CoursePreview.html' in fnameBase or not reCrossMgrHtml.match(fnameBase):
			return None
		
		cache = self.fileCache.get( fname, {} )
		
		fnameFull = os.path.join( self.dirRace, fname )
		if race and self.fnameRace and coreName(self.fnameRace) == coreName(fnameFull):
			if forceUpdate or race.lastChangedTime > cache.get('mtime',0.0):
				
				if '_TTCountdown' in fname:
					content = getCurrentTTCountdownHtml()
				elif '_TTStartList' in fname:
					content = getCurrentTTStartListHtml()
				else:
					content = getCurrentHtml()
				
				if content:
					cache['mtime'] = time.time()
					result = ParseHtmlPayload( content=content )
					cache['payload'] = result['payload'] if result['success'] else {}
					if six.PY2:
						cache['content'] = content
						cache['gzip_content'] = gzipEncode( content )
					else:
						cache['content'] = content.encode() if not isinstance(content, bytes) else content
						cache['gzip_content'] = gzipEncode( content )
					cache['status'] = self.Changed
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
		cache['gzip_content'] = gzipEncode( cache['content'] )
		self.fileCache[fname] = cache
		return cache
	
	def reset( self ):
		if self.fnameRace:
			self.setFNameRace( self.fnameRace )
	
	def setFNameRace( self, fnameRace ):
		with self.lock:
			self.fnameRace = fnameRace
			self.dirRace = os.path.dirname( fnameRace )
			coreNameRace = coreName( os.path.basename(fnameRace) )
			
			self.fileCache = {}
			self._updateFile( os.path.splitext(os.path.basename(fnameRace))[0] + '.html' )
			for f in glob.glob( os.path.join(self.dirRace, '*.html') ):
				self._updateFile( os.path.basename(f), coreName(os.path.basename(f)) == coreNameRace )
	
	def _getFiles( self ):
		return [fname for fname, cache in sorted(
			six.iteritems(self.fileCache),
			key=lambda x: (x[1]['payload'].get('raceScheduledStart',futureDate), x[0])
		) if not (fname.endswith('_TTCountdown.html') or fname.endswith('_TTStartList.html'))]
	
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
			if cache:
				return cache.get('content', ''), cache.get('gzip_content', None)
			return '', None
		
	def getIndexInfo( self ):
		with self.lock:
			race = Model.race
			if not race:
				return {}
			
			result = {
				'logoSrc': race.headerImage or DefaultLogoSrc,
				'organizer': race.organizer.encode(),
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
					categories = [
							(
								c['name'].encode(),
								quote(six.text_type(c['name']).encode()),
								c.get( 'starters', 0 ),
								c.get( 'finishers', 0 ),
							)
						for c in payload.get('catDetails',[]) if c['name'] != 'All'],
					url = urllib.request.pathname2url(fname),
					isTimeTrial = payload.get('isTimeTrial',False),
					raceIsRunning = payload.get('raceIsRunning',False),
					raceIsFinished = payload.get('raceIsFinished',False),
				)
				if g.isTimeTrial:
					g.urlTTCountdown = urllib.request.pathname2url(os.path.splitext(fname)[0] + '_TTCountdown.html')
					g.urlTTStartList = urllib.request.pathname2url(os.path.splitext(fname)[0] + '_TTStartList.html')
				else:
					g.urlLapCounter = urllib.request.pathname2url('LapCounter.html')
				info.append( g )
			
			result['info'] = info
			return result

#-----------------------------------------------------------------------

contentBuffer = ContentBuffer()
DEFAULT_HOST = None
def SetFileName( fname ):
	if fname.endswith( '.cmn' ):
		fname = os.path.splitext(fname)[0] + '.html'
	q.put( {'cmd':'fileName', 'fileName':fname} )

def GetPreviousFileName():
	file = None
	try:
		fnameCur = os.path.splitext(Model.race.getFileName())[0] + '.html'
	except:
		fnameCur = None
	
	files = contentBuffer._getFiles()
	try:
		file = files[files.index(fnameCur)-1]
	except:
		pass
	if file is None:
		try:
			file = files[-1]
		except:
			pass
	return file
	
def getQRCodePage( urlPage ):
	qr = QRCode()
	qr.add_data( urlPage )
	qr.make()
	qrcode = '["' + '",\n"'.join(
		[''.join( '1' if v else '0' for v in qr.modules[row] ) for row in six.moves.range(qr.modules_count)]
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
	return result.getvalue().encode()

def getIndexPage( share=True ):
	info = contentBuffer.getIndexInfo()
	if not info:
		return ''
	info['share'] = share
	info.update( icons )
	return indexTemplate.generate( **info )

#---------------------------------------------------------------------------

def WriteHtmlIndexPage():
	fname = os.path.join( os.path.dirname(Utils.getFileName()), 'index.html' )
	try:
		with io.open(fname, 'rb') as f:	# Read as bytes as the index pages is already utf-8 encoded.
			previousContent = f.read()
	except Exception as e:
		previousContent = ''
	
	content = getIndexPage(share=False)
	if content != previousContent:
		with io.open(fname, 'wb') as f:	# Write as bytes as the index pages is already utf-8 encoded.
			f.write( getIndexPage(share=False) )
	return fname

class CrossMgrHandler( BaseHTTPRequestHandler ):
	html_content = 'text/html; charset=utf-8'
	json_content = 'application/json'
	reLapCounterHtml = re.compile( r'^\/LapCounter[\d-]*\.html$' )
	
	def do_GET(self):
		up = urllib.parse.urlparse( self.path )		
		content, gzip_content = None,  None
		try:
			if up.path=='/':
				content = getIndexPage()
				content_type = self.html_content
				assert isinstance( content, bytes )
			elif up.path=='/favicon.ico':
				content = favicon
				content_type = 'image/x-icon'
				assert isinstance( content, bytes )
			elif self.reLapCounterHtml.match( up.path ):
				content = getLapCounterHtml()
				content_type = self.html_content
				assert isinstance( content, bytes )
			elif up.path=='/Announcer.html':
				content = getAnnouncerHtml()
				content_type = self.html_content
				assert isinstance( content, bytes )
			elif up.path=='/qrcode.html':
				urlPage = GetCrossMgrHomePage()
				content = getQRCodePage( urlPage )
				content_type = self.html_content
				assert isinstance( content, bytes )
			elif up.path=='/servertimestamp.html':
				content = Utils.ToJSon( {
						'servertime':time.time()*1000.0,
						'requesttimestamp':float(up.query),
					}
				).encode()
				content_type = self.json_content;
				assert isinstance( content, bytes )
			else:
				file = None
				
				if up.path == '/CurrentResults.html':
					try:
						file = os.path.splitext(Model.race.getFileName())[0] + '.html'
					except:
						pass
				
				elif up.path == '/PreviousResults.html':
					file = GetPreviousFileName()
				
				if file is None: 
					file = url2pathname(os.path.basename(up.path))
				content, gzip_content = contentBuffer.getContent( file )
				content_type = self.html_content
				assert isinstance( content, bytes )
		except Exception as e:
			self.send_error(404,'File Not Found: {} {}\n{}'.format(self.path, e, traceback.format_exc()))
			return
		
		self.send_response( 200 )
		self.send_header('Content-Type',content_type)
		if content_type == self.html_content:
			if gzip_content and 'Accept-Encoding' in self.headers and 'gzip' in self.headers['Accept-Encoding']:
				content = gzip_content
				self.send_header( 'Content-Encoding', 'gzip' )
			self.send_header( 'Cache-Control', 'no-cache, no-store, must-revalidate' )
			self.send_header( 'Pragma', 'no-cache' )
			self.send_header( 'Expires', '0' )
		self.send_header( 'Content-Length', len(content) )
		self.end_headers()
		self.wfile.write( content )
	
	def log_message(self, format, *args):
		return

#--------------------------------------------------------------------------
def GetCrossMgrHomePage( ip=None ):
	if ip is None:
		ip = not sys.platform.lower().startswith('win')
		ip = True
	
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
		elif cmd == 'exit':
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

from websocket_server import WebsocketServer
#-------------------------------------------------------------------

def message_received(client, server, message):
	msg = json.loads( message )
	if msg['cmd'] == 'send_baseline' and (msg['raceName'] == 'CurrentResults' or msg['raceName'] == GetRaceName()):
		server.send_message( client, json.dumps(GetResultsBaseline()) )

wsServer = None
def WsServerLaunch():
	global wsServer
	while 1:
		try:
			wsServer = WebsocketServer( port=PORT_NUMBER + 1, host='' )
			wsServer.set_fn_message_received( message_received )
			wsServer.run_forever()
		except Exception as e:
			wsServer = None
			time.sleep( 5 )

def WsQueueListener( q ):
	global wsServer
	
	keepGoing = True
	while keepGoing:
		message = q.get()
		if message.get('cmd', None) == 'exit':
			keepGoing = False
		elif wsServer and wsServer.hasClients():
			wsServer.send_message_to_all( Utils.ToJSon(message).encode() )
		q.task_done()
	
	wsServer = None	

wsQ = Queue()
wsQThread = threading.Thread( target=WsQueueListener, name='WsQueueListener', args=(wsQ,) )
wsQThread.daemon = True
wsQThread.start()

wsThread = threading.Thread( target=WsServerLaunch, name='WsServer' )
wsThread.daemon = True
wsThread.start()

wsTimer = tTimerStart = None
def WsPost():
	global wsServer, wsTimer, tTimerStart
	if wsServer and wsServer.hasClients():
		while 1:
			try:
				ram = GetResultsRAM()
				break
			except AttributeError:
				time.sleep( 0.25 )
		if ram:
			wsQ.put( ram )
	if wsTimer:
		wsTimer.cancel()
	wsTimer = tTimerStart = None

def WsRefresh( updatePrevious=False ):
	global wsTimer, tTimerStart
	
	if updatePrevious:
		wsQ.put( {'cmd':'reload_previous'} )
		return
	
	# If we have a string of competitors, don't send the update
	# until there is a gap of a second or more between arrivals.
	if not tTimerStart:
		tTimerStart = now()
	else:
		# Check if it has been 5 seconds since the last update.
		# If so, let the currently scheduled update fire.
		if (now() - tTimerStart).total_seconds() > 5.0:
			return
		wsTimer.cancel()

	# Schedule an update to be sent in the next second.
	# This either schedules the first update, or extends a pending update.
	wsTimer = threading.Timer( 1.0, WsPost )
	wsTimer.start()
			
#-------------------------------------------------------------------
def GetLapCounterRefresh():
	try:
		return Utils.mainWin.lapCounter.GetState()
	except:
		return {
			'cmd': 'refresh',
			'labels': [],
			'foregrounds': [],
			'backgrounds': [],
			'raceStartTime': None,
			'lapElapsedClock': False,
		}

def lap_counter_new_client(client, server):
	server.send_message( client, json.dumps(GetLapCounterRefresh()) )

wsLapCounterServer = None
def WsLapCounterServerLaunch():
	global wsLapCounterServer
	while 1:
		try:
			wsLapCounterServer = WebsocketServer( port=PORT_NUMBER + 2, host='' )
			wsLapCounterServer.set_fn_new_client( lap_counter_new_client )
			wsLapCounterServer.run_forever()
		except Exception as e:
			wsLapCounterServer = None
			time.sleep( 5 )

def WsLapCounterQueueListener( q ):
	global wsLapCounterServer
		
	keepGoing = True
	while keepGoing:
		message = q.get()
		cmd = message.get('cmd', None)
		if cmd == 'refresh':
			if wsLapCounterServer and wsLapCounterServer.hasClients():
				race = Model.race
				message['tNow'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
				message['curRaceTime'] = race.curRaceTime() if race and race.startTime else 0.0
				wsLapCounterServer.send_message_to_all( Utils.ToJSon(message).encode() )
		elif cmd == 'exit':
			keepGoing = False
		q.task_done()
	
	wsLapCounterServer = None	

wsLapCounterQ = Queue()
wsLapCounterQThread = threading.Thread( target=WsLapCounterQueueListener, name='WsLapCounterQueueListener', args=(wsLapCounterQ,) )
wsLapCounterQThread.daemon = True
wsLapCounterQThread.start()

wsLapCounterThread = threading.Thread( target=WsLapCounterServerLaunch, name='WsLapCounterServer' )
wsLapCounterThread.daemon = True
wsLapCounterThread.start()

lastRaceName, lastMessage = None, None
def WsLapCounterRefresh():
	global lastRaceName, lastMessage
	race = Model.race
	if not (race and race.isRunning()):
		return
	if not (wsLapCounterServer and wsLapCounterServer.hasClients()):
		return
	message, raceName = GetLapCounterRefresh(), GetRaceName()
	if lastMessage != message or lastRaceName != raceName:
		wsLapCounterQ.put( message )
		lastMessage, lastRaceName = message, raceName
			
if __name__ == '__main__':
	SetFileName( os.path.join('Gemma', '2015-11-10-A Men-r4-.html') )
	six.print_( 'Started httpserver on port ' , PORT_NUMBER )
	try:
		time.sleep( 10000 )
	except KeyboardInterrupt:
		q.put( {'cmd':'exit'} )

