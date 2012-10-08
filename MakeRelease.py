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

distPath = 'dist'

#-----------------------------------------------------------------------
# Compile the help files
#
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

#-----------------------------------------------------------------------
# Make the distribution folder.
#
if not os.path.exists(distPath):
	os.makedirs( distPath )

#-----------------------------------------------------------------------
# Compile all the python files.
#
for f in os.listdir( '.' ):
	if not (f.endswith( '.py' ) or f.endswith( '.pyw' )):
		continue
	print( 'compiling:', f, '...' )
	py_compile.compile( f )

'''------------------------------------------------------------------'''
'''------------------------------------------------------------------'''

buildPath = 'CrossMgrBuild'

#-----------------------------------------------------------------------
# Clean up the build folder.
#
shutil.rmtree( buildPath )

#-----------------------------------------------------------------------
# Create the release.
#
p = subprocess.Popen( ['bash', 'pyinstaller.sh'], stdout=subprocess.PIPE )
ret = p.communicate()

releasePath = 'CrossMgrBuild/dist/CrossMgr'

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
'''------------------------------------------------------------------'''

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
