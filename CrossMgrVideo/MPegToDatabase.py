import os
import glob
import shutil
import subprocess
import sqlite3
import datetime
from PIL import Image
import StringIO
from Database import Database

def MPegToDatabase( fnameMPeg ):
	shutil.rmtree( 'frames', ignore_errors=True )
	os.mkdir( 'frames' )
	
	fnameBase = os.path.splitext(os.path.basename(fnameMPeg))[0]
	subprocess.call( [
		os.path.join('ffmpeg','ffmpeg.exe'),
		'-i', fnameMPeg, '-r', '24/1', 'frames/{}_%04d.bmp'.format(fnameBase)
	] )
	
	database = Database()
	fps = 24.0
	secsPerFrame = 1 / fps
	dt = datetime.timedelta( seconds = secsPerFrame )
	tStart = datetime.datetime.now()
	t = datetime.datetime.now()
	for fname in sorted( glob.glob(os.path.join('frames', '*.bmp')) ):
		print 'adding:', fname
		image = Image.open( fname )
		jpgIO = StringIO.StringIO()
		image.save( jpgIO, 'jpeg' )
		database.write( tsJpgs=[(t, sqlite3.Binary(jpgIO.getvalue()))] )
		t += dt
	
	ts = tStart + datetime.timedelta( seconds = (t - tStart).total_seconds()/2.0 )
	print tStart, ts, t
	#          ts,bib,first_name,last_name,team,wave,race_name
	trigger = (ts,  1,   '',     fnameMPeg,  '',  '','Test'  )
	database.write( tsTriggers=[trigger] )
	#shutil.rmtree( 'frames', ignore_errors=True )

if __name__ == '__main__':
	MPegToDatabase( os.path.join('bugs', '290 Jacob Lifson.mpeg') )