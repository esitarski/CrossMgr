#!/usr/bin/env python

import shutil
import os
import stat
import glob
import datetime
import subprocess

version = '0.1.0'

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
	print 'creating', fname, '...'
	with open(os.path.join(pypiDir,fname), 'wb') as f:
		f.write( s )

#------------------------------------------------------
# Create a release area for pypi
print 'Clearing previous contents...'
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

All Messagea and Parameters are full Python classes.
Full validation of all LLRP Messages and Parameters including data type, date values and parameter checking.
Full support for enumerated values.

See TinyExample.py and wxExample.py for how to use.

A reader connection manager is also included that can connect to a reader, transact commands, then start/stop a thread to listen for tag reads.  A message handler can be configured to respond to any reader message.  See wxExample.py for a simple method to show reader messages in a wxPython application with a Queue (requires wxPython install).

At this time, the module does not support XML.  As the Python representation of reader messages is so consise and has full type and semantic checking, it seems redundant to support another syntax like XML.  It is easier to modify Python code than to modify XML.

This could change in the future with more support.
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

print 'Copy the src files and add the copyright notice.'
license = license.replace( '\n', '\n# ' )
for fname in glob.glob( '*.*' ):
	if not (fname.endswith( '.py' ) or fname.endswith('.pyw')) or fname == 'pypi.py':
		continue
	print '   ', fname, '...'
	with open(fname, 'rb') as f:
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
	with open(os.path.join(srcDir, fname), 'wb' ) as f:
		f.write( contents )


print 'Creating setup.py...'
setup = {
	'name':			'pyllrp',
	'version':		version,
	'author':		'Edward Sitarski',
	'author_email':	'edward.sitarski@gmail.com',
	'packages':		['pyllrp'],
	'license':		'License.txt',
	'include_package_data': True,
	'description':	'pyllrp: a pure Python implementation of LLRP (Low Level Reader Protocol).',
	'install_requires':	[
		'bitstring >= 3.1.1',
	],
}

with open(os.path.join(pypiDir,'setup.py'), 'wb') as f:
	f.write( 'from distutils.core import setup\n' )
	f.write( 'setup(\n' )
	for key, value in setup.iteritems():
		f.write( '    %s=%s,\n' % (key, repr(value)) )
	f.write( "    long_description=open('README.txt').read(),\n" )
	f.write( ')\n' )

print 'Creating install package...'
os.chdir( pypiDir )
subprocess.call( ['python', 'setup.py', 'sdist'] )

os.chdir( 'dist' )
try:
	shutil.move( 'pyllrp-%s.zip' % version, 'pip-install-pyllrp-%s.zip' % version )
except:
	shutil.move( 'pyllrp-%s.tar.gz' % version, 'pip-install-pyllrp-%s.tar.gz' % version )
	
print 'Done.'
