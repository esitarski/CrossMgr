import re
import datetime
import xml.sax

reGpxTime = re.compile( '[^0-9+.]' )

class GpxContentHandler( xml.sax.ContentHandler ):
	def __init__( self ):
		xml.sax.ContentHandler.__init__( self )
		self.reset()
		
	def reset( self ):
		self.fields = {}
		self.fieldCur = None
		self.trkCount = 0
		self.points = []
		
	def startElement( self, name, attr ):
		if name in ['trkpt', 'rtept']:
			self.fields = {'lat': float(attr.getValue('lat')), 'lon': float(attr.getValue('lon')) }
		elif name in ['ele', 'time']:
			self.fieldCur = name
		elif name == 'trk':
			self.trkCount += 1
		
	def characters( self, content ):
		if   self.fieldCur == 'ele':
			self.fields['ele'] = float( content.strip() )
			self.fieldCur = None
		elif self.fieldCur == 'time':
			try:
				self.fields['time'] = datetime.datetime( *[int(f) for f in reGpxTime.split(content.strip()) if f] )
			except:
				pass
			self.fieldCur = None
				
	def endElement( self, name ):
		if name in ['trkpt', 'rtept'] and self.trkCount <= 1 and 'lat' in self.fields and 'lon' in self.fields:
			self.points.append( self.fields )

def GpxParse( fname ):
	gpxCH = GpxContentHandler()
	with open(fname) as f:
		xml.sax.parse( f, gpxCH )
	return gpxCH.points
	
if __name__ == '__main__':
	points = GpxParse( 'Seymour_Smith_Cyclocross_Course.gpx' )