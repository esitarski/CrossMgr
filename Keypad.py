import wx
import os
import datetime
import wx.lib.intctrl
import wx.lib.buttons

from collections import defaultdict

import Utils
from GetResults import GetResults
import Model
from EditEntry import DoDNF, DoDNS, DoPull, DoDQ
from InputUtils import enterCodes, validKeyCodes, clearCodes, actionCodes, getRiderNumsFromText, MakeKeypadButton

SplitterMinPos = 390
SplitterMaxPos = 530

class Keypad( wx.Panel ):
	def __init__( self, parent, controller, id = wx.ID_ANY ):
		super().__init__(parent, id)
		self.SetBackgroundColour( wx.WHITE )
		self.controller = controller
		
		fontPixels = 36
		font = wx.Font((0,fontPixels), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		dc = wx.WindowDC( self )
		dc.SetFont( font )
		wNum, hNum = dc.GetTextExtent( '999' )
		wNum += 8
		hNum += 8
		
		outsideBorder = 4

		vsizer = wx.BoxSizer( wx.VERTICAL )
		
		self.numEditHS = wx.BoxSizer( wx.HORIZONTAL )
		
		self.numEditLabel = wx.StaticText(self, label='{}'.format(_('Bib')))
		self.numEditLabel.SetFont( font )
		
		editWidth = 140
		self.numEdit = wx.TextCtrl( self, style=wx.TE_RIGHT | wx.TE_PROCESS_ENTER,
							size=(editWidth, int(fontPixels*1.2)) if 'WXMAC' in wx.Platform else (editWidth,-1) )
		self.numEdit.Bind( wx.EVT_CHAR, self.handleNumKeypress )
		self.numEdit.SetFont( font )
		
		self.numEditHS.Add( self.numEditLabel, wx.ALIGN_CENTRE | wx.ALIGN_CENTRE_VERTICAL )
		self.numEditHS.Add( self.numEdit, flag=wx.LEFT|wx.EXPAND, border = 4 )
		vsizer.Add( self.numEditHS, flag=wx.EXPAND|wx.LEFT|wx.TOP, border = outsideBorder )
		
		#------------------------------------------------------------------------------------------
		self.keypadPanel = wx.Panel( self )
		gbs = wx.GridBagSizer(4, 4)
		self.keypadPanel.SetSizer( gbs )
		
		rowCur = 0		
		numButtonStyle = 0
		self.num = []

		self.num.append( MakeKeypadButton( self.keypadPanel, label='&0', style=wx.BU_EXACTFIT, font = font) )
		self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = 0 : self.onNumPress(event, aValue) )
		gbs.Add( self.num[0], pos=(3+rowCur,0), span=(1,2), flag=wx.EXPAND )

		for i in range(9):
			self.num.append( MakeKeypadButton( self.keypadPanel, label='&{}'.format(i+1), style=numButtonStyle, size=(wNum,hNum), font = font) )
			self.num[-1].Bind( wx.EVT_BUTTON, lambda event, aValue = i+1 : self.onNumPress(event, aValue) )
			j = 8-i
			gbs.Add( self.num[-1], pos=(j//3 + rowCur, 2-j%3) )
		
		self.delBtn = MakeKeypadButton( self.keypadPanel, id=wx.ID_DELETE, label=_('&Del'), style=numButtonStyle, size=(wNum,hNum), font = font)
		self.delBtn.Bind( wx.EVT_BUTTON, self.onDelPress )
		gbs.Add( self.delBtn, pos=(3+rowCur,2) )
		rowCur += 4
	
		self.enterBtn = MakeKeypadButton( self.keypadPanel, id=0, label=_('&Enter'), style=wx.EXPAND|wx.GROW, font = font)
		gbs.Add( self.enterBtn, pos=(rowCur,0), span=(1,3), flag=wx.EXPAND )
		self.enterBtn.Bind( wx.EVT_LEFT_DOWN, self.onEnterPress )
		rowCur += 1
		
		self.showTouchScreen = False
		self.keypadPanel.Show( self.showTouchScreen )
		vsizer.Add( self.keypadPanel, flag=wx.TOP, border=4 )
			
		font = wx.Font((0,int(fontPixels*.6)), wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
		
		hbs = wx.GridSizer( 2, 2, 4, 4 )
		for label, actionFn in [(_('DN&F'),DoDNF), (_('DN&S'),DoDNS), (_('&Pull'),DoPull), (_('D&Q'),DoDQ)]:
			btn = MakeKeypadButton( self, label=label, style=wx.EXPAND|wx.GROW, font = font)
			btn.Bind( wx.EVT_BUTTON, lambda event, fn = actionFn: self.doAction(fn) )
			hbs.Add( btn, flag=wx.EXPAND )
		
		vsizer.Add( hbs, flag=wx.EXPAND|wx.TOP, border=4 )
		
		self.touchBitmap = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'touch24.png'), wx.BITMAP_TYPE_PNG )
		self.touchButton = wx.BitmapButton( self, bitmap = self.touchBitmap )
		self.touchButton.Bind( wx.EVT_BUTTON, self.onToggleTouchScreen)
		self.touchButton.SetToolTip(wx.ToolTip(_("Touch Screen Toggle")))
		
		vsizer.Add( self.touchButton, flag=wx.TOP|wx.ALIGN_CENTRE, border=12 )
		self.SetSizer( vsizer )
	
	def onToggleTouchScreen( self, event ):
		self.showTouchScreen ^= True
		self.keypadPanel.Show( self.showTouchScreen )
		self.GetSizer().Layout()
		self.GetParent().GetParent().GetParent().SetSashPosition( SplitterMaxPos if self.showTouchScreen else SplitterMinPos )
		try:
			self.GetParent().GetSizer().Layout()
		except Exception:
			pass
	
	def onNumPress( self, event, value ):
		self.numEdit.SetInsertionPointEnd()
		txt = self.numEdit.GetValue()
		txt += '{}'.format(value)
		self.numEdit.SetValue( txt )
		self.numEdit.SetInsertionPointEnd()
		
	def onDelPress( self, event ):
		txt = self.numEdit.GetValue()
		if txt is not None:
			self.numEdit.SetValue( txt[:-1] )
	
	def handleNumKeypress(self, event):
		keycode = event.GetKeyCode()
		if keycode in enterCodes:
			self.onEnterPress()
		elif keycode in clearCodes:
			self.numEdit.SetValue( '' )
		elif keycode in actionCodes:
			if   keycode == ord('/'):	# DNF
				pass	
			elif keycode == ord('*'):	# DNS
				pass
			elif keycode == ord('-'):	# PUL
				pass
			elif keycode == ord('+'):	# DQ
				pass
		elif keycode < 255:
			if keycode in validKeyCodes:
				event.Skip()
			else:
				Utils.writeLog( 'handleNumKeypress: ignoring keycode < 255: {}'.format(keycode) )
		else:
			Utils.writeLog( 'handleNumKeypress: ignoring keycode: >= 255 {}'.format(keycode) )
			event.Skip()
	
	def onEnterPress( self, event = None ):
		nums = getRiderNumsFromText( self.numEdit.GetValue() )
		if nums:
			mainWin = Utils.getMainWin()
			if mainWin is not None:
				mainWin.forecastHistory.logNum( nums )
		self.controller.refreshLaps()
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
	
	def Enable( self, enable ):
		wx.Panel.Enable( self, enable )
		
def getLapInfo( lap, lapsTotal, tCur, tNext, leader ):
	race = Model.race
	if not race or not race.startTime:
		return
	info = []
	startTime = race.startTime
	
	if lap > lapsTotal:
		info.append( (_("Last Rider"), (startTime + datetime.timedelta(seconds=tNext)).strftime('%H:%M:%S')) )
		return info	
	
	tLap = tNext - tCur
	info.append( (_("Lap"), '{}/{} ({} {})'.format(lap,lapsTotal,lapsTotal-lap, _('to go'))) )
	info.append( (_("Time"), Utils.formatTimeGap(tLap, highPrecision=False)) )
	info.append( (_("Start"), (startTime + datetime.timedelta(seconds=tCur)).strftime('%H:%M:%S')) )
	info.append( (_("End"), (startTime + datetime.timedelta(seconds=tNext)).strftime('%H:%M:%S')) )
	lapDistance = None
	try:
		bib = int(leader.split()[-1])
		category = race.getCategory( bib )
		lapDistance = category.getLapDistance( lap )
	except Exception:
		pass
	if lapDistance is not None:
		sLap = (lapDistance / tLap) * 60.0*60.0
		info.append( ('', '{:.02f} {}'.format(sLap, 'km/h')) )
	return info

def getCategoryStats():
	race = Model.race
	if not race:
		return []
	
	isRunning = race.isRunning()
	isTimeTrial = race.isTimeTrial
	lastRaceTime = race.lastRaceTime()
	Finisher = Model.Rider.Finisher
	DNS = Model.Rider.DNS
	NP = Model.Rider.NP
	
	statusSortSeq = Model.Rider.statusSortSeq
	statusNames = Model.Rider.statusNames

	finishedAll, onCourseAll, statsAll = 0, 0, defaultdict( int )
	
	def getStatsStr( finished, onCourse, stats ):
		total = finished + onCourse + sum( stats.values() )
		if total:
			b = [f'{_("Starters")}({total})']
			if finished:
				b.append( f'{_("Finished")}({finished})' )
			b.extend( f'{statusNames[k]}({v})' for k,v in sorted(stats.items(), key = lambda x: statusSortSeq[x[0]]) )
			return f'{_("OnCourse")}({onCourse}) = {" - ".join(b)}'
		else:
			return ''

	categoryStats = [(_('All'), '')]
	for category in race.getCategories():
		finished, onCourse, stats = 0, 0, defaultdict( int )
		for rr in GetResults( category ):
			status = rr.status
			if status == DNS:
				continue
			
			rider = race.riders[rr.num]
			firstTime = rider.firstTime or 0.0
			if isTimeTrial:
				if status == NP and lastRaceTime >= firstTime:
					status = Finisher		# Consider started riders as Finishers, not NP.
			else:
				if status == Finisher:
					status = rider.status	# Set status back to the original status (will set back to Pulled).
				
			if status == Finisher:
				if rr.raceTimes:
					lastTime, interp = rr.raceTimes[-1], rr.interp[-1]
					if isTimeTrial:
						# Adjust to the time trial start time.
						lastTime += firstTime
				else:
					lastTime, interp = 0.0, True
				
				if lastTime <= lastRaceTime and (not interp if isRunning else True):
					finished += 1
				else:
					onCourse += 1
			else:
				stats[status] += 1
				
		statsStr  = getStatsStr(finished, onCourse, stats)
		if statsStr:
			categoryStats.append( (f'{category.fullname}', statsStr) )
			
		finishedAll += finished
		onCourseAll += onCourse
		for k, v in stats.items():
			statsAll[k] += v
	
	categoryStats[0] = ( _('All'), getStatsStr(finishedAll, onCourseAll, statsAll) )
	return categoryStats

