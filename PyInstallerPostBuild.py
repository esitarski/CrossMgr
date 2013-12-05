#!/usr/bin/env python

import shutil
import os
import sys

print 'Building help files from markdown...'
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

print 'Indexing help files...'
from HelpIndex import BuildHelpIndex
BuildHelpIndex()

# Get platform.
if sys.platform == 'darwin':
	platform = 'OSX'
else:
	platform = 'Linux'
    
print 'Copying help, template and image files into the build folder...'
resourceDirs = ['CrossMgrHtml', 'CrossMgrHtmlDoc', 'CrossMgrHelpIndex', 'CrossMgrImages']

dest = os.path.join('CrossMgrBuild', 'dist', 'CrossMgr')
for d in resourceDirs:
	shutil.copytree( d, os.path.join(dest, d) )

if platform == 'OSX':
	dest = os.path.join('CrossMgrBuild', 'CrossMgr.app', 'Contents', 'Resources')
	for d in resourceDirs:
		shutil.copytree( d, os.path.join(dest, d) )
    
# Check if 32 or 64 bit.
import struct
bits = '{}bit'.format( struct.calcsize("P") * 8 ) 

from Version import AppVerName
fname = platform + '_' + bits + '_' + AppVerName.replace(' ', '_') + '.tar.gz'
fname = os.path.join( 'CrossMgrBuild', fname )

print 'Combining and compressing the build directory...'
import tarfile
tr = tarfile.open( fname, 'w:gz' )
tr.add( dest, 'CrossMgr' )
tr.close()

print 'Created:', fname
print 'Done.'
