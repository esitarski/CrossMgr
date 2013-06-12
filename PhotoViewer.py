import Model
import Utils
import ReadSignOnSheet
from PhotoFinish import getPhotoDirName, ResetPhotoInfoCache, GetPhotoFName
from LaunchFileBrowser import LaunchFileBrowser
from FtpWriteFile import FtpWriteRacePhoto
import wx
import wx.lib.agw.thumbnailctrl as TC
import os
import re
import types
import threading

TestDir = r'C:\Users\Edward Sitarski\Documents\2013-02-07-test-r1-_Photos'

def getRiderName( info ):
	lastName = info.get('LastName','')
	firstName = info.get('FirstName','')
	if lastName:
		if firstName:
			return '%s, %s' % (lastName, firstName)
		else:
			return lastName
	return firstName

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
	fileList.sort( key = lambda f: os.path.basename(f).split('-')[3] )	# Sort by time rather than bib.
	return fileList[-200:]	# Limit to the last 200 photos so as not to crash the system.

def getRiderNameFromFName( fname ):
	# Get the rider name based on the picture fname
	name = ''
	try:
		num = int(os.path.basename(fname).split('-')[1])
	except:
		num = None
		
	if num:
		try:
			externalInfo = Model.race.excelLink.read()
		except:
			externalInfo = {}
		info = externalInfo.get(num, {})
		name = getRiderName( info )
		if info.get('Team', ''):
			name = '%s  (%s)' % (name, info.get('Team', '').strip())
		
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
		image.Rescale( int(wImage * ratio), int(hImage * ratio), wx.IMAGE_QUALITY_HIGH )
		if dc.GetDepth() == 8:
			image = image.ConvertToGreyscale()
		bitmap = image.ConvertToBitmap()
		
		fontHeight = int(border/2 - border/10)
		font = wx.FontFromPixelSize( wx.Size(0,fontHeight), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL )
		dc.DrawText( self.title, border, border )
		dc.DrawBitmap( bitmap, border, (3 * border) // 2 )

		return True

class PhotoViewerDialog( wx.Dialog ):
	ShowAllPhotos = -1

	def __init__(
			self, parent, ID, title='Photo Viewer', size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER ):

		# Instead of calling wx.Dialog.__init__ we precreate the dialog
		# so we can set an extra style that must be set before
		# creation, and then we create the GUI object using the Create
		# method.
		pre = wx.PreDialog()
		#pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
		pre.Create(parent, ID, title, pos, size, style)

		# This next step is the most important, it turns this Python
		# object into the real wrapper of the dialog (instead of pre)
		# as far as the wxPython extension is concerned.
		self.PostCreate(pre)

		self.num = 0
		self.thumbSelected = -1
		self.thumbFileName = ''
		
		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		self.title = wx.StaticText( self, wx.ID_ANY, '' )
		self.title.SetFont( wx.FontFromPixelSize( wx.Size(0,24), wx.FONTFAMILY_SWISS, wx.NORMAL, wx.FONTWEIGHT_NORMAL ) )
		
		self.toolbar = wx.ToolBar( self, wx.ID_ANY )
		self.toolbar.Bind( wx.EVT_TOOL, self.OnToolBar )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Refresh.png'), wx.BITMAP_TYPE_PNG )
		self.refreshID = wx.NewId()
		self.toolbar.AddSimpleTool( self.refreshID, bitmap, 'Refresh Photos' )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'ClipboardPlus.png'), wx.BITMAP_TYPE_PNG )
		self.copyToClipboardID = wx.NewId()
		self.toolbar.AddSimpleTool( self.copyToClipboardID, bitmap, 'Copy Photo to Clipboard...' )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'FileBrowser.png'), wx.BITMAP_TYPE_PNG )
		self.showFilesID = wx.NewId()
		self.toolbar.AddSimpleTool( self.showFilesID, bitmap, 'Show Files...' )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'FTP.png'), wx.BITMAP_TYPE_PNG )
		self.ftpID = wx.NewId()
		self.toolbar.AddSimpleTool( self.ftpID, bitmap, 'Upload Photo with FTP...' )
		
		bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'Printer.png'), wx.BITMAP_TYPE_PNG )
		self.printID = wx.NewId()
		self.toolbar.AddSimpleTool( self.printID, bitmap, 'Print Photo...' )
		
		#self.closeButton = wx.Button( self, wx.ID_CANCEL, 'Close' )
		#self.Bind(wx.EVT_BUTTON, self.OnClose, self.closeButton )
		
		self.toolbar.Realize()
		
		self.splitter = wx.SplitterWindow( self, wx.ID_ANY )
		self.splitter.Bind( wx.EVT_SPLITTER_SASH_POS_CHANGED, self.OnSplitterChange )
		self.thumbs = TC.ThumbnailCtrl( self.splitter, wx.ID_ANY )
		self.thumbs.EnableToolTips( True )
		self.thumbs.SetThumbOutline( TC.THUMB_OUTLINE_FULL )
		self.thumbs._scrolled.filePrefix = '#######################'
		self.thumbs._scrolled.ListDirectory = types.MethodType(ListDirectory, self.thumbs._scrolled)
		self.mainPhoto = wx.StaticBitmap( self.splitter, wx.ID_ANY, style = wx.BORDER_SUNKEN )
		
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
			Utils.MessageOK( self, 'Photo Copied to Clipboard.\nYou can now Paste it into another program.', 'Copy Succeeded' )
		else: 
			Utils.MessageOK( self, 'Unable to Copy Photo to Clipboard.', 'Copy Failed', iconMask = wx.ICON_ERROR )
	
	def OnLauchFileBrowser( self, event ):
		if Utils.mainWin and Utils.mainWin.fileName:
			dir = getPhotoDirName( Utils.mainWin.fileName )
		else:
			dir = TestDir
		LaunchFileBrowser( dir )
	
	def OnFTPUpload( self, event ):
		if not Model.race or not getattr(Model.race, 'ftpHost', None) or getattr(Model.race, 'ftpPhotoPath', None) is None:
			Utils.MessageOK( self, 'FTP Upload Photo Path Not Configured.', 'FTP Publish Failed', iconMask = wx.ICON_ERROR )
			return
			
		# Run the upload in the background so we don't hang the UI.
		thread = threading.Thread( target = FtpWriteRacePhoto, args = (self.thumbFileName,) )
		thread.daemon = True
		thread.run()
	
	def OnPrint( self, event ):
		try:
			bitmap = wx.Bitmap( self.thumbFileName, wx.BITMAP_TYPE_JPEG )
		except:
			Utils.MessageOK( self, 'No Photo Available.', 'Print Failed', iconMask = wx.ICON_ERROR )
			return
		
		if Utils.mainWin:
			pdd = wx.PrintDialogData(Utils.mainWin.printData)
		else:
			printData = wx.PrintData()
			printData.SetPaperId(wx.PAPER_LETTER)
			printData.SetPrintMode(wx.PRINT_MODE_PRINTER)
			printData.SetOrientation(wx.LANDSCAPE)
			pdd = wx.PrintDialogData(printData)
			
		pdd.SetAllPages( 1 )
		pdd.EnablePageNumbers( 0 )
		pdd.EnableHelp( 0 )
		
		printer = wx.Printer(pdd)
		printout = PhotoPrintout( getRiderNameFromFName(self.thumbFileName), self.thumbFileName )

		if not printer.Print(self, printout, True):
			if printer.GetLastError() == wx.PRINTER_ERROR:
				Utils.MessageOK(self, "There was a printer problem.\nCheck your printer setup.", "Printer Error",iconMask=wx.ICON_ERROR)
		else:
			self.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )

		printout.Destroy()
	
	def OnToolBar( self, event ):
		{
			self.refreshID:			self.OnRefresh,
			self.copyToClipboardID:	self.OnCopyToClipboard,
			self.showFilesID:		self.OnLauchFileBrowser,
			self.ftpID:				self.OnFTPUpload,
			self.printID:			self.OnPrint,
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
			name = ('%s  (%d rider photos)' if self.num != self.ShowAllPhotos else '%s  (last %d race photos)') % (name, numPhotos)
			self.title.SetLabel( '%d  %s' % (num, name) )
		
		try:
			bitmap = wx.Bitmap( self.thumbFileName, wx.BITMAP_TYPE_JPEG )
		except:
			self.mainPhoto.SetBitmap( wx.NullBitmap )
			self.mainPhoto.Refresh()
			return
			
		depth = bitmap.GetDepth()
		image = bitmap.ConvertToImage()
		bitmap = None
		
		wPhoto, hPhoto = self.mainPhoto.GetSize()
		wImage, hImage = image.GetSize()
		
		ratio = min( float(wPhoto) / float(wImage), float(hPhoto) / float(hImage) )
		image = image.Rescale( int(wImage * ratio), int(hImage * ratio), wx.IMAGE_QUALITY_HIGH )
		image = image.Resize( (wPhoto, hPhoto), (0,0), 255, 255, 255 )
		
		self.mainPhoto.SetBitmap( image.ConvertToBitmap(depth) )
		self.mainPhoto.Refresh()
		
	def OnPhotoViewer( self, event ):
		self.OnDoPhotoViewer()
		
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
		
	def refresh( self, num = None, t = None ):
		if num:
			self.num = num
		
		with Model.LockRace() as race:
			if race is None:
				self.clear()
				return
				
			# Automatically refresh the screen only if the rider showing has last been updated.
			if num is None and t is None and race.isRunning():
				tLast, rLast = race.getLastKnownTimeRider()
				if rLast and rLast.num != self.num:
					return
				
		if Utils.mainWin and Utils.mainWin.fileName:
			dir = getPhotoDirName( Utils.mainWin.fileName )
		else:
			dir = TestDir
		
		if self.num == self.ShowAllPhotos:
			self.thumbs._scrolled.filePrefix = ''
		else:
			self.thumbs._scrolled.filePrefix = 'bib-%04d' % self.num
		
		if Utils.mainWin:
			ResetPhotoInfoCache( Utils.mainWin.fileName )
		
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
			# Select the photo specified by the time.
			fnameMatch = GetPhotoFName( num, t )
			for i in xrange(itemCount):
				if fnameMatch == self.thumbs.GetItem(i).GetFileName():
					break
			self.thumbs.SetSelection( i )
		else:
			self.thumbs.SetSelection( self.thumbs.GetItemCount() - 1 )
			
		self.OnSelChanged()
	
if __name__ == '__main__':
	race = Model.newRace()
	race._populate()

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	mainWin.Show()
	photoDialog = PhotoViewerDialog( mainWin, wx.ID_ANY, "PhotoViewer", size=(600,400) )
	photoDialog.refresh( photoDialog.ShowAllPhotos )
	photoDialog.Show()
	app.MainLoop()
