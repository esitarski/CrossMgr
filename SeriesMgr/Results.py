import wx
import wx.grid as gridlib

import os
import io
import cgi
import urllib
import sys
import base64
import StringIO

import Utils
import SeriesModel
import GetModelInfo
from ReorderableGrid import ReorderableGrid
from FitSheetWrapper import FitSheetWrapper
import FtpWriteFile

import xlwt
import re
import webbrowser
from contextlib import contextmanager

HeaderNames = ['Pos', 'Last Name', 'First Name', 'License', 'Points']

@contextmanager
def tag( buf, name, attrs = {} ):
	if isinstance(attrs, str) and attrs:
		attrs = { 'class': attrs }
	buf.write( '<%s>' % ' '.join(
			[name] + ['%s="%s"' % (attr, value) for attr, value in attrs.iteritems()]
		) )
	yield
	buf.write( '</%s>\n' % name )
	
#----------------------------------------------------------------------------------

def getHeaderGraphic():
	return os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png')

def getHtmlFileName():
	modelFileName = Utils.getFileName() if Utils.getFileName() else 'Test.smn'
	fileName		= os.path.basename( os.path.splitext(modelFileName)[0] + '.html' )
	defaultPath = os.path.dirname( modelFileName )
	return os.path.join( defaultPath, fileName )
	
def getHtml():
	model = SeriesModel.model
	raceResults = model.extractAllRaceResults()
	
	categoryNames = sorted( set(rr.categoryName for rr in raceResults) )
	if not categoryNames:
		return ''
		
	pointsForRank = { r.getFileName(): r.pointStructure for r in model.races }
	
	title = os.path.basename( os.path.splitext(Utils.mainWin.fileName)[0] ) if Utils.mainWin and Utils.mainWin.fileName else 'Series Results'
	
	pointsStructures = {}
	pointsStructuresList = []
	for race in model.races:
		if race.pointStructure not in pointsStructures:
			pointsStructures[race.pointStructure] = []
			pointsStructuresList.append( race.pointStructure )
		pointsStructures[race.pointStructure].append( race )
	
	html = StringIO.StringIO()
	
	with tag(html, 'html'):
		with tag(html, 'head'):
			with tag(html, 'title'):
				html.write( title.replace('\n', ' ') )
			with tag(html, 'meta', dict(charset="UTF-8", author="Edward Sitarski", copyright="Edward Sitarski, 2013", generator="SeriesMgr")):
				pass
			with tag(html, 'style', dict( type="text/css")):
				html.write( '''
body{ font-family: sans-serif; }

#idRaceName {
	font-size: 200%;
	font-weight: bold;
}
#idImgHeader { box-shadow: 4px 4px 4px #888888; }
.smallfont { font-size: 80%; }
.bigfont { font-size: 120%; }
.hidden { display: none; }

table.results
{
	font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
	border-collapse:collapse;
}
table.results td, table.results th 
{
	font-size:1em;
	padding:3px 7px 2px 7px;
	text-align: left;
}
table.results th 
{
	font-size:1.1em;
	text-align:left;
	padding-top:5px;
	padding-bottom:4px;
	background-color:#7FE57F;
	color:#000000;
}
table.results tr.odd
{
	color:#000000;
	background-color:#EAF2D3;
}

smallFont {
	font-size: 75%;
}

table.results td.leftBorder, table.results th.leftBorder
{
	border-left:1px solid #98bf21;
}

table.results tr:hover
{
	color:#000000;
	background-color:#FFFFCC;
}
table.results tr.odd:hover
{
	color:#000000;
	background-color:#FFFFCC;
}

table.results td.colSelect
{
	color:#000000;
	background-color:#FFFFCC;
}}

table.results td {
	border-top:1px solid #98bf21;
}

table.results td.noborder {
	border-top:0px solid #98bf21;
}

table.results td.rightAlign, table.results th.rightAlign {
	text-align:right;
}

table.results td.leftAlign, table.results th.leftAlign {
	text-align:left;
}

table.results td.topAlign, table.results th.topAlign {
	text-align:top;
}

table.results td.centerAlign, table.results th.centerAlign {
	text-align:center;
}

@media print { .noprint { display: none; } }
''')

			with tag(html, 'script', dict( type="text/javascript")):
				html.write( '''
function parsePoints( s ) {
	var i = s.indexOf( ' ' );
	if( i < 0 )
		return 0;
	else
		return parseInt( s.substring(0, i) );
}

function removeClass( classStr, oldClass ) {
	var classes = classStr.split( ' ' );
	var ret = [];
	for( var i = 0; i < classes.length; ++i ) {
		if( classes[i] != oldClass )
			ret.push( classes[i] );
	}
	return ret.join(' ');
}

function addClass( classStr, newClass ) {
	return removeClass( classStr, newClass ) + ' ' + newClass;
}

function sortTable( table, col, reverse ) {
	var tb = table.tBodies[0];
	var tr = Array.prototype.slice.call(tb.rows, 0);
	
	var cmpPos = function( a, b ) {
		var x = parseInt( a.cells[0].textContent.trim() );
		var y = parseInt( b.cells[0].textContent.trim() );
		return x - y;
	};
	var MakeCmpStable = function( a, b, res ) {
		if( res != 0 )
			return res;
		return cmpPos( a, b );
	};
	
	var cmpFunc;
	if( col == 0 ) {		// Pos
		cmpFunc = cmpPos;
	}
	else if( col == 4 ) {	// Points
		cmpFunc = function( a, b ) {
			var x = parseInt( a.cells[col].textContent.trim() );
			var y = parseInt( b.cells[col].textContent.trim() );
			return MakeCmpStable( a, b, y - x );
		};
	}
	else if( col > 4 ) {	// Race Points
		cmpFunc = function( a, b ) {
			var x = parsePoints( a.cells[col].textContent.trim() );
			var y = parsePoints( b.cells[col].textContent.trim() );
			return MakeCmpStable( a, b, y - x );
		};
	}
	else {					// Assume string field.
		cmpFunc = function( a, b ) {
		   return MakeCmpStable( a, b, a.cells[col].textContent.trim().localeCompare(b.cells[col].textContent.trim()) );
		};
	}
	tr = tr.sort( function (a, b) { return reverse * cmpFunc(a, b); } );
	
	for( var i = 0; i < tr.length; ++i) {
		tr[i].className = (i % 2 == 1) ? addClass(tr[i].className,'odd') : removeClass(tr[i].className,'odd');
		tb.appendChild( tr[i] );
	}
}

var ssPersist = {};
function sortTableId( iTable, iCol ) {
	var upChar = ' &#x25b2; ', dnChar = ' &#x25bc; ';
	var isNone = 0, isDn = 1, isUp = 2;
	var id = 'idUpDn' + iTable + '_' + iCol;
	var upDn = document.getElementById(id);
	var sortState = ssPersist[id] ? ssPersist[id] : isNone;
	var table = document.getElementById('idTable' + iTable);
	
	console.log( id + ' ' + sortState + ' ' + upDn.innerHTML );
	
	// Clear all sort states.
	var row0Len = table.tBodies[0].rows[0].cells.length
	for( var i = 0; i < row0Len; ++i ) {
		var idCur = 'idUpDn' + iTable + '_' + i;
		document.getElementById(idCur).innerHTML = '';
		ssPersist[idCur] = isNone;
	}

	if( iCol == 0 ) {
		sortTable( table, 0, 1 );
		return;
	}
	
	++sortState;
	switch( sortState ) {
	case isDn:
		upDn.innerHTML = dnChar;
		sortTable( table, iCol, 1 );
		break;
	case isUp:
		upDn.innerHTML = upChar;
		sortTable( table, iCol, -1 );
		break;
	default:
		sortState = isNone;
		sortTable( table, 0, 1 );
		break;
	}
	ssPersist[id] = sortState;
}
''' )

		with tag(html, 'body'):
			with tag(html, 'table'):
				with tag(html, 'tr'):
					with tag(html, 'td', dict(valign='top')):
						data = base64.b64encode(io.open(getHeaderGraphic(),'rb').read())
						html.write( '<img id="idImgHeader" src="data:image/png;base64,%s" />' % data )
					with tag(html, 'td'):
						with tag(html, 'h1'):
							html.write( '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;' + cgi.escape(title) )
			for iTable, categoryName in enumerate(categoryNames):
				results, races = GetModelInfo.GetCategoryResults( categoryName, raceResults, pointsForRank, model.numPlacesTieBreaker )
				results = [rr for rr in results if rr[3] > 0]
				
				headerNames = HeaderNames + [u'{}'.format(r[1]) for r in races]
				
				with tag(html, 'p'):
					pass
				with tag(html, 'hr'):
					pass
				
				with tag(html, 'h2'):
					html.write( cgi.escape(categoryName) )
				with tag(html, 'table', {'class': 'results', 'id': 'idTable{}'.format(iTable)} ):
					with tag(html, 'thead'):
						with tag(html, 'tr'):
							for iHeader, col in enumerate(HeaderNames):
								with tag(html, 'th', {
										'onclick': 'sortTableId({}, {})'.format(iTable, iHeader),
										} ):
									with tag(html, 'span', dict(id='idUpDn{}_{}'.format(iTable,iHeader)) ):
										pass
									html.write( cgi.escape(col).replace('\n', '<br/>\n') )
							for iRace, r in enumerate(races):
								with tag(html, 'th', {
										'class':'leftBorder centerAlign',
										'onclick': 'sortTableId({}, {})'.format(iTable, len(HeaderNames) + iRace),
									} ):
									with tag(html, 'span', dict(id='idUpDn{}_{}'.format(iTable,len(HeaderNames) + iRace)) ):
										pass
									if r[2]:
										with tag(html,'a',dict(href=u'{}?raceCat={}'.format(r[2], urllib.quote(categoryName.encode('utf8')))) ):
											html.write( cgi.escape(r[1]).replace('\n', '<br/>\n') )
									else:
										html.write( cgi.escape(r[1]).replace('\n', '<br/>\n') )
									if r[0]:
										html.write( '<br/>' )
										with tag(html, 'span', {'class': 'smallFont'}):
											html.write( r[0].strftime('%b %d, %Y') )
									html.write( '<br/>' )
									with tag(html, 'span', {'class': 'smallFont'}):
										html.write( u'Top {}'.format(len(r[3].pointStructure)) )
					with tag(html, 'tbody'):
						for pos, (lastName, firstName, license, points, racePoints) in enumerate(results):
							with tag(html, 'tr', {'class':'odd'} if pos % 2 == 1 else {} ):
								with tag(html, 'td', {'class':'rightAlign'}):
									html.write( unicode(pos+1) )
								with tag(html, 'td'):
									html.write( unicode(lastName or '') )
								with tag(html, 'td'):
									html.write( unicode(firstName or '') )
								with tag(html, 'td'):
									html.write( unicode(license or '') )
								with tag(html, 'td', {'class':'rightAlign'}):
									html.write( unicode(points or '') )
								for rPoints, rRank in racePoints:
									with tag(html, 'td', {'class':'leftBorder centerAlign'}):
										html.write( u'{} ({})'.format(rPoints, Utils.ordinal(rRank)) if rPoints else '' )
										
			with tag(html, 'p'):
				pass
			with tag(html, 'hr'):
				pass
				
			with tag(html, 'h2'):
				html.write( 'Point Structures' )
			with tag(html, 'table' ):
				for ps in pointsStructuresList:
					with tag(html, 'tr'):
						for header in [ps.name, u'Races Scored with "{}"'.format(ps.name)]:
							with tag(html, 'th'):
								html.write( header )
					
					with tag(html, 'tr'):
						with tag(html, 'td', {'class': 'topAlign'}):
							html.write( ps.getHtml() )
						with tag(html, 'td', {'class': 'topAlign'}):
							with tag(html, 'ul'):
								for r in pointsStructures[ps]:
									with tag(html, 'li'):
										html.write( r.getRaceName() )
				
				with tag(html, 'tr'):
					with tag(html, 'td'):
						pass
					with tag(html, 'td'):
						pass
						
			with tag(html, 'p'):
				with tag(html, 'a', dict(href='http://sites.google.com/site/crossmgrsoftware')):
					html.write( 'Powered by CrossMgr' )
	
	return html.getvalue()

brandText = 'Powered by CrossMgr (sites.google.com/site/crossmgrsoftware)'

textStyle = xlwt.easyxf(
	"alignment: horizontal left;"
	"borders: bottom thin;"
)
numberStyle = xlwt.easyxf(
	"alignment: horizontal right;"
	"borders: bottom thin;"
)
centerStyle = xlwt.easyxf(
	"alignment: horizontal center;"
	"borders: bottom thin;"
)
labelStyle = xlwt.easyxf(
	"alignment: horizontal center;"
    "borders: bottom medium;"
)

class Results(wx.Panel):
	#----------------------------------------------------------------------
	def __init__(self, parent):
		"""Constructor"""
		wx.Panel.__init__(self, parent)
 
		self.categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Category:' )
		self.categoryChoice = wx.Choice( self, wx.ID_ANY, choices = ['No Categories'] )
		self.categoryChoice.SetSelection( 0 )
		self.categoryChoice.Bind( wx.EVT_CHOICE, self.onCategoryChoice )
		self.exportToHtml = wx.Button( self, wx.ID_ANY, 'Export to Html' )
		self.exportToHtml.Bind( wx.EVT_BUTTON, self.onExportToHtml )
		self.exportToFtp = wx.Button( self, wx.ID_ANY, 'Export to Html with FTP' )
		self.exportToFtp.Bind( wx.EVT_BUTTON, self.onExportToFtp )
		self.exportToExcel = wx.Button( self, wx.ID_ANY, 'Export to Excel' )
		self.exportToExcel.Bind( wx.EVT_BUTTON, self.onExportToExcel )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.categoryLabel, 0, flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL, border = 4 )
		hs.Add( self.categoryChoice, 0, flag=wx.ALL, border = 4 )
		hs.AddStretchSpacer()
		hs.Add( self.exportToHtml, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.exportToFtp, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.exportToExcel, 0, flag=wx.ALL, border = 4 )
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(HeaderNames) )
		self.grid.SetRowLabelSize( 0 )
		self.grid.EnableReorderRows( False )
		self.grid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		self.sortCol = None

		self.setColNames(HeaderNames)

		sizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer.Add(hs, 0, flag=wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, border = 6 )
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.ALL, border = 6)
		self.SetSizer(sizer)
	
	def onCategoryChoice( self, event ):
		wx.CallAfter( self.refresh )
	
	def readReset( self ):
		self.sortCol = None
	
	def doLabelClick( self, event ):
		col = event.GetCol()
		label = self.grid.GetColLabelValue( col )
		if self.sortCol == col:
			self.sortCol = -self.sortCol
		elif self.sortCol == -col:
			self.sortCol = None
		else:
			self.sortCol = col
			
		if not self.sortCol:
			self.sortCol = None
		wx.CallAfter( self.refresh )
	
	def setColNames( self, headerNames ):
		for col, headerName in enumerate(headerNames):
			self.grid.SetColLabelValue( col, headerName )
			attr = gridlib.GridCellAttr()
			if headerName in ('First Name', 'Last Name', 'Team', 'License'):
				attr.SetAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
			elif headerName in ('Pos', 'Points'):
				attr.SetAlignment( wx.ALIGN_RIGHT, wx.ALIGN_TOP )
			else:
				attr.SetAlignment( wx.ALIGN_CENTRE, wx.ALIGN_TOP )
			
			attr.SetReadOnly( True )
			self.grid.SetColAttr( col, attr )
	
	def getGrid( self ):
		return self.grid
		
	def getTitle( self ):
		return self.showResults.GetStringSelection() + ' Series Results'
	
	def fixCategories( self ):
		categoryNames = sorted( set(rr.categoryName for rr in self.raceResults) )
		lastSelection = self.categoryChoice.GetStringSelection()
		self.categoryChoice.SetItems( categoryNames )
		iCurSelection = 0
		for i, n in enumerate(categoryNames):
			if n == lastSelection:
				iCurSelection = i
				break
		self.categoryChoice.SetSelection( iCurSelection )
		self.GetSizer().Layout()

	def refresh( self ):
		model = SeriesModel.model
		self.raceResults = model.extractAllRaceResults()
		
		self.fixCategories()
		self.grid.ClearGrid()
		
		categoryName = self.categoryChoice.GetStringSelection()
		if not categoryName:
			return
			
		pointsForRank = { r.getFileName(): r.pointStructure for r in model.races }

		results, races = GetModelInfo.GetCategoryResults( categoryName, self.raceResults, pointsForRank, 0 )
		results = [rr for rr in results if rr[3] > 0]
		
		headerNames = HeaderNames + [r[1] for r in races]
		
		Utils.AdjustGridSize( self.grid, len(results), len(headerNames) )
		self.setColNames( headerNames )
		
		for row, (lastName, firstName, license, points, racePoints) in enumerate(results):
			self.grid.SetCellValue( row, 0, unicode(row+1) )
			self.grid.SetCellValue( row, 1, unicode(lastName if lastName else '') )
			self.grid.SetCellValue( row, 2, unicode(firstName if firstName else '') )
			self.grid.SetCellValue( row, 3, unicode(license if license else '') )
			self.grid.SetCellValue( row, 4, unicode(points) )
			for q, (rPoints, rRank) in enumerate(racePoints):
				self.grid.SetCellValue( row, 5 + q, u'{} ({})'.format(rPoints, Utils.ordinal(rRank)) if rPoints else '' )
				
			for c in xrange( 0, len(headerNames) ):
				self.grid.SetCellBackgroundColour( row, c, wx.WHITE )
				self.grid.SetCellTextColour( row, c, wx.BLACK )
		
		if self.sortCol is not None:
			data = []
			for r in xrange(0, self.grid.GetNumberRows()):
				rowOrig = [self.grid.GetCellValue(r, c) for c in xrange(0, self.grid.GetNumberCols())]
				rowCmp = [v for v in rowOrig]
				rowCmp[0] = int(rowCmp[0])
				rowCmp[4] = int(rowCmp[4])
				rowCmp[5:] = [-int( v.split()[0] ) if v else 0 for v in rowCmp[5:]]
				rowCmp.extend( rowOrig )
				data.append( rowCmp )
			
			if self.sortCol > 0:
				fg = wx.WHITE
				bg = wx.Colour(0,100,0)
			else:
				fg = wx.BLACK
				bg = wx.Colour(255,165,0)
				
			iCol = abs(self.sortCol)
			data.sort( key = lambda x: x[iCol], reverse = (self.sortCol < 0) )
			for r, row in enumerate(data):
				for c, v in enumerate(row[self.grid.GetNumberCols():]):
					self.grid.SetCellValue( r, c, v )
					if c == iCol:
						self.grid.SetCellTextColour( r, c, fg )
						self.grid.SetCellBackgroundColour( r, c, bg )
						if c < 4:
							halign = wx.ALIGN_LEFT
						elif c == 4:
							halign = wx.ALIGN_RIGHT
						else:
							halign = wx.ALIGN_CENTRE
						self.grid.SetCellAlignment( r, c, halign, wx.ALIGN_TOP )
		
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
	def onExportToExcel( self, event ):
		model = SeriesModel.model
		
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		self.raceResults = model.extractAllRaceResults()
		
		categoryNames = sorted( set(rr.categoryName for rr in self.raceResults) )
		if not categoryNames:
			return
			
		pointsForRank = { r.fileName: r.pointStructure for r in model.races }
		
		wb = xlwt.Workbook()

		for categoryName in categoryNames:
			results, races = GetModelInfo.GetCategoryResults( categoryName, self.raceResults, pointsForRank, model.numPlacesTieBreaker )
			results = [rr for rr in results if rr[3] > 0]
			
			headerNames = HeaderNames + [r[1] for r in races]
			
			ws = wb.add_sheet( re.sub('[:\\/?*\[\]]', ' ', categoryName) )
			wsFit = FitSheetWrapper( ws )

			fnt = xlwt.Font()
			fnt.name = 'Arial'
			fnt.bold = True
			fnt.height = int(fnt.height * 1.5)
			
			headerStyle = xlwt.XFStyle()
			headerStyle.font = fnt
			
			rowCur = 0
			ws.write_merge( rowCur, rowCur, 0, 8, model.name, headerStyle )
			rowCur += 2
			colCur = 0
			ws.write_merge( rowCur, rowCur, colCur, colCur + 4, categoryName, xlwt.easyxf(
																	"font: name Arial, bold on;"
																	) );
				
			rowCur += 2
			for c, headerName in enumerate(headerNames):
				wsFit.write( rowCur, c, headerName, labelStyle, bold = True )
			rowCur += 1
			
			for pos, (lastName, firstName, license, points, racePoints) in enumerate(results):
				wsFit.write( rowCur, 0, pos+1, numberStyle )
				wsFit.write( rowCur, 1, lastName, textStyle )
				wsFit.write( rowCur, 2, firstName, textStyle )
				wsFit.write( rowCur, 3, license, textStyle )
				wsFit.write( rowCur, 4, points, numberStyle )
				for q, (rPoints, rRank) in enumerate(racePoints):
					wsFit.write( rowCur, 5 + q, '{} ({})'.format(rPoints, Utils.ordinal(rRank)) if rPoints else '', centerStyle )
				rowCur += 1
		
			# Add branding at the bottom of the sheet.
			style = xlwt.XFStyle()
			style.alignment.horz = xlwt.Alignment.HORZ_LEFT
			ws.write( rowCur + 2, 0, brandText, style )
		
		if Utils.mainWin:
			xlfileName = os.path.splitext(Utils.mainWin.fileName)[0] + '.xls'
		else:
			xlfileName = 'ResultsTest.xls'
			
		try:
			wb.save( xlfileName )
			webbrowser.open( xlfileName, new = 2, autoraise = True )
			Utils.MessageOK(self, 'Excel file written to:\n\n   %s' % xlfileName, 'Excel Write')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "%s".\n\nCheck if this spreadsheet is open.\nIf so, close it, and try again.' % xlfileName,
						'Excel File Error', iconMask=wx.ICON_ERROR )
	
	def onExportToHtml( self, event ):
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		htmlfileName = getHtmlFileName()

		try:
			with io.open(htmlfileName, 'w', encoding='utf-8') as fp:
				fp.write( getHtml() )
			webbrowser.open( htmlfileName, new = 2, autoraise = True )
			Utils.MessageOK(self, 'Html file written to:\n\n   %s' % htmlfileName, 'html Write')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "%s".\n\nCheck if this file is open.\nIf so, close it, and try again.' % htmlfileName,
						'Html File Error', iconMask=wx.ICON_ERROR )
	
	def onExportToFtp( self, event ):
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		with FtpWriteFile.FtpPublishDialog( self, getHtml() )  as dlg:
			dlg.ShowModal();
	
	def commit( self ):
		pass
		
########################################################################

class ResultsFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, None, title="Results Grid Test", size=(800,600) )
		panel = Results(self)
		panel.refresh()
		self.Show()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
	app = wx.App(False)
	Utils.disable_stdout_buffering()
	model = SeriesModel.model
	files = [
		r'C:\Projects\CrossMgr\ParkAvenue2\2013-06-26-Park Ave Bike Camp Arrowhead mtb 4-r1-.cmn',
	]
	model.races = [SeriesModel.Race(fileName, model.pointStructures[0]) for fileName in files]
	frame = ResultsFrame()
	app.MainLoop()