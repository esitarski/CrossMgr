import os
import math

def formatTime( secs ):
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = secs // (60*60)
	minutes = (secs // 60) % 60
	secStr = '{:06.3f}'.format( secs%60 + f ).replace('.', '-')
	return "{:02d}-{:02d}-{}".format(hours, minutes, secStr)

def GetPhotoFName( dirName, bib, raceSeconds, i ):
	return os.path.join(dirName, 'bib-{:04d}-time-{}-{}.jpg'.format(int(bib or 0), formatTime(raceSeconds or 0), i+1))
