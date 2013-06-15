import wx
import time
import Utils
import datetime
import threading
import bisect
from Queue import Queue, Empty
from PhotoFinish import SetCameraState, SavePhoto, fileFormatTime

now = datetime.datetime.now

fileFormat = 'bib-%04d-time-%s-%d.jpg'
def GetFilename( bib, t, dirName, i ):
	return os.path.join( dirName, fileFormat % (bib if bib else 0, fileFormatTime(t), (i+1) ) )
	
class VideoBuffer( threading.Thread ):
	def __init__( self, camera, refTime = None, fps = 50, bufferSeconds = 1.5 ):
		threading.Thread.__init__( self )
		self.daemon = True
		self.camera = camera
		self.refTime = refTime if refTime is not None else now()
		self.fps = fps
		self.frameMax = int(fps * bufferSeconds)
		self.frameDelay = 1.0 / fps
		self.frameDelayMicroseconds = int(self.frameDelay * 1000000.0)
		self.reset()
	
	def reset( self ):
		self.frames = [(0.0, None)] * self.frameMax
		self.frameCur =  self.frameMax - 1;
		self.queue = Queue()
		
	def saveFrames( self, bib, t, dirName, frames ):
		for i, frame in enumerate(frames):
			SavePhoto( GetFilename(bib, t, dirName, i), bib, t, frame )
		
	def run( self ):
		self.reset()
		tLaunch = now()
		while 1:
			self.grabFrame()
			try:
				message = self.queue.get( False )
			except Empty:
				pass
			else:
				if   message[0] == 'Save':
					cmd, bib, t, dirName = message
					frames = self.find( t )
					threading.Thread( target=self.saveFrames, args=(bib, t, dirName, frames) ).start()
					
				elif message[0] == 'Terminate':
					self.reset()
					break
				
			# Sleep until we need to grab the next frame.
			microSeconds = (now() - tLaunch).microseconds
			frameWait = ((int(microSeconds / self.frameDelayMicroseconds)+1) * self.frameDelayMicroseconds) - microSeconds
			time.sleep( frameWait / 1000000.0 )
	
	def stop( self ):
		self.queue.put( ['Terminate'] )
		return self
		
	def takePicture( self, bib, t, dirName ):
		self.queue.put( ['Save', bib, t, dirName] )
	
	def append( self, t, frame ):
		self.frames[self.frameCur] = (t, frame)
		self.frameCur = (self.frameCur + 1) % self.frameMax
	
	def getT( self, i ):
		return self.frames[ (i + self.frameCur) % self.frameMax ][0]
		
	def getFrame( self, i ):
		return self.frames[ (i + self.frameCur) % self.frameMax ][1]
		
	def __len__( self ):
		return self.frameMax
	
	def find( self, t ):
		frames = self.frames
		frameCur = self.frameCur
		frameMax = self.frameMax
		
		try:
			iBest = (i for i in xrange(frameMax-1, -1, -1) if frames[ (i + frameCur) % frameMax ][0] < t).next()
		except StopIteration:
			return []
		else:
			return [self.getFrame(i) for i in xrange(max(0, iBest-1), min(frameMax, iBest + 2)) if self.getFrame(i)]
		
	def grabFrame( self ):
		try:
			self.frames[self.frameCur] = ((now() - self.refTime).total_seconds(), self.camera.getImage())
			self.frameCur = (self.frameCur + 1) % self.frameMax
		except:
			pass
		
if __name__ == '__main__':
	import os
	import random
	import shutil
	
	app = wx.PySimpleApp()
	app.SetAppName("CrossMgr")
	Utils.disable_stdout_buffering()
	
	dirName = 'VideoBufferTest_Photos'
	if os.path.isdir(dirName):
		shutil.rmtree( dirName, True )
	os.mkdir( dirName )
	
	tRef = now()
	vb = VideoBuffer( SetCameraState(True), tRef )
	vb.start()
	for i in xrange(60):
		time.sleep( random.random() )
		vb.takePicture( 0, (now() - tRef).total_seconds(), dirName )
	vb.stop().join()
