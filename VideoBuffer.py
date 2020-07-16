import wx
import os
import sys
import time
import Utils
import Model
import PhotoFinish
from FrameCircBuf import FrameCircBuf
from datetime import datetime, timedelta
import threading
from Utils import logCall, logException
from queue import Queue, Empty
import wx.lib.newevent

now = datetime.now

PhotoEvent, EVT_PHOTO = wx.lib.newevent.NewEvent()

fileFormat = 'bib-%04d-time-%s-%d.jpg'
def GetFilename( bib, t, dirName, i ):
	return os.path.join( dirName, fileFormat % (bib if bib else 0, PhotoFinish.fileFormatTime(t), (i+1) ) )

class FrameSaver( threading.Thread ):
	def __init__( self ):
		threading.Thread.__init__( self )
		self.daemon = True
		self.name = 'FrameSaver'
		self.reset()
	
	def reset( self ):
		self.queue = Queue()
	
	def run( self ):
		self.reset()
		while 1:
			message = self.queue.get()
			if   message[0] == 'Save':
				cmd, fileName, bib, t, frame = message
				#sys.stderr.write( 'save' )
				PhotoFinish.SavePhoto( fileName, bib, t, frame )
				self.queue.task_done()
			elif message[0] == 'Terminate':
				self.queue.task_done()
				self.reset()
				break
	
	def stop( self ):
		self.queue.put( ['Terminate'] )
		self.join()
	
	def save( self, fileName, bib, t, frame ):
		self.queue.put( ['Save', fileName, bib, t, frame] )
	
class CallbackTimer( wx.Timer ):
	def __init__( self, callback ):
		super().__init__()
		self.callback = callback
		
	def Notify( self ):
		self.callback()

class VideoBuffer( object ):
	
	def __init__( self, camera, refTime=None, dirName='.', fps=25, bufferSeconds=4.0, owner=None, burstMode=True ):
		self.camera = camera
		self.refTime = refTime if refTime is not None else now()
		self.dirName = dirName
		self.fps = fps
		self.frameMax = int(fps * bufferSeconds)
		
		self.frameDelay = 1.0 / fps
		self.frameDelayTimeDelta = timedelta(seconds=self.frameDelay)
		
		self.frameSaver = None
		self.fcb = FrameCircBuf()
		self.owner = owner			# Destination to send photos after they are taken.
		self.burstMode = burstMode
		
		self.timer = CallbackTimer( self.recordVideoFrame )
		self.reset()
	
	def setOwner( self, owner=None ):
		self.owner = owner
	
	def reset( self ):
		if self.frameSaver and self.frameSaver.is_alive():
			self.frameSaver.stop()
		
		if self.timer.IsRunning():
			self.timer.Stop()
		
		self.fcb.reset( self.frameMax )
		self.frameCount = 0
		
		self.frameSaver = FrameSaver()
		self.frameSaver.start()
		
		self.tFindLast = now() - timedelta( days=1 )
		
		self.lastSampleTime = now()
		self.sampleCount = 0
	
	def recordVideoFrame( self ):
		tNow = now()
		self.sampleCount += 1
		if not self.camera:
			return
			
		try:
			image = self.camera.getImage()
			self.fcb.append( tNow, image )
			if self.owner is not None:
				wx.PostEvent( self.owner, PhotoEvent(t=tNow, photo=image) )
		except Exception as e:
			logException( e, sys.exc_info() )

	def getFrameRate( self ):
		tNow = now()
		rate = self.sampleCount / (tNow -self.lastSampleTime).total_seconds()
		self.lastSampleTime = tNow
		self.sampleCount = 0
		return rate
	
	def start( self ):
		self.reset()
		milliseconds = int(self.frameDelay * 1000.0)
		self.timer.Start( milliseconds, oneShot=False )
	
	def stop( self ):
		if self.timer.IsRunning():
			self.timer.Stop()
		if self.frameSaver and self.frameSaver.is_alive():
			self.frameSaver.stop()
		self.frameSaver = None
		self.lastSampleTime = now()
			
	def takePhoto( self, bib, t ):
		tNow = now()

		tFind = self.refTime + timedelta( seconds = t + Model.race.advancePhotoMilliseconds / 1000.0 )
		if tFind > tNow:
			wx.CallLater( max(1,int(((tFind - tNow).total_seconds() + 0.1) * 1000.0)), self.takePhoto, bib, t )
			return
		
		# If burst mode, check if there was another rider before within frameDelay seconds.
		# If so, also save the frame just before the given time.
		# Always save the closest frame after the given time.
		times, frames = self.fcb.findBeforeAfter(
							tFind,
							1, # 1 if tFind - self.tFindLast < self.frameDelayTimeDelta and self.burstMode else 0,
							1 )
		for i, frame in enumerate( frames ):
			t = (times[i]-self.refTime).total_seconds()
			self.frameSaver.save( GetFilename(bib, t, self.dirName, i), bib, t, frame )
		self.frameCount += len(frames)
		self.tFindLast = tFind
	
	def getT( self, i ):
		return self.fcb.getT(i)
		
	def getFrame( self, i ):
		return self.fcb.getFrame(i)
	
	def getTimeFrame( self, i ):
		return (self.fcb.getT(i), self.fcb.getFrame(i))
		
	def findBeforeAfter( self, t, before=0, after=1 ):
		''' Call the frame cyclic buffer from race time, not clock time. '''
		tFind = self.refTime + timedelta( seconds=t )
		times, frames = self.fcb.findBeforeAfter( tFind, before, after )
		return zip( times, frames )
		
	def __len__( self ):
		return self.frameMax
	
videoBuffer = None
def StartVideoBuffer( refTime, raceFileName ):
	global videoBuffer
	
	if not videoBuffer:
		camera = PhotoFinish.SetCameraState( True )
		if not camera:
			return False
			
		dirName = PhotoFinish.getPhotoDirName( raceFileName )
		if not os.path.isdir( dirName ):
			try:
				os.makedirs( dirName )
			except Exception as e:
				logException( e, sys.exc_info() )
				return False
				
		videoBuffer = VideoBuffer( camera, refTime, dirName )
		videoBuffer.start()
	return True

def TakePhoto( raceFileName, bib, raceSeconds ):
	global videoBuffer
	
	race = Model.race
	if not race or not race.isRunning():
		return 0
	
	if not videoBuffer:
		if not StartVideoBuffer(race.startTime, raceFileName):
			return 0
	
	videoBuffer.refTime = race.startTime
	videoBuffer.takePhoto( bib, raceSeconds )
	return videoBuffer.frameCount - race.photoCount + 1
	
def Shutdown():
	global videoBuffer
	if videoBuffer:
		videoBuffer.stop()
		videoBuffer = None
	PhotoFinish.SetCameraState( False )
	
def GetFrameRate():
	global videoBuffer
	return videoBuffer.getFrameRate() if videoBuffer else 0.0

def _getTestPhotoFileName():
	return os.path.join(os.path.dirname(Utils.getHomeDir()), 'Test.cmn')
	
def ModelTakePhoto( bib, raceSeconds ):
	race = Model.race
	if race:
		if PhotoFinish.okTakePhoto(bib, raceSeconds):
			if race.enableVideoBuffer:
				return TakePhoto( Utils.mainWin.fileName if Utils.mainWin else _getTestPhotoFileName(), bib, raceSeconds )
			elif race.enableUSBCamera:
				return PhotoFinish.TakePhoto( Utils.mainWin.fileName if Utils.mainWin else _getTestPhotoFileName(), bib, raceSeconds )
		else:
			return 0
	else:
		return PhotoFinish.TakePhoto( _getTestPhotoFileName(), bib, raceSeconds )
	Utils.cameraError = _('ModelTakePhoto: usb camera is not enabled')
	return 0

@logCall
def ModelStartCamera( refTime=None, raceFileName=None ):
	Shutdown()
	
	race = Model.race
	if race and race.enableUSBCamera:
		if refTime is None:
			refTime = race.startTime
		if raceFileName is None:
			raceFileName = Utils.getFileName()
		
		assert refTime is not None and raceFileName is not None
	
		if race.enableJChipIntegration:
			StartVideoBuffer( refTime, raceFileName )
		else:
			PhotoFinish.SetCameraState( True )
		return True
	
	return False
	
if __name__ == '__main__':
	import random
	import shutil
	
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	Utils.disable_stdout_buffering()
	
	mainWin = wx.Frame(None, title="CrossMan", size=(200,200))
	mainWin.Show()
	
	print( 'initializing photo folder' )
	dirName = 'VideoBufferTest_Photos'
	if os.path.isdir(dirName):
		try:
			shutil.rmtree( dirName, True )
		except Exception as e:
			print( e )
	try:
		os.mkdir( dirName )
	except Exception as e:
		print( e )
	
	print( 'starting camera' )
	tRef = now()
	camera = PhotoFinish.SetCameraState( True )
	
	print( 'create video buffer' )
	vb = VideoBuffer( camera, tRef, dirName )
	
	print( 'start video buffer' )
	vb.start()
	
	print( 'taking photos at random intervals' )
	timer = None
	def TestPhoto():
		print( 'Snap! {:.3f} fps'.format(vb.getFrameRate()) )
		vb.takePhoto( 101, (now() - tRef).total_seconds() )
		timer.Start( random.random() * 2000, oneShot = True )
	
	timer = CallbackTimer( TestPhoto )
	def StartTest():
		timer.Start( random.random() * 2000, oneShot = True )
		
	wx.CallAfter( StartTest )
	
	app.MainLoop()
