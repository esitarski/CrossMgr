import wx
import wx.lib.intctrl
import io
import os
import sys
import ftplib
import urllib
import datetime
import threading
import Utils
import Model
from ExportGrid import getHeaderBitmap, getQRCodeBitmap

import inspect
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def FtpWriteFile( host, user = 'anonymous', passwd = 'anonymous@', timeout = 30, serverPath = '.', fname = '', file = None ):
	ftp = ftplib.FTP( host, timeout = timeout )
	ftp.login( user, passwd )
	if serverPath and serverPath != '.':
		ftp.cwd( serverPath )
	fileOpened = False
	if file is None:
		file = open(fname, 'rb')
		fileOpened = True
	ftp.storbinary( 'STOR {}'.format(os.path.basename(fname)), file )
	ftp.quit()
	if fileOpened:
		file.close()
		
def FtpIsConfigured():
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return False
			
		host		= getattr( race, 'ftpHost', None )
		user		= getattr( race, 'ftpUser', None )
		
	return host and user
		
def FtpUploadFile( fname ):
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return None
			
		host		= getattr( race, 'ftpHost', '' )
		user		= getattr( race, 'ftpUser', '' )
		passwd		= getattr( race, 'ftpPassword', '' )
		serverPath	= getattr( race, 'ftpPath', '' )
	
	try:
		FtpWriteFile(
			host		= host,
			user		= user,
			passwd		= passwd,
			serverPath	= serverPath,
			fname		= fname,
		)
	except Exception as e:
		Utils.writeLog( 'UploadFile: Error: {}'.format(e) )
		return e
		
	return None

def FtpUploadFileAsync( fname ):
	thread = threading.Thread( target=FtpUploadFile, args=(fname,), name='FtpUploadFileAsync: {}'.format(fname) )
	thread.daemon = True
	thread.start()

def FtpWriteRaceHTML():
	Utils.writeLog( 'FtpWriteRaceHTML: called.' )
	
	htmlFile = os.path.join(Utils.getHtmlFolder(), 'RaceAnimation.html')
	try:
		with io.open(htmlFile, 'r', encoding='utf-8') as fp:
			html = fp.read()
	except Exception as e:
		Utils.writeLog( 'FtpWriteRaceHTML Error(1): {}'.format(e) )
		return e
	
	html = Utils.mainWin.addResultsToHtmlStr( html )
	
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return None
			
		host		= getattr( race, 'ftpHost', '' )
		user		= getattr( race, 'ftpUser', '' )
		passwd		= getattr( race, 'ftpPassword', '' )
		serverPath	= getattr( race, 'ftpPath', '' )
		
	fname		= os.path.basename( os.path.splitext(Utils.getFileName())[0] + '.html' )
	defaultPath = os.path.dirname( Utils.getFileName() )
	with io.open(os.path.join(defaultPath, fname), 'w', encoding='utf-8') as fp:
		fp.write( html )
	
	file		= open( os.path.join(defaultPath, fname), 'rb' )
	try:
		FtpWriteFile(	host		= host,
						user		= user,
						passwd		= passwd,
						serverPath	= serverPath,
						fname		= fname,
						file		= file )
	except Exception as e:
		Utils.writeLog( 'FtpWriteRaceHTML Error(2): {}'.format(e) )
		return e
		
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
		However, the out of date the new information will be.
		
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
	return wx.FontFromPixelSize( (0,pixelSize), wx.FONTFAMILY_SWISS, wx.NORMAL,
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
		title = u'{}:{}\n{} {}\n{}   {}'.format( race.name, race.raceNum, _('by'), race.organizer, race.date, race.scheduledStart )
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
			
		bm = getQRCodeBitmap( url )
		
		qrWidth = int( min(heightPix - yPix - borderPix * 2, widthPix - borderPix * 2) )
		magnify = int( qrWidth / bm.GetWidth() )
		qrWidth = bm.GetWidth() * magnify
		xLeft = (widthPix - qrWidth) // 2
		yTop = yPix
		
		dc.SetBrush( wx.BLACK_BRUSH )
		dc.SetPen( wx.TRANSPARENT_PEN )
		
		img = bm.ConvertToImage()
		for y in xrange(img.GetWidth()):
			for x in xrange(img.GetWidth()):
				if img.GetRed(x, y) == 0:
					dc.DrawRectangle( xLeft + x * magnify, yTop + y * magnify, magnify, magnify )
		
		dc.SetFont( getFont(borderPix * 0.25) )
		dc.SetTextForeground( wx.BLACK )
		dc.SetTextBackground( wx.WHITE )
		xText = widthPix - borderPix - dc.GetTextExtent(url)[0]
		yText = yPix + qrWidth + borderPix
		print url, xText, yText, widthPix, heightPix
		dc.DrawText( url, xText, yText )
			
		return True

#------------------------------------------------------------------------------------------------

class FtpPublishDialog( wx.Dialog ):

	fields = 	['ftpHost',	'ftpPath',	'ftpPhotoPath',	'ftpUser',		'ftpPassword',	'ftpUploadDuringRace',	'urlPath', 'ftpUploadPhotos']
	defaults =	['',		'',			'',				'anonymous',	'anonymous@',	False,					'http://',	False]

	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Ftp Publish Results",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		bs = wx.GridBagSizer(vgap=0, hgap=4)
		
		self.ftpHost = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpUploadPhotos = wx.CheckBox( self, label=_("Upload Photos to Path:") )
		self.ftpUploadPhotos.Bind( wx.EVT_CHECKBOX, self.ftpUploadPhotosChanged )
		self.ftpPhotoPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpUser = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPassword = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER|wx.TE_PASSWORD, value='' )
		self.ftpUploadDuringRace = wx.CheckBox( self, label = _("Automatically Upload Results During Race") )
		self.urlPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER )
		self.urlPath.Bind( wx.EVT_TEXT, self.urlPathChanged )
		self.urlFull = wx.StaticText( self )
		
		self.refresh()
		
		self.qrcodeBitmap = wx.StaticBitmap( self, bitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'QRCodeIcon.png'), wx.BITMAP_TYPE_PNG ) )
		self.printBtn = wx.Button( self, label = _('Print Results URL as a QR Code...') )
		self.Bind( wx.EVT_BUTTON, self.onPrint, self.printBtn )
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		self.helpBtn = wx.Button( self, wx.ID_HELP )
		self.Bind( wx.EVT_BUTTON, lambda evt: Utils.showHelp('Menu-File.html#publish-html-results-with-ftp'),
					self.helpBtn )
		
		row = 0
		border = 8
		bs.Add( wx.StaticText( self, label = _("Ftp Host Name:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpHost, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, label = _("Upload HTML to Path:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( self.ftpUploadPhotos,  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPhotoPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, label = _("User:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpUser, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, label = _("Password:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPassword, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( self.ftpUploadDuringRace, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		row += 1
		bs.Add( wx.StaticText( self, label = _("URL Path (optional):")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.urlPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		row += 1
		bs.Add( wx.StaticText( self, label = _("Race Results URL:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.urlFull, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.qrcodeBitmap, flag=wx.ALIGN_CENTRE_VERTICAL )
		hb.Add( self.printBtn, border = border, flag=wx.ALL|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( hb, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL )
		
		row += 1
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.okBtn, border = border, flag=wx.ALL )
		hb.Add( self.cancelBtn, border = border, flag=wx.ALL )
		hb.Add( self.helpBtn, border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		
		bs.Add( hb, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onPrint( self, event ):
		race = Model.race
		if not race:
			return
			
		self.setRaceAttr()
		
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
		with Model.LockRace() as race:
			if not race:
				for f, v in zip(FtpPublishDialog.fields, FtpPublishDialog.defaults):
					getattr(self, f).SetValue( v )
			else:
				for f, v in zip(FtpPublishDialog.fields, FtpPublishDialog.defaults):
					getattr(self, f).SetValue( getattr(race, f, v) )
		self.urlPathChanged()
		self.ftpUploadPhotosChanged()
	
	def setRaceAttr( self ):
		self.urlPathChanged()
		with Model.LockRace() as race:
			if race:
				for f in FtpPublishDialog.fields:
					setattr( race, f, getattr(self, f).GetValue() )
				race.urlFull = self.urlFull.GetLabel()
	
	def onOK( self, event ):
		self.setRaceAttr()
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
		
if __name__ == '__main__':
	'''
	file = StringIO.StringIO( 'This is a test' )
	FtpWriteFile(	host = 'ftp://127.0.0.1:55555',
					user = 'crossmgr',
					passwd = 'crossmgr',
					timeout = 30,
					serverPath = '',
					fname = 'test.html',
					file = None )
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
