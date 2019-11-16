import wx
import os
import wx.grid as gridlib
import wx.lib.mixins.gridlabelrenderer as glr
import wx.lib.mixins.grid as gae
import Utils

class GridCellMultiLineStringRenderer(gridlib.GridCellRenderer):   
	def __init__(self):
		gridlib.GridCellRenderer.__init__(self)

	def Draw(self, grid, attr, dc, rect, row, col, isSelected):
		text = grid.GetCellValue(row, col)
		dc.SetFont( attr.GetFont() ) 
		hAlign, vAlign = attr.GetAlignment()       
		if isSelected: 
			bg = grid.GetSelectionBackground() 
			fg = grid.GetSelectionForeground() 
		else: 
			bg = attr.GetBackgroundColour()
			fg = attr.GetTextColour() 
		dc.SetTextBackground(bg) 
		dc.SetTextForeground(fg)
		dc.SetBrush(wx.Brush(bg, wx.SOLID))
		dc.SetPen(wx.TRANSPARENT_PEN)
		dc.DrawRectangle(rect)            
		grid.DrawTextRectangle(dc, text, rect, hAlign, vAlign)

	def GetBestSize(self, grid, attr, dc, row, col): 
		text = grid.GetCellValue(row, col)
		dc.SetFont(attr.GetFont())
		w, h, lineHeight = dc.GetMultiLineTextExtent(text)                   
		return wx.Size(w, h)        

	def Clone(self): 
		return GridCellMultiLineStringRenderer()

class ReorderableGridRowMixin( object ):
	"""This mixin allows the use of grid rows as Rearrange sources, you can Rearrange
	rows off of a grid to a text target.  Only row labels are Rearrangegable, internal
	cell contents are not.

	You must Initialize this class *after* the wxGrid initialization.
	example
	class MyGrid(Grid, ReorderableGridRowMixin):
		def __init__(self, parent, id):
			Grid.__init__(self, parent, id)
			ReorderableGridRowMixin.__init__(self)
	"""
	def __init__( self ):
		rowWindow = self.GetGridRowLabelWindow()
		# various flags to indicate whether we should have a select
		# event or a Rearrange event
		self._potentialRearrange = False
		self._lastRow = None
		self._enableReorderRows = True

		rowWindow.Bind( wx.EVT_LEFT_DOWN, self.OnReorderableGridLeftDown )
		rowWindow.Bind( wx.EVT_LEFT_UP, self.OnRearrangeEnd )
		rowWindow.Bind( wx.EVT_MOTION, self.OnReorderableGridMotion )
		
		self.Bind( wx.EVT_LEFT_UP, self.OnRearrangeEnd )
		self.Bind( wx.EVT_MOTION, self.OnRearrangeEnd )
		
		gridWindow = self.GetGridWindow()
		gridWindow.Bind( wx.EVT_LEFT_UP, self.OnRearrangeEnd )
		gridWindow.Bind( wx.EVT_MOTION, self.OnRearrangeEnd )

	def EnableReorderRows( self, enableReorderRows ):
		self._enableReorderRows = enableReorderRows
		
	def OnReorderableGridLeftDown(self, evt):
		if not self._enableReorderRows:
			self._potentialRearrange = False
			evt.Skip()
			return
			
		x,y = evt.GetX(), evt.GetY()
		row, col = self.ReorderableGridRowXYToCell(x,y, colheight=0)
		
		self.SaveEditControlValue()
		self.DisableCellEditControl()
		self.SetFocus()
		
		self._lastRow = row
		self.ClearSelection()
		self.SelectRow(row, True)
		self._potentialRearrange = True
		evt.Skip()

	def OnRearrangeEnd(self, evt):
		"""We are not Rearranging anymore, so unset the potentialRearrange flag"""
		self._potentialRearrange = False
		evt.Skip()

	def copyRow( self, fromRow, toRow ):
		for c in range(self.GetNumberCols()):
			self.SetCellValue( toRow, c, self.GetCellValue(fromRow, c) )
			self.SetCellBackgroundColour( toRow, c, self.GetCellBackgroundColour(fromRow, c) )
		
	def OnReorderableGridMotion(self, evt):
		"""We are moving so see whether this should be a Rearrange event or not"""
		if not self._potentialRearrange:
			evt.Skip()
			return

		if not self._enableReorderRows:
			self._potentialRearrange = False
			evt.Skip()
			return
			
		x, y = evt.GetX(), evt.GetY()
		row, col = self.ReorderableGridRowXYToCell(x,y, colheight=0)
		if row == self._lastRow:
			return
			
		self.DeselectRow( self._lastRow )
		
		lastRowSave = [self.GetCellValue(self._lastRow, c) for c in range(self.GetNumberCols())]
		lastRowBackgroundColourSave = [self.GetCellBackgroundColour(self._lastRow, c) for c in range(self.GetNumberCols())]
		direction = 1 if row > self._lastRow else -1 if row < self._lastRow else 0
		for r in range(self._lastRow, row, direction ):
			self.copyRow( r + direction, r )
		for c in range(self.GetNumberCols()):
			self.SetCellValue( row, c, lastRowSave[c] )
			self.SetCellBackgroundColour( row, c, lastRowBackgroundColourSave[c] )
		
		self.SelectRow( row, False )
		self._lastRow = row

	def ReorderableGridRowXYToCell(self, x, y, colheight=None, rowwidth=None):
		# For virtual grids, XYToCell doesn't work properly
		# For some reason, the width and heights of the labels
		# are not computed properly and thw row and column
		# returned are computed as if the window wasn't
		# scrolled
		# This function replaces XYToCell for Virtual Grids
		row = col = 0

		if rowwidth is None:
			rowwidth = self.GetGridRowLabelWindow().GetRect().width
		if colheight is None:
			colheight = self.GetGridColLabelWindow().GetRect().height
		yunit, xunit = self.GetScrollPixelsPerUnit()
		xoff =  self.GetScrollPos(wx.HORIZONTAL) * xunit
		yoff = self.GetScrollPos(wx.VERTICAL) * yunit

		# the solution is to offset the x and y values
		# by the width and height of the label windows
		# and then adjust by the scroll position
		# Then just go through the columns and rows
		# incrementing by the current column and row sizes
		# until the offset points lie within the computed
		# bounding boxes.
		x += xoff - rowwidth
		xpos = 0
		for col in range(self.GetNumberCols()):
			nextx = xpos + self.GetColSize(col)
			if xpos <= x <= nextx:
				break
			xpos = nextx

		y += yoff - colheight
		ypos = 0
		for row in range(self.GetNumberRows()):
			nexty = ypos + self.GetRowSize(row)
			if ypos <= y <= nexty:
				break
			ypos = nexty

		return row, col

class KeyboardNavigationGridMixin( object ):
	def __init__( self ):
		self.Bind( gridlib.EVT_GRID_EDITOR_CREATED, self.onCellEdit )
		
	def onCellEdit( self, event ):
		editor = event.GetControl()
		editor.Bind( wx.EVT_KEY_DOWN, self.onEditorKey )
		event.Skip()
		
	def onEditorKey( self, event ):
		keycode = event.GetKeyCode()
		if keycode == wx.WXK_UP:
			self.MoveCursorUp(False)
		elif keycode == wx.WXK_DOWN:
			self.MoveCursorDown(False)
		elif keycode == wx.WXK_TAB:
			if event.ShiftDown():
				if self.GetGridCursorCol() == 0 and self.GetGridCursorRow() != 0:
					self.MoveCursorUp(False)
					for c in range(self.GetNumberCols()):
						self.MoveCursorRight(False)
				else:
					self.MoveCursorLeft(False)
			else:
				if self.GetGridCursorCol() == self.GetNumberCols() - 1 and self.GetGridCursorRow() != self.GetNumberRows() - 1:
					self.MoveCursorDown(False)
					for c in range(self.GetNumberCols()):
						self.MoveCursorLeft(False)
				else:
					self.MoveCursorRight(False)
		else:
			pass
		event.Skip()

class SaveEditWhenFocusChangesGridMixin( object ):
	def __init__(self):
		self.Bind(gridlib.EVT_GRID_EDITOR_CREATED, self.OnGridEditorCreated)

	def OnGridEditorCreated(self, event):
		""" Bind the kill focus event to the newly instantiated cell editor """
		editor = event.GetControl()
		if not isinstance(editor, wx.ComboBox):
			editor.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
		event.Skip()

	def OnKillFocus(self, event):
		# Cell editor's grandparent, the grid GridWindow's parent, is the grid.
		grid = event.GetEventObject().GetGrandParent()
		grid.SaveEditControlValue()
		grid.DisableCellEditControl()
		event.Skip()
		
#-----------------------------------------------------------------------------
class CornerReorderableGridLabelRenderer(glr.GridLabelRenderer):
	def __init__(self):
		self._bmp = wx.Bitmap( os.path.join(Utils.getImageFolder(), 'UpDown.png'), wx.BITMAP_TYPE_PNG )
		
	def Draw(self, grid, dc, rect, rc):
		if grid._enableReorderRows:
			x = rect.left + (rect.width - self._bmp.GetWidth()) / 2
			y = rect.top + (rect.height - self._bmp.GetHeight()) / 2
			dc.DrawBitmap(self._bmp, x, y, True)

class ReorderableGrid(	gridlib.Grid,
						ReorderableGridRowMixin,
						KeyboardNavigationGridMixin,
						SaveEditWhenFocusChangesGridMixin,
						glr.GridWithLabelRenderersMixin,
						gae.GridAutoEditMixin ):
	def __init__( self, parent, style = 0 ):
		gridlib.Grid.__init__( self, parent, style=style )
		ReorderableGridRowMixin.__init__( self )
		KeyboardNavigationGridMixin.__init__( self )
		SaveEditWhenFocusChangesGridMixin.__init__( self )
		glr.GridWithLabelRenderersMixin.__init__(self)
		gae.GridAutoEditMixin.__init__(self)
		
		self.SetCornerLabelRenderer(CornerReorderableGridLabelRenderer())
		
	def GetSelectedRows( self ):
		rows=[] 
		gcr=self.GetGridCursorRow() 
		set1=self.GetSelectionBlockTopLeft() 
		set2=self.GetSelectionBlockBottomRight() 
		if len(set1): 
			assert len(set1)==len(set2) 
			for i in range(len(set1)): 
				for row in range(set1[i][0], set2[i][0]+1): # range in wx is inclusive of last element 
					if row not in rows: 
						rows.append(row) 
		else: 
			 rows.append(gcr) 
		return rows 
	
