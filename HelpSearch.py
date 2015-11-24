import Utils
import wx
import os
import sys
import cStringIO as StringIO
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import  wx.html as html
import  wx.lib.wxpTag

class HelpSearch( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY, style = 0, size=(-1-1) ):
		wx.Panel.__init__(self, parent, id, style=style, size=size )

		self.searchLabel = wx.StaticText( self, label=_('Search Text:') )
		self.search = wx.SearchCtrl( self, style=wx.TE_PROCESS_ENTER, value='main screen', size=(200,-1) )
		self.Bind( wx.EVT_TEXT_ENTER, self.doSearch, self.search )
		self.Bind( wx.EVT_TEXT, self.doSearch, self.search )
		self.Bind( wx.EVT_SEARCHCTRL_SEARCH_BTN, self.doSearch, self.search )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.searchLabel, 0, flag=wx.ALIGN_CENTRE_VERTICAL )
		hs.Add( self.search, 1, flag=wx.EXPAND|wx.LEFT, border=4 )
		
		self.vbs = wx.BoxSizer(wx.VERTICAL)
		
		self.html = html.HtmlWindow( self, size=(800,600), style=wx.BORDER_SUNKEN )
		self.Bind( wx.html.EVT_HTML_LINK_CLICKED, self.doLink, self.html )
		
		self.vbs.Add( hs, 0, flag=wx.BOTTOM|wx.EXPAND, border=4 )
		self.vbs.Add( self.html, 1, flag=wx.EXPAND )
		
		self.SetSizer(self.vbs)
		self.doSearch()

	def doLink( self, event ):
		info = event.GetLinkInfo()
		href = info.GetHref()
		Utils.showHelp( href )
		
	def doSearch( self, event = None ):
		busy = wx.BusyCursor()
		text = self.search.GetValue()
		
		f = StringIO.StringIO()
		try:
			ix = open_dir( Utils.getHelpIndexFolder(), readonly=True )
		except Exception as e:
			Utils.logException( e, sys.exc_info() )
			ix = None
			
		f.write( u'<html>\n' )
		
		if ix is not None:
			with ix.searcher() as searcher:
				query = QueryParser('content', ix.schema).parse(unicode(text))
				results = searcher.search(query, limit=20)
				
				# Allow larger fragments
				results.formatter.maxchars = 300
				# Show more context before and after
				results.formatter.surround = 50
				
				f.write( u'<table>\n' )
				for i, hit in enumerate(results):
					file = os.path.splitext(hit['path'].split('#')[0])[0]
					if not file.startswith('Menu'):
						section = u'{}: {}'.format(file, hit['section'])
					else:
						section = u'Menu: {}'.format( hit['section'] )
					f.write( u'''<tr>
							<td valign="top">
								<font size=+1><a href="{}">{}</a></font><br></br>
								{}
								<font size=+1><br></br></font>
							</td>
						</tr>\n'''.format(hit['path'], section, hit.highlights('content') ) )
				f.write( u'</table>\n' )
			ix.close()
		
		f.write( u'</html>\n' )
		
		htmlTxt = f.getvalue()
		f.close()
		self.html.SetPage( htmlTxt )
	
class HelpSearchDialog( wx.Dialog ):
	def __init__(
			self, parent, ID = wx.ID_ANY, title='Help Search', size=wx.DefaultSize, pos=wx.DefaultPosition, 
			style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER ):

		super( HelpSearchDialog, self ).__init__(parent, ID, title, pos, size, style)

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.search = HelpSearch( self, size=(600,400) )
		sizer.Add(self.search, 1, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
		
		self.SetSizer(sizer)
		sizer.Fit(self)
		
if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(600,400))
	mainWin.Show()
	searchDialog = HelpSearchDialog( mainWin, size=(600,400) )
	searchDialog.Show()
	app.MainLoop()
