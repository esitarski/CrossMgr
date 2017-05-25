import re
import os
import glob
import shutil
import tempfile
import subprocess
import sqlite3
import platform
import datetime
from PIL import Image
import StringIO
from Database import Database

def MPegToDatabase( fnameMPeg, tRecorded=None ):
	program = os.path.join('ffmpeg','ffmpeg.exe') if platform.system() == 'Windows' else 'ffmpeg'
	
	# Get fps.
	p = subprocess.Popen( args=(program, '-i', fnameMPeg), stdout=subprocess.PIPE, stderr=subprocess.PIPE )
	info = '   '.join( p.communicate() )
	m = re.search(r'(\d+) fps,', info)
	fps = int(m.group(1)) if m else 25

	# Create a temporary directory for the extracted frames.
	tmpdir = tempfile.mkdtemp( prefix='MPegToDB' )
	
	# Convert mpeg to set of jpeg frames, one jpeg per file.
	fnameBase = os.path.splitext(os.path.basename(fnameMPeg))[0]
	subprocess.call( [
		program,
		'-i', fnameMPeg, '-r', '{}/1'.format(fps), '{}/{}_%05d.jpeg'.format(tmpdir, fnameBase)
	] )
	
	# Store the frames in the database.  Set a frame timestamp.
	database = Database()
	secsPerFrame = 1.0 / fps
	dt = datetime.timedelta( seconds = secsPerFrame )
	tStart = t = (tRecorded or datetime.datetime.now())
	tsJpgs = []
	bytesBuffer = 0
	for fname in sorted( glob.glob(os.path.join(tmpdir, '*.jpeg')), key=lambda s: int(re.search(r'_(\d+)\.jpeg$', s).group(1)) ):
		with open(fname, 'rb') as f:
			tsJpgs.append( (t, sqlite3.Binary(f.read())) )
		t += dt
		bytesBuffer += len(tsJpgs[-1][1])
		if bytesBuffer > 20000000:
			database.write( tsJpgs=tsJpgs )
			del tsJpgs[:]
			bytesBuffer = 0
			
	database.write( tsJpgs=tsJpgs )
	del tsJpgs[:]
	
	ts = tStart + datetime.timedelta( seconds = (t - tStart).total_seconds()/2.0 )
	print tStart, ts, t
	#          ts,bib,first_name,last_name,team,wave,race_name
	trigger = (ts,  1,   '',     fnameMPeg,  '',  '','Test'  )
	database.write( tsTriggers=[trigger] )
	shutil.rmtree( tmpdir, ignore_errors=True )

if __name__ == '__main__':
	MPegToDatabase( os.path.join('bugs', '290 Jacob Lifson.mpeg') )
