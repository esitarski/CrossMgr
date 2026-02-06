import wx
import io
import os
import csv
import math
import time
import operator
import datetime
import random

import Model
import Utils
from Undo import undo

def getLynxDir( race ):
	fileName = Utils.getFileName()
	if not fileName:
		fileName = 'test.test'
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
	if p.isdigit():					# All numeric == Finisher.
		return Model.Rider.Finisher
	if p == 'DNS':
		return Model.Rider.DNS
	if 'Q' in p:
		return Model.Rider.DQ
	return Model.Rider.DNF			# default to DNF

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

	def formatUciId( uci_id ):
		if not isinstance(uci_id, str):
			if isinstance(uci_id, float):
				uci_id = f'{uci_id:.0f}'
			else:
				uci_id = f'{uci_id}'
		uci_id = uci_id.replace( ' ', '' )
		return ' '.join( uci_id[i:i+3] for i in range(0, len(uci_id), 3) ) if uci_id.isdigit() else uci_id	# add separating spaces in groups of 3.
	
	# Create the people reference file.
	# ID number, last name, first name, affiliation
	fields = ('LastName', 'FirstName', 'Team')
	with open(fnameBase + '.ppl', 'w', newline='', encoding='utf8') as f:
		writer = csv.writer( f )
		for id, info in sorted( externalInfo.items(), key=operator.itemgetter(0) ):
			row = [id]
			row.extend( info.get(field,'') for field in fields )
			row.append( formatUciId(info.get('UCIID','')) or info.get('License','') )
			writer.writerow( row )

	# Event number, round number, heat number, event name
	# <tab, space or comma>ID, lane # lane=0 as there are no assigned lanes.
	with open(fnameBase + '.evt', 'w', encoding='utf8') as f:
		f.write( '1,1,1,{}\n'.format( os.path.splitext(race.getFileName(includeMemo=False))[0] ) )
		for id in sorted( externalInfo.keys() ):
			f.write( ',{},0\n'.format(id) )
	
	# event number, round number, heat number
	with open(fnameBase + '.sch', 'w', encoding='utf8') as f:
		f.write( '1,1,1\n' )

#-----------------------------------------------------------------------

def ReadLIF( fname ):
	# Read the FinishLynx .LIF finish file.
	# This code assumes that the Export function below was used to create the .ppl, .sch and .evt files for this race.
	# In particular, the 'ID' field is the bib number.
	race = Model.race
	if not race:
		return

	reader = csv.reader( fname )
	# Place, ID, lane, last name, first name, affiliation, <time>, <license>, <delta time>, <ReacTime>, <splits>, time trial start time, user 1, user 2, user 3
	
	fields = ('place', 'id', 'lane', 'last_name', 'first_name', 'affiliation', 'time', 'license', 'delta_time', 'react_time', 'splits', 'tt_start_time')
	int_fields = {'id', 'lane'}
	time_fields = {'time', 'react_time', 'delta_time', 'tt_start_time'}
	
	def getFields( raceStart, row ):
		record = {f:None for f in fields}
		del record['splits']
		record['race_times'] = []
		record['status'] = None
		for i, f in enumerate(fields):
			try:
				v = row[i]
			except IndexError:
				break
				
			if f == 'splits':
				# "splits" may be a comma separated field of "race_time (lap_time)" pairs.
				race_times = []
				for split in v.split(','):
					sv = split.split(' ')
					try:
						t = strToSeconds(sv[0])
						if t:
							race_times.append( t )
					except IndexError:
						continue
						
				record['race_times'] = race_times
				continue

			if f == 'place':
				record['status'] = getStatus( v )
			
			if f in time_fields:
				v = strToSeconds( v )
			elif f in int_fields:
				v = strToInt( v )
				
			record[f] = v
			
		return record

	for i in range(3):
		with open(fname, encoding='utf8') as f:
			s = f.read()
			
		# Check for trailing newline.
		if not (s and s.endswith('\n')):
			# Empty file or no newline.  File is likely being written.  Wait a little and try again.
			time.sleep( 0.5 + random.random() )
			continue
			
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
			except Exception:
				pass
		break
	else:
		raise ValueError( 'FinishLynx results file is empty or does not end with newline' )
	
def ImportLIF( fname ):
	# Update all time entries from FinishLynx.
	# Assume that 'id' is the bib number.
	race = Model.race
	if not race:
		return
		
	race.resetAllCaches()
	undo.pushState()
	race.setChanged()

	count = 0
	for r in ReadLIF( fname ):
		rider = race.getRider( r['id'] )
		
		success = False
		if 'race_times' in r and r['race_times'] and 'time' in r and r['time']:
			# If we have split times, replace the rider times with the splits.
			rider.times = []
			if not race.isTimeTrial:
				rider.firstTime = None
			for t in r['race_times']:
				race.addTime( r['id'], t, False )
			success = True
			count += 1
		elif 'time' in r and r['time']:
			# If not split times, just replace the finish time.
			if rider.times:
				del rider.times[-1:]	# Delete the last known time.			
			race.addTime( r['id'], r['time'], False )
			success = True
			count += 1
	
	race.setChanged()
	return count

def ImportLIFFinish( fname ):
	# Update the last entry from FinishLynx.
	# This is to support the case where we are use RFID for each lap (including the last lap),
	# then use FinishLynx to get the last lap time at the finish.
	# Assume that 'id' is the bib number.
	race = Model.race
	if not race:
		return
	
	race.resetAllCaches()
	undo.pushState()

	count = 0
	for r in ReadLIF( fname ):
		# Update the last entry only (finish time).
		rider = race.getRider( r['id'] )
		
		if 'time' in r and r['time']:
			try:
				if rider.times:
					del rider.times[-1:]	# Delete the last previous time.
				
				# Add the time recorded from FinishLynx.  Ignore the lap splits.
				race.addTime( r['id'], r['time'], False )
				count += 1
			except Exception:
				pass
	
	race.setChanged()
	return count

#-----------------------------------------------------------------------

class FinishLynxDialog( wx.Dialog ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__( parent, id, "FinishLynx",
						style=wx.DEFAULT_DIALOG_STYLE|wx.TAB_TRAVERSAL )
					
		mainSizer = wx.BoxSizer( wx.VERTICAL )	
		
		sz = wx.StaticBoxSizer( wx.VERTICAL, self, _('Export to FinishLynx') + ' (lynx.ppl, lynx.evt, lynx.sch)' )
		
		self.exportButton = wx.Button( self, label=_('Export FinishLynx Files') )
		self.exportButton.Bind( wx.EVT_BUTTON, self.onExport )
		sz.Add( self.exportButton, flag=wx.ALL, border=4 )
		
		mainSizer.Add( sz, flag=wx.EXPAND|wx.ALL, border=8 )

		sz = wx.StaticBoxSizer( wx.VERTICAL, self, _('Import from FinishLynx') +  ' (.lif)' )
		
		self.importFinishButton = wx.Button( self, label=_('FINISH Times ONLY') )
		self.importFinishButton.Bind( wx.EVT_BUTTON, self.onImportFinish )
		sz.Add( self.importFinishButton, flag=wx.ALL, border=4 )
				
		self.importAllButton = wx.Button( self, label=_('ALL Times') )
		self.importAllButton.Bind( wx.EVT_BUTTON, self.onImportAll )
		sz.Add( self.importAllButton, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=4 )

		mainSizer.Add( sz, flag=wx.EXPAND|wx.ALL, border=8 )
		
		btnSizer = self.CreateStdDialogButtonSizer( wx.CANCEL )
		if btnSizer:
			mainSizer.Add( btnSizer, flag=wx.ALL|wx.EXPAND, border=8 )
			
		self.SetSizerAndFit( mainSizer )

	def onExport( self, event ):
		race = Model.race
		if not Model.race:
			return
		
		folder = getLynxDir( race )
		pplname = os.path.join( folder, 'lynx.ppl' )
		if (os.path.isfile(pplname) and
			wx.OK != wx.MessageBox(
				'{}:\n\n\t{}\n\n{}'.format(
					_("FinishLynx files already exist in"),
					folder,
					_("Replace them?"),
				),
				_("FinishLynx Export"), wx.OK|wx.CANCEL, self )
			):
			return
		
		try:
			Export()
			wx.MessageBox( '{}.\n\n{}:\n\n  {}'.format( _("Export successful"), _(".ppl, .evt, .sch files written to folder"), getLynxDir(race) ), _("FinishLynx Export"), wx.OK )
		except Exception as e:
			wx.MessageBox( '{}:\n\n\t{}'.format( _("Export failure"), e), _("FinishLynx Export"), wx.OK )
		
	def onImportFinish( self, event ):
		race = Model.race
		if not Model.race:
			return
			
		with wx.FileDialog(self, _("FinishLynx FINISH Import "), defaultDir=getLynxDir(race), wildcard="FinishLynx Results (*.lif;*.LIF)|*.lif;*.LIF",
						   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			pathname = fileDialog.GetPath()
			
		if wx.OK != wx.MessageBox( _('Replace FINISH timess from FinishLynx.  Confirm?'), _('FinishLynx Import Confirm'),  wx.OK|wx.CANCEL|wx.ICON_WARNING, self ):
			return
			
		try:
			count = ImportLIFFinish( pathname )
			wx.MessageBox( '{} ({})'.format(_("Import FINISH successful"),count), _("FinishLynx Import"), wx.OK, self )
			Utils.refresh()
			self.Destroy()
		except Exception as e:
			wx.MessageBox( '{}:\n\n\t{}'.format( _("Import failure"), e), _("FinishLynx Import"), wx.OK, self )

	def onImportAll( self, event ):
		race = Model.race
		if not Model.race:
			return
		
		with wx.FileDialog(self, _("FinishLynx ALL Import "), defaultDir=getLynxDir(race), wildcard="FinishLynx Results (*.lif;*.LIF)|*.lif;*.LIF",
						   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

			if fileDialog.ShowModal() == wx.ID_CANCEL:
				return
			pathname = fileDialog.GetPath()
			
		if wx.OK != wx.MessageBox( _('Replace ALL lap times from FinishLynx.  Confirm?'), _('FinishLynx Import Confirm'),  wx.OK|wx.CANCEL|wx.ICON_WARNING, self ):
			return
		
		try:
			count = ImportLIF( pathname )
			wx.MessageBox( '{} ({})'.format(_("Import ALL successful"),count), _("FinishLynx Import"), wx.OK, self )
			Utils.refresh()
			self.Destroy()
		except Exception as e:
			wx.MessageBox( '{}:\n\n\t{}'.format( _("Import failure"), e), _("FinishLynx Import"), wx.OK, self )
				
if __name__ == "__main__":
	Model.race = Model.Race()
	Model.race._populate()
	
	#Export( 'finishlynx' )
	ImportLIF( '/home/esitarski/Projects/CrossMgr/data/003-1-01 Default.lif' )
	
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	finishLynx = FinishLynxDialog( mainWin )
	Model.newRace()
	finishLynx.ShowModal()
	app.MainLoop()
