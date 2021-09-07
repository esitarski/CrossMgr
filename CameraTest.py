import wx
import time
import datetime
import threading
from queue import Queue, Empty
import Utils
import Model
from PhotoFinish import SnapPhoto

now = datetime.datetime.now

def RescaleImage( image, width, height ):
	wImage = image.GetWidth()
	hImage = image.GetHeight()
	ratio = min( float(width) / float(wImage), float(height) / float(hImage) )
	return image.Rescale( int(wImage*ratio), int(hImage*ratio), wx.IMAGE_QUALITY_NORMAL ) if not (0.94 < ratio < 1.06) else image
	
class ScaledImage( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(640,400) ):
		super().__init__( parent, id, size=size )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.image = None
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		
	def OnPaint( self, event=None ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
		
		width, height = self.GetSize()
		try:
			image = self.image.Copy()
			image = RescaleImage( image, width, height )
		except Exception:
			return
		
		bitmap = image.ConvertToBitmap()
		dc.DrawBitmap( bitmap, (width - bitmap.GetWidth())//2, (height - bitmap.GetHeight())//2 )
	
	def SetImage( self, image ):
		self.image = image
		self.Refresh()
		
	def GetImage( self ):
		return self.image

class CameraTestDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, title=_("Camera Test"), size=(690, 590) ):
		super().__init__(
			parent, id, title=title, size=size,
			style=wx.CAPTION
		)
		
		self.photo = ScaledImage( self )
		self.status = wx.StaticText( self )
		
		self.saveButton = wx.Button( self, label=_('Take Snapshot') )
		self.saveButton.Bind( wx.EVT_BUTTON, self.onSave )
		self.ok = wx.Button( self, wx.ID_OK )
		self.ok.Bind( wx.EVT_BUTTON, self.onClose )
		self.Bind( wx.EVT_CLOSE, self.onClose )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( self.photo, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.status, 1, flag=wx.EXPAND|wx.ALIGN_CENTRE_VERTICAL|wx.RIGHT, border=4 )
		hs.Add( self.saveButton, 0, flag=wx.ALL, border=4 )
		hs.Add( self.ok, 0, flag=wx.ALL, border=4 )
		sizer.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizer( sizer )
		
		self.resolutionFormat = _("Camera Resolution") + ': {} x {}  fps: {:.3f}'
		
		self.tStart = now()
		self.framesPerSecond = 25
		self.frameDelay = 1.0/self.framesPerSecond
		self.timer = wx.Timer( self )
		self.frameCount = 0
		self.tStart = now()
		self.fps = 0.0
		self.Bind( wx.EVT_TIMER, self.updatePhoto )
		
		SetCameraState( True )
		
		if Utils.cameraError:
			self.status.SetLabel( Utils.cameraError )
		else:
			self.timer.Start( int(self.frameDelay*1000) )
		
	def updatePhoto( self, event ):
		tNow = now()
		cameraImage = SnapPhoto()
		if not cameraImage:
			self.status.SetLabel( Utils.cameraError if Utils.cameraError else _("Camera Failed: Unknown Error.") )
			return
		
		try:
			photo = AddPhotoHeader( 9999, (tNow - self.tStart).total_seconds(), cameraImage )
			self.status.SetLabel( self.resolutionFormat.format(photo.GetWidth(), photo.GetHeight(), self.fps) )
			self.photo.SetImage( photo )
		except Exception:
			pass
			
		self.frameCount += 1
		if self.frameCount == self.framesPerSecond:
			tNow = now()
			self.fps = self.frameCount / (tNow - self.tStart).total_seconds()
			self.frameCount = 0
			self.tStart = tNow
		
	def onSave( self, event ):
		try:
			tNow = now()
			image = self.photo.GetImage()
		except Exception:
			Utils.MessageOK( self, _('Cannot access photo image.'), title = _("Camera Error"), iconMask=wx.ICON_ERROR )
			return
		
		race = Model.race
		fname = Utils.RemoveDisallowedFilenameChars('{} {}.png'.format( tNow.strftime('%Y-%m-%d %H-%M-%S'), Utils.toAscii(race.name if race else 'CameraTest')) )
		
		with wx.FileDialog( self,
			message=_("Save Photo as PNG File:"),
			wildcard="PNG files (*.png)| *.png",
			style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT,
			defaultDir = Utils.getFileDir(),
		) as fd:
			fd.SetFilename( fname )		
			if fd.ShowModal() != wx.ID_OK:
				return
			fname = fd.GetPath()
		
		try:
			image.SaveFile( fname, wx.BITMAP_TYPE_PNG )
		except Exception as e:
			Utils.MessageOK( self,  '{}\n\n  {}\n\n{}'.format(_('Cannot save photo:'), fname, e),
				title = _("Save Error"), iconMask=wx.ICON_ERROR )
		
	def onClose( self, event ):
		self.timer.Stop()
		SetCameraState( False )
		self.EndModal( wx.ID_OK )
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None, title="CrossMan", size=(100,100))
	mainWin.Show()
	with CameraTestDialog(mainWin) as cameraTestDialog:
		cameraTestDialog.ShowModal()
	app.MainLoop()
		
