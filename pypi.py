#!/usr/bin/env python

import shutil
import os
import io
import stat
import glob
import datetime
import subprocess
from Version import AppVerName

pypiDir = 'pypi'
version = AppVerName.split(' ')[1]

print( 'version=', version )

def removeTabs( buf, tabStop = 4 ):
	# Remove tabs from Python code and preserve formatting.
	lines = []
	for line in buf.split( '\n' ):
		lineOut = []
		for c in line:
			if c == '\t':
				lineOut.append( ' ' )
				pad = tabStop - len(lineOut) % tabStop
				if pad != tabStop:
					lineOut.append( ' ' * pad )
			else:
				lineOut.append( c )
		lines.append( ''.join(lineOut) )
	return '\n'.join( lines ) + '\n'

def writeToFile( s, fname ):
	print( 'creating', fname, '...' )
	with io.open(os.path.join(pypiDir,fname), 'w', encoding='utf-8') as f:
		f.write( s )

#-----------------------------------------------------------------------
# Compile the help files
#
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

# Index the help files.
from HelpIndex import BuildHelpIndex
BuildHelpIndex()

#------------------------------------------------------
# Create a release area for pypi
print( 'Clearing previous contents...' )
try:
	subprocess.call( ['rm', '-rf', pypiDir] )
except Exception:
	try:
		shutil.rmtree( pypiDir, ignore_errors=True )
	except Exception:
		pass
	
os.mkdir( pypiDir )

#--------------------------------------------------------
readme = '''
========
CrossMgr
========

Free timing and results software for to get results for Cyclo-Cross, MTB, Time Trials, Criteriums and Road races
(donations recommended for paid events).

CrossMgr quickly produces professional results including rider lap times.
It reads rider data from Excel, and formats result in Excel format or Html for
publishing to the web.
CrossMgr was created by a cycling official, and has extensive features to
settle disputes.

CrossMgr supports the`JChip <http://www.j-chipusa.com/>`_
and RaceResult <http://www.raceresult.com> chip timing systems.
CrossMgr also support the `Alien <http://www.alientechnology.com>`_ and
`Impinj <http://www.impinj.com`_ passive chip readers.
It can read data from the `Orion <http://www.orion-timing.com/>`_ system.

See `CrossMgr <http://www.sites.google.com/site/crossmgrsoftware/>`_ for details.
'''

writeToFile( readme, 'README.txt' )

#--------------------------------------------------------
changes = '''
See http://www.sites.google.com/site/crossmgrsoftware/ for details.
'''
writeToFile( changes, 'CHANGES.txt' )
	
#--------------------------------------------------------
license = '''
Copyright (C) 2008-%d Edward Sitarski

Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
and associated documentation files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
''' % datetime.datetime.now().year

writeToFile( license, 'License.txt' )
			
manifest = '''include *.txt
recursive-include CrossMgr/CrossMgrDoc *
recursive-include CrossMgr/CrossMgrHtml *.html
recursive-include CrossMgr/CrossMgrHtmlDoc *.html
recursive-include CrossMgr/CrossMgrImages *
recursive-include CrossMgr/CrossMgrLocale *
recursive-include CrossMgr/CrossMgrHelpIndex *
'''

writeToFile( manifest, 'MANIFEST.in' )

#--------------------------------------------------------

srcDir = os.path.join( pypiDir, 'CrossMgr' )
os.mkdir( srcDir )
data_dirs = (
	'CrossMgrImages',
	'CrossMgrHtml', 'CrossMgrHtmlDoc', 'CrossMgrHelpIndex', 'CrossMgrLocale',
)
def get_dir_suffixes( data_dirs ):
	dir_suffixes = set()
	for d in data_dirs:
		for root, dirs, files in os.walk(d):
			for f in files:
				dir_suffixes.add( '{}/*{}'.format(root.replace('\\','/'),os.path.splitext(f)[1]) )
	return sorted(dir_suffixes)

for dir in data_dirs:
	print( 'copying', dir, 'to', os.path.join(pypiDir,'CrossMgr',dir) )
	shutil.copytree( dir, os.path.join(pypiDir,'CrossMgr',dir) )

print( 'Copying doc files to doc directory.' )
docDir = os.path.join( pypiDir, 'CrossMgr','CrossMgrDoc' )
os.mkdir( docDir )
for f in ['MacInstallReadme.txt', 'LinuxInstallReadme.txt', 'CrossMgrTutorial.doc']:
	shutil.copy( f, os.path.join(docDir, f) )

print( 'Copy the src files and add the copyright notice.' )
license = license.replace( '\n', '\n# ' )
for fname in glob.glob( '*.*' ):
	if not (fname.endswith('.py') or fname.endswith('.pyw')):
		continue
	print( '   ', fname, '...' )
	with open(fname, 'r', encoding='utf-8') as f:
		contents = f.read()
	if contents.startswith('import'):
		p = 0
	else:
		for search in ['\nimport', '\nfrom']:
			p = contents.find(search)
			if p >= 0:
				p += 1
				break
	if p >= 0:
		contents = ''.join( [contents[:p],
							'\n',
							'#------------------------------------------------------',
							license,
							'\n',
							contents[p:]] )
	
	contents = removeTabs( contents )
	contents.replace( '\r\n', '\n' )
	with open(os.path.join(srcDir, fname), 'w', encoding='utf8') as f:
		f.write( contents )

print( 'Adding script to bin dir..' )
binDir = os.path.join( pypiDir, 'bin' )
os.mkdir( binDir )
exeName = os.path.join(binDir,'CrossMgrRun')
shutil.copy( os.path.join(srcDir,'CrossMgr.pyw'), exeName )
shutil.copy( os.path.join(srcDir,'CrossMgr.pyw'), exeName+'.pyw' )

# Make it executable.
os.chmod( exeName, os.stat(exeName)[0] | stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH )
os.chmod( exeName, os.stat(exeName+'.pyw')[0] | stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH )

print( 'Creating setup.py...' )
setup = {
	'name':			'CrossMgr',
	'version':		version,
	'author':		'Edward Sitarski',
	'author_email':	'edward.sitarski@gmail.com',
	'packages':		['CrossMgr'],
	'package_data':	{'CrossMgr': get_dir_suffixes(data_dirs)},
	'scripts':		[('bin/' + f) for f in os.listdir(binDir)],
	'url':			'http://www.sites.google.com/site/crossmgrsoftware/',
	'license':		'License.txt',
	'include_package_data': True,
	'description':	'CrossMgr: scoring/results application for Cyclo-Cross, MTB, Time Trial, Criterium and Road cycling races.',
	'install_requires':	[
		'xlrd >= 0.9.2',
		'xlwt >= 0.7.5',
		'xlsxwriter >= 0.6.7',
		'whoosh >= 2.5.7',
		'qrcode >= 4.0.4',
		'beautifulsoup4 >= 4.0.0',
		'fpdf >= 1.7',
		'ftputil >= 3.3',
		'tornado >= 4.4',
		'requests >= 2.13.0',
		'netifaces >= 0.10.6',
		'bitstring',
		'wxPython',
	],
}

with open(os.path.join(pypiDir,'setup.py'), 'w', encoding='utf8') as f:
	f.write( 'from distutils.core import setup\n' )
	f.write( 'setup(\n' )
	for key, value in setup.items():
		f.write( '    {}={},\n'.format(key, repr(value)) )
	f.write( "    long_description=open('README.txt').read(encoding='utf8'),\n" )
	f.write( ')\n' )

print( 'Creating install package...' )
os.chdir( pypiDir )
subprocess.call( ['python', 'setup.py', 'sdist'] )

os.chdir( 'dist' )
try:
	shutil.move( 'CrossMgr-{}.zip'.format(version), 'PIP-Install-CrossMgr-{}.zip'.format(version) )
except Exception:
	pipName = 'PIP-Install-CrossMgr-{}.tar.gz'.format(version)
	installDir = os.path.join( os.path.expanduser("~"), 'Google Drive', 'Downloads', 'Mac', 'CrossMgr')
    
	shutil.move( 'CrossMgr-{}.tar.gz'.format(version), pipName )
	shutil.copyfile( pipName, os.path.join( installDir, pipName) )
	print()
	print( '********************' )
	print( installDir )
	print( '********************' )
	print( '\n'.join( os.listdir(installDir) ) )
	
	installDir = os.path.join( os.path.expanduser("~"), 'Google Drive', 'Downloads', 'All Platforms', 'CrossMgr')
	shutil.copyfile( pipName, os.path.join( installDir, pipName) )
	shutil.copyfile( '../../LinuxInstallReadme.txt', os.path.join(installDir, 'LinuxInstallReadme.txt') )
	print()
	print( '********************' )
	print( installDir )
	print( '********************' )
	print( '\n'.join( os.listdir(installDir) ) )
	
print( 'Done.' )
