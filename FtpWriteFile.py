import wx
import wx.lib.intctrl
import io
import os
import sys
import webbrowser
import ftputil
import urllib
import datetime
import threading
import Utils
import Model
import HelpSearch
from ExportGrid import getHeaderBitmap, drawQRCode
from WebServer import WriteHtmlIndexPage

import inspect
def lineno():
	"""Returns the current line number in our program."""
	return inspect.currentframe().f_back.f_lineno

def FtpWriteFile( host, user='anonymous', passwd='anonymous@', timeout=30, serverPath='.', fname='', callback=None ):
	
	if isinstance(fname, basestring):
		fname = [fname]
	
	# This stops the ftputils from going into an infinite loop.
	serverPath = serverPath.strip().lstrip('/').lstrip('\\')
	
	'''
	if callback:
		print 'FtpWriteFile: called with callback'
		import time
		for i, f in enumerate(fname):
			fSize = os.path.getsize(f)
			for s in xrange(0, fSize, 1024 ):
				callback( ' '*1024, f, i )
				time.sleep( 0.1 )
			if s != fSize:
				callback( ' '*(fSize-s), f, i )
				time.sleep( 0.1 )
			#if i == 2:
			#	raise ValueError, 'Testing exception'
		return
	'''
	
	with ftputil.FTPHost( host, user, passwd ) as host:
		try:
			host.makedirs( serverPath )
		except Exception as e:
			pass
		for i, f in enumerate(fname):
			host.upload_if_newer(
				f,
				serverPath + '/' + os.path.basename(f),
				(lambda byteStr, fname=f, i=i: callback(byteStr, fname, i)) if callback else None
			)

def FtpIsConfigured():
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return False
			
		host		= getattr( race, 'ftpHost', None )
		user		= getattr( race, 'ftpUser', None )
		
	return host and user
	
def FtpUploadFile( fname=None, callback=None ):
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return None
	
	try:
		FtpWriteFile(
			host		= getattr( race, 'ftpHost', '' ),
			user		= getattr( race, 'ftpUser', '' ),
			passwd		= getattr( race, 'ftpPassword', '' ),
			serverPath	= getattr( race, 'ftpPath', '' ),
			fname		= fname or [],
			callback	= callback,
		)
	except ftputil.error.FTPOSError as e:
		Utils.writeLog( 'FtpUploadFile: Error: {}'.format(e) )
		return e
	except Exception as e:
		# Utils.logException( e, sys.exc_info() )
		Utils.writeLog( 'FtpUploadFile: Error: {}'.format(e) )
		return e
		
	return None
	
def FtpTest():
	return FtpUploadFile()

def FtpUploadFileAsync( fname ):
	thread = threading.Thread( target=FtpUploadFile, args=(fname,), name='FtpUploadFileAsync: {}'.format(fname) )
	thread.daemon = True
	thread.start()

def FtpWriteRaceHTML():
	Utils.writeLog( 'FtpWriteRaceHTML: called.' )
	
	html = Model.getCurrentHtml()
	if not html:
		return None
	
	try:
		fname = os.path.splitext(Utils.getFileName())[0] + '.html'
		with io.open(fname, 'w', encoding='utf-8') as fp:
			fp.write( html )
		html = None
	except Exception as e:
		Utils.writeLog( 'FtpWriteRaceHTML: (2) "{}"'.format(e) )
		return None
	
	files = [fname]
	try:
		if (getattr(Model.race, 'publishFormatIndexHtml', 3) & 3) == 3:
			files.append( WriteHtmlIndexPage() )
	except Exception as e:
		pass
	
	FtpUploadFile( files )
	return None

class RealTimeFtpPublish( object ):
	latencyTimeMin = 3
	latencyTimeMax = 32

	def __init__( self ):
		self.timer = None
		self.latencyTime = RealTimeFtpPublish.latencyTimeMin
		self.lastUpdateTime = datetime.datetime.now() - datetime.timedelta( seconds = 24*60*60 )

	def publish( self ):
		self.timer = None	# Cancel the one-shot timer.
		FtpWriteRaceHTML()
		self.lastUpdateTime = datetime.datetime.now()

	def publishEntry( self, publishNow = False ):
		'''
		This function attempts to publish race results with low latency but without wasting bandwidth.
		It was inspired by TCP/IP and double-exponential backoff.
		
		When we get a new entry, we schedule an update in the future to give time for more entries to accumulate.
		The longer we wait, the more likely that more entries are going to arrive.
		However, the more out of date the new information will be.
		
		The logic below attempts to balance bandwidth and latency.
		The procedure is based on latencyTime, the current time to wait before publishing an update,
		and lastUpdateTime, the last time an update was made.
		
		If the time of the last update is less than the last latencyTime, we double latencyTime.
		If the time of the last update exceeds the last latencyTime, we reset latencyTime to latencyTimeMin.
		
		The behavior we expect to see is that when the first riders cross the line on a lap, an update will be triggered
		4 seconds in the future.  Any lead riders arriving in those 4 seconds will be included in the update.
		
		If the entire pack goes by, we are done.
		If stragglers arrive within 4 seconds, the latency time doubles to a maximum to 8 to get more stragglers.
		In this way, the latency increases longer and longer to get the stragglers, giving them more time to arrive.
		'''
		if self.timer is not None:
			return

		# If this publish request is less than latencyTime, double latencyTime for the next publish waiting interval.
		# If this publish request exceeds latencyTime, reset latencyTime to latencyTimeMin.
		if (datetime.datetime.now() - self.lastUpdateTime).total_seconds() < self.latencyTime:
			self.latencyTime = min( self.latencyTimeMax, self.latencyTime * 2 )
		else:
			self.latencyTime = self.latencyTimeMin
		
		self.timer = threading.Timer( self.latencyTime if not publishNow else 0.1, self.publish )
		self.timer.daemon = True
		self.timer.name = 'FTP Publish Timer'
		self.timer.start()

realTimeFtpPublish = RealTimeFtpPublish()

#------------------------------------------------------------------------------------------------
def drawMultiLineText( dc, text, x, y ):
	if not text:
		return
	wText, hText, lineHeightText = dc.GetMultiLineTextExtent( text, dc.GetFont() )
	for line in text.split( '\n' ):
		dc.DrawText( line, x, y )
		y += lineHeightText

def getFont( pixelSize = 28, isBold = False ):
	return wx.Font( (0,pixelSize), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
								 wx.FONTWEIGHT_BOLD if isBold else wx.FONTWEIGHT_NORMAL )

def getFontToFit( dc, widthToFit, heightToFit, sizeFunc, isBold = False ):
	left = 1
	right = max(widthToFit, heightToFit)
	
	while right - left > 1:
		mid = (left + right) / 2.0
		font = getFont( mid, isBold )
		widthText, heightText = sizeFunc( font )
		if widthText <= widthToFit and heightText <= heightToFit:
			left = mid
		else:
			right = mid - 1
	
	return getFont( left, isBold )
	
class FtpQRCodePrintout( wx.Printout ):
	def __init__(self, categories = None):
		wx.Printout.__init__(self)

	def OnBeginDocument(self, start, end):
		return super(FtpQRCodePrintout, self).OnBeginDocument(start, end)

	def OnEndDocument(self):
		super(FtpQRCodePrintout, self).OnEndDocument()

	def OnBeginPrinting(self):
		super(FtpQRCodePrintout, self).OnBeginPrinting()

	def OnEndPrinting(self):
		super(FtpQRCodePrintout, self).OnEndPrinting()

	def OnPreparePrinting(self):
		super(FtpQRCodePrintout, self).OnPreparePrinting()

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		race = Model.race
		if not race:
			return
			
		dc = self.GetDC()
		
		widthPix, heightPix = dc.GetSizeTuple()
		
		# Get a reasonable border.
		borderPix = max(widthPix, heightPix) / 20
		
		widthFieldPix = widthPix - borderPix * 2
		heightFieldPix = heightPix - borderPix * 2
		
		xPix = borderPix
		yPix = borderPix
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = heightPix * 0.15
		graphicWidth = float(bmWidth) / float(bmHeight) * graphicHeight
		graphicBorder = int(graphicWidth * 0.15)

		# Rescale the graphic to the correct size.
		# We cannot use a GraphicContext because it does not support a PrintDC.
		img = bitmap.ConvertToImage()
		img.Rescale( graphicWidth, graphicHeight, wx.IMAGE_QUALITY_HIGH )
		if dc.GetDepth() == 8:
			img = img.ConvertToGreyscale()
		bm = img.ConvertToBitmap( dc.GetDepth() )
		dc.DrawBitmap( bm, xPix, yPix )
		
		# Draw the title.
		title = u'{}:{}\n{} {}\n{}   {}'.format( race.title, race.raceNum, _('by'), race.organizer, race.date, race.scheduledStart )
		font = getFontToFit( dc, widthFieldPix - graphicWidth - graphicBorder, graphicHeight,
									lambda font: dc.GetMultiLineTextExtent(title, font)[:-1], True )
		dc.SetFont( font )
		drawMultiLineText( dc, title, xPix + graphicWidth + graphicBorder, yPix )
		yPix += graphicHeight + borderPix
		
		heightFieldPix = heightPix - yPix - borderPix
		url = getattr( race, 'urlFull', '' )
		if url.startswith( 'http://' ):
			url = urllib.quote( url[7:] )
		else:
			url = urllib.quote( url )
			
		qrWidth = int( min(heightPix - yPix - borderPix * 2, widthPix - borderPix * 2) )
		xLeft = (widthPix - qrWidth) // 2
		yTop = yPix		
		drawQRCode( url, dc, xLeft, yTop, qrWidth )
		
		dc.SetFont( getFont(borderPix * 0.25) )
		dc.SetTextForeground( wx.BLACK )
		dc.SetTextBackground( wx.WHITE )
		xText = widthPix - borderPix - dc.GetTextExtent(url)[0]
		yText = yPix + qrWidth + borderPix
		dc.DrawText( url, xText, yText )
			
		return True

#------------------------------------------------------------------------------------------------

ftpFields = 	['ftpHost',	'ftpPath',	'ftpPhotoPath',	'ftpUser',		'ftpPassword',	'ftpUploadDuringRace',	'urlPath', 'ftpUploadPhotos']
ftpDefaults =	['',		'',			'',				'anonymous',	'anonymous@',	False,					'http://',	False]

def GetFtpPublish( isDialog=True ):
	ParentClass = wx.Dialog if isDialog else wx.Panel
	class FtpPublishObject( ParentClass ):

		def __init__( self, parent, id=wx.ID_ANY, uploadNowButton=True ):
			if isDialog:
				super(FtpPublishObject, self).__init__( parent, id, _("Ftp Publish Results"),
								style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
			else:
				super(FtpPublishObject, self).__init__( parent, id )
							
			fgs = wx.FlexGridSizer(vgap=4, hgap=4, rows=0, cols=2)
			fgs.AddGrowableCol( 1, 1 )
			
			self.ftpHost = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
			self.ftpPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
			self.ftpUploadPhotos = wx.CheckBox( self, label=_("Upload Photos to Path") )
			self.ftpUploadPhotos.Bind( wx.EVT_CHECKBOX, self.ftpUploadPhotosChanged )
			self.ftpPhotoPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
			self.ftpUser = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
			self.ftpPassword = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER|wx.TE_PASSWORD, value='' )
			self.ftpUploadDuringRace = wx.CheckBox( self, label = _("Automatically Upload Results During Race") )
			self.urlPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER )
			self.urlPath.Bind( wx.EVT_TEXT, self.urlPathChanged )
			self.urlFull = wx.StaticText( self )
			
			self.refresh()
			
			self.qrcodeBitmap = wx.StaticBitmap( self, wx.ID_ANY, wx.Bitmap( os.path.join(Utils.getImageFolder(), 'QRCodeIcon.png'), wx.BITMAP_TYPE_PNG ) )
			self.printBtn = wx.Button( self, label = _('Print Results URL as a QR Code...') )
			self.Bind( wx.EVT_BUTTON, self.onPrint, self.printBtn )
			
			if isDialog:
				self.okBtn = wx.Button( self, wx.ID_OK )
				self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

				self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
				self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
				
				self.helpBtn = wx.Button( self, wx.ID_HELP )
				self.Bind( wx.EVT_BUTTON, lambda evt: HelpSearch.showHelp('Menu-File.html#publish-html-results-with-ftp'), self.helpBtn )
			
			fgs.Add( wx.StaticText( self, label = _("Ftp Host Name")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.ftpHost, 1, flag=wx.TOP|wx.ALIGN_LEFT|wx.EXPAND )
			
			fgs.Add( wx.StaticText( self, label = _("Upload files to Path")),  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.ftpPath, 1, flag=wx.EXPAND )
			
			fgs.Add( self.ftpUploadPhotos, flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.ftpPhotoPath, 1, flag=wx.EXPAND )
			
			fgs.Add( wx.StaticText( self, label = _("User")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.ftpUser, 1, flag=wx.EXPAND )
			
			fgs.Add( wx.StaticText( self, label = _("Password")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.ftpPassword, 1, flag=wx.EXPAND )
			
			fgs.AddSpacer( 16 )
			fgs.Add( self.ftpUploadDuringRace )
			
			fgs.AddSpacer( 16 )
			fgs.AddSpacer( 16 )
			
			fgs.Add( wx.StaticText( self, label = _("URL Path (optional)")),  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.urlPath, 1, flag=wx.EXPAND )
			
			fgs.Add( wx.StaticText( self, label = _("Published Results URL")),  flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.urlFull, 1, flag=wx.EXPAND )
			
			border = 4
			hb = wx.BoxSizer( wx.HORIZONTAL )
			hb.Add( self.qrcodeBitmap, flag=wx.ALIGN_CENTRE_VERTICAL )
			hb.Add( self.printBtn, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL, border=border )
			fgs.AddSpacer( 16 )
			fgs.Add( hb )
			
			if isDialog:
				hb = wx.BoxSizer( wx.HORIZONTAL )
				hb.Add( self.okBtn, border = border, flag=wx.ALL )
				hb.Add( self.cancelBtn, border = border, flag=wx.ALL )
				hb.Add( self.helpBtn, border = border, flag=wx.ALL )
				self.okBtn.SetDefault()
				
				mvs = wx.BoxSizer( wx.VERTICAL )
				mvs.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=4 )
				mvs.Add( hb, flag=wx.ALL|wx.ALIGN_CENTER, border=4 )
				self.SetSizerAndFit( mvs )
				mvs.Fit( self )
			
				self.CentreOnParent( wx.BOTH )
				wx.CallAfter( self.SetFocus )
			else:
				self.ftpTestButton = wx.Button( self, label=_('Test FTP Connection') )
				self.ftpTestButton.Bind( wx.EVT_BUTTON, self.onFtpTest )
				if uploadNowButton:
					self.ftpUploadNowButton = wx.Button( self, label=_('Do FTP Upload Now') )
					self.ftpUploadNowButton.Bind( wx.EVT_BUTTON, self.onFtpUploadNow )
				fgs.AddSpacer( 16 )
				fgs.AddSpacer( 16 )
				fgs.Add( self.ftpTestButton, flag=wx.ALIGN_RIGHT )
				if uploadNowButton:
					fgs.Add( self.ftpUploadNowButton )
				else:
					fgs.AddSpacer( 4 )
				self.SetSizerAndFit( fgs )
				fgs.Fit( self )

		def onFtpTest( self, event ):
			self.commit()
			result = FtpTest()
			if result:
				Utils.MessageOK(self, u'{}\n\n{}\n'.format(_("Ftp Test Failed"), result), _("Ftp Test Failed"), iconMask=wx.ICON_ERROR)
			else:
				Utils.MessageOK(self, _("Ftp Test Successful"), _("Ftp Test Successful"))				

		def onFtpUploadNow( self, event ):
			self.commit()
			FtpUploadNow( self )
		
		def onPrint( self, event ):
			race = Model.race
			if not race:
				return
				
			self.commit()
			
			mainWin = Utils.getMainWin()
			pd = mainWin.printData if mainWin else wx.PrintData()
			orientationSave = pd.GetOrientation()
			pd.SetOrientation( wx.PORTRAIT )
			
			pdd = wx.PrintDialogData( pd )
			pdd.SetAllPages( True )
			pdd.EnableSelection( False )
			pdd.EnablePageNumbers( False )
			pdd.EnableHelp( False )
			pdd.EnablePrintToFile( False )
			
			printer = wx.Printer( pdd )
			printout = FtpQRCodePrintout()

			if not printer.Print(self, printout, True):
				if printer.GetLastError() == wx.PRINTER_ERROR:
					Utils.MessageOK(self, u'\n\n'.join( [_("There was a printer problem."),_("Check your printer setup.")] ), _("Printer Error"), iconMask=wx.ICON_ERROR)

			pd.SetOrientation( orientationSave )
			printout.Destroy()
			
		def urlPathChanged( self, event = None ):
			url = self.urlPath.GetValue()
			fname = Utils.getFileName()
			if not url or url == 'http://' or not Model.race or not fname:
				self.urlFull.SetLabel( '' )
			else:
				if not url.endswith( '/' ):
					url += '/'
				fname = os.path.basename( fname[:-4] + '.html' )
				url += fname
				self.urlFull.SetLabel( url )
				
		def ftpUploadPhotosChanged( self, event = None ):
			self.ftpPhotoPath.SetEditable( self.ftpUploadPhotos.GetValue() )
			self.ftpPhotoPath.Enable( self.ftpUploadPhotos.GetValue() )
			
		def refresh( self ):
			race = Model.race
			if not race:
				for f, v in zip(ftpFields, ftpDefaults):
					getattr(self, f).SetValue( v )
			else:
				for f, v in zip(ftpFields, ftpDefaults):
					getattr(self, f).SetValue( getattr(race, f, v) )
			self.urlPathChanged()
			self.ftpUploadPhotosChanged()
		
		def commit( self ):
			self.urlPathChanged()
			race = Model.race
			if race:
				for f in ftpFields:
					setattr( race, f, getattr(self, f).GetValue() )
				race.urlFull = self.urlFull.GetLabel()
			race.setChanged()
		
		def onOK( self, event ):
			self.commit()
			self.EndModal( wx.ID_OK )
			
		def onCancel( self, event ):
			self.EndModal( wx.ID_CANCEL )
			
	return FtpPublishObject

def FtpPublishDialog( parent, *args, **kwargs ):
	return GetFtpPublish( True )( parent, *args, **kwargs )

def FtpProperties( parent, *args, **kwargs ):
	return GetFtpPublish( False )( parent, *args, **kwargs )

def FtpUploadNow( parent ):
	race = Model.race
	host = getattr( race, 'ftpHost', '' )
		
	if not host:
		Utils.MessageOK(parent, u'{}\n\n    {}'.format(_('Error'), _('Missing host name.')), _('Ftp Upload Failed'), iconMask=wx.ICON_ERROR )
		return
	
	wx.BeginBusyCursor()
	e = FtpWriteRaceHTML()
	wx.EndBusyCursor()

	if e:
		Utils.MessageOK(parent, u'{}  {}\n\n{}'.format(_('Ftp Upload Failed.'), _('Error'), e), _('Ftp Upload Failed'), iconMask=wx.ICON_ERROR )
	else:
		# Automatically open the browser on the published file for testing.
		if race.urlFull and race.urlFull != 'http://':
			webbrowser.open( race.urlFull, new = 0, autoraise = True )

if __name__ == '__main__':
	'''
	FtpWriteFile(	host = 'ftp://127.0.0.1:55555',
					user = 'crossmgr',
					passwd = 'crossmgr',
					timeout = 30,
					serverPath = '',
					fname = 'test.html',
	)
	sys.exit()
	'''

	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMgr", size=(600,400))
	Model.setRace( Model.Race() )
	Model.getRace()._populate()
	ftpPublishDialog = FtpPublishDialog(mainWin)
	ftpPublishDialog.ShowModal()
	mainWin.Show()
	app.MainLoop()
