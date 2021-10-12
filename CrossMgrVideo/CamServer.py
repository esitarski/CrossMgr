import numpy as np
import cv2
import sys
import time
import platform
import simplejpeg
import queue
from queue import Empty, Queue

from threading import Thread, Timer

from datetime import datetime, timedelta
from FrameCircBuf import FrameCircBuf
from FIFOCache import FIFOCacheSet
import CVUtil

now = datetime.now

CameraUsbMax = 16
	
def getCameraUsb():
	# Check for cameras on all usb ports (in parallel).
	
	def checkUsbPortForCamera( q, usb ):
		cap = cv2.VideoCapture( usb )
		q.put( (usb, cap.isOpened()) )
		cap.release()

	q = queue.Queue()	
	for usb in range(CameraUsbMax):
		Thread(group=None, target=checkUsbPortForCamera, args=(q, usb) ).start()
		
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
			if fourcc.upper() == 'MJPG':
				properties.append( ('convert_rgb', cv2.CAP_PROP_CONVERT_RGB, 0) )
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

transmitFramesMax = 6
bufferSeconds = 8

def EstimateQuerySeconds( ts, s_before, s_after, fps ):
	t = now()
	tEarliest = ts - timedelta(seconds=s_before)
	tLatest = ts + timedelta(seconds=s_after)
	if tEarliest > t:		# Request is completely after the current time.
		return (tLatest - t).total_seconds()
	
	transmitRate = float(fps * transmitFramesMax)
	sBefore = (t - tEarliest).total_seconds()
	sAfter = (tLatest - t).total_seconds()
	backlog = (sBefore + sAfter) * fps
	
	if t >= tLatest:		# Request is completely before the current time.
		return backlog/transmitRate
	
	# Some part of the request is before the current time, some is after.
	# The transmit rate may or may not be able to catch up.
	backlogRemaining = backlog - sAfter * transmitRate	
	return sAfter + max(0.0, backlogRemaining / transmitRate)

def CamServer( qIn, qWriter, camInfo=None ):
	sendUpdates = {}
	tsSeen = FIFOCacheSet( 60*60 )		# Cache of times that have already been written to the database.
	camInfo = camInfo or {}
	backlog = []
	
	def qWriterSend( msg ):
		try:
			qWriter.put( msg )
		except MemoryError as e:
			print( 'qWriterSend: ', e )
	
	qWriterSend( {'cmd':'cameraUsb', 'usb':getCameraUsb()} )
	time.sleep( 0.25 )
	
	while True:
		
		with VideoCaptureManager(**camInfo) as (cap, retvals):
			time.sleep( 0.25 )
			frameCount = fpsFrameCount = 0
			fpsStart = now()
			inCapture = False
			doSnapshot = False
			fcb = FrameCircBuf( int(camInfo.get('fps', 30) * bufferSeconds) )
			tsMax = now()
			keepCapturing = True
			secondsPerFrame = 1.0/30.0
			convert_rgb = True
			
			while keepCapturing:
				# Read the frame.
				if not cap.isOpened():		# Handle the case if the camera cannot open.
					ret, frame = True, None
					qWriterSend( {'cmd':'cameraUsb', 'usb':getCameraUsb()} )
					break
				else:						
					try:
						ret, frame = cap.read()
					except KeyboardInterrupt:
						return
				
				# Get the closest time to the read.
				ts = now()
				
				# If the cam read failed, break out and reconnect.
				if not ret:
					break
				
				# If the frame is not in jpeg format, encode it now.  This spreads out the CPU per frame rather than when
				# we send a group of photos for a capture.
				frame = CVUtil.toJpeg( frame )
				
				# print( len(frame) if isinstance(frame, bytes) else frame.shape )
				
				# Add the frame to the circular buffer.
				fcb.append( ts, frame )
				
				# Process all pending requests.
				# Do this as quickly as possible so we can keep up with the camera's frame rate.
				while True:
					#-------- start of message processing loop --------#
					try:
						m = qIn.get_nowait()
					except Empty:
						break
					
					cmd = m['cmd']
					
					if cmd == 'query':
						if m['tStart'] > ts:
							# Reschedule requests in the future to the past when the buffer has the frames.
							Timer( (m['tStart'] - ts).total_seconds(), qIn.put, (m,) ).start()
							continue
						
						backlog.extend( (t, f) for t, f in zip(*fcb.getTimeFrames(m['tStart'], m['tEnd'], tsSeen)) )
						if m['tEnd'] > tsMax:
							tsMax = m['tEnd']
					
					elif cmd == 'query_closest':
						if (ts - m['t']).total_seconds() < secondsPerFrame:
							# Reschedule requests earlier than secondsPerFrame.
							# This ensures that the buffer has a frame after the time, which might be the closest one.
							Timer( secondsPerFrame*2.0 - (ts - m['t']).total_seconds(), qIn.put, (m,) ).start()
							continue
						
						backlog.extend( (t, f) for t, f in zip(*fcb.getTimeFramesClosest(m['t'], m['closest_frames'], tsSeen)) )
						if m['t'] > tsMax:
							tsMax = m['t']
					
					elif cmd == 'start_capture':
						if 'tStart' in m:
							backlog.extend( (t, f) for t, f in zip(*fcb.getTimeFrames(m['tStart'], ts, tsSeen)) )
							inCapture = True
					
					elif cmd == 'stop_capture':
						inCapture = False
					
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
					
					elif cmd == 'terminate':
						qWriterSend( {'cmd':'terminate'} )
						return
					
					else:
						assert False, 'Unknown Command'
						
					#--------- end of message processing loop ---------#
				
				# Camera info.
				if retvals:
					qWriterSend( {'cmd':'info', 'retvals':retvals} )
					convert_rgb = True
					for name, property_index, call_status, update_value in retvals:
						if name == 'convert_rgb' and call_status and update_value == 0:
							convert_rgb = False
							break
					retvals = None
				
				# If inCapture, or the capture time is in the future, add the frame to the backlog.
				if (tsMax > ts or inCapture) and ts not in tsSeen and frame is not None :
					tsSeen.add( ts )
					backlog.append( (ts, frame) )

				# Send the frames to the database for writing.
				# Don't send too many frames at a time so we don't overwhelm the queue and lose frame rate.
				# Always ensure that the most recent frame is sent so any update requests can be satisfied with the last frame.
				if backlog:
					backlogTransmitFrames = transmitFramesMax * (5 if not convert_rgb else 1)	# If we are sending jpeg frames we can send more at a time.
					qWriterSend( { 'cmd':'response', 'ts_frames': backlog[-backlogTransmitFrames:] } )
					del backlog[-backlogTransmitFrames:]
						
				# Send status messages.
				for name, freq in sendUpdates.items():
					if frameCount % freq == 0:
						qWriterSend( {'cmd':'update', 'name':name, 'frame':frame} )				
				frameCount += 1
						
				# Send snapshot message.
				if doSnapshot:
					if frame is not None:
						qWriterSend( {'cmd':'snapshot', 'ts':ts, 'frame':frame} )
					doSnapshot = False
				
				# Send fps message.
				fpsFrameCount += 1
				if (ts - fpsStart).total_seconds() >= 3.0:
					qWriterSend( {'cmd':'fps', 'fps_actual':fpsFrameCount / (ts - fpsStart).total_seconds()} )
					fpsStart = ts
					fpsFrameCount = 0
				
def getCamServer( camInfo=None ):
	qIn = Queue()
	qWriter = Queue()
	thread = Thread( target=CamServer, args=(qIn, qWriter, camInfo), name='CamServer' )
	thread.start()
	return qIn, qWriter
	
def callCamServer( qIn, cmd, **kwargs ):
	kwargs['cmd'] = cmd
	qIn.put( kwargs )
	
if __name__ == '__main__':
	print( getCameraUsb() )
	# sys.exit()
	
	def handleMessages( q ):
		while True:
			m = q.get()
			print( ', '.join( '{}={}'.format(k, v if k not in ('frame', 'ts_frames') else len(v)) for k, v in m.items()) )
	
	qIn, qWriter = getCamServer( dict(usb=4, width=1920, height=1080, fps=30, fourcc="MJPG") )
	qIn.put( {'cmd':'start_capture'} )
	
	thread = Thread( target=handleMessages, args=(qWriter,) )
	thread.daemon = True
	thread.start()
	
	time.sleep( 10000 )
	
	time.sleep( 2.0 )
	callCamServer( qIn, 'cam_info', info=dict(usb=1, width=1920, height=1080, fps=30) )
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
	
