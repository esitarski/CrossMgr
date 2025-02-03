import wx
import Utils
import Model
from EditEntry import DoDNF, DoDNS, DoPull, DoDQ
from Keypad import getRiderNumsFromText, enterCodes, validKeyCodes

class BibEnter( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id, _("Bib Enter"),
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL|wx.STAY_ON_TOP )

		fontPixels = 20
		font = wx.Font((0,fontPixels), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
						
		self.numEditLabel = wx.StaticText(self, label='{}'.format(_('Bib')))
		self.numEdit = wx.TextCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER )
		self.numEdit.Bind( wx.EVT_CHAR, self.handleNumKeypress )

		for w in (self.numEditLabel, self.numEdit):
			w.SetFont( font )
		
		nes = wx.BoxSizer( wx.HORIZONTAL )
		nes.Add( self.numEditLabel, flag=wx.ALIGN_CENTRE_VERTICAL )
		nes.Add( self.numEdit, 1, flag=wx.LEFT|wx.EXPAND, border=4 )
		
		hbs = wx.GridSizer( 4, 2, 2 )
		for i, (label, actionFn) in enumerate( ((_('DN&F'),DoDNF), (_('DN&S'),DoDNS), (_('&Pull'),DoPull), (_('D&Q'),DoDQ)) ):
			btn = wx.Button( self, label=label, style=wx.BU_EXACTFIT )
			btn.SetFont( font )
			btn.Bind( wx.EVT_BUTTON, lambda event, fn = actionFn: self.doAction(fn) )
			hbs.Add( btn, flag=wx.EXPAND )
			
		mainSizer = wx.BoxSizer( wx.VERTICAL )
		mainSizer.Add( nes, flag=wx.ALL|wx.EXPAND, border=2 )
		mainSizer.Add( hbs, flag=wx.ALL, border=2 )
		self.SetSizerAndFit( mainSizer )
		
	def handleNumKeypress(self, event):
		keycode = event.GetKeyCode()
		if keycode in enterCodes:
			self.onEnterPress()
		elif keycode < 255:
			if keycode in validKeyCodes:
				event.Skip()
		else:
			event.Skip()
	
	def onEnterPress( self, event = None ):
		nums = getRiderNumsFromText( self.numEdit.GetValue() )
		if nums:
			mainWin = Utils.getMainWin()
			if mainWin is not None:
				mainWin.forecastHistory.logNum( nums )
		wx.CallAfter( self.numEdit.SetValue, '' )
	
	def doAction( self, action ):
		race = Model.race
		t = race.curRaceTime() if race and race.isRunning() else None
		success = False
		for num in getRiderNumsFromText( self.numEdit.GetValue() ):
			if action(self, num, t):
				success = True
		if success:
			self.numEdit.SetValue( '' )
			wx.CallAfter( Utils.refreshForecastHistory )

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	bibEnter = BibEnter(mainWin)
	Model.newRace()
	Model.race.enableJChipIntegration = False
	Model.race.isTimeTrial = False
	bibEnter.Show()
	app.MainLoop()
	
