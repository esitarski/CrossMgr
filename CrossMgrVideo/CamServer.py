import cv2
import time
import queue
from queue import Empty, Queue

from threading import Thread, Timer

from datetime import datetime, timedelta
from FrameCircBuf import FrameCircBuf
from FIFOCache import FIFOCacheSet
import CVUtil

now = datetime.now

CameraUsbMax = 16
	
def getCameraUsb( usbSuccess=None ):
	# Check for cameras on all usb ports (in parallel).
	
	def checkUsbPortForCamera( q, usb ):
		if usb == usbSuccess:
			q.put( (usb, True) )
		else:
			cap = cv2.VideoCapture( usb )
			q.put( (usb, cap.isOpened()) )
			cap.release()

	q = queue.Queue()	
	for usb in range(CameraUsbMax):
		Thread(target=checkUsbPortForCamera, args=(q, usb), daemon=True ).start()
		
	cameraUsb = []
	for i in range(CameraUsbMax):
		usb, hasCamera = q.get()
		if hasCamera:
			cameraUsb.append( usb )
	
	cameraUsb.sort()
	return cameraUsb

def getVideoCapture( usb=0, fps=30, width=640, height=480, fourcc='' ):
	cap = cv2.VideoCapture( usb )
	
	retvals = []
	if cap.isOpened():
		properties = []
		if fourcc and len(fourcc) == 4:
			properties.append( ('fourcc', cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*fourcc) ) )
		properties.append( ('frame_width', cv2.CAP_PROP_FRAME_WIDTH, width) )
		properties.append( ('frame_height', cv2.CAP_PROP_FRAME_HEIGHT, height) )
		properties.append( ('fps', cv2.CAP_PROP_FPS, fps) )
		
		# Set all the camera attributes.
		for pname, pindex, pvalue in properties:
			retvals.append( (pname, pindex, cap.set(pindex, pvalue)) )
			
		# Then, get all the attribute values from the capture object.
		for i, (pname, pindex, pvalue) in enumerate(properties):
			retvals[i] += tuple( [cap.get(pindex)] )
	
	# print( cap.get(cv2.CAP_PROP_FOURCC), cv2.VideoWriter_fourcc(*'MJPG') )
	return cap, retvals

class VideoCaptureManager:
	def __init__( self, **kwargs ):
		self.cap, self.retvals = getVideoCapture(**kwargs)
	
	def __enter__(self):
		return self.cap, self.retvals
	
	def __exit__(self, type, value, traceback):
		self.cap.release()

bufferSeconds = 8

class TimeInterval:
	def __init__( self, start, end ):
		self.start, self.end = start, end
		
	def contains( self, t ):
		return self.start <= t <= self.end
		
	def overlaps( self, ti ):
		return not (ti.end < self.start or self.end < ti.start)
		
	def merge( self, ti ):
		self.start, self.end = min(self.start, ti.start), max(self.end, ti.end)

def CamServer( qIn, qOut, camInfo=None ):
	'''
		Message processing for the camera.
		This includes writing photos from the frame buffer as well as returning information about the camera itself.
		All output is asyncronously written to qOut.
	'''
	sendUpdates = {}
	tsSeen = FIFOCacheSet( 60*60 )		# Cache of times that have already been written to the database.
	camInfo = camInfo or {}
	backlog = []
	
	#print( 'CamServer: camInfo={}'.format(camInfo) )
	
	def backgroundGetCameraUsb( usbSuccess, camInfo ):
		def get( usbSuccess, camInfo ):
			qOut.put( {'cmd':'cameraUsb', 'usb_available':getCameraUsb(usbSuccess), 'usb_cur':camInfo.get('usb',0)} )
		Thread( target=get, args=(usbSuccess, camInfo), daemon=True ).start()
	
	while True: 
		with VideoCaptureManager(**camInfo) as (cap, retvals):
			frameCount = 0
			fpsFrameCount = 0
			fpsStart = now() - timedelta( seconds=10 )		# Force an initial fps update.
			
			doSnapshot = False
			endOfTime = now() + timedelta( days=400*100 )
			keepCapturing = True
			secondsPerFrame = 1.0/30.0
			
			tiCapture = TimeInterval( fpsStart, fpsStart )	# Interval for interactive capture.
			intervals = []									# Current intervals we are capturing for.
			captureLatency = timedelta( seconds=0.0 )		# Delay it takes for frame to get from the camera to the computer.
			
			fcb = FrameCircBuf( int(camInfo.get('fps', 30) * bufferSeconds) )
			
			# Get the available usb ports.  If the current port succeeded, don't waste time checking it again.
			backgroundGetCameraUsb( camInfo['usb'] if cap.isOpened() else None, camInfo )
			
			while keepCapturing:
				# Read the frame.  If anything fails, keep going in the loop so we can reset with another camInfo.
				if not cap.isOpened():
					ret, frame = False, None
					time.sleep( 0.5 )		# Keep going so we can get a camInfo to try again.
				else:						
					try:
						ret, frame = cap.read()
					except Exception as e:	# Potential out of memory error?
						ret, frame = False, None
					except KeyboardInterrupt:
						return
				
				# Get the closest time to the read.
				ts = now()
				
				# If the frame is not in jpeg format, encode it now.  This spreads out the CPU per frame rather than when
				# we send a group of photos for a capture.
				opencv_frame = frame
				frame = CVUtil.toJpeg( frame )
				
				# Add the frame to the circular buffer.  Adjust for the capture latency.
				tsFrame = ts - captureLatency
				fcb.append( tsFrame, frame )
				
				# Process all pending requests.
				# Do this as quickly as possible so we can keep up with the camera's frame rate.
				while True:
					#-------- start of message processing loop --------#
					try:
						# No need to timeout here.  Breaking to the frame capture prevents a busy loop.
						m = qIn.get_nowait()
					except Empty:
						break
					
					cmd = m['cmd']
					
					if cmd == 'query':
						#-----------------------------------------------
						# Query frames in an interval.
						#
						tiCur = TimeInterval( m['tStart'], m['tEnd'] )
						
						# Process all frames before the current time.
						backlog.extend( (t, f) for t, f in zip(*fcb.getTimeFrames(tiCur.start, tiCur.end, tsSeen)) )
						
						# Add this query interval to the list, or expand the existing interval if it overlaps.
						for ti in intervals:
							if ti.overlaps( tiCur ):
								ti.merge( tiCur )
								break
						else:
							intervals.append( tiCur )
					
					elif cmd == 'query_closest':
						#-----------------------------------------------
						# Query the closest frames to a given time.
						#
						if (ts - m['t']).total_seconds() < secondsPerFrame + captureLatency.total_seconds():
							# Reschedule requests earlier than secondsPerFrame.
							# This ensures that the buffer has a frame after the time, which might be the closest one.
							Timer( captureLatency.total_seconds() + secondsPerFrame*2.0 - (ts - m['t']).total_seconds(), qIn.put, (m,) ).start()
							continue
						
						backlog.extend( (t, f) for t, f in zip(*fcb.getTimeFramesClosest(m['t'], m['closest_frames'], tsSeen)) )
										
					elif cmd == 'start_capture':
						#-----------------------------------------------
						# Start capturing frames.  Send frames from the buffer
						# if tStart is in the past.
						#
						if 'tStart' in m:
							tiCapture.start, tiCapture.end = m['tStart'], endOfTime
							backlog.extend( (t, f) for t, f in zip(*fcb.getTimeFrames(tiCapture.start, tiCapture.end, tsSeen)) )
					
					elif cmd == 'stop_capture':
						#-----------------------------------------------
						# Stop capturing frames.
						#
						tiCapture.end = ts
					
					elif cmd == 'snapshot':
						doSnapshot = True
					
					elif cmd == 'send_update':
						sendUpdates[m['name']] = m['freq']
					
					elif cmd == 'cancel_update':
						if 'name' not in m:
							sendUpdates.clear()
						else:
							sendUpdates.pop(m['name'], None)
					
					elif cmd == 'cam_info':
						camInfo = m['info'] or {}
						keepCapturing = False
						break
					
					elif cmd == 'get_usb':
						keepCapturing = False	# Forces a camera reconnect to the same camInfo.  This, sends updated usb information.
						break
					
					elif cmd == 'terminate':
						#-----------------------------------------------
						# Quit processing frames.
						#
						qOut.put( {'cmd':'terminate'} )
						return
					
					else:
						assert False, 'Unknown Command'
						
					#--------- end of message processing loop ---------#
				
				# Send camera info.
				if retvals:
					qOut.put( {'cmd':'info', 'retvals':retvals} )
					retvals = None
				
				# Check if we need to keep the current photo.
				if frame is not None and tsFrame not in tsSeen and (tiCapture.contains(tsFrame) or any(i.contains(tsFrame) for i in intervals)):
					tsSeen.add( tsFrame )
					backlog.append( (tsFrame, frame) )

				# Send the frames to the database for writing.
				if backlog:
					qOut.put( { 'cmd':'response', 'ts_frames':backlog.copy() } )
					backlog.clear()
						
				# Send status images.
				for name, freq in sendUpdates.items():
					if frameCount % freq == 0:
						qOut.put( {'cmd':'update', 'name':name, 'frame':opencv_frame} )	# Pass the raw frame so we don't have to convert it.
				frameCount += 1
						
				# Send snapshot message.
				if doSnapshot:
					if frame is not None:
						qOut.put( {'cmd':'snapshot', 'ts':ts, 'frame':frame} )
					doSnapshot = False
				
				# Send fps message.
				fpsFrameCount += bool( frame is not None )
				if (ts - fpsStart).total_seconds() >= 3.0:
					qOut.put( {'cmd':'fps', 'fps_actual':fpsFrameCount / (ts - fpsStart).total_seconds()} )
					fpsStart = ts
					fpsFrameCount = 0
					
					# Remove stale intervals from list.
					if intervals:
						tsCutoff = now() - timedelta( seconds=6 )
						intervals = [ti for ti in intervals if ti.end > tsCutoff]
				
def getCamServer( camInfo=None ):
	qIn = Queue()
	qOut = Queue()
	Thread( target=CamServer, args=(qIn, qOut, camInfo), name='CamServer', daemon=True ).start()
	return qIn, qOut
	
def callCamServer( qIn, cmd, **kwargs ):
	kwargs['cmd'] = cmd
	qIn.put( kwargs )
	
if __name__ == '__main__':
	ti1 = TimeInterval( 0, 10 )
	ti2 = TimeInterval( 5, 15 )
	ti3 = TimeInterval( 11, 21 )
	assert ti1.overlaps( ti2 )
	assert not ti1.overlaps( ti3 )
	assert ti1.contains( 5 )
	assert not ti1.contains( 15 )
	
	print( getCameraUsb() )
	# sys.exit()
	
	def handleMessages( q ):
		while True:
			m = q.get()
			print( ', '.join( '{}={}'.format(k, v if k not in ('frame', 'ts_frames') else len(v)) for k, v in m.items()) )
	
	qIn, qWriter = getCamServer( dict(usb=6, width=10000, height=10000, fps=30, fourcc="MJPG") )
	qIn.put( {'cmd':'start_capture'} )
	
	thread = Thread( target=handleMessages, args=(qWriter,), daemon=True )
	thread.start()
	
	time.sleep( 10000 )
	
	time.sleep( 2.0 )
	callCamServer( qIn, 'cam_info', info=dict(usb=4, width=1920, height=1080, fps=30) )
	time.sleep( 5.0 )
	#callCamServer( qIn, 'send_update', name='a', freq=4 )
	#callCamServer( qIn, 'send_update', name='b', freq=1 )
	time.sleep( 3 )
	#callCamServer( qIn, 'cancel_update', name='a' )
	#callCamServer( qIn, 'cancel_update', name='b' )
	callCamServer( qIn, 'query', tStart=now()-timedelta(seconds=1), tEnd=now() )
	time.sleep( 2 )
	callCamServer( qIn, 'query', tStart=now()-timedelta(seconds=1), tEnd=now() )
	time.sleep( 2 )
	callCamServer( qIn, 'query', tStart=now()-timedelta(seconds=1), tEnd=now() )
	time.sleep( 2 )
	callCamServer( qIn, 'query_closest', tStart=now()-timedelta(seconds=1), tEnd=now() )
	time.sleep( 2 )
	callCamServer( qIn, 'terminate' )
	
