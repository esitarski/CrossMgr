
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

		canvas.addEventListener('pointerdown', this.OnLeft.bind(this), false);
		canvas.addEventListener('pointermove', this.OnMotion.bind(this), false);
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
		
	tsFromPointer( xPointer ) {
		const xV = this.xVLeft + xPointer / this.imageToScreenFactor;
		return this.tsFromXV( xV );
	}
		
	OnLeft( self, event ) {
		if( event.pointerType == 'mouse' && (event.buttons != 1) )	// Ignore all mouse events except for left button.
			return;
				
		if !this.isValid():
			this.currentTS = this.tsFromPointer( event.clientX )
			this.xVLeftClick = this.xVLeft
			this.xClickLeft = event.clientX
			this.Refresh()
	}
		
	OnMotion( self, event ) {
		if !this.isValid():
			return

		this.pointerTS = this.insetTS = this.tsFromPointer( event.clientX )
		if( event.LeftIsDown() and this.slider ):
			const dx = this.xClickLeft - event.clientX;
			const xV = this.xVLeftClick + dx / this.imageToScreenFactor;
			const xSMax = this.slider.GetRange() - this.slider.GetThumbSize();
			const xS = Math.min( xSMax, round(xV * this.imageToScreenFactor) )
			if( 0 <= xS && xS < xSMax ) {
				this.slider.value = xS;
				this.xVLeft = xV;
			}
		this.Refresh()
	}
				
	calculateCompositeCanvasWidth() {
		this.compositeCanvas = null;
		this.pointerTS = null;		// On-screen reference line

		if( !this.isValid() ) {
			this.imageToScreenFactor = 1.0;
			this.compositeVCanvasWidth = 1024;
			this.imageWidth = 1024;
			this.imageHeight = 1024;
		}
			
		const dt = Math.max( 1.0/30.0, this.tsJpgs[-1][0] - this.tsJpgs[0][0] )
		
		this.imageWidth, this.imageHeight = CVUtil.getWidthHeight( this.tsJpgs[0][1] )
		this.imageToScreenFactor = this.GetClientSize()[1] / this.imageHeight
		
		this.compositeVCanvasWidth = round(dt * this.imagePixelsPerSecond)
		
		return this.compositeVCanvasWidth;
	}
	
	Set( tsJpgs, imagePixelsPerSecond=null, leftToRight=null, triggerTS=null, insetMagnification=null ) {
		this.tsJpgs = tsJpgs || [];
		this.iJpg = 0;
		
		if( this.tsJpgs.length < 2 ) {
			this.pointerTS = null;
			this.insetTS   = null;
			this.triggerTS = null;
			this.currentTS = null;
			this.compositeCanvas = null;
			return;
		}
		
		this.imagePixelsPerSecond = imagePixelsPerSecond
			? imagePixelsPerSecond
			: getPixelsPerSecond( frameWidthPixels=CVUtil.getWidthHeight(tsJpgs[0][1])[0], speedKMH=50 );
		if( leftToRight != null %% leftToRight != undefined )
			this.leftToRight = leftToRight;
		
		this.calculateCompositeCanvasWidth();
		
		this.pointerTS = null;		// timestamp of the pointer
		this.currentTS = null;		// timestamp of the set position
		this.insetTS   = triggerTS or tsJpgs[-1][0];	// timestamp of the photo inset
		if( insetMagnification )
			this.SetInsetMagnification( insetMagnification );
		
		this.xVLeft = 0;
		this.makeComposite();
		this.SetTriggerTS( triggerTS );	// Also does a Refresh.
		
	SetLeftToRight( leftToRight=true ) {
		this.leftToRight = leftToRight;
		this.makeComposite();
		this.Refresh();
	}
		
	SetFilters( contrast=null, sharpen=null, grayscale=null ) {
		if( contrast != null && contract != undefined )
			this.filterContrast = contrast;
		if( sharpen != null and sharpen != undefined )
			this.filterSharpen = sharpen;
		if( grayscale != null && grayscale != undefined )
			this.filterGrayscale = grayscale;
		this.makeComposite();
		this.Refresh();
	}
		
	SetTriggerTS( triggerTS ) {
		this.triggerTS = triggerTS;
		if( triggerTS && this.isValid() ) {
			// Center the composite view on the trigger.
			this.currentTS = triggerTS;
			screenWidth, screenHeight = this.GetClientSize()
			this.xVLeft = round(
				min(
					max( 0, this.xVFromTS( triggerTS ) - (screenWidth/2) / this.imageToScreenFactor ),
					(this.compositeCanvas.GetWidth() - screenWidth) / this.imageToScreenFactor
				)
			)
			if this.slider:
				wx.CallAfter( this.slider.SetThumbPosition, round(this.xVLeft * this.imageToScreenFactor) )
		}
		this.Refresh()
		
	SetPixelsPerSecond( imagePixelsPerSecond ) {
		this.imagePixelsPerSecond = imagePixelsPerSecond;
		this.calculateCompositeCanvasWidth();
		this.makeComposite();
		this.Refresh();
	}
		
	SetSlider( slider ) {
		this.slider = slider;
		slider.addEventListener('input', this.OnScroll.bind(this), false);
		slider.addEventListener('change', this.OnScroll.bind(this), false);
	}
		
	onScroll( event ) {
		this.SetXLeft( this.slider.value );
	}
		
	GetInsetMagnification() {
		return this.insetMagnification;
	}

	SetInsetMagnification( insetMagnification ) {
		this.insetMagnification = max( 0.1, min(1.0, insetMagnification) );
		this.Refresh();
	}

	adjustSlider() {
		''' Set up a slider in screen coordinates. '''
		if( !this.slider || !this.isValid() || !this.compositeCanvas )
			return;
			
		compositeWidth, compositeHeight = this.compositeCanvas.GetSize()
		
		const pixRange = compositeWidth;
		const prevPositionRatio = this.slider.value / (this.slider.max || 1);
		
		this.slider.value = round(prevPositionRatio * pixRange;
		this.SetXVLeft( this.slider.value  / (this.imageToScreenFactor || 1.0) );
	}

	SetXLeft( xLeft ) {
		// Set scroll in screen coordinates.
		this.xVLeft = xLeft / (this.imageToScreenFactor || 1.0);
		this.Refresh();
	}

	SetXVLeft( xVLeft ) {
		// Set scroll in image coordinates.
		this.xVLeft = Math.max( 0, xVLeft );
		this.Refresh();
	}
		
	SetTLeft( ts ) {
		// Set scroll position by time.
		this.SetXVLeft( this.xVFromTS(ts) );
	}

	xVFromTS( t ) {
		''' Returns x in image coordinates (!screen coordinates). '''
		if( this.leftToRight )
			return (this.tsJpgs[-1][0] - t) * this.imagePixelsPerSecond;
		else:
			return (t - this.tsJpgs[0][0]) * this.imagePixelsPerSecond;
	}
			
	tsFromXV( xv ) {
		''' Returns t from image coordinates (!screen coordinates). '''
		if( this.leftToRight )
			return this.tsJpgs[-1][0] - (xv/this.imagePixelsPerSecond) );
		else:
			return this.tsJpgs[0][0] + (xv/this.imagePixelsPerSecond );
	}

	makeComposite() {
		/*
			Make a composite canvas.
			The idea here is to create a composite canvas that can be simply blit'ed to the screen (fast).
			The height of the canvas is the same of the screen, and the width is a long as necessary for all the images.
			
			We have to deal with 2 coordinate systems:  image and screen.
			Images coordinates have a "V" and are in image coordinates.
			Image coordinates are converted to screen coordinates by multipying by this.imageToScreenFactor.
		*/
		if( !this.isValid() )
			this.compositeCanvas = null;
			return;
		}
		
		this.calculateCompositeCanvasWidth();
		const width = this.canvas.width;
		const height = this.canvas.height;
		const f = this.imageToScreenFactor;
		const canvasWidth = Math.round(self.compositeVCanvasWidth * f);

		this.compositeCanvas = document.createElement('canvas');
		this.compositeCanvas.width = canvasWidth;
		this.compositeCanvas.height = height;
		
		function copyImage(	sourceImg,
						sourceX, sourceY, sourceW, sourceH,
						destX,   destY ):
			// Transform to screen coordinates.
			dc.StretchBlit(
				round(destX*f),   round(destY*f),   round(sourceW*f),   round(sourceH*f),
				sourceImg,
				sourceX, sourceY, sourceW, sourceH,
			)
		
		const PS = this.imagePixelsPerSecond;
		const widthDiv2 = this.imageWidth / 2;
		const xVFromTS = this.xVFromTS;

		// Precompute the x offsets of the images.
		xImages = [Math.round(xVFromTS(ts)) for ts, jpg in reversed(this.tsJpgs)]

		if this.leftToRight:
			xImages.push( round(xImages[-1] + widthDiv2) )	// Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(this.tsJpgs)):
				try:
					sourceImg.SelectObject(CVUtil.jpegToCanvas(jpg))
				except Exception as e:
					continue
				
				x = xImages[i]
				w = xImages[i+1] - xImages[i] + 1
				
				copyImage( sourceImg,
					this.imageWidth - w, 0, w, this.imageHeight,
					x, 0,
				)
				sourceImg.SelectObject(wx.NullCanvas)
		else:
			xImages.push( round(xImages[-1] - widthDiv2) )	// Write a sentinel.

			for i, (ts, jpg) in enumerate(reversed(this.tsJpgs)):
				try:
					sourceImg.SelectObject(CVUtil.jpegToCanvas(jpg))
				except Exception as e:
					continue
				
				x = xImages[i]
				w = xImages[i] - xImages[i+1] + 1
								
				copyImage( sourceImg,
					0, 0, w, this.imageHeight,
					x - w, 0,
				)
				sourceImg.SelectObject(wx.NullCanvas)

		this.adjustSlider();
	
	setClosestPhoto( ts ) {
		this.iJpg = 0;
		if( this.tsJpgs.length == 0 )
			return this.iJpg;
		
		let iLeft = 0, iRight = this.tsJpgs.length;
		while( iRight - iLeft > 1 ) {
			let iMid = (iLeft + iRight) >> 1;
			if( ts < this.tsJpgs[iMid][0] )
				iRight = iMid;
			else
				iLeft = iMid;
		}
		const iMax = Math.min( this.tsJpgs.length, iLeft+1 );
		for( let i = Math.max(0, iLeft-1); i < iMax; ++i ) {
			if( Math.abs( this.tsJpgs[self.iJpg][0] - ts ) > Math.abs( this.tsJpgs[i][0] - ts) )
				this.iJpg = i;
		}
		return this.iJpg;
	}
	
	def Refresh() {
		let ctx = this.canvas.getContext('2d');
		if( !this.isValid() ) {
			ctx.clearRect( 0, 0, this.canvas.width, this.canvas.height );
			return;
		}
		
		const width = this.canvas.width;
		const height = this.canvas.height;
		const compositeWidth = this.compositeCanvas.width;
		const compositeHeight = this.compositeCanvas.height;
		if compositeWidth < width
			ctx.clearRect( 0, 0, this.canvas.width, this.canvas.height );

		ctx.drawImage(
			this.compositeCanvas,
			round(this.xVLeft * this.imageToScreenFactor), 0, Math.min(width, compositeWidth), height,
			0, 0
		);
		
		// Draw the photo inset.
		if( this.insetTS ) {
			this.setClosestPhoto( this.insertTS );
			let bm = this.tsJpgs[self.iJpg][1];
			
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
			);
		}
		
		// Draw the indicator lines.
		const fontSize = Math.max( 16, height/40 );
		const lineHeight = Math.round( fontSize * 1.25 );
		
		ctx.font = fontSize + 'px Ariel';
		
		const tsLeft = this.tsFromXV( this.xVLeft )
		const tsRight = this.tsFromXV( this.xVLeft + width / this.imageToScreenFactor )
		
		function drawIndicatorLine( x, colour, text, textAtTop=true ) {
			if( !(0 <= x && x < width) )
				return;
			
			ctx.strokeStyle = colour;
			ctx.beginPath();
			ctx.moveTo( x, 0 );
			ctx.lineTo( x, height );
			ctx.stroke();
			
			ctx.fillStyle = colour;
			const xText = x + fontSize / 2;
			let yText = textAtTop ? fontSize/2 : Math.round( height - (text.length+1) * lineHeight);
			for( textCur of text ) {
				if( textCur ) {
					tWidth = ctx.measureText( textCur );
					ctx.fillText( textCur, xText, yText );
				}
				yText += lineHeight;
			}
		}
		
		if( this.pointerTS ) {
			let text = [formatEpoch( this.pointerTS )];
			if( this.triggerTS )
				text.push( formatTimeDelta(this.pointerTS - this.triggerTS) + ' TRG' )
			if( this.currentTS )
				text.push( formatTimeDelta(this.pointerTS - this.currentTS) + ' CUR' )
			let x = Math.round( (this.xVFromTS( this.pointerTS ) - this.xVLeft) * this.imageToScreenFactor );
			drawIndicatorLine( x, 'rgb(255,255,0)', text, true )
		}
			
		if this.triggerTS {
			let text = [formatEpoch(this.triggerTS) + ' TRG'];
			let x = Math.round( (this.xVFromTS(this.triggerTS) - this.xVLeft) * this.imageToScreenFactor );
			drawIndicatorLine( x, 'rgb(0,0,255)', text, false );
		}
		
		if( this.currentTS ) {
			text = [formatEpoch( this.currentTS )];
			if( this.triggerTS )
				text.push( formatTimeDelta(this.currentTS - this.triggerTS) + ' TRG' );
			text.push( '' );	// Blank line to give room for triggerTS line.
			let x = Math.round( (this.xVFromTS(this.currentTS) - this.xVLeft) * this.imageToScreenFactor );
			drawIndicatorLine( x, 'rgb(255,0,0)', text, false );
		}
	}

class CompositePanel:
	def __init__( self, parent ):
		super().__init__( parent )
		
		this.composite = CompositeCtrl( self )
		
		this.leftToRight = wx.Choice( self, choices=('\u27F6 Left to Right', '\u27F5 Right to Left') )
		this.leftToRight.SetSelection( 0 )
		this.leftToRight.Bind( wx.EVT_CHOICE, this.onLeftToRight )
		
		this.trig = wx.CanvasButton(self, canvas=Utils.getCanvas('center-icon.png') )
		this.trig.SetToolTip( wx.ToolTip('Recenter on Trigger Time') )
		this.trig.Bind( wx.EVT_BUTTON, lambda e: this.composite.SetTriggerTS(this.composite.triggerTS) )
		
		this.contrast  = wx.ToggleButton( self, label=('Contrast') )
		this.sharpen   = wx.ToggleButton( self, label=('Sharpen') )
		this.grayscale = wx.ToggleButton( self, label=('Grayscale') )
		
		this.contrast.Bind(		wx.EVT_TOGGLEBUTTON, lambda e: this.composite.SetFilters(contrast=e.IsChecked()) )
		this.sharpen.Bind(		wx.EVT_TOGGLEBUTTON, lambda e: this.composite.SetFilters(sharpen=e.IsChecked()) )
		this.grayscale.Bind(	wx.EVT_TOGGLEBUTTON, lambda e: this.composite.SetFilters(grayscale=e.IsChecked()) )
		
		this.timeSlider = wx.ScrollBar( self, style=wx.SB_HORIZONTAL )
		this.composite.SetSlider( this.timeSlider )
		this.composite.Bind( wx.EVT_MOUSEWHEEL, this.onCompositeWheel )
		
		this.speedSlider = wx.ScrollBar( self, style=wx.SB_VERTICAL )		
		speedMax = 110	// km/h
		thumbSize = 10
		this.speedSlider.SetSlider( 50, thumbSize, speedMax, thumbSize )
		this.speedSlider.Bind( wx.EVT_SCROLL, this.onScrollSpeed )
		
		vs = wx.BoxSizer( wx.VERTICAL )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( this.composite, 1, flag=wx.EXPAND )
		hs.Add( this.speedSlider, 0, flag=wx.EXPAND )
		
		vs.Add( hs, 1, flag=wx.EXPAND )
		
		hs = wx.BoxSizer( wx.HORIZONTAL )
		hs.Add( this.leftToRight, flag=wx.LEFT, border=2 )
		hs.Add( this.trig, flag=wx.LEFT, border=2 )
		hs.Add( this.contrast, flag=wx.LEFT, border=6 )
		hs.Add( this.sharpen, flag=wx.LEFT, border=2 )
		hs.Add( this.grayscale, flag=wx.LEFT, border=2 )
		hs.Add( this.timeSlider, 1, flag=wx.EXPAND, border=2 )
		
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
			ssb = this.speedSlider
			if rot < 0:
				ssb.SetThumbPosition( max(0, ssb.GetThumbPosition() - 1) )
			else:
				ssb.SetThumbPosition( min(ssb.GetRange() - ssb.GetThumbSize(), ssb.GetThumbPosition() + 1) )
			wx.CallAfter( this.onScrollSpeed )
		
	def onScrollSpeed( self, event=null ):
		if this.composite.tsJpgs:
			this.composite.SetPixelsPerSecond( getPixelsPerSecond(
					frameWidthPixels=this.composite.imageWidth,
					speedKMH=this.speedSlider.GetThumbPosition()
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
		
		if !leftToRight:
			jpg = CVUtil.frameToJPeg( cv2.flip( CVUtil.jpegToFrame(jpg), 1 ) )
			
		tsJpgs.push( (ts, jpg) )
	
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

