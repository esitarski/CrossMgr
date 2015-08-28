import os
import math
import datetime

epoch = datetime.datetime.utcfromtimestamp(0.0)

def formatTime( secs ):
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = secs // (60*60)
	minutes = (secs // 60) % 60
	secStr = '{:06.3f}'.format( secs%60 + f ).replace('.', '-')
	return "{:02d}-{:02d}-{}".format(hours, minutes, secStr)

def base36encode( number ):
	digits = []
	while number:
		digits.append( '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[number % 36] )
		number //= 36
	return ''.join(digits)[::-1] or '0'

def ParsePhotoFName( fname ):
	fname = os.path.splitext(os.path.basename(fname))[0]
	fields = fname.split( '-' )
	
	bib = int(fields[1])
	hour, minute, second, decimal = fields[3:7]
	raceTime = float(hour)*(60.0*60.0) + float(minute)*60.0 + float(second) + float(decimal)/(10**len(decimal))
	count = int(fields[-1])
	photoTime = datetime.datetime.fromtimestamp(int(fields[7], 36) / 10000.0) if len(fields) >= 9 else None
	return bib, raceTime, count, photoTime

def GetPhotoFName( dirName, bib, raceSeconds, i, photoTime ):
	return os.path.join(dirName, 'bib-{:04d}-time-{}-{}-{}.jpg'.format(
		int(bib or 0),
		formatTime(raceSeconds or 0),
		base36encode(int((photoTime - epoch).total_seconds()*10000)),	# in 1/10,000s of a second since 1970, base 36.
		i+1 )
	)
