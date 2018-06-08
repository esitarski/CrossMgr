import wx
import sys
import os
import numpy as np

sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__))) )
from QuadReg import QuadRegRemoveOutliersRobust, QuadRegRemoveOutliersRansac
import re

colorTable = '''
Red	#e6194b	(230, 25, 75)	(0, 100, 66, 0)
Green	#3cb44b	(60, 180, 75)	(75, 0, 100, 0)
Blue	#0082c8	(0, 130, 200)	(100, 35, 0, 0)
Orange	#f58231	(245, 130, 48)	(0, 60, 92, 0)
Purple	#911eb4	(145, 30, 180)	(35, 70, 0, 0)
Cyan	#46f0f0	(70, 240, 240)	(70, 0, 0, 0)
Magenta	#f032e6	(240, 50, 230)	(0, 100, 0, 0)
Lime	#d2f53c	(210, 245, 60)	(35, 0, 100, 0)
Pink	#fabebe	(250, 190, 190)	(0, 30, 15, 0)
Teal	#008080	(0, 128, 128)	(100, 0, 0, 50)
Lavender	#e6beff	(230, 190, 255)	(10, 25, 0, 0)
Brown	#aa6e28	(170, 110, 40)	(0, 35, 75, 33)
Beige	#fffac8	(255, 250, 200)	(5, 10, 30, 0)
Maroon	#800000	(128, 0, 0)	(0, 100, 100, 50)
Mint	#aaffc3	(170, 255, 195)	(33, 0, 23, 0)
Olive	#808000	(128, 128, 0)	(0, 0, 100, 50)
Coral	#ffd8b1	(255, 215, 180)	(0, 15, 30, 0)
Navy	#000080	(0, 0, 128)	(100, 100, 0, 50)
Grey	#808080	(128, 128, 128)	(0, 0, 0, 50)
'''
colors = []
for c in colorTable.split('\n'):
	c = c.strip()
	if not c:
		continue
	ct = c[c.find('(')+1:c.find(')')]
	r, g, b = [int(v) for v in ct.split(',')]
	colors.append( wx.Colour(r, g, b) )

def readData( fname ):
	data = {}
	tMin, tMax = 1000*24*60*60.0, -1000*24*60*60.0
	dbMin, dbMax = 1000, -1000
	with open(fname, 'r') as fp:
		for line in fp:
			line = line.strip()
			
			''' Reader,EPC,FirstTime,LastTime,BestTime,PeakRSSI (-DB*10),RFPhaseAngle,DopplerFreq (Hz),TagSeenCount,Det,Alg,Err '''
			if not line[0].isdigit():
				continue
			fields = line.split(',')
			
			Reader = int(fields[0])			
			EPC = fields[1]
			t = fields[3]
			t = int(t[:2]) * 60 * 60 + int(t[2:4]) * 60 + float(t[4:])
			db = -float(fields[5]) / 10.0
			if db < -85 or db > -10:
				continue

			dbMin = min( dbMin, db )
			dbMax = max( dbMax, db )
			tMin = min( t, tMin )
			tMax = max( t, tMax )
			
			key = (Reader, EPC)
			if key in data:
				if t - data[key][-1][-1][0] > 0.5:
					data[key].append( [] )
				data[key][-1].append( (t, db) )
			else:
				data[key] = [[(t, db)]]
	
	return {'tMin':tMin, 'tMax':tMax, 'dbMin':dbMin, 'dbMax':dbMax, 'data':data}

class PlotPanel( wx.Panel ):
	def __init__(self, parent):
		super(PlotPanel, self).__init__(parent)
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
		self.Bind(wx.EVT_SIZE, self.onSize)
		self.Bind(wx.EVT_PAINT, self.onPaint)
		self.Bind(wx.EVT_MOUSEWHEEL, self.onMouseWheel)
		self.Bind(wx.EVT_LEFT_UP, self.onMouseClick)
		self.Bind(wx.EVT_RIGHT_UP, self.onMouseClick)
	
	def onSize(self, event):
		event.Skip()
		self.Refresh()
		
	def onMouseWheel( self, event ):
		self.setTLeft( self.tLeft + event.GetWheelRotation()/8.0 )
		
	def onMouseClick( self, event ):
		if event.Button( wx.MOUSE_BTN_LEFT ):
			self.iBreak -= 1
			if self.iBreak < 0:
				self.iBreak = 0
		elif event.Button( wx.MOUSE_BTN_RIGHT ):
			self.iBreak += 1
			if self.iBreak >= len(self.iBreakTime):
				self.iBreak = len(self.iBreakTime)-1
		
		self.setTLeft( self.tAll[self.iBreakTime[self.iBreak]] - 0.1 )
		self.Refresh()
	
	def onPaint(self, event):
		w, h = self.GetClientSize()
		dc = wx.AutoBufferedPaintDC(self)
		dc.SetBackground( wx.WHITE_BRUSH )
		dc.Clear()
		
		#fontHeight = max( h//40, 5 )
		#dc.SetFont( wx.Font(wx.FontInfo((0, fontHeight))) )
		
		tScale = 2000000 / (self.data['tMax'] - self.data['tMin'])
		dbScale = h / (self.data['dbMax'] - self.data['dbMin'])
		
		def tToX( t ):
			return int((t - self.tLeft) * tScale + 0.5)
			
		def dbToY( db ):
			return h - int((db-self.data['dbMin']) * dbScale + 0.5)
		
		iCount = 0
		for (reader, EPC), coords in self.data['data'].iteritems():
			for coordsCur in coords:
				if len(coordsCur) < 3 or tToX(coordsCur[0][0]) > w or tToX(coordsCur[-1][0]) < 0:
					continue
				#abc, inliers, outliers = QuadRegRemoveOutliersRobust( coordsCur, True )
				abc, inliers, outliers = QuadRegRemoveOutliersRansac( coordsCur, True )
					
				if abc is not None:
					p = np.poly1d( abc )
					a, b, c = abc
					apex_t = -b / (2.0 * a)
					apex_db = p( apex_t )
				else:
					if len(coordsCur) & 1 == 1:
						iMedian = len(coordsCur) // 2
						apex_t, apex_db = coordsCur[iMedian]
						inliers = [coordsCur[iMedian]]
						outliers = [v for v in coordsCur if v not in inliers]
					else:
						iMedian = len(coordsCur) // 2
						apex_t, apex_db = (coordsCur[iMedian][0] + coordsCur[iMedian-1][0]) / 2.0, (coordsCur[iMedian][1] + coordsCur[iMedian-1][1]) / 2.0
						inliers = [coordsCur[iMedian-1], coordsCur[iMedian]]
						outliers = [v for v in coordsCur if v not in inliers]
				
				col = colors[(int(EPC, 16)+reader) % len(colors)]
				dc.SetPen( wx.TRANSPARENT_PEN )
				dc.SetBrush( wx.Brush(col) )
				for t, db in inliers:
					x, y = tToX(t), dbToY(db)
					if x > 0 and x < w and y > 0 and y < h:
						dc.DrawCircle( x, y, 4 )
					
				dc.SetPen( wx.Pen(col) )
				dc.SetBrush( wx.WHITE_BRUSH )
				for t, db in outliers:
					x, y = tToX(t), dbToY(db)
					if x > 0 and x < w and y > 0 and y < h:
						dc.DrawCircle( x, y, 4 )
				
				if abc is not None:
					dc.SetPen( wx.Pen(wx.Colour(160,160,160) ) )
					points = []
					#for x in xrange( tToX(coordsCur[0][0]), tToX(coordsCur[-1][0])+1 ):
					for x in xrange( tToX(inliers[0][0]), tToX(inliers[-1][0])+1 ):
						t = (x / tScale) + self.tLeft
						y = dbToY(p(t))
						if x > 0 and x < w and y > 0 and y < h:
							points.append( wx.Point(x, dbToY(p(t)) ) )
					dc.DrawLines( points )
				
				#dc.SetPen( wx.Pen(wx.Colour(160,160,160)) )
				dc.SetPen( wx.Pen(wx.Colour(255,165,0)) )
				dc.DrawLine( tToX(apex_t), h, tToX(apex_t), dbToY(apex_db) )
				
				#dc.DrawText( EPC, tToX(apex_t), h - fontHeight * (iCount%4) )
				#iCount += 1

	def setData( self, data ):
		self.data = data
		self.setTLeft( data['tMin'] )
		self.tAll = []
		for (reader, EPC), coords in self.data['data'].iteritems():
			for c in coords:
				self.tAll.extend( [t for t, db in c] )
		self.iTime = 0
		self.tAll.sort()
		self.iBreakTime = [0]
		for i in xrange(len(self.tAll)-1):
			if self.tAll[i+1] - self.tAll[i] > 0.25:
				self.iBreakTime.append( i+1 )
		self.iBreak = 0
		
	def setTLeft(self, t):
		self.tLeft = t
		self.Refresh()

class PlotFrame( wx.Frame ):
	def __init__( self, parent, title, id=wx.ID_ANY, size=wx.DefaultSize ):
		super(PlotFrame, self).__init__(parent, id, title=title)
		self.plot = PlotPanel( self )
		
		vb = wx.BoxSizer( wx.VERTICAL )
		vb.Add( self.plot, 1, flag=wx.EXPAND )
		self.SetSizer( vb )
		
	def setData( self, data ):
		self.data = data
		self.plot.setData( data )
	
def MainLoop():
	app = wx.App(False)
	app.SetAppName("QRPlot")
	mainWin = PlotFrame( None, title='QRPlot', size=(800,min(int(wx.GetDisplaySize()[1]*0.85),1000)) )
	mainWin.setData( readData('Impinj-2018-05-29-18-12-21.txt') )
	mainWin.Show()
	app.MainLoop()

if __name__ == '__main__':
	MainLoop()
	
	
