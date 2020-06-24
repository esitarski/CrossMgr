import wx
import os
import base64
import Utils

def GetFlagFName( ioc ):
	return os.path.join( Utils.getImageFolder(), 'flags', ioc + '.png' )

flagImageCache = {}
def GetFlagImage( ioc ):
	ioc = ioc.upper()
	try:
		return flagImageCache[ioc]
	except KeyError:
		pass
	
	fname = GetFlagFName( ioc )
	if not os.path.exists(fname):
		flagImageCache[ioc] = None
	else:
		flagImageCache[ioc] = wx.Image( fname, wx.BITMAP_TYPE_PNG )
		
	return flagImageCache[ioc]

flagBase64Cache = {}
def GetFlagBase64( ioc ):
	ioc = ioc.upper()
	try:
		return flagBase64Cache[ioc]
	except KeyError:
		pass
	
	fname = GetFlagFName( ioc )
	try:
		with open(fname, 'rb') as f:
			flagBase64Cache[ioc] = 'data:image/png;base64,{}'.format(base64.standard_b64encode(f.read()))
	except:
		flagBase64Cache[ioc] = None
		
	return flagBase64Cache[ioc]
	
def GetFlagBase64ForUCI( codes ):
	flags = {}
	for c in codes:
		ioc = c[:3]
		if ioc not in flags:
			flag = GetFlagBase64( ioc )
			if flag:
				flags[ioc] = flag
	return flags
	
if __name__ == '__main__':
	print( GetFlagBase64( 'CAN' ) )
	print( GetFlagBase64( 'USA' ) )
	print( GetFlagBase64( 'SUI' ) )
	print( GetFlagBase64ForUCI( ['CAN19920203', 'USA19870407', 'SUI20020905'] ) )
