import wx
import os
import sys
from Version import AppVerName

dirNames = {}

def GetFolders():
	if not dirNames:
		AppName = AppVerName.split()[0]
		imageFolder = '{}Images'.format( AppName )
		appExe = '{}.exe'.format( AppName )
		
		if 'MAC' in wx.Platform:
			try:
				topDirName = os.environ['RESOURCEPATH']
			except Exception:
				topDirName = os.path.dirname(os.path.realpath(__file__))
			if os.path.isdir( os.path.join(topDirName, imageFolder) ):
				dirName = topDirName
			else:
				dirName = os.path.normpath(topDirName + '/../Resources/')
			if not os.path.isdir(dirName):
				dirName = os.path.normpath(topDirName + '/../../Resources/')
			if not os.path.isdir(dirName):
				raise Exception("Resource Directory does not exist:" + dirName)
		else:
			try:
				dirName = os.path.dirname(os.path.abspath(__file__))
			except Exception:
				dirName = os.path.dirname(os.path.abspath(sys.argv[0]))
			
			if os.path.basename(dirName) in ('library.zip', 'MainWin.exe', appExe):
				dirName = os.path.dirname(dirName)
			if '{}?'.format(AppName) in os.path.basename(dirName):
				dirName = os.path.dirname(dirName)
			if not os.path.isdir( os.path.join(dirName, imageFolder) ):
				dirName = os.path.dirname(dirName)

			if os.path.isdir( os.path.join(dirName, imageFolder) ):
				pass
			elif os.path.isdir( '/usr/local/{}'.format(imageFolder) ):
				dirName = '/usr/local'
		
		dirNames.update( {
				'dirName':dirName,
				'imageFolder':os.path.join( dirName, imageFolder ),
				'htmlFolder':os.path.join( dirName, '{}Html'.format(AppName) ),
				'helpFolder':os.path.join( dirName, '{}HtmlDoc'.format(AppName) ),
				'helpIndexFolder':os.path.join( dirName, '{}HelpIndex'.format(AppName) ),
			}
		)
	
	return dirNames

def GetFolder( folderName ):
	try:
		return dirNames[folderNmae]
	except KeyError:
		return GetFolders()[folderName]
