#!/usr/bin/env python

import shutil
import os
import sys
import six

six.print_( 'Building help files from markdown...' )
from helptxt.compile import CompileHelp
CompileHelp( 'helptxt' )

six.print_( 'Indexing help files...' )
from HelpIndex import BuildHelpIndex
BuildHelpIndex()

