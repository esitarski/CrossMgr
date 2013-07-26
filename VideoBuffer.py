import wx
import os
import time
import Utils
import Model
import PhotoFinish
import datetime
import threading
from Utils import logException
import traceback
from Queue import Queue, Empty

now = datetime.datetime.now

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
	
class VideoBuffer( threading.Thread ):
	def __init__( self, camera, refTime = None, dirName = '.', fps = 25, bufferSeconds = 3.0 ):
		threading.Thread.__init__( self )
		self.daemon = True
		self.name = 'VideoBuffer'
		self.camera = camera
		self.refTime = refTime if refTime is not None else now()
		self.dirName = dirName
		self.fps = fps
		self.frameMax = int(fps * bufferSeconds)
		self.frameDelay = 1.0 / fps
		self.frameSaver = FrameSaver()
		self.reset()
	
	def reset( self ):
		if self.frameSaver.is_alive():
			self.frameSaver.stop()
			self.frameSaver = FrameSaver()
			self.frameSaver.daemon = True
		self.frames = [(0.0, None)] * self.frameMax
		self.frameCur =  self.frameMax - 1;
		self.frameSaver.start()
		self.frameCount = 0
		self.queue = Queue()
		
	def run( self ):
		self.reset()
		tLaunch = now()
		keepGoing = True
		while keepGoing:
			try:
				tGrab = now()
				tRace = (tGrab - self.refTime).total_seconds()
				self.frames[self.frameCur] = (tRace, self.camera.getImage())
				self.frameCur = (self.frameCur + 1) % self.frameMax
			except Exception as e:
				logException( e, sys.exc_info() )
				break
			
			while 1:
				try:
					message = self.queue.get( False )
				except Empty:
					break
				
				if   message[0] == 'Save':
					cmd, bib, t = message
					tFind = t + getattr(Model.race, 'advancePhotoMilliseconds', Model.Race.advancePhotoMillisecondsDefault) / 1000.0
					if tFind > tRace:
						threading.Timer( tFind - tRace, self.takePhoto, args=[bib, t] ).start()
						continue
						
					frames = self.find( tFind )
					for i, frame in enumerate( frames ):
						self.frameSaver.save( GetFilename(bib, t, self.dirName, i), bib, t, frame )
					self.frameCount += len(frames)
					self.queue.task_done()
					
				elif message[0] == 'Terminate':
					self.queue.task_done()
					self.reset()
					keepGoing = False
					break
				
			# Sleep until we need to grab the next frame.
			frameWait = self.frameDelay - (now() - tGrab).total_seconds()
			if frameWait < 0.0:
				frameWait = self.frameDelay		# Give some more time if we are falling behind.
			time.sleep( frameWait )	
			
	def stop( self ):
		self.queue.put( ['Terminate'] )
		self.join()
		if self.frameSaver.is_alive():
			self.frameSaver.stop()
		
	def takePhoto( self, bib, t ):
		self.queue.put( ['Save', bib, t] )
	
	def getT( self, i ):
		return self.frames[ (i + self.frameCur) % self.frameMax ][0]
		
	def getFrame( self, i ):
		return self.frames[ (i + self.frameCur) % self.frameMax ][1]
	
	def getTimeFrame( self, i ):
		return self.frames[ (i + self.frameCur) % self.frameMax ]
		
	def __len__( self ):
		return self.frameMax
	
	def find( self, t ):
		frames = self.frames
		frameCur = self.frameCur
		frameMax = self.frameMax
		for iBest in xrange(frameMax-1, -1, -1):
			if frames[ (iBest + frameCur) % frameMax ][0] < t:
				fRange = list( xrange(max(0, iBest-1), min(frameMax, iBest + 2)) )
				timeError = [abs(t - self.getT(i)) for i in fRange]
				iClosest = fRange[timeError.index( min(timeError) )]
				#Utils.writeLog( 'VideoBuffer.find: %s:  delta: %s  [%s]' % (
				#	Utils.formatTime(t, True), Utils.formatTime(min(timeError), True),
				#	', '.join( Utils.formatTime(self.getT(i), True) if i != iClosest
				#				else ('*' + Utils.formatTime(self.getT(i), True)) for i in fRange ) ) )
				return [self.getFrame(i) for i in fRange if self.getFrame(i)]
		return []
		
	def findBeforeAfter( self, t, before, after ):
		frames = self.frames
		frameCur = self.frameCur
		frameMax = self.frameMax
		for iBest in xrange(frameMax-1, -1, -1):
			if frames[ (iBest + frameCur) % frameMax ][0] < t:
				fRange = list( xrange(max(0, iBest-before), min(frameMax, iBest + after)) )
				return [self.getTimeFrame(i) for i in fRange if self.getFrame(i)]
		return []

videoBuffer = None
def StartVideoBuffer( refTime, raceFileName):
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
		if not StartVideoBuffer(Model.race.startTime, raceFileName):
			return 0
		
	videoBuffer.takePhoto( bib, raceSeconds )
	return videoBuffer.frameCount - getattr(race,'photoCount',0) + 3
	
def Shutdown():
	global videoBuffer
	if videoBuffer:
		videoBuffer.stop()
		videoBuffer = None
	PhotoFinish.SetCameraState( False )
		
def ModelTakePhoto( bib, raceSeconds ):
	race = Model.race
	if race:
		if race.enableVideoBuffer:
			return TakePhoto( Utils.mainWin.fileName, bib, raceSeconds )
		elif getattr(race, 'enableUSBCamera', False):
			return PhotoFinish.TakePhoto( Utils.mainWin.fileName, bib, raceSeconds )
	return 0

def ModelStartCamera( refTime = None, raceFileName = None ):
	race = Model.race
	
	if refTime is None:
		refTime = race.startTime
	if raceFileName is None:
		raceFileName = Utils.getFileName()
	
	assert refTime is not None and raceFileName is not None
	
	if race and getattr(race, 'enableUSBCamera', False):
		''' VideoBuffer: FIXLATER '''
		if False and getattr(race, 'enableJChipIntegration', False):
			StartVideoBuffer( refTime, raceFilename )
		else:
			PhotoFinish.SetCameraState( True )
		return True
	return False
	
if __name__ == '__main__':
	import os
	import random
	import shutil
	
	'''
	import dis
	dis.dis( VideoBuffer.run )
	print '------------'
	dis.dis( VideoBuffer.grabFrame )
	print '------------'
	dis.dis( VideoBuffer.find )
	sys.exit()
	'''
	
	app = wx.PySimpleApp()
	app.SetAppName("CrossMgr")
	Utils.disable_stdout_buffering()
	
	dirName = 'VideoBufferTest_Photos'
	if os.path.isdir(dirName):
		shutil.rmtree( dirName, True )
	os.mkdir( dirName )
	
	tRef = now()
	camera = PhotoFinish.SetCameraState( True )
	vb = VideoBuffer( camera, tRef, dirName )
	vb.daemon = True
	vb.start()
	for i in xrange(60):
		time.sleep( random.random() )
		vb.takePhoto( i, (now() - tRef).total_seconds() )
	vb.stop()
	vb = None
