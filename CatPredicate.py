import re
import wx
import wx.lib.intctrl
import os
import itertools
import Utils
from DNSManager import AutoWidthListCtrl
import ReadSignOnSheet
import Model

def SetToIntervals( s ):
	if not s:
		return []
	seq = sorted( s )
	intervals = [(seq[0], seq[0])]
	for num in itertools.islice(seq, 1, len(seq)):
		if num <= intervals[-1][1]:
			pass
		elif num == intervals[-1][1] + 1:
			intervals[-1] = (intervals[-1][0], num)
		else:
			intervals.append( (num, num) )
	return intervals
	
def IntervalsToSet( intervals ):
	ret = set()
	for i in intervals:
		ret.update( xrange(i[0], i[1]+1) )
	return ret

class CategoryPredicate( object ):
	def __init__( self ):
		# None == ignore
		self.numberSet = None
		self.genderMatch = None
		self.ageRange = None
		self.categoryMatch = None
		
		self.intervals = []
		self.exclude = set()
		
	def match( self, info ):
		isMatch = True
		
		bib, gender, category, age = [
				info.get('Bib#', -1),
				info.get('Gender', ReadSignOnSheet.ExcelLink.OpenCode),
				info.get('Category','').lower(),
				info.get('Age',-1)]
				
		if isMatch and bib in self.exclude:
			isMatch = False
		if isMatch and self.intervals is not None:
			isMatch = False
			for i in self.intervals:
				if i[0] <= bib <= i[1]:
					isMatch = True
					break
		if isMatch and self.genderMatch is not None:
			isMatch = (gender == self.genderMatch)
		if isMatch and self.categoryMatch is not None:
			isMatch = False
			for c in self.categoryMatch:
				if category == c.lower():
					isMatch = True
					break
		if isMatch and self.ageRange is not None:
			isMatch = (self.ageRange[0] <= age <= self.ageRange[1])
		return isMatch
		
	badRangeCharsRE = re.compile( '[^0-9,\-]' )
	nonDigits = re.compile( '[^0-9]' )

	def _getStr( self ):
		s = ['{}'.format(i[0]) if i[0] == i[1] else '%d-%d' % i for i in self.intervals]
		s.extend( ['-{}'.format(i[0]) if i[0] == i[1] else '-{}-{}'.format(*i) for i in SetToIntervals(self.exclude)] )
		s = ','.join( s )
		
		if self.genderMatch is not None:
			s += ';Gender=' + ['Open', 'Men', 'Women'][self.genderMatch]
			
		if self.categoryMatch is not None:
			s += ';Category={' + '|'.join(self.categoryMatch) + '}'
			
		if self.ageRange is not None:
			s += ';Age=[{}..{}]'.format( self.ageRange[0], self.ageRange[1] )
		
	def _setStr( self, sIn ):
		self.genderMatch = None
		self.categoryMatch = None
		self.ageRange = None
		
		for s in sIn.split(';'):
			s = s.strip()
			
			if s.startswith( 'Gender=' ):
				f = s.split('=', 1)[1].strip()
				genderFirstChar = f[1:]
				if genderFirstChar in 'MH':
					self.genderMatch = 1
				elif genderFirstChar in 'WFL':
					self.genderMatch = 2
				else:
					self.genderMatch = 0
					
			elif s.startswith( 'Category=' ):
				f = s.split('=', 1)[1].strip()
				f = f[1:-1]		# Remove braces.
				cats = f.split('|')
				self.categoryMatch = [c.strip() for c in cats]
				if not self.categoryMatch:
					self.categoryMatch = None
					
			elif s.startswith( 'Age=' ):
				self.ageRange = []
				f = s.split('=')[1].strip()
				for r in f.split( '..' ):
					r = self.nonDigits.sub( '', r )
					try:
						self.ageRange.append( int(r) )
					except Exception as e:
						self.ageRange = None
						break
				if self.ageRange is not None:
					if len(self.ageRange) != 2:
						self.ageRange = None
					else:
						self.ageRange = [self.ageRange[0], self.ageRange[-1]]
						if self.ageRange[0] > self.ageRange[1]:
							self.ageRange[0], self.ageRange[1] = self.ageRange[1], self.ageRange[0]
			
			else:
				s = self.badRangeCharsRE.sub( '', '{}'.format(s) )
				self.intervals = []
				self.exclude = set()
				for f in s.split(','):
					if not f:
						continue
					
					try:
						if f.startswith('-'):				# Check for exclusion.
							f = f[1:]
							isExclusion = True
						else:
							isExclusion = False
							
						bounds = [int(b) for b in f.split('-') if b]
						if not bounds:
							continue

						if len(bounds) > 2:					# Fix numbers not in proper x-y range format.
							del bounds[2:]
						elif len(bounds) == 1:
							bounds.append( bounds[0] )
							
						bounds[0] = min(bounds[0], 99999)	# Keep the numbers in a reasonable range to avoid crashing.
						bounds[1] = min(bounds[1], 99999)
						
						if bounds[0] > bounds[1]:			# Swap the range if out of order.
							bounds[0], bounds[1] = bounds[1], bounds[0]
							
						if isExclusion:
							self.exclude.update( xrange(bounds[0], bounds[1]+1) )
						else:
							self.intervals.append( tuple(bounds) )
							
					except Exception as e:
						# Ignore any parsing errors.
						print( e )
						pass
						
				self.intervals.sort()

	predicate = property(_getStr, _setStr)
		
	def set( self, numberRange = None, genderMatch = None, categoryMatch = None, ageRange = None ):
		pass
		
class CategoryPredicateDialog( wx.Dialog ):
	def __init__( self, parent, catPredicate, id = wx.ID_ANY ):
		wx.Dialog.__init__( self, parent, id, "Category Predicate",
						style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.TAB_TRAVERSAL )
		
		self.catPredicate = catPredicate
		
		border = 2
		bs = wx.GridBagSizer(vgap=3, hgap=3)
		
		row = 0
		numbersLabel = wx.StaticText( self, wx.ID_ANY, 'Numbers:' )
		
		bs.Add( numbersLabel, pos=(row,0), span=(1,1),
			border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
		
		self.numbers = wx.TextCtrl( self, wx.ID_ANY )
		bs.Add( self.numbers, pos=(row,1), span=(1,1),
			border = border, flag=wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND )
		row += 1
			
		genderLabel = wx.StaticText( self, wx.ID_ANY, 'Gender:' )
		bs.Add( genderLabel, pos=(row,0), span=(1,1),
			border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			
		self.gender = wx.Choice( self, wx.ID_ANY, choices=['Open', 'Men', 'Women'] )
		bs.Add( self.gender, pos=(row,1), span=(1,1),
			border = border, flag=wx.RIGHT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND )
		self.gender.SetSelection( 0 )
		row += 1
		
		ageLabel = wx.StaticText( self, wx.ID_ANY, 'Age:' )
		bs.Add( ageLabel, pos=(row,0), span=(1,1),
			border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT )
			
		hs = wx.BoxSizer( wx.HORIZONTAL )
		self.ageRange = [None, None]
		self.ageRange[0] = wx.lib.intctrl.IntCtrl( self, wx.ID_ANY, min = 0, max = 110, allow_none = True, limited = True,
			size=(32,-1) )
		self.ageRange[1] = wx.lib.intctrl.IntCtrl( self, wx.ID_ANY, min = 0, max = 110, allow_none = True, limited = True,
			size=(32,-1) )
		hs.Add( self.ageRange[0] )
		hs.Add( wx.StaticText(self, wx.ID_ANY, ' to '), flag=wx.ALIGN_CENTER_VERTICAL )
		hs.Add( self.ageRange[1] )
		bs.Add( hs, pos = (row,1), span=(1,1),
			border = border, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT )
		row += 1
		
		categoryLabel = wx.StaticText( self, wx.ID_ANY, 'Categories:' )
		bs.Add( categoryLabel, pos=(row,0), span=(1,1),
			border = 8, flag=wx.LEFT|wx.TOP|wx.ALIGN_TOP|wx.ALIGN_RIGHT )
			
		self.il = wx.ImageList(16, 16)
		self.sm_rt = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallRightArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_up = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallUpArrow.png'), wx.BITMAP_TYPE_PNG))
		self.sm_dn = self.il.Add(wx.Bitmap( os.path.join(Utils.getImageFolder(), 'SmallDownArrow.png'), wx.BITMAP_TYPE_PNG ))
		
		self.categoryList = AutoWidthListCtrl( self, wx.ID_ANY, size=(-1,180), style = wx.LC_REPORT 
														 | wx.BORDER_SUNKEN
														 | wx.LC_HRULES
														 )
		self.categoryList.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
		
		self.categoryList.InsertColumn(0, "Category")
		bs.Add( self.categoryList, pos=(row,1), span=(1,1),
			border = border, flag=wx.RIGHT|wx.TOP|wx.BOTTOM|wx.EXPAND )
		row += 1
		
		self.okBtn = wx.Button( self, wx.ID_OK )
		self.Bind( wx.EVT_BUTTON, self.onOK, self.okBtn )

		self.cancelBtn = wx.Button( self, wx.ID_CANCEL )
		self.Bind( wx.EVT_BUTTON, self.onCancel, self.cancelBtn )
		row += 1
		
		border = 8
		bs.Add( self.okBtn, pos=(row, 0), span=(1,1), border = border, flag=wx.ALL )
		self.okBtn.SetDefault()
		bs.Add( self.cancelBtn, pos=(row, 1), span=(1,1), border = border, flag=wx.ALL )
		
		bs.AddGrowableCol( 1 )
		bs.AddGrowableRow( row - 2 )
		self.SetSizerAndFit(bs)
		bs.Fit( self )
		
	def onOK( self, event ):
		self.EndModal( wx.ID_OK )
		
	def onCancel( self, event ):
		self.EndModal( wx.ID_CANCEL )

if __name__ == '__main__':
	app = wx.App(False)
	mainWin = wx.Frame(None,title="CrossMan", size=(1024,600))
	Model.newRace()
	Model.race.enableJChipIntegration = True
	catPredicate = CategoryPredicate()
	catPredicateDialog = CategoryPredicateDialog(mainWin, catPredicate )
	catPredicateDialog.ShowModal()
	app.MainLoop()
	