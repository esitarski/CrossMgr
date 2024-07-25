import glob
import datetime
from TagGroup import TagGroup, QuadraticRegressionMethod

def Test():
	method = QuadraticRegressionMethod
	#method = StrongestReadMethod

	for file in sorted(glob.glob('data/*.txt')):
		tg = TagGroup()
		tNow = datetime.datetime.now()
		tFirst = None
		tLast = 0.0
		
		# 10.16.21.147,738AD3FF13CFD7C9F62F029D,123132.461593,0,-52
		with open(file, 'r') as pf:
			for line in pf:
				if line.startswith('127.'):
					continue
				fields = [f.strip() for f in line.split(',')]
				if len(fields) != 5:
					continue
				try:
					tagID = fields[1]
					t     = float(fields[2])
					db    = int(fields[4])
				except Exception:
					continue
				
				if tFirst is None: tFirst = t
				if t > tLast: tLast = t
				tg.add( 1, tagID, tNow + datetime.timedelta(seconds=t - tFirst), db )
		
		reads, strays = tg.getReadsStrays( tNow + datetime.timedelta( seconds = tLast - tFirst + 1.0), method )
		print( '************************************************' )
		print( '    {}'.format( file ) )
		print( '************************************************' )
		for tagID, t, sampleSize, antennaID in reads:
			print( tagID, t.strftime('%H:%M:%S.%f'), sampleSize )
			
		break
				
if __name__ == '__main__':
	Test()
