import wx
import os
import sys
import traceback
from time import sleep
from datetime import datetime, timedelta, date, time
import sqlite3
from collections import namedtuple, defaultdict
from threading import RLock, Timer

import CVUtil
from FIFOCache import FIFOCacheSet

from queue import Queue, Empty

import unicodedata
def removeDiacritic( s ):
	return unicodedata.normalize('NFKD', '{}'.format(s)).encode('ascii', 'ignore').decode()

now = datetime.now

class BulkInsertDBRows:
	def __init__( self, table, fields, toDB, maxlen=2000 ):
		self.toDB = toDB
		self.sql = 'INSERT INTO {} ({}) VALUES ({})'.format( table, ','.join(fields), ','.join('?'*len(fields)) )
		self.rows = []
		#self.maxlen = maxlen
		self.maxlen = 1
				
	def append( self, row ):
		self.rows.append( row )
		if len(self.rows) > self.maxlen:
			self.flush()
			
	def flush( self ):
		with self.toDB.dbLock, self.toDB.conn:
			self.toDB.conn.executemany( self.sql, self.rows )
		self.rows.clear()
				
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.flush()

def _createTable( c, table, fields ):
	def default_str( d ):
		return ' DEFAULT {}'.format(d) if d is not None else ''
	
	c.execute(
		'CREATE TABLE IF NOT EXISTS {} ({})'.format(table, ','.join('{} {}{}'.format(
				field, type, default_str(default)
			)
			for field, type, idx, default in fields ) )
	)
	for field, type, idx, default in fields:
		if idx:
			c.execute( 'CREATE INDEX IF NOT EXISTS {}_{}_idx on {} ({} ASC)'.format(table, field, table, field) )

class Database:

	triggerFieldsAll = (
		'id','ts','s_before','s_after','ts_start','closest_frames','bib','first_name','last_name','team','wave','race_name',
		'note','kmh','frames',
		'finish_direction',
		'zoom_frame', 'zoom_x', 'zoom_y', 'zoom_width', 'zoom_height',
	)
	TriggerRecord = namedtuple( 'TriggerRecord', triggerFieldsAll )
	triggerFieldsAllSet = set( triggerFieldsAll )
	
	triggerFieldsInput = tuple( triggerFieldsAllSet
		- {'id', 'note', 'kmh', 'frames', 'finish_direction', 'zoom_frame', 'zoom_x', 'zoom_y', 'zoom_width', 'zoom_height',})	# Fields to compare for equality of triggers.
	triggerFieldsUpdate = ('wave','race_name',)
	triggerEditFields = ('bib', 'first_name', 'last_name', 'team', 'wave', 'race_name', 'note',)
	
	@staticmethod
	def isValidDatabase( fname ):
		try:
			conn = sqlite3.connect( fname, detect_types=sqlite3.PARSE_DECLTYPES, timeout=45.0, check_same_thread=False )
		except Exception as e:
			return False
			
		with conn:
			cur = conn.cursor()
			cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
			cols = {row[0] for row in cur.fetchall()}
			# print( cols )
		return 'trigger' in cols and 'photo' in cols		
	
	def __init__( self, fname=None, initTables=True, fps=30 ):
		self.fname = (fname or os.path.join( os.path.expanduser("~"), 'CrossMgrVideo.sqlite3' ) )
		self.fps = fps
		
		'''
		try:
			print( 'database bytes: {}'.format( os.stat(self.fname).st_size ) )
		except Exception:
			pass
		'''
		
		UpdateSeconds = 10	# Seconds into the past to track duplicate times.
		self.lastTsPhotos = FIFOCacheSet( UpdateSeconds*60 )
		
		# Use an RLock to contol database access ourselves.
		self.dbLock = RLock()
		self.conn = sqlite3.connect( self.fname, detect_types=sqlite3.PARSE_DECLTYPES, timeout=45.0, check_same_thread=False )

		# Configure database for better performance of large blobs.
		cmds = '''
pragma journal_mode = WAL;
pragma synchronous = normal;
pragma temp_store = memory;
pragma page_size = 32768;
pragma mmap_size = 30000000000;'''

		for c in cmds.split(';'):
			c = c.strip()
			if c:
				self.conn.execute( c )
		
		if initTables:
			with self.dbLock, self.conn:
				# Add missing database fields.
				cur = self.conn.cursor()
				cur.execute( 'PRAGMA table_info(trigger)' )
				cols = cur.fetchall()
				if cols:
					col_names = {col[1] for col in cols}
					if 'note' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN note TEXT DEFAULT ""' )
					if 'kmh' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN kmh DOUBLE DEFAULT 0.0' )
					if 'ts_start' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN ts_start timestamp DEFAULT 0' )
						self.conn.execute( 'UPDATE trigger SET ts_start=ts' )
					# Seconds before and after the ts time that frames were captured.
					if 's_before' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN s_before DOUBLE DEFAULT 0.0' )
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN s_after DOUBLE DEFAULT 0.0' )
					# Cache of number of frames.
					if 'frames' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN frames INTEGER DEFAULT 0' )
					# Closest frames queries.
					if 'closest_frames' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN closest_frames INTEGER DEFAULT 0' )
					if 'finish_direction' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN finish_direction INTEGER DEFAULT 0' )
					# Zoom window.
					if 'zoom_frame' not in col_names:
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN zoom_frame  INTEGER DEFAULT -1' )
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN zoom_x      INTEGER DEFAULT 0' )
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN zoom_y      INTEGER DEFAULT 0' )
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN zoom_width  INTEGER DEFAULT 0' )
						self.conn.execute( 'ALTER TABLE trigger ADD COLUMN zoom_height INTEGER DEFAULT 0' )
		
				_createTable( self.conn, 'photo', (
						('id', 'INTEGER PRIMARY KEY', False, None),
						('ts', 'timestamp', 'ASC', None),
						('jpg', 'BLOB', False, None),
					)
				)		
				_createTable( self.conn, 'trigger', (
						('id', 'INTEGER PRIMARY KEY', False, None),
						('ts', 'timestamp', 'ASC', None),			# Capture timestamp.
						('ts_start', 'timestamp', False, None),		# race timestamp.
						('s_before', 'DOUBLE', False, None),		# Seconds before ts of capture.
						('s_after', 'DOUBLE', False, None),			# Seconds after ts of capture.
						('closest_frames', 'INTEGER', False, 0),	# Number of frames if a closest Frames trigger.
						('bib', 'INTEGER', 'ASC', None),
						('first_name', 'TEXT', 'ASC', None),
						('last_name', 'TEXT', 'ASC', None),
						('team', 'TEXT', 'ASC', None),
						('wave', 'TEXT', 'ASC', None),
						('race_name', 'TEXT', 'ASC', None),
						('note', 'TEXT', False, None),
						('kmh', 'DOUBLE', False, 0.0),
						('frames', 'INTEGER', False, 0),			# Number of frames with this trigger.
						
						('finish_direction', 'INTEGER', False, 0),	# 0 == unspecified, 1 == left to right, 2 == right to left.
						
						('zoom_frame',	'INTEGER', False, -1),		# Frame of the best zoom image.  -1 means the Trigger frame.
						('zoom_x', 		'INTEGER', False, 0),		# Zoom x coord
						('zoom_y', 		'INTEGER', False, 0),		# Zoom y coord
						('zoom_width',	'INTEGER', False, 0),		# Zoom width
						('zoom_height', 'INTEGER', False, 0),		# Zoom height
					)
				)
				
				# Initialize the duplicate time cache to the last photos.
				for row in self.conn.execute( 'SELECT ts FROM photo WHERE ts BETWEEN ? AND ?', (now() - timedelta(seconds=UpdateSeconds), now()) ):
					self.lastTsPhotos.add( row[0] )
				
			self.deleteExistingTriggerDuplicates()
			# self.deleteAllDuplicatePhotos()
		
		self.tsJpgsKeyLast = None
		self.tsJpgsLast = None

	def clone( self ):
		return Database( self.fname, initTables=False, fps=self.fps )
		
	def getfname( self ):
		return self.fname
		
	def getsize( self ):
		with self.dbLock:
			try:
				return os.path.getsize( self.fname )
			except Exception:
				return None
	
	def _purgeTriggerWriteDuplicates( self, tsTriggers ):
		'''
			Purge triggers that are already in the database.
			Optimized to use one database call.
		'''
		if not tsTriggers:
			return tsTriggers

		# Get all existing triggers in the same interval as the new ones.
		tsTriggers.sort( key=lambda trig: trig['ts'] )	# Seems inefficient, but tsTriggers are most likely already sorted so this happens quickly.
		tsLower, tsUpper = tsTriggers[0]['ts'], tsTriggers[-1]['ts']
		existingTriggers = set( self.conn.execute( 'SELECT {} FROM trigger WHERE ts BETWEEN ? AND ?'.format(','.join(self.triggerFieldsInput)), (tsLower, tsUpper) ) )
		return [trig for trig in tsTriggers if tuple(trig[f] for f in self.triggerFieldsInput) not in existingTriggers]
	
	def write( self, tsTriggers=None, tsJpgs=None ):
		if tsTriggers or tsJpgs:
			with self.dbLock, self.conn:
				if tsTriggers:
					tsTriggers = self._purgeTriggerWriteDuplicates( tsTriggers )
					for trig in tsTriggers:
						# We can't do an executemany here as each trigger might have different fields.
						# This isn't critical for performance as triggers are low volume.
						# Write this out as sorted fields to keep the sql statements consistent so we maximize precompiling sql statements.
						if trig:
							fields, values = zip( *sorted(trig.items()) )
							self.conn.execute( 'INSERT INTO trigger ({}) VALUES ({})'.format(','.join(fields), ','.join('?'*len(trig))), values )

				if tsJpgs:
					# Purge photos with the same timestamp.
					tsJpgsUnique = []
					for ts, jpg in tsJpgs:
						if ts and jpg and ts not in self.lastTsPhotos:
							self.lastTsPhotos.add( ts )
							tsJpgsUnique.append( (ts, jpg) )
					tsJpgs = tsJpgsUnique
				
				if tsJpgs:
					self.conn.executemany( 'INSERT INTO photo (ts,jpg) VALUES (?,?)', tsJpgs )
			
			# print( 'Database: write tsTriggers={}, tsJpgs={}'.format( tsTriggers, len(tsJpgs) if tsJpgs else 0) )
	
	def updateTriggerRecord( self, id, data ):
		if not id:
			return False
		if data:
			# Filter out any fields that are not part of the record.
			safe_data  = { k:v for k,v in data.items() if k in self.triggerFieldsAllSet }
			if safe_data:
				# Keep the fields sorted so we maximize pre-compiled sql statements.
				fields, values = zip( *sorted(safe_data.items()) )
				with self.dbLock, self.conn:
						self.conn.execute( 'UPDATE trigger SET {} WHERE id=?'.format(','.join('{}=?'.format(f) for f in fields)),
							values + (id,)
						)
		return True
		
	def getTriggerFields( self, id, fieldNames=None ):
		if not fieldNames:
			fieldNames = self.triggerFieldsAll
		with self.dbLock, self.conn:
			row = self.conn.execute( 'SELECT {} FROM trigger WHERE id=?'.format(','.join(fieldNames)), (id,) ).fetchone()
		return { f:row[i] for i, f in enumerate(fieldNames) } if row else None
	
	def updateTriggerKMH( self, id, kmh ):
		self.updateTriggerRecord(id, {'kmh':kmh})
	
	def updateTriggerBeforeAfter( self, id, s_before, s_after ):
		self.updateTriggerRecord(id, {'s_before':s_before, 's_after':s_after})
		
	def initCaptureTriggerData( self, id ):
		'''
			Initialize triggerFieldsUpdate from the previous record.
			Returns the updated fields as a dict.
		'''
		with self.dbLock, self.conn:
			# Get the trigger data and timestamp of the given record.
			triggerRow = self.conn.execute(
				'SELECT {},ts FROM trigger WHERE id=?'.format(','.join(self.triggerFieldsUpdate)), (id,)
			).fetchone()
			if not triggerRow:
				return None
			ts = triggerRow[-1]
			
			# Get the trigger just before this one on this day.
			tsLower, tsUpper = ts.replace(hour=0, minute=0, second=0, microsecond=0), ts
			referenceRow = self.conn.execute( 
				'SELECT {} FROM trigger WHERE id!=? AND ts BETWEEN ? AND ? ORDER BY ts DESC LIMIT 1'.format(','.join(self.triggerFieldsUpdate)),
					(id, tsLower, tsUpper)
			).fetchone()
			if referenceRow and referenceRow != triggerRow[:-1]:
				self.conn.execute(
					'UPDATE trigger SET {} WHERE id=?'.format(','.join('{}=?'.format(f) for f in self.triggerFieldsUpdate)),
						referenceRow + (id,)
				)
				return { k:v for k, v in zip(self.triggerFieldsUpdate, referenceRow) }
			return None
	
	def getTriggers( self, tsLower, tsUpper, bib=None ):
		with self.dbLock, self.conn:
			if not bib:
				triggers = self.conn.execute(
					'SELECT {} FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts'.format(','.join(self.triggerFieldsAll)),
					(tsLower, tsUpper)
				)
			else:
				triggers = self.conn.execute(
					'SELECT {} FROM trigger WHERE bib=? AND ts BETWEEN ? AND ? ORDER BY ts'.format(','.join(self.triggerFieldsAll)),
					(bib, tsLower, tsUpper)
				)
				
			return [self.TriggerRecord(*trig) for trig in triggers]
	
	def _deleteIds( self, table, ids ):
		chunk_size = 500
		while ids:
			to_delete = ids[-chunk_size:]
			self.conn.execute( 'DELETE FROM {} WHERE id IN ({})'.format(table, ','.join('?'*len(to_delete))), to_delete )
			del ids[-chunk_size:]
	
	def _purgeDuplicateTS( self, tsJpgIdIter ):
		tsSeen = set()
		duplicateIds = []
		for ts, jpgId in tsJpgIdIter:
			if ts not in tsSeen:
				tsSeen.add( ts )
				yield ts, jpgId
			else:
				duplicateIds.append( jpgId )
		# For now, just filter out duplicates without removing them from the database.
		# self._deleteIds( 'photo', duplicateIds )
	
	def deleteTss( self, table, tss, callback=None ):
		# Convert the timestamps to strings for the database.
		tss = tss.copy()	# Make a local copy as we destroy this as we go.
		tssTotal = len(tss)
		chunk_size = 250
		if callback:
			callback( 0, tssTotal )
		while tss:
			to_delete = tss[-chunk_size:]
			with self.dbLock, self.conn:
				self.conn.execute( 'DELETE FROM {} WHERE ts IN ({})'.format(table, ','.join('?'*len(to_delete))), to_delete )
			del tss[-chunk_size:]
			if callback:
				callback( tssTotal - len(tss), tssTotal )
	
	def _getPhotosPurgeDuplicateTS( self, tsLower, tsUpper, maxPhotos=None ):
		tsJpgs = []
		tsSeen = set()
		duplicateIds = []
		maxPhotos = maxPhotos or 10000000
		for jpgId, ts, jpg in self.conn.execute( 'SELECT id,ts,jpg FROM photo WHERE ts BETWEEN ? AND ? ORDER BY ts', (tsLower, tsUpper) ):
			if ts and jpg and ts not in tsSeen:
				tsSeen.add( ts )
				tsJpgs.append( (ts, jpg) )
				if len(tsJpgs) == maxPhotos:
					break
			else:
				duplicateIds.append( jpgId )
		# For now, just filter out duplicates without removing them from the database.
		# self._deleteIds( 'photo', duplicateIds )
		return tsJpgs
		
	def _getPhotoCount( self, tsLower, tsUpper ):
		return sum( 1 for _ in self._purgeDuplicateTS(self.conn.execute( 'SELECT ts,id FROM photo WHERE ts BETWEEN ? AND ?', (tsLower, tsUpper))) )
	
	def getPhotos( self, tsLower, tsUpper ):
		# Cache the results of the last query.
		key = (tsLower, tsUpper)
		if key == self.tsJpgsKeyLast:
			return self.tsJpgsLast
		
		with self.dbLock, self.conn:
			tsJpgs = self._getPhotosPurgeDuplicateTS( *key )
		
		if tsJpgs:
			self.tsJpgsKeyLast, self.tsJpgsLast = key, tsJpgs
		return tsJpgs
		
	def runQuery( self, sql, params=None ):
		with self.dbLock, self.conn:
			return list(self.conn.execute( sql, params or tuple()))
	
	def getPhotosClosest( self, ts, closestFrames ):
		# Cache the results of the last query.
		key = (ts, closestFrames)
		if key == self.tsJpgsKeyLast:
			return self.tsJpgsLast
			
		with self.dbLock, self.conn:
			for ts, jpg in self.conn.execute( 'SELECT ts,jpg FROM photo WHERE ts <= ? ORDER BY ts DESC', (ts,) ):
				tsEarlier, jpgEarlier = ts, jpg
				break
			else:
				tsEarlier, jpgEarlier = None, None
			
			for ts, jpg in self.conn.execute( 'SELECT ts,jpg FROM photo WHERE ts > ? ORDER BY ts ASC', (ts,) ):
				tsLater, jpgLater = ts, jpg
				break
			else:
				tsLater, jpgLater = None, None

		# Only works for closestFrames == 1 and closestFrames == 2
		if closestFrames == 1:
			tsJpgs = [(tsEarlier, jpgEarlier) if (tsLater is None or abs((tsEarlier - ts).total_seconds()) < abs((tsLater - ts).total_seconds())) else (tsLater, jpgLater)]
		else:
			tsJpgs = [p for p in [(tsEarlier,jpgEarlier), (tsLater,jpgLater)] if p[1]]
		
		self.tsJpgsKeyLast, self.tsJpgsLast = key, tsJpgs
		return tsJpgs
	
	def _getPhotosClosestIds( self, ts, closestFrames ):
		for ts, id in self.conn.execute( 'SELECT ts,id FROM photo WHERE ts <= ? ORDER BY ts DESC', (ts,) ):
			tsEarlier, idEarlier = ts, id
			break
		else:
			tsEarlier, idEarlier = None, None
		
		for ts, id in self.conn.execute( 'SELECT ts,id FROM photo WHERE ts > ? ORDER BY ts ASC', (ts,) ):
			tsLater, idLater = ts, id
			break
		else:
			tsLater, idLater = None, None

		# Only works for closestFrames == 1 and closestFrames == 2
		if closestFrames == 1:
			tsJpgIds = [(tsEarlier, idEarlier) if (tsLater is None or abs((tsEarlier - ts).total_seconds()) < abs((tsLater - ts).total_seconds())) else (tsLater, idLater)]
		else:
			tsJpgIds = [p for p in [(tsEarlier,idEarlier), (tsLater,idLater)] if p[1]]
		return tsJpgIds
	
	def getPhotoClosest( self, ts ):
		tsJpgs = self.getPhotosClosest( ts, 1 )
		return tsJpgs[0] if tsJpgs else (None, None)
		
	def getTriggerPhotoCount( self, id, s_before_default=0.5, s_after_default=2.0 ):
		with self.dbLock, self.conn:
			trigger = list( self.conn.execute( 'SELECT ts,s_before,s_after FROM trigger WHERE id=?', (id,) ) )
			if not trigger:
				return 0
			ts, s_before, s_after = trigger[0]
			if s_before == 0.0 and s_after == 0.0:
				s_before, s_after = s_before_default, s_after_default
			tsLower, tsUpper = ts - timedelta(seconds=s_before), ts + timedelta(seconds=s_after)
			return self._getPhotoCount(tsLower, tsUpper)
		
	def updateTriggerPhotoCount( self, id, frames=None ):
		with self.dbLock, self.conn:
			frames = frames or self.getTriggerPhotoCount( id )
			self.conn.execute( 'UPDATE trigger SET frames=? WHERE id=? AND frames!=?', (frames, id, frames) )
			return frames
	
	def getPhotoById( self, id ):
		with self.dbLock, self.conn:
			row = self.conn.execute( 'SELECT jpg FROM photo WHERE id=?', (id,) ).fetchone()
		if row is None:
			raise ValueError( 'Nonexistent photo id={}'.format(id) )
		return row[0]		
	
	def getBestTriggerPhoto( self, id ):
		'''
			Return the photo closest to the trigger time, unless the zoom_frame is specified.
			If the zoom_frame is specified, return the tsJpg at that frame.
		'''
		with self.dbLock, self.conn:
			row = self.conn.execute( 'SELECT ts,zoom_frame,s_before,s_after,closest_frames FROM trigger WHERE id=?', (id,) ).fetchone()
		if not row:
			return None, None
		ts,zoom_frame,s_before,s_after,closest_frames = row
		
		if zoom_frame >= 0:
			if closest_frames:
				tsJpgs = self.getPhotosClosest( ts, closest_frames )
			else:
				with self.dbLock, self.conn:
					tsJpgs = self._getPhotosPurgeDuplicateTS( ts-timedelta(seconds=s_before), ts+timedelta(seconds=s_after), zoom_frame+1 )
			try:
				return tsJpgs[zoom_frame]
			except IndexError:
				pass
		return self.getPhotoClosest( ts )
	
	def queryTriggers( self, tsLower, tsUpper, bib=None ):
		triggers = self.getTriggers( tsLower, tsUpper, bib )
		trigs = []
		with self.dbLock, self.conn:
			for trig in triggers:
				trigCur = trig._asdict()
				if trig.closest_frames:
					trigCur['tsJpgIds'] = self._getPhotosClosestIds( trig.ts, trig.closest_frames )
				else:
					trigCur['tsJpgIds'] = list( self._purgeDuplicateTS(
						self.conn.execute( 'SELECT ts,id FROM photo WHERE ts BETWEEN ? AND ?',
							(trig.ts - timedelta(seconds=trig.s_before), trig.ts + timedelta(seconds=trig.s_after)) ) 
						)
					)
				trigs.append( trigCur )
		return trigs
	
	def getTriggerPhotoCounts( self, tsLower, tsUpper ):
		'''
			Return photo counts for all triggers in the interval (tsLower, tsUpper).
		'''
		if isinstance( tsLower, date ):
			tsLower = datetime.combine( tsLower, time(0) )
		if isinstance( tsUpper, date ):
			tsUpper = datetime.combine( tsUpper, time(0) )
		
		tsLowerPhoto, tsUpperPhoto = tsLower, tsUpper
		with self.dbLock, self.conn:
			# Create trigger intervals.
			counts = {}
			trigger_intervals = []
			for (id, ts, s_before, s_after, closest_frames) in self.conn.execute(
					'SELECT id,ts,s_before,s_after,closest_frames FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts', (tsLower, tsUpper) ):
				if closest_frames:
					counts[id] = closest_frames
				else:
					ti = (ts-timedelta(seconds=s_before), ts+timedelta(seconds=s_after), id)
					if ti[0] < tsLowerPhoto: tsLowerPhoto = ti[0]
					if ti[1] > tsUpperPhoto: tsUpperPhoto = ti[1]
					trigger_intervals.append( ti )
					counts[id] = 0
			
			# Sort intervals by start interval 
			trigger_intervals.sort()

			# Count the number of photos in each trigger's interval.
			# Maintain an "active" list of intervals containing the current photo ts.
			active = []
			i = 0
			len_trigger_intervals = len(trigger_intervals)
			for (ts,) in self.conn.execute( 'SELECT ts FROM photo WHERE ts BETWEEN ? AND ? ORDER BY ts', (tsLowerPhoto, tsUpperPhoto) ):
				# Purge intervals outside the current ts.
				active = [act for act in active if ts <= act[1]]

				# Add intervals containing the current ts.
				while i < len_trigger_intervals and trigger_intervals[i][0] <= ts:
					active.append( trigger_intervals[i] )
					i += 1
					
				# Count the photos for all active intervals.
				for act in active:
					counts[act[2]] += 1
			
			return counts			
	
	def updateTriggerPhotoCounts( self, counts ):
		with self.dbLock, self.conn:
			self.conn.executemany( 'UPDATE trigger SET frames=? WHERE id=? AND frames!=?',
				[(count, id, count) for id, count in counts.items()]
			)
	
	def updateTriggerPhotoCountInterval( self, tsLower, tsUpper ):
		self.updateTriggerPhotoCounts( self.getTriggerPhotoCounts(tsLower, tsUpper) )
	
	def getLastPhotos( self, count ):
		with self.dbLock, self.conn:
			tsJpgs = list( self.conn.execute( 'SELECT ts,jpg FROM photo ORDER BY ts DESC LIMIT ?', (count,)) )
		tsJpgs.reverse()
		return tsJpgs
	
	def getLastTimestamp( self, tsLower, tsUpper ):
		with self.dbLock, self.conn:
			c = self.conn.cursor()
			c.execute( 'SELECT ts FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts', (tsLower, tsUpper) )
			return c.fetchone()[0]
		
	def getTimestampRange( self ):
		with self.dbLock, self.conn:
			c = self.conn.cursor()
			c.execute( 'SELECT ts FROM trigger ORDER BY ts ASC' )
			row = c.fetchone()
			if not row:
				return None, None
			trigFirst = row[0]
			c.execute( 'SELECT ts FROM trigger ORDER BY ts DESC' )
			trigLast = c.fetchone()[0]
			return trigFirst, trigLast
	
	def getTriggerDates( self ):
		dates = defaultdict( int )
		races = defaultdict( set )
		with self.dbLock, self.conn:
			for row in self.conn.execute( 'SELECT ts,race_name FROM trigger' ):
				d = row[0].date()
				dates[d] += 1
				races[d].add( row[1] )
		return sorted( (d, c, ','.join(sorted(races[d]))) for d, c in dates.items() )
	
	def getTriggerEditFields( self, id ):
		with self.dbLock, self.conn:
			rows = list( self.conn.execute('SELECT {} FROM trigger WHERE id=?'.format(','.join(self.triggerEditFields)), (id,) ) )
		return {k:v for k, v in zip(self.triggerEditFields, rows[0])} if rows else {}
		
	def setTriggerEditFields( self, id, **kwargs ):
		with self.dbLock, self.conn:
			self.conn.execute(
				'UPDATE trigger SET {} WHERE id=?'.format(','.join('{}=?'.format(f) for f in kwargs.keys())),
				list(kwargs.values()) + [id]
			)
	
	def isDup( self, ts ):
		return ts in self.lastTsPhotos
		
	def deleteExistingTriggerDuplicates( self ):
		with self.dbLock, self.conn:
			rowPrev = None
			duplicateIds = []
			for row in self.conn.execute( 'SELECT id,{} from trigger ORDER BY ts ASC,kmh DESC'.format(','.join(self.triggerFieldsInput)) ):
				if rowPrev is not None and row[1:] == rowPrev[1:]:
					duplicateIds.append( rowPrev[0] )
				else:
					rowPrev = row
		
			self._deleteIds( 'trigger', duplicateIds )
		
	def deleteAllDuplicatePhotos( self ):
		tsSeen = set()
		duplicateIds = []
		with self.dbLock, self.conn:
			for jpgId, ts in self.conn.execute( 'SELECT id,ts FROM photo ORDER BY ts DESC' ):
				if ts and ts not in tsSeen:
					tsSeen.add( ts )
				else:
					duplicateIds.append( jpgId )
			self._deleteIds( 'photo', duplicateIds )
	
	def cleanBetween( self, tsLower, tsUpper ):
		if not tsLower and not tsUpper:
			return
			
		tsLower = tsLower or datedatetime(1900,1,1,0,0,0)
		tsUpper = tsUpper or datedatetime(datedatenow().year+1000,1,1,0,0,0)
	
		with self.dbLock, self.conn:
			self.conn.execute( 'DELETE from photo WHERE ts BETWEEN ? AND ?', (tsLower,tsUpper) )
			self.conn.execute( 'DELETE from trigger WHERE ts BETWEEN ? AND ?', (tsLower,tsUpper) )
	
	def deleteTrigger( self, id, s_before_default=0.5,  s_after_default=2.0 ):
		def getClosestBeforeAfter( ts, closest_frames ):
			tsJpgs = self.getPhotosClosest( ts, closest_frames )
			if not tsJpgs:
				return 0.0, 0.0
			s_before = (ts - tsJpgs[0][0]).total_seconds()
			s_after = (tsJpgs[-1][0] - ts).total_seconds()
			return s_before, s_after
		
		with self.dbLock, self.conn:
			row = self.conn.execute( 'SELECT ts,s_before,s_after,closest_frames FROM trigger WHERE id=?', (id,) ).fetchone()
			if not row:
				return
			
			ts, s_before, s_after, closest_frames = row
			self.conn.execute( 'DELETE FROM trigger WHERE id=?', (id,) )
			
		if closest_frames:
			s_before, s_after = getClosestBeforeAfter( ts, closest_frames )
		
		tsLower, tsUpper = ts - timedelta(seconds=s_before), ts + timedelta(seconds=s_after)
				
		with self.dbLock, self.conn:
			# Get all other intervals that intersect this one.
			triggers = list( self.conn.execute( 'SELECT ts,s_before,s_after,closest_frames FROM trigger WHERE ts BETWEEN ? AND ?',
					(tsLower - timedelta(minutes=15),tsUpper + timedelta(minutes=15)) )
			)
			
		intervals = []
		for ts,s_before,s_after,closest_frames in triggers:
			if closest_frames:
				s_before, s_after = getClosestBeforeAfter( ts, closest_frames )
			elif s_before == 0.0 and s_after == 0.0:
				s_before, s_after = s_before_default, s_after_default
			
			tsStart, tsEnd = ts - timedelta(seconds=s_before), ts + timedelta(seconds=s_after)
			if tsEnd <= tsLower or tsUpper <= tsStart:
				continue
			intervals.append( (max(tsLower,tsStart), min(tsUpper,tsEnd)) )
		
		# Merge overlapping and adjacent intervals together.
		if intervals:
			intervals.sort()
			intervalsNormal = [intervals[0]]
			for a, b in intervals[1:]:
				if a <= intervalsNormal[-1][1]:
					if b > intervalsNormal[-1][1]:
						intervalsNormal[-1] = (intervalsNormal[-1][0], b)
				elif a != b:
					intervalsNormal.append( (a, b) )
			intervals = intervalsNormal

		toRemove = [(tsLower, tsUpper)]
		for a, b in intervals:
			# Split the last interval to accommodate the interval.
			u, v = toRemove.pop()
			if u != a:
				toRemove.append( (u, a) )
			if b != v:
				toRemove.append( (b, v) )

		if toRemove:
			with self.dbLock, self.conn:
				for a, b in toRemove:
					self.conn.execute( 'DELETE from photo WHERE ts BETWEEN ? AND ?', (a,b) )
			
	def vacuum( self ):
		with self.dbLock, self.conn:
			self.conn.execute( 'VACUUM' )

dbGlobal = None
def GlobalDatabase( fname=None ):
	global dbGlobal
	if dbGlobal is None:
		dbGlobal = Database( fname=fname )
	return dbGlobal

def DBWriter( q, queueEmptyCB=None, fname=None ):
	db = GlobalDatabase( fname=fname )
	
	tsTriggers, tsJpgs = [], []
	def flush():
		# Write all outstanding triggers and photos to the database.
		# Clear the buffers afterwards.
		db.write( tsTriggers, tsJpgs )
		tsTriggers.clear()
		tsJpgs.clear()

	keepGoing = True
	
	isTimerRunning = []		# Flag indicating that the timer is running.  Use a list so we can change it from inside the lowActivity function.
	
	if queueEmptyCB:
		def lowActivity():
			# print( 'lowActivity: called' )
			isTimerRunning.clear()
			flush()
			queueEmptyCB()
	else:
		def lowActivity():
			# print( 'lowActivity: called' )
			isTimerRunning.clear()
			flush()

	inactivitySeconds = 0.2
	inactivityTimer = None
	
	# If syncWhenEmpty is True, the lowActivity timer is started when the queue is empty.
	# Set to True when doing buffered writes (eg. photos or triggers).
	syncWhenEmpty = False
	
	def appendPhoto( t, f ):
		if f is not None and not db.isDup( t ):
			# If the photo is "bytes" assume it is already in jpeg encoding.  This should always be the case.
			# Otherwise it is a numpy array and needs to be jpeg encoded before writing to the database.
			tsJpgs.append( (t, sqlite3.Binary(f if isinstance(f, bytes) else CVUtil.frameToJPeg(f))) )
			return True
		return False

	while keepGoing:
		v = q.get()
		
		if v[0] == 'photo':
			syncWhenEmpty = True
			appendPhoto( v[1], v[2] )
		elif v[0] == 'ts_frames':
			lenSave = len( tsJpgs )
			for t, f in v[1]:
				appendPhoto( t, f )
			syncWhenEmpty = (lenSave != len(tsJpgs))
		elif v[0] == 'trigger':
			syncWhenEmpty = True
			tsTriggers.append( v[1] )
		elif v[0] == 'kmh':
			db.updateTriggerKMH( v[1], v[2] )			# id, kmh
		elif v[0] == 'photoCount':
			db.updateTriggerPhotoCount( v[1], v[2] )	# id, count
		elif v[0] == 'flush':
			flush()
		elif v[0] == 'terminate':
			keepGoing = False
		
		if len(tsJpgs) >= 30*4:	# Sync about 4 seconds of frames at a 
			flush()
		
		q.task_done()
		
		if keepGoing and syncWhenEmpty and q.empty():
			# Detect database inactivity after writing photos or triggers.
			#
			# When we have an empty queue, start a timer.
			# If we get more photos or triggers, reset the timer.
			# When the timer goes off, flush the database and call the application callback.
			if isTimerRunning:
				inactivityTimer.cancel()
				isTimerRunning.clear()
			inactivityTimer = Timer( inactivitySeconds, lowActivity )
			inactivityTimer.start()
			isTimerRunning.append( True )
			syncWhenEmpty = False
		
	flush()
	if isTimerRunning:
		inactivityTimer.cancel()
		isTimerRunning.clear()
		if queueEmptyCB:
			queueEmptyCB()
	
if __name__ == '__main__':
	if False:
		try:
			os.remove( os.path.join( os.path.expanduser("~"), 'CrossMgrVideo.sqlite3' ) )
		except Exception:
			pass

	d = GlobalDatabase()
	
	import time
	t_start = process_time()
	# counts = d.getTriggerPhotoCounts(datenow() - timedelta(days=30), datetime(2200,1,1))
	d.updateTriggerPhotoCountInterval( datenow() - timedelta(days=2000), datetime(2200,1,1) )
	print( process_time() - t_start )
	sys.exit()
	
	for k,v in counts.items():
		print( k, v )
	sys.exit()
	
	ts = d.getLastTimestamp(datenow() - timedelta(days=30), datetime(2200,1,1))
	print( ts )
	
	def printTriggers():
		qTriggers = 'SELECT {} FROM trigger ORDER BY ts LIMIT 8'.format(','.join(d.triggerFieldsInput))
		print( '*******************' )
		for row in d.conn.execute(qTriggers):
			print( removeDiacritic(','.join( '{}'.format(v) for v in row )) )
	
	# Create existing duplicateIds all the triggers.
	tsTriggers = d.conn.execute('SELECT {} FROM trigger'.format(','.join(d.triggerFieldsInput))).fetchall()
	d.conn.executemany(
		'INSERT INTO trigger ({}) VALUES ({})'.format(','.join(d.triggerFieldsInput), ','.join('?'*len(d.triggerFieldsInput))),
		tsTriggers
	)	
	printTriggers()
	
	# Delete the existing duplicates.
	d.deleteExistingTriggerDuplicates()
	printTriggers()
	
	# Now, test for checking duplicate triggers on add.
	d.write( tsTriggers, None )
	printTriggers()
	
	print( d.getTriggerDates() )
	
