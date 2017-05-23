import re
import os
import glob
import shutil
import subprocess
import sqlite3
import platform
import datetime
from PIL import Image
import StringIO
from Database import Database

def MPegToDatabase( fnameMPeg ):
	shutil.rmtree( 'frames', ignore_errors=True )
	os.mkdir( 'frames' )
	
	program = os.path.join('ffmpeg','ffmpeg.exe') if platform.system() == 'Windows' else 'ffmpeg'
	
	p = subprocess.Popen( args=(program, '-i', fnameMPeg), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	info = '   '.join( p.communicate() )
	m = re.search(r'(\d+) fps,', info)
	fps = int(m.group(1)) if m else 25
	
	fnameBase = os.path.splitext(os.path.basename(fnameMPeg))[0]
	subprocess.call( [
		program,
		'-i', fnameMPeg, '-r', '{}/1'.format(fps), 'frames/{}_%04d.jpeg'.format(fnameBase)
	] )
	
	database = Database()
	fps = 24.0
	secsPerFrame = 1.0 / fps
	dt = datetime.timedelta( seconds = secsPerFrame )
	tStart = datetime.datetime.now()
	t = datetime.datetime.now()
	tsJpgs = []
	for fname in sorted( glob.glob(os.path.join('frames', '*.jpeg')) ):
		print t.strftime( '%Y-%m-%d %H:%M:%S.%f' ), fname
		with open(fname, 'rb') as f:
			tsJpgs.append( (t, sqlite3.Binary(f.read())) )
		t += dt
		if len(tsJpgs) == 50:
			database.write( tsJpgs=tsJpgs )
			del tsJpgs[:]
			
	database.write( tsJpgs=tsJpgs )
	del tsJpgs[:]
	
	ts = tStart + datetime.timedelta( seconds = (t - tStart).total_seconds()/2.0 )
	print tStart, ts, t
	#          ts,bib,first_name,last_name,team,wave,race_name
	trigger = (ts,  1,   '',     fnameMPeg,  '',  '','Test'  )
	database.write( tsTriggers=[trigger] )
	shutil.rmtree( 'frames', ignore_errors=True )

if __name__ == '__main__':
	MPegToDatabase( os.path.join('bugs', '290 Jacob Lifson.mpeg') )
