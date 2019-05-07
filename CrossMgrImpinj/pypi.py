#!/usr/bin/env python

import shutil
import os
import io
import six
import sys
import stat
import glob
import datetime
import subprocess
from Version import AppVerName

pypiDir = 'pypi'
version = AppVerName.split(' ')[1]

six.print_( 'version=', version )

def removeTabs( buf, tabStop = 4 ):
	# Remove tabs from Python code and preserve formatting.
	lines = []
	for line in buf.split( '\n' ):
		lineOut = []
		for c in line:
			if c == '\t':
				lineOut.append( ' ' )
				while len(lineOut) % tabStop != 0:
					lineOut.append( ' ' )
			else:
				lineOut.append( c )
		lines.append( ''.join(lineOut) )
	return '\n'.join( lines ) + '\n'

def writeToFile( s, fname ):
	six.print_( 'creating', fname, '...' )
	with io.open(os.path.join(pypiDir,fname), 'w') as f:
		f.write( s )

#------------------------------------------------------
# Create a release area for pypi
six.print_( 'Clearing previous contents...' )
try:
	subprocess.call( ['rm', '-rf', pypiDir] )
except:
	try:
		shutil.rmtree( pypiDir, ignore_errors=True )
	except:
		pass
	
os.mkdir( pypiDir )

#--------------------------------------------------------
readme = '''
========
CrossMgrImpinj
========

Impinj reader interface to CrossMgr.

CrossMgr is free timing and results software for to get results for Cyclo-Cross, MTB, Time Trials, Criteriums and Road races
(donations recommended for paid events).

CrossMgr quickly produces professional looking results including rider lap times.
It reads rider data from Excel, and formats result in Excel format or Html for
publishing to the web.
CrossMgr was created by a cycling official, and has extensive features to
settle disputes.

CrossMgr is also fully integrated with the `JChip <http://www.j-chipusa.com/>`_
chip timing system.
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
Copyright (C) 2008-{} Edward Sitarski

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
'''.format( datetime.datetime.now().year )

writeToFile( license, 'License.txt' )

#--------------------------------------------------------

manifest = '''include *.txt
recursive-include doc *
recursive-include CrossMgrImpinjHtmldoc *.html
recursive-include CrossMgrImpinjHtml *.html
recursive-include CrossMgrImpinjImages *
'''

writeToFile( manifest, 'MANIFEST.in' )

#--------------------------------------------------------

srcDir = os.path.join( pypiDir, 'CrossMgrImpinj' )
os.mkdir( srcDir )
for dir in ['CrossMgrImpinjImages']:
	six.print_( 'copying', dir, '...' )
	shutil.copytree( dir, os.path.join(pypiDir,dir) )

six.print_( 'Copying doc files to doc directory.' )
docDir = os.path.join( pypiDir, 'CrossMgrImpinjDoc' )
os.mkdir( docDir )
for f in ['LinuxInstallReadme.txt']:
	shutil.copy( f, os.path.join(docDir, f) )
	
six.print_( 'Collecting data_files.' )
data_files = []
for dir in ['CrossMgrImpinjImages']:
	dataDir = os.path.join(pypiDir, dir)
	data_files.append( (dir, [os.path.join(dir,f) for f in os.listdir(dataDir)]) )

six._print( 'Copy the src files and add the copyright notice.' )
license = license.replace( '\n', '\n# ' )
for fname in glob.glob( '*.*' ):
	if not (fname.endswith( '.py' ) or fname.endswith('.pyw')):
		continue
	six.print_( '   ', fname, '...' )
	with io.open(fname, 'r') as f:
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
	with io.open(os.path.join(srcDir, fname), 'w' ) as f:
		f.write( contents )


six.print_( 'Adding script to bin dir..' )
binDir = os.path.join( pypiDir, 'bin' )
os.mkdir( binDir )
exeName = os.path.join(binDir,'CrossMgrImpinj')
shutil.copy( os.path.join(srcDir,'CrossMgrImpinj.pyw'), exeName )
# Make it executable.
os.chmod( exeName, os.stat(exeName)[0] | stat.S_IXUSR|stat.S_IXGRP|stat.S_IXOTH )
	
six.print_( 'Creating setup.py...' )
setup = {
	'name':			'CrossMgrImpinj',
	'version':		version,
	'author':		'Edward Sitarski',
	'author_email':	'edward.sitarski@gmail.com',
	'packages':		['CrossMgrImpinj'],
	'data_files':	data_files,
	'scripts':		['bin/CrossMgrImpinj'],
	'url':			'http://www.sites.google.com/site/crossmgrsoftware/',
	'license':		'License.txt',
	'include_package_data': True,
	'description':	'CrossMgrImpinj: interface to Impinj RFID reader for CrossMgr.',
	'install_requires':	[
		'wxPython',
	],
}

with io.open(os.path.join(pypiDir,'setup.py'), 'w') as f:
	f.write( 'from distutils.core import setup\n' )
	f.write( 'setup(\n' )
	for key, value in six.iteritems(setup):
		f.write( '    {}={},\n'.format(key, repr(value)) )
	f.write( "    long_description=open('README.txt').read(),\n" )
	f.write( ')\n' )

six.print_( 'Creating install package...' )
os.chdir( pypiDir )
subprocess.call( ['python', 'setup.py', 'sdist'] )

os.chdir( 'dist' )
installDir = os.path.join( os.path.expanduser("~"), 'Google Drive', 'Downloads', 'All Platforms', 'CrossMgrImpinj')

try:
	pipName = 'PIP-Install-CrossMgrImpinj-{}.zip'.format(version)
	shutil.move( 'CrossMgrImpinj-{}.zip'.format(version), pipName )
	shutil.copyfile( pipName, os.path.join(installDir, pipName) )
except Exception as e:
	six.print_( '**** Exception ****', e )
	installDirSave = installDir
	installDir = os.path.join( os.path.expanduser("~"), 'Google Drive', 'Downloads', 'Mac', 'CrossMgrImpinj')
	pipName = 'PIP-Install-CrossMgrImpinj-{}.tar.gz'.format(version)
    
	shutil.move( 'CrossMgrImpinj-{}.tar.gz'.format(version), pipName )
	shutil.copyfile( pipName, os.path.join( installDir, pipName) )
	six.print_()
	six.print_( '********************' )
	six.print_( installDir )
	six.print_( '********************' )
	six.print_( '\n'.join( os.listdir(installDir) ) )
	
	shutil.copyfile( pipName, os.path.join( installDir, pipName) )
	shutil.copyfile( '../../LinuxInstallReadme.txt', os.path.join(installDir, 'LinuxInstallReadme.txt') )
	six.print_()
	six.print_( '********************' )
	six.print_( installDir )
	six.print_( '********************' )
	six.print_( '\n'.join( os.listdir(installDir) ) )
	
os.chdir( '..' )
os.chdir( '..' )

six.print_( '************', os.getcwd() )

six.print_( 'Creating pyllrp install...' )
os.chdir( 'pyllrp' )
subprocess.call( ['python', 'pypi.py'] )
	
for f in glob.glob('pypi/dist/*'):
	shutil.copyfile( f, os.path.join(installDir, os.path.basename(f)) )

os.chdir( '..' )

six.print_( 'Done.' )
