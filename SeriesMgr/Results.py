import os
import io
import re
import base64
import datetime
import xlsxwriter
import webbrowser
import subprocess
import platform
from html import escape
from urllib.parse import quote

import wx
import wx.grid as gridlib

import Utils
import SeriesModel
import GetModelInfo
from ReorderableGrid import ReorderableGrid
from FitSheetWrapper import FitSheetWrapperXLSX
import FtpWriteFile
from ExportGrid import tag

reNoDigits = re.compile( '[^0-9]' )

HeaderNamesTemplate = ['Pos', 'Name', 'License', 'UCI ID', 'Team']
def getHeaderNames():
	return HeaderNamesTemplate + ['Total Time' if SeriesModel.model.scoreByTime else 'Points', 'Gap']

def isUCIID( uci_id ):
	uci_id = re.sub( '[^0-9]', '', str(uci_id) )
	return len(uci_id == 11) and int(uci_id[:-2]) % 97 == int(uci_id[-2:])

def formatUCIID( uci_id ):
	uci_id = re.sub( '[^0-9]', '', str(uci_id) )
	return ' '.join( uci_id[i:i+3] for i in range(0, len(uci_id), 3 ) )

#----------------------------------------------------------------------------------

def toFloat( n ):
	try:
		return float(n)
	except Exception:
		pass
	try:
		return float(n.split()[0])
	except Exception:
		pass
	try:
		return float(n.split(',')[0])
	except Exception:
		pass
		
	if ':' in n:
		t = 0.0
		for v in n.split(':'):
			try:
				t = t * 60.0 + float(v)
			except Exception:
				return -1
		return t
	
	return -1.0

def getHeaderGraphicBase64():
	if Utils.mainWin:
		b64 = Utils.mainWin.getGraphicBase64()
		if b64:
			return b64
	graphicFName = os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png')
	with open(graphicFName, 'rb') as f:
		s64 = base64.standard_b64encode(f.read()).decode()
		return 'data:image/png;base64,{}'.format(s64)

def getFaviconBase64():
	graphicFName = os.path.join(Utils.getImageFolder(), 'SeriesMgr128.png')
	image = wx.Image( graphicFName )
	image.Rescale( 32, 32, wx.IMAGE_QUALITY_HIGH )
	b = io.BytesIO()
	image.SaveFile( b, wx.BITMAP_TYPE_PNG )
	return 'data:image/png;base64,{}'.format(base64.standard_b64encode(b.getvalue()).decode())

def getHtmlFileName():
	modelFileName = Utils.getFileName() if Utils.getFileName() else 'Test.smn'
	fileName		= os.path.basename( os.path.splitext(modelFileName)[0] + '.html' )
	defaultPath = os.path.dirname( modelFileName )
	return os.path.join( defaultPath, fileName )

def fixHeaderNames( results ):
	hasTeam, hasLicense, hasUCIID = True, True, True
	toRemove = set()
	if not any( team for name, license, uci_id, team, points, gap, racePoints in results ):
		toRemove.add( 'Team' )
		hasTeam = False
	if not any( license for name, license, uci_id, team, points, gap, racePoints in results ):
		toRemove.add( 'License' )
		hasLicense = False
	if not any( uci_id for name, license, uci_id, team, points, gap, racePoints in results ):
		toRemove.add( 'UCI ID' )
		hasUCIID = False
	return [h for h in getHeaderNames() if h not in toRemove], hasTeam, hasLicense, hasUCIID

def translateHeader( h ):
	translations = {
		'Team': 'Team/Équipe',
		'Gap': 'Gap/Écart',
		'Name': 'Name/Nom',
	}
	return translations.get( h, h )

def filterValidResults( results ):
	# name, license, uci_id, team, points
	#   0      1       2       3      4
	return [rr for rr in results if toFloat(rr[4]) > 0.0]

def getHtml( htmlfileName=None, seriesFileName=None ):
	model = SeriesModel.model
	scoreByTime = model.scoreByTime
	scoreByPercent = model.scoreByPercent
	scoreByTrueSkill = model.scoreByTrueSkill
	hasUpgrades = model.upgradePaths
	considerPrimePointsOrTimeBonus = model.considerPrimePointsOrTimeBonus
	raceResults = model.extractAllRaceResults()
	
	categoryNames = model.getCategoryNamesSortedPublish()
	if not categoryNames:
		return '<html><body>SeriesMgr: No Categories.</body></html>'
	categoryDisplayNames = model.getCategoryDisplayNames()
	
	if not seriesFileName:
		seriesFileName = (os.path.splitext(Utils.mainWin.fileName)[0] if Utils.mainWin and Utils.mainWin.fileName else 'Series Results')
	title = os.path.basename( seriesFileName )
	
	licenseLinkTemplate = model.licenseLinkTemplate
	
	pointStructures = {}
	pointStructuresList = []
	for race in model.races:
		if race.pointStructure not in pointStructures:
			pointStructures[race.pointStructure] = []
			pointStructuresList.append( race.pointStructure )
		pointStructures[race.pointStructure].append( race )
	
	html = open( htmlfileName, 'w', encoding='utf-8', newline='' )
	
	def ordinal( x ):
		return f'{x}'
	
	def write( s ):
		html.write( '{}'.format(s) )
	
	with tag(html, 'html'):
		with tag(html, 'head'):
			with tag(html, 'title'):
				write( title.replace('\n', ' ') )
			with tag(html, 'meta', {'charset':'UTF-8'}):
				pass
			for k, v in model.getMetaTags():
				with tag(html, 'meta', {'name':k, 'content':v}):
					pass
			with tag(html, 'link', dict(rel="icon", type="image/png", href=getFaviconBase64())):
				pass
			with tag(html, 'style', dict( type="text/css")):
				with open( os.path.join(Utils.getImageFolder(),('green-theme.css','red-theme.css')[model.colorTheme]), encoding='utf8' ) as fs:
					write( fs.read() )

			with tag(html, 'script', dict( type="text/javascript")):
				write( '\nvar catMax={};\n'.format( len(categoryNames) ) )
				write( '''
function removeClass( classStr, oldClass ) {
	let classes = classStr.split( ' ' );
	let ret = [];
	for( let i = 0; i < classes.length; ++i ) {
		if( classes[i] != oldClass )
			ret.push( classes[i] );
	}
	return ret.join(' ');
}

function addClass( classStr, newClass ) {
	return removeClass( classStr, newClass ) + ' ' + newClass;
}

function selectCategory( iCat ) {
	for( let i = 0; i < catMax; ++i ) {
		let e = document.getElementById('catContent' + i);
		if( i == iCat || iCat < 0 )
			e.className = removeClass(e.className, 'hidden');
		else
			e.className = addClass(e.className, 'hidden');
	}
}

function sortTable( table, col, reverse ) {
	let tb = table.tBodies[0];
	let tr = Array.prototype.slice.call(tb.rows, 0);
	
	let parseRank = function( s ) {
		if( !s )
			return 999999;
		let fields = s.split( '(' );
		return parseInt( fields[1] );
	}
	
	let cmpPos = function( a, b ) {
		return parseInt( a.cells[0].textContent.trim() ) - parseInt( b.cells[0].textContent.trim() );
	};
	
	let MakeCmpStable = function( a, b, res ) {
		if( res != 0 )
			return res;
		return cmpPos( a, b );
	};
	
	let cmpFunc;
	if( col == 0 || col == 4 || col == 5 ) {		// Pos, Points or Gap
		cmpFunc = cmpPos;
	}
	else if( col >= 6 ) {				// Race Points/Time and Rank
		cmpFunc = function( a, b ) {
			const x = parseRank( a.cells[6+(col-6)*2+1].textContent.trim() );
			const y = parseRank( b.cells[6+(col-6)*2+1].textContent.trim() );
			return MakeCmpStable( a, b, x - y );
		};
	}
	else {								// Rider data field.
		cmpFunc = function( a, b ) {
		   return MakeCmpStable( a, b, a.cells[col].textContent.trim().localeCompare(b.cells[col].textContent.trim()) );
		};
	}
	tr = tr.sort( function (a, b) { return reverse * cmpFunc(a, b); } );
	
	for( let i = 0; i < tr.length; ++i) {
		tr[i].className = (i % 2 == 1) ? addClass(tr[i].className,'odd') : removeClass(tr[i].className,'odd');
		tb.appendChild( tr[i] );
	}
}

var ssPersist = {};
function sortTableId( iTable, iCol ) {
	let upChar = '&nbsp;&nbsp;&#x25b2;', dnChar = '&nbsp;&nbsp;&#x25bc;';
	let isNone = 0, isDn = 1, isUp = 2;
	let id = 'idUpDn' + iTable + '_' + iCol;
	let upDn = document.getElementById(id);
	let sortState = ssPersist[id] ? ssPersist[id] : isNone;
	let table = document.getElementById('idTable' + iTable);
	
	// Clear all sort states.
	let row0Len = table.tBodies[0].rows[0].cells.length;
	for( let i = 0; i < row0Len; ++i ) {
		let idCur = 'idUpDn' + iTable + '_' + i;
		let ele = document.getElementById(idCur);
		if( ele ) {
			ele.innerHTML = '';
			ssPersist[idCur] = isNone;
		}
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
						write( '<img id="idImgHeader" src="{}" />'.format(getHeaderGraphicBase64()) )
					with tag(html, 'td'):
						with tag(html, 'h1', {'style': 'margin-left: 1cm;'}):
							write( escape(model.name) )
							
						with tag(html, 'h2', {'style': 'margin-left: 1cm;'}):
							write( "Individual Series Results/Résultats Cumulatifs Individuels" )

						with tag(html, 'h2', {'style': 'margin-left: 1cm;'}):
							if model.organizer:
								write( '{}'.format(escape(model.organizer)) )
							with tag(html, 'span', {'style': 'font-size: 60%'}):
								if model.organizer:
									write( '&nbsp;' * 5 )
								write( datetime.datetime.now().strftime('%Y-%m-%d&nbsp;%H:%M:%S') )

			if len(categoryNames) > 1:
				with tag(html, 'h3' ):
					with tag(html, 'label', {'for':'categoryselect'} ):
						write( 'Cat' + ':' )
					with tag(html, 'select', {'name': 'categoryselect', 'onchange':'selectCategory(parseInt(this.value,10))'} ):
						with tag(html, 'option', {'value':-1} ):
							write( '---' )
						for iTable, categoryName in enumerate(categoryNames):
							with tag(html, 'option', {'value':iTable} ):
								write( '{}'.format(escape(categoryDisplayNames[categoryName])) )
			
			hasPrimePoints = any( rr.primePoints for rr in raceResults )
			hasTimeBonus = any( rr.timeBonus for rr in raceResults )
			
			for iTable, categoryName in enumerate(categoryNames):
				
				category = model.categories[categoryName]				
				bestResultsToConsider = (category.bestResultsToConsider if category.bestResultsToConsider is not None else model.bestResultsToConsider)
				mustHaveCompleted = (category.mustHaveCompleted if category.mustHaveCompleted is not None else model.mustHaveCompleted)
				
				results, races, potentialDuplicates = GetModelInfo.GetCategoryResults(
					categoryName,
					raceResults,
					useMostEventsCompleted=model.useMostEventsCompleted,
					numPlacesTieBreaker=model.numPlacesTieBreaker,
					bestResultsToConsider=bestResultsToConsider,
					mustHaveCompleted=mustHaveCompleted,
				)
				
				results = filterValidResults( results )
				headerNames, hasTeam, hasLicense, hasUCIID = fixHeaderNames( results )
				# Do not add the race names (these are added directly below in the <thead> section).
				
				with tag(html, 'div', {'id':'catContent{}'.format(iTable)} ):
					write( '<p/>')
					write( '<hr/>')
					
					with tag(html, 'h2', {'class':'title'}):
						write( escape(categoryDisplayNames[categoryName]) )
					with tag(html, 'table', {'class': 'results', 'id': 'idTable{}'.format(iTable)} ):
						with tag(html, 'thead'):
							with tag(html, 'tr'):
								for iHeader, col in enumerate(headerNames):
									colAttr = { 'onclick': 'sortTableId({}, {})'.format(iTable, iHeader) }
									if col in ('License', 'Gap'):
										colAttr['class'] = 'noprint'
									with tag(html, 'th', colAttr):
										with tag(html, 'span', dict(id='idUpDn{}_{}'.format(iTable,iHeader)) ):
											pass
										write( '{}'.format(escape(translateHeader(col)).replace('\n', '<br/>\n')) )
								for iRace, r in enumerate(races):
									# r[0] = RaceData, r[1] = RaceName, r[2] = RaceURL, r[3] = Race
									with tag(html, 'th', {
											'class':'leftBorder centerAlign noprint',
											'colspan': 2,
											'onclick': 'sortTableId({}, {})'.format(iTable, len(headerNames) + iRace),
										} ):
										with tag(html, 'span', dict(id='idUpDn{}_{}'.format(iTable,len(headerNames) + iRace)) ):
											pass
										
										rName = r[1].replace('\n', '<br/>\n').replace('  ',' ')
										if rName.endswith('Finals'):
											rName = rName.replace('Finals', 'Final')
										rName = escape(rName)
										if r[2]:
											with tag(html,'a',dict(href='{}?raceCat={}'.format(r[2], quote(categoryName.encode('utf8')))) ):
												write( rName )
										else:
											write( rName )
										if r[0]:
											write( '<br/>' )
											with tag(html, 'span', {'class': 'smallFont'}):
												write( '{}'.format(r[0].strftime('%b %d, %Y')) )
										if not scoreByTime and not scoreByPercent and not scoreByTrueSkill:
											write( '<br/>' )
											with tag(html, 'span', {'class': 'smallFont'}):
												write( 'Top {}'.format(len(r[3].pointStructure)) )
						with tag(html, 'tbody'):
							for pos, (name, license, uci_id, team, points, gap, racePoints) in enumerate(results):
								with tag(html, 'tr', {'class':'odd'} if pos % 2 == 1 else {} ):
									with tag(html, 'td', {'class':'rightAlign'}):
										write( '{}'.format(pos+1) )
									with tag(html, 'td'):
										write( '{}'.format(name or '') )
									if hasLicense:
										with tag(html, 'td', {'class':'noprint'}):
											if licenseLinkTemplate and license:
												with tag(html, 'a', {'href':'{}{}'.format(licenseLinkTemplate, license), 'target':'_blank'}):
													write( '{}'.format(license or '') )
											else:
												write( '{}'.format(license or '') )
									if hasUCIID:
										with tag(html, 'td', {'class':'nowrap'}):
											write( '{}'.format( formatUCIID(uci_id)) )
									if hasTeam:
										with tag(html, 'td'):
											write( '{}'.format(team or '') )
									with tag(html, 'td', {'class':'rightAlign'}):
										write( '{}'.format(points or '') )
									with tag(html, 'td', {'class':'rightAlign noprint'}):
										write( '{}'.format(gap or '') )
									for rPoints, rRank, rPrimePoints, rTimeBonus, rr in racePoints:
										if rPoints:
											with tag(html, 'td', {'class':'leftBorder rightAlign noprint' + (' ignored' if '**' in '{}'.format(rPoints) else '')}):
												write( '{}'.format(rPoints).replace('[','').replace(']','').replace(' ', '&nbsp;') )
										else:
											with tag(html, 'td', {'class':'leftBorder noprint'}):
												pass
										
										if rRank <= SeriesModel.rankDNF:
											if rPrimePoints:
												with tag(html, 'td', {'class':'rank noprint'}):
													if hasattr(rr, 'points_explanation'):
														write( '({})'.format( rr.points_explanation.replace(' ','&nbsp;') ) )
													else:
														write( '({})&nbsp;+{}'.format(ordinal(rRank).replace(' ', '&nbsp;'), rPrimePoints) )
											elif rTimeBonus:
												with tag(html, 'td', {'class':'rank noprint'}):
													write( '({})&nbsp;-{}'.format(
														ordinal(rRank).replace(' ', '&nbsp;'),
														Utils.formatTime(rTimeBonus, twoDigitMinutes=False)),
													)
											else:
												with tag(html, 'td', {'class':'rank noprint'}):
													write( '({})'.format(ordinal(rRank).replace(' ', '&nbsp;')) )
										else:
											with tag(html, 'td', {'class':'noprint'}):
												pass
										
			#-----------------------------------------------------------------------------
			if considerPrimePointsOrTimeBonus:
				with tag(html, 'p', {'class':'noprint'}):
					if scoreByTime:
						if hasTimeBonus:
							with tag(html, 'strong'):
								with tag(html, 'span', {'style':'font-style: italic;'}):
									write( '-MM:SS' )
							write( ' - {}'.format( 'Time Bonus subtracted from Finish Time.') )
					elif not scoreByTime and not scoreByPercent and not scoreByTrueSkill:
						if hasPrimePoints:
							with tag(html, 'strong'):
								with tag(html, 'span', {'style':'font-style: italic;'}):
									write( '+N' )
							write( ' - {}'.format( 'Bonus Points added to Points for Place.') )
					
			if bestResultsToConsider is not None and bestResultsToConsider > 0 and not scoreByTrueSkill:
				with tag(html, 'p', {'class':'noprint'}):
					with tag(html, 'strong'):
						write( '**' )
					write( ' - {}'.format( 'Result not considered.  Not in best of {} scores.'.format(bestResultsToConsider) ) )
					
			if hasUpgrades:
				with tag(html, 'p', {'class':'noprint'}):
					with tag(html, 'strong'):
						write( 'pre-upg' )
					write( ' - {}'.format( 'Points carried forward from pre-upgrade category results (see Upgrades Progression below).' ) )
			
			if mustHaveCompleted > 0:
				with tag(html, 'p', {'class':'noprint'}):
					write( 'Participants completing fewer than {} events are not shown.'.format(mustHaveCompleted) )
			
			#-----------------------------------------------------------------------------
			if scoreByTrueSkill:
				with tag(html, 'div', {'class':'noprint'} ):
					with tag(html, 'p'):
						pass
					with tag(html, 'hr'):
						pass
					
					with tag(html, 'p'):
						with tag(html, 'h2'):
							write( 'TrueSkill' )
						with tag(html, 'p'):
							write( "TrueSkill is a ranking method developed by Microsoft Research for the XBox.  ")
							write( "TrueSkill maintains an estimation of the skill of each competitor.  Every time a competitor races, the system accordingly changes the perceived skill of the competitor and acquires more confidence about this perception.  This is unlike a regular points system where a points can be accumulated through regular participation: not necessarily representing  overall racing ability.  ")
						with tag(html, 'p'):
							write( "Results are shown above in the form RR (MM,VV).  Competitor skill is represented by a normally distributed random variable with estimated mean (MM) and variance (VV).  The mean is an estimation of the skill of the competitor and the variance represents how unsure the system is about it (bigger variance = more unsure).  Competitors all start with mean = 25 and variance = 25/3 which corresponds to a zero ranking (see below).  ")
						with tag(html, 'p'):
							write( "The parameters of each distribution are updated based on the results from each race using a Bayesian approach.  The extent of updates depends on each player's variance and on how 'surprising' the outcome is to the system. Changes to scores are negligible when outcomes are expected, but can be large when favorites surprisingly do poorly or underdogs surprisingly do well.  ")
						with tag(html, 'p'):
							write( "RR is the skill ranking defined by RR = MM - 3 * VV.  This is a conservative estimate of the 'actual skill', which is expected to be higher than the estimate 99.7% of the time.  " )
							write( "There is no meaning to positive or negative skill levels which are a result of the underlying mathematics.  The numbers are only meaningful relative to each other.  ")
						with tag(html, 'p'):
							write( "The TrueSkill score can be improved by 'consistently' (say, 2-3 times in a row) finishing ahead of higher ranked competitors.  ")
							write( "Repeatedly finishing with similarly ranked competitors will not change the score much as it isn't evidence of improvement.  ")
						with tag(html, 'p'):
							write("Full details ")
							with tag(html, 'a', {'href': 'https://www.microsoft.com/en-us/research/publication/trueskilltm-a-bayesian-skill-rating-system/'} ):
								write('here.')
				
			if not scoreByTime and not scoreByPercent and not scoreByTrueSkill:
				with tag(html, 'div', {'class':'noprint'} ):
					'''
					with tag(html, 'p'):
						pass
					with tag(html, 'hr'):
						pass
					
					with tag(html, 'h2'):
						write( 'Point Structures' )
					with tag(html, 'table' ):
						for ps in pointStructuresList:
							with tag(html, 'tr'):
								for header in [ps.name, 'Races Scored with {}'.format(ps.name)]:
									with tag(html, 'th'):
										write( header )
							
							with tag(html, 'tr'):
								with tag(html, 'td', {'class': 'topAlign'}):
									write( ps.getHtml() )
								with tag(html, 'td', {'class': 'topAlign'}):
									with tag(html, 'ul'):
										for r in pointStructures[ps]:
											with tag(html, 'li'):
												write( r.getRaceName() )
						
						with tag(html, 'tr'):
							with tag(html, 'td'):
								pass
							with tag(html, 'td'):
								pass
					'''
					#-----------------------------------------------------------------------------
					
					with tag(html, 'p'):
						pass
					with tag(html, 'hr'):
						pass
						
					with tag(html, 'h3'):
						write( 'Tie Breaking Rules' )
						
					with tag(html, 'p'):
						write( "If two or more riders are tied on points, the following rules are applied in sequence until the tie is broken:" )
					isFirst = True
					tieLink = "if still a tie, use "
					with tag(html, 'ol'):
						if model.useMostEventsCompleted:
							with tag(html, 'li'):
								write( "{}number of events completed".format( tieLink if not isFirst else "" ) )
								isFirst = False
						if model.numPlacesTieBreaker != 0:
							finishOrdinals = [Utils.ordinal(p+1) for p in range(model.numPlacesTieBreaker)]
							if model.numPlacesTieBreaker == 1:
								finishStr = finishOrdinals[0]
							else:
								finishStr = ', '.join(finishOrdinals[:-1]) + ' then ' + finishOrdinals[-1]
							with tag(html, 'li'):
								write( "{}number of {} place finishes".format( tieLink if not isFirst else "",
									finishStr,
								) )
								isFirst = False
						with tag(html, 'li'):
							write( "{}finish position in most recent event".format(tieLink if not isFirst else "") )
							isFirst = False
					
					if hasUpgrades:
						with tag(html, 'p'):
							pass
						with tag(html, 'hr'):
							pass
						with tag(html, 'h2'):
							write( "Upgrades Progression" )
						with tag(html, 'ol'):
							for i in range(len(model.upgradePaths)):
								with tag(html, 'li'):
									write( "{}: {:.2f} points in pre-upgrade category carried forward".format(model.upgradePaths[i], model.upgradeFactors[i]) )
			#-----------------------------------------------------------------------------
			with tag(html, 'p'):
				with tag(html, 'a', dict(href='http://sites.google.com/site/crossmgrsoftware')):
					write( 'Powered by CrossMgr' )
	
	html.close()

brandText = 'Powered by CrossMgr (sites.google.com/site/crossmgrsoftware)'

class Results(wx.Panel):
	#----------------------------------------------------------------------
	def __init__(self, parent):
		"""Constructor"""
		wx.Panel.__init__(self, parent)
 
		self.categoryLabel = wx.StaticText( self, label='Category:' )
		self.categoryChoice = wx.Choice( self, choices = ['No Categories'] )
		self.categoryChoice.SetSelection( 0 )
		self.categoryChoice.Bind( wx.EVT_CHOICE, self.onCategoryChoice )
		self.statsLabel = wx.StaticText( self, label='   /   ' )
		self.refreshButton = wx.Button( self, label='Refresh' )
		self.refreshButton.Bind( wx.EVT_BUTTON, self.onRefresh )
		self.publishToHtml = wx.Button( self, label='Publish to Html' )
		self.publishToHtml.Bind( wx.EVT_BUTTON, self.onPublishToHtml )
		self.publishToFtp = wx.Button( self, label='Publish to Html with FTP' )
		self.publishToFtp.Bind( wx.EVT_BUTTON, self.onPublishToFtp )
		self.publishToExcel = wx.Button( self, label='Publish to Excel' )
		self.publishToExcel.Bind( wx.EVT_BUTTON, self.onPublishToExcel )
		
		self.postPublishCmdLabel = wx.StaticText( self, label='Post Publish Cmd:' )
		self.postPublishCmd = wx.TextCtrl( self, size=(300,-1) )
		self.postPublishExplain = wx.StaticText( self, label='Command to run after publish.  Use %* for all filenames (eg. "copy %* dirname")' )

		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( self.categoryLabel, flag=wx.TOP, border=4 )
		hs.Add( self.categoryChoice )
		hs.AddSpacer( 4 )
		hs.Add( self.statsLabel, flag=wx.TOP|wx.LEFT|wx.RIGHT, border=4 )
		hs.AddStretchSpacer()
		hs.Add( self.refreshButton )
		hs.Add( self.publishToHtml, flag=wx.LEFT, border=48 )
		hs.Add( self.publishToFtp, flag=wx.LEFT, border=4 )
		hs.Add( self.publishToExcel, flag=wx.LEFT, border=4 )
		
		hs2 = wx.BoxSizer( wx.HORIZONTAL )
		hs2.Add( self.postPublishCmdLabel, flag=wx.ALIGN_CENTRE_VERTICAL )
		hs2.Add( self.postPublishCmd, flag=wx.ALIGN_CENTRE_VERTICAL )
		hs2.Add( self.postPublishExplain, flag=wx.ALIGN_CENTRE_VERTICAL|wx.LEFT, border=4 )
		
		self.grid = ReorderableGrid( self, style = wx.BORDER_SUNKEN )
		self.grid.DisableDragRowSize()
		self.grid.SetRowLabelSize( 64 )
		self.grid.CreateGrid( 0, len(HeaderNamesTemplate)+1 )
		self.grid.SetRowLabelSize( 0 )
		self.grid.EnableReorderRows( False )
		self.grid.Bind( wx.grid.EVT_GRID_LABEL_LEFT_CLICK, self.doLabelClick )
		self.grid.Bind( wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.doCellClick )
		self.sortCol = None

		self.setColNames( getHeaderNames() )

		sizer = wx.BoxSizer( wx.VERTICAL )
		
		sizer.Add(hs, flag=wx.TOP|wx.LEFT|wx.RIGHT, border = 4 )
		sizer.Add(hs2, flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT|wx.RIGHT, border = 4 )
		sizer.Add(self.grid, 1, flag=wx.EXPAND|wx.TOP|wx.ALL, border = 4)
		self.SetSizer(sizer)
	
	def onRefresh( self, event ):
		SeriesModel.model.clearCache()
		self.refresh()
	
	def onCategoryChoice( self, event ):
		try:
			Utils.getMainWin().teamResults.setCategory( self.categoryChoice.GetString(self.categoryChoice.GetSelection()) )
		except AttributeError:
			pass
		wx.CallAfter( self.refresh )
	
	def setCategory( self, catName ):
		self.fixCategories()
		model = SeriesModel.model
		categoryNames = model.getCategoryNamesSortedPublish()
		for i, n in enumerate(categoryNames):
			if n == catName:
				self.categoryChoice.SetSelection( i )
				break
	
	def readReset( self ):
		self.sortCol = None
		
	def doLabelClick( self, event ):
		col = event.GetCol()
		if self.sortCol == col:
			self.sortCol = -self.sortCol
		elif self.sortCol == -col:
			self.sortCol = None
		else:
			self.sortCol = col
			
		if not self.sortCol:
			self.sortCol = None
		wx.CallAfter( self.refresh )
	
	def doCellClick( self, event ):
		if not hasattr(self, 'popupInfo'):
			self.popupInfo = [
				('{}...'.format(_('Copy Name to Clipboard')),	wx.NewId(), self.onCopyName),
				('{}...'.format(_('Copy License to Clipboard')),	wx.NewId(), self.onCopyLicense),
				('{}...'.format(_('Copy Team to Clipboard')),	wx.NewId(), self.onCopyTeam),
			]
			for p in self.popupInfo:
				if p[2]:
					self.Bind( wx.EVT_MENU, p[2], id=p[1] )

		menu = wx.Menu()
		for i, p in enumerate(self.popupInfo):
			if p[2]:
				menu.Append( p[1], p[0] )
			else:
				menu.AppendSeparator()
		
		self.rowCur, self.colCur = event.GetRow(), event.GetCol()
		self.PopupMenu( menu )
		menu.Destroy()		
	
	def copyCellToClipboard( self, r, c ):
		if wx.TheClipboard.Open():
			# Create a wx.TextDataObject
			do = wx.TextDataObject()
			do.SetText( self.grid.GetCellValue(r, c) )

			# Add the data to the clipboard
			wx.TheClipboard.SetData(do)
			# Close the clipboard
			wx.TheClipboard.Close()
		else:
			wx.MessageBox("Unable to open the clipboard", "Error")		
	
	def onCopyName( self, event ):
		self.copyCellToClipboard( self.rowCur, 1 )
	
	def onCopyLicense( self, event ):
		self.copyCellToClipboard( self.rowCur, 2 )
	
	def onCopyTeam( self, event ):
		self.copyCellToClipboard( self.rowCur, 3 )
	
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
		model = SeriesModel.model
		categoryNames = model.getCategoryNamesSortedPublish()
		lastSelection = self.categoryChoice.GetStringSelection()
		self.categoryChoice.SetItems( categoryNames )
		iCurSelection = 0
		for i, n in enumerate(categoryNames):
			if n == lastSelection:
				iCurSelection = i
				break
		self.categoryChoice.SetSelection( iCurSelection )
		self.GetSizer().Layout()

	def refresh( self, backgroundUpdate=False ):
		model = SeriesModel.model
		
		self.postPublishCmd.SetValue( model.postPublishCmd )
		
		if backgroundUpdate:
			self.raceResults = []
			self.categoryChoice.SetItems( [] )
		else:
			with wx.BusyCursor():
				self.raceResults = model.extractAllRaceResults()
			self.fixCategories()
		
		self.grid.ClearGrid()
		
		categoryName = self.categoryChoice.GetStringSelection()
		if not categoryName:
			return
			
		category = model.categories[categoryName]				
		bestResultsToConsider=(category.bestResultsToConsider if category.bestResultsToConsider is not None else model.bestResultsToConsider)
		mustHaveCompleted=(category.mustHaveCompleted if category.mustHaveCompleted is not None else model.mustHaveCompleted)

		results, races, potentialDuplicates = GetModelInfo.GetCategoryResults(
			categoryName,
			self.raceResults,
			useMostEventsCompleted=model.useMostEventsCompleted,
			numPlacesTieBreaker=model.numPlacesTieBreaker,
			bestResultsToConsider=bestResultsToConsider,
			mustHaveCompleted=mustHaveCompleted,
		)
		
		results = filterValidResults( results )
		headerNames, hasTeam, hasLicense, hasUCIID = fixHeaderNames( results )
		
		headerNames.extend( '{}\n{}'.format(r[1],r[0].strftime('%Y-%m-%d') if r[0] else '') for r in races )
		
		Utils.AdjustGridSize( self.grid, len(results), len(headerNames) )
		self.setColNames( headerNames )
		
		for row, (name, license, uci_id, team, points, gap, racePoints) in enumerate(results):
			iCol = 0
			self.grid.SetCellValue( row, iCol, '{}'.format(row+1) ); iCol += 1
			self.grid.SetCellValue( row, iCol, '{}'.format(name or '') )
			self.grid.SetCellBackgroundColour( row, iCol, wx.Colour(255,255,0) if name in potentialDuplicates else wx.Colour(255,255,255) )
			iCol += 1
			if hasLicense:
				self.grid.SetCellValue( row, iCol, '{}'.format(license or '') ); iCol += 1
			if hasUCIID:
				self.grid.SetCellValue( row, iCol, formatUCIID(uci_id) ); iCol += 1
			if hasTeam:
				self.grid.SetCellValue( row, iCol, '{}'.format(team or '') ); iCol += 1
			self.grid.SetCellValue( row, iCol, '{}'.format(points) ); iCol += 1
			self.grid.SetCellValue( row, iCol, '{}'.format(gap) ); iCol += 1
			for q, (rPoints, rRank, rPrimePoints, rTimeBonus, rr) in enumerate(racePoints):
					
				if hasattr(rr, 'points_explanation'):
					points_explanation = f'{rPoints} ({rr.points_explanation})'
				elif rPoints and rPrimePoints:
					 points_explanation = '{} ({}) +{}'.format(rPoints, Utils.ordinal(rRank), rPrimePoints)
				elif rPoints and rRank and rTimeBonus:
					points_explanation = '{} ({}) -{}'.format(rPoints, Utils.ordinal(rRank), Utils.formatTime(rTimeBonus, twoDigitMinutes=False)) 
				elif rPoints:
					points_explanation = '{} ({})'.format(rPoints, Utils.ordinal(rRank)) 
				elif rRank <= SeriesModel.rankDNF:
					points_explanation = '({})'.format(Utils.ordinal(rRank)) 
				else:
					points_explanation = ''

				self.grid.SetCellValue( row, iCol + q, points_explanation )
				
			for c in range( len(headerNames) ):
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
			for r in range(self.grid.GetNumberRows()):
				rowOrig = [self.grid.GetCellValue(r, c) for c in range(0, self.grid.GetNumberCols())]
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
		
	def onPublishToExcel( self, event ):
		model = SeriesModel.model
		
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		raceResults = model.extractAllRaceResults()
		
		categoryNames = model.getCategoryNamesSortedPublish()
		if not categoryNames:
			return
			
		if Utils.mainWin:
			xlfileName = os.path.splitext(Utils.mainWin.fileName)[0] + '.xlsx'
		else:
			xlfileName = 'ResultsTest.xlsx'
		
		wb = xlsxwriter.Workbook( xlfileName )
		
		textStyle = wb.add_format()
		textStyle.set_align( 'left' )
		textStyle.set_bottom( 1 )
		
		numberStyle = wb.add_format()
		numberStyle.set_align( 'right' )
		numberStyle.set_bottom( 1 )
		
		centerStyle = wb.add_format()
		centerStyle.set_align( 'center' )
		centerStyle.set_bottom( 1 )
		
		labelStyle = wb.add_format()
		labelStyle.set_bold()
		labelStyle.set_align( 'center' )
		labelStyle.set_bottom( 2 )

		brandingStyle = wb.add_format()
		brandingStyle.set_align( 'left' )
		
		headerStyle = wb.add_format()
		headerStyle.set_bold()
		font_size = 16
		headerStyle.set_font_size( font_size )
		
		for categoryName in categoryNames:
			category = model.categories[categoryName]				
			bestResultsToConsider = (category.bestResultsToConsider if category.bestResultsToConsider is not None else model.bestResultsToConsider)
			mustHaveCompleted = (category.mustHaveCompleted if category.mustHaveCompleted is not None else  model.mustHaveCompleted)
			results, races, potentialDuplicates = GetModelInfo.GetCategoryResults(
				categoryName,
				raceResults,
				useMostEventsCompleted=model.useMostEventsCompleted,
				numPlacesTieBreaker=model.numPlacesTieBreaker,
				bestResultsToConsider=bestResultsToConsider,
				mustHaveCompleted=mustHaveCompleted,
			)
			
			results = filterValidResults( results )
			headerNames, hasTeam, hasLicense, hasUCIID = fixHeaderNames( results )
			headerNames.extend( '{}'.format(r[1]) for r in races )
			
			ws = wb.add_worksheet( re.sub('[:\\/?*\\[\\]]', ' ', categoryName) )
			wsFit = FitSheetWrapperXLSX( ws )

			rowCur = 0
			ws.set_row( rowCur, font_size*1.15 )
			ws.merge_range( rowCur, 0, rowCur, 8, model.name, headerStyle )
			rowCur += 1
			if model.organizer:
				ws.set_row( rowCur, font_size*1.15 )
				ws.merge_range( rowCur, 0, rowCur, 8, f'{model.organizer}', headerStyle )
				rowCur += 1
			rowCur += 1
			colCur = 0
			ws.set_row( rowCur, font_size*1.15 )
			ws.merge_range( rowCur, colCur, rowCur, colCur + 4, categoryName, headerStyle )
				
			rowCur += 2
			for c, headerName in enumerate(headerNames):
				wsFit.write( rowCur, c, headerName, labelStyle, bold = True )
			rowCur += 1
			
			for pos, (name, license, uci_id, team, points, gap, racePoints) in enumerate(results):
				iCol = 0
				wsFit.write( rowCur, iCol, pos+1, numberStyle ); iCol += 1
				wsFit.write( rowCur, iCol, name, textStyle ); iCol += 1
				if hasLicense:
					wsFit.write( rowCur, iCol, license, textStyle ); iCol += 1
				if hasUCIID:
					wsFit.write( rowCur, iCol, formatUCIID(uci_id), textStyle ); iCol += 1
				if hasTeam:
					wsFit.write( rowCur, iCol, team, textStyle ); iCol += 1
				wsFit.write( rowCur, iCol, points, numberStyle ); iCol += 1
				wsFit.write( rowCur, iCol, gap, numberStyle ); iCol += 1
				for q, (rPoints, rRank, rPrimePoints, rTimeBonus) in enumerate(racePoints):
					wsFit.write( rowCur, iCol + q,
						'{} ({}) +{}'.format(rPoints, Utils.ordinal(rRank), rPrimePoints) if rPoints and rPrimePoints
						else '{} ({}) -{}'.format(rPoints, Utils.ordinal(rRank), Utils.formatTime(rTimeBonus, twoDigitMinutes=False)) if rPoints and rRank and rTimeBonus
						else '{} ({})'.format(rPoints, Utils.ordinal(rRank)) if rPoints
						else '({})'.format(Utils.ordinal(rRank)) if rRank <= SeriesModel.rankDNF
						else '',
						centerStyle
					)
				rowCur += 1
		
			# Add branding at the bottom of the sheet.
			ws.write( rowCur + 2, 0, brandText, brandingStyle )
		
		try:
			wb.close()
			webbrowser.open( xlfileName, new = 2, autoraise = True )
			Utils.MessageOK(self, 'Excel file written to:\n\n   {}'.format(xlfileName), 'Excel Write')
			self.callPostPublishCmd( xlfileName )
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "{}".\n\nCheck if this spreadsheet is open.\nIf so, close it, and try again.'.format(xlfileName),
						'Excel File Error', iconMask=wx.ICON_ERROR )
	
	def onPublishToHtml( self, event ):
		if Utils.mainWin:
			if not Utils.mainWin.fileName:
				Utils.MessageOK( self, 'You must save your Series to a file first.', 'Save Series' )
				return
		
		htmlfileName = getHtmlFileName()
		model = SeriesModel.model
		model.postPublishCmd = self.postPublishCmd.GetValue().strip()

		try:
			getHtml( htmlfileName )
			webbrowser.open( htmlfileName, new = 2, autoraise = True )
			Utils.MessageOK(self, 'Html file written to:\n\n   {}'.format(htmlfileName), 'html Write')
		except IOError:
			Utils.MessageOK(self,
						'Cannot write "%s".\n\nCheck if this file is open.\nIf so, close it, and try again.' % htmlfileName,
						'Html File Error', iconMask=wx.ICON_ERROR )
		self.callPostPublishCmd( htmlfileName )
	
	def onPublishToFtp( self, event ):
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
		self.callPostPublishCmd( htmlfileName )
	
	def commit( self ):
		model = SeriesModel.model
		postPublishCmd = self.postPublishCmd.GetValue().strip()
		if model.postPublishCmd != postPublishCmd:
			model.postPublishCmd = postPublishCmd
			model.setChanged()

	def callPostPublishCmd( self, fname ):
		self.commit()
		postPublishCmd = SeriesModel.model.postPublishCmd
		if postPublishCmd and fname:
			allFiles = [fname]
			if platform.system() == 'Windows':
				files = ' '.join('""{}""'.format(f) for f in allFiles)
			else:
				files = ' '.join('"{}"'.format(f) for f in allFiles)

			if '%*' in postPublishCmd:
				cmd = postPublishCmd.replace('%*', files)
			else:
				cmd = ' '.join( [postPublishCmd, files] )
			
			try:
				subprocess.check_call( cmd, shell=True )
			except subprocess.CalledProcessError as e:
				Utils.MessageOK( self, '{}\n\n    {}\n{}: {}'.format('Post Publish Cmd Error', e, 'return code', e.returncode), _('Post Publish Cmd Error')  )
			except Exception as e:
				Utils.MessageOK( self, '{}\n\n    {}'.format('Post Publish Cmd Error', e), 'Post Publish Cmd Error'  )
		
########################################################################

class ResultsFrame(wx.Frame):
	#----------------------------------------------------------------------
	def __init__(self):
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
