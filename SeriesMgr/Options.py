import wx
import wx.grid as gridlib
import wx.lib.agw.floatspin as FS

import os
import re
import sys
import SeriesModel
import Utils

class Options(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)

		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, _("Output Options") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		fgs = wx.FlexGridSizer( rows=0, cols=2, vgap=4, hgap=2 )
		fgs.AddGrowableCol( 1, proportion=1 )
		
		self.showLastToFirst = wx.CheckBox( self, label=_("Show Race Results in Last-to-First Order") )
		self.showLastToFirst.SetValue( True )
		fgs.Add( wx.StaticText(self) )
		fgs.Add( self.showLastToFirst )
		bsizer.Add( fgs, 1, flag=wx.EXPAND )
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		self.SetSizer(sizer)
						
	def refresh( self ):
		model = SeriesModel.model
		self.showLastToFirst.SetValue( model.showLastToFirst )
	
	def commit( self ):
		model = SeriesModel.model
		if model.showLastToFirst != self.showLastToFirst.GetValue():
			model.showLastToFirst = self.showLastToFirst.GetValue()
			model.changed = True
		
########################################################################

class OptionsFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		wx.Frame.__init__(self, None, title="Options Test", size=(800,600) )
		self.panel = Options(self)
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	frame = OptionsFrame()
	frame.panel.refresh()
	app.MainLoop()
