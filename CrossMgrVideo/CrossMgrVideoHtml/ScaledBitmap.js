const contrastColour = 'rgb( 255, 130, 0 )';

function GetScaleRatio( wBitmap, hBitmap, width, height ) {
	return Math.min( width / wBitmap, height / hBitmap );
}

function intervalsOverlap( a0, a1, b0, b1 ) {
	return a0 <= b1 && b0 <= a1;
}

// A rectangle is an array [x, y, width, height].
// These convenience routines get the rectangle corners.
function topRight( r )		{ return [r[0] + r[2], r[1]]; }
function topLeft( r )		{ return [r[0], r[1]]; }
function bottomLeft( r ) 	{ return [r[0], r[1] + r[3]]; }
function bottomRight( r )	{ return [r[0] + r[2], r[1] + r[3]]; }

function intersectRect( a, b ) {
	// Return the intersection rectangle between the two given rectangles.
	// Returns an empty rectangle if there is no intersection.
	const x = Math.max(a[0], b[0]);
	const num1 = Math.min(a[0] + a[2], b[0] + b[2]);
	const y = Math.max(a[1], b[1]);
	const num2 = Math.min(a[1] + a[3], b[1] + b[3]);
	if (num1 >= x && num2 >= y)
		return [x, y, num1 - x, num2 - y];
	else
		return [0,0,0,0];
}

class ScaledBitmap {
	constructor( canvas, image=null, drawFinishLine=false, inset=true, drawCallback=null ) {
		this.canvas = canvas;
		this.SetImage( image );
		this.mouseButtonDown = false;
		this.background = 'rgb(232,232,232)';
		this.resetMagRect();
		canvas.addEventListener('resize', this.OnSize.bind(this) );

		this.drawFinishLine = drawFinishLine;
		this.drawCallback = drawCallback
		
		this.eventCache = [];
		if( inset ) {
			canvas.addEventListener('pointerdown', this.OnPointerDown.bind(this), false);
			canvas.addEventListener('pointermove', this.OnPointerMove.bind(this), false);
			canvas.addEventListener('pointerup', this.OnPointerUp.bind(this), false);
			canvas.addEventListener('pointercancel', this.OnPointerUp.bind(this), false);
			canvas.addEventListener('pointerleave', this.OnPointerUp.bind(this), false);
		}
		this.Refresh();
	}
	
	resetMagRect() {
		this.beginX = 0;
		this.beginY = 0;
		this.endX = 0;
		this.endY = 0;
		this.sourceRect = [0,0,0,0];
	}
	
	getMagRect() {
		return [Math.min(this.beginX, this.endX), Math.min(this.beginY, this.endY), Math.abs(this.endX-this.beginX), Math.abs(this.endY-this.beginY)];
	}
	
	OnSize( event ) {
		this.resetMagRect();
		this.Refresh();overflow:scroll;
	}
	
	OnPointerDown( event ) {
		if( event.pointerType == 'mouse' && (event.buttons != 1) )	// Ignore all mouse events except for left button.
			return;
		
		this.eventCache.push( event );
		if( this.eventCache.length == 1 ) {
			//console.log( 'OnPointerDown: initializing zoom' );
			this.beginX = this.endX = this.eventCache[0].offsetX;
			this.beginY = this.endY = this.eventCache[0].offsetY;
			this.Refresh();
			
			this.mouseButtonDown = (event.pointerType == 'mouse' && (event.buttons == 1));
			this.canvas.style.cursor = 'zoom-in';
		}
		else {
			//console.log( 'OnPointerDown: pinch zoom point' );
			this.OnPointerMove( event );
		}
	}
	
	OnPointerMove( event ) {
		const i = this.eventCache.findIndex( e => e.pointerId == event.pointerId );
		if( i >= 0 )
			this.eventCache[i] = event;
		
		if( this.eventCache.length == 1 ) {
			if( this.mouseButtonDown ) {
				//console.log( 'OnPointerMove: mouse expand zoom' );
				this.endX   = this.eventCache[0].offsetX;
				this.endY   = this.eventCache[0].offsetY;
				this.Refresh();
			}
		}
		else if( this.eventCache.length >= 2 ) {
			//console.log( 'OnPointerMove: pinch expand zoom' );
			this.beginX = this.beginY = Number.POSITIVE_INFINITY;
			this.endX   = this.endY   = Number.NEGATIVE_INFINITY;
			for( let i = 0; i < this.eventCache.length; ++i ) {
				const offsetX = this.eventCache[i].offsetX, offsetY = this.eventCache[i].offsetY;
				this.beginX  = Math.min( this.beginX, offsetX );
				this.beginY  = Math.min( this.beginY, offsetY );
				this.endX    = Math.max( this.endX,   offsetX );
				this.endY    = Math.max( this.endY,   offsetY );
			}
			this.Refresh();
		}
	}
	
	OnPointerUp( event ) {
		const i = this.eventCache.findIndex( e => e.pointerId == event.pointerId );
		if( i >= 0 )
			this.eventCache.splice(i, 1);
			
		if( this.eventCache.length == 0 ) {
			this.canvas.style.cursor = 'auto';
			this.mouseButtonDown = false;
		}
		else
			this.OnPointerMove( this.eventCache[0] );
	}
	
	getInsetRect( width, height, isWest, isNorth ) {
		const r = 0.75;
		const insetWidth = width*r, insetHeight = height*r;
		return [!isWest ? 0 : width - insetWidth, !isNorth ? 0 : height - insetHeight, insetWidth, insetHeight];
	}
	
	GetSourceRect() {
		// Returns the zoom rectangle in photo pixel coordinates.
		return this.sourceRect;
	}
	
	SetSourceRect( rect ) {
		// Sets the zoom rectangle, given in photo pixel coordinates.
		if( rect[2] == 0 || rect[3] == 0 || !this.image ) {
			this.resetMagRect();
			this.Refresh();
			return;
		}
			
		let sourceImage = this.image;
		const sourceWidth = sourceImage.width, sourceHeight = sourceImage.height;
		const ratio = GetScaleRatio( sourceWidth, sourceHeight, this.canvas.width, this.canvas.height );
		const destWidth = sourceWidth * ratio, destHeight = sourceHeight * ratio;

		const xLeft = Math.max(0, (this.canvas.width - destWidth)/2);
		const yTop = Math.max(0, (this.canvas.height - destHeight)/2);

		this.beginX = xLeft + rect[0] * ratio;
		this.beginY = yTop + rect[1] * ratio;
		this.endX = this.beginX + rect[2] * ratio;
		this.endY = this.beginY + rect[3] * ratio;
		
		this.Refresh();
	}
	
	draw( dc, width, height ) {
		// Clear the canvas.
		dc.beginPath();
		dc.rect( 0, 0, width, height );
		dc.fillStyle = '#000';
		dc.fill();
		
		if( !this.image ) {
			this.drawTestImage( dc, width, height );
			return;
		}
		
		// Draw the image in the canvas.
		let sourceImage = this.image;
		const sourceWidth = sourceImage.width, sourceHeight = sourceImage.height;
		const ratio = GetScaleRatio( sourceWidth, sourceHeight, width, height );
		const destWidth = sourceWidth * ratio, destHeight = sourceHeight * ratio;

		const xLeft = Math.max(0, (width - destWidth)/2);
		const yTop = Math.max(0, (height - destHeight)/2);
		if( sourceWidth > 0 && sourceHeight > 0 && destWidth > 0 && destHeight > 0 )
			dc.drawImage( sourceImage, 0, 0, sourceWidth, sourceHeight, xLeft, yTop, destWidth, destHeight );
		
		if( this.drawFinishLine ) {
			dc.strokeStyle = contrastColour;
			dc.lineWidth = 1;
			dc.beginPath();
			dc.moveTo( width/2, 0 );
			dc.lineTo( width/2, height );
			dc.stroke();
		}
		
		// Draw the magnifying rectangle.
		const magnifyRect = this.getMagRect();
		if( magnifyRect[2] <= 0 || magnifyRect[3] <= 0 )
			return;
			
		let sourceRect = intersectRect(
			[0, 0, sourceWidth, sourceHeight],
			[(magnifyRect[0] - xLeft)/ratio, (magnifyRect[1]-yTop)/ratio, magnifyRect[2]/ratio, magnifyRect[3]/ratio]
		);
		
		if( sourceRect[2] <= 0 || sourceRect[3] <= 0 )
			return;
			
		this.sourceRect = sourceRect;
			
		const xCenter = sourceRect[0] + sourceRect[2] / 2, yCenter = sourceRect[1] + sourceRect[3] / 2;
		const isWest = xCenter < this.image.width/2, isNorth = yCenter < this.image.width/2;
		let insetRect = this.getInsetRect( width, height, isWest, isNorth );
		
		const magRatio = GetScaleRatio( sourceRect[2], sourceRect[3], insetRect[2], insetRect[3] );
		const iWidth = sourceRect[2] * magRatio, iHeight = sourceRect[3] * magRatio;
		insetRect = [
			insetRect[0] != 0 ? insetRect[0] + insetRect[2] - iWidth : 0,
			insetRect[1] != 0 ? insetRect[1] + insetRect[3] - iHeight : 0,
			iWidth, iHeight
		];
		
		dc.drawImage( sourceImage, ...sourceRect, ...insetRect );

		// Draw the outlines.
		dc.strokeStyle = 'rgb(200,200,0)';
		dc.lineWidth = 2;

		dc.beginPath();
		dc.rect( ...insetRect );
		dc.rect( ...magnifyRect );
		dc.stroke();
		
		// Draw the direction lines.
		function drawLine( p1, p2 ) {
			dc.moveTo( ...p1 );
			dc.lineTo( ...p2 );
		}
				
		if( intervalsOverlap(magnifyRect[0], magnifyRect[0] + magnifyRect[2], insetRect[0], insetRect[0] + insetRect[2]) ) {
			if( intervalsOverlap(magnifyRect[1], magnifyRect[1] + magnifyRect[3], insetRect[1], insetRect[1] + insetRect[3]) )
				return;
				
			dc.beginPath();
			if( isNorth ) {
				drawLine( bottomLeft(magnifyRect), topLeft(insetRect) );				
				drawLine( bottomRight(magnifyRect), topRight(insetRect) );
			}
			else {
				drawLine( topLeft(magnifyRect), bottomLeft(insetRect) );
				drawLine( topRight(magnifyRect), bottomRight(insetRect) );
			}
			dc.stroke();
		}
		else {
			dc.beginPath();
			if( isWest ) {
				drawLine( topRight(magnifyRect), topLeft(insetRect) );
				drawLine( bottomRight(magnifyRect), bottomLeft(insetRect) );
			}
			else {
				drawLine( topLeft(magnifyRect), topRight(insetRect) );
				drawLine( bottomLeft(magnifyRect), bottomRight(insetRect) );
			}
			dc.stroke();
		}
	}
	
	drawTestImage( dc, width, height ) {
		let colours = [
			'rgb(255,255,255)', 'rgb(255,0,0)', 'rgb(0,255,0)', 'rgb(0,0,255)',
			'rgb(255,255,0)', 'rgb(255,0,255)', 'rgb(0,255,255)', 'rgb(0,0,0)'
		];
		let x, y;
		const rWidth = width / colours.length;
		for( let row = 0; row < 2; ++row ) {
			y = (row == 0 ? 0 : height * 0.75);
			let hCur = (row == 0 ? height * 0.75 : height * 0.25);
			for( let col = 0; col < colours.length; ++col ) {
				dc.beginPath();
				dc.rect( rWidth * col, y, rWidth+1, hCur );
				dc.fillStyle = colours[col];
				dc.fill();
			}
			colours.reverse();
		}
		
		const r = Math.min(width, height) / 3;
		x = width / 2;
		y = height / 2;
		const angle = 2.0*Math.PI / colours.length;
		for( let i = 0; i < colours.length; ++i ) {
			dc.beginPath();
			dc.moveTo( x, y );
			dc.lineTo( x + r * Math.cos(angle*i), y + r * Math.sin(angle*i) );
			dc.arc( x, y, r, angle*i, angle*(i+1), false);
			dc.closePath();
			dc.fillStyle = colours[i];
			dc.fill();
		}
	}
	
	SetImage( image ) {
		this.image = image;
		this.Refresh()
	}
	
	SetToEmpty() {
		this.SetImage( null );
	}
		
	Refresh() {
		this.draw( this.canvas.getContext('2d'), this.canvas.width, this.canvas.height );
		if( this.drawCallback )
			this.drawCallback( this.canvas );
	}
};
