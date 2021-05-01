import Utils
import datetime
import re
import wx
import wx.lib.masked.numctrl as NC
import wx.lib.intctrl as IC
from wx.lib.masked import TimeCtrl, EVT_TIMEUPDATE

def convert(name):
	s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
	return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

# Includes articles and conjunctions.
nonCapWords = set( ['the', 'of', 'by', 'in', 'to', 'a', 'an', 'some', 'at', 'on', 'to', 'for', 'from', 'and', 'or', 'but', 'yet', 'so', ] )
	
def niceName( name ):
	names = [n[0].upper() + n[1:] if n not in nonCapWords else n for n in convert(name).split('_')]
	name = ' '.join( names )
	return name[0].upper() + name[1:]	# Ensure the first word is capitalized.

class FieldDef:
	StringType		= 'string'
	IntType			= 'int'
	FloatType		= 'float'
	DateType		= 'date'
	TimeType		= 'time'
	ChoiceType		= 'choice'
	
	def __init__( self, attr, name = None, type = None, choices = None, changeCallback = None, data = None ):
		if name is None:
			name = niceName( attr )
		if choices is not None:
			type = FieldDef.ChoiceType
		elif type is None:
			if data is not None:
				type = FieldDef.getType( data )
			else:
				type = FieldDef.StringType
		self.name = name
		self.attr = attr if attr else name.lower()
		self.type = type
		self.choices = choices
		self.nameCtrl = None
		self.editCtrl = None
		self.changeCallback = changeCallback
		
	def __repr__( self ):
		return 'Field: {}, {}'.format(self.name, self.type)
		
	@staticmethod
	def getType( v ):
		if isinstance(v, str):				return FieldDef.StringType
		if isinstance(v, float):			return FieldDef.FloatType
		if isinstance(v, int):				return FieldDef.IntType
		if isinstance(v, datetime.date):	return FieldDef.DateType
		if isinstance(v, datetime.time):	return FieldDef.TimeType
		raise ValueError( "unknown type" )
	
	def makeCtrls( self, parent ):
		self.labelCtrl = wx.StaticText( parent, label=self.name )
		
		if   self.type == FieldDef.StringType:
			self.editCtrl = wx.TextCtrl( parent, style=wx.TE_PROCESS_ENTER,size=(175,-1) )
			self.editCtrl.Bind( wx.EVT_TEXT, self.onChanged )
			
		elif self.type == FieldDef.IntType:
			self.editCtrl = IC.IntCtrl( parent, min=0, value=0, limited=True, style=wx.ALIGN_RIGHT, size=(32,-1) )
			self.editCtrl.Bind( wx.EVT_TEXT, self.onChanged )
			
		elif self.type == FieldDef.FloatType:
			self.editCtrl = NC.NumCtrl( parent, min = 0, integerWidth = 3, fractionWidth = 3, style=wx.ALIGN_RIGHT, size=(32,-1), useFixedWidthFont = False )
			self.editCtrl.SetAllowNegative(False)
			self.editCtrl.Bind( wx.EVT_TEXT, self.onChanged )
			
		elif self.type == FieldDef.DateType:
			self.editCtrl = wx.adv.DatePickerCtrl( parent, style = wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY, size=(120,-1))
			self.editCtrl.Bind( wx.adv.EVT_DATE_CHANGED, self.onChanged )
			
		elif self.type == FieldDef.TimeType:
			self.editCtrl = TimeCtrl( parent, format = '24HHMM', displaySeconds = False, useFixedWidthFont = False )
			self.editCtrl.Bind( EVT_TIMEUPDATE, self.onChanged)
			
		elif self.type == FieldDef.ChoiceType:
			self.editCtrl = wx.Choice( parent, choices=self.choices )
			self.editCtrl.Bind( wx.EVT_CHOICE, self.onChanged )	
			
		return self.labelCtrl, self.editCtrl
		
	def refresh( self, obj ):
		if self.type in [FieldDef.StringType, FieldDef.IntType, FieldDef.FloatType]:
			self.editCtrl.SetValue( getattr(obj, self.attr) )
		elif self.type == FieldDef.DateType:
			dt = getattr( obj, self.attr )
			xdt = wx.DateTime()
			xdt.Set( dt.day, dt.month-1, dt.year, 0, 0, 0, 0 )
			self.editCtrl.SetValue( xdt )
		elif self.type == FieldDef.TimeType:
			tm = getattr( obj, self.attr )
			s = '{:02d}:{:02d}'.format(tm.hour, tm.minute)
			self.editCtrl.SetValue( s )
		elif self.type == FieldDef.ChoiceType:
			self.editCtrl.SetSelection( getattr(obj, self.attr) )
	
	def commit( self, obj ):
		if not self.editCtrl.IsEnabled():
			return False
		if self.type in [FieldDef.StringType, FieldDef.IntType, FieldDef.FloatType]:
			v = self.editCtrl.GetValue()
			if self.type == FieldDef.StringType:
				v = v.strip()
		elif self.type == FieldDef.DateType:
			dt = self.editCtrl.GetValue()
			v = datetime.date( dt.GetYear(), dt.GetMonth() + 1, dt.GetDay() )	# Adjust for 0-based month.
		elif self.type == FieldDef.TimeType:
			tm = self.editCtrl.GetValue()
			secs = 0
			values = tm.split( ':' )
			for n in values:
				secs = secs * 60 + int(n)
			if len(values) == 2:
				secs *= 60
			v = datetime.time( secs // (60*60), (secs // 60) % 60, secs % 60 )
		elif self.type == FieldDef.ChoiceType:
			v = self.editCtrl.GetSelection()
			
		if getattr(obj, self.attr) != v:
			setattr( obj, self.attr, v )
			return True
		else:
			return False
	
	def getText( self ):
		if self.type in [FieldDef.StringType, FieldDef.IntType, FieldDef.FloatType]:
			v = self.editCtrl.GetValue()
			if self.type == FieldDef.StringType:
				v = v.strip()
			return '{}'.format(v)
		if self.type == FieldDef.DateType:
			dt = self.editCtrl.GetValue()
			v = datetime.date( dt.GetYear(), dt.GetMonth() + 1, dt.GetDay() )	# Adjust for 0-based month.
			return v.strftime( '%Y-%m-%d' )
		if self.type == FieldDef.TimeType:
			tm = self.editCtrl.GetValue()
			secs = 0
			values = tm.split( ':' )
			for n in values:
				secs = secs * 60 + int(n)
			if len(values) == 2:
				secs *= 60
			v = datetime.time( secs // (60*60), (secs // 60) % 60, secs % 60 )
			return v.strftime( '%H:%M:%S' )
		elif self.type == FieldDef.ChoiceType:
			return self.editCtrl.GetStringSelection()
	
	def onChanged( self, event ):
		if self.changeCallback:
			wx.CallAfter( self.changeCallback, self )
