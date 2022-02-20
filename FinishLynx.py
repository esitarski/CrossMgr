import wx
import io
import os
import csv
import math
import operator
import datetime
from collections import defaultdict

import Model
import Utils

def getLynxDir( race ):
	fileName = Utils.getFileName()
	baseName = os.path.splitext(fileName)[0]
	while baseName.endswith('-'):
		baseName = baseName[:-1]
	return baseName + '-lynx'

def hhmmssmsFromSeconds( t ):
	fract, secs = math.modf( t )
	ms = round( fract * 1000000.0 )
	
	secs = int( secs )
	hh = secs // (60*60)
	mm = (secs // 60) % 60
	ss = secs % 60
	
	return hh, mm, ss, ms
	

def strToSeconds( s = '' ):
	secs = 0.0
	for f in s.split(':'):
		try:
			n = float(f)
		except ValueError:
			n = 0.0
		secs = secs * 60.0 + n
	return secs

def strToInt( s ):
	try:
		return int(s.strip())
	except ValueError:
		return s
		
def getStatus( p ):
	p = p.upper().strip()
	if p.isdigit():
		return Model.Rider.Finisher
	if p == 'DNS':
		return Model.Rider.DNS
	if 'Q' in p:
		return Model.Rider.DQ
	return Model.Rider.DNF			# default DNF

def ReadLIF( fname ):
	race = Model.race
	if not race:
		return

	reader = csv.reader( fname )
	# Place, ID, lane, last name, first name, affiliation, <time>, license, <delta time>, <ReacTime>, <splits>, time trial start time, user 1, user 2, user 3
	
	fields = ('place', 'id', 'lane', 'last_name', 'first_name', 'affiliation', 'time', 'delta_time', 'react_time', 'splits', 'tt_start_time')
	int_fields = {'id', 'lane'}
	time_fields = {'time', 'react_time', 'tt_start_time','delta_time'}
	
	def getFields( raceStart, row ):
		record = {f:None for f in fields}
		del record['splits']
		record['race_times'] = []
		record['lap_times'] = []
		record['status'] = Model.Rider.Finisher
		for i, f in enumerate(fields):
			try:
				v = row[i]
			except IndexError:
				break
				
			if f == 'splits':
				# "splits" is a comma separated field of "race_time (lap_time)" pairs.
				race_times = []
				lap_times = []
				for split in v.split(','):
					sv = split.split(' ')
					try:
						race_times.append( strToSeconds(sv[0]) )
						lap_times.append( strToSeconds(sv[1:-1]) )	# Remove brackets.
					except IndexError:
						break
				record['race_times'] = race_times
				record['lap_times'] = lap_times
				continue

			if f == 'place':
				record['status'] = getStatus( v )
			
			if f in time_fields:
				v = strToSeconds( v )
			elif f in int_fields:
				v = strToInt( v )
				
			record[f] = v
			
		return record

	with open(fname) as f:
		s = f.read()
		
	# Check for training newline (hopefully indicates we got the entire file).
	if s.endswith('\n'):
		raceStart = None
		reader = csv.reader( io.StringIO(s) )
		for i, row in enumerate(reader):
			if i == 0:
				# Get the race start time from the header.
				raceStart = strToSeconds( row[-1] )
				race.startTime = datetime.datetime( *(tuple(int(v) for v in race.date.split('-')) + hhmmssmsFromSeconds(raceStart)) )
				continue
			
			try:
				yield getFields(raceStart, row)
			except Exception as e:
				pass
	
def ImportLIF( fname ):
	race = Model.race
	if not race:
		return
	
	for r in ReadLIF(fname):
		rider = race.getRider( r['id'] )
		category = race.getCategory( rider.num )
		startOffset = self.categoryStartOffset(category)
		rider.times = [t + startOffset for t in record['race_times']]
		rider.status = record['status']
		
	race.setChanged()

#-----------------------------------------------------------------------

def Export( folder=None ):
	''' Export the race in FinishLynx file format (lynx.ppl, lynx.evt, lynx.sch). '''
	''' Write the files into a -lynx folder in the CrossMgr race folder (if no folder given). '''
	''' Ignore the category start offsets and put everyone into one start for FinishLynx. '''
	''' Assume that the categories were started with the correct offsets on import. '''

	race = Model.race
	if not race:
		return
		
	try:
		externalInfo = race.excelLink.read()
	except Exception:
		externalInfo = {}
		
	folder = folder or getLynxDir( race )
	if not os.path.isdir(folder):
		os.mkdir( folder )
	
	fnameBase = os.path.join( folder, 'lynx' )
	
	# Create the people reference file.
	# ID number, last name, first name, affiliation
	fields = ('LastName', 'FirstName', 'Team')
	with open(fnameBase + '.ppl', 'w', newline='') as f:
		writer = csv.writer( f );
		for id, info in sorted( externalInfo.items(), key=operator.itemgetter(0) ):
			writer.writerow( [id] + [externalInfo.get(field,'') for field in fields] )

	# Event number, round number, heat number, event name
	# <tab, space or comma>ID, lane # lane=0 as there are no assigned lanes.
	with open(fnameBase + '.evt', 'w') as f:
		f.write( '1,1,1,{}\n'.format( os.path.splitext(race.getFileName(includeMemo=False))[0] ) )
		for id in sorted( externalInfo.keys() ):
			f.write( ',{},0\n'.format(id) )
	
	# event number, round number, heat number
	with open(fnameBase + '.sch', 'w') as f:
		f.write( '1,1,1\n' )

#-----------------------------------------------------------------------

class FinishLynxDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id, "FinishLynx",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
					
		mainSizer = wx.BoxSizer( wx.VERTICAL )	
		fgs = wx.FlexGridSizer( 2, 4, 4 )
		
		self.exportButton = wx.Button( self, label=_('Export CrossMgr Data to FinishLynx Files (linx.ppl, linx.evt, linx.sch)') )
		self.exportButton.Bind( wx.EVT_BUTTON, self.onExport )
		fgs.Add( self.exportButton )
		self.exportText = wx.StaticText( self, label=_('') )
		fgs.Add( self.exportText )
		
		self.importButton = wx.Button( self, label=_('Import FinishLynx Results Files into CrossMgr (*.lif)') )
		self.importButton.Bind( wx.EVT_BUTTON, self.onImport )
		self.importText = wx.StaticText( self, label=_('') )
		fgs.Add( self.importButton )
		fgs.Add( self.importText )
		
		fgs.AddGrowableCol( 1 )
		
		mainSizer.Add( fgs, flag=wx.EXPAND|wx.ALL, border=8 )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.CLOSE )
		if btnSizer:
			mainSizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border = 8 )
			
		self.SetSizerAndFit( mainSizer )

	def onExport( self, event ):
		race = Model.race
		if not Model.race:
			return
		
		folder = getLynxDir( race )
		pplname = os.path.join( folder, 'lynx.ppl' )
		if (os.path.isfile(pplname) and
			wx.OK != wx.MessageBox(
				'{}\n\n\t{}\n\n{}'.format(
					_("FinishLynx files already exist in."),
					folder,
					_("Replace them?"),
				),
				_("FinishLynx Export"), wx.OK|wx.CANCEL, self )
			):
			return
		
		try:
			Export()
			wx.MessageBox( '{}.\n{}:\n\n  {}'.format( _("Export successful"), _(".ppl, .evt, .sch files written to folder"), getLynxDir(race) ), _("FinishLynx Export"), wx.OK, self )
		except Exception as e:
			wx.MessageBox( '{}:\n\n\t{}'.format( _("Export failure"), e), _("FinishLynx Export"), wx.OK, self )
		
	def onImport( self, event ):
		race = Model.race
		if not Model.race:
			return
		
		with wx.FileDialog(self, _("FinishLynx Results Import "), defaultDir=getLynxDir(race), wildcard="FinishLynx Results (*.lif)|*.lif",
						   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			pathname = fileDialog.GetPath()
			
		try:
			ImportLIF( pathname )
			wx.MessageBox( _("Import successful"), _("FinishLynx Import"), wx.OK, self )
			Utils.refresh()
		except Exception as e:
			wx.MessageBox( '{}:\n\n\t{}'.format( _("Import failure"), e), _("FinishLynx Import"), wx.OK, self )
		
if __name__ == "__main__":
	Model.race = Model.Race()
	Model.race._populate()
	
	Export( 'finishlynx' )
	ImportLIF( 'data/003-1-01 Default.lif' )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	finishLynx = FinishLynxDialog( mainWin )
	Model.newRace()
	finishLynx.ShowModal()
	app.MainLoop()
