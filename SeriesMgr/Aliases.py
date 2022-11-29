import wx
from AliasGrid import AliasGrid
from AliasesName		import AliasesName
from AliasesLicense		import AliasesLicense
from AliasesMachine		import AliasesMachine
from AliasesTeam		import AliasesTeam

def normalizeText( text ):
	return ', '.join( [t.strip() for t in text.split(',')][:2] )

class Aliases(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.notebook = wx.Notebook( self )
		self.notebook.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanging )
		
		# Add all the pages to the notebook.
		self.pages = []

		def addPage( page, name ):
			self.notebook.AddPage( page, name )
			self.pages.append( page )
			
		self.attrClassName = [
			[ 'aliasesName',	AliasesName,		'Name Aliases' ],
			[ 'licenseAliases',	AliasesLicense,		'License Aliases' ],
			[ 'machineAliases',	AliasesMachine,		'Machine Aliases' ],
			[ 'teamAliases',	AliasesTeam,		'Team Aliases' ],
		]
		
		for i, (a, c, n) in enumerate(self.attrClassName):
			setattr( self, a, c(self.notebook) )
			addPage( getattr(self, a), n )
		
		self.notebook.SetSelection( 0 )
		
		sizer = wx.BoxSizer( wx.VERTICAL )
		sizer.Add( self.notebook, 1, flag=wx.EXPAND )
		self.SetSizer( sizer )
		
		wx.CallAfter( self.Refresh )
		
	def refreshCurrentPage( self ):
		self.setTitle()
		self.callPageRefresh( self.notebook.GetSelection() )

	def refresh( self ):
		self.refreshCurrentPage()

	def callPageRefresh( self, i ):
		try:
			self.pages[i].refresh()
		except (AttributeError, IndexError) as e:
			pass
		
	def commit( self ):
		self.callPageCommit( self.notebook.GetSelection() )
		self.setTitle()
		
	def callPageCommit( self, i ):
		try:
			self.pages[i].commit()
			self.setTitle()
		except (AttributeError, IndexError) as e:
			pass
		
	def onPageChanging( self, event ):
		self.callPageCommit( event.GetOldSelection() )
		self.callPageRefresh( event.GetSelection() )
		event.Skip()	# Required to properly repaint the screen.
