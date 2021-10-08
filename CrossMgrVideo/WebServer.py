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
import functools
from qrcode import QRCode
from io import StringIO

from urllib.parse import quote, urlparse, parse_qs
from cgi import parse_header, parse_multipart

from queue import Queue, Empty
from socketserver import ThreadingMixIn

from http.server import BaseHTTPRequestHandler, HTTPServer, HTTPStatus

import Utils
import CVUtil
from Database import GlobalDatabase
import Version
from GetMyIP import GetMyIP

from ThreadPoolMixIn import ThreadPoolMixIn
class CrossMgrVideoServer(ThreadPoolMixIn, HTTPServer):
	pass
    
PORT_NUMBER = 8775

now = datetime.datetime.now

with open( os.path.join(Utils.getImageFolder(), 'CrossMgrVideo.ico'), 'rb' ) as f:
	favicon = f.read()

mainPage = None
def getMainPage( dateStr=None ):
	global mainPage
	
	if True or not mainPage:
		with open( os.path.join(Utils.getHtmlFolder(), 'main.html') ) as f:
			mainPage = f.read()
	
	if dateStr:
		mainPage = mainPage.replace( 'var dateStrInitial = null;', 'var dateStrInitial = "{}";'.format(dateStr) )
	
	return mainPage.encode()	# Make sure to return bytes.

@functools.lru_cache(maxsize=16)
def getPNG( fname ):
	with open( os.path.join(Utils.getImageFolder(), fname), 'rb' ) as f:
		return f.read()

@functools.lru_cache(maxsize=16)
def getJS( fname ):
	with open( os.path.join(Utils.getHtmlFolder(), fname), 'rb' ) as f:
		return f.read()

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
	const qrcode={qrcode};
	let c = document.getElementById("idqrcode");
	let ctx = c.getContext("2d");
	ctx.fillStyle = '#000';
	const s = Math.floor( c.width / qrcode.length );
	for( let y = 0; y < qrcode.length; ++y ) {
		let row = qrcode[y];
		for( let x = 0; x < row.length; ++x ) {
			if( row.charAt(x) == '1' )
				ctx.fillRect( x*s, y*s, s, s );
		}
	}
}
'''.replace('{qrcode}', qrcode) )
	w( '</script>' )
	w( '</head>' )
	w( '<body onload="Draw();">' )
	w( '<h1 style="margin-top: 32px;">Share CrossMgrVideo Access</h1>' )
	w( '<canvas id="idqrcode" width="360" height="360"></canvas>' )
	w( '<h2>Scan the QRCode.<br/>Follow it to the CrossMgrVideo page.</h2>' )
	w( '<h2>{}</h2>'.format(urlPage) )
	w( 'Powered by <a href="http://www.sites.google.com/site/crossmgrsoftware">CrossMgr</a>.' )
	w( '</body>' )
	w( '</html>' )
	return result.getvalue().encode()
#---------------------------------------------------------------------------

class CrossMgrVideoHandler( BaseHTTPRequestHandler ):
	html_content	= 'text/html; charset=utf-8'
	js_content		= 'text/javascript';
	ico_content		= 'image/x-icon'
	json_content	= 'application/json'
	jpeg_content	= 'image/jpeg'
	png_content		= 'image/png'
	re_jpeg_request = re.compile( r'^\/img([0-9]+)c?s?g?\.jpeg$' )
	
	def parse_POST( self ):
		ctype, pdict = parse_header(self.headers['content-type'])
		if ctype == 'multipart/form-data':
			postvars = parse_multipart(self.rfile, pdict)
		elif ctype == 'application/x-www-form-urlencoded':
			length = int(self.headers['content-length'])
			postvars = parse_qs(
					self.rfile.read(length), 
					keep_blank_values=1)
		else:
			postvars = {}
		return postvars

	def do_POST(self):
		postvars = self.parse_POST()
		if 'id' in postvars:
			id = postvars.pop('id')
			GlobalDatabase().updateTriggerRecord( id, postvars )

	def do_GET(self):
		up = urlparse( self.path )
		content, gzip_content = None, None
		try:
			if up.path=='/':
				query = { k:v[0] for k,v in parse_qs( up.query ).items() }
				content = getMainPage( query.get('date') )
				content_type = self.html_content
				
			elif self.re_jpeg_request.match( up.path ):		# Images.
				imgName = up.path.split('img')[1]
				content = GlobalDatabase().getPhotoById( int(re.sub('[^0-9]', '', imgName)) )
				mods = re.match( '^[0-9]+([a-z]*)\.jpeg$', imgName ).group(1)
				if mods:
					frame = CVUtil.jpegToFrame( content )
					if 'c' in mods:
						frame = CVUtil.adjustContrastFrame( frame )
					if 's' in mods:
						frame = CVUtil.sharpenFrame( frame )
					if 'g' in mods:
						frame = CVUtil.grayscaleFrame( frame )
					content = CVUtil.frameToJPeg( frame )
				content_type = self.jpeg_content
				
			elif up.path=='/triggers.js':
				# Get all triggers for a given day.  Also support seaching for a bib.
				query = { k:v[0] for k,v in parse_qs( up.query ).items() }
				
				if 'day' in query:
					tsLower = datetime.datetime( *[int(v) for v in query['day'].split('-')] )	# Expected in YYYY-MM-DD format.
					tsUpper = tsLower + datetime.timedelta( hours=24 )
				else:
					# Default to today.
					t = datetime.datetime.now()
					tsLower = datetime.datetime( t.year, t.month, t.day, 0, 0, 0 )
					tsUpper = tsLower + datetime.timedelta( hours=24 )
				
				bib = query.get('bib', None)
				triggers = GlobalDatabase().queryTriggers( tsLower, tsUpper, bib )
				# Convert times to seconds since epoch.
				for trig in triggers:
					trig['ts'] = trig['ts'].timestamp()
					trig['ts_start'] = trig['ts_start'].timestamp()
					trig['tsJpgIds'] = [(ts.timestamp(), id) for ts,id in trig['tsJpgIds']]
				
				content = json.dumps( triggers ).encode()
				content_type = self.json_content
				
			elif up.path=='/trigger_update.js':
				# Update trigger values.
				query = { k:v[0] for k,v in parse_qs( up.query ).items() }
				if 'id' in query:
					id = query.pop('id')
					try:
						id = int(id)
					except:
						id = 0
					if 'bib' in query:
						try:
							query['bib'] = int(query['bib'])
						except:
							query['bib'] = 0
					success = GlobalDatabase().updateTriggerRecord( id, query )
				else:
					success = False
				content = json.dumps( [success] ).encode()
				content_type = self.json_content
				
			elif up.path=='/trigger.js':
				# Update trigger values.
				query = { k:v[0] for k,v in parse_qs( up.query ).items() }
				fields = {}
				if 'id' in query:
					id = query.pop('id')
					try:
						id = int(id)
					except:
						id = 0
					if id:
						fields = GlobalDatabase().getTriggerFields( id )
						fields['ts'] = fields['ts'].timestamp()
						fields['ts_start'] = fields['ts_start'].timestamp()

				content = json.dumps( fields ).encode()
				content_type = self.json_content
				
			elif up.path=='/triggerdates.js':
				# Get all dates that have triggers, and the image count.
				# Most recent first.
				triggerDates = [(d.strftime('%Y-%m-%d'),c) for d, c in reversed(GlobalDatabase().getTriggerDates())]
				
				content = json.dumps( triggerDates ).encode()
				content_type = self.json_content
				
			elif up.path=='/favicon.ico':
				content = favicon
				content_type = self.ico_content
			
			elif up.path=='/qrcode.html':
				query = { k:v[0] for k,v in parse_qs( up.query ).items() }
				if 'url' in query:
					url = query['url']
				else:
					url = '{}:{}'.format(GetMyIP(), PORT_NUMBER)
				content = getQRCodePage( url )
				content_type = self.html_content
			
			elif up.path.endswith('.png'):
				content = getPNG( up.path[1:] )
				content_type = self.png_content
				
			elif up.path=='/identity.js':
				# Return the identify of this CrossMgrVideo instance.
				content = json.dumps( {
						'serverTime':epochTime(),
						'version':Version.AppVerName,
						'host':socket.gethostname(),
					}
				).encode()
				content_type = self.json_content
				
			elif up.path.endswith('.js'):
				content = getJS( up.path[1:] )
				content_type = self.js_content
				
			else:
				raise ValueError( 'Unknown url="{}"'.format(up) )
				
		except Exception as e:
			self.send_error(404,'Error: {} {}\n{}'.format(self.path, e, traceback.format_exc()))
			return
		
		self.send_response( 200 )
		self.send_header('Content-Type', content_type)
		
		# Adjust for compression.
		if content_type == self.html_content:
			if gzip_content and 'Accept-Encoding' in self.headers and 'gzip' in self.headers['Accept-Encoding']:
				content = gzip_content
				self.send_header( 'Content-Encoding', 'gzip' )
		
		# Set no caching for html and json content.  Cache everything else.
		if content_type == self.html_content or content_type == self.json_content:
			self.send_header( 'Cache-Control', 'no-cache, no-store, must-revalidate' )
			self.send_header( 'Pragma', 'no-cache' )
			self.send_header( 'Expires', '0' )
		
		self.send_header( 'Content-Length', len(content) )
		self.end_headers()
		self.wfile.write( content )
	
	def log_message(self, format, *args):
		return

#--------------------------------------------------------------------------

server = None
def WebServer():
	global server
	while True:
		try:
			server = CrossMgrVideoServer(('', PORT_NUMBER), CrossMgrVideoHandler)
			server.init_thread_pool()
			server.serve_forever( poll_interval = 2 )
		except Exception as e:
			server = None
			time.sleep( 5 )

webThread = threading.Thread( target=WebServer, name='CrossMgrVideoWebServer' )
webThread.daemon = True
webThread.start()
			
#-------------------------------------------------------------------
if __name__ == '__main__':
	print( 'Started CrossMgrVideoWebServer on http://{}:{} '.format(GetMyIP(), PORT_NUMBER) )
	try:
		time.sleep( 10000 )
	except KeyboardInterrupt:
		pass

