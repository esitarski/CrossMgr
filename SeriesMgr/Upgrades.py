import wx
import wx.grid as gridlib
import wx.lib.agw.floatspin as FS

import os
import re
import sys
import SeriesModel
import Utils

class Upgrades(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, 'Upgrades' )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		example = wx.StaticText( self, label=(u'\n'.join( [
				u'"Category Upgrade Progression" is the sequence of Category upgrades, lowest to highest.',
				u'"Factor" is the fraction of previous points than can be carried forward from the current category',
				u'to the Upgrade category.',
				u'',
				u'For example:',
				u'Category Upgrade Progression:     Beginner (Men), Novice (Men), Intermediate (Men), Expert (Men)',
				u'Factor:        0.5',
				u'',
				u'This would specify that if a rider is upgraded from Beginner to Novice (or Novice to Intermediate,',
				u'or Intermediate to Expert), 0.5 of the total points earned in the previous category carry forward',
				u'to the new category.',
				u'',
				u'Upgrades only apply when the Scoring Criteria is by Points.  They have no effect on other scoring systems.',
				u'',
			]))
		)
		
		fgs = wx.FlexGridSizer( rows=0, cols=3, vgap=4, hgap=2 )
		fgs.AddGrowableCol( 1, proportion=1 )
		
		fgs.Add( wx.StaticText(self, label='') )
		fgs.Add( wx.StaticText(self, label=u'{}:'.format('Category Upgrade Progression')) )
		fgs.Add( wx.StaticText(self, label=u'{}:'.format('Factor')) )
		self.upgradePaths, self.upgradeFactors = [], []
		for i in range(8):
			self.upgradePaths.append( wx.TextCtrl(self) )
			self.upgradeFactors.append( FS.FloatSpin(self, min_val=0.0, max_val=1.0, increment=0.01, value=0.5, agwStyle=FS.FS_RIGHT ) )
			self.upgradeFactors[-1].SetFormat( '%f' )
			self.upgradeFactors[-1].SetDigits( 2 )
			fgs.Add( wx.StaticText(self, label=u'{}.'.format(i+1) ), flag=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE_VERTICAL )
			fgs.Add( self.upgradePaths[-1], 1, flag=wx.EXPAND )
			fgs.Add( self.upgradeFactors[-1], 0 )

		bsizer.Add( example,flag=wx.ALL, border=8 )
		bsizer.Add( fgs, 1, flag=wx.EXPAND )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		self.SetSizer(sizer)
						
	def refresh( self ):
		model = SeriesModel.model
		for row in range(len(self.upgradePaths)):
			self.upgradePaths[row].SetValue(model.upgradePaths[row] if row < len(model.upgradePaths) else u'' )			
			self.upgradeFactors[row].SetValue(model.upgradeFactors[row] if row < len(model.upgradeFactors) else 0.5 )
	
	def commit( self ):
		upgradePaths = []
		upgradeFactors = []
		for row in range(len(self.upgradePaths)):
			path = self.upgradePaths[row].GetValue().strip()
			components = [re.sub(r'\s+', u' ', p).strip() for p in path.split(u',')]
			cleanPath = u', '.join( c for c in components if c )
			if cleanPath:
				upgradePaths.append( cleanPath )
				upgradeFactors.append( self.upgradeFactors[row].GetValue() )
		
		model = SeriesModel.model
		if upgradePaths != model.upgradePaths or upgradeFactors != model.upgradeFactors:
			model.upgradePaths = upgradePaths
			model.upgradeFactors = upgradeFactors
			model.changed = True
		
########################################################################

class UpgradesFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Upgrades Test", size=(800,600) )
		self.panel = Upgrades(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = UpgradesFrame()
	frame.panel.refresh()
	app.MainLoop()
