#!/usr/bin/env python

print( 'Building help files from markdown...' )
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

#print( 'Indexing help files...' )
#from HelpIndex import BuildHelpIndex
#BuildHelpIndex()

