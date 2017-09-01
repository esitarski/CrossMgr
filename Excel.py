# -*- coding: utf-8 -*-
from __future__ import print_function

import xlrd
import xml.etree.ElementTree
import os
import math
import itertools
import unicodedata
from mmap import mmap, ACCESS_READ

def toAscii( s ):
	if not s:
		return ''
	ret = unicodedata.normalize('NFKD', s).encode('ascii','ignore') if type(s) == unicode else str(s)
	if ret.endswith( '.0' ):
		ret = ret[:-2]
	return ret

#----------------------------------------------------------------------------

class ReadExcelXls( object ):
	def __init__(self, filename):
		if not os.path.isfile(filename):
			raise ValueError, "%s is not a valid filename" % filename
		with open(filename,'rb') as f:
			self.book = xlrd.open_workbook(
				filename=filename,
				file_contents=mmap(f.fileno(),0,access=ACCESS_READ),
			)
		# self.book = xlrd.open_workbook(filename)
		
	def is_nonempty_row(self, sheet, i):
		values = sheet.row_values(i)
		if isinstance(values[0], basestring) and values[0].startswith('#'):
			return False # ignorable comment row
		return any( bool(v) for v in values )
	
	def sheet_names( self ):
		return self.book.sheet_names()
		
	def _parse_row(self, sheet, row_index, date_as_tuple):
		""" Sanitize incoming excel data """
		# Data Type Codes:
		#  EMPTY 0
		#  TEXT 1 a Unicode string
		#  NUMBER 2 float
		#  DATE 3 float
		#  BOOLEAN 4 int; 1 means TRUE, 0 means FALSE
		#  ERROR 5
		values = []
		for type, value in itertools.izip(sheet.row_types(row_index), sheet.row_values(row_index)):
			if type == 2:
				if value == int(value):
					value = int(value)
			elif type == 3:
				if isinstance(value, float) and value < 1.0:
					t = value * (24.0*60.0*60.0)
					fract, secs = math.modf( t )
					if fract >= 0.99999:
						secs += 1.0
						fract = 0.0
					elif fract <= 0.00001:
						fract = 0.0
					
					secs = int(secs)
					if fract:
						value = '{:02d}:{:02d}:{:02d}.{}'.format(
							secs // (60*60), (secs // 60) % 60, secs % 60,
							'{:.20f}'.format(fract)[2:],
						)
					else:
						value = '{:02d}:{:02d}:{:02d}'.format(secs // (60*60), (secs // 60) % 60, secs % 60)
				else:
					try:
						datetuple = xlrd.xldate_as_tuple(value, self.book.datemode)
						validDate = True
					except:
						value = 'UnreadableDate'
						validDate = False
					if validDate:
						if date_as_tuple:
							value = datetuple
						else:
							# time only - no date component
							if datetuple[0] == 0 and datetuple[1] == 0 and  datetuple[2] == 0:
								value = "%02d:%02d:%02d" % datetuple[3:]
							# date only, no time
							elif datetuple[3] == 0 and datetuple[4] == 0 and datetuple[5] == 0:
								value = "%04d/%02d/%02d" % datetuple[:3]
							else: # full date
								value = "%04d/%02d/%02d %02d:%02d:%02d" % datetuple
			elif type == 5:
				value = xlrd.error_text_from_code[value]
			values.append(value)
		return values
		
	def iter_list(self, sname, date_as_tuple=False):
		sheet = self.book.sheet_by_name(sname) # XLRDError
		for i in xrange(sheet.nrows):
			yield self._parse_row(sheet, i, date_as_tuple)

#----------------------------------------------------------------------------

ReadExcelXlsx = ReadExcelXls

#----------------------------------------------------------------------------

def GetExcelReader( filename ):
	if filename.endswith( '.xls' ):
		return ReadExcelXls( filename )
	elif filename.endswith( '.xlsx' ) or filename.endswith( '.xlsm' ):
		return ReadExcelXlsx( filename )
	else:
		raise ValueError, '%s is not a recognized Excel format' % filename

#----------------------------------------------------------------------------

