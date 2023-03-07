import wx
from html import escape
import sys
import Model
import Utils

class Commentary( wx.Panel ):
	def __init__( self, parent, id = wx.ID_ANY ):
		super().__init__(parent, id, style=wx.BORDER_SUNKEN)
		
		self.SetDoubleBuffered(True)
		self.SetBackgroundColour( wx.WHITE )

		self.hbs = wx.BoxSizer(wx.HORIZONTAL)

		self.text = wx.TextCtrl( self, style=wx.TE_MULTILINE|wx.TE_READONLY )
		self.hbs.Add( self.text, 1, wx.EXPAND )
		self.SetSizer( self.hbs )
		
	def getText( self ):
		race = Model.race
		riderInfo = {info.bib:info for info in race.riderInfo} if race else {}

		def infoLinesSprint( sprint, bibs ):
			lines = []
			pfpText = ''
			for place_in, bib in enumerate(bibs,1):
				ri = riderInfo.get( bib, None )
				points, place, tie = race.getSprintPoints( sprint, place_in, bibs )
				if points:
					pfpText = ' ({:+d} pts)'.format(points)
				else:
					pfpText = ''
				if ri is not None:
					lines.append( '    {}.{}  {}: {} {}, {}'.format(place, pfpText, bib, ri.first_name, ri.last_name, ri.team) )
				else:
					lines.append( '    {}.{}  {}'.format(place, pfpText, bib) )
			return lines
		
		def infoLines( bibs, pointsForPlace=None ):
			lines = []
			pfpText = ''
			for place_in, bib in enumerate(bibs,1):
				ri = riderInfo.get( bib, None )
				points, place = pointsForPlace, place_in
				if points:
					pfpText = ' ({:+d} pts)'.format(points)
				else:
					pfpText = ''
				if ri is not None:
					lines.append( '    {}.{}  {}: {} {}, {}'.format(place, pfpText, bib, ri.first_name, ri.last_name, ri.team) )
				else:
					lines.append( '    {}.{}  {}'.format(place, pfpText, bib) )
			return lines
		
		RaceEvent = Model.RaceEvent
		lines = []
		self.sprintCount = 0
		
		def CommSprint( e ):
			self.sprintCount += 1
			lines.append( 'Sprint {} Result:'.format(self.sprintCount) )
			lines.extend( infoLinesSprint(self.sprintCount, e.bibs[:len(race.pointsForPlace)]) )

		def CommLapUp( e ):
			lines.append( 'Gained a Lap:' )
			lines.extend( infoLines(e.bibs, race.pointsForLapping) )

		def CommLapDown( e ):
			lines.append( 'Lost a Lap:' )
			lines.extend( infoLines(e.bibs, -race.pointsForLapping) )

		def CommFinish( e ):
			lines.append( 'Finish:' )
			self.sprintCount += 1
			lines.extend( infoLinesSprint(self.sprintCount, e.bibs) )

		def CommDNF( e ):
			lines.append( 'DNF (Did Not Finish):' )
			lines.extend( infoLines(e.bibs) )
			
		def CommDNS( e ):
			lines.append( 'DNS (Did Not Start):' )
			lines.extend( infoLines(e.bibs) )
			
		def CommPUL( e ):
			lines.append( 'PUL (Pulled by Race Officials):' )
			lines.extend( infoLines(e.bibs) )

		def CommDSQ( e ):
			lines.append( 'DSQ (Disqualified)' )
			lines.extend( infoLines(e.bibs) )

		CommEventHandler = {
			RaceEvent.Sprint:	CommSprint,
			RaceEvent.LapUp:	CommLapUp,
			RaceEvent.LapDown:	CommLapDown,
			RaceEvent.Finish:	CommFinish,
			RaceEvent.DNF:		CommDNF,
			RaceEvent.DNS:		CommDNS,
			RaceEvent.PUL:		CommPUL,
			RaceEvent.DSQ:		CommDSQ,
		}
		
		for e in race.events:
			if handler := CommEventHandler.get( e.eventType, None ):
				handler( e )
				lines.append( '' )
		
		return '\n'.join(lines)

	def toHtml( self, html ):
		text = self.getText().replace('.', '')
		if not text:
			return ''
		lines = []
		inList = False
		html.write( '<dl>' )
		for line in text.split('\n'):
			if not line:
				continue
			if line[:1] != ' ':
				if inList:
					html.write('</ol>\n')
					html.write('</dd>\n')
					inList = False
				html.write( '<dd>\n' )
				html.write( escape(line) )
				html.write( '<ol>' )
				inList = True
				continue
			line = line.strip()
			html.write( '<li>{}</li>\n'.format(line.split(' ',1)[1].strip()) )
		html.write('</ol>\n')
		html.write('</dd>\n')
		html.write('</dl>\n')
		
	def refresh( self ):
		self.text.Clear()
		self.text.AppendText( self.getText() )

	def commit( self ):
		pass
	
if __name__ == '__main__':
	app = wx.App( False )
	mainWin = wx.Frame(None,title="Commentary", size=(600,400))
	Model.newRace()
	Model.race._populate()
	rd = Commentary(mainWin)
	rd.refresh()
	rd.toHtml( sys.stdout )
	mainWin.Show()
	app.MainLoop()
