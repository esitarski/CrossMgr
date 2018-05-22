import wx
import wx.lib.intctrl
import io
import os
import sys
import ftplib
import datetime
import threading
import webbrowser
import Utils
import SeriesModel

import inspect
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno
	
def FtpWriteFile( host, user = 'anonymous', passwd = 'anonymous@', timeout = 30, serverPath = '.', fileName = '', file = None ):
	ftp = ftplib.FTP( host, timeout = timeout )
	ftp.login( user, passwd )
	if serverPath and serverPath != '.':
		ftp.cwd( serverPath )
	fileOpened = False
	if file is None:
		file = open(fileName, 'rb')
		fileOpened = True
	ftp.storbinary( 'STOR %s' % os.path.basename(fileName), file )
	ftp.quit()
	if fileOpened:
		file.close()

def FtpWriteHtml( html ):
	Utils.writeLog( 'FtpWriteHtml: called.' )
	modelFileName = Utils.getFileName() if Utils.getFileName() else 'Test.smn'
	fileName		= os.path.basename( os.path.splitext(modelFileName)[0] + '.html' )
	defaultPath = os.path.dirname( modelFileName )
	with io.open(os.path.join(defaultPath, fileName), 'w', encoding='utf-8') as fp:
		fp.write( html )
		
	model = SeriesModel.model
	host		= getattr( model, 'ftpHost', '' )
	user		= getattr( model, 'ftpUser', '' )
	passwd		= getattr( model, 'ftpPassword', '' )
	serverPath	= getattr( model, 'ftpPath', '' )
	
	file		= open( os.path.join(defaultPath, fileName), 'rb' )
	try:
		FtpWriteFile(	host		= host,
						user		= user,
						passwd		= passwd,
						serverPath	= serverPath,
						fileName	= fileName,
						file		= file )
	except Exception as e:
		Utils.writeLog( 'FtpWriteHtml Error: {}'.format(e) )
		return e
		
	return None

#------------------------------------------------------------------------------------------------
class FtpPublishDialog( wx.Dialog ):

	fields = 	['ftpHost',	'ftpPath',	'ftpUser',		'ftpPassword',	'urlPath']
	defaults =	['',		'',			'anonymous',	'anonymous@'	'http://']

	def __init__( self, parent, html, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Ftp Publish Results",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
						
		self.html = html
		bs = wx.GridBagSizer(vgap=0, hgap=4)
		
		self.ftpHost = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPath = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpUser = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPassword = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER|wx.TE_PASSWORD, value='' )
		self.urlPath = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.urlPath.Bind( wx.EVT_TEXT, self.urlPathChanged )
		self.urlFull = wx.StaticText( self, wx.ID_ANY )
		
		self.refresh()
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		row = 0
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, _("Ftp Host Name:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpHost, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, _("Path on Host to Write HTML:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, _("User:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpUser, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, _("Password:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPassword, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, _("URL Path (optional):")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.urlPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, _("Series Results URL:")),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.urlFull, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		hb = wx.BoxSizer( wx.HORIZONTAL )
		hb.Add( self.okBtn, border = border, flag=wx.ALL )
		hb.Add( self.cancelBtn, border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		
		bs.Add( hb, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL|wx.ALIGN_RIGHT )
		
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
			fileName = os.path.basename( os.path.splitext(fileName)[0] + '.html' )
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
		e = FtpWriteHtml( self.html )
		if e:
			Utils.MessageOK( self, u'FTP Publish: {}'.format(e), u'FTP Publish Error' )
		else:
			# Automatically open the browser on the published file for testing.
			model = SeriesModel.model
			if model.urlFull and model.urlFull != 'http://':
				webbrowser.open( model.urlFull, new = 0, autoraise = True )
				
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
					fileName = 'test.html',
					file = None )
	sys.exit()
	'''

	app = wx.PySimpleApp()
	mainWin = wx.Frame(None,title="CrossMgr", size=(600,400))
	ftpPublishDialog = FtpPublishDialog(mainWin)
	ftpPublishDialog.ShowModal()
	mainWin.Show()
	app.MainLoop()
