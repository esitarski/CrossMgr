import wx
import os
import io
import re
import sys
import gzip
import glob
import time
import json
import base64
import urllib
import socket
import datetime
import traceback
import threading
from urllib.parse import quote

from urllib.request import url2pathname
from queue import Queue

from qrcode import QRCode
from tornado.template import Template
from ParseHtmlPayload import ParseHtmlPayload
from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus
from io import StringIO
import Utils
import Model
import Version
import WebReader
from GetResults import GetResultsRAM, GetResultsBaseline, GetRaceName
from PhotoFinish		import okTakePhoto
from Synchronizer import syncfunc
from SendPhotoRequests import SendPhotoRequests

# import LockLog
# Lock, RLock = LockLog.Lock, LockLog.RLock
Lock, RLock = threading.Lock, threading.RLock

from ThreadPoolMixIn import ThreadPoolMixIn
class CrossMgrServer(ThreadPoolMixIn, HTTPServer):
	pass
    
def epochMilliseconds():
	return time.time_ns() / 1000000.0		# milliseconds since epoch.
    
def epochTime():
	return time.time_ns() / 1000000000.0	# seconds since epoch.
	
now = datetime.datetime.now
reCrossMgrHtml = re.compile( r'^\d\d\d\d-\d\d-\d\d-.*\.html$' )
futureDate = datetime.datetime( now().year+20, 1, 1 )

with open( os.path.join(Utils.getImageFolder(), 'CrossMgr.ico'), 'rb' ) as f:
	favicon = f.read()

def readBase64( fname ):
	with open( os.path.join(Utils.getImageFolder(), fname), 'rb' ) as f:
		return "data:image/png;base64," + base64.b64encode( f.read() ).decode('ascii')

with open( os.path.join(Utils.getImageFolder(), 'CrossMgrHeader.png'), 'rb' ) as f:
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

with open(os.path.join(Utils.getHtmlFolder(), 'Index.html'), encoding='utf8') as f:
	indexTemplate = Template( f.read() )

PORT_NUMBER = 8765

def gzipEncode( content ):
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

with open(os.path.join(Utils.getHtmlFolder(), 'LapCounter.html'), encoding='utf8') as f:
	lapCounterTemplate = f.read().encode()
def getLapCounterHtml():
	return lapCounterTemplate
	
with open(os.path.join(Utils.getHtmlFolder(), 'Announcer.html'), encoding='utf8') as f:
	announcerHTML = f.read().encode()
def getAnnouncerHtml():
	return announcerHTML
	
def coreName( fname ):
	return os.path.splitext(os.path.basename(fname).split('?')[0])[0].replace('_TTCountdown','').replace('_TTStartList','').strip('-')

class Generic:
	def __init__( self, **kwargs ):
		self.__dict__.update( kwargs )

class ContentBuffer:
	'''
		Underscore functions require the lock before calling.
	'''
	Unchanged = 0
	Changed = 1
	ReadError = 2
	ContentError = 3

	def __init__( self ):
		self.fileCache = {}
		self.fnameRace = None
		self.dirRace = None
		self.lock = RLock()
	
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
					cache['mtime'] = epochTime()
					result = ParseHtmlPayload( content=content )
					cache['payload'] = result['payload'] if result['success'] else {}
					cache['content'] = content.encode() if not isinstance(content, bytes) else content
					cache['gzip_content'] = gzipEncode( content )
					cache['status'] = self.Changed
					self.fileCache[fname] = cache
			
			return cache
			
		try:
			mtime = os.path.getmtime( fnameFull )
		except Exception:
			self.fileCache.pop( fname, None )
			return None
			
		if not forceUpdate and (cache.get('mtime',None) == mtime and cache.get('content',None)):
			cache['status'] = self.Unchanged
			return cache
			
		cache['status'] = self.Changed
		try:
			with open(fnameFull, encoding='utf8') as f:
				content = f.read()
		except Exception:
			cache['status'] = self.ReadError
			return cache
			
		if not validContent(content):
			cache['status'] = self.ContentError
			content = ''
			
		cache['mtime'] = mtime
		result = ParseHtmlPayload( content=content )
		cache['payload'] = result['payload'] if result['success'] else {}
		cache['content'] = content.encode() if not isinstance(content, bytes) else content
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
		
		with self.lock:
			self.fileCache = {}
			self._updateFile( os.path.splitext(os.path.basename(fnameRace))[0] + '.html' )
		
			for f in glob.glob( os.path.join(self.dirRace, '*.html') ):
				self._updateFile( os.path.basename(f), coreName(os.path.basename(f)) == coreNameRace )
	
	def _getFiles( self ):
		return [fname for fname, cache in sorted(
			self.fileCache.items(),
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
		race = Model.race
		if not race:
			return {}
		
		result = {
			'logoSrc': race.headerImage or DefaultLogoSrc,
			'organizer': race.organizer.encode(),
		}
		
		with self.lock:
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
								quote('{}'.format(c['name']).encode()),
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
	except Exception:
		fnameCur = None
	
	files = contentBuffer._getFiles()
	try:
		file = files[files.index(fnameCur)-1]
	except Exception:
		pass
	if file is None:
		try:
			file = files[-1]
		except Exception:
			pass
	return file
	
def getQRCodePage( urlPage ):
	qr = QRCode()
	qr.add_data( urlPage )
	qr.make()
	qrcode = '["' + '",\n"'.join(
		[''.join( '1' if v else '0' for v in qr.modules[row] ) for row in range(qr.modules_count)]
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
	w( '<h1 style="margin-top: 32px;">Share Competition Results</h1>' )
	w( '<canvas id="idqrcode" width="360" height="360"></canvas>' )
	w( '<h2>Scan the QRCode.<br/>Follow it to the Competition Results page.</h2>' )
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
		with open(fname, 'rb') as f:	# Read as bytes as the index page is already utf-8 encoded.
			previousContent = f.read()
	except Exception:
		previousContent = ''
	
	content = getIndexPage(share=False)
	if content != previousContent:
		with open(fname, 'wb') as f:	# Write as bytes as the index page is already utf-8 encoded.
			f.write( getIndexPage(share=False) )
	return fname

class CrossMgrHandler( BaseHTTPRequestHandler ):
	html_content = 'text/html; charset=utf-8'
	json_content = 'application/json'
	reLapCounterHtml = re.compile( r'^\/LapCounter[0-9A-Z-]*\.html$' )
	
	def do_POST( self ):
		up = urllib.parse.urlparse( self.path )
		try:
			if up.path == '/rfid.js':
				# Accept RFID input as json.  Assume all time corrections have been done by the client.
				content_len = int(self.headers.get('Content-Length'))
				post_body = self.rfile.read(content_len)
				success = True
				try:
					rfid_data = json.loads( post_body )
				except Exception as e:
					success = False
					wx.CallAfter( Utils.writeLog, str(post_body) )
					wx.CallAfter( Utils.logException, e, sys.exc_info() )
					
				if success:
					data = []
					for d in rfid_data['data']:
						try:
							data.append( ('data', d['tag'], datetime.datetime.fromisoformat( d['t'] )) )
						except Exception as e:
							wx.CallAfter( Utils.writeLog, str(d) )
							wx.CallAfter( Utils.logException, e, sys.exc_info() )
					WebReader.SetData( data )					
					wx.CallAfter( Utils.refresh )
					
				self.send_response( HTTPStatus.OK if success else HTTPStatus.BAD_REQUEST )
				self.end_headers()
			
			elif up.path == '/bib.js':
				# Accept Bib input as json.  Assume all time corrections have been done by the client.
				content_len = int(self.headers.get('Content-Length'))
				post_body = self.rfile.read(content_len)
				success = True
				try:
					rfid_data = json.loads( post_body )
				except Exception as e:
					success = False
					wx.CallAfter( Utils.writeLog, str(post_body) )
					wx.CallAfter( Utils.logException, e, sys.exc_info() )
				
				if success:
					data = []
					for d in rfid_data['data']:
						try:
							data.append( (int(d['bib']), datetime.datetime.fromisoformat(d['t'])) )
						except Exception as e:
							wx.CallAfter( Utils.writeLog, str(d) )
							wx.CallAfter( Utils.logException, e, sys.exc_info() )
					
					def updateModel( data ):
						# Must be run on the main thread.
						race = Model.race
						if not race or not data:
							return
						data = [(num, (ts-race.startTime).total_seconds()) for num, ts in data]
						for num, t in data:
							race.addTime( num, t, False )
						race.setChanged()
						
						if race.enableUSBCamera:
							photoRequests = [(num, t) for num, t in data if okTakePhoto(num, t)]
							if photoRequests:
								success, error = SendPhotoRequests( photoRequests, includeFTP=False )
							
						Utils.refresh()
						
					wx.CallAfter( updateModel, data )

				self.send_response( HTTPStatus.OK if success else HTTPStatus.BAD_REQUEST )
				self.end_headers()
				
			else:
				assert( 'Unrecognized POST' )
		except Exception as e:
			self.send_error(501,'Error: {} {}\n{}'.format(self.path, e, traceback.format_exc()))
			return
	
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
			elif up.path=='/servertimestamp.js':
				# Return the clientTime and the serverTime so the client can computer the round-trip time.
				# Used by Christian's algorithm to estimate the round-trip time and get a better time correction between the two computers.
				try:
					clientMilliseconds = float( urllib.parse.parse_qs(up.query).get('clientTime', None)[0] )
				except Exception:
					clientMilliseconds = 0.0
				content = json.dumps( {
						'serverTime':epochMilliseconds(),
						'clientTime':clientMilliseconds,
					}
				).encode()
				content_type = self.json_content
			elif up.path=='/identity.js':
				# Return the identify of this CrossMgr instance.
				content = json.dumps( {
						'serverTime':epochTime(),
						'version':Version.AppVerName,
						'host':socket.gethostname(),
					}
				).encode()
				content_type = self.json_content
			else:
				file = None
				
				if up.path == '/CurrentResults.html':
					try:
						file = os.path.splitext(Model.race.getFileName())[0] + '.html'
					except Exception:
						pass
				
				elif up.path == '/PreviousResults.html':
					file = GetPreviousFileName()
				
				if file is None: 
					file = url2pathname(os.path.basename(up.path))
				content, gzip_content = contentBuffer.getContent( file )
				content_type = self.html_content
				assert isinstance( content, bytes )
		except Exception as e:
			self.send_error(404,'Error: {} {}\n{}'.format(self.path, e, traceback.format_exc()))
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
		except Exception:
			hostname = DEFAULT_HOST
	return 'http://{}:{}'.format(hostname, PORT_NUMBER)

server = None
def WebServer():
	global server
	while True:
		try:
			server = CrossMgrServer(('', PORT_NUMBER), CrossMgrHandler)
			server.init_thread_pool()
			server.serve_forever( poll_interval = 2 )
		except Exception:
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
	while True:
		try:
			wsServer = WebsocketServer( port=PORT_NUMBER + 1, host='' )
			wsServer.set_fn_message_received( message_received )
			wsServer.run_forever()
		except Exception:
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
			wsServer.send_message_to_all( Utils.ToJson(message).encode() )
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
		while True:
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
	except Exception:
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
	while True:
		try:
			wsLapCounterServer = WebsocketServer( port=PORT_NUMBER + 2, host='' )
			wsLapCounterServer.set_fn_new_client( lap_counter_new_client )
			wsLapCounterServer.run_forever()
		except Exception:
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
				wsLapCounterServer.send_message_to_all( Utils.ToJson(message).encode() )
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
	print( 'Started httpserver on port ' , PORT_NUMBER )
	try:
		time.sleep( 10000 )
	except KeyboardInterrupt:
		q.put( {'cmd':'exit'} )

