import wx
import wx.adv as adv
import StringIO
import datetime
from ScaledImageVerticalLines import ScaledImageVerticalLines, EVT_VERTICAL_LINES
from Utils import formatTime

_ = lambda x: x

class WheelEdgesPage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		
		self.t = None
		self.wheelDiameter = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.sivl = ScaledImageVerticalLines( self, numLines=2, colors=(wx.Colour(255, 0, 0), wx.Colour(0, 255, 0)) )
		vbs.Add( self.sivl, 1, wx.EXPAND|wx.ALL, border=border)
		vbs.Add( wx.StaticText(self, label = _('1.  Drag the Green Square so the line is on the Leading Edge of the Front Wheel.')),
					flag=wx.TOP|wx.LEFT|wx.RIGHT, border = border )
		vbs.Add( wx.StaticText(self, label = _('2.  Drag the Red Square so the line is on the Trailing edge of the Front Wheel.')),
					flag=wx.BOTTOM|wx.LEFT|wx.RIGHT, border = border )
		self.explain = wx.StaticText( self )
		vbs.Add( self.explain, flag=wx.ALL, border = border )
		self.SetSizer( vbs )
		
	def setExplain( self ):
		self.explain.SetLabel(
			'The wheel in this frame (taken at {}) establishes a reference distance of {}m.'.format(
				self.t.strftime('%H:%M:%S.%f')[:-3] if self.t else 'None',
				'{:.3f}'.format(self.wheelDiameter) if self.wheelDiameter else 'None',
			)
		)
		self.GetSizer().Layout()
		
	def Set( self, t, image, wheelDiameter ):
		self.t = t
		self.wheelDiameter = wheelDiameter
		self.sivl.SetImage( image )
		self.setExplain()
	
	def getWheelEdges( self ):
		return self.sivl.GetVerticalLines()
	
class FrontWheelEdgePage(adv.WizardPageSimple):
	def __init__(self, parent, getSpeed):
		adv.WizardPageSimple.__init__(self, parent)
		
		self.getSpeed = getSpeed
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.sivl = ScaledImageVerticalLines( self, numLines=1, colors=(wx.Colour(0, 255, 0),) )
		self.sivl.Bind( EVT_VERTICAL_LINES, self.onVerticalLines )
		vbs.Add( self.sivl, 1, wx.EXPAND|wx.ALL, border=border)
		vbs.Add( wx.StaticText(self, label = _('Drag the Green Square so the line is on the Leading Edge of the Front Wheel.')),
					flag=wx.ALL, border = border )
		self.speed = wx.StaticText( self )
		bigFont = wx.Font( (0,32), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		self.speed.SetFont( bigFont )
		vbs.Add( self.speed, flag=wx.ALL, border = border )
		self.SetSizer( vbs )
		
	def onVerticalLines( self, event=None ):
		mps, kmh, mph, pps = self.getSpeed()
		if mps is None:
			mps = kmh = mph = pps = 0.0
		s = u'{:.2f}km/h   {:.2f}m/s   {:.2f}mph'.format(kmh, mps, mph)
		self.speed.SetLabel( s )
		self.GetSizer().Layout()
		
	def Set( self, t, image, wheelDiameter ):
		self.t = t
		self.wheelDiameter = wheelDiameter
		self.sivl.SetImage( image )
		self.onVerticalLines()
	
	def getFrontWheelEdge( self ):
		return self.sivl.GetVerticalLines()[0]
	
class TimePage(adv.WizardPageSimple):
	def __init__(self, parent):
		adv.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.sivl = ScaledImageVerticalLines( self, numLines=1, colors=(wx.Colour(255,0,255),) )
		self.sivl.Bind( EVT_VERTICAL_LINES, self.onVerticalLines )
		vbs.Add( self.sivl, 1, wx.EXPAND|wx.ALL, border=border)
		vbs.Add( wx.StaticText(self,
			label = _("Drag the Purple Square to show the Time in the photo.")),
			flag=wx.ALL, border = border
		)
		self.speed = wx.StaticText( self )
		bigFont = wx.Font( (0,32), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		self.speed.SetFont( bigFont )
		vbs.Add( self.speed, flag=wx.ALL, border = border )
		self.SetSizer( vbs )
		
	def onVerticalLines( self, event=None ):
		try:
			t = self.tImage + datetime.timedelta(
				seconds=self.direction * (self.getPosition() - self.frontWheelEdge) / self.pixelsPerSecond
			)
		except Exception as e:
			return
		secs = (t - self.tStart).total_seconds()
		self.speed.SetLabel( formatTime(secs, True) )
		self.GetSizer().Layout()
		
	def Set( self, image, tImage, tStart, frontWheelEdge, pixelsPerSecond, leftToRight ):
		self.sivl.SetImage( image )
		self.tImage = tImage
		self.tStart = tStart
		self.frontWheelEdge = frontWheelEdge
		self.pixelsPerSecond = pixelsPerSecond
		self.direction = 1.0 if leftToRight else -1.0
		self.onVerticalLines()
	
	def getPosition( self ):
		return self.sivl.GetVerticalLines()[0]
	
class ComputeSpeed( object ):
	wheelDiameter = 0.678

	def __init__( self, parent, size=wx.DefaultSize ):
		self.wizard = adv.Wizard( parent, wx.ID_ANY, _('Compute Speed') )
		self.wizard.Bind( adv.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		
		self.t1 = None
		self.t2 = None
		self.image1 = None
		self.image2 = None
		
		self.wheelEdgesPage = WheelEdgesPage( self.wizard )
		self.frontWheelEdgePage = FrontWheelEdgePage( self.wizard, self.getSpeed )
		self.timePage = TimePage( self.wizard )
		
		adv.WizardPageSimple.Chain( self.wheelEdgesPage, self.frontWheelEdgePage )
		adv.WizardPageSimple.Chain( self.frontWheelEdgePage, self.timePage )

		self.wizard.SetPageSize( size )
		self.wizard.GetPageAreaSizer().Add( self.wheelEdgesPage )
		self.wizard.FitToPage( self.wheelEdgesPage )
	
	def getSpeed( self ):
		wheelTrailing, wheelLeading = self.wheelEdgesPage.getWheelEdges()
		frontWheelEdge = self.frontWheelEdgePage.getFrontWheelEdge()
		if wheelTrailing is None or wheelLeading is None or frontWheelEdge is None:
			return None, None, None, None
		
		dSeconds = max(0.0001, (self.t2 - self.t1).total_seconds())
		
		wheelPixels = max( 1.0, abs(wheelLeading - wheelTrailing) )
		metersPerPixel = self.wheelDiameter / wheelPixels
		dPixels = abs(frontWheelEdge - wheelLeading)
		metersPerSecond = dPixels * metersPerPixel / dSeconds
		pixelsPerSecond = dPixels / dSeconds
		return metersPerSecond, metersPerSecond*3.6, metersPerSecond*2.23694, pixelsPerSecond
		
	def Show( self, image1, t1, image2, t2, ts_start ):
		self.t1, self.t2, self.ts_start = t1, t2, ts_start
		self.image1, self.image2 = image1, image2
		self.wheelEdgesPage.Set( t1, image1, self.wheelDiameter )
		self.frontWheelEdgePage.Set( t2, image2, self.wheelDiameter )
		self.timePage.Set( self.image2, self.t2, self.ts_start, 0.0001, 1, True )
	
		if self.wizard.RunWizard(self.wheelEdgesPage):
			return self.getSpeed()
			
		return None, None, None, None
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		if isForward:
			page = evt.GetPage()
			if page == self.wheelEdgesPage:
				self.frontWheelEdgePage.sivl.verticalLines = [self.wheelEdgesPage.sivl.verticalLines[1]]
			elif page == self.frontWheelEdgePage:
				v = self.wheelEdgesPage.sivl.verticalLines
				self.timePage.Set(
					self.image2, self.t2, self.ts_start,
					self.frontWheelEdgePage.getFrontWheelEdge(),
					self.getSpeed()[3],		# pixels per second
					v[0] < v[1],
				)
				self.timePage.sivl.ratio = self.frontWheelEdgePage.sivl.ratio
				self.timePage.sivl.verticalLines = [self.frontWheelEdgePage.sivl.verticalLines[0]]
				self.timePage.onVerticalLines()
			
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
if __name__ == '__main__':
	from Database import Database

	tsJpgs = Database().getLastPhotos( 12 )
	t1, t2 = tsJpgs[0][0], tsJpgs[-1][0]
	image1 = wx.Image( StringIO.StringIO(tsJpgs[0][1]), wx.BITMAP_TYPE_JPEG )
	image2 = wx.Image( StringIO.StringIO(tsJpgs[-1][1]), wx.BITMAP_TYPE_JPEG )

	app = wx.App(False)
	mainWin = wx.Frame(None,title="ComputeSpeed", size=(600,300))
	size=image1.GetSize()
	size = (800,600)
	computeSpeed = ComputeSpeed(mainWin, size=size)
	mainWin.Show()
	mps, kmh, mph, pps = computeSpeed.Show( image1, t1, image2, t2, t2 )
	print 'm/s={}, km/h={}, mph={} pps={}'.format(mps, kmh, mph, pps)
	app.MainLoop()
