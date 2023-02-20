import wx
import wx.lib.intctrl
import os
import sys
import ftplib
import paramiko
import datetime
import threading
import webbrowser
import Utils
import SeriesModel

import inspect
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

class CallCloseOnExit:
	def __init__(self, obj):
		self.obj = obj
	def __enter__(self):
		return self.obj
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.obj.close()
        
class FtpWithPort(ftplib.FTP):
	def __init__(self, host, user, passwd, port, timeout):
		#Act like ftplib.FTP's constructor but connect to another port.
		ftplib.FTP.__init__(self)
		#self.set_debuglevel(2)
		self.connect(host, port, timeout)
		self.login(user, passwd)

class FtpsWithPort(ftplib.FTP_TLS):
	def __init__(self, host, user, passwd, port, timeout):
		ftplib.FTP_TLS.__init__(self)
		#self.set_debuglevel(2)
		self.connect(host, port, timeout)
		self.auth()
		self.login(user, passwd)
		#Switch to secure data connection.
		self.prot_p()
		
	def ntransfercmd(self, cmd, rest=None):
		conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
		if self._prot_p:
			conn = self.context.wrap_socket(conn,
											server_hostname=self.host,
											session=self.sock.session)  # reuse ssl session
		return conn, size

def FtpWriteFile( host, port, user = 'anonymous', passwd = 'anonymous@', timeout = 30, serverPath = '.', fileName = '', file = None, protocol='FTP'):
	if protocol == 'SFTP':
		with CallCloseOnExit(paramiko.SSHClient()) as ssh:
			ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
			ssh.load_system_host_keys()                  
			ssh.connect( host, port, user, passwd )

			with CallCloseOnExit(ssh.open_sftp()) as sftp:
				fileOpened = False
				if file is None:
					file = open(fileName, 'rb')
					fileOpened = True
				sftp.putfo(
					file,
					serverPath + os.path.basename(fileName)
				)
				if fileOpened:
					file.close()
	elif protocol == 'FTPS':
		ftps = FtpsWithPort( host, user, passwd, port, timeout)
		if serverPath and serverPath != '.':
			ftps.cwd( serverPath )
		fileOpened = False
		if file is None:
			file = open(fileName, 'rb')
			fileOpened = True
		ftps.storbinary( 'STOR {}'.format(os.path.basename(fileName)), file )
		ftps.quit()
		if fileOpened:
			file.close()
	else:  #default to unencrypted FTP
		ftp = FtpWithPort( host, user, passwd, port, timeout)
		if serverPath and serverPath != '.':
			ftp.cwd( serverPath )
		fileOpened = False
		if file is None:
			file = open(fileName, 'rb')
			fileOpened = True
		ftp.storbinary( 'STOR {}'.format(os.path.basename(fileName)), file )
		ftp.quit()
		if fileOpened:
			file.close()

def FtpWriteHtml( html_in, team = False ):
	Utils.writeLog( 'FtpWriteHtml: called.' )
	modelFileName = Utils.getFileName() if Utils.getFileName() else 'Test.smn'
	fileName		= os.path.basename( os.path.splitext(modelFileName)[0] + ('-Team.html' if team else '.html') )
	defaultPath = os.path.dirname( modelFileName )
	with open(os.path.join(defaultPath, fileName), 'w') as fp:
		fp.write( html_in )
		
	model = SeriesModel.model
	host		= getattr( model, 'ftpHost', '' )
	port		= getattr( model, 'ftpPort', 21 )
	user		= getattr( model, 'ftpUser', '' )
	passwd		= getattr( model, 'ftpPassword', '' )
	serverPath	= getattr( model, 'ftpPath', '' )
	protocol	= getattr( model, 'ftpProtocol', 'FTP' )
	
	with open( os.path.join(defaultPath, fileName), 'rb') as file:
		try:
			FtpWriteFile(	host		= host,
							port		= port,
							user		= user,
							passwd		= passwd,
							serverPath	= serverPath,
							fileName	= fileName,
							file		= file,
							protocol 	= protocol)
		except Exception as e:
			Utils.writeLog( 'FtpWriteHtml Error: {}'.format(e) )
			return e
		
	return None

#------------------------------------------------------------------------------------------------
class FtpPublishDialog( wx.Dialog ):

	fields = 	['ftpHost',	'ftpPort',	'ftpPath',	'ftpUser',		'ftpPassword',	'urlPath']
	defaults =	['',	21,		'',			'anonymous',	'anonymous@',	'http://']
	team = False

	def __init__( self, parent, html, team = False, id = wx.ID_ANY ):
		super().__init__( parent, id, "(S)FTP Publish Results",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.html = html
		self.team = team
		self.protocol = 'FTP'
		
		bs = wx.GridBagSizer(vgap=0, hgap=4)
		
		self.useFtp = wx.RadioButton( self, label=_("FTP (unencrypted)"), style = wx.RB_GROUP )
		self.useFtps = wx.RadioButton( self, label=_("FTPS (FTP with TLS)") )
		self.useSftp = wx.RadioButton( self, label=_("SFTP (SSH file transfer)") )
		self.Bind( wx.EVT_RADIOBUTTON,self.onSelectProtocol ) 
		self.ftpHost = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPort = wx.lib.intctrl.IntCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER )
		self.ftpPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpUser = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPassword = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER|wx.TE_PASSWORD, value='' )
		self.urlPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.urlPath.Bind( wx.EVT_TEXT, self.urlPathChanged )
		self.urlFull = wx.StaticText( self )
		
		self.refresh()
		
		row = 0
		border = 8
		
		bs.Add( wx.StaticText( self, label=_("Protocol:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.useFtp, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		
		bs.Add( self.useFtps, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		
		bs.Add( self.useSftp, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		
		bs.Add( wx.StaticText( self, label=_("Host Name:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpHost, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		
		row += 1
		
		bs.Add( wx.StaticText( self, label=_("Port:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPort, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, label=_("Path on Host to Write HTML:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, label=_("User:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpUser, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, label=_("Password:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPassword, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		row += 1
		bs.Add( wx.StaticText( self, label=_("URL Path (optional):")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.urlPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		row += 1
		bs.Add( wx.StaticText( self, label=_("Series Results URL:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.urlFull, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onOK, id=wx.ID_OK )
		if btnSizer:
			row += 1
			bs.Add( btnSizer, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

	def onSelectProtocol( self, event ):
		if self.useSftp.GetValue():
			self.protocol = 'SFTP'
			self.ftpPort.SetValue(22)
		elif self.useFtps.GetValue():
			self.protocol = 'FTPS'
			self.ftpPort.SetValue(21)
		else:
			self.protocol = 'FTP'
			self.ftpPort.SetValue(21)

	def urlPathChanged( self, event = None ):
		url = self.urlPath.GetValue()
		fileName = Utils.getFileName()
		if not url or url == 'http://' or not SeriesModel.model or not fileName:
			self.urlFull.SetLabel( '' )
		else:
			if not url.endswith( '/' ):
				url += '/'
			fileName = os.path.basename( os.path.splitext(fileName)[0] + ( '-Team.html' if self.team else '.html') )
			url += fileName
			self.urlFull.SetLabel( url )
		
	def refresh( self ):
		model = SeriesModel.model
		if not model:
			for f, v in zip(FtpPublishDialog.fields, FtpPublishDialog.defaults):
				getattr(self, f).SetValue( v )
		else:
			for f, v in zip(FtpPublishDialog.fields, FtpPublishDialog.defaults):
				getattr(self, f).SetValue( getattr(model, f, v) )
			self.protocol = getattr(model, 'ftpProtocol', '')
		self.urlPathChanged()
	
	def setModelAttr( self ):
		self.urlPathChanged()
		model = SeriesModel.model
		for f in FtpPublishDialog.fields:
			value = getattr(self, f).GetValue()
			if getattr( model, f, None ) != value:
				setattr( model, f, value )
				model.setChanged()
		if getattr( model, 'ftpProtocol', None ) != self.protocol:
			setattr( model, 'ftpProtocol', self.protocol)
			model.setChanged()
		model.urlFull = self.urlFull.GetLabel()
	
	def onOK( self, event ):
		self.setModelAttr()
		e = FtpWriteHtml( self.html, self.team )
		if e:
			Utils.MessageOK( self, 'FTP Publish: {}'.format(e), 'FTP Publish Error' )
		else:
			# Automatically open the browser on the published file for testing.
			model = SeriesModel.model
			if model.urlFull and model.urlFull != 'http://':
				webbrowser.open( model.urlFull, new = 0, autoraise = True )
				
		self.EndModal( wx.ID_OK )
		
if __name__ == '__main__':
	'''
	file = StringIO.StringIO( 'This is a test' )
	FtpWriteFile(	host = 'ftp://127.0.0.1:55555',
					user = 'crossmgr',
					passwd = 'crossmgr',
					timeout = 30,
					serverPath = '',
					fileName = 'test.html',
					file = None )
	sys.exit()
	'''

	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMgr", size=(600,400))
	ftpPublishDialog = FtpPublishDialog(mainWin, 'TestHtml')
	ftpPublishDialog.ShowModal()
	mainWin.Show()
	app.MainLoop()
