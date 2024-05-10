import os
import wx
import wx.lib.intctrl
import webbrowser
import ftputil
import paramiko
from urllib.parse import quote
import datetime
import threading

import Utils
import Model
from ExportGrid import getHeaderBitmap, drawQRCode
from WebServer import WriteHtmlIndexPage

import inspect
def lineno():
	"""Returns the current line number in our program."""
	return inspect.currentframe().f_back.f_lineno
	
class CallCloseOnExit:
	def __enter__(self, obj):
		self.obj = obj
		return obj

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.obj.close()

class SftpCallback:
	def __init__( self, callback, fname, i ):
		self.callback = callback
		self.fname = fname
		self.i = i
		self.bytesCur = 0
		
	def __call__( self, bytesCur, bytesTotal ):
		# Fake a call to the ftputil callback signature.
		self.callback( b' '*(bytesCur - self.bytesCur), self.fname, self.i )
		self.bytesCur = bytesCur

def sftp_mkdir_p( sftp, remote_directory ):
	dirs_exist = remote_directory.split('/')
	i_dir_last = len( dirs_exist )
	
	# Find the highest level where the dir exists.
	while i_dir_last:
		try:
			sftp.listdir('/'.join(dirs_exist[:i_dir_last]))
			break
		except IOError:
			i_dir_last -= 1
	
	# Create new dirs starting from the last one that existed.
	for i in range( i_dir_last, len(dirs_exist) ):
		sftp.mkdir( '/'.join(dirs_exist[:i+1]) )

def FtpWriteFile( host, user='anonymous', passwd='anonymous@', timeout=30, serverPath='.', fname='', useSftp=False, sftpPort=22, callback=None ):
	
	if isinstance(fname, str):
		fname = [fname]

	# Normalize serverPath.
	serverPath = serverPath.strip().replace('\\', '/').rstrip('/')
	
	if not useSftp:
		# Stops ftputils from going into an infinite loop by removing leading slashes..
		serverPath = serverPath.lstrip('/').lstrip('\\')
	
	'''
	if callback:
		print( 'FtpWriteFile: called with callback' )
		import time
		for i, f in enumerate(fname):
			fSize = os.path.getsize(f)
			for s in range(0, fSize, 1024 ):
				callback( b' '*1024, f, i )
				time.sleep( 0.1 )
			if s != fSize:
				callback( b' '*(fSize-s), f, i )
				time.sleep( 0.1 )
			#if i == 2:
			#	raise ValueError, 'Testing exception'
		return
	'''
	
	if useSftp:
		with CallCloseOnExit(paramiko.SSHClient()) as ssh:
			ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
			ssh.load_system_host_keys()                  
			ssh.connect( host, sftpPort, user, passwd )

			with CallCloseOnExit(ssh.open_sftp()) as sftp:
				sftp_mkdir_p( sftp, serverPath )
				for i, f in enumerate(fname):
					sftp.put(
						f,
						serverPath + '/' + os.path.basename(f),
						SftpCallback( callback, f, i ) if callback else None
					)
	else:
		with ftputil.FTPHost( host, user, passwd ) as ftp_host:
			ftp_host.makedirs( serverPath, exist_ok=True )
			for i, f in enumerate(fname):
				ftp_host.upload_if_newer(
					f,
					serverPath + '/' + os.path.basename(f),
					(lambda byteStr, fname=f, i=i: callback(byteStr, fname, i)) if callback else None
				)

def FtpIsConfigured():
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return False
			
		host = getattr( race, 'ftpHost', None )
		user = getattr( race, 'ftpUser', None )
		
	return host and user
	
def FtpUploadFile( fname=None, callback=None ):
	with Model.LockRace() as race:
		if not race or not Utils.getFileName():
			return None
	
	params = {
		'host': 		getattr(race, 'ftpHost', '').strip().strip('\t'),	# Fix cut and paste problems.
		'user':			getattr(race, 'ftpUser', ''),
		'passwd':		getattr(race, 'ftpPassword', ''),
		'serverPath':	getattr(race, 'ftpPath', ''),
		'useSftp':		getattr(race, 'useSftp', False),
		'fname':		fname or [],
		'callback':		callback,
	}
	
	try:		
		FtpWriteFile( **params )
	
	except Exception as e:
		Utils.writeLog( 'FtpUploadFile: {}: {}'.format(e.__class__.__name__, e) )
		Utils.writeLog( 'FtpUploadFile: call FtpWriteFile({})'.format(', '.join('{}="{}"'.format(k,v) for k,v in params.items())) )
		return e
		
	return None
	
def FtpTest():
	return FtpUploadFile()

def FtpUploadFileAsync( fname ):
	thread = threading.Thread( target=FtpUploadFile, args=(fname,), name='FtpUploadFileAsync: {}'.format(fname) )
	thread.daemon = True
	thread.start()

def FtpWriteRaceHTML():
	html = Model.getCurrentHtml()
	if not html:
		return None
	
	try:
		fname = os.path.splitext(Utils.getFileName())[0] + '.html'
		with open(fname, 'w', encoding='utf8') as fp:
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

class RealTimeFtpPublish:
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
		This function attempts to publish competiton results with low latency but without wasting bandwidth.
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
	lineHeightText = dc.GetTextExtent( 'Py' )[1]
	for line in text.split( '\n' ):
		dc.DrawText( line, x, y )
		y += lineHeightText

def getFont( pixelSize = 28, isBold = False ):
	return wx.Font( (0,int(pixelSize)), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL,
								 wx.FONTWEIGHT_BOLD if isBold else wx.FONTWEIGHT_NORMAL )

def getFontToFit( dc, widthToFit, heightToFit, sizeFunc, isBold = False ):
	left = 1
	right = max(widthToFit, heightToFit)
	
	while right - left > 1:
		mid = (left + right) // 2
		font = getFont( mid, isBold )
		widthText, heightText = sizeFunc( font )
		if widthText <= widthToFit and heightText <= heightToFit:
			left = mid
		else:
			right = mid - 1
	
	return getFont( left, isBold )
	
class FtpQRCodePrintout( wx.Printout ):
	def __init__(self, categories = None):
		super().__init__()

	def OnBeginDocument(self, start, end):
		return super().OnBeginDocument(start, end)

	def OnEndDocument(self):
		super().OnEndDocument()

	def OnBeginPrinting(self):
		super().OnBeginPrinting()

	def OnEndPrinting(self):
		super().OnEndPrinting()

	def OnPreparePrinting(self):
		super().OnPreparePrinting()

	def HasPage(self, page):
		return page == 1

	def GetPageInfo(self):
		return (1,1,1,1)

	def OnPrintPage(self, page):
		race = Model.race
		if not race:
			return
			
		dc = self.GetDC()
		
		widthPix, heightPix = dc.GetSize()
		
		# Get a reasonable border.
		borderPix = int(max(widthPix, heightPix) / 20)
		
		widthFieldPix = widthPix - borderPix * 2
		
		xPix = borderPix
		yPix = borderPix
		
		# Draw the graphic.
		bitmap = getHeaderBitmap()
		bmWidth, bmHeight = bitmap.GetWidth(), bitmap.GetHeight()
		graphicHeight = int(heightPix * 0.15)
		graphicWidth = int(float(bmWidth) / float(bmHeight) * graphicHeight)
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
		title = '{}:{}\n{} {}\n{}   {}'.format( race.title, race.raceNum, _('by'), race.organizer, race.date, race.scheduledStart )
		def getTitleTextSize( font ):
			dc.SetFont( font )
			return dc.GetMultiLineTextExtent( title )
		font = getFontToFit( dc, widthFieldPix - graphicWidth - graphicBorder, graphicHeight, getTitleTextSize, True )
		dc.SetFont( font )
		drawMultiLineText( dc, title, xPix + graphicWidth + graphicBorder, yPix )
		yPix += graphicHeight + borderPix
		
		heightPix - yPix - borderPix
		url = getattr( race, 'urlFull', '' )
		if url.startswith( 'http://' ):
			url = quote( url[7:] )
		else:
			url = quote( url )
			
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

ftpFields = 	['ftpHost',	'ftpPath',	'ftpPhotoPath',	'ftpUser',		'ftpPassword',	'useSftp',	'ftpUploadDuringRace',	'urlPath', 'ftpUploadPhotos']
ftpDefaults =	['',		'',			'',				'anonymous',	'anonymous@',	False,		False,					'http://',	False]

def GetFtpPublish( isDialog=True ):
	ParentClass = wx.Dialog if isDialog else wx.Panel
	class FtpPublishObject( ParentClass ):

		def __init__( self, parent, id=wx.ID_ANY, uploadNowButton=True ):
			if isDialog:
				super().__init__( parent, id, _("Ftp Publish Results"),
								style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
			else:
				super().__init__( parent, id )
							
			fgs = wx.FlexGridSizer(vgap=4, hgap=4, rows=0, cols=2)
			fgs.AddGrowableCol( 1, 1 )
			
			self.useSftp = wx.CheckBox( self, label=_("Use SFTP Protocol (on port 22)") )
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
			
			self.qrcodeBitmap = wx.StaticBitmap( self, bitmap=wx.Bitmap(os.path.join(Utils.getImageFolder(), 'QRCodeIcon.png'), wx.BITMAP_TYPE_PNG) )
			self.printBtn = wx.Button( self, label = _('Print Results URL as a QR Code...') )
			self.Bind( wx.EVT_BUTTON, self.onPrint, self.printBtn )
			
			if isDialog:
				self.okBtn = wx.Button( self, wx.ID_OK )
				self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

				self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
				self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
			
			fgs.AddSpacer( 16 )
			fgs.Add( self.useSftp )
			
			fgs.Add( wx.StaticText( self, label = _("Host Name")), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
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
				self.okBtn.SetDefault()
				
				mvs = wx.BoxSizer( wx.VERTICAL )
				mvs.Add( fgs, 1, flag=wx.EXPAND|wx.ALL, border=4 )
				mvs.Add( hb, flag=wx.ALL|wx.ALIGN_CENTER, border=4 )
				self.SetSizerAndFit( mvs )
				mvs.Fit( self )
			
				self.CentreOnParent( wx.BOTH )
				wx.CallAfter( self.SetFocus )
			else:
				self.ftpTestButton = wx.Button( self, label=_('Test Connection') )
				self.ftpTestButton.Bind( wx.EVT_BUTTON, self.onFtpTest )
				if uploadNowButton:
					self.ftpUploadNowButton = wx.Button( self, label=_('Do Upload Now') )
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
			if Utils.MessageYesNo(self, "Are you sure you want to Test Now? This can take several minutes and you will not be able to do anything until complete?", "Test Upload"):
				with wx.BusyInfo('Uploading...', self):
					result = FtpTest()
				if result:
					Utils.MessageOK(self, '{}\n\n{}\n'.format(_("Ftp Test Failed"), result), _("Ftp Test Failed"), iconMask=wx.ICON_ERROR)
				else:
					Utils.MessageOK(self, _("Test Successful"), _("Test Successful"))
								

		def onFtpUploadNow( self, event ):
			self.commit()
			if Utils.MessageYesNo(self, "Are you sure you want to Upload Now? This can take several minutes and you will not be able to do anything until complete?", "Upload Now"):
				with wx.BusyInfo('Uploading...', self):
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
			pdd.EnableSelection( False )
			pdd.EnablePageNumbers( False )
			pdd.EnableHelp( False )
			pdd.EnablePrintToFile( False )
			
			printer = wx.Printer( pdd )
			printout = FtpQRCodePrintout()

			if not printer.Print(self, printout, True):
				if printer.GetLastError() == wx.PRINTER_ERROR:
					Utils.MessageOK(self, '\n\n'.join( [_("There was a printer problem."),_("Check your printer setup.")] ), _("Printer Error"), iconMask=wx.ICON_ERROR)

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
		Utils.MessageOK(parent, '{}\n\n    {}'.format(_('Error'), _('Missing host name.')), _('Upload Failed'), iconMask=wx.ICON_ERROR )
		return
	
	wx.BeginBusyCursor()
	e = FtpWriteRaceHTML()
	wx.EndBusyCursor()

	if e:
		Utils.MessageOK(parent, '{}  {}\n\n{}'.format(_('Upload Failed.'), _('Error'), e), _('Upload Failed'), iconMask=wx.ICON_ERROR )
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
					useSftp = False,
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
