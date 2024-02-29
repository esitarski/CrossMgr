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
		sizer = wx.BoxSizer(wx.VERTICAL)

		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, _("Output Options") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.showLastToFirst = wx.CheckBox( self, label=_("Show Race Results in Last-to-First Order") )
		self.showLastToFirst.SetValue( True )
		bsizer.Add( self.showLastToFirst, 1, flag=wx.EXPAND )
		
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		#--------------------------------------------------------------------------
		box = wx.StaticBox( self, -1, _("Input Options") )
		bsizer = wx.StaticBoxSizer( box, wx.VERTICAL )
		
		self.riderKey = wx.Choice( self, choices=[
				_("Use First and Last Name to match participants"),
				_("Use UCI ID to match participants"),
				_("Use License to match participants"),
			]
		)
		self.riderKey.SetSelection( SeriesModel.SeriesModel.KeyByName )
		bsizer.Add( self.riderKey )
		bsizer.Add( wx.StaticText(self, label='''
The CrossMgr or Spreadsheet results must include the fields you are using to match.
If you have missing UCI ID or License fields, the safest option is to match
using First and Last Name.'''
		))
		
		sizer.Add(bsizer, 0, flag=wx.EXPAND|wx.ALL, border = 4 )
		
		#--------------------------------------------------------------------------
		
		self.SetSizer(sizer)
						
	def refresh( self ):
		model = SeriesModel.model
		self.showLastToFirst.SetValue( model.showLastToFirst )
		self.riderKey.SetSelection( model.uciIdKey )
	
	def commit( self ):
		model = SeriesModel.model
		if model.showLastToFirst != self.showLastToFirst.GetValue():
			model.showLastToFirst = self.showLastToFirst.GetValue()
			model.changed = True
		if model.riderKey != self.uciIdKey.GetSelection():
			model.riderKey = self.uciIdKey.GetSelection()
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
