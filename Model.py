from __future__ import print_function
import re
import sys
import math
import bisect
import socket
import random
import getpass
import datetime
import itertools
import functools
import threading
from os.path import commonprefix

import Utils
import Version

CurrentUser = getpass.getuser()
CurrentComputer = socket.gethostname()

maxInterpolateTime = 7.0*60.0*60.0	# 7 hours.

lock = threading.RLock()

#----------------------------------------------------------------------
class memoize(object):
	"""Decorator that caches a function's return value each time it is called.
	If called later with the same arguments, the cached value is returned, and
	not re-evaluated.
	"""
   
	cache = {}
	
	@classmethod
	def clear( cls ):
		cls.cache = {}
   
	def __init__(self, func):
		# print( 'memoize:', func.__name__ )
		self.func = func
		
	def __call__(self, *args):
		# print( self.func.__name__, args )
		try:
			return memoize.cache[self.func.__name__][args]
		except KeyError:
			value = self.func(*args)
			memoize.cache.setdefault(self.func.__name__, {})[args] = value
			return value
		except TypeError:
			# uncachable -- for instance, passing a list as an argument.
			# Better to not cache than to blow up entirely.
			return self.func(*args)
			
	def __repr__(self):
		"""Return the function's docstring."""
		return self.func.__doc__
		
	def __get__(self, obj, objtype):
		"""Support instance methods."""
		return functools.partial(self.__call__, obj)

#------------------------------------------------------------------------------
# Define a global current race.
race = None

def getRace():
	global race
	return race

def newRace():
	global race
	memoize.clear()
	race = Race()
	return race

def setRace( r ):
	global race
	race = r
	if race:
		race.setChanged()
	memoize.clear()

def resetCache():
	memoize.clear()

class LockRace:
	def __enter__(self):
		lock.acquire()
		return race
		
	def __exit__( self, type, value, traceback ):
		lock.release()
		return False
	
#----------------------------------------------------------------------
def SetToIntervals( s ):
	if not s:
		return []
	seq = sorted( s )
	intervals = [(seq[0], seq[0])]
	for num in itertools.islice(seq, 1, len(seq)):
		if num <= intervals[-1][1]:
			pass
		elif num == intervals[-1][1] + 1:
			intervals[-1] = (intervals[-1][0], num)
		else:
			intervals.append( (num, num) )
	return intervals
	
def IntervalsToSet( intervals ):
	ret = set()
	for i in intervals:
		ret.update( xrange(i[0], i[1]+1) )
	return ret


#----------------------------------------------------------------------
class Category(object):

	DistanceByLap = 0
	DistanceByRace = 1

	badRangeCharsRE = re.compile( '[^0-9,\-]' )
	
	CatWave = 0
	CatComponent = 1
	CatCustom = 2
	
	catType = 0
	uploadFlag = True
	seriesFlag = True

	def _getStr( self ):
		s = ['{}'.format(i[0]) if i[0] == i[1] else '{}-{}'.format(*i) for i in self.intervals]
		s.extend( ['-{}'.format(i[0]) if i[0] == i[1] else '-{}-{}'.format(*i) for i in SetToIntervals(self.exclude)] )
		return ','.join( s )
		
	def _setStr( self, s ):
		s = self.badRangeCharsRE.sub( '', u'{}'.format(s) )
		self.intervals = []
		self.exclude = set()
		for f in s.split(','):
			if not f:
				continue
			
			try:
				if f.startswith('-'):				# Check for exclusion.
					f = f[1:]
					isExclusion = True
				else:
					isExclusion = False
					
				bounds = [int(b) for b in f.split('-') if b]
				if not bounds:
					continue

				if len(bounds) > 2:					# Fix numbers not in proper x-y range format.
					del bounds[2:]
				elif len(bounds) == 1:
					bounds.append( bounds[0] )
					
				bounds[0] = min(bounds[0], 99999)	# Keep the numbers in a reasonable range to avoid crashing.
				bounds[1] = min(bounds[1], 99999)
				
				if bounds[0] > bounds[1]:			# Swap the range if out of order.
					bounds[0], bounds[1] = bounds[1], bounds[0]
					
				if isExclusion:
					self.exclude.update( xrange(bounds[0], bounds[1]+1) )
				else:
					self.intervals.append( tuple(bounds) )
					
			except Exception as e:
				# Ignore any parsing errors.
				print( e )
				pass
				
		self.intervals.sort()

	catStr = property(_getStr, _setStr)

	def getMask( self ):
		''' Return the common number prefix for all intervals (None if non-existent). '''
		mask = None
		for i in self.intervals:
			for k in i:
				num = '{}'.format(k)
				if len(num) < 3:				# No mask for 1 or 2-digit numbers
					return None
				if mask is None:
					mask = num
				elif len(mask) != len(num):		# No mask for numbers of different lengths
					return None
				else:
					cp = commonprefix([mask, num])
					if not cp:
						return None
					mask = cp.ljust(len(mask), '.')
		return mask

	def __init__( self, active = True, name = 'Category 100-199', catStr = '100-199', startOffset = '00:00:00',
						numLaps = None, sequence = 0,
						distance = None, distanceType = None, firstLapDistance = None,
						gender = 'Open', lappedRidersMustContinue = False,
						catType = CatWave, uploadFlag = True, seriesFlag = True ):
		self.active = False
		active = unicode(active).strip()
		if active and active[0] in u'TtYy1':
			self.active = True
		
		self.name = name
		self.catStr = catStr
		self.startOffset = startOffset if startOffset else '00:00:00'
		
		self.catType = self.CatWave
		catType = unicode(catType)
		try:
			self.catType = int(catType)
		except ValueError:
			try:
				if catType.lower().startswith(u'component'):
					self.catType = self.CatComponent
				elif catType.lower().startswith(u'custom'):
					self.catType = self.CatCustom
			except:
				pass
				
		self.uploadFlag = True
		uploadFlag = unicode(uploadFlag).strip()
		if uploadFlag and uploadFlag[0] not in u'TtYy1':
			self.uploadFlag = False
		
		self.seriesFlag = True
		seriesFlag = unicode(seriesFlag).strip()
		if seriesFlag and seriesFlag[0] not in u'TtYy1':
			self.seriesFlag = False
			
		try:
			self._numLaps = int(numLaps)
			if self._numLaps < 1:
				self._numLaps = None
		except (ValueError, TypeError):
			self._numLaps = None
			
		try:
			self.sequence = int(sequence)
		except (ValueError, TypeError):
			self.sequence = 0
			
		try:
			self.distance = float(distance) if distance else None
		except (ValueError, TypeError):
			self.distance = None
		if self.distance is not None and self.distance <= 0.0:
			self.distance = None
			
		try:
			self.distanceType = int(distanceType)
		except (ValueError, TypeError):
			self.distanceType = None
			
		if self.distanceType not in [Category.DistanceByLap, Category.DistanceByRace]:
			self.distanceType = Category.DistanceByLap
			
		try:
			self.firstLapDistance = float(firstLapDistance) if firstLapDistance else None
		except (ValueError, TypeError):
			self.firstLapDistance = None
		if self.firstLapDistance is not None and self.firstLapDistance <= 0.0:
			self.firstLapDistance = None
			
		if gender in {'Men', 'Women', 'Open'}:
			self.gender = gender
		else:
			self.gender = 'Open'
			
		self.lappedRidersMustContinue = False
		lappedRidersMustContinue = '{}'.format(lappedRidersMustContinue).strip()
		if lappedRidersMustContinue and lappedRidersMustContinue[0] in 'TtYy1':
			self.lappedRidersMustContinue = True

	def __setstate( self, d ):
		self.__dict__.update(d)
		i = getattr( self, 'intervals', None )
		if i:
			i.sort()
	
	def getLapDistance( self, lap ):
		if getattr(self, 'distanceType', None) != Category.DistanceByLap:
			return None
		if lap <= 0:
			return 0

		if lap == 1:
			firstLapDistance = getattr(self, 'firstLapDistance', None)
			if firstLapDistance:
				return firstLapDistance
		return getattr(self, 'distance', None)
	
	def getDistanceAtLap( self, lap ):
		if getattr(self, 'distanceType', None) != Category.DistanceByLap:
			return None
		if lap <= 0:
			return 0
		
		firstLapDistance = getattr(self, 'firstLapDistance', None)
		if lap <= 1 and firstLapDistance:
			return firstLapDistance * lap
		
		distance = getattr(self, 'distance', None)
		if not distance:
			return None
			
		if firstLapDistance:
			return firstLapDistance + distance * (lap-1)
		else:
			return distance * lap
	
	@property
	def fullname( self ):
		return (u'%s (%s)' % (self.name, getattr(self, 'gender', 'Open'))).strip()
	
	@property
	def firstLapRatio( self ):
		if getattr(self, 'distanceType', None) != Category.DistanceByLap:
			return 1.0
		firstLapDistance = getattr(self, 'firstLapDistance', None)
		if not firstLapDistance:
			return 1.0
		distance = getattr(self, 'distance', None)
		if not distance:
			return 1.0
		return firstLapDistance / distance
	
	@property
	def distanceIsByLap( self ):
		return getattr(self, 'distanceType', Category.DistanceByLap) == Category.DistanceByLap
	
	@property
	def distanceIsByRace( self ):
		return getattr(self, 'distanceType', Category.DistanceByLap) == Category.DistanceByRace
		
	def getNumLaps( self ):
		return getattr( self, '_numLaps', None )
		
	def setNumLaps( self, numLaps ):
		try:
			numLaps = int(numLaps)
		except ValueError:
			numLaps = None
		self._numLaps = numLaps if numLaps else None
		
	numLaps = property(getNumLaps, setNumLaps) 

	def matches( self, num, ignoreActiveFlag = False ):
		if not ignoreActiveFlag:
			if not self.active:
				return False
		
		if num in self.exclude:
			return False
		
		i = bisect.bisect_left( self.intervals, (num, num) )
		for k in xrange(max(0, i-1), min(i+2, len(self.intervals))):
			if self.intervals[k][0] <= num <= self.intervals[k][1]:
				return True
		return False
		
	def getMatchSet( self ):
		matchSet = set()
		for i in self.intervals:
			matchSet.update( xrange(i[0], i[1] + 1) )
		matchSet.difference_update( self.exclude )
		return matchSet

	key_attr = ['sequence', 'name', 'active', 'startOffset', '_numLaps', 'catStr',
				'distance', 'distanceType', 'firstLapDistance',
				'gender', 'lappedRidersMustContinue', 'catType', 'uploadFlag', 'seriesFlag']
	def __cmp__( self, c ):
		for attr in self.key_attr:
			cCmp = cmp( getattr(self, attr, None), getattr(c, attr, None) )
			if cCmp != 0:
				return cCmp 
		return 0
	
	def key( self ):
		return tuple( getattr(self, attr, None) for attr in self.key_attr )
	
	def removeNum( self, num ):
		if not self.matches(num, True):
			return
		
		# Remove any singleton intervals.
		for j in xrange(len(self.intervals)-1, -1, -1):
			interval = self.intervals[j]
			if num == interval[0] == interval[1]:
				self.intervals.pop( j )
				
		# If we still match, add to the exclude set.
		if self.matches(num, True):
			self.exclude.add( num )
		
	def addNum( self, num ):
		self.exclude.discard( num )
		if self.matches(num, True):
			return
		self.intervals.append( (num, num) )
		self.intervals.sort()

	def normalize( self ):
		# Combine any consecutive or overlapping intervals.
		if self.intervals:
			newIntervals = [self.intervals[0]]
			for interval in self.intervals[1:]:
				if interval[0] <= newIntervals[-1][1] + 1:
					if interval[1] > newIntervals[-1][1]:
						newIntervals[-1] = (newIntervals[-1][0], interval[1])
				else:
					newIntervals.append( interval )
			self.intervals = newIntervals
		
		# Check if there are some excludes that don't have to be there.
		needlessExcludes = []
		for num in self.exclude:
			found = False
			i = bisect.bisect_left( self.intervals, (num, num) )
			if i > 0:
				i -= 1
			for j in xrange(i, min(i+2,len(self.intervals)) ):
				if self.intervals[j][0] <= num <= self.intervals[j][1]:
					found = True
					break
			if not found:
				needlessExcludes.append( num )
				
		self.exclude.difference_update( needlessExcludes )
		
	def __repr__( self ):
		return u'Category(active={}, name="{}", catStr="{}", startOffset="{}", numLaps={}, sequence={}, distance={}, distanceType={}, gender="{}", lappedRidersMustContinue="{}")'.format(
				self.active,
				self.name,
				self.catStr,
				self.startOffset,
				self.numLaps,
				self.sequence,
				getattr(self,'distance',None),
				getattr(self,'distanceType', Category.DistanceByLap),
				getattr(self,'gender',''),
				getattr(self,'lappedRidersMustContinue',False),
			)

	def getStartOffsetSecs( self ):
		return Utils.StrToSeconds( self.startOffset )

#------------------------------------------------------------------------------------------------------------------

def CmpEntryTT( e1, e2 ):
	if e1.lap == 0 or e2.lap == 0:
		return cmp( (e1.lap, e1.t), (e2.lap, e2.t) )
	return e1.__cmp__( e2 )

class Entry(object):
	__slots__ = ('num', 'lap', 't', 'interp')		# Suppress the default dictionary to save space.

	def __init__( self, num, lap, t, interp ):
		self.num	= num
		self.lap	= lap
		self.t		= t
		self.interp	= interp

	def __cmp__( self, e ):
		return cmp( (self.t, -self.lap, self.num, self.interp), (e.t, -e.lap, e.num, e.interp) )

	def key( self ):
		return (self.t, -self.lap, self.num, self.interp)
		
	def keyTT( self ):
		return (0 if self.lap == 0 else 1, self.t, -self.lap, self.num, self.interp)
		
	def set( self, e ):
		self.num	= e.num
		self.lap	= e.lap
		self.t		= e.t
		self.interp	= e.interp
		
	def __hash__( self ):
		return (self.num<<16) ^ (self.lap<<8) ^ hash(self.t) ^ ((1<<20) if self.interp else 0)

	def __repr__( self ):
		return u'Entry( num={}, lap={}, interp={}, t={} )'.format(self.num, self.lap, self.interp, self.t)

class Rider(object):
	# Rider Status.
	Finisher  = 0
	DNF       = 1
	Pulled    = 2
	DNS       = 3
	DQ 		  = 4
	OTL		  = 5
	NP		  = 6
	statusNames = ['Finisher', 'DNF', 'PUL', 'DNS', 'DQ', 'OTL', 'NP']
	statusSortSeq = { 'Finisher':1,	Finisher:1,
					  'PUL':2,		Pulled:2,
					  'OTL':6,		OTL:6,
					  'DNF':3,		DNF:3,
					  'DQ':4,		DQ:4,
					  'DNS':5,		DNS:5,
					  'NP':7,		NP:7 }

	# Factors for range of acceptable lap times.
	pMin, pMax = 0.85, 1.20
	
	# Maximum entries generated by interpolation.
	entriesMax = 200
		
	def __init__( self, num ):
		self.num = num
		self.times = []
		self.status = Rider.Finisher
		self.tStatus = None
		self.autocorrectLaps = True
		self.firstTime = None		# Used for time trial mode.  Also used to flag the first start time.

	def __repr__( self ):
		return u'{} ({})'.format( self.num, self.statusNames[self.status] )
		
	def setAutoCorrect( self, on = True ):
		self.autocorrectLaps = on
		
	def addTime( self, t ):
		# All times in race time seconds.
		timesLen = len(self.times)
		if timesLen == 0 or t > self.times[timesLen-1]:
			self.times.append( t )
		else:
			i = bisect.bisect_left(self.times, t, 0, timesLen)
			if i >= timesLen or self.times[i] != t:
				self.times.insert( i, t )

	def deleteTime( self, t ):
		try:
			self.times.remove( t )
		except ValueError:
			pass

	def getTimeCount( self ):
		if not self.times:
			return 0.0, 0					# No times, no count.
			
		# If there is only the first lap, return that.
		if len(self.times) == 1:
			return self.times[0], 1
			
		# If there is more than one lap, return the time from the other laps.
		return self.times[-1] - self.times[0], len(self.times) - 1

	def getLastKnownTime( self ):
		try:
			return self.times[-1]
		except IndexError:
			return 0
			
	def getFirstKnownTime( self ):
		t = getattr( self, 'firstTime', None )
		if t is None:
			try:
				t = self.times[1]
			except IndexError:
				pass
		return t

	def isDNF( self ):			return self.status == Rider.DNF
	def isDNS( self ):			return self.status == Rider.DNS
	def isPulled( self ):		return self.status == Rider.Pulled

	def setStatus( self, status, tStatus = None ):
		if status in [Rider.Finisher, Rider.DNS, Rider.DQ]:
			tStatus = None
		elif status in [Rider.Pulled, Rider.DNF]:
			if tStatus is None:
				race = getRace()
				if race:
					tStatus = race.lastRaceTime()
		
		self.status = status
		self.tStatus = tStatus
	
	def getCleanLapTimes( self ):
		if not self.times or self.status in [Rider.DNS, Rider.DQ]:
			return None

		# Create a separate working list.
		iTimes = [None] * (len(self.times) + 1)
		# Add a zero start time for the beginning of the race.
		# This avoids a whole lot of special cases later.
		iTimes[0] = 0.0
		iTimes[1:] = self.times

		averageLapTime = race.getAverageLapTime() if race else iTimes[-1] / float(len(iTimes) - 1)
		mustBeRepeatInterval = averageLapTime * 0.5

		# Remove duplicate entries.
		while len(iTimes) > 2:
			try:
				i = (i for i in xrange(len(iTimes) - 1, 0, -1) \
						if iTimes[i] - iTimes[i-1] < mustBeRepeatInterval).next()
				if i == 1:
					iDelete = i				# if the short interval is the first one, delete i
				elif i == len(iTimes) - 1:
					iDelete = i - 1			# if the short interval is the last one, delete i - 1
				else:
					#
					# Delete the entry that equalizes the time on each side.
					# -------g-------h---i---------j---------
					#
					g = i - 2
					h = i - 1
					j = i + 1
					gh = iTimes[h] - iTimes[g]
					ij = iTimes[j] - iTimes[i]
					iDelete = i - 1 if gh < ij else i
				del iTimes[iDelete]
			except StopIteration:
				break

		return self.removeEarlyTimes(iTimes)

	def getExpectedLapTime( self, iTimes = None ):
		if iTimes is None:
			iTimes = self.getCleanLapTimes()
			if iTimes is None:
				return None

		if len(iTimes) == 2:
			# If only one lap is known, rely on the global average.
			#return getRace().getAverageLapTime()
			return iTimes[-1]

		# Ignore the first lap time as there is often a staggered start.
		if len(iTimes) > 2:
			iStart = 2
		else:
			iStart = 1

		# Compute differences between times.
		dTimes = [iTimes[i] - iTimes[i-1] for i in xrange(iStart, len(iTimes))]
		dTimes.sort()
		median = dTimes[int(len(dTimes) / 2)]

		mMin = median * Rider.pMin
		mMax = median * Rider.pMax

		#print 'median = %f' % median

		# Compute the average lap time (ignore times that are way off based on the median).
		# Check the most common case first (no wacky lap times).
		if mMin < dTimes[0] and dTimes[-1] < mMax:
			return sum(dTimes, 0.0) / len(dTimes)

		# Ignore the outliers and compute the average based on the core data.
		iLeft  = (i for i in xrange(0, len(dTimes))     if dTimes[i]   > mMin).next()
		iRight = (i for i in xrange(len(dTimes), 0, -1) if dTimes[i-1] < mMax).next()
		return sum(dTimes[iLeft:iRight], 0.0) / (iRight - iLeft)

	def removeEarlyTimes( self, times ):
		try:
			startOffset = race.getCategory(self.num).getStartOffsetSecs()
			if startOffset:
				times = [t for t in times if t == 0.0 or t > startOffset]
				if len(times) <= 1:
					return []
		except (ValueError, AttributeError):
			pass
		assert len(times) == 0 or len(times) >= 2
		return times
		
	def countEarlyTimes( self ):
		count = 0
		try:
			startOffset = race.getCategory(self.num).getStartOffsetSecs()
			if startOffset:
				for t in self.times:
					if t >= startOffset:
						break
					if t > 0.0:
						count += 1
		except Exception as e:
			pass
		return count
		
	def interpolate( self, stopTime = maxInterpolateTime ):
		if not self.times or self.status in [Rider.DNS, Rider.DQ]:
			return tuple()
		
		# Check if we need to do any interpolation or if the user wants the raw data.
		if not getattr(self, 'autocorrectLaps', True):
			if not self.times:
				return tuple()
			iTimes = [None] * (len(self.times) + 1)
			# Add a zero start time for the beginning of the race.
			# This avoids a whole lot of special cases later.
			iTimes[0] = 0.0
			iTimes[1:] = self.times
			return tuple(Entry(t=t, lap=i, num=self.num, interp=False)
						for i, t in enumerate(self.removeEarlyTimes(iTimes)))

		# Adjust the stop time.
		st = stopTime
		dnfPulledTime = None
		if self.status in [Rider.DNF, Rider.Pulled]:
			# If no given time, use the last recorded time for DNF and Pulled riders.
			dnfPulledTime = self.tStatus if self.tStatus is not None else self.times[-1]
			st = min(st, dnfPulledTime + 0.01)
		
		iTimes = self.getCleanLapTimes()
		
		if not iTimes:
			return tuple()

		# Flag that these are not interpolated times.
		expected = self.getExpectedLapTime( iTimes )
		iTimes = [(t, False) for t in iTimes]
		
		# Check for missing lap data and fill it in.
		for missing in xrange(1, 3):
			mMin = expected * missing + expected * Rider.pMin
			mMax = expected * missing + expected * Rider.pMax
			for j in (j for j in xrange(len(iTimes)-1, 0, -1) if mMin < (iTimes[j][0] - iTimes[j-1][0]) < mMax):
				tStart = iTimes[j-1][0]
				interp = float(iTimes[j][0] - tStart) / float(missing + 1)
				fill = [(tStart + interp * m, True) for m in xrange(1, missing+1)]
				iTimes[j:j] = fill

		# Pad out to one entry exceeding stop time if we are less than it.
		tBegin = iTimes[-1][0]
		if tBegin < st and len(iTimes) < Rider.entriesMax:
			tBegin += expected
			iMax = max( 1, int(math.ceil(st - tBegin) / expected) if expected > 0 else 1 )
			iMax = min( iMax, Rider.entriesMax - len(iTimes) )
			iTimes.extend( [(tBegin + expected * i, True) for i in xrange(iMax)] )

		# Remove any entries exceeding the dnfPulledTime.
		if dnfPulledTime is not None and tBegin > dnfPulledTime:
			i = bisect.bisect_right( iTimes, (dnfPulledTime, False) )
			while i < len(iTimes) and iTimes[i][0] <= dnfPulledTime:
				i += 1
			del iTimes[i:]
		
		if len(iTimes) <= 1:
			return tuple()
		return tuple(Entry(t=it[0], lap=i, num=self.num, interp=it[1]) for i, it in enumerate(iTimes))
		
	def hasInterpolatedTime( self, tMax ):
		interpolate = self.interpolate()
		try:
			return any( e.interp for e in interpolate if e.t <= tMax )
		except (ValueError, StopIteration):
			return False

class NumTimeInfo(object):

	Original	= 0
	Add			= 1
	Edit		= 2
	Delete		= 3
	Swap		= 4
	Split		= 5
	MaxReason	= 6
	
	ReasonName = {
		Original:	'Original',
		Add:		'Add',
		Edit:		'Edit',
		Delete:		'Delete',
		Swap:		'Swap',
		Split:		'Split',
	}

	def __init__( self ):
		self.info = {}
		
	def _setData( self, num, t, reason ):
		self.info.setdefault(num,{})[t]  = (reason, CurrentUser, datetime.datetime.now())
		
	def _delData( self, num, t ):
		try:
			j = self.info[num]
			del j[t]
			if not j:
				del self.info[num]
		except KeyError:
			pass
		
	def add( self, num, t, reason = None ):
		self._setData( num, t, reason if reason is not None else NumTimeInfo.Add )
		
	def change( self, num, tOld, tNew, reason = None ):
		if tOld is None:
			self.add( num, tNew )
		elif tNew == tOld:
			self.add( num, tNew, reason )
		else:
			self._delData( num, tOld )
			self._setData( num, tNew, reason if reason is not None else NumTimeInfo.Edit )
	
	def adjustAllTimes( self, dTime ):
		newInfo = {}
		for num, numInfo in self.info.iteritems():
			newInfo[num] = dict( (t+dTime, v) for t, v in numInfo.iteritems() )
		self.info = newInfo
	
	def delete( self, num, t, reason = None ):
		self._setData( num, t, reason if reason is not None else NumTimeInfo.Delete )
		
	def renumberRider( self, numOld, numNew ):
		if numOld in self.info:
			self.info[numNew] = self.info[numOld]
			del self.info[numOld]
	
	def swapRiders( self, numOld, numNew ):
		if numOld in self.info or numNew in self.info:
			self.info[numOld], self.info[numNew] = self.info.get(numNew, {}), self.info.get(numOld, {})
			if not self.info[numOld]:
				del self.info[numOld]
			if not self.info[numNew]:
				del self.info[numNew]
	
	def __contains__( self, key ):			# Key is (num, t)
		try:
			return key[1] in self.info[key[0]]
		except KeyError:
			return False
	
	def getInfo( self, num, t ):
		try:
			return self.info[num][t]
		except KeyError:
			return None
			
	def getInfoStr( self, num, t ):
		info = self.getInfo( num, t )
		if info is None:
			return ''
		infoStr = u'{}, {}\n    by: {}\n    on: {}\n'.format(Utils.formatTime(t, True), NumTimeInfo.ReasonName[info[0]], info[1], info[2].ctime())
		return infoStr
			
	def getNumInfo( self, num ):
		return self.info.get( num, {} )
		
class Race(object):
	finisherStatusList = [Rider.Finisher, Rider.Pulled]
	finisherStatusSet = set( finisherStatusList )
	
	nonFinisherStatusList = [Rider.DNF, Rider.DNS, Rider.DQ, Rider.NP, Rider.OTL]
	nonFinisherStatusSet = set( nonFinisherStatusList )
	
	UnitKm = 0
	UnitMiles = 1
	
	advancePhotoMillisecondsDefault = -100
	city = ''
	stateProv = ''
	country = ''
	
	def __init__( self ):
		self.reset()

	def reset( self ):
		self.name = '<EventName>'
		self.organizer = '<Organizer>'
		
		self.city = '<MyCity>'
		self.stateProv = '<MyStateProv>'
		self.country = '<MyCountry>'
		
		self.raceNum = 1
		self.date = datetime.date.today().strftime('%Y-%m-%d')
		self.scheduledStart = '10:00'
		self.minutes = 60
		self.commissaire = '<Commissaire>'
		self.memo = '<RaceMemo>'
		self.discipline = 'Cyclo-cross'

		self.categories = {}
		self.riders = {}
		self.startTime = None
		self.finishTime = None
		self.numLaps = None
		self.firstRecordedTime = None	# Used to trigger the race on the first recorded time.
		
		self.allCategoriesFinishAfterFastestRidersLastLap = True
		self.isTimeTrial = False
		
		self.autocorrectLapsDefault = True
		self.highPrecisionTimes = False
		self.syncCategories = True
		self.modelCategory = 0
		self.distanceUnit = Race.UnitKm
		self.missingTags = set()
		
		self.enableUSBCamera = False
		self.enableJChipIntegration = False
		self.photoCount = 0
		
		# Animation options.
		self.finishTop = False
		self.reverseDirection = False
		
		self.isChangedFlag = True
		
		self.allCategoriesHaveRaceLapsDefined = False
		
		self.numTimeInfoField = NumTimeInfo()
		
		self.tagNums = None
		memoize.clear()
	
	@property
	def numTimeInfo( self ):
		try:
			return self.numTimeInfoField
		except AttributeError:
			self.numTimeInfoField = NumTimeInfo()
			return self.numTimeInfoField
	
	@property
	def enableVideoBuffer( self ):
		return getattr(self, 'enableUSBCamera', False) and getattr(self, 'enableJChipIntegration', False)
		
	@property
	def distanceUnitStr( self ):
		return 'km' if getattr(self, 'distanceUnit', Race.UnitKm) == Race.UnitKm else 'miles'
		
	@property
	def speedUnitStr( self ):
		return 'km/h' if getattr(self, 'distanceUnit', Race.UnitKm) == Race.UnitKm else 'mph'
	
	def resetCache( self ):
		memoize.clear()
	
	def hasRiders( self ):
		return len(self.riders) > 0

	def isChanged( self ):
		return getattr(self, 'isChangedFlag', False)

	def setChanged( self, changed = True ):
		self.isChangedFlag = changed
		if changed:
			memoize.clear()
		
	def isRunning( self ):
		return self.startTime is not None and self.finishTime is None

	def isUnstarted( self ):
		return self.startTime is None

	def isFinished( self ):
		return self.startTime is not None and self.finishTime is not None

	def startRaceNow( self ):
		self.startTime = datetime.datetime.now()
		self.tagNums = None
		self.missingTags = set()
		self.setChanged()

	def finishRaceNow( self ):
		self.finishTime = datetime.datetime.now()
		self.tagNums = None
		self.setChanged()

	def set( self, values = None ):
		self.reset()
		if values is not None:
			for k, d in values.iteritems():
				if k in self.__dict__:
					self.__dict__[k] = d

	def getRider( self, num ):
		try:
			num = int(num,10)
		except TypeError:
			num = int(num)

		try:
			rider = self.riders[num]
		except KeyError:
			rider = Rider( num )
			self.riders[num] = rider
			rider.autocorrectLaps = getattr(self, 'autocorrectLapsDefault', True)
		return rider

	def getRiderNumbers( self ):
		return self.riders.keys()
		
	def __contains__( self, num ):
		return num in self.riders

	def __getitem__( self, num ):
		return self.riders[num]

	def curRaceTime( self ):
		if self.startTime is None:
			return 0.0
		tCur = datetime.datetime.now() - self.startTime
		return tCur.total_seconds()

	def lastRaceTime( self ):
		if self.finishTime is not None:
			t = self.finishTime - self.startTime
			return t.total_seconds()
		return self.curRaceTime()

	def addTime( self, num, t = None ):
		if t is None:
			t = self.curRaceTime()
		
		if getattr(self, 'isTimeTrial', False):
			r = self.getRider(num)
			if r.firstTime is None:
				r.firstTime = t
			else:
				r.addTime( t - r.firstTime )
		else:
			if getattr(race, 'enableJChipIntegration', False):
				if getattr(self, 'resetStartClockOnFirstTag', False):
					if not getattr(self, 'firstRecordedTime', None):
						self.firstRecordedTime = self.startTime + datetime.timedelta( seconds = t )
						self.startTime = self.firstRecordedTime
						t = 0.0
					r = self.getRider(num)
					if r.firstTime is None:
						r.firstTime = t
					else:
						r.addTime( t )
						
				elif getattr(self, 'skipFirstTagRead', False):
					if not getattr(self, 'firstRecordedTime', None):
						self.firstRecordedTime = self.startTime + datetime.timedelta( seconds = t )
					r = self.getRider(num)
					if r.firstTime is None:
						r.firstTime = t
					else:
						r.addTime( t )
						
				else:
					self.getRider(num).addTime( t )
			else:
				self.getRider(num).addTime( t )
		
		self.setChanged()
		return t

	def importTime( self, num, t ):
		self.getRider(num).addTime( t )
		
	def deleteRiderTimes( self, num ):
		try:
			rider = self.riders[num]
			rider.times = []
			rider.firstTime = None
		except KeyError:
			pass
			
	def clearAllRiderTimes( self ):
		for num in self.riders.iterkeys():
			self.deleteRiderTimes( num )
		self.firstRecordedTime = None
		self.startTime = None
		self.finishTime = None
		self.setChanged()

	def deleteRider( self, num ):
		try:
			del self.riders[num]
			self.setChanged()
		except KeyError:
			pass
			
	def deleteAllRiders( self ):
		self.riders = {}
		self.setChanged()
			
	def renumberRider( self, num, newNum ):
		try:
			rider = self.riders[num]
		except KeyError:
			return False
		if newNum in self.riders:
			return False
			
		del self.riders[rider.num]
		rider.num = newNum
		self.riders[rider.num] = rider
		memoize.clear()
		self.setChanged()
		return True
			
	def swapRiders( self, num1, num2 ):
		try:
			r1 = self.riders[num1]
			r2 = self.riders[num2]
		except KeyError:
			return False
		
		del self.riders[num1]
		del self.riders[num2]
		r1.num, r2.num = r2.num, r1.num
		self.riders[r1.num] = r1
		self.riders[r2.num] = r2
		self.setChanged()
		return True
			
	def copyRiderTimes( self, num1, num2 ):
		try:
			r1 = self.riders[num1]
		except KeyError:
			return False
			
		r2 = self.getRider( num2 )
		
		tAdjust = random.random() * 0.00001
		r2.times = [t - tAdjust for t in r1.times]
		r2.status = Rider.Finisher
		r2.tStatus = None
		r2.autocorrectLaps = True
		r2.firstTime = getattr(r1, 'firstTime', None)
		
		self.setChanged()
		return True
	
	def deleteTime( self, num, t ):
		if not num in self.riders:
			return
		rider = self.riders[num]
		rider.deleteTime( t )
		self.setChanged()

	@memoize
	def getLastKnownTimeRider( self ):
		tBest, rBest = -1, None
		for r in self.riders.itervalues():
			try:
				t = r.getLastKnownTime()
				if t > tBest:
					tBest, rBest = t, r
			except ValueError:
				pass
				
		return tBest, rBest

	@memoize
	def getBestLapTime( self, lap ):
		try:
			return min( (r.getBestLapTime(lap), n) for n, r in self.riders.iteritems() )
		except ValueError:
			return 0.0
	
	@memoize
	def getAverageLapTime( self ):
		tTotal, count = 0.0, 0
		for r in self.riders.itervalues():
			t, c = r.getTimeCount()
			tTotal += t
			count += c
		if count > 0:
			averageLapTime = tTotal / count
		else:
			averageLapTime = 8.0 * 60.0	# Default to 8 minutes.
		return averageLapTime

	@memoize
	def interpolate( self ):
		# Reduce memory management in the list assignment.
		entries = [None] * Rider.entriesMax * len(self.riders)
		iCur, iEnd = 0, 0
		for rider in self.riders.itervalues():
			interpolate = rider.interpolate()
			iEnd = iCur + len(interpolate)
			entries[iCur:iEnd] = interpolate
			iCur = iEnd
		del entries[iEnd:]
		entries.sort( key=Entry.key )
		return entries

	def getLastRecordedTime( self ):
		try:
			return max( e.t for e in self.interpolate() if not e.interp )
		except:
			return None
		
	@memoize
	def interpolateCategoryNumLaps( self ):
		entries = self.interpolate()
		if not entries:
			return []
		
		# Find the number of laps for the category of each rider.
		riderNumLapsMax = {}
		for r in self.riders.iterkeys():
			try:
				catNumLaps = self.getCategory(r).getNumLaps()
				riderNumLapsMax[r] = catNumLaps if catNumLaps else 500
			except AttributeError:
				riderNumLapsMax[r] = 500
		
		# Filter results so that only the allowed number of laps is returned.
		return [e for e in entries if e.lap <= riderNumLapsMax[e.num]]
	
	@memoize
	def interpolateLap( self, lap, useCategoryNumLaps = False ):
		entries = self.interpolate() if not useCategoryNumLaps else self.interpolateCategoryNumLaps()
		# Find the first occurrence of the given lap.
		if not entries:
			return []

		if lap > self.getMaxAnyLap():
			lap = self.getMaxAnyLap()

		# Find the first entry for the given lap.
		try:
			iFirst = (i for i, e in enumerate(entries) if e.lap == lap).next()
			# Remove all entries except the next time for each rider after the given lap.
			seen = {}
			return entries[:iFirst] + [ seen.setdefault(e.num, e) for e in entries[iFirst:] if e.num not in seen ]
		except StopIteration:
			pass
			
		return entries

	@memoize
	def interpolateLapNonZeroFinishers( self, lap, useCategoryNumLaps = False ):
		entries = self.interpolateLap( lap, useCategoryNumLaps )
		finisher = Rider.Finisher
		return [e for e in entries if e.t > 0 and self.riders[e.num].status == finisher]
	
	@memoize
	def getRule80LapTime( self, category = None ):
		entries = self.interpolate()
		if not entries or self.getMaxLap(category) < 2:
			return None

		if category:
			entries = [e for e in entries if e.lap <= 2 and self.getCategory(e.num) == category]
		else:
			entries = [e for e in entries if e.lap <= 2]
			
		# Find the first entry for the given lap.
		iFirst = (i for i, e in enumerate(entries) if e.lap == 1).next()
		try:
			iSecond = (i for i, e in enumerate(entries) if e.lap == 2).next()
		except StopIteration:
			iSecond = None

		# Try to figure out if we should use the first lap or the second.
		# The first lap may not be the same length as the second.
		if iSecond is not None:
			tFirst = entries[iFirst].t
			tSecond = entries[iSecond].t - tFirst
			tDifference = abs(tFirst - tSecond)
			tAverage = (tFirst + tSecond) / 2.0
			# If there is more than 5% difference, use the second lap (assume a run-up or start offset).
			if tDifference / tAverage > 0.05:
				t = tSecond
			else:
				t = max(tFirst, tSecond)	# Else, use the maximum of the two (aren't we nice!).
		else:
			t = entries[iFirst].t
		return t

	def getRule80CountdownTime( self, category = None ):
		try:
			return self.getRule80LapTime(category) * 0.8
		except:
			return None

	def getRule80RemainingCountdown( self ):
		rule80Begin, rule80End = self.getRule80BeginEndTimes()
		if rule80Begin is None:
			return None
		raceTime = self.lastRaceTime()
		if rule80Begin <= raceTime <= rule80End:
			tRemaining = rule80End - raceTime
			if tRemaining < 0.5:
				tRemaining = None
			return tRemaining
		return None

	@memoize
	def getMaxLap( self, category = None ):
		entries = self.interpolate()
		try:
			if not category:
				maxLap = max( (e.lap for e in entries if not e.interp) )
			else:
				maxLap = max( (e.lap for e in entries
									if not e.interp and self.getCategory(e.num) == category) )
		except ValueError:
			maxLap = 0
		return maxLap

	def getRaceLaps( self ):
		raceLap = self.getMaxLap()
		if self.numLaps is not None and self.numLaps < raceLap:
			raceLap = self.numLaps
		return raceLap

	@memoize
	def getMaxAnyLap( self ):
		entries = self.interpolate()
		if not entries:
			maxAnyLap = 0
		else:
			maxAnyLap = max( e.lap for e in entries )
		return maxAnyLap

	@memoize
	def getLeaderTimesNums( self ):
		entries = self.interpolate()
		if not entries:
			return None, None
			
		leaderTimes = [ 0.0 ]
		leaderNums = [ None ]
		leaderTimesLen = 1
		for e in (e for e in entries if e.lap == leaderTimesLen):
			leaderTimes.append( e.t )
			leaderNums.append( e.num )
			leaderTimesLen += 1
		
		if leaderTimesLen > 1 and getattr(self, 'allCategoriesHaveRaceLapsDefined', False):
			maxRaceLaps = max( category.getNumLaps() for category in self.categories.itervalues() if category.active )
			leaderTimes = leaderTimes[:maxRaceLaps + 1]
			leaderNums = leaderNums[:maxRaceLaps + 1]
		
		if leaderTimesLen == 1:
			return None, None
		else:
			return leaderTimes, leaderNums
	
	def getLeaderOfLap( self, lap ):
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		try:
			return leaderNums[lap]
		except (TypeError, IndexError):
			return None
	
	def getCurrentLap( self, t ):
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		try:
			return bisect.bisect_left(leaderTimes, t)
		except (TypeError, IndexError):
			return 0
	
	def getLeaderAtTime( self, t ):
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		try:
			return leaderNums[bisect.bisect_left(leaderTimes, t, hi=len(leaderTimes) - 1)]
		except (TypeError, IndexError):
			return None
	
	def getLeaderTimeLap( self ):
		# returns: (num, t, lap)
		leaderInfo = (None, None, None)

		entries = self.interpolate()
		if not entries:
			return leaderInfo

		raceTime = self.lastRaceTime()
		
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		i = bisect.bisect_right( leaderTimes, raceTime, hi=len(leaderTimes) - 1 )
		leaderInfo = (leaderNums[i], leaderTimes[i], i-1)
		return leaderInfo

	def getRule80BeginEndTimes( self ):
		if self.getMaxLap() < 2:
			return None
	
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		raceTime = self.lastRaceTime()
		i = bisect.bisect_right( leaderTimes, raceTime, hi=len(leaderTimes) - 1 )
		
		tLeaderLastLap = leaderTimes[i-1]

		try:
			if raceTime < self.minutes*60.0 + self.getAverageLapTime()/2.0:
				return tLeaderLastLap, tLeaderLastLap + self.getRule80CountdownTime()
		except:
			pass
		return None, None
		
	def getLeader( self ):
		try:
			return self.getLeaderTimeLap()[0]
		except:
			return None

	def getLeaderLapTime( self ):
		try:
			return self.riders[self.getLeader()].getExpectedLapTime()
		except:
			return None

	def getLeaderTime( self ):
		try:
			return self.getLeaderTimeLap()[1]
		except:
			return None

	@memoize
	def getCategoryTimesNums( self ):
		''' Return times and nums for the leaders of each category. '''
		ctn = {}
		
		activeCategories = [c for c in self.categories.itervalues() if c.active]
		activeCategories.sort( key = Category.key )
		
		entries = self.interpolate()
		getCategory = self.getCategory
		for c in activeCategories:
			times = [0.0]
			nums = [None]
			lapCur = 1
			for e in (e for e in entries if e.lap == lapCur and getCategory(e.num) == c):
				times.append( e.t )
				nums.append( e.num )
				lapCur += 1
				
			ctn[c] = [times, nums]
		
		return ctn
		
	@memoize
	def getCategoryRaceLaps( self ):
		crl = {}
		raceTime = self.minutes * 60.0
		for c, (catTimes, catNums) in self.getCategoryTimesNums().iteritems():
			if len(catTimes) < 2 or self.getMaxLap(c) < 2:
				continue
			lap = bisect.bisect( catTimes, raceTime, hi=len(catTimes) - 1 )
			if lap > 1:
				catWinner = self.riders[catNums[lap]]
				entries = catWinner.interpolate()
				if entries[lap].interp:
					lapTime = catTimes[lap] - catTimes[lap-1]
					if catTimes[lap] - raceTime > lapTime / 2:
						lap -= 1
			crl[c] = lap
		
		return crl
		
	def isOutsideTimeBound( self, num ):
		category = self.getCategory( num )
		
		rule80Time = self.getRule80CountdownTime(category)
		if not rule80Time:
			return False
			
		try:
			leaderTimes = self.getCategoryTimesNums()[category][0]
		except KeyError:
			leaderTimes = self.getLeaderTimesNums()[0]
			
		if not leaderTimes:
			return False
			
		# Get the time the leader started this lap.
		t = self.curRaceTime()
		leaderLap = bisect.bisect_right(leaderTimes, t) - 1
		leaderTime = leaderTimes[leaderLap]

		# Get the rider time for the same lap.
		entries = self.interpolate()
		i = bisect.bisect_left( entries, Entry(num = 0, lap = leaderLap, t = leaderTime, interp = False) )
		try:
			riderTime = (e.t for e in itertools.islice(entries, i, len(entries)) if e.num == num and e.lap == leaderLap).next()
		except StopIteration:
			return False
		
		# Check if the difference exceeds the rule80 time.
		return riderTime - leaderTime > rule80Time

	def getCatPrevNextLeaders( self, t ):
		''' Return a dict accessed by number referring to category. '''
		catPrevLeaders, catNextLeaders = {}, {}
		for c, (times, nums) in self.getCategoryTimesNums().iteritems():
			i = bisect.bisect_right( times, t ) - 1
			catPrevLeaders[nums[i]] = c
			try:
				catNextLeaders[nums[i+1]] = c
			except IndexError:
				pass
		return catPrevLeaders, catNextLeaders
		
	def getPrevNextLeader( self, t ):
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		try:
			i = bisect.bisect_left(leaderTimes, t, hi=len(leaderTimes) - 1)
			return leaderNums[i-1], leaderNums[i]
		except (TypeError, IndexError):
			return None, None
		
	def hasDNFRiders( self ):
		return any(r.status == Rider.DNF for r in self.riders.itervalues())

	def numDNFRiders( self ):
		return sum( (1 for r in self.riders.itervalues() if r.status == Rider.DNF) )

	def hasPulledRiders( self ):
		return any(r.status == Rider.Pulled for r in self.riders.itervalues())

	def numPulledRiders( self ):
		return sum( (1 for r in self.riders.itervalues() if r.status == Rider.Pulled) )

	def getCategories( self, startWaveOnly = True, uploadOnly = False, excludeCustom = False ):
		activeCategories = [c for c in self.categories.itervalues() if c.active and (not startWaveOnly or c.catType == Category.CatWave)]
		if uploadOnly:
			activeCategories = [c for c in activeCategories if c.uploadFlag]
		if excludeCustom:
			activeCategories = [c for c in activeCategories if c.catType != Category.CatCustom]
		activeCategories.sort( key = Category.key )
		return activeCategories

	def setCategoryMask( self ):
		self.categoryMask = ''
		
		masks = []
		for c in self.categories.itervalues():
			if not c.active:
				continue
			maskCur = c.getMask()
			if maskCur is None:
				return
			masks.append( maskCur )
		
		if not masks:
			return

		maskLen = len(masks[0])
		if any( len(m) != maskLen for m in masks ):
			return

		cp = commonprefix( masks )
		mask = cp.ljust( maskLen, '.' )
		self.categoryMask = mask

	def getCategoryMask( self ):
		if getattr(self, 'categoryMask', None) is None:
			self.setCategoryMask()
		return self.categoryMask

	def getAllCategories( self ):
		allCategories = [c for c in self.categories.itervalues()]
		allCategories.sort( key = Category.key )
		return allCategories

	def setActiveCategories( self, active = None ):
		allCategories = self.getAllCategories()
		for i, c in enumerate(allCategories):
			c.active = True if active is None or i in active else False
		self.setChanged()
		
	def getCategoryWave( self, category ):
		if not category.active:
			return None
		if category.catType == Category.CatWave:
			return category
		if category.catType == Category.CatCustom:
			return None
		categories = [c for c in self.categories.itervalues() if c.active and c.catType != Category.CatCustom]
		if not categories:
			return None
		categories.sort( lambda c: c.sequence )
		categoryWave = category[0]
		for c in categories:
			if c.catType == Category.CatWave:
				categoryWave = c
			elif c == category:
				return categoryWave
		return None
		
	def adjustCategoryWaveNumbers( self, category ):
		if category.catType != Category.CatWave or not category.active:
			return
		if not getattr(self, 'categoryNumsCache', None):
			self._buildCategoryCache()
		
		categories = [c for c in self.categories.itervalues() if c.active and c.catType != Category.CatCustom and c.sequence > category.sequence]
		categories.sort( key = lambda c: c.sequence )
		
		unionNums = set()
		for c in categories:
			if c.catType == Category.CatWave:
				break
			unionNums |= c.getMatchSet()
		
		if unionNums:
			category.catStr = u','.join( unicode(n) for n in sorted(unionNums) )
			category.normalize()
		
	def adjustAllCategoryWaveNumbers( self ):
		categories = [c for c in self.categories.itervalues() if c.active and c.catType == Category.CatWave]
		for c in categories:
			self.adjustCategoryWaveNumbers( c )

	def setCategories( self, nameStrTuples ):
		i = 0
		newCategories = {}
		for t in nameStrTuples:
			args = dict( t )
			if not 'name' in args or not args['name']:
				continue
			args['sequence'] = i
			category = Category( **args )
			# Ensure we don't have any duplicate category fullnames.
			if category.fullname in newCategories:
				originalName = category.name
				for count in xrange(1, 999):
					category.name = _('{} Copy({})').format(originalName, count)
					if not category.fullname in newCategories:
						break
			newCategories[category.fullname] = category
			i += 1

		if self.categories != newCategories:
			self.categories = newCategories
			self.resetCategoryCache()
			self.setChanged()
			
			# Reclassify all the riders if something changed.
			for num in self.riders.iterkeys():
				self.getCategory( num )

			if self.categories:
				self.allCategoriesHaveRaceLapsDefined = True
				self.categoryLapsMax = 0
				for category in self.categories.itervalues():
					if not category.active:
						continue
					if category.getNumLaps():
						self.categoryLapsMax = max( self.categoryLapsMax, category.getNumLaps() )
					else:
						self.allCategoriesHaveRaceLapsDefined = False
						break
			else:
				self.allCategoriesHaveRaceLapsDefined = False
				
			changed = True
		else:
			changed = False
			
		if self.allCategoriesHaveRaceLapsDefined:
			self.numLaps = self.categoryLapsMax
			
		self.setCategoryMask()
		
		return changed

	def exportCategories( self, fp ):
		fp.write( u'#################################################################\n' )
		fp.write( u'# CrossMgr Categories File\n' )
		fp.write( u'#\n' )
		fp.write( u'# Created By: {}\n'.format(CurrentUser) )
		fp.write( u'# Created On: {}\n'.format(datetime.datetime.now()) )
		fp.write( u'#   Computer: {}\n'.format(CurrentComputer) )
		fp.write( u'#  From Race: "{}-r{}"\n'.format(self.name, self.raceNum) )
		fp.write( u'#    Version: {}\n'.format(Version.AppVerName) )
		fp.write( u'#\n' )
		fp.write( u'# for details see http://sites.google.com/site/crossmgrsoftware/\n' )
		fp.write( u'#################################################################\n' )
		categoryTypeName = ['Wave', 'Component', 'Custom']
		for c in sorted( self.categories.itervalues(), key = Category.key ):
			fp.write( u'{}\n'.format( u'|'.join( [
							c.name.replace('|',''),
							c.catStr.replace('|',''),
							getattr(c,'gender','Open'),
							categoryTypeName[c.catType]
						]) ) )

	def importCategories( self, fp ):
		categories = []
		for r, line in enumerate(fp):
			line = line.strip()
			if not line or line.startswith('#'):
				continue
			fields = line.split('|')
			if len(fields) < 2:
				continue
			if len(fields) < 3:
				fields.append( 'Open' )
			if len(fields) < 4:
				fields.append( 'Wave' )
			catType = { 'Wave':0, 'Component':1, 'Custom':2 }.get( fields[4], 0 )
			categories.append( {'name':fields[0], 'catStr':fields[1], 'gender':fields[2], 'catType':catType} )
		self.setCategories( categories )

	def catCount( self, category ):
		return sum( 1 for num in self.riders.iterkeys() if self.inCategory(num, category) )
		
	def hasCategory( self, category ):
		# Check if there is at least one rider in this category.
		return any( self.inCategory(num, category) for num in self.riders.iterkeys() )

	def hasTime( self, num, t ):
		try:
			rider = self.riders[num]
			if getattr(self, 'isTimeTrial', False):
				if getattr(rider, 'firstTime', None) is None:
					return False
				t -= rider.firstTime
			return rider.times[bisect.bisect_left(rider.times, t)] == t
		except (KeyError, IndexError):
			return False
	
	def getCategoryName( self, num ):
		c = self.getCategory( num )
		return c.name if c else ''

	def _buildCategoryCache( self ):
		# Reset the cache for all categories by sequence number.
		self.categoryCache = {}
		self.categoryNumsCache = {}
		categories = [c for c in self.categories.itervalues() if c.active and c.catType == Category.CatWave]
		if not categories:
			return None
			
		# Handle bib exclusivity for wave categories.
		categories.sort( key = lambda c: c.sequence )
		for c in categories:
			for n in c.getMatchSet():
				if n not in self.categoryCache:
					self.categoryCache[n] = c

		# Now handle all categories.
		# Bib exclusivity in enforced for component categories based on their wave.
		# Custom categories have no exclusivity rules.
		categories = [c for c in self.categories.itervalues() if c.active]
		categories.sort( key = lambda c: c.sequence )
		
		self.categoryNumsCache = dict( (c, set()) for c in categories if c.catType != Category.CatCustom )
		for n, c in self.categoryCache.iteritems():
			self.categoryNumsCache[c].add( n )
		
		waveCategory = categories[0]
		waveNumsSeen = set()
		waveCategoryNums = set()
		for c in categories:
			if c.catType == Category.CatWave:
				waveCategory = c
				waveNumsSeen = set()
				waveCategoryNums = self.categoryNumsCache[c]
			elif c.catType == Category.CatComponent:
				cNumsCache = self.categoryNumsCache[c]
				for n in c.getMatchSet():
					if n in waveCategoryNums and n not in waveNumsSeen:
						cNumsCache.add( n )
						waveNumsSeen.add( n )
			else:	# c.catType == Category.CatCustom
				self.categoryNumsCache[c] = c.getMatchSet()		

	def getCategory( self, num ):
		# Check the cache for this rider.
		try:
			return self.categoryCache.get(num, None)
		except (TypeError, AttributeError):
			pass
		
		self._buildCategoryCache()
		return self.categoryCache.get(num, None)
	
	def inCategory( self, num, category ):
		if category is None:
			return True
			
		try:
			return num in self.categoryNumsCache[category]
		except (TypeError, AttributeError):
			pass
			
		self._buildCategoryCache()
		return num in self.categoryNumsCache[category]
		
	def getCategoriesInUse( self ):
		catSet = set()
		for num in self.riders.iterkeys():
			category = self.getCategory(num)
			if category:
				catSet.add( category )
		return sorted( catSet, key = Category.key )
	
	def getCategoryNumLaps( self, num ):
		try:
			category = self.getCategory( num )
			return category.getNumLaps() or 1000
		except AttributeError:
			return 1000
	
	def resetCategoryCache( self ):
		self.categoryCache = None
		self.categoryNumsCache = None
		
	def resetAllCaches( self ):
		self.resetCategoryCache()
		self.resetCache();
	
	def getRaceIntro( self ):
		intro = [
			_('Race: {}:{}').format(self.name, self.raceNum),
			_('Start: {} ({})').format(self.scheduledStart, self.date),
		]
		activeCategories = [c for c in self.categories.itervalues() if c.active]
		if all( c.numLaps for c in activeCategories ):
			activeCategories.sort( key = Category.key )
			intro.append( _('Category Laps: {}').format(', '.join( '{}'.format(c.numLaps) for c in activeCategories )) )
		else:
			intro.append( _('Duration: {} min').format(self.minutes) )
		return '\n'.join( intro )
	
	def getNextExpectedLeaderTNL( self, t ):
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		if leaderTimes:
			i = bisect.bisect_left( leaderTimes, t )
			if 0 < i < len(leaderTimes):
				return leaderTimes[i], leaderNums[i], leaderTimes[i] - leaderTimes[i-1]
		return None, None, None
	
	def isLeaderExpected( self ):
		if not self.isRunning():
			return False

		# Get the leaders and entries.
		leader = self.getLeader()
		entries = self.interpolate()
		if not entries or leader is None:
			return False

		# Check if the leader is expected in the next few riders.
		pos = bisect.bisect_right( entries, Entry(num=0, lap=0, t=self.curRaceTime(), interp=False) )
		for i in xrange(pos, min(pos+5, len(entries))):
			if entries[i].num == leader:
				return True
		return False
		
	def getTimeToLeader( self ):
		if not self.isRunning():
			return None, None
		leaderTimes, leaderNums = self.getLeaderTimesNums()
		if leaderTimes:
			tCur = self.curRaceTime()
			i = bisect.bisect_left( leaderTimes, tCur )
			if 0 < i < len(leaderTimes) and (self.numLaps is None or i <= self.numLaps):
				return leaderNums[i], leaderTimes[i] - tCur
		return None, None
		
	def getRiderNums( self ):
		return self.riders.keys()

	#---------------------------------------------------------------------------------------

	@memoize
	def getCatEntries( self ):
		# Split up all the entries by category.
		catEntries = {}
		getCategory = self.getCategory
		finisherStatusSet = Race.finisherStatusSet
		localCat = {}
		for e in self.interpolate():
			if race[e.num].status in finisherStatusSet:
				try:
					category = localCat[e.num]
				except KeyError:
					category = localCat[e.num] = getCategory(e.num)
				try:
					catEntries[category].append( e )
				except KeyError:
					catEntries[category] = [e]
		return catEntries
	
	def getPrevNextRiderPositions( self, tRace ):
		if not self.isRunning() or not self.riders:
			return {}, {}
			
		catEntriesDict = self.getCatEntries()
		if not catEntriesDict:
			return {}, {}

		# For each category, find the first instance of each rider after the leader's lap.
		catTimesNums = self.getCategoryTimesNums()
		ret = [{},{}]
		scanMax = len( self.riders ) * 2
		for cat, catEntries in catEntriesDict.iteritems():
			try:
				catTimes, catNums = catTimesNums[cat]
			except:
				continue
			iLap = bisect.bisect_right( catTimes, tRace )
			for r in xrange(2):
				if iLap >= len(catTimes):
					break
				iFirst = bisect.bisect_left( catEntries, Entry(catNums[iLap], iLap, catTimes[iLap], False) )

				seen = {}
				catFinishers = [ seen.setdefault(catEntries[i].num, catEntries[i])
								for i in xrange(iFirst, min(len(catEntries),iFirst+scanMax)) if catEntries[i].num not in seen ]
				catFinishers.sort( key = lambda x: (-x.lap, x.t, x.num) )
				for pos, e in enumerate(catFinishers):
					ret[r][e.num] = pos + 1
				iLap += 1
					
		return ret
		
	def getPrevNextRiderGaps( self, tRace ):
		if not self.isRunning() or not self.riders:
			return {}, {}
			
		catEntriesDict = self.getCatEntries()
		if not catEntriesDict:
			return {}, {}

		# For each category, find the first instance of each rider after the leader's lap.
		catTimesNums = self.getCategoryTimesNums()
		ret = [{},{}]
		scanMax = len( self.riders ) * 2
		for cat, catEntries in catEntriesDict.iteritems():
			try:
				catTimes, catNums = catTimesNums[cat]
			except:
				continue
			iLap = bisect.bisect_right( catTimes, tRace )
			for r in xrange(2):
				if iLap >= len(catTimes):
					break
				iFirst = bisect.bisect_left( catEntries, Entry(catNums[iLap], iLap, catTimes[iLap], False) )

				seen = {}
				catFinishers = [ seen.setdefault(catEntries[i].num, catEntries[i])
								for i in xrange(iFirst, min(len(catEntries),iFirst+scanMax)) if catEntries[i].num not in seen ]
				catFinishers.sort( key = lambda x: (-x.lap, x.t, x.num) )
				leader = catFinishers[0]
				for e in catFinishers:
					if leader.lap == e.lap:
						ret[r][e.num] = Utils.formatTimeGap( e.t - leader.t ) if leader.num != e.num else ' '
					else:
						lapsDown = e.lap - leader.lap
						ret[r][e.num] = _('{} laps').format(lapsDown) if lapsDown < -1 else _('{} lap').format(lapsDown)
				iLap += 1
					
		return ret
		
	#----------------------------------------------------------------------------------------
	
	@memoize
	def getCategoryBestLaps( self, category = None ):
		if category:
			# Check if the number of laps is specified.  If so, use that.
			# Otherwise, check if we can figure out the number of laps.
			lap = (category.getNumLaps() or self.getCategoryRaceLaps().get(category, None))
			if lap:
				return lap
				
		# Otherwise get the closest leader's lap time.
		times, nums = self.getLeaderTimesNums()
		if not times:
			return None
		raceTime = self.minutes * 60.0
		lap = bisect.bisect_left( times, raceTime, hi=len(times) - 1 )
		if lap > 1:
			lap = min( len(nums)-1, lap )
			entries = self.riders[nums[lap]].interpolate()
			if entries[lap].interp:
				lapTime = times[lap] - times[lap-1]
				if times[lap] - raceTime > lapTime / 2.0:
					lap -= 1
		return lap
		
	def getNumBestLaps( self, num ):
		if num not in self.riders:
			return 0
		category = self.getCategory( num )
		return self.getCategoryBestLaps( category )
	
	def addCategoryException( self, category, num ):
		try:
			num = int(num)
		except ValueError:
			return
		
		categoryWave = self.getCategoryWave( category )
		for c in self.categories.itervalues():
			if c != category and c != categoryWave:
				c.removeNum( num )
				c.normalize()
				
		category.addNum( num )
		category.normalize()
		
		if categoryWave:
			categoryWave.addNum( num )
			categoryWave.normalize()
		
		self.resetCategoryCache()
		self.setChanged()
		self.setCategoryMask()
	
	@memoize
	def allRidersFinished( self ):
		# This is dangerous!  Do not end the program early!  Always let the user end the race in case of additional laps.
		# Simply check that it has been 60 minutes since the race ended.
		if not self.isRunning():
			return True
			
		try:
			entries = self.interpolate()
			eLastRecorded = (e for e in reversed(entries) if not e.interp).next()
			return self.lastRaceTime() - eLastRecorded.t > 60.0*60.0
		except StopIteration:
			pass
			
		return False
		
	def setCategoryChoice( self, iSelection, categoryAttribute = None ):
		self.modelCategory = iSelection
		if categoryAttribute:
			setattr( self, categoryAttribute, iSelection )
			
	def getRawData( self ):
		''' Return all data in the model.  If edited, return the edit details. '''
		if not self.startTime:
			return None, None, None
			
		nti = self.numTimeInfo
		def dr( t, num, count, tOffset = 0 ):
			info = nti.getInfo(num, t)
			if info:
				return (t + tOffset, num, count, NumTimeInfo.ReasonName[info[0]], info[1], info[2].ctime())
			else:
				return (t + tOffset, num, count)
		
		data = []
		for num, r in self.riders.iteritems():
			entryCount = 1
			if getattr(self, 'isTimeTrial', False):
				data.append( dr(r.firstTime, num, entryCount) )
				entryCount += 1
				for t in r.times:
					data.append( dr(t, num, entryCount, r.firstTime) )
					entryCount += 1
			else:
				if r.firstTime:
					data.append( dr(r.firstTime, num, entryCount) )
					entryCount += 1
				for t in r.times:
					data.append( dr(t, num, entryCount) )
					entryCount += 1
				
		data.sort()
		
		return self.startTime, self.finishTime, data

	def _populate( self ):
		self.reset()

		random.seed( 1010101 )
		mean = 5 * 60
		var = 30
		lapsTotal = 5
		riders = 30
		self.startTime = datetime.datetime.now() - datetime.timedelta(seconds=lapsTotal*mean + 4*60)
		for num in xrange(100,100+riders+1):
			t = 0
			mu = random.normalvariate( mean, var )	# Rider's random average lap time.
			for laps in xrange(lapsTotal):
				t += random.normalvariate(mu, var )	# Rider's lap time.
				self.addTime( num, t )
		if Utils.isMainWin():
			Utils.getMainWin().startRaceClock()

		for j, i in enumerate(xrange(100,100+riders+1,10)):
			name = 'Cat{}'.format(j+1)
			self.categories[name] = Category(True, name, '{}-{}'.format(i, i+9) )

		self.setChanged()

if __name__ == '__main__':
	c = Category(True, 'test', '100-150,132,134,192,537,538,539,-199,205,-50-60,-80-90,-110,-111,-112,-113', '00:00')
	print( c.getMatchSet() )
	print( 105 in c.getMatchSet() )
	assert( c.matches(105) )
	assert( c.matches(100) )
	assert( not c.matches(99) )
	assert( c.matches(134) )
	assert( not c.matches(50) )
	print( c )
	print( c.intervals )
	print( sorted(c.exclude) )
	sys.exit()
	
	r = newRace()
	
	print( r.getMaxLap() )
	
	r.addTime( 10, 1 * 60 )
	r.addTime( 10, 5 * 60 )
	r.addTime( 10, 9 * 60 )
	r.addTime( 10, 10 * 60 )
	rider = r.getRider( 10 )
	entries = rider.interpolate( 11 )
	print( [(Utils.SecondsToMMSS(e.t), e.interp) for e in entries] )
	#sys.exit( 0 )
	
	r.addTime( 10,  5 )
	#r.addTime( 10, 10 )
	r.addTime( 10, 15 )
	r.addTime( 10, 15.05 )
	r.addTime( 10, 15.06 )
	r.addTime( 10, 20 )
	r.addTime( 10, 25 )
	r.addTime( 10, 30 )
	#r.addTime( 10, 35 )
	rider = r.getRider( 10 )
	entries = rider.interpolate( 36 )
	print( [(e.t, e.interp) for e in entries] )
	'''
	entries = rider.interpolate( 36 )
	print [e.t for e in entries]
	'''

	c = Category(True, 'test', '100-150-199,205,-50-60', '00:00')
	print( c )
	print( 'mask=', c.getMask() )
	c = Category(True, 'test', '100-199,-150')
	print( 'mask=', c.getMask() )
	c = Category(True, 'test', '1400-1499,-1450')
	print( 'mask=', c.getMask() )
	
	r.setCategories( [	{'name':'test1', 'catStr':'1100-1199'},
						{'name':'test2', 'catStr':'1200-1299, 2000,2001,2002'},
						{'name':'test3', 'catStr':'1300-1399'}] )
	print( r.getCategoryMask() )
	print( r.getCategory( 2002 ) )

