#!/usr/bin/env python

#-----------------------------------------------------------------------
# Based on the instructions found in:
# http://wiki.wxpython.org/CreatingStandaloneExecutables
#
from __future__ import print_function

import platform
if platform.system() != 'Linux':
	print( 'This script only runs on Linux' )
	sys.exit()

import os
import shutil
import stat
import sys
import datetime
import hashlib
import tarfile
import py_compile
import subprocess
from string import Template

releasePath = 'CrossMgrRelease'
distPath = 'dist'

# Compile the help files
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

shutil.rmtree( releasePath )

for f in os.listdir( '.' ):
	if not (f.endswith( '.py' ) or f.endswith( '.pyw' )):
		continue
	print( 'compiling:', f, '...' )
	py_compile.compile( f )

#-----------------------------------------------------------------------
from bbfreeze import Freezer
f = Freezer(releasePath)
f.addScript("CrossMgr.pyw")
f()    # starts the freezing process

#-----------------------------------------------------------------------
# Remove any hard-coded library dependencies
#
for f in os.listdir( releasePath ):
	if not f.endswith( '.so' ):
		continue
	fname = os.path.join(releasePath, f)
	p = subprocess.Popen( ['chrpath', '-r', fname], stdout=subprocess.PIPE )
	ret = p.communicate()
	print( f, ret )

#-----------------------------------------------------------------------
# Make the distribution folder.
if not os.path.exists(distPath):
	os.makedirs( distPath )

import Version
tarName = Version.AppVerName.replace(' ', '_') + '_i386.tar.gz'
tf = tarfile.open( os.path.join(distPath, tarName), 'w:gz' )
for f in os.listdir( releasePath ):
	tf.add( os.path.join(releasePath, f), os.path.join('CrossMgr',f) )

for dir in ['images', 'htmldoc', 'html']:
	targetDir = os.path.join( 'CrossMgr', dir )
	for f in os.listdir( dir ):
		tf.add( os.path.join(dir,f), os.path.join(targetDir, f) )

targetDir = os.path.join( 'CrossMgr', 'doc' )
tf.add( 'CrossMgrTutorial.doc', os.path.join(targetDir,'CrossMgrTutorial.doc') )
	
tf.close()
sys.exit()

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

print( 'Create a new debian package area.')
shutil.rmtree( packageRoot, ignore_errors = True )
shutil.rmtree( controlRoot, ignore_errors = True )

import Version
debName = Version.AppVerName.replace(' ', '_') + '_2.0_i386.deb'
	
print( 'Create directory for the program and data files.')
optPath = os.path.join(packageRoot,'opt','CrossMgr')
os.makedirs( optPath )

print( 'Copy executable and libraries.' )
for f in os.listdir( releasePath ):
	shutil.copy( os.path.join(releasePath, f), optPath )

print( 'Copy html directory.' )
shutil.copytree( 'html',	os.path.join(optPath, 'html') )

print( 'Copy htmldoc directory.' )
shutil.copytree( 'htmldoc',	os.path.join(optPath, 'htmldoc') )

print( 'Copy images directory.' )
shutil.copytree( 'images',	os.path.join(optPath, 'images') )

#-----------------------------------------------------------------------
print( 'Create copyright file.' )
copyrightFile = os.path.join(packageRoot,'usr','share','doc','CrossMgr','copyright')
os.makedirs( os.path.dirname(copyrightFile) )
copyrightStr = '''This software is copyright (c) 2010, 2011 Edward Sitarski
All rights reserved.
'''
open( copyrightFile, 'w' ).write( copyrightStr )

#-----------------------------------------------------------------------
#-----------------------------------------------------------------------
print( 'Creating md5sums file.')
os.makedirs( controlRoot )
md5sums = open( os.path.join(controlRoot, 'md5sums'), 'w' )
for dirpath, dirnames, filenames in os.walk(packageRoot):
	for filename in filenames:
		fname = os.path.join( dirpath, filename )
		m = hashlib.md5()
		m.update( open(fname,'r').read() )
		md5sum = m.hexdigest()
		fname = fname[len(packageRoot)+1:]
		md5sums.write( '%s  %s\n' % (md5sum, fname) )
md5sums.close()
	
#-----------------------------------------------------------------------
print( 'Create control file.')

installedSize = sum( os.path.getsize(os.path.join(dirpath,filename))
		for dirpath, dirnames, filenames in os.walk(packageRoot) for filename in filenames ) + 256

# day-of-week, dd month yyyy hh:mm:ss +zzzz
dateStr = datetime.datetime.today().strftime('%a, %d %b %Y %H:%M:%S %z')

controlStr = Template('''Package: $package
Version: $version
Priority: optional
Architecture: i386
Homepage: $homepage
Date: $date
Essential: no
Recommends: mozilla | netscape  
Installed-Size: $installedSize
Maintainer: Edward Sitarski [edward.sitarski@gmail.com]
Provides: $package
Replaces: $package
Description: Low-cost solution for getting results for Cyclo-Cross races.
 Creates nice web and Excel-based results output.
 Comprehensive graphical displays to resolve disputes.
 Extensive error-correcting capabilities for mis-entered numbers.
 See sites.google.com/site/crossmgrsoftware/ for details.
''').substitute( {
		'package':			Version.AppVerName.split(' ')[0].lower(),
		'version':			Version.AppVerName.split(' ')[1],
		'installedSize':	installedSize,
		'homepage':			'http://sites.google.com/site/crossmgrsoftware/',
		'date':				dateStr,
		} )
		
open( os.path.join(controlRoot, 'control'), 'w' ).write( controlStr )

#-----------------------------------------------------------------------
print( 'Creating postinst file.')
postinstStr = '#!/bin/sh\nln -s %s/CrossMgr.pyw /usr/bin/CrossMgr\n' % optPath
fname = os.path.join(controlRoot, 'postinst')
open( fname, 'w' ).write( postinstStr )
os.system( 'chmod 755 %s' % fname )

#-----------------------------------------------------------------------
print( 'Creating prerm file.')
prermStr = '#!/bin/sh\nrm /usr/bin/CrossMgr\n'
fname = os.path.join(controlRoot, 'prerm')
open( fname, 'w' ).write( prermStr )
os.system( 'chmod 755 %s' % fname )

#-----------------------------------------------------------------------
print( 'Adding control files to the archive')
tf = tarfile.open( os.path.join(controlRoot, 'control.tar.gz'), 'w:gz' )
for f in os.listdir( controlRoot ):
	tf.add( os.path.join(controlRoot, f), f )
tf.close()

tf = tarfile.open( os.path.join(controlRoot, 'data.tar.gz'), 'w:gz' )
tf.add( packageRoot, '.' )
tf.close()

#-----------------------------------------------------------------------
print( 'Create binary file.')
open( os.path.join(controlRoot, 'debian-binary'), 'w' ).write( '2.0\n' )

print( 'Creating debian archive.')
files = ['debian-binary', 'control.tar.gz', 'data.tar.gz']
'''
tf = tarfile.open( os.path.join(controlRoot, debName), 'w' )
for f in files:
	tf.add( os.path.join(controlRoot, f), f )
tf.close()
'''
os.system( 'cd %s; ar rv %s %s' % (controlRoot, debName, ' '.join(files)) )

try:
	os.makedirs( 'dist' )
except:
	pass
shutil.copy( os.path.join(controlRoot, debName), 'dist' )

shutil.rmtree( packageRoot, ignore_errors = True )
shutil.rmtree( controlRoot, ignore_errors = True )
shutil.rmtree( releasePath, ignore_errors = True )
