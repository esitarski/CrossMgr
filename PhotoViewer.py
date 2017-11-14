import Model
import Utils
import ReadSignOnSheet
from PhotoFinish import GetPhotoFName, TakePhoto
from FinishStrip import ShowFinishStrip
from SendPhotoRequests import getPhotoDirName, SendPhotoRequests
from LaunchFileBrowser import LaunchFileBrowser

import wx
import wx.lib.agw.thumbnailctrl as TC
import os
import sys
import math
import types
import threading
import datetime

TestDir = r'C:\Users\Edward Sitarski\Documents\2013-02-07-test-r1-_Photos'

def getRiderName( info ):
	lastName = info.get('LastName',u'')
	firstName = info.get('FirstName',u'')
	if lastName:
		if firstName:
			return u'{}, {}'.format(lastName, firstName)
		else:
			return lastName
	return firstName

def getFileKey( f ):
	bib, raceTime, count, photoTime = Utils.ParsePhotoFName(f)
	return raceTime
	
def CmpThumb(first, second):
	"""
	Compares two thumbnails by race time, not bib number.

	:param `first`: an instance of L{Thumb};
	:param `second`: another instance of L{Thumb}.
	"""
	return cmp( getFileKey(first.GetFileName()), getFileKey(second.GetFileName()) )

# Monkey Patch thumbnail sort by time.
TC.CmpThumb = CmpThumb
	
def ListDirectory(self, directory, fileExtList):
	"""
	Returns list of file info objects for files of particular extensions.

	:param `directory`: the folder containing the images to thumbnail;
	:param `fileExtList`: a Python list of file extensions to consider.
	"""

	fileList = [os.path.normcase(f) for f in os.listdir(directory)]
	fileList = [f for f in fileList if os.path.splitext(f)[1] in fileExtList]
	fileList = [f for f in fileList
		if os.path.basename(f).startswith(self.filePrefix) and os.path.splitext(f)[1] in ['.jpeg', '.jpg'] ]
	fileList.sort( key = lambda f: getFileKey(os.path.join(directory, f)) )
	return fileList[-2000:]	# Limit to the last 2000 photos so as not to crash the system.

def getRiderNameFromFName( fname ):
	# Get the rider name based on the picture fname
	try:
		num, raceTime, count, photoTime = Utils.ParsePhotoFName(fname)
	except:
		return ''
		
	name = ''
	if num:
		try:
			externalInfo = Model.race.excelLink.read()
		except:
			externalInfo = {}
		info = externalInfo.get(num, {})
		name = getRiderName( info )
		if info.get('Team', u''):
			name = u'{}  ({})'.format(name, info.get('Team', '').strip())
		
	return name
	
class PhotoPrintout(wx.Printout):
	def __init__(self, title, fname):
		wx.Printout.__init__(self)
		self.title = title
		self.fname = fname

	def OnBeginDocument(self, start, end):
		return super(PhotoPrintout, self).OnBeginDocument(start, end)

	def OnEndDocument(self):
		super(PhotoPrintout, self).OnEndDocument()

	def OnBeginPrinting(self):
		super(PhotoPrintout, self).OnBeginPrinting()

	def OnEndPrinting(self):
		super(PhotoPrintout, self).OnEndPrinting()

	def OnPreparePrinting(self):
		super(PhotoPrintout, self).OnPreparePrinting()

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		dc = self.GetDC()
		try:
			bitmap = wx.Bitmap( self.fname, wx.BITMAP_TYPE_JPEG )
		except:
			return False
			
		image = bitmap.ConvertToImage()
		
		wDC, hDC = dc.GetSize()
		border = min(wDC, hDC) // 20
		wPhoto, hPhoto = wDC - border * 2, hDC - (3 * border) // 2
		wImage, hImage = image.GetSize()
		
		ratio = min( float(wPhoto) / float(wImage), float(hPhoto) / float(hImage) )
		image.Rescale( int(wImage * ratio), int(hImage * ratio) )
		if dc.GetDepth() == 8:
			image = image.ConvertToGreyscale()
		
		bitmap = image.ConvertToBitmap()
		dc.DrawBitmap( bitmap, border, border )
		return True

class PhotoViewerDialog( wx.Dialog ):
	ShowAllPhotos = -1

	def __init__( self, parent, ID = wx.ID_ANY, title='Photo Viewer', size=wx.DefaultSize, pos=wx.DefaultPosition, 
					style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.MINIMIZE_BOX|wx.MAXIMIZE_BOX ):
		super(PhotoViewerDialog, self).__init__( parent, ID, title=title, pos=pos, size=size, style=style )

		self.num = 0
		self.thumbSelected = -1
		self.thumbFileName = ''
		
		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		self.title = wx.StaticText( self )
		self.title.SetFont( wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		
		self.toolbar = wx.ToolBar( self )
		self.toolbar.Bind( wx.EVT_TOOL, self.OnToolBar )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Refresh.png'), wx.BITMAP_TYPE_PNG )
		self.refreshID = wx.NewId()
		self.toolbar.AddTool( self.refreshID, _('Refresh Photos'), bitmap )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'ClipboardPlus.png'), wx.BITMAP_TYPE_PNG )
		self.copyToClipboardID = wx.NewId()
		self.toolbar.AddTool( self.copyToClipboardID, _('Copy Photo to Clipboard...'), bitmap )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'FileBrowser.png'), wx.BITMAP_TYPE_PNG )
		self.showFilesID = wx.NewId()
		self.toolbar.AddTool( self.showFilesID, _('Show Files...'), bitmap )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Printer.png'), wx.BITMAP_TYPE_PNG )
		self.printID = wx.NewId()
		self.toolbar.AddTool( self.printID, _('Print Photo...'), bitmap )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'camera_toolbar.png'), wx.BITMAP_TYPE_PNG )
		self.takePhotoID = wx.NewId()
		self.toolbar.AddTool( self.takePhotoID, _('Photo Test'), bitmap )
		
		#bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'CheckeredFlagIcon.png'), wx.BITMAP_TYPE_PNG )
		#self.finishStripID = wx.NewId()
		#self.toolbar.AddTool( self.finishStripID, _('Composite Finish Photo'), bitmap )
		
		#self.closeButton = wx.Button( self, wx.ID_CANCEL, 'Close' )
		#self.Bind(wx.EVT_BUTTON, self.OnClose, self.closeButton )
		
		self.toolbar.Realize()
		
		self.splitter = wx.SplitterWindow( self )
		self.splitter.Bind( wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSplitterChange )
		self.thumbs = TC.ThumbnailCtrl( self.splitter, imagehandler=TC.NativeImageHandler )
		self.thumbs.EnableToolTips( True )
		self.thumbs.SetThumbOutline( TC.THUMB_OUTLINE_FULL )
		self.thumbs._scrolled.filePrefix = '#######################'
		self.thumbs._scrolled.ListDirectory = types.MethodType(ListDirectory, self.thumbs._scrolled)
		self.mainPhoto = wx.StaticBitmap( self.splitter, style = wx.BORDER_SUNKEN )
		
		self.splitter.SetMinimumPaneSize( 140 )
		self.splitter.SplitVertically( self.thumbs, self.mainPhoto, 140 )
		
		self.vbs.Add( self.title, proportion=0, flag=wx.EXPAND|wx.ALL, border = 2 )
		self.vbs.Add( self.toolbar, proportion=0, flag=wx.EXPAND|wx.ALL, border = 2 )
		self.vbs.Add( self.splitter, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border = 4 )
		
		self.Bind( wx.EVT_SIZE, self.OnResize )
		self.thumbs.Bind(TC.EVT_THUMBNAILS_SEL_CHANGED, self.OnSelChanged)
		
		self.SetSizer(self.vbs)
		self.vbs.SetSizeHints(self)
		self.SetSize( (800,560) )
		self.vbs.Layout()

	def OnResize( self, event ):
		self.drawMainPhoto()
		event.Skip()
	
	def OnSplitterChange( self, event ):
		self.vbs.Layout()
		self.drawMainPhoto()
	
	def OnSelChanged(self, event = None):
		self.thumbSelected = self.thumbs.GetSelection()
		try:
			self.thumbFileName = self.thumbs.GetSelectedItem(0).GetFullFileName()
		except:
			self.thumbFileName = ''
		self.drawMainPhoto()
		if event:
			event.Skip()
		
	def OnClose( self, event ):
		self.Show( False )
			
	def OnRefresh( self, event ):
		self.refresh( self.num )
		
	def OnCopyToClipboard( self, event ):
		try:
			bitmap = wx.Bitmap( self.thumbFileName, wx.BITMAP_TYPE_JPEG )
		except:
			return
		d = wx.BitmapDataObject( bitmap )
		if wx.TheClipboard.Open(): 
			wx.TheClipboard.SetData( d ) 
			wx.TheClipboard.Flush() 
			wx.TheClipboard.Close() 
			Utils.MessageOK( self, u'\n\n'.join([_('Photo Copied to Clipboard.'), _('You can now Paste it into another program.')]), _('Copy to Clipboard Succeeded') )
		else: 
			Utils.MessageOK( self, _('Unable to Copy Photo to Clipboard.'), _('Copy Failed'), iconMask=wx.ICON_ERROR )
	
	def OnLaunchFileBrowser( self, event ):
		dir = getPhotoDirName( Utils.mainWin.fileName if Utils.mainWin and Utils.mainWin.fileName else 'Photos' )
		LaunchFileBrowser( dir )
	
	def OnPrint( self, event ):
		try:
			bitmap = wx.Bitmap( self.thumbFileName, wx.BITMAP_TYPE_JPEG )
		except:
			Utils.MessageOK( self, _('No Photo Available.'), _('Print Failed'), iconMask = wx.ICON_ERROR )
			return
		
		if Utils.mainWin:
			pdd = wx.PrintDialogData(Utils.mainWin.printData)
		else:
			printData = wx.PrintData()
			printData.SetPaperId(wx.PAPER_LETTER)
			printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
			printData.SetOrientation(wx.LANDSCAPE)
			pdd = wx.PrintDialogData(printData)
			
		pdd.EnablePageNumbers( 0 )
		pdd.EnableHelp( 0 )
		
		printer = wx.Printer(pdd)
		printout = PhotoPrintout( getRiderNameFromFName(self.thumbFileName), self.thumbFileName )

		if not printer.Print(self, printout, True):
			if printer.GetLastError() == wx.PRINTER_ERROR:
				Utils.MessageOK(self, u'\n\n'.join( [_("There was a printer problem."), _('Check your printer setup.')] ), _("Printer Error"), iconMask=wx.ICON_ERROR)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

		printout.Destroy()
	
	def OnFinishStrip( self, event ):
		ShowFinishStrip( self )
	
	def OnToolBar( self, event ):
		{
			self.refreshID:			self.OnRefresh,
			self.copyToClipboardID:	self.OnCopyToClipboard,
			self.showFilesID:		self.OnLaunchFileBrowser,
			self.printID:			self.OnPrint,
			self.takePhotoID:		self.OnTakePhoto,
			self.finishStripID:		self.OnFinishStrip,
		}[event.GetId()]( event )
	
	def drawMainPhoto( self ):
		self.title.SetLabel( '' )
		self.mainPhoto.Refresh()
		if not self.thumbFileName:
			self.mainPhoto.SetBitmap( wx.NullBitmap )
			self.mainPhoto.Refresh()
			return
		
		# Update the title based on the picture shown.
		try:
			num = int(os.path.basename(self.thumbFileName).split('-')[1])
		except:
			num = None
			
		if num:
			name = getRiderNameFromFName( self.thumbFileName )
			numPhotos = self.thumbs.GetItemCount()
			name = u'{}  ({} {})'.format(name, numPhotos, _('photos') if self.num != self.ShowAllPhotos else _('last race photos'))
			self.title.SetLabel( u'{}  {}'.format(num, name) )
		
		try:
			bitmap = wx.Bitmap( self.thumbFileName, wx.BITMAP_TYPE_JPEG )
		except:
			self.mainPhoto.SetBitmap( wx.NullBitmap )
			self.mainPhoto.Refresh()
			return
			
		depth = bitmap.GetDepth()
		try:
			image = bitmap.ConvertToImage()
		except Exception as e:
			Utils.logException( e, sys.exc_info() )
			self.mainPhoto.SetBitmap( wx.NullBitmap )
			self.mainPhoto.Refresh()
			return
		
		bitmap = None
		
		wPhoto, hPhoto = self.mainPhoto.GetSize()
		wImage, hImage = image.GetSize()
		
		ratio = min( float(wPhoto) / float(wImage), float(hPhoto) / float(hImage) )
		image = image.Rescale( int(wImage * ratio), int(hImage * ratio), wx.IMAGE_QUALITY_HIGH )
		image = image.Resize( (wPhoto, hPhoto), (0,0), 255, 255, 255 )
		
		self.mainPhoto.SetBitmap( image.ConvertToBitmap() )
		self.mainPhoto.Refresh()
		
	def OnTakePhoto( self, event ):
		race = Model.race
		if not race or not race.isRunning():
			Utils.MessageOK( self, _('Race must be running'), _('Camera Test Unavailable') )
			return
		if not race.enableUSBCamera:
			Utils.MessageOK( self, _('USB camera option must be enabled'), _('Camera Test Unavailable') )
			return
		
		testNum = 9999
		raceSeconds = race.curRaceTime()
		success, error = SendPhotoRequests( [(testNum, raceSeconds)] )
		if success:
			wx.CallLater( 750, self.refresh, testNum )
		else:
			Utils.MessageOK( self, u'{}: {}'.format(_('Camera error'), error), _('Camera Error') )
		
	def OnPhotoViewer( self, event ):
		self.OnDoPhotoViewer()
		
	def SetT( self, t ):
		self.refresh( tClosest=t, forceRefresh=True )
		
	def OnClosePhotoViewer( self, event ):
		self.clear()
		
	def OnDoPhotoViewer( self, event = None ):
		self.refresh()

	def setNumSelect( self, num ):
		if self.num != num:
			self.refresh( num )
		
	def clear( self ):
		self.title.SetLabel( '' )
		self.thumbs._scrolled.filePrefix = '##############'
		self.thumbs.ShowDir( '.' )
		
	def refresh( self, num=None, t=None, tClosest=None, forceRefresh=False ):
		if num:
			self.num = num
		
		with Model.LockRace() as race:
			if race is None:
				self.clear()
				return
				
			# Automatically refresh the screen only if the rider showing has last been updated.
			if not forceRefresh and num is None and t is None and race.isRunning():
				tLast, rLast = race.getLastKnownTimeRider()
				if rLast and rLast.num != self.num:
					return
					
		dir = getPhotoDirName( Utils.mainWin.fileName ) if Utils.mainWin and Utils.mainWin.fileName else 'Photos'
		self.thumbs._scrolled.filePrefix = '' if self.num == self.ShowAllPhotos else 'bib-{:04d}'.format(self.num)
		
		if os.path.isdir(dir):
			self.thumbs.ShowDir( dir )
		else:
			self.clear()
			return
		
		itemCount = self.thumbs.GetItemCount()
		if not itemCount:
			self.clear()
			return
		
		if self.num is not None and t is not None:
			# Select the photo specified by the bib and time.
			fnames = [os.path.basename(GetPhotoFName(dir, num, t, i)) for i in xrange(2)]
			for i in xrange(itemCount):
				fnameToMatch = self.thumbs.GetItem(i).GetFileName()
				if any( f in fnameToMatch for f in fnames ):
					break
			self.thumbs.SetSelection( min(i, self.thumbs.GetItemCount() - 1) )
		elif tClosest is not None:
			tDeltaBest = 1000.0*24.0*60.0*60.0
			iBest = None
			for i in xrange(itemCount):
				tDelta = abs( getFileKey(self.thumbs.GetItem(i).GetFileName()) - tClosest )
				if tDelta < tDeltaBest:
					iBest = i
					tDeltaBest = tDelta
			if iBest is not None:
				self.thumbs.SetSelection( iBest )
		else:
			self.thumbs.SetSelection( self.thumbs.GetItemCount() - 1 )
		
		self.OnSelChanged()
	
if __name__ == '__main__':
	Utils.initTranslation()
	
	race = Model.newRace()
	race._populate()
	race.enableUSBCamera = True

	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	mainWin.Show()
	photoDialog = PhotoViewerDialog( mainWin, title = "PhotoViewer", size=(600,400) )
	photoDialog.refresh( photoDialog.ShowAllPhotos )
	photoDialog.Show()
	app.MainLoop()
