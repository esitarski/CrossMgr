import Model
import datetime
import wx
import os
import re
import sys
import math
import subprocess
import unicodedata
import webbrowser
import wx.grid		as gridlib
try:
	from win32com.shell import shell, shellcon
except ImportError:
	pass

def removeDiacritic(input):
	'''
	Accept a unicode string, and return a normal string (bytes in Python 3)
	without any diacritical marks.
	'''
	if type(input) == str:
		return input
	else:
		return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')
	
def PlaySound( soundFile ):
	if mainWin and not mainWin.playSounds:
		return True
		
	soundFile = os.path.join( getImageFolder(), soundFile )
	if sys.platform.startswith('linux'):
		try:
			subprocess.Popen(['aplay', '-q', soundFile])
		except:
			pass
		return True
	else:
		return wx.Sound.PlaySound( soundFile )

def GetSelectedRows( grid ): 
	rows = [] 
	rowSet = set()
	gcr = grid.GetGridCursorRow() 
	set1 = grid.GetSelectionBlockTopLeft() 
	set2 = grid.GetSelectionBlockBottomRight() 
	if len(set1): 
		assert len(set1)==len(set2) 
		for i in range(len(set1)): 
			for row in range(set1[i][0], set2[i][0]+1): # range in wx is inclusive of last element 
				if row not in rowSet: 
					rows.append( row ) 
					rowSet.add( row )
	else: 
		rows.append(gcr) 
	return rows 

'''
wx.ICON_EXCLAMATION	Shows an exclamation mark icon.
wx.ICON_HAND	Shows an error icon.
wx.ICON_ERROR	Shows an error icon - the same as wxICON_HAND.
wx.ICON_QUESTION	Shows a question mark icon.
wx.ICON_INFORMATION	Shows an information (i) icon.
'''

def MessageOK( parent, message, title = '', iconMask = wx.ICON_INFORMATION, pos = wx.DefaultPosition ):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | iconMask, pos)
	dlg.ShowModal()
	dlg.Destroy()
	return True
	
def MessageOKCancel( parent, message, title = '', iconMask = wx.ICON_QUESTION):
	dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.CANCEL | iconMask )
	response = dlg.ShowModal()
	dlg.Destroy()
	return True if response == wx.ID_OK else False
	
def SetValue( st, value ):
	if st.GetValue() != value:
		st.SetValue( value )
		return True
	return False

def SetLabel( st, label ):
	if st.GetLabel() != label:
		st.SetLabel( label )
		return True
	return False

def MakeGridReadOnly( grid ):
	attr = gridlib.GridCellAttr()
	attr.SetReadOnly()
	for c in xrange(grid.GetNumberCols()):
		grid.SetColAttr( c, attr )

def SwapGridRows( grid, r, rTarget ):
	if r != rTarget and 0 <= r < grid.GetNumberRows() and 0 <= rTarget < grid.GetNumberRows():
		for c in xrange(grid.GetNumberCols()):
			vSave = grid.GetCellValue( rTarget, c )
			grid.SetCellValue( rTarget, c, grid.GetCellValue(r,c) )
			grid.SetCellValue( r, c, vSave )
		
def AdjustGridSize( grid, rowsRequired = None, colsRequired = None ):
	# print( 'AdjustGridSize: rowsRequired=', rowsRequired, ' colsRequired=', colsRequired )

	if rowsRequired is not None:
		rowsRequired = int(rowsRequired)
		d = grid.GetNumberRows() - rowsRequired
		if d > 0:
			grid.DeleteRows( rowsRequired, d )
		elif d < 0:
			grid.AppendRows( -d )

	if colsRequired is not None:
		colsRequired = int(colsRequired)
		d = grid.GetNumberCols() - colsRequired
		if d > 0:
			grid.DeleteCols( colsRequired, d )
		elif d < 0:
			grid.AppendCols( -d )

def formatTime( secs, highPrecision = False ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	if highPrecision:
		decimal = '.%02d' % int( f * 100 )
	else:
		decimal = ''
	if hours > 0:
		return "%s%d:%02d:%02d%s" % (sign, hours, minutes, secs, decimal)
	else:
		return "%s%02d:%02d%s" % (sign, minutes, secs, decimal)

def formatTimeGap( secs, highPrecision = False ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	if highPrecision:
		decimal = '.%02d' % int( f * 100 )
	else:
		decimal = ''
	if hours > 0:
		return "%s%dh%d'%02d%s\"" % (sign, hours, minutes, secs, decimal)
	else:
		return "%s%d'%02d%s\"" % (sign, minutes, secs, decimal)

def formatTimeCompressed( secs, highPrecision = False ):
	f = formatTime( secs, highPrecision )
	if f[0] == '0':
		return f[1:]
	return f
		
def formatDate( date ):
	y, m, d = date.split('-')
	d = datetime.date( int(y,10), int(m,10), int(d,10) )
	return d.strftime( '%B %d, %Y' )
		
def StrToSeconds( str = '' ):
	secs = 0.0
	for f in str.split(':'):
		f = f.replace( ' ', '' )
		secs = secs * 60.0 + (float(f) if f else 0.0)
	return secs
	
def SecondsToStr( secs = 0 ):
	secs = int(secs)
	return '%02d:%02d:%02d' % (secs // (60*60), (secs // 60)%60, secs % 60)

def SecondsToMMSS( secs = 0 ):
	secs = int(secs)
	return '%02d:%02d' % ((secs // 60)%60, secs % 60)

def ordinal( value ):
	"""
	Converts zero or a *postive* integer (or their string 
	representations) to an ordinal value.

	>>> for i in range(1,13):
	...	 ordinal(i)
	...	 
	'1st'
	'2nd'
	'3rd'
	'4th'
	'5th'
	'6th'
	'7th'
	'8th'
	'9th'
	'10th'
	'11th'
	'12th'

	>>> for i in (100, '111', '112',1011):
	...	 ordinal(i)
	...	 
	'100th'
	'111th'
	'112th'
	'1011th'

	"""
	try:
		value = int(value)
	except ValueError:
		return value

	if (value % 100)//10 != 1:
		return "%d%s" % (value, ['th','st','nd','rd','th','th','th','th','th','th'][value%10])
	return "%d%s" % (value, "th")
	
def getHomeDir():
	sp = wx.StandardPaths.Get()
	homedir = sp.GetUserDataDir()
	try:
		if os.path.basename(homedir) == '.CrossMgr':
			homedir = os.path.join( os.path.dirname(homedir), '.CrossMgrApp' )
	except:
		pass
	if not os.path.exists(homedir):
		os.makedirs( homedir )
	return homedir

def getDocumentsDir():
	sp = wx.StandardPaths.Get()
	return sp.GetDocumentsDir()
	
#------------------------------------------------------------------------
try:
	dirName = os.path.dirname(os.path.abspath(__file__))
except:
	dirName = os.path.dirname(os.path.abspath(sys.argv[0]))

if os.path.basename(dirName) == 'library.zip':
	dirName = os.path.dirname(dirName)
imageFolder = os.path.join(dirName, 'images')
htmlFolder = os.path.join(dirName, 'html')
helpFolder = os.path.join(dirName, 'htmldoc')

def getDirName():		return dirName
def getImageFolder():	return imageFolder
def getHtmlFolder():	return htmlFolder
def getHelpFolder():	return helpFolder

def showHelp( url ):
	url = os.path.join( getHelpFolder(), url )
	webbrowser.open( url, new = 0, autoraise = True )

#------------------------------------------------------------------------

reSpace = re.compile(r'\s')
def approximateMatch( s1, s2 ):
	s1 = reSpace.sub( '', s1 ).lower()
	s2 = reSpace.sub( '', s2 ).lower()
	if s1[-1].isdigit():
		return 1.2 if s1 == s2 else 0.0
	if s1.startswith(s2) or s2.startswith(s1):
		return 1.1
	return len(set(s1) & set(s2)) / float(len(s1) + len(s2))
	
#------------------------------------------------------------------------
def writeLog( message ):
	try:
		dt = datetime.datetime.now()
		dt = dt.replace( microsecond = 0 )
		sys.stdout.write( '%s %s%s' % (dt.isoformat(), message, '\n' if not message or message[-1] != '\n' else '' ) )
		sys.stdout.flush()
	except IOError:
		pass

def disable_stdout_buffering():
	fileno = sys.stdout.fileno()
	temp_fd = os.dup(fileno)
	sys.stdout.close()
	os.dup2(temp_fd, fileno)
	os.close(temp_fd)
	sys.stdout = os.fdopen(fileno, "w", 0)
		
def logCall( f ):
	def new_f( *args, **kwargs ):
		writeLog( 'call: %s' % f.__name__ )
		return f( *args, **kwargs)
	return new_f
#------------------------------------------------------------------------
mainWin = None
def setMainWin( mw ):
	global mainWin
	mainWin = mw
	
def getMainWin():
	return mainWin

def refresh():
	if mainWin is not None:
		mainWin.refresh()

def refreshForecastHistory():
	if mainWin is not None:
		mainWin.forecastHistory.refresh()

def updateUndoStatus():
	if mainWin is not None:
		mainWin.updateUndoStatus()

def writeRace():
	if mainWin is not None:
		mainWin.writeRace()
	
def getFileName():
	return mainWin.fileName if mainWin is not None else None
	
def isMainWin():
	return mainWin is not None
	
def highPrecisionTimes():
	try:
		return Model.race.highPrecisionTimes
	except AttributeError:
		return False

def setCategoryChoice( iSelection, categoryAttribute = None ):
	try:
		setCategoryChoice = Model.race.setCategoryChoice
	except AttributeError:
		return
	setCategoryChoice( iSelection, categoryAttribute )

def hasTrailingSeparator( menu ):
	itemCount = menu.GetMenuItemCount()
	return itemCount > 0 and menu.FindItemByPosition(itemCount-1).IsSeparator()
	
def addMissingSeparator( menu ):
	if not hasTrailingSeparator(menu):
		menu.AppendSeparator()
	
def deleteTrailingSeparators( menu ):
	while hasTrailingSeparator(menu):
		menu.DeleteItem( menu.FindItemByPosition(menu.GetMenuItemCount()-1) )
	
def AlignHorizontalScroll( gFrom, gTo ): 
	xFrom, yFrom = gFrom.GetViewStart()
	xTo,   yTo   = gTo.GetViewStart()
	gTo.Scroll( xFrom, yTo )
	
def AlignVerticalScroll( gFrom, gTo ): 
	xFrom, yFrom = gFrom.GetViewStart()
	xTo,   yTo   = gTo.GetViewStart()
	gTo.Scroll( xTo, yFrom )

def LayoutChildResize( child ):
	parent = child.GetParent()
	while parent:
		parent.Layout()
		if parent.IsTopLevel():
			break
		parent = parent.GetParent()
			
def CombineFirstLastName( firstName, lastName ):
	if lastName:
		if firstName:
			return '%s, %s' % (lastName, firstName)
		else:
			return lastName
	else:
		return firstName
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	hd = getHomeDir()
	fn = os.path.join(hd, 'Test.txt')
	with open( fn, 'w' ) as fp:
		print 'successfully opened: ' + fn
