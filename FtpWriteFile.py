import wx
import wx.grid				as gridlib
import wx.lib.intctrl
import wx.lib.masked		as masked
import ftplib
import os
import sys
import threading
import datetime
import Utils
from Utils				import logCall
import Model
import cStringIO as StringIO

def FtpWriteFile( host, user = 'anonymous', passwd = 'anonymous@', timeout = 30, serverPath = '.', fname = '', file = None ):
	ftp = ftplib.FTP( host, timeout = timeout )
	ftp.login( user, passwd )
	if serverPath:
		ftp.cwd( serverPath )
	if file is None:
		file = open(fname, 'rb')
	ftp.storbinary( 'STOR %s' % os.path.basename(fname), file )
	ftp.quit()

class RealTimeFtpPublish( object ):
	waitSecMin = 4
	waitSecMax = 32

	def __init__( self ):
		self.timer = None
		self.waitSec = RealTimeFtpPublish.waitSecMin
		self.tLastUpdate = datetime.datetime.now() - datetime.timedelta( seconds = 24*60*60 )

	def publish( self ):
		htmlFile = os.path.join(Utils.getHtmlFolder(), 'RaceAnimation.html')
		try:
			with open(htmlFile) as fp:
				html = fp.read()
		except:
			self.timer = None
			return
		
		html = Utils.mainWin.addResultsToHtmlStr( html )

		with Model.LockRace() as race:
			if not race or not race.isRunning() or not Utils.getFileName():
				self.timer = None
				return
			host		= getattr( race, 'ftpHost', '' )
			user		= getattr( race, 'ftpUser', '' )
			passwd		= getattr( race, 'ftpPassword', '' )
			serverPath	= getattr( race, 'ftpPath', '' )
			fname		= os.path.basename( Utils.getFileName()[:-4] + '.html' )
			file		= StringIO.StringIO( html )
			
		try:
			FtpWriteFile(	host		= host,
							user		= user,
							passwd		= passwd,
							serverPath	= serverPath,
							fname		= fname,
							file		= file )
			self.tLastUpdate = datetime.datetime.now()
		except Exception, e:
			Utils.writeLog( 'RealTimeFtpPublish: %s' % str(e) )
			
		self.timer = None

	def publishEntry( self ):
		'''
		This function attempts to publish race results in a timely manner without wasting bandwidth.
		It was inspired by TCP/IP and double-exponential backoff.
		
		When we get a new entry, we schedule an update in the future to give time for more entries to accumulate.
		The longer we wait, the more likely that more entries are going to arrive.
		However, the more latency there will be to publish the new information.
		
		The logic below attempts to balance bandwidth and latency.
		The procedure is based on waitSec, the current seconds to wait before publishing an update, and
		tLastUpdate, the last time an update was made.
		
		If the time of the last update is less than the last waitSec, we double waitSec.
		If the time of the last update exceeds the last waitSec, we reset waitSec to waitSecMin.
		
		The behavior we expect to see is that when the first riders cross the line on a lap, an update will be triggered
		4 seconds in the future.  Any lead riders arriving in those 4 seconds will be included in the update.
		
		If the entire pack goes by, we are done.
		If stragglers arrive within 4 seconds, the wait time doubles to a maximum to 8 to get more stragglers.
		In this way, the publish takes longer and longer to update the stragglers, giving them more time to arrive.
		'''
		if self.timer:
			return

		# If this publish request is less than waitSec, double waitSec for the next publish waiting interval.
		# If this publish request exceeds waitSec, reset waitSec to waitSecMin.
		if (datetime.datetime.now() - self.tLastUpdate).total_seconds() < self.waitSec:
			self.waitSec = min( RealTimeFtpPublish.waitSecMax, self.waitSec * 2 )
		else:
			self.waitSec = self.waitSecMin
		
		self.timer = threading.Timer( self.waitSec, self.publish )
		self.timer.start()

realTimeFtpPublish = RealTimeFtpPublish()
		
#------------------------------------------------------------------------------------------------
class FtpPublishDialog( wx.Dialog ):

	fields = 	['ftpHost',	'ftpPath',	'ftpUser',		'ftpPassword',	'ftpUploadDuringRace']
	defaults =	['',		'',			'anonymous',	'anonymous@',	False]

	def __init__( self, parent, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Ftp Publish Html Results",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
						
		bs = wx.GridBagSizer(vgap=0, hgap=4)
		
		self.ftpHost = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPath = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpUser = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER, value='' )
		self.ftpPassword = wx.TextCtrl( self, wx.ID_ANY, size=(256,-1), style=wx.TE_PROCESS_ENTER|wx.TE_PASSWORD, value='' )
		self.ftpUploadDuringRace = wx.CheckBox( self, wx.ID_ANY, "Automatically Upload Results During Race" )
		
		self.refresh()
		
		self.okBtn = wx.Button( self, wx.ID_ANY, '&OK' )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_ANY, '&Cancel' )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		
		row = 0
		border = 8
		bs.Add( wx.StaticText( self, wx.ID_ANY, "Ftp Host Name:"),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpHost, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, "Path on Host to Store File:"),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPath, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, "User:"),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpUser, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( wx.StaticText( self, wx.ID_ANY, "Password:"),  pos=(row,0), span=(1,1), border = border,
				flag=wx.LEFT|wx.TOP|wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
		bs.Add( self.ftpPassword, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
		row += 1
		bs.Add( self.ftpUploadDuringRace, pos=(row,1), span=(1,1), border = border, flag=wx.RIGHT|wx.TOP|wx.ALIGN_LEFT )
		
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

	def refresh( self ):
		with Model.LockRace() as race:
			if not race:
				for f, v in zip(FtpPublishDialog.fields, FtpPublishDialog.defaults):
					getattr(self, f).SetValue( v )
			else:
				for f, v in zip(FtpPublishDialog.fields, FtpPublishDialog.defaults):
					getattr(self, f).SetValue( getattr(race, f, v) )
		
	def onOK( self, event ):
		with Model.LockRace() as race:
			if not race:
				return
			for f in FtpPublishDialog.fields:
				setattr( race, f, getattr(self, f).GetValue() )
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )
