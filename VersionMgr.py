
import wx
import urllib2
import socket
import re
import os
import time
import Utils
import Version

urlRoot = "http://sites.google.com/site/crossmgrsoftware"

def getVersionFileName():
	return os.path.join(Utils.getHomeDir(), 'CurrentVersion.txt')
	
def resetVersionCache( fname = None ):
	if not fname:
		fname = getVersionFileName()
		
	try:
		os.remove( fname )
	except:
		pass

def isUpgradeRecommended( fname = None ):
	''' Check if an upgrade is recommended to the current version. '''
	# Check the NextVersion file.
	if not fname:
		fname = getVersionFileName()
		
	try:
		with open(fname, 'rb') as f:
			for line in f:
				verMax = tuple( int(n) for n in line.split('.') )

			# Get the current version.
			verCur = tuple( int(n) for n in re.search(" (\d+\.\d+)", Version.AppVerName).group(1).split('.') )
			
			if verCur < verMax:
				return True
	except:
		pass
	return False
	
def updateVersionCache( fname = None ):
	''' Write the next version to the cache. '''
	# If an upgrade is already required, don't check over the internet again.
	if not fname:
		fname = getVersionFileName()
		
	if isUpgradeRecommended(fname):
		return
	
	# If we already checked in the last few days, don't check again.
	try:
		if time.time() < os.path.getmtime(fname) + (3 * 24 * 60 * 60):
			return
	except:
		pass
		
	timeoutSave = socket.getdefaulttimeout()
	socket.setdefaulttimeout( 20.0 )
		
	try:
		# Get all the zip files from the downloads page.
		reZipFile = re.compile( "CrossMgr[^'.]*\.zip" )
		zips = set()

		p = urllib2.urlopen(urlRoot + '/file-cabinet').read()
		for line in p.split('\n'):
			for m in reZipFile.findall(line):
				zips.add( m )
		
		# Extract the version number from the zip files.
		reVersion = re.compile( "_v(\d+_\d+)" )
		vers = []
		for zip in zips:
			try:
				ver = reVersion.search(zip).group(1)
				vers.append( tuple(int(n) for n in ver.split('_')) )
			except:
				pass
		
		# Get the max version number.
		verMax = max(vers)
		
		# Write the max version into the cache file.
		with open( fname, 'wb' ) as f:
			f.write( '.'.join( str(n) for n in verMax ) )
			f.write( '\n' )
		
	except:
		pass
		
	socket.setdefaulttimeout( timeoutSave )
	
if __name__ == '__main__':
	app = wx.PySimpleApp()
	resetVersionCache()
	updateVersionCache()
	print open(getVersionFileName()).read()
	print isUpgradeRecommended()
	Version.AppVerName = "CrossMgr 1.11"
	updateVersionCache()
	print isUpgradeRecommended()
	Version.AppVerName = "CrossMgr 2.11"
	updateVersionCache()
	print isUpgradeRecommended()
	with open( getVersionFileName(), 'wb' ) as f:
		f.write( '3.15\n' )
	print isUpgradeRecommended()
