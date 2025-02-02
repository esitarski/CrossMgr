import wx
import os
import re
import operator
import itertools

import Utils
import Model
from ReadSignOnSheet	import ExcelLink

def GetRiderAttributes( rider, race, externalInfo, riderAttributes ):
	info = externalInfo.get( rider.num, {} )
	category = race.getCategory( rider.num )
	attrs = {}
	for attr in riderAttributes:
		if attr == 'Name':
			attrs['Name'] = ', '.join( f for f in [info.get('LastName', ''), info.get('FirstName', '')] if f ) 
		else:
			attrs[attr] = info.get( attr, '' )
	attrs['Category'] = category.fullname if category else ''
	attrs['num'] = str(rider.num)
	return attrs

def GetResultNotesData():
	if not (race := Model.race):
		return {}
		
	resultNotes = sorted( (rider for rider in race.riders.values() if rider.resultNote), key=operator.attrgetter('num') )
	
	try:
		excelLink = race.excelLink
		externalFields = set(excelLink.getFields())
		externalInfo = excelLink.read()
	except Exception:
		excelLink = None
		externalFields = set()
		externalInfo = {}
	
	rightJustifyCols = { 0 }
	colnames = [_('Bib'),]
	riderAttributes = ['num']
	if ('FirstName' in externalFields or 'LastName' in externalFields):
		colnames.append( _('Name') )
		riderAttributes.append( 'Name' )
		
	if 'License' in externalFields:
		colnames.append( _('License') )
		riderAttributes.append( 'License' )
	
	if 'UCIID' in externalFields:
		colnames.append( _('UCIID') )
		riderAttributes.append( 'UCIID' )
	
	if 'Team' in externalFields:
		colnames.append( _('Team') )
		riderAttributes.append( 'Team' )
		
	colnames.append( _('Category') )	
	riderAttributes.append( 'Category' )
	
	return {
		'colnames':colnames,
		'riderAttributes':riderAttributes,
		'resultNotes':resultNotes,
		'rightJustifyCols':rightJustifyCols,
		'excelLink':excelLink,
		'externalFields':externalFields,
		'externalInfo':externalInfo
	}

class ResultNoteContents( wx.TextCtrl ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, editCallback=None ):
		super().__init__( parent, id, size=size, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_AUTO_URL|wx.HSCROLL|wx.BORDER_NONE )
		self.editCallback = editCallback
		self.Bind( wx.EVT_TEXT_URL, self.doURL )
		
	def doURL( self, event ):
		if event.MouseEvent.LeftUp():
			url = self.GetRange(event.GetURLStart(), event.GetURLEnd())
			# Parse the number from the fake url and call the callback.
			try:
				num = int( re.search( r'_(\d+)_', url).group(1) )
				self.editCallback( num )
			except (IndexError, TypeError):
				pass
		
		event.Skip()
		
	def update( self, rnd ):
		self.Clear()
		if not rnd:
			return
		
		race = Model.race
		colnames = rnd['colnames']
		riderAttributes = rnd['riderAttributes']
		resultNotes = rnd['resultNotes']
		externalInfo = rnd['externalInfo']
		
		regularStyle = self.GetDefaultStyle()
		titleStyle = wx.TextAttr( wx.BLACK, font=self.GetFont().Bold() )
		hiddenTextStyle = wx.TextAttr( self.GetBackgroundColour() )
		
		for rider in resultNotes:
			rna = GetRiderAttributes( rider, race, externalInfo, riderAttributes )
			attrs = [(a, rna[a]) for a in riderAttributes if rna[a]]
			for a, attr in attrs:
				last = (a == attrs[-1][0])
				if a == 'num':
					self.SetDefaultStyle( titleStyle )
					self.write( f'{attr}: ' )
				elif a == 'Name':
					self.SetDefaultStyle( titleStyle )
					self.write( attr + ('; ' if not last else '') )
				else:
					self.write( attr + ('; ' if not last else '') )
				self.SetDefaultStyle( regularStyle )

			# Write a specially-styled url to trigger the editor.
			for s, t in ((hiddenTextStyle, ' www.'), (regularStyle, _('Edit')), (hiddenTextStyle, '_' + attrs[0][1] + '_.com'), (regularStyle, '\n')):
				self.SetDefaultStyle( s )
				self.write( t )
			
			for line in rider.resultNote.split('\n'):
				self.write( f'\t{line}\n' )
				
			self.write( '\n' )
			
		self.ShowPosition( 0 )

class ResultNoteMassEditDialog( wx.Dialog ):
	Add = 0
	Replace = 1
	
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize, verb=Replace, bibs=None, note=None ):
		super().__init__( parent, id, size=size, title=_('Result Note Add') )
		
		self.verb = verb
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		description = wx.StaticText( self, label=_('Enter all bibs (comma or space separated).') )
		vsOverall.Add( description, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.bibs = wx.TextCtrl( self, value=(bibs or '').strip() )
		vsOverall.Add( self.bibs, 0, flag=wx.EXPAND|wx.ALL, border=4 )
		
		description = wx.StaticText( self, label=_('Result Note:') )
		vsOverall.Add( description, 0, flag=wx.EXPAND|wx.ALL, border=4 )

		self.resultNote = wx.TextCtrl( self, value=(note or ''), style=wx.TE_MULTILINE|wx.HSCROLL )
		vsOverall.Add( self.resultNote, 1, flag=wx.EXPAND|wx.BOTTOM|wx.LEFT|wx.RIGHT, border=4 )
		
		sdbs = self.CreateStdDialogButtonSizer( wx.OK|wx.CANCEL )
		if sdbs:
			vsOverall.Add( sdbs, flag=wx.BOTTOM|wx.LEFT|wx.RIGHT, border=4 )
			
		self.SetSizer( vsOverall )

	def apply( self ):
		if not (race := Model.race):
			return
			
		bibs = self.bibs.GetValue()
		bibs = re.sub( r'[^\d]', ' ', bibs ).strip()
		
		lines = [line.strip() for line in self.resultNote.GetValue().strip().split('\n')]
		for b in bibs.split():
			try:
				b = int( b )
			except Exception:
				continue
			
			if b not in race.riders:
				continue
			
			rider = race.riders[b]
			if self.verb == self.Add:
				resultNote = (rider.resultNote or '').strip() + '\n'
			else:
				resultNote = '\n'
			
			resultNoteLines = set( resultNote.strip().split('\n') )
			for line in lines:
				if line and line not in resultNoteLines:
					resultNote += line + '\n'
					resultNoteLines.add( line )
			
			resultNote = (resultNote.strip() or None)
			if rider.resultNote != resultNote:
				rider.resultNote = resultNote
				race.setChanged()
	
class ResultNote( wx.Panel ):
	def __init__( self, parent, id=wx.ID_ANY, size=wx.DefaultSize ):
		super().__init__( parent, id, size=(800,800) )
		
		vsOverall = wx.BoxSizer( wx.VERTICAL )
		
		buttonSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.addBtn = wx.Button( self, label=_('Add') )
		self.addBtn.Bind( wx.EVT_BUTTON, lambda e: self.doAction(verb=ResultNoteMassEditDialog.Add) )
		buttonSizer.Add( self.addBtn, flag=wx.ALL, border=4 )
		
		self.replaceBtn = wx.Button( self, label=_('Replace') )
		self.replaceBtn.Bind( wx.EVT_BUTTON, lambda e: self.doAction(verb=ResultNoteMassEditDialog.Replace) )
		buttonSizer.Add( self.replaceBtn, flag=wx.ALL, border=4 )
		
		vsOverall.Add( buttonSizer, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.resultNoteContents = ResultNoteContents( self, editCallback=self.doNumEdit )
		vsOverall.Add( self.resultNoteContents, 1, flag=wx.EXPAND|wx.ALL, border=4 )
		
		self.SetSizer( vsOverall )
	
	def doAction( self, verb, bibs=None, note=None ):
		with ResultNoteMassEditDialog(self, verb=verb, bibs=bibs, note=note, size=(800,400)) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				insertionPointSave = self.resultNoteContents.GetInsertionPoint()
				dlg.apply()
				wx.CallAfter( self.update, insertionPointSave )

	def doNumEdit( self, num ):
		race = Model.race
		if race and num in race.riders:
			self.doAction( verb=ResultNoteMassEditDialog.Replace, bibs=str(num), note=race.riders[num].resultNote )
	
	def update( self, insertionPoint=None ):
		rnd = GetResultNotesData()
		self.resultNoteContents.update( rnd )
		self.Layout()

		# Overset and backup the insertion point to show more context.
		insertionPoint = (insertionPoint or 0)
		self.resultNoteContents.SetInsertionPoint( min(insertionPoint+128, self.resultNoteContents.GetLastPosition()) )
		self.resultNoteContents.SetInsertionPoint( min(insertionPoint, self.resultNoteContents.GetLastPosition()) )
	
	def refresh( self ):
		self.update()
		
	def commit( self ):
		pass

########################################################################

class ResultNoteFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Results Note Test", size=(800,600) )
		panel = ResultNote(self)
		panel.refresh()
		self.Show()

if __name__ == '__main__':
	app = wx.App(False)
	app.SetAppName("CrossMgr")
	
	Utils.disable_stdout_buffering()
	
	race = Model.newRace()
	race._populate()
	
	fnameRiderInfo = os.path.join(os.path.expanduser('~'), 'CrossMgrSimulation', 'SimulationRiderData.xlsx')
	sheetName = 'Registration'
	
	race.excelLink = ExcelLink()
	race.excelLink.setFileName( fnameRiderInfo )
	race.excelLink.setSheetName( sheetName )
	race.excelLink.setFieldCol( {'Bib#':0, 'LastName':1, 'FirstName':2, 'Team':3} )
	
	for r in race.riders.values():
		r.resultNote = 'This is a result note.\nThis is another result note.'
		
	frame = ResultNoteFrame()
	app.MainLoop()
