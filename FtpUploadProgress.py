import wx
import os
import datetime
import Utils

class FtpUploadProgress( wx.Dialog ):
	def __init__( self, parent, id=wx.ID_ANY, fileTotal=0, bytesTotal=0 ):
		super( FtpUploadProgress, self ).__init__( parent, id, title=_('Ftp Update Progress'), style=wx.CAPTION )
		self.fileTotal = fileTotal
		self.bytesCur = 0
		self.bytesTotal = bytesTotal
		self.startTime = datetime.datetime.now()
		
		self.message = wx.StaticText( self, label=u'{}:\n\n{}/{}:  '.format(
				_('Ftp Update Progress'),
				1, self.fileTotal,
			)
		)
		self.bytesGauge = wx.Gauge( self, range=bytesTotal, size=(600,24) )
		
		border = 16
		ms = wx.BoxSizer( wx.VERTICAL )
		ms.Add( self.message, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=border )
		ms.Add( self.bytesGauge, flag=wx.ALL, border=border )
		
		self.SetSizerAndFit( ms )
		
	def update( self, bytestr, fname, i ):
		eta = u''
		tCur = (datetime.datetime.now() - self.startTime).total_seconds()
		self.bytesCur += len(bytestr)
		if self.bytesTotal:
			tEnd = tCur * float(self.bytesTotal) / float(self.bytesCur)
			eta = u'{},  {} {}'.format(Utils.formatTime(
				max(0.0, tEnd - tCur + 1.0)),
				max(0.0, self.bytesTotal - self.bytesCur) // 1000, _('KB to go'),
			)
	
		self.bytesGauge.SetValue( self.bytesCur )
		self.message.SetLabel( u'{}:  {}\n\n{} {} {}:  {}'.format(
				_('Ftp Update Progress'), eta,
				i+1, _('of'), self.fileTotal,
				os.path.basename(fname),
			)
		)
		
if __name__ == '__main__':
	app = wx.App(False)
	ftpUploadProgress = FtpUploadProgress( None, fileTotal=6, bytesTotal=500000 )
	ftpUploadProgress.Show()
	
	app.MainLoop()

