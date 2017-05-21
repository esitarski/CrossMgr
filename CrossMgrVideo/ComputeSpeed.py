import wx
import wx.wizard as wiz
import StringIO
from ScaledImageVerticalLines import ScaledImageVerticalLines

_ = lambda x: x

class WheelEdgesPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Drag the Green Square so the line is on the Leading Edge of the Front Wheel.')),
					flag=wx.ALL, border = border )
		vbs.Add( wx.StaticText(self, label = _('Drag the Red Square so the line is on the Trailing edge of the Front Wheel.')),
					flag=wx.ALL, border = border )
		self.sivl = ScaledImageVerticalLines( self, numLines=2, colors=(wx.Colour(255, 0, 0), wx.Colour(0, 255, 0)) )
		vbs.Add( self.sivl, 1, wx.EXPAND|wx.ALL, border=border)
		self.SetSizer( vbs )
		
	def SetImage( self, image ):
		self.sivl.SetImage( image )
	
	def getWheelEdges( self ):
		return self.sivl.GetVerticalLines()
	
class FrontWheelEdgePage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		border = 4
		vbs = wx.BoxSizer( wx.VERTICAL )
		vbs.Add( wx.StaticText(self, label = _('Drag the Green Square so the line is on the Leading Edge of the Front Wheel.')),
					flag=wx.ALL, border = border )
		self.sivl = ScaledImageVerticalLines( self, numLines=1, colors=(wx.Colour(0, 255, 0),) )
		vbs.Add( self.sivl, 1, wx.EXPAND|wx.ALL, border=border)
		self.SetSizer( vbs )
	
	def SetImage( self, image ):
		self.sivl.SetImage( image )
	
	def getFrontWheelEdge( self ):
		return self.sivl.GetVerticalLines()[0]
	
class SpeedPage(wiz.WizardPageSimple):
	def __init__(self, parent):
		wiz.WizardPageSimple.__init__(self, parent)
		
		bigFont = wx.FontFromPixelSize( (0,32), wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL )
		
		fgs = wx.FlexGridSizer( cols=2, vgap=8, hgap=8 )
		
		label = wx.StaticText( self, label='km/h =' )
		label.SetFont( bigFont )
		self.kmh = wx.StaticText( self )
		self.kmh.SetFont( bigFont )
		fgs.Add( label, flag=wx.ALIGN_RIGHT )
		fgs.Add( self.kmh, flag=wx.ALIGN_RIGHT )
		
		label = wx.StaticText( self, label='mph =' )
		label.SetFont( bigFont )
		self.mph = wx.StaticText( self )
		self.mph.SetFont( bigFont )
		fgs.Add( label, flag=wx.ALIGN_RIGHT )
		fgs.Add( self.mph, flag=wx.ALIGN_RIGHT )
		
		label = wx.StaticText( self, label='m/s =' )
		label.SetFont( bigFont )
		self.mps = wx.StaticText( self )
		self.mps.SetFont( bigFont )
		fgs.Add( label, flag=wx.ALIGN_RIGHT )
		fgs.Add( self.mps, flag=wx.ALIGN_RIGHT )
		
		self.SetSizer( fgs )
	
	def Set( self, mps, kmh, mph ):
		self.mps.SetLabel( '{:.3f}'.format(mps) )
		self.kmh.SetLabel( '{:.3f}'.format(kmh) )
		self.mph.SetLabel( '{:.3f}'.format(mph) )
		self.GetSizer().Layout()
	
class ComputeSpeed( object ):
	wheelDiameter = 0.678

	def __init__( self, parent, size=(640,480) ):
		self.wizard = wiz.Wizard( parent, wx.ID_ANY, _('Compute Speed') )
		self.wizard.Bind( wiz.EVT_WIZARD_PAGE_CHANGING, self.onPageChanging )
		
		self.t1 = None
		self.t2 = None
		self.image1 = None
		self.image2 = None
		
		self.wheelEdgesPage = WheelEdgesPage( self.wizard )
		self.frontWheelEdgePage = FrontWheelEdgePage( self.wizard )
		self.speedPage = SpeedPage( self.wizard )
		
		wiz.WizardPageSimple_Chain( self.wheelEdgesPage, self.frontWheelEdgePage )
		wiz.WizardPageSimple_Chain( self.frontWheelEdgePage, self.speedPage )

		self.wizard.SetPageSize( size )
		self.wizard.GetPageAreaSizer().Add( self.wheelEdgesPage )
		self.wizard.FitToPage( self.wheelEdgesPage )
	
	def getSpeed( self ):
		wheelTrailing, wheelLeading = self.wheelEdgesPage.getWheelEdges()
		wheelPixels = max( 1.0, abs(wheelLeading - wheelTrailing) )
		metersPerPixel = self.wheelDiameter / wheelPixels
		frontWheelEdge = self.frontWheelEdgePage.getFrontWheelEdge()
		dPixels = abs(frontWheelEdge - wheelLeading)
		metersPerSecond = dPixels * metersPerPixel / (self.t2 - self.t1).total_seconds()
		return metersPerSecond, metersPerSecond*3.6, metersPerSecond*2.23694
	
	def Show( self, image1, t1, image2, t2 ):
		self.t1, self.t2 = t1, t2
		self.image1, self.image2 = image1, image2
		self.wheelEdgesPage.SetImage( image1 )
		self.frontWheelEdgePage.SetImage( image2 )
	
		if self.wizard.RunWizard(self.wheelEdgesPage):
			return self.getSpeed()
			
		return None, None, None
	
	def onPageChanging( self, evt ):
		isForward = evt.GetDirection()
		if isForward:
			page = evt.GetPage()
			if page == self.wheelEdgesPage:
				self.frontWheelEdgePage.sivl.verticalLines = [self.wheelEdgesPage.sivl.verticalLines[1]]
			elif page == self.frontWheelEdgePage:
				self.speedPage.Set( *self.getSpeed() )
			
	def onPageChanged( self, evt ):
		isForward = evt.GetDirection()
		
if __name__ == '__main__':
	from Database import Database

	tsJpgs = Database().getLastPhotos( 12 )
	t1, t2 = tsJpgs[0][0], tsJpgs[-1][0]
	image1 = wx.ImageFromStream( StringIO.StringIO(tsJpgs[0][1]), wx.BITMAP_TYPE_JPEG )
	image2 = wx.ImageFromStream( StringIO.StringIO(tsJpgs[-1][1]), wx.BITMAP_TYPE_JPEG )

	app = wx.App(False)
	mainWin = wx.Frame(None,title="ComputeSpeed", size=(600,300))
	size=image1.GetSize()
	size = (800,600)
	computeSpeed = ComputeSpeed(mainWin, size=size)
	mainWin.Show()
	mps, kmh, mph = computeSpeed.Show( image1, t1, image2, t2 )
	print 'm/s={}, km/h={}, mph={}'.format(mps, kmh, mph)
	app.MainLoop()
