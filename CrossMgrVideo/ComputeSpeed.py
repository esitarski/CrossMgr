import wx
import wx.adv as adv
from ScaledBitmapVerticalLines import ScaledBitmapVerticalLines, EVT_VERTICAL_LINES
import CVUtil

_ = lambda x: x

class WheelEdgesPage(adv.WizardPageSimple):
	def __init__(self, parent):
		super().__init__(parent)
		
		self.tsJpg, self.iPhoto1, self.iPhoto2 = None, None, None
		self.wheelDiameter = None
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.sbvl = ScaledBitmapVerticalLines( self, numLines=2, colors=(wx.Colour(255, 0, 0), wx.Colour(0, 255, 0)) )
		vbs.Add( self.sbvl, 1, wx.EXPAND|wx.ALL, border=border)
		
		self.sbvl.Bind( wx.EVT_MOUSEWHEEL, self.onMouseWheel )
		self.sbvl.Bind( wx.EVT_KEY_DOWN, self.onKeyDown )
		
		footerSizer = wx.BoxSizer( wx.HORIZONTAL )
		
		self.timestamp = wx.StaticText(self, label='00:00:00.000')
		self.timestamp.SetFont( wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL ) )
		footerSizer.Add( self.timestamp, flag=wx.LEFT, border=2)
		
		self.frameLeft = wx.Button( self, style=wx.BU_EXACTFIT, label='\u25C0' )
		self.frameLeft.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(-1) )
		self.frameRight = wx.Button( self, style=wx.BU_EXACTFIT, label='\u25B6' )
		self.frameRight.Bind( wx.EVT_BUTTON, lambda e: self.changeFrame(1) )
				
		footerSizer.Add( self.frameLeft, flag=wx.LEFT, border=2)
		footerSizer.Add( self.frameRight, flag=wx.LEFT, border=0)
		footerSizer.Add( wx.StaticText(self, label='or Mousewheel'), flag=wx.LEFT|wx.TOP, border=2 )
		
		vbsFooter = wx.BoxSizer( wx.VERTICAL )
		vbsFooter.Add( wx.StaticText(self, label = _('1.  Drag the Green Square so the line is on the Leading Edge of the Front Wheel.')),
					flag=wx.TOP|wx.LEFT|wx.RIGHT, border = border )
		vbsFooter.Add( wx.StaticText(self, label = _('2.  Drag the Red Square so the line is on the Trailing edge of the Front Wheel.')),
					flag=wx.BOTTOM|wx.LEFT|wx.RIGHT, border = border )
		self.explain = wx.StaticText( self )
		vbsFooter.Add( self.explain, flag=wx.ALL, border = border )
		
		footerSizer.Add( vbsFooter, flag=wx.LEFT, border=4 )
		
		vbs.Add( footerSizer )
		self.SetSizerAndFit( vbs )
		
	def changeFrame( self, frameDir ):
		if self.iPhoto1 is None:
			return
		if frameDir < 0:
			self.iPhoto1 = max(0, self.iPhoto1-1 )
		else:
			self.iPhoto1 = min(self.iPhoto2-1, self.iPhoto1+1 )
		self.sbvl.SetBitmap( self.bitmap )
		self.timestamp.SetLabel( self.t.strftime('%H:%M:%S.%f')[:-3] )
		self.setExplain()
		
	def onMouseWheel( self, event ):
		self.changeFrame( event.GetWheelRotation() )
	
	def onKeyDown( self, event ):
		self.changeFrame( -1 if event.ShiftDown() else 1 )
	
	def setExplain( self ):
		self.explain.SetLabel(
			'The wheel in this frame at {} is a reference of {}m.'.format(
				self.t.strftime('%H:%M:%S.%f')[:-3] if self.t else 'None',
				'{:.3f}'.format(self.wheelDiameter) if self.wheelDiameter else 'None',
			)
		)
		self.GetSizer().Layout()
		
	@property
	def t( self ):
		return self.tsJpg[self.iPhoto1][0] if self.iPhoto1 is not None else None
		
	@property
	def bitmap( self ):
		return CVUtil.jpegToBitmap(self.tsJpg[self.iPhoto1][1]) if self.iPhoto1 is not None else None
		
	def Set( self, tsJpg, iPhoto1, iPhoto2, wheelDiameter ):
		self.tsJpg, self.iPhoto1, self.iPhoto2 = tsJpg, iPhoto1, iPhoto2
		self.wheelDiameter = wheelDiameter
		self.sbvl.SetBitmap( self.bitmap )
		self.setExplain()
	
	def getWheelEdges( self ):
		return self.sbvl.GetVerticalLines()
	
class FrontWheelEdgePage(adv.WizardPageSimple):
	def __init__(self, parent, getSpeed):
		super().__init__(parent)
		
		self.getSpeed = getSpeed
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		self.sbvl = ScaledBitmapVerticalLines( self, numLines=1, colors=(wx.Colour(0, 255, 0),) )
		self.sbvl.Bind( EVT_VERTICAL_LINES, self.onVerticalLines )
		vbs.Add( self.sbvl, 1, wx.EXPAND|wx.ALL, border=border)
		vbs.Add( wx.StaticText(self, label = _('Drag the Green Square so the line is on the Leading Edge of the Front Wheel.')),
					flag=wx.ALL, border = border )
		self.speed = wx.StaticText( self, label=self.formatSpeed() )
		#bigFont = wx.Font( (0,24), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		#self.speed.SetFont( bigFont )
		vbs.Add( self.speed, flag=wx.ALL, border = border )
		self.SetSizerAndFit( vbs )
		
	def formatSpeed( self, kmh=0.0, mps=0.0, mph=0.0 ):
		return f'{kmh:.2f}km/h   {mps:.2f}m/s   {mph:.2f}mph'
		
	def onVerticalLines( self, event=None ):
		mps, kmh, mph, pps = self.getSpeed()
		if mps is None:
			mps = kmh = mph = pps = 0.0
		self.speed.SetLabel( self.formatSpeed(kmh, mps, mph) )
		self.GetSizer().Layout()
		
	def Set( self, t, bitmap, wheelDiameter ):
		self.t = t
		self.wheelDiameter = wheelDiameter
		self.sbvl.SetBitmap( bitmap )
		self.onVerticalLines()
	
	def getFrontWheelEdge( self ):
		return self.sbvl.GetVerticalLines()[0]
	
class ComputeSpeed:
	wheelDiameter = 0.678

	def __init__( self, parent, size=wx.DefaultSize ):
		self.wizard = adv.Wizard( parent, wx.ID_ANY, _('Compute Speed'), style=wx.RESIZE_BORDER)
		self.wizard.Bind( adv.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		
		self.iPhoto1 = None
		self.iPhoto2 = None
		
		self.wheelEdgesPage = WheelEdgesPage( self.wizard )
		self.frontWheelEdgePage = FrontWheelEdgePage( self.wizard, self.getSpeed )
		
		adv.WizardPageSimple.Chain( self.wheelEdgesPage, self.frontWheelEdgePage )

		self.wizard.SetPageSize( size )
		self.wizard.GetPageAreaSizer().Add( self.wheelEdgesPage )
		self.wizard.FitToPage( self.wheelEdgesPage )
	
	def getSpeed( self ):
		wheelTrailing, wheelLeading = self.wheelEdgesPage.getWheelEdges()
		t1 = self.wheelEdgesPage.t
		frontWheelEdge = self.frontWheelEdgePage.getFrontWheelEdge()
		if wheelTrailing is None or wheelLeading is None or frontWheelEdge is None:
			return None, None, None, None
		
		dSeconds = max(0.0001, (self.t2 - t1).total_seconds())
		
		wheelPixels = max( 1.0, abs(wheelLeading - wheelTrailing) )
		metersPerPixel = self.wheelDiameter / wheelPixels
		dPixels = abs(frontWheelEdge - wheelLeading)
		metersPerSecond = dPixels * metersPerPixel / dSeconds
		pixelsPerSecond = dPixels / dSeconds
		return metersPerSecond, metersPerSecond*3.6, metersPerSecond*2.23694, pixelsPerSecond
	
	@property
	def t1( self ):
		return self.tsJpg[self.iPhoto1][0] if self.iPhoto1 is not None else None
	
	@property
	def bitmap1( self ):
		return CVUtil.jpegToBitmap(self.tsJpg[self.iPhoto1][1]) if self.iPhoto1 is not None else None
	
	@property
	def t2( self ):
		return self.tsJpg[self.iPhoto2][0] if self.iPhoto2 is not None else None
	
	@property
	def bitmap2( self ):
		return CVUtil.jpegToBitmap(self.tsJpg[self.iPhoto2][1]) if self.iPhoto2 is not None else None
	
	def Show( self, tsJpg, iPhoto1, iPhoto2, ts_start ):
		self.tsJpg, self.iPhoto1, self.iPhoto2, self.ts_start = tsJpg, iPhoto1, iPhoto2, ts_start
		self.wheelEdgesPage.Set( self.tsJpg, self.iPhoto1, self.iPhoto2, self.wheelDiameter )
		self.frontWheelEdgePage.Set( self.t2, self.bitmap2, self.wheelDiameter )
	
		if self.wizard.RunWizard(self.wheelEdgesPage):
			return self.getSpeed()
			
		return None, None, None, None
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		if isForward:
			page = evt.GetPage()
			if page == self.wheelEdgesPage:
				self.frontWheelEdgePage.sbvl.verticalLines = [self.wheelEdgesPage.sbvl.verticalLines[1]]
			
	def onPageChanged( self, evt ):
		pass
		
if __name__ == '__main__':
	from Database import GlobalDatabase
	app = wx.App(False)

	tsJpg = GlobalDatabase().getLastPhotos( 12 )
	t1, t2 = tsJpg[0][0], tsJpg[-1][0]
	bitmap1 = CVUtil.jpegToBitmap(tsJpg[0][1])
	bitmap2 = CVUtil.jpegToBitmap(tsJpg[-1][1])

	mainWin = wx.Frame(None,title="ComputeSpeed", size=(600,300))
	size = bitmap1.GetSize()
	computeSpeed = ComputeSpeed(mainWin, size=size)
	mainWin.Show()
	mps, kmh, mph, pps = computeSpeed.Show( tsJpg, len(tsJpg)-2, len(tsJpg)-1, t2 )
	print( 'm/s={}, km/h={}, mph={} pps={}'.format(mps, kmh, mph, pps) )
	app.MainLoop()
