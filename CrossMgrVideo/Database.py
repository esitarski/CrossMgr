import wx
import os
import time
from datetime import datetime, timedelta
import sqlite3
import StringIO

from Queue import Queue, Empty

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

	def __init__( self, fname=None, initTables=True, fps=25 ):
		self.fname = (fname or os.path.join( os.path.expanduser("~"), 'CrossMgrVideo.sqlite3' ) )
		self.fps = fps
		
		'''
		try:
			print 'database bytes: {}'.format( os.stat(self.fname).st_size )
		except:
			pass
		'''
		
		self.conn = sqlite3.connect( self.fname, detect_types=sqlite3.PARSE_DECLTYPES )
		
		# Add kmh and ts_start to the trigger table if necessary.
		with self.conn:
			cur = self.conn.cursor()
			cur.execute( 'PRAGMA table_info(trigger)' )
			cols = cur.fetchall()
			if cols and not any( col[1] == 'kmh' for col in cols ):
				self.conn.execute( 'ALTER TABLE trigger ADD COLUMN kmh DOUBLE DEFAULT 0.0' )
			if cols and not any( col[1] == 'ts_start' for col in cols ):
				tNow = now()
				self.conn.execute( 'ALTER TABLE trigger ADD COLUMN ts_start timestamp DEFAULT ?', (tNow,) )
				#ts_id = list( self.conn.execute( 'SELECT ts,id from trigger' ))
				#self.conn.executemany( 'UPDATE trigger SET ts_start=? WHERE id=?', ts_id )
				#del ts_id
				self.conn.execute( 'UPDATE trigger SET ts_start=ts' )
		
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
						('ts', 'timestamp', 'ASC', None),
						('ts_start', 'timestamp', False, None),
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

	def getsize( self ):
		try:
			return os.path.getsize( self.fname )
		except:
			return None
		
	def write( self, tsTriggers=None, tsJpgs=None ):
		if not tsTriggers and not tsJpgs:
			return
		
		if tsJpgs:
			tsJpgs = [(ts, jpg) for ts, jpg in tsJpgs if ts not in self.photoTsCache]
		
		with self.conn:
			if tsTriggers:
				self.conn.executemany( 'INSERT INTO trigger (ts,ts_start,bib,first_name,last_name,team,wave,race_name) VALUES (?,?,?,?,?,?,?,?)', tsTriggers )
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
	
	def getTriggers( self, tsLower, tsUpper, bib=None ):
		with self.conn:
			if not bib:
				return list( self.conn.execute(
					'SELECT id,ts,ts_start,bib,first_name,last_name,team,wave,race_name,kmh FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts',
					(tsLower, tsUpper)
				))
			else:
				return list( self.conn.execute(
					'SELECT id,ts,ts_start,bib,first_name,last_name,team,wave,race_name,kmh FROM trigger WHERE bib=? AND ts BETWEEN ? AND ? ORDER BY ts',
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
		c.execute( 'SELECT max(ts) from trigger WHERE ts BETWEEN ? AND ?', (tsLower, tsUpper) )
		return c.fetchone()[0]
	
	def isDup( self, ts ):
		return ts in self.photoTsCache
		
	def cleanBetween( self, tsLower, tsUpper ):
		if not tsLower and not tsUpper:
			return
	
		if tsLower is None:
			with self.conn:
				self.conn.execute( 'DELETE from photo WHERE ts <= ?', (tsUpper,) )
				self.conn.execute( 'DELETE from trigger WHERE ts <= ?', (tsUpper,) )
		elif tsUpper is None:
			with self.conn:
				self.conn.execute( 'DELETE from photo WHERE ts >= ?', (tsLower,) )
				self.conn.execute( 'DELETE from trigger WHERE ts >= ?', (tsLower,) )
		else:
			with self.conn:
				self.conn.execute( 'DELETE from photo WHERE ts BETWEEN ? AND ?', (tsLower,tsUpper) )
				self.conn.execute( 'DELETE from trigger WHERE ts BETWEEN ? AND ?', (tsLower,tsUpper) )
			
		with self.conn:
			self.conn.execute( 'VACUUM' )
		
def DBWriter( q, fps=25 ):
	db = Database( fps=fps )
	tsJpgs = []
	tsTriggers = []
	
	def flush():
		db.write( tsTriggers, tsJpgs )
		del tsTriggers[:]
		del tsJpgs[:]
		
	keepGoing = True
	while keepGoing:
		try:
			v = q.get( timeout=1 )
		except Empty:
			if tsTriggers or tsJpgs:
				flush()
			continue
			
		if v[0] == 'photo':
			if not db.isDup( v[1] ):
				outStream = StringIO.StringIO()
				v[2].SaveFile( outStream, wx.BITMAP_TYPE_JPEG )
				tsJpgs.append( (v[1], sqlite3.Binary(outStream.getvalue())) )
		elif v[0] == 'trigger':
			tsTriggers.append( (list(v[1:]) + [u''] * 6)[:7] )
		elif v[0] == 'kmh':
			db.updateTriggerKMH( v[1], v[2] )	# id, kmh
		elif v[0] == 'flush':
			flush()
		elif v[0] == 'terminate':
			flush()
			keepGoing = False
		
		q.task_done()
		
		if len(tsJpgs) >= db.fps*4:
			flush()
	flush()
	
def DBReader( q, callback ):
	db = Database( initTables=False )
	
	keepGoing = True
	while keepGoing:
		v = q.get()
		if v[0] == 'getphotos':
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
	
	'''
	tsTriggers = [((time.sleep(0.1) and False) or now(), 100+i, u'', u'', u'', u'', u'') for i in xrange(100)]
	
	tsJpgs = [((time.sleep(0.01) and False) or now(), b'asdfasdfasdfasdfasdf') for i in xrange(100)]
	d.write( tsTriggers, tsJpgs )
	d.write( [], tsJpgs )
		
	print len(d.getTriggers( now() - timedelta(seconds=5), now() ))
	print len(d.getPhotos( now() - timedelta(seconds=5), now() ))
	'''
