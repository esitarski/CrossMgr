import wx
import time
import datetime
import threading
from Queue import Queue, Empty
import Utils
import Model
from PhotoFinish import AddPhotoHeader, SetCameraState, SnapPhoto

now = datetime.datetime.now

def RescaleImage( image, width, height ):
	wImage = image.GetWidth()
	hImage = image.GetHeight()
	ratio = min( float(width) / float(wImage), float(height) / float(hImage) )
	return image.Rescale( int(wImage*ratio), int(hImage*ratio), wx.IMAGE_QUALITY_NORMAL ) if not (0.94 < ratio < 1.06) else image
	
class ScaledImage( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=(640,400) ):
		super(ScaledImage, self).__init__( parent, id, size=size )
		self.SetBackgroundStyle( wx.BG_STYLE_CUSTOM )
		self.image = None
		self.Bind( wx.EVT_PAINT, self.OnPaint )
		
	def OnPaint( self, event=None ):
		dc = wx.AutoBufferedPaintDC( self )
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
		
		width, height = self.GetSizeTuple()
		try:
			image = self.image.Copy()
			image = RescaleImage( image, width, height )
		except:
			return
		
		bitmap = wx.BitmapFromImage( image )
		dc.DrawBitmap( bitmap, (width - bitmap.GetWidth())//2, (height - bitmap.GetHeight())//2 )
	
	def SetImage( self, image ):
		self.image = image
		self.Refresh()
		
	def GetImage( self ):
		return self.image

class CameraTestDialog( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, title=_("Camera Test"), size=(690, 590) ):
		super(CameraTestDialog, self).__init__(
			parent, id, title=title, size=size,
			style=wx.CAPTION
		)
		
		SetCameraState( False )

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
		
		self.resolutionFormat = _("Camera Resolution") + u': {} x {}'
		
		self.tStart = now()
		self.frameDelay = 1.0/25.0
		self.timer = wx.Timer( self )
		self.Bind( wx.EVT_TIMER, self.updatePhoto )
		
		SetCameraState( True )
		
		if Utils.cameraError:
			self.status.SetLabel( Utils.cameraError )
		else:
			self.timer.Start( self.frameDelay )
		
	def updatePhoto( self, event ):
		tNow = now()
		cameraImage = SnapPhoto()
		if not cameraImage:
			self.status.SetLabel( Utils.cameraError if Utils.cameraError else _("Camera Failed: Unknown Error.") )
			return
			
		try:
			photo = AddPhotoHeader( 9999, (tNow - self.tStart).total_seconds(), cameraImage )
			self.status.SetLabel( self.resolutionFormat.format(photo.GetWidth(), photo.GetHeight()) )
			self.photo.SetImage( photo )
		except:
			pass
		
	def onSave( self, event ):
		try:
			tNow = now()
			image = self.photo.GetImage()
		except:
			Utils.MessageOK( self, _('Cannot access photo image.'), title = _("Camera Error"), iconMask=wx.ICON_ERROR )
			return
		
		race = Model.race
		fname = Utils.RemoveDisallowedFilenameChars(u'{} {}.png'.format( tNow.strftime('%Y-%m-%d %H-%M-%S'), Utils.toAscii(race.name if race else 'CameraTest')) )
		
		fd = wx.FileDialog( self,
			message=_("Save Photo as PNG File:"),
			wildcard="PNG files (*.png)| *.png",
			style=wx.FD_SAVE|wx.FD_OVERWRITE_PROMPT
		)
		fd.SetFilename( fname )
		
		ret = fd.ShowModal()
		if ret != wx.ID_OK:
			fd.Destroy()
			return
		fname = fd.GetPath()
		fd.Destroy()
		
		try:
			image.SaveFile( fname, wx.BITMAP_TYPE_PNG )
		except Exception as e:
			Utils.MessageOK( self, _('Cannot save photo:') + +u'\n\n' + _('Filename:') + u'  {}'.format(fname) + u'\n\n{}'.format(e),
				title = _("Save Error"), iconMask=wx.ICON_ERROR )
		
	def onClose( self, event ):
		self.timer.Stop()
		SetCameraState( False )
		self.EndModal( wx.ID_OK )
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None, title="CrossMan", size=(100,100))
	mainWin.Show()
	cameraTestDialog = CameraTestDialog( mainWin )
	cameraTestDialog.ShowModal()
	cameraTestDialog.Destroy()
	app.MainLoop()
		
