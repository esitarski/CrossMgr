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

def FtpWriteFile( host, user = 'anonymous', passwd = 'anonymous@', timeout = 30, serverPath = '.', fileName = '', file = None, useSftp = False, sftpPort = 22):
	if useSftp:
		with CallCloseOnExit(paramiko.SSHClient()) as ssh:
			ssh.set_missing_host_key_policy( paramiko.AutoAddPolicy() )
			ssh.load_system_host_keys()                  
			ssh.connect( host, sftpPort, user, passwd )

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
	else:
		ftp = ftplib.FTP( host, timeout = timeout )
		ftp.login( user, passwd )
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
	user		= getattr( model, 'ftpUser', '' )
	passwd		= getattr( model, 'ftpPassword', '' )
	serverPath	= getattr( model, 'ftpPath', '' )
	useSftp		= getattr( model, 'useSftp', False )
	
	with open( os.path.join(defaultPath, fileName), 'rb') as file:
		try:
			FtpWriteFile(	host		= host,
							user		= user,
							passwd		= passwd,
							serverPath	= serverPath,
							fileName	= fileName,
							file		= file,
							useSftp 	= useSftp)
		except Exception as e:
			Utils.writeLog( 'FtpWriteHtml Error: {}'.format(e) )
			return e
		
	return None

#------------------------------------------------------------------------------------------------
class FtpPublishDialog( wx.Dialog ):

	fields = 	['ftpHost',	'ftpPath',	'ftpUser',		'ftpPassword',	'urlPath', 'useSftp']
	defaults =	['',		'',			'anonymous',	'anonymous@',	'http://', False]
	team = False

	def __init__( self, parent, html, team = False, id = wx.ID_ANY ):
		super().__init__( parent, id, "Ftp Publish Results",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.html = html
		self.team = team
		bs = wx.GridBagSizer(vgap=0, hgap=4)
		
		self.useSftp = wx.CheckBox( self, label=_("Use SFTP Protocol (on port 22)") )
		self.ftpHost = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpUser = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPassword = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER|wx.TE_PASSWORD, value='' )
		self.urlPath = wx.TextCtrl( self, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.urlPath.Bind( wx.EVT_TEXT, self.urlPathChanged )
		self.urlFull = wx.StaticText( self )
		
		self.refresh()
		
		
		
		row = 0
		border = 8
		
		bs.Add( self.useSftp, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		
		bs.Add( wx.StaticText( self, label=_("Ftp Host Name:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpHost, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
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
		self.urlPathChanged()
	
	def setModelAttr( self ):
		self.urlPathChanged()
		model = SeriesModel.model
		for f in FtpPublishDialog.fields:
			value = getattr(self, f).GetValue()
			if getattr(model, f, None) != value:
				setattr( model, f, value )
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
