#!/usr/bin/env python

import os
import io
import sys
import six
import stat
import glob
import shutil
import datetime
import subprocess

import ParseDef

version = '3.0.0'

pypiDir = 'pypi'

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
======
pyllrp
======

A pure Python implementation of LLRP (Low Level Reader Protocol)
used by RFID readers including Impinj, Alien and ThingMagic.
See the LLRP spec for details on the messages.

Allows quick-and-easy scripting in fully portable pure Python to create LLRP applications.

All Message and Parameters are full Python classes.
Full validation of all LLRP Messages and Parameters including data type, date values and parameter checking.
Full support for enumerated values.

See TinyExample.py for how to use.

A reader connection manager is also included that can connect to a reader, transact commands, then start/stop a thread to listen for tag reads.  A message handler can be configured to respond to any reader message.  See wxExample.py for a simple method to show reader messages in a wxPython application with a Queue (requires wxPython install).

The module also supports reading and writing messages in XML format.
'''

writeToFile( readme, 'README.txt' )

#--------------------------------------------------------
changes = '''
'''
writeToFile( changes, 'CHANGES.txt' )
	
#--------------------------------------------------------
license = '''
Copyright (C) 2013-%d Edward Sitarski

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

#--------------------------------------------------------

manifest = '''include *.txt
'''

writeToFile( manifest, 'MANIFEST.in' )

#--------------------------------------------------------

srcDir = os.path.join( pypiDir, 'pyllrp' )
os.mkdir( srcDir )

six.print_( 'Copy the src files and add the copyright notice.' )
license = license.replace( '\n', '\n# ' )
for fname in glob.glob( '*.*' ):
	if not (fname.endswith( '.py' ) or fname.endswith('.pyw')) or fname == 'pypi.py':
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


six.print_( 'Creating setup.py...' )
setup = {
	'name':			'pyllrp',
	'version':		version,
	'author':		'Edward Sitarski',
	'author_email':	'edward.sitarski@gmail.com',
	'url':			'http://www.sites.google.com/site/crossmgrsoftware/',
	'packages':		['pyllrp'],
	'license':		'License.txt',
	'include_package_data': True,
	'description':	'pyllrp: a pure Python implementation of LLRP (Low Level Reader Protocol).',
	'install_requires':	[
		'bitstring >= 3.1.1',
		'six',
	],
	'classifiers' : [
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7 :: Python :: 3',
		"Operating System :: OS Independent",
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
try:
	shutil.move( 'pyllrp-{}.zip'.format(version), 'pip-install-pyllrp-{}.zip'.format(version) )
except:
	shutil.move( 'pyllrp-{}.tar.gz'.format(version), 'pip-install-pyllrp-{}.tar.gz'.format(version) )
	
six.print_( 'Done.' )
