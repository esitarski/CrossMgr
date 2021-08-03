import re
import wx

def floatOrNone( v ):
	try:
		return float(v)
	except (TypeError, ValueError):
		return None

class AdvancedDialog( wx.Dialog ):
	def __init__( self, *args, **kwargs ):
		self.receive_sensitivity_table = kwargs.pop('receive_sensitivity_table')
		self.transmit_power_table = kwargs.pop('transmit_power_table')
		self.receive_dB = kwargs.pop('receive_dB')
		self.transmit_dBm = kwargs.pop('transmit_dBm')
		self.generalCapabilities = kwargs.pop('general_capabilities')
		kwargs['title'] = 'Advanced RFID Options'
		super().__init__( *args, **kwargs )
		
		fgs = wx.FlexGridSizer( 2, 3, 4, 6 )
		fgs.AddGrowableRow( 1 )
		
		fgs.Add( wx.StaticText( self, label="Reader Info" ), flag=wx.ALIGN_CENTRE )
		fgs.Add( wx.StaticText( self, label="Transmit Power" ) )
		fgs.Add( wx.StaticText( self, label="Receiver Sensitivity" ) )
		
		self.transmitPower = wx.ListCtrl( self, style=wx.LC_SINGLE_SEL|wx.LC_REPORT, size=(-1,300) )
		self.transmitPower.AppendColumn( 'dBm',  format=wx.LIST_FORMAT_RIGHT, width=64 )
		
		self.fgsGeneral = wx.FlexGridSizer( len(self.generalCapabilities), 2, 4, 4 )
		self.receiveSensitivity = wx.ListCtrl( self, style=wx.LC_SINGLE_SEL|wx.LC_REPORT )
		self.receiveSensitivity.AppendColumn( 'dB',  format=wx.LIST_FORMAT_RIGHT, width=64 )
		
		self.initialize()
		
		fgs.Add( self.fgsGeneral )
		fgs.Add( self.transmitPower, flag=wx.EXPAND )
		fgs.Add( self.receiveSensitivity, flag=wx.EXPAND )
		
		bs = wx.StdDialogButtonSizer()
		bs.AddButton( wx.Button(self, wx.ID_OK) )
		bs.AddButton( wx.Button(self, wx.ID_CANCEL) )
		bs.Realize()
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( fgs, flag=wx.EXPAND|wx.ALL, border=4 )		
		sizer.Add( bs, flag=wx.ALL, border=4 )
		
		self.SetSizerAndFit( sizer )
		
	def initialize( self ):
		self.receiveSensitivity.DeleteAllItems()
		self.receiveSensitivity.Append( ('Max',) )
		receive_dB = floatOrNone( self.receive_dB )
		iSelect = 0
		for i, v in enumerate(self.receive_sensitivity_table):
			self.receiveSensitivity.InsertItem( self.receiveSensitivity.GetItemCount(), '{:4.2f}'.format(v) )
			if v == receive_dB:
				iSelect = i
		self.receiveSensitivity.Select( iSelect )
		self.receiveSensitivity.EnsureVisible( iSelect )
			
		self.transmitPower.DeleteAllItems()
		transmit_dBm = floatOrNone( self.transmit_dBm )
		iSelect = len(self.transmit_power_table)
		for i, v in enumerate(self.transmit_power_table):
			self.transmitPower.InsertItem( self.transmitPower.GetItemCount(), '{:4.2f}'.format(v) )
			if v == transmit_dBm:
				iSelect = i
		self.transmitPower.Append( ('Max',) )
		self.transmitPower.Select( iSelect )
		self.transmitPower.EnsureVisible( iSelect )
		
		def formatAttr( s ):
			return re.sub('[A-Z]', lambda m: ' ' + m.group(0), s).replace('U T C','UTC').strip()
		for a, v in self.generalCapabilities:
			self.fgsGeneral.Add( wx.StaticText(self, label='{}:'.format(formatAttr(a))), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL )
			self.fgsGeneral.Add( wx.TextCtrl(self, value='{}'.format(v), style=wx.TE_READONLY) )

	def get( self ):
		try:
			r = self.receiveSensitivity.GetItem(self.receiveSensitivity.GetFirstSelected()).GetText()
		except ValueError:
			r = 'Max'
		try:
			t = self.transmitPower.GetItem(self.transmitPower.GetFirstSelected()).GetText()
		except ValueError:
			t = 'Max'
		return r, t

if __name__ == '__main__':
	app = wx.App( False )
	app.SetAppName( 'TagReadWrite' )
	with AdvancedDialog(
			None,
			receive_sensitivity_table=list(range(-80, -30)), receive_dB=None,
			transmit_power_table=list(range(15, 35)), transmit_dBm=None,
			general_capabilities=[('ReaderFirmwareVersion', '3.4')]) as advDlg:
		advDlg.ShowModal()
		print( advDlg.get() )
	
