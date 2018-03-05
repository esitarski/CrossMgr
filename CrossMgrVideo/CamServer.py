import numpy as np
import cv2
from datetime import datetime, timedelta
import time
from Queue import Empty
from multiprocessing import Process, Pipe, Queue
from threading import Thread, Timer
from FrameCircBuf import FrameCircBuf

now = datetime.now

def getVideoCapture( usb=1, fps=30, width=640, height=480 ):
	cap = cv2.VideoCapture( usb )
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	cap.set(cv2.CAP_PROP_FPS, fps)
	return cap

class VideoCaptureManager( object ):
	def __init__( self, **kwargs ):
		self.cap = getVideoCapture(**kwargs)
	def __enter__(self):
		return self.cap
	def __exit__(self, type, value, traceback):
		self.cap.release()

transmitFramesMax = 2
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

def CamServer( qIn, pWriter, camInfo=None ):
	sendUpdates = {}
	tsSeen = set()
	camInfo = camInfo or {}
	backlog = []
	
	def pWriterSend( msg ):
		try:
			pWriter.send( msg )
		except MemoryError as e:
			print 'pWriterSend: ', e
	
	while 1:
		with VideoCaptureManager(**camInfo) as cap:
			time.sleep( 0.25 )
			frameCount = 0
			inCapture = False
			doSnapshot = False
			tsSeen.clear()
			fcb = FrameCircBuf( int(camInfo.get('fps', 30) * bufferSeconds) )
			tsQuery = tsMax = now()
			keepCapturing = 1
			
			while keepCapturing:
				# Capture frame-by-frame
				try:
					ret, frame = cap.read()
				except KeyboardInterrupt:
					return
				
				ts = now()
				if not ret:
					break
				fcb.append( ts, frame )
				
				try:
					m = qIn.get_nowait()
					while 1:
						cmd = m['cmd']
						if cmd == 'query':
							if m['tStart'] > ts:
								# Reschedule future requests for later.
								Timer( (m['tStart'] - ts).total_seconds(), qIn.put, m ).start()
								continue
							
							if (ts - tsQuery).total_seconds() > bufferSeconds or len(tsSeen) > 5000:
								tsSeen.clear()
							tsQuery = ts

							times, frames = fcb.getTimeFrames( m['tStart'], m['tEnd'], tsSeen )
							backlog.extend( (t, f) for t, f in zip(times, frames) )
							
							if m['tEnd'] > tsMax:
								tsMax = m['tEnd']
						elif cmd == 'start_capture':
							if 'tStart' in m:
								times, frames = fcb.getTimeFrames( m['tStart'], ts, tsSeen )
								backlog.extend( (t, f) for t, f in zip(times, frames) )
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
							keepCapturing = 0
							break
						elif cmd == 'terminate':
							pWriterSend( {'cmd':'terminate'} )
							return
						else:
							assert False, 'Unknown Command'
						m = qIn.get_nowait()						
				except Empty:
					pass
				
				if tsMax > ts or inCapture:
					backlog.append( (ts, frame) )
					tsSeen.add( ts )

				# Don't send too many frames at a time.  We don't want to overwhelm the pipe and lose frames.
				# Always ensure that the most recent frame is sent so any update requests can be satisfied with the last frame.
				if backlog:
					pWriterSend( { 'cmd':'response', 'ts_frames': backlog[-transmitFramesMax:] } )
						
				# Send update messages.  If there was a backlog, don't send the frame as we can use the last frame sent.
				updateFrame = None if backlog and backlog[-1][0] == ts else frame
				for name, f in sendUpdates.iteritems():
					#if frameCount % (f if backlog else 8) == 0:
					if frameCount % f == 0:
						pWriterSend( {'cmd':'update', 'name':name, 'frame':updateFrame} )
						updateFrame = None
				if doSnapshot:
					pWriterSend( {'cmd':'snapshot', 'ts':ts, 'frame':updateFrame} )
					doSnapshot = False
						
				del backlog[-transmitFramesMax:]
				frameCount += 1
				
def getCamServer( camInfo=None ):
	qIn = Queue()
	pReader, pWriter = Pipe( False )
	p = Process( target=CamServer, args=(qIn, pWriter, camInfo), name='CamServer' )
	p.daemon = True
	p.start()
	return qIn, pReader
	
def callCamServer( qIn, cmd, **kwargs ):
	kwargs['cmd'] = cmd
	qIn.put( kwargs )
	
if __name__ == '__main__':
	def handleMessages( q ):
		while 1:
			m = q.get()
			print ', '.join( '{}={}'.format(k, v if k not in ('frame', 'ts_frames') else len(v)) for k, v in m.iteritems())
	
	qIn, pWriter = getCamServer( dict(usb=1, width=1920, height=1080, fps=30) )
	thread = Thread( target=handleMessages, args=(pWriter,) )
	thread.daemon = True
	thread.start()
	
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
	callCamServer( qIn, 'query', tStart=now()-timedelta(seconds=1), tEnd=now() )
	time.sleep( 2 )
	callCamServer( qIn, 'terminate' )
	
