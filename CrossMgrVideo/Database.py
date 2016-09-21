import wx
import os
import time
from datetime import datetime, timedelta
import sqlite3
import StringIO

from Queue import Queue, Empty

now = datetime.now

def createTable( c, table, fields ):
	c.execute( 'CREATE TABLE IF NOT EXISTS {} ({})'.format(table, ','.join('{} {}'.format(field, type) for field, type, idx in fields ) ) )
	for field, type, idx in fields:
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
		
		if initTables:
			with self.conn:
				createTable( self.conn, 'photo', (
						('id', 'INTEGER PRIMARY KEY', False),
						('ts', 'timestamp', 'ASC'),
						('jpg', 'BLOB', False),
					)
				)		
				createTable( self.conn, 'trigger', (
						('id', 'INTEGER PRIMARY KEY', False),
						('ts', 'timestamp', 'ASC'),
						('bib', 'INTEGER', 'ASC'),
						('first_name', 'TEXT', 'ASC'),
						('last_name', 'TEXT', 'ASC'),
						('team', 'TEXT', 'ASC'),
						('wave', 'TEXT', 'ASC'),
						('race_name', 'TEXT', 'ASC'),
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
		tsJpgs = [(ts, jpg) for ts, jpg in tsJpgs if ts not in self.photoTsCache]
		
		if not tsTriggers and not tsJpgs:
			return
			
		with self.conn:
			if tsTriggers:
				self.conn.executemany( 'INSERT INTO trigger (ts,bib,first_name,last_name,team,wave,race_name) VALUES (?,?,?,?,?,?,?)', tsTriggers )
			if tsJpgs:
				self.conn.executemany( 'INSERT INTO photo (ts,jpg) VALUES (?,?)', tsJpgs )
		
		self.photoTsCache.update( ts for ts, jpg in tsJpgs )
		
		if (now() - self.lastUpdate).total_seconds() > self.UpdateSeconds:
			expired = now() - timedelta(seconds=self.UpdateSeconds)
			self.photoTsCache = set( ts for ts in self.photoTsCache if ts > expired )
			self.lastUpdate = now()
			
	def getTriggers( self, tsLower, tsUpper, bib=None ):
		with self.conn:
			if not bib:
				return list( self.conn.execute(
					'SELECT ts,bib,first_name,last_name,team,wave,race_name FROM trigger WHERE ts BETWEEN ? AND ? ORDER BY ts',
					(tsLower, tsUpper)
				))
			else:
				return list( self.conn.execute(
					'SELECT ts,bib,first_name,last_name,team,wave,race_name FROM trigger WHERE bib=? AND ts BETWEEN ? AND ? ORDER BY ts',
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
		
	def cleanBefore( self, tsUpper ):
		with self.conn:
			self.conn.execute( 'DELETE from photo WHERE ts < ?', (tsUpper,) )
			self.conn.execute( 'DELETE from trigger WHERE ts < ?', (tsUpper,) )
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
				v[2].SaveStream( outStream, wx.BITMAP_TYPE_JPEG )
				tsJpgs.append( (v[1], sqlite3.Binary(outStream.getvalue())) )
		elif v[0] == 'trigger':
			tsTriggers.append( (list(v[1:]) + [u''] * 6)[:7] )
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
	try:
		os.remove( os.path.join( os.path.expanduser("~"), 'CrossMgrVideo.sqlite3' ) )
	except:
		pass

	d = Database()
	
	ts = d.getLastTimestamp(datetime(2000,1,1), datetime(2200,1,1))
	print ts
	
	d.cleanBefore( ts )
	
	'''
	tsTriggers = [((time.sleep(0.1) and False) or now(), 100+i, u'', u'', u'', u'', u'') for i in xrange(100)]
	
	tsJpgs = [((time.sleep(0.01) and False) or now(), b'asdfasdfasdfasdfasdf') for i in xrange(100)]
	d.write( tsTriggers, tsJpgs )
	d.write( [], tsJpgs )
		
	print len(d.getTriggers( now() - timedelta(seconds=5), now() ))
	print len(d.getPhotos( now() - timedelta(seconds=5), now() ))
	'''
