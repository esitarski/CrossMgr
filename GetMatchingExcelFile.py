import os
import re
import glob
import Utils

reExcelFileVersion = re.compile(r' \((\d+)\)\.(xls|xlsx)$')

def removeExcelFileVersion( fname ):
	ext = os.path.splitext(fname)[1]
	fname = reExcelFileVersion.sub( '', fname )
	if not fname.endswith(ext):
		fname += ext
	return fname
	
def getExcelFileVersion( fname ):
	m = reExcelFileVersion.search( fname )
	if not m:
		return 0
	return int(m.group(1))

def GetMatchingExcelFile( fileName, excelFileName ):
	# Check if the file exists.
	if os.path.isfile(excelFileName):
		return excelFileName
		
	baseName = Utils.plat_ind_basename(excelFileName)
	dirName = os.path.dirname(fileName)
	
	# Then check if a spreadsheet with the same name exists in the race directory.
	newFileName = os.path.join( dirName, baseName )
	if os.path.isfile(newFileName):
		return newFileName

	# Look for another spreadsheet with a more recent version number both in the race dir and the excel dir.
	lastVersion = getExcelFileVersion( baseName )
	baseMatchName = removeExcelFileVersion( baseName )
	for src in (fileName, excelFileName):
		dirName = os.path.dirname( src )
		
		newFileName = None
		for f in glob.glob('{}/*{}'.format(dirName, os.path.splitext(baseName)[1])):
			baseNewName = os.path.basename( f )
			if removeExcelFileVersion(baseNewName) != baseMatchName:
				continue
			newVersion = getExcelFileVersion( baseNewName )
			if newVersion > lastVersion:
				lastVersion = newVersion
				newFileName = f
		
		if newFileName:
			break
			
	return newFileName
