import wx
import wx.grid as gridlib

import os
import io
import cgi
import sys
import urllib
import base64
import StringIO
import datetime

import Utils
import SeriesModel
import GetModelInfo
from ReorderableGrid import ReorderableGrid
from FitSheetWrapper import FitSheetWrapper
import FtpWriteFile
from ExportGrid import tag

import xlwt
import io
import re
import webbrowser

reNoDigits = re.compile( '[^0-9]' )

HeaderNamesTemplate = ['Pos', 'Name', 'License', 'Team']
def getHeaderNames():
	return HeaderNamesTemplate + ['Total Time' if SeriesModel.model.scoreByTime else 'Points', 'Gap']

#----------------------------------------------------------------------------------

def getHeaderGraphicBase64():
	if Utils.mainWin:
		b64 = Utils.mainWin.getGraphicBase64()
		if b64:
			return b64
	graphicFName = os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png')
	with open(graphicFName, 'rb') as f:
		return 'data:image/png;base64,{}'.format(base64.standard_b64encode(f.read()))

def getHtmlFileName():
	modelFileName = Utils.getFileName() if Utils.getFileName() else 'Test.smn'
	fileName		= os.path.basename( os.path.splitext(modelFileName)[0] + '.html' )
	defaultPath = os.path.dirname( modelFileName )
	return os.path.join( defaultPath, fileName )
	
def getHtml( htmlfileName=None, seriesFileName=None ):
	model = SeriesModel.model
	scoreByTime = model.scoreByTime
	scoreByPercent = model.scoreByPercent
	bestResultsToConsider = model.bestResultsToConsider
	mustHaveCompleted = model.mustHaveCompleted
	hasUpgrades = model.upgradePaths
	considerPrimePointsOrTimeBonus = model.considerPrimePointsOrTimeBonus and not (scoreByTime or scoreByPercent)
	raceResults = model.extractAllRaceResults()
	
	categoryNames = sorted( set(rr.categoryName for rr in raceResults) )
	if not categoryNames:
		return '<html><body>SeriesMgr: No Categories.</body></html>'
	
	HeaderNames = getHeaderNames()
	pointsForRank = { r.getFileName(): r.pointStructure for r in model.races }

	if not seriesFileName:
		seriesFileName = (os.path.splitext(Utils.mainWin.fileName)[0] if Utils.mainWin and Utils.mainWin.fileName else 'Series Results')
	title = os.path.basename( seriesFileName )
	
	licenseLinkTemplate = model.licenseLinkTemplate
	
	pointsStructures = {}
	pointsStructuresList = []
	for race in model.races:
		if race.pointStructure not in pointsStructures:
			pointsStructures[race.pointStructure] = []
			pointsStructuresList.append( race.pointStructure )
		pointsStructures[race.pointStructure].append( race )
	
	html = io.open( htmlfileName, 'w', encoding='utf-8', newline='' )
	
	def write( s ):
		html.write( unicode(s) )
	
	with tag(html, 'html'):
		with tag(html, 'head'):
			with tag(html, 'title'):
				write( title.replace('\n', ' ') )
			with tag(html, 'meta', dict(charset="UTF-8",
										author="Edward Sitarski",
										copyright="Edward Sitarski, 2013-{}".format(datetime.datetime.now().strftime('%Y')),
										generator="SeriesMgr")):
				pass
			with tag(html, 'style', dict( type="text/css")):
				write( u'''
body{ font-family: sans-serif; }

h1{ font-size: 250%; }
h2{ font-size: 200%; }

#idRaceName {
	font-size: 200%;
	font-weight: bold;
}
#idImgHeader { box-shadow: 4px 4px 4px #888888; }
.smallfont { font-size: 80%; }
.bigfont { font-size: 120%; }
.hidden { display: none; }

#buttongroup {
	margin:4px;   
	float:left;
}

#buttongroup label {
	float:left;
	margin:4px;
	background-color:#EFEFEF;
	border-radius:4px;
	border:1px solid #D0D0D0;
	overflow:auto;
	cursor: pointer;
}

#buttongroup label span {
	text-align:center;
	padding:8px 8px;
	display:block;
}

#buttongroup label input {
	position:absolute;
	top:-20px;
}

#buttongroup input:checked + span {
	background-color:#404040;
	color:#F7F7F7;
}

#buttongroup .yellow {
	background-color:#FFCC00;
	color:#333;
}

#buttongroup .blue {
	background-color:#00BFFF;
	color:#333;
}

#buttongroup .pink {
	background-color:#FF99FF;
	color:#333;
}

#buttongroup .green {
	background-color:#7FE57F;
	color:#333;
}
#buttongroup .purple {
	background-color:#B399FF;
	color:#333;
}

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
	vertical-align:bottom;
}
table.results tr.odd
{
	color:#000000;
	background-color:#EAF2D3;
}

.smallFont {
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

.topAlign {
	vertical-align:top;
}

table.results th.centerAlign, table.results td.centerAlign {
	text-align:center;
}

.ignored {
	color: #999;
	font-style: italic;
}

tbody td.points {
	text-align: right;
}

.rank {
	color: #999;
	font-style: italic;
}

hr { clear: both; }

@media print { .noprint { display: none; } }
''')

			with tag(html, 'script', dict( type="text/javascript")):
				write( u'\nvar catMax={};\n'.format( len(categoryNames) ) )
				write( u'''
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

function selectCategory( iCat ) {
	for( var i = 0; i < catMax; ++i ) {
		var e = document.getElementById('catContent' + i);
		if( i == iCat || iCat < 0 )
			e.className = removeClass(e.className, 'hidden');
		else
			e.className = addClass(e.className, 'hidden');
	}
}

function sortTable( table, col, reverse ) {
	var tb = table.tBodies[0];
	var tr = Array.prototype.slice.call(tb.rows, 0);
	
	var parseRank = function( s ) {
		if( !s )
			return 999999;
		var fields = s.split( '(' );
		return parseInt( fields[1] );
	}
	
	var cmpPos = function( a, b ) {
		return parseInt( a.cells[0].textContent.trim() ) - parseInt( b.cells[0].textContent.trim() );
	};
	
	var MakeCmpStable = function( a, b, res ) {
		if( res != 0 )
			return res;
		return cmpPos( a, b );
	};
	
	var cmpFunc;
	if( col == 0 || col == 4 || col == 5 ) {		// Pos, Points or Gap
		cmpFunc = cmpPos;
	}
	else if( col > 4 ) {				// Race Points/Time and Rank
		cmpFunc = function( a, b ) {
			var x = parseRank( a.cells[col].textContent.trim() );
			var y = parseRank( b.cells[col].textContent.trim() );
			return MakeCmpStable( a, b, x - y );
		};
	}
	else {								// Rider data field.
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
	var upChar = '&nbsp;&nbsp;&#x25b2;', dnChar = '&nbsp;&nbsp;&#x25bc;';
	var isNone = 0, isDn = 1, isUp = 2;
	var id = 'idUpDn' + iTable + '_' + iCol;
	var upDn = document.getElementById(id);
	var sortState = ssPersist[id] ? ssPersist[id] : isNone;
	var table = document.getElementById('idTable' + iTable);
	
	// Clear all sort states.
	var row0Len = table.tBodies[0].rows[0].cells.length;
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
						write( u'<img id="idImgHeader" src="{}" />'.format(getHeaderGraphicBase64()) )
					with tag(html, 'td'):
						with tag(html, 'h1', {'style': 'margin-left: 1cm;'}):
							write( cgi.escape(model.name) )
						if model.organizer:
							with tag(html, 'h2', {'style': 'margin-left: 1cm;'}):
								write( u'by {}'.format(cgi.escape(model.organizer)) )
			with tag(html, 'div', {'id':'buttongroup', 'class':'noprint'} ):
				with tag(html, 'label', {'class':'green'} ):
					with tag(html, 'input', {
							'type':"radio",
							'name':"categorySelect",
							'checked':"true",
							'onclick':"selectCategory(-1);"} ):
						with tag(html, 'span'):
							write( u'All' )
				for iTable, categoryName in enumerate(categoryNames):
					with tag(html, 'label', {'class':'green'} ):
						with tag(html, 'input', {
								'type':"radio",
								'name':"categorySelect",
								'onclick':"selectCategory({});".format(iTable)} ):
							with tag(html, 'span'):
								write( unicode(cgi.escape(categoryName)) )
			for iTable, categoryName in enumerate(categoryNames):
				results, races = GetModelInfo.GetCategoryResults(
					categoryName,
					raceResults,
					pointsForRank,
					useMostEventsCompleted=model.useMostEventsCompleted,
					numPlacesTieBreaker=model.numPlacesTieBreaker )
				results = [rr for rr in results if rr[3] > 0]
				
				headerNames = HeaderNames + [u'{}'.format(r[1]) for r in races]
				
				with tag(html, 'div', {'id':'catContent{}'.format(iTable)} ):
					write( u'<p/>')
					write( u'<hr/>')
					
					with tag(html, 'h2'):
						write( cgi.escape(categoryName) )
					with tag(html, 'table', {'class': 'results', 'id': 'idTable{}'.format(iTable)} ):
						with tag(html, 'thead'):
							with tag(html, 'tr'):
								for iHeader, col in enumerate(HeaderNames):
									with tag(html, 'th', {
											'onclick': 'sortTableId({}, {})'.format(iTable, iHeader),
											} ):
										with tag(html, 'span', dict(id='idUpDn{}_{}'.format(iTable,iHeader)) ):
											pass
										write( unicode(cgi.escape(col).replace('\n', '<br/>\n')) )
								for iRace, r in enumerate(races):
									# r[0] = RaceData, r[1] = RaceName, r[2] = RaceURL, r[3] = Race
									with tag(html, 'th', {
											'class':'leftBorder centerAlign',
											'colspan': 2,
											'onclick': 'sortTableId({}, {})'.format(iTable, len(HeaderNames) + iRace),
										} ):
										with tag(html, 'span', dict(id='idUpDn{}_{}'.format(iTable,len(HeaderNames) + iRace)) ):
											pass
										if r[2]:
											with tag(html,'a',dict(href=u'{}?raceCat={}'.format(r[2], urllib.quote(categoryName.encode('utf8')))) ):
												write( unicode(cgi.escape(r[1]).replace('\n', '<br/>\n')) )
										else:
											write( unicode(cgi.escape(r[1]).replace('\n', '<br/>\n')) )
										if r[0]:
											write( u'<br/>' )
											with tag(html, 'span', {'class': 'smallFont'}):
												write( unicode(r[0].strftime('%b %d, %Y')) )
										if not scoreByTime and not scoreByPercent:
											write( u'<br/>' )
											with tag(html, 'span', {'class': 'smallFont'}):
												write( u'Top {}'.format(len(r[3].pointStructure)) )
						with tag(html, 'tbody'):
							for pos, (name, license, team, points, gap, racePoints) in enumerate(results):
								with tag(html, 'tr', {'class':'odd'} if pos % 2 == 1 else {} ):
									with tag(html, 'td', {'class':'rightAlign'}):
										write( unicode(pos+1) )
									with tag(html, 'td'):
										write( unicode(name or u'') )
									with tag(html, 'td'):
										if licenseLinkTemplate and license:
											with tag(html, 'a', {'href':u'{}{}'.format(licenseLinkTemplate, license), 'target':'_blank'}):
												write( unicode(license or u'') )
										else:
											write( unicode(license or u'') )
									with tag(html, 'td'):
										write( unicode(team or '') )
									with tag(html, 'td', {'class':'rightAlign'}):
										write( unicode(points or '') )
									with tag(html, 'td', {'class':'rightAlign'}):
										write( unicode(gap or '') )
									for rPoints, rRank, rPrimePoints, rTimeBonus in racePoints:
										if rPoints:
											with tag(html, 'td', {'class':'leftBorder points' + (' ignored' if u'**' in u'{}'.format(rPoints) else '')}):
												write( u'{}'.format(rPoints).replace(u'[',u'').replace(u']',u'').replace(' ', '&nbsp;') )
										else:
											with tag(html, 'td', {'class':'leftBorder'}):
												pass
										
										if rRank:
											if rPrimePoints:
												with tag(html, 'td', {'class':'rank'}):
													write( u'({})&nbsp;+{}'.format(Utils.ordinal(rRank).replace(' ', '&nbsp;'), rPrimePoints) )
											elif rTimeBonus:
												with tag(html, 'td', {'class':'rank'}):
													write( u'({})&nbsp;-{}'.format(
														Utils.ordinal(rRank).replace(' ', '&nbsp;'),
														Utils.formatTime(rTimeBonus)),
													)
											else:
												with tag(html, 'td', {'class':'rank'}):
													write( u'({})'.format(Utils.ordinal(rRank).replace(' ', '&nbsp;')) )
										else:
											with tag(html, 'td'):
												pass
										
			#-----------------------------------------------------------------------------
			if considerPrimePointsOrTimeBonus > 0:
				with tag(html, 'p'):
					with tag(html, 'strong'):
						write( u'+N' )
					write( u' - {}'.format( u'Bonus Points Added.') )
					
			if bestResultsToConsider > 0:
				with tag(html, 'p'):
					with tag(html, 'strong'):
						write( u'**' )
					write( u' - {}'.format( u'Result not considered.  Not in best of {} scores.'.format(bestResultsToConsider) ) )
					
			if hasUpgrades:
				with tag(html, 'p'):
					with tag(html, 'strong'):
						write( u'pre-upg' )
					write( u' - {}'.format( u'Points carried forward from pre-upgrade category results (see Upgrades Progression below).' ) )
			
			if mustHaveCompleted > 0:
				with tag(html, 'p'):
					write( u'Participants completing fewer than {} events are not shown.'.format(mustHaveCompleted) )
			
			#-----------------------------------------------------------------------------
			
			if not scoreByTime and not scoreByPercent:
				with tag(html, 'p'):
					pass
				with tag(html, 'hr'):
					pass
				
				with tag(html, 'h2'):
					write( 'Point Structures' )
				with tag(html, 'table' ):
					for ps in pointsStructuresList:
						with tag(html, 'tr'):
							for header in [ps.name, u'Races Scored with "{}"'.format(ps.name)]:
								with tag(html, 'th'):
									write( header )
						
						with tag(html, 'tr'):
							with tag(html, 'td', {'class': 'topAlign'}):
								write( ps.getHtml() )
							with tag(html, 'td', {'class': 'topAlign'}):
								with tag(html, 'ul'):
									for r in pointsStructures[ps]:
										with tag(html, 'li'):
											write( r.getRaceName() )
					
					with tag(html, 'tr'):
						with tag(html, 'td'):
							pass
						with tag(html, 'td'):
							pass
						
				#-----------------------------------------------------------------------------
				
				with tag(html, 'p'):
					pass
				with tag(html, 'hr'):
					pass
					
				with tag(html, 'h2'):
					write( u'Tie Breaking Rules' )
					
				with tag(html, 'p'):
					write( u"If two or more riders are tied on points, the following rules will be applied in sequence until the tie is broken:" )
				isFirst = True
				tieLink = u"if still a tie, use "
				with tag(html, 'ol'):
					if model.useMostEventsCompleted:
						with tag(html, 'li'):
							write( u"{}number of events completed".format( tieLink if not isFirst else "" ) )
							isFirst = False
					if model.numPlacesTieBreaker != 0:
						finishOrdinals = [Utils.ordinal(p+1) for p in xrange(model.numPlacesTieBreaker)]
						if model.numPlacesTieBreaker == 1:
							finishStr = finishOrdinals[0]
						else:
							finishStr = u', '.join(finishOrdinals[:-1]) + u' then ' + finishOrdinals[-1]
						with tag(html, 'li'):
							write( u"{}number of {} place finishes".format( tieLink if not isFirst else "",
								finishStr,
							) )
							isFirst = False
					with tag(html, 'li'):
						write( u"{}finish position in most recent event".format(tieLink if not isFirst else "") )
						isFirst = False
				
				if hasUpgrades:
					with tag(html, 'p'):
						pass
					with tag(html, 'hr'):
						pass
					with tag(html, 'h2'):
						write( u"Upgrades Progression" )
					with tag(html, 'ol'):
						for i in xrange(len(model.upgradePaths)):
							with tag(html, 'li'):
								write( u"{}: {:.2f} points in pre-upgrade category carried forward".format(model.upgradePaths[i], model.upgradeFactors[i]) )
			#-----------------------------------------------------------------------------
			with tag(html, 'p'):
				with tag(html, 'a', dict(href='http://sites.google.com/site/crossmgrsoftware')):
					write( u'Powered by CrossMgr' )
	
	html.close()

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
 
		self.categoryLabel = wx.StaticText( self, label='Category:' )
		self.categoryChoice = wx.Choice( self, wx.ID_ANY, choices = ['No Categories'] )
		self.categoryChoice.SetSelection( 0 )
		self.categoryChoice.Bind( wx.EVT_CHOICE, self.onCategoryChoice )
		self.statsLabel = wx.StaticText( self, label='   /   ' )
		self.refreshButton = wx.Button( self, label='Refresh' )
		self.refreshButton.Bind( wx.EVT_BUTTON, lambda event, self = self: self.refresh() )
		self.exportToHtml = wx.Button( self, label='Export to Html' )
		self.exportToHtml.Bind( wx.EVT_BUTTON, self.onExportToHtml )
		self.exportToFtp = wx.Button( self, label='Export to Html with FTP' )
		self.exportToFtp.Bind( wx.EVT_BUTTON, self.onExportToFtp )
		self.exportToExcel = wx.Button( self, label='Export to Excel' )
		self.exportToExcel.Bind( wx.EVT_BUTTON, self.onExportToExcel )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.categoryLabel, 0, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT|wx.RIGHT, border = 4 )
		hs.Add( self.categoryChoice, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.statsLabel, 0, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT|wx.RIGHT, border = 4 )
		hs.AddStretchSpacer()
		hs.Add( self.refreshButton, 0, flag=wx.ALL, border = 4 )
		hs.AddSpacer( 52 )
		hs.Add( self.exportToHtml, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.exportToFtp, 0, flag=wx.ALL, border = 4 )
		hs.Add( self.exportToExcel, 0, flag=wx.ALL, border = 4 )
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(HeaderNamesTemplate)+1 )
		self.grid.SetRowLabelSize( 0 )
		self.grid.EnableReorderRows( False )
		self.grid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		self.sortCol = None

		self.setColNames(getHeaderNames())

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
			if headerName in ('Name', 'Team', 'License'):
				attr.SetAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
			elif headerName in ('Pos', 'Points', 'Gap'):
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
		scoreByTime = model.scoreByTime
		scoreByPercent = model.scoreByPercent
		HeaderNames = getHeaderNames()
		
		wait = wx.BusyCursor()
		self.raceResults = model.extractAllRaceResults()
		del wait
		
		self.fixCategories()
		self.grid.ClearGrid()
		
		categoryName = self.categoryChoice.GetStringSelection()
		if not categoryName:
			return
			
		pointsForRank = { r.getFileName(): r.pointStructure for r in model.races }

		results, races = GetModelInfo.GetCategoryResults(
			categoryName,
			self.raceResults,
			pointsForRank,
			useMostEventsCompleted=model.useMostEventsCompleted,
			numPlacesTieBreaker=model.numPlacesTieBreaker,
		)
		results = [rr for rr in results if rr[3] > 0]
		
		headerNames = HeaderNames + [r[1] for r in races]
		
		Utils.AdjustGridSize( self.grid, len(results), len(headerNames) )
		self.setColNames( headerNames )
		
		for row, (name, license, team, points, gap, racePoints) in enumerate(results):
			self.grid.SetCellValue( row, 0, unicode(row+1) )
			self.grid.SetCellValue( row, 1, unicode(name or u'') )
			self.grid.SetCellValue( row, 2, unicode(license or u'') )
			self.grid.SetCellValue( row, 3, unicode(team or u'') )
			self.grid.SetCellValue( row, 4, unicode(points) )
			self.grid.SetCellValue( row, 5, unicode(gap) )
			for q, (rPoints, rRank, rPrimePoints, rTimeBonus) in enumerate(racePoints):
				self.grid.SetCellValue( row, 6 + q,
					u'{} ({}) +{}'.format(rPoints, Utils.ordinal(rRank), rPrimePoints) if rPoints and rPrimePoints
					else u'{} ({}) -{}'.format(rPoints, Utils.ordinal(rRank), Utils.formatTime(rTimeBonus)) if rPoints and rRank and rTimeBonus
					else u'{} ({})'.format(rPoints, Utils.ordinal(rRank)) if rPoints
					else u'({})'.format(Utils.ordinal(rRank)) if rRank
					else u''
				)
				
			for c in xrange( 0, len(headerNames) ):
				self.grid.SetCellBackgroundColour( row, c, wx.WHITE )
				self.grid.SetCellTextColour( row, c, wx.BLACK )
		
		if self.sortCol is not None:
			def getBracketedNumber( v ):
				numberMax = 99999
				if not v:
					return numberMax
				try:
					return int(reNoDigits.sub('', v.split('(')[1]))
				except (IndexError, ValueError):
					return numberMax
				
			data = []
			for r in xrange(0, self.grid.GetNumberRows()):
				rowOrig = [self.grid.GetCellValue(r, c) for c in xrange(0, self.grid.GetNumberCols())]
				rowCmp = rowOrig[:]
				rowCmp[0] = int(rowCmp[0])
				rowCmp[4] = Utils.StrToSeconds(rowCmp[4])
				rowCmp[5:] = [getBracketedNumber(v) for v in rowCmp[5:]]
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
						elif c == 4 or c == 5:
							halign = wx.ALIGN_RIGHT
						else:
							halign = wx.ALIGN_CENTRE
						self.grid.SetCellAlignment( r, c, halign, wx.ALIGN_TOP )
		
		self.statsLabel.SetLabel( '{} / {}'.format(self.grid.GetNumberRows(), GetModelInfo.GetTotalUniqueParticipants(self.raceResults)) )
		
		self.grid.AutoSizeColumns( False )
		self.grid.AutoSizeRows( False )
		
		self.GetSizer().Layout()
		
	def onExportToExcel( self, event ):
		model = SeriesModel.model
		scoreByTime = model.scoreByTime
		scoreByPercent = model.scoreByPercent
		HeaderNames = getHeaderNames()
		
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		self.raceResults = model.extractAllRaceResults()
		
		categoryNames = sorted( set(rr.categoryName for rr in self.raceResults) )
		if not categoryNames:
			return
			
		pointsForRank = { r.getFileName(): r.pointStructure for r in model.races }
		
		wb = xlwt.Workbook()

		for categoryName in categoryNames:
			results, races = GetModelInfo.GetCategoryResults(
				categoryName,
				self.raceResults,
				pointsForRank,
				useMostEventsCompleted=model.useMostEventsCompleted,
				numPlacesTieBreaker=model.numPlacesTieBreaker,
			)
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
			rowCur += 1
			if model.organizer:
				ws.write_merge( rowCur, rowCur, 0, 8, u'by {}'.format(model.organizer), headerStyle )
				rowCur += 1
			rowCur += 1
			colCur = 0
			ws.write_merge( rowCur, rowCur, colCur, colCur + 4, categoryName, xlwt.easyxf(
																	"font: name Arial, bold on;"
																	) );
				
			rowCur += 2
			for c, headerName in enumerate(headerNames):
				wsFit.write( rowCur, c, headerName, labelStyle, bold = True )
			rowCur += 1
			
			for pos, (name, license, team, points, gap, racePoints) in enumerate(results):
				wsFit.write( rowCur, 0, pos+1, numberStyle )
				wsFit.write( rowCur, 1, name, textStyle )
				wsFit.write( rowCur, 2, license, textStyle )
				wsFit.write( rowCur, 3, team, textStyle )
				wsFit.write( rowCur, 4, points, numberStyle )
				wsFit.write( rowCur, 5, gap, numberStyle )
				for q, (rPoints, rRank, rPrimePoints, rTimeBonus) in enumerate(racePoints):
					wsFit.write( rowCur, 6 + q,
						'{} ({}) +{}'.format(rPoints, Utils.ordinal(rRank), rPrimePoints) if rPoints and rPrimePoints
						else '{} ({}) -{}'.format(rPoints, Utils.ordinal(rRank), Utils.formatTime(rTimeBonus)) if rPoints and rRank and rTimeBonus
						else '{} ({})'.format(rPoints, Utils.ordinal(rRank)) if rPoints
						else '({})'.format(Utils.ordinal(rRank)) if rRank
						else '',
						centerStyle
				)
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
			getHtml( htmlfileName )
			webbrowser.open( htmlfileName, new = 2, autoraise = True )
			Utils.MessageOK(self, u'Html file written to:\n\n   {}'.format(htmlfileName), 'html Write')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "%s".\n\nCheck if this file is open.\nIf so, close it, and try again.' % htmlfileName,
						'Html File Error', iconMask=wx.ICON_ERROR )
	
	def onExportToFtp( self, event ):
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		htmlfileName = getHtmlFileName()
		try:
			getHtml( htmlfileName )
		except IOError:
			return
		
		html = io.open( htmlfileName, 'r', encoding='utf-8', newline='' ).read()
		with FtpWriteFile.FtpPublishDialog( self, html=html ) as dlg:
			dlg.ShowModal()
	
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
