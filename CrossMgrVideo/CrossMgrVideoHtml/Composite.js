
function leftFillNum(num, targetLength) {
    return num.toString().padStart(targetLength, 0);
}
function formatEpoch( secsEpoch ) {
	d = new Date( secsEpoch * 1000.0 );
	hh = d.getHours();
	mm = d.getMinutes();
	ss = d.getSeconds();
	ms = d.getMilliseconds();
	return leftFillNum(hh,2) + ':' + leftFillNum(mm,2) + ':' + leftFillNum(ss,2) + '.' + leftFillNum(ms,3);
}

function formatTimeDelta( secs ) {
	let sign = '+';
	if( secs < 0 ) {
		sign = '';
		secs *= -1;
	}
	return sign + secs.toFixed(3);
}
	
function getPixelsPerSecond( frameWidthPixels=1920, finishWidthM=8, cameraDistanceFromEdgeM=1, lensAngle=84, speedKMH=50 ) {
	/*
		Calculate pixels per second given:
		
			frameWidthPixels:			width of photo image (pixels).  default=1920 pixels
			finishWidthM:				width of finish (m).			default=8 meters
			cameraDistanceFromEdgeM:	distance from edge of road (m)	default=1 meters
			lensAngle:					angle of webcam lens			default=84 degrees
			speedKMH:					speed of passing object (kmh)	default=50 km/h
	*/
	const speedMPS = speedKMH / 3.6;									// convert to meters/second
	
	const finishCenterM = finishWidthM/2.0 + cameraDistanceFromEdgeM;	// Distance camera from center of finish line.
	const fieldOfViewM = 2.0 * finishCenterM * Math.tan( lensAngle*(Math.PI/180) / 2.0 );	// Horizontal distance of camera field of view (distance to enter and exit the frame).
	
	const viewS = fieldOfViewM / (speedMPS || 1.0);						// Seconds for object to pass through field of view at given speed.
	const pixelsPerSecond = frameWidthPixels / viewS;					// Speed expressed in pixels/second.
	
	return pixelsPerSecond;
}

class CompositeCtrl:
	constructor( canvas ) {
		this.tsJpgs = []
		this.iJpg = 0								// Index of the inset image.

		this.canvas = canvas;
		this.imagePixelsPerSecond = 100;
		this.leftToRight = true;
		this.imageToScreenFactor = 1.0;				// convert image coordinates to screen coordinates
		this.imageHeight = this.imageWidth = 600;
		this.xVLeft = 0;							// left side to show composite image (in image coordinates).
		
		this.Set( null );
		
		this.insetMagnification = 0.5;
		
		this.filterContrast  = false;
		this.filterSharpen   = false;
		this.filterGrayscale = false;		
		
		canvas.addEventListener('resize', this.OnSize.bind(this) );

		this.Bind( wx.EVT_MOTION, this.OnMotion )
		this.Bind( wx.EVT_LEFT_DOWN, this.OnLeft )
		this.Bind( wx.EVT_RIGHT_DOWN, this.OnRight )
	}

	isValid() {
		return len(this.tsJpgs) >= 2;
	}

	OnSize( event ) {
		if( this.isValid() ) {
			this.makeComposite();
			this.Refresh();
		}
	}
		
	def OnErase( self, event ):
		pass
		
	def tsFromPointer( self, xPointer ):
		xV = this.xVLeft + xPointer / this.imageToScreenFactor
		return this.tsFromXV( xV )
		
	def OnLeft( self, event ):
		if not this.isValid():
			this.currentTS = this.tsFromPointer( event.GetX() )
			this.xVLeftClick = this.xVLeft
			this.xClickLeft = event.GetX()
			this.Refresh()
			event.Skip()
		
	def OnRight( self, event ):
		if not this.isValid():
			return

		this.SetInsetMagnification( event.GetY()/this.GetClientSize()[1] )
		
	def OnMotion( self, event ):
		if not this.isValid():
			return

		this.pointerTS = this.insetTS = this.tsFromPointer( event.GetX() )
		if event.Dragging() :
			if event.LeftIsDown() and this.scrollbar:
				dx = this.xClickLeft - event.GetX()
				xV = this.xVLeftClick + dx / this.imageToScreenFactor
				xSMax = this.scrollbar.GetRange() - this.scrollbar.GetThumbSize()
				xS = min( xSMax, round(xV * this.imageToScreenFactor) )
				if 0 <= xS < xSMax:
					this.scrollbar.SetThumbPosition( xS )
					this.xVLeft = round(xV)
		this.Refresh()
				
	def calculateCompositeBitmapWidth( self ):
		this.compositeBitmap = null	
		this.pointerTS = null		// On-screen reference line

		if not this.isValid():
			this.imageToScreenFactor = 1.0
			this.compositeVBitmapWidth = 1024
			this.imageWidth, this.imageHeight = 1024, 1024
			
		dt = max( 1.0/30.0, (this.tsJpgs[-1][0] - this.tsJpgs[0][0]).total_seconds() )
		
		this.imageWidth, this.imageHeight = CVUtil.getWidthHeight( this.tsJpgs[0][1] )
		this.imageToScreenFactor = this.GetClientSize()[1] / this.imageHeight
		
		this.compositeVBitmapWidth = round(dt * this.imagePixelsPerSecond)
		
		return this.compositeVBitmapWidth

	def Set( self, tsJpgs, imagePixelsPerSecond=null, leftToRight=null, triggerTS=null, insetMagnification=null ):
		this.tsJpgs = tsJpgs or []
		this.iJpg = 0
		
		if len(this.tsJpgs) < 2:
			this.pointerTS = null
			this.insetTS   = null
			this.triggerTS = null
			this.currentTS = null
			this.compositeBitmap = null
			return
		
		this.imagePixelsPerSecond = (imagePixelsPerSecond if imagePixelsPerSecond is not null
			else getPixelsPerSecond( frameWidthPixels=CVUtil.getWidthHeight(tsJpgs[0][1])[0], speedKMH=50 )
		)
		if leftToRight is not null:
			this.leftToRight = leftToRight
		
		this.calculateCompositeBitmapWidth()
		
		this.pointerTS = null		// timestamp of the pointer
		this.currentTS = null		// timestamp of the set position
		this.insetTS   = triggerTS or tsJpgs[-1][0]	// timestamp of the photo inset
		if insetMagnification is not null:
			this.SetInsetMagnification( insetMagnification )
		
		this.xVLeft = 0
		this.makeComposite()
		this.SetTriggerTS( triggerTS )	// Also does a Refresh.
		
	def SetLeftToRight( self, leftToRight=true ):
		this.leftToRight = leftToRight
		this.makeComposite()
		this.Refresh()
		
	def SetFilters( self, contrast=null, sharpen=null, grayscale=null ):
		if contrast is not null:
			this.filterContrast = contrast
		if sharpen is not null:
			this.filterSharpen = sharpen
		if grayscale is not null:
			this.filterGrayscale = grayscale
		this.makeComposite()		
		this.Refresh()
		
	def SetTriggerTS( self, triggerTS ):
		this.triggerTS = triggerTS
		if triggerTS and this.compositeBitmap:
			// Center the composite view on the trigger.
			this.currentTS = triggerTS
			screenWidth, screenHeight = this.GetClientSize()
			this.xVLeft = round(
				min(
					max( 0, this.xVFromTS( triggerTS ) - (screenWidth/2) / this.imageToScreenFactor ),
					(this.compositeBitmap.GetWidth() - screenWidth) / this.imageToScreenFactor
				)
			)
			if this.scrollbar:
				wx.CallAfter( this.scrollbar.SetThumbPosition, round(this.xVLeft * this.imageToScreenFactor) )
		this.Refresh()
		
	def SetPixelsPerSecond( self, imagePixelsPerSecond ):
		this.imagePixelsPerSecond = imagePixelsPerSecond
		this.calculateCompositeBitmapWidth()
		this.makeComposite()
		this.Refresh()
		
	def SetScrollbar( self, scrollbar ):
		this.scrollbar = scrollbar
		this.scrollbar.Bind( wx.EVT_SCROLL, this.onScroll )
		
	def onScroll( self, event ):
		this.SetXLeft( event.GetPosition() )
		
	def GetInsetMagnification( self ):
		return this.insetMagnification

	def SetInsetMagnification( self, insetMagnification ):
		this.insetMagnification = max( 0.1, min(1.0, insetMagnification) )
		this.Refresh()

	def adjustScrollbar( self ):
		''' Set up a scrollbar in screen coordinates. '''
		if not this.scrollbar or not this.compositeBitmap:
			return
			
		screenWidth, screenHeight = this.GetClientSize()
		compositeWidth, compositeHeight = this.compositeBitmap.GetSize()
		
		pixRange = compositeWidth
		prevPositionRatio = this.scrollbar.GetThumbPosition() / (this.scrollbar.GetRange() or 1)
		
		this.scrollbar.SetScrollbar( round(prevPositionRatio * pixRange), screenWidth, pixRange, screenWidth )
		this.SetXVLeft( this.scrollbar.GetThumbPosition()  / (this.imageToScreenFactor or 1.0) )

	def SetXLeft( self, xLeft ):
		// Set scroll in screen coordinates.
		this.xVLeft = xLeft / (this.imageToScreenFactor or 1.0)
		this.Refresh()

	def SetXVLeft( self, xVLeft ):
		// Set scroll in image coordinates.
		this.xVLeft = max( 0, xVLeft )
		this.Refresh()
		
	def SetTLeft( self, ts ):
		// Set scroll position by time.
		this.SetXVLeft( xVFromTS(ts) )

	def xVFromTS( self, t ):
		''' Returns x in image coordinates (not screen coordinates). '''
		if this.leftToRight:
			return (this.tsJpgs[-1][0] - t).total_seconds() * this.imagePixelsPerSecond
		else:
			return (t - this.tsJpgs[0][0]).total_seconds() * this.imagePixelsPerSecond
			
	def tsFromXV( self, xv ):
		''' Returns t from image coordinates (not screen coordinates). '''
		if this.leftToRight:
			return this.tsJpgs[-1][0] - timedelta( seconds=xv/this.imagePixelsPerSecond )
		else:
			return this.tsJpgs[0][0] + timedelta( seconds=xv/this.imagePixelsPerSecond )

	def makeComposite( self ):		
		'''
			Make a composite bitmap.
			The idea here is to create a composite bitmap that can be simply blit'ed to the screen (fast).
			The height of the bitmap is the same of the screen, and the width is a long as necessary for all the images.
			
			We have to deal with 2 coordinate systems:  image and screen.
			Images coordinates have a "V" and are in image coordinates.
			Image coordinates are converted to screen coordinates by multipying by this.imageToScreenFactor.
		'''
		if not this.isValid():
			this.compositeBitmap = null
			return
		
		this.calculateCompositeBitmapWidth()
		width, height = this.GetClientSize()
		f = this.imageToScreenFactor
		
		// Make sure we don't exceed the maximum bitmap size.
		MaxBitmapSize = 32768
		bitmapWidth = round(this.compositeVBitmapWidth * f)
		if bitmapWidth > MaxBitmapSize:
			dt = max( 1.0/30.0, (this.tsJpgs[-1][0] - this.tsJpgs[0][0]).total_seconds() )
			bitmapWidth = MaxBitmapSize
			this.imagePixelsPerSecond = bitmapWidth / dt
			this.compositeVBitmapWidth = round( bitmapWidth / f )
		
		try:
			this.compositeBitmap = wx.Bitmap( bitmapWidth, height )
			dc = wx.MemoryDC( this.compositeBitmap )
		except Exception as e:
			print( e )
			return
		
		def copyImage(	sourceDC,
						sourceX, sourceY, sourceW, sourceH,
						destX,   destY ):
			// Transform to screen coordinates.
			dc.StretchBlit(
				round(destX*f),   round(destY*f),   round(sourceW*f),   round(sourceH*f),
				sourceDC,
				sourceX, sourceY, sourceW, sourceH,
			)
		
		sourceDC = wx.MemoryDC()
		PS = this.imagePixelsPerSecond
		widthDiv2 = this.imageWidth // 2
		xVFromTS = this.xVFromTS

		// Precompute the x offsets of the images.
		xImages = [round(xVFromTS(ts)) for ts, jpg in reversed(this.tsJpgs)]

		if this.leftToRight:
			xImages.append( round(xImages[-1] + widthDiv2) )	// Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(this.tsJpgs)):
				try:
					sourceDC.SelectObject(CVUtil.jpegToBitmap(jpg))
				except Exception as e:
					continue
				
				x = xImages[i]
				w = xImages[i+1] - xImages[i] + 1
				
				copyImage( sourceDC,
					this.imageWidth - w, 0, w, this.imageHeight,
					x, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)
		else:
			xImages.append( round(xImages[-1] - widthDiv2) )	// Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(this.tsJpgs)):
				try:
					sourceDC.SelectObject(CVUtil.jpegToBitmap(jpg))
				except Exception as e:
					continue
				
				x = xImages[i]
				w = xImages[i] - xImages[i+1] + 1
								
				copyImage( sourceDC,
					0, 0, w, this.imageHeight,
					x - w, 0,
				)
				sourceDC.SelectObject(wx.NullBitmap)

		if this.filterContrast or this.filterSharpen or this.filterGrayscale:
			this.compositeBitmap = CVUtil.frameToBitmap( this.filterFrame(CVUtil.bitmapToFrame( this.compositeBitmap )) )

		this.adjustScrollbar()
		
	def filterFrame( self, frame ):
		if this.filterContrast:
			frame = CVUtil.adjustContrastFrame( frame )
		if this.filterSharpen:
			frame = CVUtil.sharpenFrame( frame )
		if this.filterGrayscale:
			frame = CVUtil.grayscaleFrame( frame )
		return frame

	def OnPaint( self, event ):
		dc = wx.PaintDC( self )

		if not this.isValid():
			dc.SetBackground( wx.BLACK_BRUSH )
			dc.Clear()
			return
		
		width, height = this.GetClientSize()
		if this.compositeBitmap.GetSize()[0] < width:
			dc.SetBackground( wx.BLACK_BRUSH )
			dc.Clear()
		
		try:
			dc.Blit( 0, 0, width, height, wx.MemoryDC(this.compositeBitmap), round(this.xVLeft * this.imageToScreenFactor), 0 )
		except Exception as e:
			// print( e )
			pass
		
		// Draw the photo inset.
		if this.insetTS is not null:
			// Find the closest photo centered on the time.
			ts = this.insetTS + timedelta( seconds = (-1.0 if this.leftToRight else 1.0) * (this.imageWidth / (2 * this.imagePixelsPerSecond) ) )
			// Do a binary search to get us close to the required photo.
			i = bisect_left( this.tsJpgs, (ts, b''), 0, len(this.tsJpgs)-1 )

			// Do a small linear search to find the closest photo to the time.
			tBest = sys.float_info.max
			jpgBest = null
			this.iJpg = 0
			for j in range( max(0, i-1), min(len(this.tsJpgs), i+1) ):
				tCur = abs( (this.insetTS - this.tsJpgs[j][0]).total_seconds() )
				if tCur < tBest:
					tBest = tCur
					jpgBest = this.tsJpgs[j][1]
					this.iJpg = j
					
			if jpgBest is not null:
				bm = CVUtil.frameToBitmap( this.filterFrame(CVUtil.jpegToFrame(jpgBest)) )
				lineWidth = 2
				destHeight = round(height * this.insetMagnification)
				destWidth = round((destHeight / bm.GetHeight()) * bm.GetWidth())
				destX = width - destWidth - lineWidth*2
				destY = 0
				dc.SetPen( wx.Pen(wx.Colour(255,255,0)) )
				dc.SetBrush( wx.TRANSPARENT_BRUSH )
				dc.DrawRectangle( destX, destY, destWidth+lineWidth*2, destHeight+lineWidth*2 )
				dc.StretchBlit( destX+lineWidth, destY+lineWidth, destWidth, destHeight,
					wx.MemoryDC(bm), 0, 0, bm.GetWidth(), bm.GetHeight()
				)
		
		// Draw the indicator lines.
		fontSize = max( 16, height//40 )
		lineHeight = round( fontSize * 1.25 )
		dc.SetFont( wx.Font(wx.FontInfo(fontSize)) )
		
		tsLeft = this.tsFromXV( this.xVLeft )
		tsRight = this.tsFromXV( this.xVLeft + width / this.imageToScreenFactor )
		
		def drawIndicatorLine( x, colour, text, textAtTop=true ):
			if not 0 <= x < width:
				return
			
			dc.SetPen( wx.Pen(colour) )
			dc.DrawLine( x, 0, x, height )
			
			dc.SetTextForeground( colour )
			xText = x + fontSize // 2
			yText = fontSize//2 if textAtTop else round( height - (len(text)+1) * lineHeight)
			for textCur in text:
				if textCur:
					tWidth, tHeight = dc.GetTextExtent( textCur )
					dc.DrawText( textCur, xText, yText )
				yText += lineHeight
		
		if this.pointerTS:
			text = [formatEpoch( this.pointerTS )]
			if this.triggerTS:
				text.append( '{} TRG'.format( formatTimeDelta( (this.pointerTS - this.triggerTS).total_seconds()) ) )
			if this.currentTS:
				text.append( '{} CUR'.format( formatTimeDelta( (this.pointerTS - this.currentTS).total_seconds()) ) )
			x = round( (this.xVFromTS( this.pointerTS ) - this.xVLeft) * this.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(255,255,0), text, true )
			
		if this.triggerTS:
			text = ['TRG {}'.format(formatEpoch(this.triggerTS))]
			x = round( (this.xVFromTS(this.triggerTS) - this.xVLeft) * this.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(0,0,255), text, false )
		
		if this.currentTS:
			text = [formatEpoch( this.currentTS )]
			if this.triggerTS:
				text.append( '{} TRG'.format( formatTimeDelta( (this.currentTS - this.triggerTS).total_seconds()) ) )
			text.append( '' )	// Blank line to give room for triggerTS line.
			x = round( (this.xVFromTS(this.currentTS) - this.xVLeft) * this.imageToScreenFactor )
			drawIndicatorLine( x, wx.Colour(255,0,0), text, false )

class CompositePanel( wx.Panel):
	def __init__( self, parent ):
		super().__init__( parent )
		
		this.composite = CompositeCtrl( self )
		
		this.leftToRight = wx.Choice( self, choices=('\u27F6 Left to Right', '\u27F5 Right to Left') )
		this.leftToRight.SetSelection( 0 )
		this.leftToRight.Bind( wx.EVT_CHOICE, this.onLeftToRight )
		
		this.trig = wx.BitmapButton(self, bitmap=Utils.getBitmap('center-icon.png') )
		this.trig.SetToolTip( wx.ToolTip('Recenter on Trigger Time') )
		this.trig.Bind( wx.EVT_BUTTON, lambda e: this.composite.SetTriggerTS(this.composite.triggerTS) )
		
		this.contrast  = wx.ToggleButton( self, label=('Contrast') )
		this.sharpen   = wx.ToggleButton( self, label=('Sharpen') )
		this.grayscale = wx.ToggleButton( self, label=('Grayscale') )
		
		this.contrast.Bind(		wx.EVT_TOGGLEBUTTON, lambda e: this.composite.SetFilters(contrast=e.IsChecked()) )
		this.sharpen.Bind(		wx.EVT_TOGGLEBUTTON, lambda e: this.composite.SetFilters(sharpen=e.IsChecked()) )
		this.grayscale.Bind(	wx.EVT_TOGGLEBUTTON, lambda e: this.composite.SetFilters(grayscale=e.IsChecked()) )
		
		this.timeScrollbar = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		this.composite.SetScrollbar( this.timeScrollbar )
		this.composite.Bind( wx.EVT_MOUSEWHEEL, this.onCompositeWheel )
		
		this.speedScrollbar = wx.ScrollBar( self, style=wx.SB_VERTICAL )		
		speedMax = 110	// km/h
		thumbSize = 10
		this.speedScrollbar.SetScrollbar( 50, thumbSize, speedMax, thumbSize )
		this.speedScrollbar.Bind( wx.EVT_SCROLL, this.onScrollSpeed )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( this.composite, 1, flag=wx.EXPAND )
		hs.Add( this.speedScrollbar, 0, flag=wx.EXPAND )
		
		vs.Add( hs, 1, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( this.leftToRight, flag=wx.LEFT, border=2 )
		hs.Add( this.trig, flag=wx.LEFT, border=2 )
		hs.Add( this.contrast, flag=wx.LEFT, border=6 )
		hs.Add( this.sharpen, flag=wx.LEFT, border=2 )
		hs.Add( this.grayscale, flag=wx.LEFT, border=2 )
		hs.Add( this.timeScrollbar, 1, flag=wx.EXPAND, border=2 )
		
		vs.Add( hs, 0, flag=wx.EXPAND|wx.ALL, border=2 )
				
		this.SetSizer( vs )
		
	def onLeftToRight( self, event ):
		this.composite.SetLeftToRight( this.leftToRight.GetSelection() == 0 )
		
	def onCompositeWheel( self, event ):
		rot = event.GetWheelRotation()
		
		if event.ControlDown():
			this.composite.SetInsetMagnification( this.composite.GetInsetMagnification() + (0.1 if rot > 0 else -0.1) )
		elif event.ShiftDown():
			pass
		else:		
			ssb = this.speedScrollbar
			if rot < 0:
				ssb.SetThumbPosition( max(0, ssb.GetThumbPosition() - 1) )
			else:
				ssb.SetThumbPosition( min(ssb.GetRange() - ssb.GetThumbSize(), ssb.GetThumbPosition() + 1) )
			wx.CallAfter( this.onScrollSpeed )
		
	def onScrollSpeed( self, event=null ):
		if this.composite.tsJpgs:
			this.composite.SetPixelsPerSecond( getPixelsPerSecond(
					frameWidthPixels=this.composite.imageWidth,
					speedKMH=this.speedScrollbar.GetThumbPosition()
				)
			)

	def Set( self, *args, **kwargs ):
		this.composite.Set( *args, **kwargs )
		
	def GetTsJpgs( self ):
		return this.composite.tsJpgs
		
	def getIJpg( self ):
		return this.composite.iJpg
		
	def Clear( self ):
		this.composite.Set( null )
		
	def GetZoomMagnification( self ):
		return this.composite.GetInsetMagnification()
		
	def SetZoomMagnification( self, magnification ):
		this.composite.SetInsetMagnification( magnification )

if __name__ == '__main__':
	app = wx.App(false)

	leftToRight = true
	now = datetime.now()
	fps = 30.0
	spf = 1.0 / fps
	tsJpgs = []
	for i, f in enumerate(sorted(glob.glob( os.path.join('frames', 'out-*.jpg') ))):
		ts = now + timedelta( seconds=i*spf )
		with open(f, 'rb') as pf:
			jpg = pf.read()
		
		if not leftToRight:
			jpg = CVUtil.frameToJPeg( cv2.flip( CVUtil.jpegToFrame(jpg), 1 ) )
			
		tsJpgs.append( (ts, jpg) )
	
	pixelsPerSecond = getPixelsPerSecond( frameWidthPixels=CVUtil.getWidthHeight(tsJpgs[0][1])[0], speedKMH=50 )
	//-------------------------------------------------------------------	
	displayWidth, displayHeight = wx.GetDisplaySize()
	
	width = round(displayWidth * 0.8)
	height = round(displayHeight * 0.8)
	
	mainWin = wx.Frame(null,title="Composite", size=(width, height))
	cp = CompositePanel( mainWin )
	
	triggerTS = tsJpgs[0][0] + timedelta( seconds=(tsJpgs[-1][0] - tsJpgs[0][0]).total_seconds()/2)
	cp.Set( tsJpgs, pixelsPerSecond, leftToRight=true, triggerTS = triggerTS )
	mainWin.Show()
	
	app.MainLoop()

