import wx
import Utils
import Model
from FieldDef import FieldDef
from Competitions import SetDefaultData, getCompetitions, DoRandomSimulation
from ReorderableGrid import ReorderableGrid
from GraphDraw import Graph
from Events import GetFont, GetBoldFont
from Clock import Clock

class Properties(wx.Panel):

	def __init__(self, parent):
		super().__init__(parent)
		self.SetBackgroundColour( wx.WHITE )
		
		model = Model.model
		
		self.competitionFormat = 0
		competitionChoices = ['{}. {} ({} Starters)'.format(i+1, c.name, c.starters) for i, c in enumerate(getCompetitions())]
		modifierChoices = [' - ', '1/4 Finals are Best of 1', '1/4 & 1/2 Finals are Best of 1', 'All Finals are Best of 1']
		
		font = GetFont()
		
		self.modelFields = [
			FieldDef(attr = a, data = getattr(model, a))
			for a in ('competition_name', 'date', 'track', 'organizer', 'category', 'chief_official')
		]
		self.competitionField = FieldDef(attr = 'competitionFormat', choices = competitionChoices)
		self.modifierField = FieldDef(attr = 'competitionModifier', choices = modifierChoices)
 
		self.sampleLabel = wx.StaticText( self, label=_('Sample Competition:') )
		self.sampleLabel.SetFont( GetBoldFont() )
		
		self.graph = Graph( self )
		#self.SetToolTip( wx.ToolTip(_("Sample competition in this Competition Format.")) )
 
		fs = wx.FlexGridSizer( cols=2, vgap=4, hgap=4 )
		for f in self.modelFields:
			label, ctrl = f.makeCtrls( self )
			label.SetFont( font )
			ctrl.SetFont( font )
			fs.Add( label, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL )
			fs.Add( ctrl, flag=wx.EXPAND )
			
		label, ctrl = self.competitionField.makeCtrls( self )
		label.SetFont( font )
		ctrl.SetFont( font )
		fs.Add( label, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL )
		fs.Add( ctrl, flag=wx.EXPAND )
		ctrl.SetBackgroundColour( wx.WHITE )
		self.competitionFormatCtrl = ctrl
		self.competitionFormatCtrl.Bind( wx.EVT_CHOICE, self.updateGraph )
		
		label, ctrl = self.modifierField.makeCtrls( self )
		label.SetFont( font )
		ctrl.SetFont( font )
		fs.Add( label, flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL )
		fs.Add( ctrl, flag=wx.EXPAND )
		ctrl.SetBackgroundColour( wx.WHITE )
		self.modifierCtrl = ctrl
		self.modifierCtrl.Bind( wx.EVT_CHOICE, self.updateGraph )
		
		fs.AddGrowableCol( 1, 1 )
		
		self.clock = Clock( self, size=(200,200) )
		self.clock.SetBackgroundColour( wx.WHITE )
		
		hSizer = wx.BoxSizer( wx.HORIZONTAL )
		hSizer.Add( fs, 0, flag=wx.ALL, border = 8 )
		hSizer.AddStretchSpacer()
		hSizer.Add( self.clock, 0, flag=wx.ALL, border = 8 )
		hSizer.AddStretchSpacer()
		
		borderSizer = wx.BoxSizer( wx.VERTICAL )
		borderSizer.Add( hSizer, flag=wx.EXPAND )
		borderSizer.Add( self.sampleLabel, flag=wx.TOP|wx.LEFT|wx.RIGHT, border = 8 )
		borderSizer.Add( self.graph, 1, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border = 8 )
		self.SetSizer( borderSizer )
	
	def getGrid( self ):
		headerNames = ['', '']
		
		grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		grid.DisableDragRowSize()
		grid.SetRowLabelSize( 0 )
		grid.EnableReorderRows( False )
		grid.CreateGrid( len(self.modelFields) + 2, len(headerNames) )
		for col, h in enumerate(headerNames):
			grid.SetColLabelValue( col, h )
		grid.Show( False )
		
		for row, fd in enumerate(self.modelFields):
			grid.SetCellValue( row, 0, fd.name )
			grid.SetCellAlignment( row, 0, wx.ALIGN_RIGHT, wx.ALIGN_BOTTOM )
			grid.SetCellValue( row, 1, fd.getText() )

		row = len(self.modelFields)
		grid.SetCellValue( row, 0, _('Competition Format') )
		grid.SetCellAlignment( row, 0, wx.ALIGN_RIGHT, wx.ALIGN_BOTTOM )
		grid.SetCellValue( row, 1, self.competitionFormatCtrl.GetStringSelection().split( '.', 1 )[1].strip() )

		row += 1
		grid.SetCellValue( row, 0, _('Modifiers') )
		grid.SetCellAlignment( row, 0, wx.ALIGN_RIGHT, wx.ALIGN_BOTTOM )
		grid.SetCellValue( row, 1, self.modifierCtrl.GetStringSelection() )

		return grid
		
	def updateGraph( self, event = None ):
		competition = getCompetitions()[self.competitionFormatCtrl.GetSelection()]
		modifier = self.modifierCtrl.GetSelection()
		self.graph.model = model = SetDefaultData( competition.name, modifier=modifier, random=True )
		for f in self.modelFields:
			f.commit( model )
		
		c = "\u25AF"
		for rr in model.riders:
			rr.first_name = c * len(rr.first_name)
			rr.last_name = c * len(rr.last_name)
			rr.team = c * len(rr.team)
		
		DoRandomSimulation( model )
		self.graph.Refresh()
	
	def refresh( self ):
		model = Model.model
			
		for f in self.modelFields:
			f.refresh( model )
		
		try:
			self.competitionFormatCtrl.SetSelection( next(i for i, c in enumerate(getCompetitions()) if c.name == model.competition.name) )
		except StopIteration:
			self.competitionFormatCtrl.SetSelection( 0 )

		self.modifierCtrl.SetSelection( model.modifier )
		self.updateGraph()

	def commit( self ):
		model = Model.model
					
		for f in self.modelFields:
			model.changed |= f.commit( model )
			
		competition = getCompetitions()[self.competitionFormatCtrl.GetSelection()]
		modifier = self.modifierCtrl.GetSelection()
		
		if competition.name != model.competition.name or modifier != model.modifier:
			# Check if changing the competition format will screw anything up.
			if model.canReassignStarters():
				model.setCompetition( competition, modifier )
				model.setQualifyingInfo()
				Utils.getMainWin().resetEvents()
			else:
				Utils.MessageOK( self, 'Cannot Change Competition Format after Event has Started', 'Cannot Change Competion Format' )
		
########################################################################

class PropertiesFrame(wx.Frame):
	""""""
 
	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		super().__init__( None, title="Properties Test", size=(800,600) )
		panel = Properties(self)
		panel.refresh()
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	Model.model = SetDefaultData()
	
	with open('competitions.csv', 'w') as f:
		for i, competition in enumerate(getCompetitions()):
			f.write( '{},{},{}\n'.format(i+1, competition.name, competition.starters) )
	
	frame = PropertiesFrame()
	app.MainLoop()
