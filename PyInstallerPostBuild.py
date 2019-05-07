#!/usr/bin/env python

import shutil
import os
import six
import sys

six.print_( 'Building help files from markdown...' )
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

six.print_( 'Indexing help files...' )
from HelpIndex import BuildHelpIndex
BuildHelpIndex()

# Get platform.
if sys.platform == 'darwin':
	platform = 'OSX'
else:
	platform = 'Linux'
    
six.print_( 'Copying help, template and image files into the build folder...' )
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

six.print_( 'Combining and compressing the build directory...' )
import tarfile
tr = tarfile.open( fname, 'w:gz' )
tr.add( dest, 'CrossMgr' )
tr.close()

six.print_( 'Created:', fname )
six.print_( 'Done.' )
