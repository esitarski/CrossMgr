import wx
import os
import sys
import time
from datetime import datetime, timedelta
import sqlite3
import CVUtil
from collections import defaultdict

from Queue import Queue, Empty

import unicodedata
def removeDiacritic( s ):
	return unicodedata.normalize('NFKD', unicode(s)).encode('ascii', 'ignore')

now = datetime.now

def createTable( c, table, fields ):
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

class Database( object ):

	UpdateSeconds = 10*60*60

	triggerFieldsAll = ('id','ts','s_before','s_after','ts_start','bib','first_name','last_name','team','wave','race_name','kmh')
	triggerFieldsInput = triggerFieldsAll[1:-1]
	triggerFieldsUpdate = tuple( ['wave','race_name'] )
	triggerEditFields = ('bib', 'first_name', 'last_name', 'team', 'wave', 'race_name')
			
	def __init__( self, fname=None, initTables=True, fps=30 ):
		self.fname = (fname or os.path.join( os.path.expanduser("~"), 'CrossMgrVideo.sqlite3' ) )
		self.fps = fps
		
		'''
		try:
			print 'database bytes: {}'.format( os.stat(self.fname).st_size )
		except:
			pass
		'''
		
		self.conn = sqlite3.connect( self.fname, detect_types=sqlite3.PARSE_DECLTYPES )
		
		# Add kmh, ts_start, sBefore and sAfter to the trigger table if necessary.
		with self.conn:
			cur = self.conn.cursor()
			cur.execute( 'PRAGMA table_info(trigger)' )
			cols = cur.fetchall()
			if cols and not any( col[1] == 'kmh' for col in cols ):
				self.conn.execute( 'ALTER TABLE trigger ADD COLUMN kmh DOUBLE DEFAULT 0.0' )
			if cols and not any( col[1] == 'ts_start' for col in cols ):
				self.conn.execute( 'ALTER TABLE trigger ADD COLUMN ts_start timestamp DEFAULT 0' )
				self.conn.execute( 'UPDATE trigger SET ts_start=ts' )
			# Seconds before and after the ts time that frames were captured.
			if cols and not any( col[1] == 's_before' for col in cols ):
				self.conn.execute( 'ALTER TABLE trigger ADD COLUMN s_before DOUBLE DEFAULT 0.0' )
				self.conn.execute( 'ALTER TABLE trigger ADD COLUMN s_after DOUBLE DEFAULT 0.0' )
		
		if initTables:
			with self.conn:
				createTable( self.conn, 'photo', (
						('id', 'INTEGER PRIMARY KEY', False, None),
						('ts', 'timestamp', 'ASC', None),
						('jpg', 'BLOB', False, None),
					)
				)		
				createTable( self.conn, 'trigger', (
						('id', 'INTEGER PRIMARY KEY', False, None),
						('ts', 'timestamp', 'ASC', None),			# Capture timestamp.
						('s_before', 'DOUBLE', False, None),		# Seconds before ts of capture.
						('s_after', 'DOUBLE', False, None),			# Seconds after ts of capture.
						('ts_start', 'timestamp', False, None),		# race timestamp.
						('bib', 'INTEGER', 'ASC', None),
						('first_name', 'TEXT', 'ASC', None),
						('last_name', 'TEXT', 'ASC', None),
						('team', 'TEXT', 'ASC', None),
						('wave', 'TEXT', 'ASC', None),
						('race_name', 'TEXT', 'ASC', None),
						('kmh', 'DOUBLE', False, 0.0),
					)
				)
				self.photoTsCache = set( row[0] for row in self.conn.execute(
						'SELECT ts FROM photo WHERE ts BETWEEN ? AND ?', (now() - timedelta(seconds=self.UpdateSeconds), now())
					)
				)
		else:
			self.photoTsCache = set()
		
		self.lastUpdate = now() - timedelta(seconds=self.UpdateSeconds)
		self.deleteExistingTriggerDuplicates()

	def getsize( self ):
		try:
			return os.path.getsize( self.fname )
		except:
			return None
	
	def purgeTriggerWriteDuplicates( self, tsTriggers ):
		""" Remove all triggers that are already in the database. """
		if not tsTriggers:
			return tsTriggers
		
		tsTriggersUnique = []
		for t in tsTriggers:
			if self.conn.execute(
				'SELECT id FROM trigger WHERE {}'.format(' AND '.join('{}=?'.format(f) for f in self.triggerFieldsInput)), t).fetchone() is None:
				tsTriggersUnique.append( t )
		return tsTriggersUnique
	
	def write( self, tsTriggers=None, tsJpgs=None ):
		tsTriggers = self.purgeTriggerWriteDuplicates( tsTriggers )
		if not tsTriggers and not tsJpgs:
			return
		
		if tsJpgs:
			# Purge duplicate photos, or with the same timestamp.
			jpgSeen = set()
			tsJpgsUnique = []
			for ts_jpg in tsJpgs:
				if ts_jpg[1] and ts_jpg[0] not in self.photoTsCache and ts_jpg[1] not in jpgSeen:
					jpgSeen.add( ts_jpg[1] )
					tsJpgsUnique.append( ts_jpg )
			tsJpgs = tsJpgsUnique
		
		with self.conn:
			if tsTriggers:
				self.conn.executemany(
					'INSERT INTO trigger ({}) VALUES ({})'.format(','.join(self.triggerFieldsInput), ','.join('?'*len(self.triggerFieldsInput))),
					tsTriggers )
			if tsJpgs:
				self.conn.executemany( 'INSERT INTO photo (ts,jpg) VALUES (?,?)', tsJpgs )
		
		if tsJpgs:
			self.photoTsCache.update( ts for ts, jpg in tsJpgs )
		
		if (now() - self.lastUpdate).total_seconds() > self.UpdateSeconds:
			expired = now() - timedelta(seconds=self.UpdateSeconds)
			self.photoTsCache = set( ts for ts in self.photoTsCache if ts > expired )
			self.lastUpdate = now()
	
	def updateTriggerKMH( self, id, kmh ):
		with self.conn:
			self.conn.execute( 'UPDATE trigger SET kmh=? WHERE id=?', (kmh,id) )
	
	def updateTriggerBeforeAfter( self, id, s_before, s_after ):
		with self.conn:
			self.conn.execute( 'UPDATE trigger SET s_before=?, s_after=? WHERE id=?', (s_before,s_after,id) )
	
	def initCaptureTriggerData( self, id, ts ):
		with self.conn:
			tsLower, tsUpper = ts, ts - timedelta( days=1 )
			rows = list( self.conn.execute( 
				'SELECT {} FROM trigger WHERE ts > ? and ts < ? ORDER BY ts DESC LIMIT 1'.format(','.join(self.triggerFieldsUpdate)),
					(tsLower, tsUpper)
				)
			)
			if rows:
				self.conn.execute(
					'UPDATE trigger SET {} WHERE id = ?'.format(','.join('{}=?'.format(f) for f in self.triggerFieldsUpdate)),
						rows[0] + [id]
				)
	
	def getTriggers( self, tsLower, tsUpper, bib=None ):
		with self.conn:
			if not bib:
				return list( self.conn.execute(
					'SELECT {} FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts'.format(','.join(self.triggerFieldsAll)),
					(tsLower, tsUpper)
				))
			else:
				return list( self.conn.execute(
					'SELECT {} FROM trigger WHERE bib=? AND ts BETWEEN ? AND ? ORDER BY ts'.format(','.join(self.triggerFieldsAll)),
					(bib, tsLower, tsUpper)
				))
			
	def getPhotos( self, tsLower, tsUpper ):
		with self.conn:
			return list( self.conn.execute( 'SELECT ts,jpg FROM photo WHERE ts BETWEEN ? AND ? ORDER BY ts', (tsLower, tsUpper)) )
	
	def getLastPhotos( self, count ):
		with self.conn:
			tsJpgs = list( self.conn.execute( 'SELECT ts,jpg FROM photo ORDER BY ts DESC LIMIT ?', (count,)) )
		tsJpgs.reverse()
		return tsJpgs
	
	def getLastTimestamp( self, tsLower, tsUpper ):
		c = self.conn.cursor()
		c.execute( 'SELECT ts FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts', (tsLower, tsUpper) )
		return c.fetchone()[0]
		
	def getTimestampRange( self ):
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
		for row in self.conn.execute( 'SELECT ts FROM trigger' ):
			dates[row[0].date()] += 1
		return sorted( dates.items() )
	
	def getTriggerEditFields( self, id ):
		with self.conn:
			rows = list( self.conn.execute('SELECT {} FROM trigger WHERE id=?'.format(','.join(self.triggerEditFields)), (id,) ) )
		return rows[0] if rows else []
		
	def setTriggerEditFields( self, id, *args ):
		with self.conn:
			self.conn.execute(
				'UPDATE trigger SET {} WHERE id=?'.format(','.join('{}=?'.format(f) for f in self.triggerEditFields)),
				list(args) + [id]
			)
	
	def isDup( self, ts ):
		return ts in self.photoTsCache
		
	def deleteExistingTriggerDuplicates( self ):
		rowPrev = None
		duplicateIds = []
		for row in self.conn.execute( 'SELECT id,{} from trigger ORDER BY ts ASC,kmh DESC'.format(','.join(self.triggerFieldsInput)) ):
			if rowPrev is not None and row[1:] == rowPrev[1:]:
				duplicateIds.append( rowPrev[0] )
			else:
				rowPrev = row
		
		chunkSize = 500
		while duplicateIds:
			ids = duplicateIds[:chunkSize]
			self.conn.execute( 'DELETE FROM trigger WHERE id IN ({})'.format( ','.join('?'*len(ids)) ), ids )
			del duplicateIds[:chunkSize]
		
	def cleanBetween( self, tsLower, tsUpper ):
		if not tsLower and not tsUpper:
			return
			
		tsLower = tsLower or datetime.datetime(1900,1,1,0,0,0)
		tsUpper = tsUpper or datetime.datetime(datetime.datetime.now().year+1000,1,1,0,0,0)
	
		with self.conn:
			self.conn.execute( 'DELETE from photo WHERE ts BETWEEN ? AND ?', (tsLower,tsUpper) )
			self.conn.execute( 'DELETE from trigger WHERE ts BETWEEN ? AND ?', (tsLower,tsUpper) )
		
	def vacuum( self ):
		self.conn.execute( 'VACUUM' )
		
tsJpgs = []
tsTriggers = []
def flush( db ):
	db.write( tsTriggers, tsJpgs )
	del tsTriggers[:]
	del tsJpgs[:]
		
def DBWriter( q, fps=30 ):
	db = Database( fps=fps )
	
	keepGoing = True
	while keepGoing:
		try:
			v = q.get( timeout=1 )
		except Empty:
			if tsTriggers or tsJpgs:
				flush( db )
			continue
		
		doFlush = True
		if v[0] == 'photo':
			doFlush = False
			if not db.isDup( v[1] ):
				tsJpgs.append( (v[1], sqlite3.Binary(CVUtil.frameToJPeg(v[2]))) )
		elif v[0] == 'trigger':
			fieldLen = len(Database.triggerFieldsInput)
			tsTriggers.append( (list(v[1:]) + [u''] * fieldLen)[:fieldLen] )
		elif v[0] == 'kmh':
			db.updateTriggerKMH( v[1], v[2] )	# id, kmh
		elif v[0] == 'flush':
			pass
		elif v[0] == 'terminate':
			keepGoing = False
		
		if doFlush or len(tsJpgs) >= db.fps*3:
			flush( db )
		q.task_done()
		
	flush( db )
	
def DBReader( q, callback ):
	db = Database( initTables=False )
	
	keepGoing = True
	while keepGoing:
		v = q.get()
		if v[0] == 'getphotos':
			flush( db )
			callback( db.getPhotos(v[1], v[2]) )
		elif v[0] == 'terminate':
			keepGoing = False
		
		q.task_done()
			
if __name__ == '__main__':
	if False:
		try:
			os.remove( os.path.join( os.path.expanduser("~"), 'CrossMgrVideo.sqlite3' ) )
		except:
			pass

	d = Database()
	
	ts = d.getLastTimestamp(datetime(2000,1,1), datetime(2200,1,1))
	print ts
	
	def printTriggers():
		qTriggers = 'SELECT {} FROM trigger ORDER BY ts LIMIT 8'.format(','.join(d.triggerFieldsInput))
		print '*******************'
		for row in d.conn.execute(qTriggers):
			print removeDiacritic(u','.join( u'{}'.format(v) for v in row ))
	
	# Create existing duplicates all the triggers.
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
	
	print d.getTriggerDates()
	
		
	'''
	tsTriggers = [((time.sleep(0.1) and False) or now(), 100+i, u'', u'', u'', u'', u'') for i in xrange(100)]
	
	tsJpgs = [((time.sleep(0.01) and False) or now(), b'asdfasdfasdfasdfasdf') for i in xrange(100)]
	d.write( tsTriggers, tsJpgs )
	d.write( [], tsJpgs )
		
	print len(d.getTriggers( now() - timedelta(seconds=5), now() ))
	print len(d.getPhotos( now() - timedelta(seconds=5), now() ))
	'''
