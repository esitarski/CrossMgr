from __future__ import print_function
import os
import io
import re
import sys
import math
import time
import copy
import bisect
import socket
import random
import getpass
import datetime
import itertools
import functools
import operator
import traceback
import threading
from os.path import commonprefix
from collections import defaultdict

import Utils
import Version
from BatchPublishAttrs import setDefaultRaceAttr
import minimal_intervals
from InSortedIntervalList import InSortedIntervalList

CurrentUser = getpass.getuser()
CurrentComputer = socket.gethostname()

maxInterpolateTime = 7.0*60.0*60.0	# 7 hours.

lock = threading.RLock()

#----------------------------------------------------------------------
class memoize(object):
	"""
	Decorator that caches a function's return value each time it is called.
	If called later with the same arguments, the cached value is returned, and
	not re-evaluated.
	
	Does NOT work with kwargs.
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
	memoize.clear()
	race = r
	if race:
		race.setChanged()

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
	
	all_nums = sorted( s )
	nBegin = nLast = all_nums.pop( 0 )
	
	intervals = []
	for n in all_nums:
		if n != nLast + 1:
			intervals.append( (nBegin, nLast) )
			nBegin = n
		nLast = n

	intervals.append( (nBegin, nLast) )		
	return intervals
	
def IntervalsToSet( intervals ):
	return set.union( *[set(xrange(i[0], i[1]+1)) for i in intervals] ) if intervals else set()

#----------------------------------------------------------------------
class Category(object):

	DistanceByLap = 0
	DistanceByRace = 1

	badRangeCharsRE = re.compile( u'[^0-9,\-]' )
	
	active = True
	CatWave = 0
	CatComponent = 1
	CatCustom = 2
	
	catType = 0
	publishFlag = True
	uploadFlag = True
	seriesFlag = True
	
	distance = None
	firstLapDistance = None
	distanceType = DistanceByLap
	raceMinutes = None
	
	lappedRidersMustContinue = False
	
	MaxBib = 999999
	
	# Attributes to be merged from existing catgories in category import or when reading categories from the Excel sheet.
	MergeAttributes = (
		'active',
		'numLaps',
		'raceMinutes',
		'startOffset',
		'distance',
		'distanceType',
		'firstLapDistance',
		'publishFlag',
		'uploadFlag',
		'seriesFlag',
		'catType',
	)
	PublishFlags = tuple( a for a in MergeAttributes if a.endswith('Flag') )

	def _getStr( self ):
		s = ['{}'.format(i[0]) if i[0] == i[1] else '{}-{}'.format(*i) for i in self.intervals]
		s.extend( ['-{}'.format(i[0]) if i[0] == i[1] else '-{}-{}'.format(*i) for i in SetToIntervals(self.exclude)] )
		return ','.join( s )
		
	def _setStr( self, s ):
		s = self.badRangeCharsRE.sub( u'', u'{}'.format(s) )
		if not s:
			s = u'{}-{}'.format(self.MaxBib, self.MaxBib)
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
					
				bounds[0] = min(bounds[0], self.MaxBib)	# Keep the numbers in a reasonable range to avoid performance issues.
				bounds[1] = min(bounds[1], self.MaxBib)
				
				if bounds[0] > bounds[1]:			# Swap the range if out of order.
					bounds[0], bounds[1] = bounds[1], bounds[0]
					
				if isExclusion:
					self.exclude.update( xrange(bounds[0], bounds[1]+1) )
				else:
					self.intervals.append( tuple(bounds) )
					
			except Exception as e:
				# Ignore any parsing errors.
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
						raceLaps = None, raceMinutes = None,
						distance = None, distanceType = None, firstLapDistance = None,
						gender = 'Open', lappedRidersMustContinue = False,
						catType = CatWave, publishFlag = True, uploadFlag = True, seriesFlag = True ):
		
		self.name = unicode(name).strip()
		self.catStr = unicode(catStr).strip()
		self.startOffset = startOffset if startOffset else '00:00:00'
		
		self.catType = self.CatWave
		catType = unicode(catType).strip().lower()
		try:
			self.catType = int(catType)
		except ValueError:
			try:
				if catType.startswith(u'component'):
					self.catType = self.CatComponent
				elif catType.startswith(u'custom'):
					self.catType = self.CatCustom
			except:
				pass
		
		def isBool( v ):
			v = unicode(v).strip()
			return v[:1] in u'TtYy1'
		
		self.active = isBool( active )
		self.publishFlag = isBool( publishFlag )
		self.uploadFlag = isBool( uploadFlag )
		self.seriesFlag = isBool( seriesFlag )
			
		try:
			self._numLaps = int(numLaps)
			if self._numLaps < 1:
				self._numLaps = None
		except (ValueError, TypeError):
			self._numLaps = None
		
		try:
			self.raceMinutes = int( raceMinutes )
		except (ValueError, TypeError):
			self.raceMinutes = None
		
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
			
		if self.distanceType not in (Category.DistanceByLap, Category.DistanceByRace):
			self.distanceType = Category.DistanceByLap
			
		try:
			self.firstLapDistance = float(firstLapDistance) if firstLapDistance else None
		except (ValueError, TypeError):
			self.firstLapDistance = None
		if self.firstLapDistance is not None and self.firstLapDistance <= 0.0:
			self.firstLapDistance = None
			
		self.gender = 'Open'
		try:
			genderFirstChar = unicode(gender or u'Open').strip()[:1].lower()
			if genderFirstChar in 'mhu':
				self.gender = 'Men'
			elif genderFirstChar in 'wfld':
				self.gender = 'Women'
		except:
			pass
			
		self.lappedRidersMustContinue = False
		lappedRidersMustContinue = u'{}'.format(lappedRidersMustContinue).strip()
		if lappedRidersMustContinue[:1] in u'TtYy1':
			self.lappedRidersMustContinue = True

	def __setstate( self, d ):
		self.__dict__.update(d)
		i = getattr( self, 'intervals', None )
		if i:
			i.sort()
	
	def getLapDistance( self, lap ):
		if self.distanceType != Category.DistanceByLap:
			return None
		if lap <= 0:
			return 0

		return self.firstLapDistance if lap == 1 and self.firstLapDistance else self.distance
	
	def getDistanceAtLap( self, lap ):
		if self.distanceType != Category.DistanceByLap:
			return None
		if lap == 1 and not (self.firstLapDistance or self.distance):
			return None
		if lap <= 0:
			return 0
		return (self.firstLapDistance or self.distance or 0.0) + (self.distance or 0.0) * (lap-1)
	
	@staticmethod
	def getFullName( name, gender ):
		GetTranslation = _
		return u'{} ({})'.format(name, GetTranslation(gender))
	
	@property
	def fullname( self ):
		return Category.getFullName( self.name.strip(), getattr(self, 'gender', u'Open') )
	
	@property
	def firstLapRatio( self ):
		if self.distanceType == Category.DistanceByLap and self.firstLapDistance and self.distance:
			return self.firstLapDistance / self.distance
		else:
			return 1.0
	
	@property
	def distanceIsByLap( self ):
		return self.distanceType == Category.DistanceByLap
	
	@property
	def distanceIsByRace( self ):
		return self.distanceType == Category.DistanceByRace

	def getNumLaps( self ):
		laps = getattr( self, '_numLaps', None )
		if (race and race.isTimeTrial) and ((laps or 0) < 1 and not self.raceMinutes):
			laps = 1
		if laps or not self.raceMinutes or not race or race.isTimeTrial:
			return laps
		
		# Estimate the number of laps based on the wave category leader's time.
		entries = race.interpolateCategory( self )
		if not entries:
			return None
		
		tFinish = self.raceMinutes * 60.0 + race.getStartOffset(entries[0].num)
		lapCur = 1
		tLeader = []
		for e in entries:
			if e.lap == lapCur:
				tLeader.append( e.t )
				if e.t > tFinish:
					break
				lapCur += 1
		if len(tLeader) <= 1:
			return 1
		
		# Check if the expected overlap exceeds race time by less than half a lap.
		if (tLeader[-1] - tFinish) < (tLeader[-1] - tLeader[-2]) / 2.0:
			return len(tLeader)
		return len(tLeader) - 1
		
	def setNumLaps( self, numLaps ):
		try:
			numLaps = int(numLaps)
		except (TypeError, ValueError):
			numLaps = None
		self._numLaps = numLaps if numLaps else None
		
	numLaps = property(getNumLaps, setNumLaps)
	
	def isNumLapsLocked( self ):
		return getattr(self, '_numLaps', None) is not None

	def matches( self, num, ignoreActiveFlag = False ):
		if not ignoreActiveFlag:
			if not self.active:
				return False
		return False if num in self.exclude else InSortedIntervalList( self.intervals, num )
		
	def getMatchSet( self ):
		matchSet = IntervalsToSet( self.intervals )
		matchSet.difference_update( self.exclude )
		return matchSet

	key_attr = ['sequence', 'name', 'active', 'startOffset', '_numLaps', 'raceMinutes', 'catStr',
				'distance', 'distanceType', 'firstLapDistance',
				'gender', 'lappedRidersMustContinue', 'catType', 'publishFlag', 'uploadFlag', 'seriesFlag']
	def __cmp__( self, c ):
		for attr in self.key_attr:
			cCmp = cmp( getattr(self, attr, None), getattr(c, attr, None) )
			if cCmp != 0:
				return cCmp 
		return 0
	
	def key( self ):
		return tuple( getattr(self, attr, None) for attr in self.key_attr )
		
	def copy( self, c ):
		for attr in self.key_attr:
			setattr( self, attr, getattr(c, attr) )
	
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

	def resetNums( self ):
		self.intervals = []
		self.exclude = set()
		self.catStr = ''
		
	def normalize( self ):
		# Combine any consecutive or overlapping intervals.
		all_nums = IntervalsToSet( self.intervals )
		
		# Remove unnecessary excludes.
		needlessExcludes = []
		for num in self.exclude:
			if num not in all_nums:
				needlessExcludes.append( num )
		self.exclude.difference_update( needlessExcludes )

		self.intervals = SetToIntervals( all_nums )
	
	def __repr__( self ):
		return u'Category(active={}, name="{}", catStr="{}", startOffset="{}", numLaps={}, raceMinutes={}, sequence={}, distance={}, distanceType={}, gender="{}", lappedRidersMustContinue="{}", catType="{}")'.format(
				self.active,
				self.name,
				self.catStr,
				self.startOffset,
				self._numLaps,
				self.raceMinutes,
				self.sequence,
				getattr(self,'distance',None),
				getattr(self,'distanceType', Category.DistanceByLap),
				getattr(self,'gender',''),
				getattr(self,'lappedRidersMustContinue',False),
				['Wave', 'Component', 'Custom'][self.catType],
			)

	def getStartOffsetSecs( self ):
		return Utils.StrToSeconds( self.startOffset )
		
	def setFromSet( self, s ):
		self.exclude = set()
		self.intervals = SetToIntervals( s )

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
		
	def __lt__( self, e ):
		return (
			((self.t > e.t) - (self.t < e.t)) or
			-((self.lap > e.lap) - (self.lap < e.lap)) or
			((self.num > e.num) - (self.num < e.num)) or
			((self.interp > e.interp) - (self.interp < e.interp))
		) < 0
		
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
		
	def isGap( self ):
		return self.num <= 0
		
	def setGroupCountGap( self, groupCount, gapTime ):
		self.num = -groupCount
		self.t = gapTime
		
	@property
	def gap( self ):
		return self.t
	@gap.setter
	def gap( self, gt ):
		self.t = gt
	
	@property
	def groupCount( self ):
		return -self.num
	@groupCount.setter
	def groupCount( self, gc ):
		self.num = -gc

	def __repr__( self ):
		return u'Entry(num={}, lap={}, interp={}, t={})'.format(self.num, self.lap, self.interp, self.t)

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
	
	firstTime = None				# Used for time trial mode.  Also used to flag the first start time.
	relegatedPosition = None
	autocorrectLaps = True
	
	def __init__( self, num ):
		self.num = num
		self.times = []
		self.status = Rider.Finisher
		self.tStatus = None
	
	def clearCache( self ):
		for attr in ('_iTimesLast', '_entriesLast'):
			try:
				delattr( self, attr )
			except AttributeError:
				pass
	
	def swap( a, b ):
		a.clearCache()
		b.clearCache()

		# Swap all attributes except the num.
		for attr in ('times', 'status', 'tStatus', 'autocorrectLaps', 'firstTime', 'relegatedPosition'):
			aVal = getattr( a, attr )
			bVal = getattr( b, attr )
			setattr( a, attr, bVal )
			setattr( b, attr, aVal )
	
	def __getstate__( self ):
		# Don't pickle cached entries.
		state = self.__dict__.copy()		
		state.pop( '_iTimesLast', None )
		state.pop( '_entriesLast', None )
		return state

	def __repr__( self ):
		return u'{} ({})'.format( self.num, self.statusNames[self.status] )
		
	def setAutoCorrect( self, on = True ):
		self.autocorrectLaps = on
		
	def addTime( self, t ):
		# All times in race time seconds.
		if t < 0.0:		# Don't add negative race times.
			return
			
		try:
			if t > self.times[-1]:
				self.times.append( t )
				return
		except IndexError:
			self.times.append( t )
			return
			
		i = bisect.bisect_left(self.times, t)
		if i >= len(self.times) or self.times[i] != t:
			self.times.insert( i, t )

	def deleteTime( self, t ):
		try:
			self.times.remove( t )
		except ValueError:
			pass

	def getTimeCount( self ):
		# Make sure we don't include times that exceed the number of laps.
		try:
			numLaps = min( race.getCategory(self.num)._numLaps or 999999, len(self.times) )
		except Exception as e:
			numLaps = len(self.times)
			
		if not numLaps:
			return 0.0, 0					# No times, no count.		
		elif numLaps == 1:
			# If we only have one lap, make sure we consider the start offset.
			try:
				startOffset = race.getStartOffset( self.num ) if not race.isTimeTrial else 0.0
			except:
				startOffset = 0.0
			return self.times[0] - startOffset, 1
		else:
			# Otherwise ignore the first lap.
			return self.times[numLaps-1] - self.times[0], numLaps-1

	def getLastKnownTime( self ):
		# Make sure we don't include times that exceed the number of laps.
		try:
			numLaps = min( race.getCategory(self.num)._numLaps or 999999, len(self.times) )
		except Exception as e:
			numLaps = len(self.times)
		
		try:
			return self.times[numLaps-1]
		except IndexError:
			return 0.0
			
	def getFirstKnownTime( self ):
		t = self.firstTime
		if t is None:
			try:
				t = self.times[0]
			except IndexError:
				pass
		return t

	def isDNF( self ):			return self.status == Rider.DNF
	def isDNS( self ):			return self.status == Rider.DNS
	def isPulled( self ):		return self.status == Rider.Pulled
	def isRelegated( self ):	return self.status == Rider.Finisher and self.relegatedPosition

	def setStatus( self, status, tStatus = None ):
		if status in (Rider.Finisher, Rider.DNS, Rider.DQ):
			tStatus = None
		elif status in (Rider.Pulled, Rider.DNF):
			if tStatus is None:
				tStatus = race.lastRaceTime() if race else None
		self.status = status
		self.tStatus = tStatus
	
	def getCleanLapTimes( self ):
		if not self.times or self.status in (Rider.DNS, Rider.DQ) or not race:
			return None

		# Create a separate working list.
		# Add the start offset for the beginning of the start wave.
		# This avoids special cases later.
		iTimes = [race.getStartOffset(self.num)]
		
		# Clean up spurious reads based on minumum possible lap time.
		# Also consider the median lap time.
		# Also removes early times.
		minPossibleLapTime = race.minPossibleLapTime
		medianLapTime = race.getMedianLapTime( race.getCategory(self.num) )
		if race.enableJChipIntegration:
			medianLapTime /= 10.0
		
		mustBeRepeatInterval = max( minPossibleLapTime, medianLapTime * 0.4 )
		for t in self.times:
			if t - iTimes[-1] > mustBeRepeatInterval:
				iTimes.append( t )
		
		try:
			numLaps = min( race.getCategory(self.num)._numLaps or 999999, len(iTimes) )
		except Exception as e:
			numLaps = len(iTimes)

		'''
		medianLapTime = race.getMedianLapTime() if race else (iTimes[-1] - iTimes[0]) / float(len(iTimes) - 1)
		mustBeRepeatInterval = medianLapTime * 0.5
		
		# Remove duplicate entries.
		while len(iTimes) > 2:
			try:
				# Don't correct the last lap - assume the rider looped around and cross the finish again.
				i = (i for i in xrange(len(iTimes) - 1, 0, -1) \
						if iTimes[i] - iTimes[i-1] < mustBeRepeatInterval).next()
				if i == 1:
					iDelete = i				# if the short interval is the first one, delete the next entry.
				elif i == len(iTimes) - 1:
					iDelete = i				# if the short interval is the last one, delete the last entry.
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
		'''
		
		# Ensure that there are no more times after the deleted ones.
		iTimes = iTimes[:numLaps+1]

		return iTimes if len(iTimes) >= 2 else []
		
	def getExpectedLapTime( self, iTimes = None ):
		if iTimes is None:
			iTimes = self.getCleanLapTimes()
			if iTimes is None:
				return None

		# If only 2 times, return a second lap adjusted for lap distance.
		if len(iTimes) == 2:
			d = iTimes[1] - iTimes[0]
			category = race.getCategory( self.num )
			return d / category.firstLapRatio if category else d
		
		# Return the median of the lap times ignoring the first lap.
		dTimes = sorted( b-a for b, a in zip(iTimes[2:], iTimes[1:]) )
		if not dTimes:
			return None
			
		dTimesLen = len(dTimes)
		return dTimes[dTimesLen // 2] if dTimesLen & 1 else (dTimes[dTimesLen//2-1] + dTimes[dTimesLen//2]) / 2.0

	def removeEarlyTimes( self, times ):
		try:
			startOffset = race.getStartOffset(self.num) if race else 0.0
			if startOffset:
				times = [t for t in times if t >= startOffset]
				if len(times) <= 1:
					return []
		except (ValueError, AttributeError):
			pass
		assert len(times) == 0 or len(times) >= 2
		return times
	
	def removeLateTimes( self, iTimes, dnfPulledTime ):
		if iTimes and dnfPulledTime is not None:
			i = bisect.bisect_right( iTimes, (dnfPulledTime,True) )
			if i < len(iTimes):
				while i > 1 and iTimes[i-1][0] > dnfPulledTime:
					i -= 1
			del iTimes[i:]
		if len(iTimes) < 2:
			iTimes = []
		return iTimes

	def countEarlyTimes( self ):
		count = 0
		try:
			startOffset = race.getStartOffset(self.num)
			if startOffset:
				for t in self.times:
					if t < startOffset:
						count += 1
		except Exception as e:
			pass
		return count
	
	def getEntries( self, iTimes ):
		try:
			if self._iTimesLast == iTimes:
				return self._entriesLast
		except AttributeError:
			pass
			
		num = self.num
		self._entriesLast = tuple(Entry(num, lap, it[0], it[1]) for lap, it in enumerate(iTimes))
		self._iTimesLast = iTimes
		return self._entriesLast
			
	def interpolate( self, stopTime = maxInterpolateTime ):
		if not self.times or self.status in (Rider.DNS, Rider.DQ):
			return self.getEntries( [] )
		
		# Adjust the stop time.
		st = stopTime
		dnfPulledTime = None
		if self.status in (Rider.DNF, Rider.Pulled):
			# If no given time, use the last recorded time for DNF and Pulled riders.
			dnfPulledTime = self.tStatus if self.tStatus is not None else self.times[-1]
			st = min(st, dnfPulledTime + 0.01)
		
		# Check if we need to do any interpolation or if the user wants the raw data.
		if not self.autocorrectLaps:
			if not self.times:
				return self.getEntries( [] )
			# Add the start time for the beginning of the rider.
			# This avoids a whole lot of special cases later.
			iTimes = [race.getStartOffset(self.num) if race else 0.0]
			iTimes[1:] = self.times
			iTimes = self.removeEarlyTimes( iTimes )
			iTimes = [(t, False) for t in iTimes]
			if dnfPulledTime is not None:
				iTimes = self.removeLateTimes( iTimes, dnfPulledTime )
			return self.getEntries( iTimes )

		iTimes = self.getCleanLapTimes()
		
		if not iTimes:
			return self.getEntries( [] )

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
		if dnfPulledTime is not None:
			iTimes = self.removeLateTimes( iTimes, dnfPulledTime )
		
		if len(iTimes) <= 1:
			iTimes = []
		return self.getEntries( iTimes )
		
	def hasInterpolatedTime( self, tMax ):
		interpolate = self.interpolate()
		try:
			return any( e.interp for e in interpolate if e.t <= tMax )
		except (ValueError, StopIteration):
			return False
			
	def hasTimes( self ):
		return self.times
		
	def getLapTimesForMedian( self ):
		# Create a separate working list.
		startOffset = race.getStartOffset(self.num) if race else 0.0
		iTimes = [t for t in self.times if t > startOffset]
		if not iTimes:
			return []
		lenITimes = len(iTimes)
		if lenITimes == 1:
			# Use 1st lap time if we only have one lap.
			return [iTimes[0] - startOffset]
		
		# Otherwise, ignore the first lap time.
		try:
			numLaps = min( race.getCategory(self.num)._numLaps or 999999, len(iTimes) )
		except Exception as e:
			numLaps = len(iTimes)
		if lenITimes > numLaps:
			iTimes = iTimes[:numLaps]
		return [b-a for b, a in zip(iTimes[1:], iTimes)]
		
	def getEarlyStartOffset( self ):
		if (not race or
			race.isTimeTrial or
			self.firstTime is None or
			not (race.enableJChipIntegration and race.resetStartClockOnFirstTag)
		):
			return None
		
		# If the rider is already in the first start wave then it is impossible to be in an earlier one.
		startOffset = race.getStartOffset( self.num )
		if not startOffset:
			return None
		
		StartGapBefore = 2.0
		
		# Check if the first read is at or after the rider's offset.  If so, this start is good.
		if (startOffset - StartGapBefore) <= self.firstTime:
			return None

		# Try to find an earlier wave that the rider started in.
		startOffsets = race.getStartOffsets()
		for startOffsetCur, startOffsetNext in zip(startOffsets, startOffsets[1:]):
			if startOffsetCur >= startOffset:
				break
			if (startOffsetCur - StartGapBefore) <= self.firstTime < startOffsetNext:
				return startOffsetCur
			
		return None

class NumTimeInfo(object):

	Original	= 0
	Add			= 1
	Edit		= 2
	Delete		= 3
	Swap		= 4
	Split		= 5
	MaxReason	= 6
	
	ReasonName = {
		Original:	_('Original'),
		Add:		_('Add'),
		Edit:		_('Edit'),
		Delete:		_('Delete'),
		Swap:		_('Swap'),
		Split:		_('Split'),
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
			return u''
		infoStr = u'{}, {}\n    {}: {}\n    {}: {}\n'.format(
			Utils.formatTime(t, True), NumTimeInfo.ReasonName[info[0]],
			_('by'), info[1],
			_('on'), info[2].ctime()
		)
		return infoStr
	
	def getNumInfo( self, num ):
		return self.info.get( num, {} )
		
class Race( object ):
	finisherStatusList = [Rider.Finisher, Rider.Pulled]
	finisherStatusSet = set( finisherStatusList )
	
	nonFinisherStatusList = [Rider.DNF, Rider.DNS, Rider.DQ, Rider.NP, Rider.OTL]
	nonFinisherStatusSet = set( nonFinisherStatusList )
	
	UnitKm = 0
	UnitMiles = 1
	
	distanceUnit = UnitKm
	
	rule80MinLapCount = 2	# Minimum number of laps to compute rule80.
	
	automaticManual = 0
	
	isChangedFlag = False
	isTimeTrial = False
	roadRaceFinishTimes = False
	
	enableJChipIntegration = False
	resetStartClockOnFirstTag = False
	firstRecordedTime = None
	skipFirstTagRead = False
	
	chipReaderType = 0
	chipReaderPort = 3601
	chipReaderIpAddr = '127.0.0.1'
	
	autocorrectLapsDefault = True
	
	allCategoriesHaveRaceLapsDefined = False
	allCategoriesFinishAfterFastestRidersLastLap = True
	
	enableUSBCamera = False
	photosAtRaceEndOnly = False
	cameraDevice = 0
	advancePhotoMilliseconds = 0
	finishKMH = 50.0
	photoCount = 0
	
	highPrecisionTimes = False
	syncCategories = True
	
	unmatchedTags = None
	
	ftpUploadDuringRace = False
	ftpUploadPhotos = False
	
	geoTrackFName = None
	geoTrack = None
	
	groupByStartWave = True
	winAndOut = False
	isTimeTrial = False
	minPossibleLapTime = 0.0
	
	city = ''
	stateProv = ''
	country = ''
	timezone = ''
	discipline = 'Cyclo-cross'
	
	showCourseAnimationInHtml = True
	licenseLinkTemplate = u''			# Used to create an html link from the rider's license number in the html output.
	hideDetails = True
	
	lapCounterForegrounds = []
	lapCounterBackgrounds = []
	secondsBeforeLeaderToFlipLapCounter = 15.0
	countdownTimer = False
	lapCounterCycle = None
	
	setNoDataDNS = False				# If True, will set all riders in the spreadsheet to DNS if they have no data in the race.
	lastChangedTime = sys.float_info.max
	
	headerImage = None
	email = None
	postPublishCmd = ''
	longName = ''
	
	def __init__( self ):
		self.reset()

	def reset( self ):
		self.name = 'MyEventName'
		self.organizer = 'MyOrganizer'
		
		self.city = 'MyCity'
		self.stateProv = 'MyStateProv'
		self.country = 'MyCountry'
		
		self.raceNum = 1
		self.date = datetime.date.today().strftime('%Y-%m-%d')
		self.scheduledStart = '10:00'
		self.minutes = 60
		self.commissaire = 'MyCommissaire'
		self.memo = u''
		self.discipline = 'Cyclo-cross'

		self.categories = {}
		self.riders = {}
		self.startTime = None
		self.finishTime = None
		self.numLaps = None
		self.firstRecordedTime = None	# Used to trigger the race on the first recorded time.
		
		self.allCategoriesFinishAfterFastestRidersLastLap = True
		
		self.autocorrectLapsDefault = True
		self.highPrecisionTimes = False
		self.syncCategories = True
		self.modelCategory = 0
		self.distanceUnit = Race.UnitKm
		self.missingTags = set()
		
		self.enableUSBCamera = False
		self.enableJChipIntegration = False
		self.photoCount = 0
		
		self.hideDetails = True
		self.photosAtRaceEndOnly = False
		
		# Animation options.
		self.finishTop = False
		self.reverseDirection = False
		
		self.isChangedFlag = True
		
		self.allCategoriesHaveRaceLapsDefined = False
		
		self.numTimeInfoField = NumTimeInfo()
		
		self.tagNums = None
		self.lastOpened = datetime.datetime.now()
		memoize.clear()
	
	
	def getFileName( self ):
		rDate = self.date
		rName = Utils.RemoveDisallowedFilenameChars( self.name )
		rNum = self.raceNum
		fname = u'{}-{}-r{}-.cmn'.format(rDate, rName, rNum)
		return fname
	
	@property
	def title( self ):
		return self.longName or self.name
	
	def getTemplateValues( self ):
		excelLink = getattr(self, 'excelLink', None)
		if excelLink:
			excelLinkStr = u'{}|{}'.format( os.path.basename(excelLink.fileName or u''), excelLink.sheetName or u'')
		else:
			excelLinkStr = u''
		
		path = Utils.getFileName() or ''
		return {
			u'EventName':	self.name,
			u'EventTitle':	self.title,
			u'RaceNum':		unicode(self.raceNum),
			u'City':		self.city,
			u'StateProv':	self.stateProv,
			u'Country':		self.country,
			u'Commissaire':	self.commissaire,
			u'Organizer':	self.organizer,
			u'Memo':		self.memo,
			u'Discipline':	self.discipline,
			u'RaceType':	_('Time Trial') if self.isTimeTrial else _('Mass Start'),
			u'RaceDate':	self.date,
			u'MinPossibleLapTime':self.minPossibleLapTime,
			u'InputMethod':	_('RFID') if self.enableJChipIntegration else _('Manual'),
			u'StartTime':	self.startTime.strftime('%H:%M:%S.%f')[:-3] if self.startTime else unicode(self.scheduledStart),
			u'StartMethod':	_('Automatic: Triggered by first tag read') if self.enableJChipIntegration and self.resetStartClockOnFirstTag else _('Manual'),
			u'CameraStatus': _('USB Camera Enabled') if self.enableUSBCamera else _('USB Camera Not Enabled'),
			u'PhotoCount':	unicode(self.photoCount),
			u'ExcelLink':	excelLinkStr,
			u'GPXFile':		os.path.basename(self.geoTrackFName or ''),

			u'Path':		path,
			u'DirName':		os.path.dirname(path),
			u'FileName':	os.path.basename(path),
		}
	
	def getBibTimes( self ):
		bibTimes = []
		for bib, rider in self.riders.iteritems():
			for t in rider.times:
				bibTimes.append( (bib, t) )
		bibTimes.sort( key=operator.itemgetter(1, 0) )
		return bibTimes

	@property
	def numTimeInfo( self ):
		try:
			return self.numTimeInfoField
		except AttributeError:
			self.numTimeInfoField = NumTimeInfo()
			return self.numTimeInfoField
	
	@property
	def distanceUnitStr( self ):
		return 'km' if self.distanceUnit == Race.UnitKm else 'miles'
		
	@property
	def speedUnitStr( self ):
		return 'km/h' if self.distanceUnit == Race.UnitKm else 'mph'
	
	def resetCache( self ):
		memoize.clear()
	
	def hasRiders( self ):
		return len(self.riders) > 0

	def isChanged( self ):
		return self.isChangedFlag

	def setChanged( self, changed = True ):
		self.isChangedFlag = changed
		if changed:
			memoize.clear()
			self.lastChangedTime = time.time()
			
	def raceTimeToClockTime( self, t=None ):
		if self.startTime is None:
			return None
		t = self.lastRaceTime() if t is None else t
		return t + self.startTime.hour*60.0*60.0 + self.startTime.minute*60.0 + self.startTime.second + self.startTime.microsecond/1000000.0
		
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
			return self.riders[num]
		except KeyError:
			pass
		
		try:
			num = int(num, 10)
		except:
			num = int(num)
		
		try:
			return self.riders[num]
		except KeyError:
			rider = Rider( num )
			rider.autocorrectLaps = self.autocorrectLapsDefault
			self.riders[num] = rider
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
		return (datetime.datetime.now() - self.startTime).total_seconds()

	def lastRaceTime( self ):
		if self.finishTime is not None:
			return (self.finishTime - self.startTime).total_seconds()
		return self.curRaceTime()

	def addTime( self, num, t = None, doSetChanged = True ):
		if t is None:
			t = self.curRaceTime()
		
		if self.isTimeTrial:
			r = self.getRider(num)
			if r.firstTime is None:
				r.firstTime = t
			else:
				r.addTime( t - r.firstTime )
		else:
			if self.enableJChipIntegration:
				if self.resetStartClockOnFirstTag:
					if not self.firstRecordedTime:
						self.firstRecordedTime = self.startTime + datetime.timedelta( seconds = t )
						self.startTime = self.firstRecordedTime
						t = 0.0
					r = self.getRider(num)
					if r.firstTime is None:
						r.firstTime = t
					else:
						r.addTime( t )
						
				elif self.skipFirstTagRead:
					if not self.firstRecordedTime:
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
		
		if doSetChanged:
			self.setChanged()
		return t

	def importTime( self, num, t ):
		self.getRider(num).addTime( t )
		
	def deleteRiderTimes( self, num ):
		try:
			rider = self.riders[num]
		except KeyError:
			pass
		rider.times = []
		rider.firstTime = None
		rider.clearCache()
			
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
		except KeyError:
			return
		self.resetAllCaches()
		self.setChanged()
			
	def deleteAllRiders( self ):
		self.riders = {}
		self.resetAllCaches()
		self.setChanged()
			
	def renumberRider( self, num, newNum ):
		try:
			rider = self.riders[num]
		except KeyError:
			return False
		if newNum in self.riders:
			return False
			
		rider.clearCache()
		del self.riders[rider.num]
		rider.num = newNum
		self.riders[rider.num] = rider
		
		self.resetAllCaches()
		self.setChanged()
		return True
			
	def swapRiders( self, na, nb ):
		try:
			a = self.riders[na]
			b = self.riders[nb]
		except KeyError:
			return False
		
		a.swap( b )
		self.resetAllCaches()
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
		
		self.resetAllCaches()
		self.setChanged()
		return True
	
	def deleteTime( self, num, t ):
		if not num in self.riders:
			return
		rider = self.riders[num]
		rider.deleteTime( t )
		self.setChanged()
		
	def hasRiderTimes( self ):
		return any( r.hasTimes() for r in self.riders.itervalues() )

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
	def getMedianLapTime( self, category=None ):
		lapTimes = sorted( itertools.chain.from_iterable( r.getLapTimesForMedian()
			for r in self.riders.itervalues() if race.inCategory(r.num, category) ) )
		if not lapTimes:
			return 8.0 * 60.0	# Default to 8 minutes.
		lapTimesLen = len(lapTimes)
		return	lapTimes[lapTimesLen//2] if lapTimesLen & 1 else (
				lapTimes[lapTimesLen//2-1] + lapTimes[lapTimesLen//2]) / 2.0

	@memoize
	def interpolate( self ):
		return sorted(
			itertools.chain.from_iterable( rider.interpolate() for rider in self.riders.itervalues() ),
			key=Entry.key
		)

	@memoize
	def interpolateCategory( self, category ):
		if category is None:
			return self.interpolate()
		inCategory = self.inCategory
		return [e for e in self.interpolate() if inCategory(e.num, category)]

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
				catNumLaps = self.getNumLapsFromCategory(self.getCategory(r))
				riderNumLapsMax[r] = catNumLaps if catNumLaps else 999999
			except AttributeError:
				riderNumLapsMax[r] = 999999
		
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
		if not entries:
			return None

		inCategory = self.inCategory
		rule80MinLapCount = self.rule80MinLapCount
		
		iFirst = iSecond = None
		
		try:
			iFirst = (i for i, e in enumerate(entries) if inCategory(e.num, category) and e.lap == 1).next()
		except StopIteration:
			return None
		
		if self.rule80MinLapCount > 1:
			try:
				iSecond = (i for i in xrange(iFirst+1, len(entries)) if inCategory(entries[i].num, category) and entries[i].lap == 2).next()
			except StopIteration:
				return None
		
		tFirst = entries[iFirst].t
		if category:
			tFirst -= category.getStartOffsetSecs()
		
		# Try to figure out if we should use the first lap or the second.
		# The first lap may not be the same length as the second.
		if iSecond is not None:
			tSecond = entries[iSecond].t - entries[iFirst].t
			tDifference = abs(tFirst - tSecond)
			tAverage = (tFirst + tSecond) / 2.0
			# If there is more than 5% difference, use the second lap (assume a run-up on the first lap).
			if tDifference / tAverage > 0.05:
				t = tSecond
			else:
				t = max(tFirst, tSecond)	# Else, use the maximum of the two (aren't we nice!).
		else:
			t = tFirst
		
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
		try:
			return max( e.lap for e in self.interpolate() if not e.interp and self.inCategory(e.num, category) )
		except ValueError:
			return 0

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
	def getLeaderTimesNums( self, category=None ):
		entries = self.interpolate()
		if not entries:
			return None, None
			
		leaderTimes = [ category.getStartOffsetSecs() if category else 0.0 ]
		leaderNums = [ None ]
		leaderTimesLen = 1
		for e in entries:
			if category and self.getCategory(e.num) != category:
				continue
			if e.lap == leaderTimesLen:
				leaderTimes.append( e.t )
				leaderNums.append( e.num )
				leaderTimesLen += 1
		
		try:
			if leaderTimesLen > 1 and self.allCategoriesHaveRaceLapsDefined:
				maxRaceLaps = max( self.getNumLapsFromCategory(category) for category in self.categories.itervalues() if category.active )
				leaderTimes = leaderTimes[:maxRaceLaps + 1]
				leaderNums = leaderNums[:maxRaceLaps + 1]
		except:
			return None, None
		
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
		# Return times and nums for the leaders of each category.
		ctn = defaultdict( lambda: ([0.0], [None]) )
		
		getCategory = self.getCategory

		catLapCur = defaultdict( lambda: 1 )
		for e in self.interpolate():
			category = getCategory(e.num)
			if e.lap == catLapCur[category]:
				v = ctn[category]
				v[0].append( e.t )
				v[1].append( e.num )
				catLapCur[category] += 1

		ctn.pop( None, None )	# Remove unmatched categories.
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

	def getCategories( self, startWaveOnly=True, publishOnly=False, uploadOnly=False, excludeCustom=False, excludeCombined=False ):
		if startWaveOnly:
			CatWave = Category.CatWave
			activeCategories = [c for c in self.categories.itervalues() if c.active and c.catType == CatWave]
		else:
			activeCategories = [c for c in self.categories.itervalues() if c.active]
		
		if publishOnly:
			activeCategories = [c for c in activeCategories if c.publishFlag]
			
		if uploadOnly:
			activeCategories = [c for c in activeCategories if c.uploadFlag]
			
		if excludeCustom:
			CatCustom = Category.CatCustom
			activeCategories = [c for c in activeCategories if c.catType != CatCustom]
			
		activeCategories.sort( key = Category.key )
		
		if excludeCombined:
			# If this is a combined category, then the following non-custom category will be a component.
			toExclude = set()
			for i, c in enumerate(activeCategories):
				if c.catType == Category.CatWave:
					for j in xrange(i+1, len(activeCategories)):
						if activeCategories[j].catType == Category.CatCustom:
							continue
						if activeCategories[j].catType == Category.CatComponent:
							toExclude.add( c )
						break
			activeCategories = [c for c in activeCategories if c not in toExclude]
		
		return activeCategories
	
	def getComponentCategories( self, category ):
		if category.catType != Category.CatWave:
			return []
		
		categories = self.getCategories( excludeCustom=True, startWaveOnly=False )
		CatComponent = Category.CatComponent
		components = []
		for i in xrange(len(categories)):
			if categories[i] == category:
				for j in xrange(i+1, len(categories)):
					if categories[j].catType == CatComponent:
						components.append( categories[j] )
				return components
		return []
	
	def getStartOffsets( self ):
		return sorted( set(c.getStartOffsetSecs() for c in self.getCategories(startWaveOnly=True)) )
		
	def categoryStartOffset( self, category ):
		# Get the start offset of the controlling Start Wave.
		if category:
			if category.catType == Category.CatWave:
				return category.getStartOffsetSecs()
			elif category.catType == Category.CatComponent:
				CatWave = Category.CatWave
				lastWave = None
				for c in self.getCategories( startWaveOnly=False ):
					if c.catType == CatWave:
						lastWave = c
					elif c == category:
						return lastWave.getStartOffsetSecs() if lastWave else 0.0
		return 0.0

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
		return sorted( self.categories.itervalues(), key=Category.key )

	def setActiveCategories( self, active = None ):
		for i, c in enumerate(self.getAllCategories()):
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
		if not self.hasCategoryCache():
			self._buildCategoryCache()
		
		categories = [c for c in self.categories.itervalues() if c.active and c.catType != Category.CatCustom and c.sequence > category.sequence]
		categories.sort( key = operator.attrgetter('sequence') )
		
		unionNums = set()
		for c in categories:
			if c.catType == Category.CatWave:
				break
			unionNums |= c.getMatchSet()
		
		if unionNums:
			category.setFromSet( unionNums )
		
	def adjustAllCategoryWaveNumbers( self ):
		categories = [c for c in self.categories.itervalues() if c.active and c.catType == Category.CatWave]
		for c in categories:
			self.adjustCategoryWaveNumbers( c )

		'''
		category_sets = [c.getMatchSet() for c in categories]		
		for c, i in zip(categories, minimal_intervals.minimal_intervals(category_sets) ):
			c.setFromSet( IntervalsToSet(i) )
		'''
		
		self.resetCategoryCache()
	
	def mergeExistingCategoryAttributes( self, nameStrTuples ):
		for cNew in nameStrTuples:
			try:
				key = Category.getFullName(cNew.get('name', ''), cNew.get('gender','Open'))
				cExisting = self.categories[key]
			except KeyError:
				continue
				
			for a in Category.MergeAttributes:
				vNew = cNew.get( a, None )
				vExisting = getattr( cExisting, a )
				if vNew is None and vExisting is not None:
					cNew[a] = vExisting
		
		return nameStrTuples

	def setCategories( self, nameStrTuples ):
		try:
			distance = self.geoTrack.lengthKm if self.distanceUnit == self.UnitKm else self.geoTrack.lengthMiles
		except  AttributeError:
			distance = None
			
		try:
			firstLapDistance = (
				self.geoTrack.firstLapDistance / 1000.0 if self.distanceUnit == self.UnitKm else self.geoTrack.firstLapDistance / 1609.344
			)
		except  AttributeError:
			firstLapDistance = None
		
		# Ensure that all categories were not set to inactive by mistake.
		allInactive = True
		for t in nameStrTuples:
			args = dict( t )
			if not 'name' in args or not args['name']:
				continue
			if unicode(args.get('active', True)).strip().upper() in u'1YT':
				allInactive = False
				break
		
		i = 0
		newCategories = {}
		waveCategory = None
		for t in nameStrTuples:
			args = dict( t )
			if not 'name' in args or not args['name']:
				continue
			args['sequence'] = i
			if allInactive:
				args['active'] = True
			category = Category( **args )
			
			if category.active:
				if category.catType == Category.CatWave:
					# Record this category if it is a CatWave.  It controls the following component categories.
					waveCategory = category
				elif waveCategory is None:
					# Else, there is a component or custom category without a start wave.
					# Make it a start wave so that the results don't mess up.
					category.catType = Category.CatWave
			
			if category.fullname not in self.categories:
				if category.distance is None:
					category.distance = distance
				if category.firstLapDistance is None:
					category.firstLapDistance = firstLapDistance
			
			# Ensure we don't have any duplicate category fullnames.
			if category.fullname in newCategories:
				originalName = category.name
				for count in xrange(1, 999):
					category.name = u'{} {}({})'.format(originalName, _('Copy'), count)
					if not category.fullname in newCategories:
						break
			newCategories[category.fullname] = category
			i += 1
		
		if self.categories != newCategories:
			# Copy the new values into the existing categories.
			# This minimizes the impact if the calling code is in a category loop.
			for cNewName, cNew in newCategories.iteritems():
				try:
					self.categories[cNewName].copy( cNew )
				except KeyError:
					self.categories[cNewName] = cNew
			
			self.categories = { cName:cValue for cName, cValue in self.categories.iteritems() if cName in newCategories }
			self.setChanged()
			
			changed = True
		else:
			changed = False
			
		self.resetCategoryCache()
		
		if self.categories:
			self.allCategoriesHaveRaceLapsDefined = True
			self.categoryLapsMax = 0
			for category in self.categories.itervalues():
				if not category.active:
					continue
				if self.getNumLapsFromCategory(category):
					self.categoryLapsMax = max( self.categoryLapsMax, self.getNumLapsFromCategory(category) )
				else:
					self.allCategoriesHaveRaceLapsDefined = False
		else:
			self.allCategoriesHaveRaceLapsDefined = False
				
		if self.allCategoriesHaveRaceLapsDefined:
			self.numLaps = self.categoryLapsMax
			
		self.setCategoryMask()
		
		return changed
		
	def normalizeCategories( self ):
		for c in self.getCategories( startWaveOnly = False ):
			c.normalize()

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
			catType = { 'Wave':0, 'Component':1, 'Custom':2 }.get( fields[3], 0 )
			categories.append( {'name':fields[0], 'catStr':fields[1], 'gender':fields[2], 'catType':catType} )
		self.setCategories( self.mergeExistingCategoryAttributes(categories) )

	def catCount( self, category ):
		return sum( 1 for num in self.riders.iterkeys() if self.inCategory(num, category) )

	def getNumsForCategory( self, category ):
		try:
			return category.bibSet
		except (TypeError, AttributeError, KeyError):
			self._buildCategoryCache()
		try:
			return category.bibSet
		except (TypeError, AttributeError, KeyError):
			return set()

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
		if hasattr(self, 'categoryNumsCache'):
			delattr( self, 'categoryNumsCache' )
		
		# Reset the cache for all categories by sequence number.
		self.categoryCache = {}			# Returns wave category by num.
		self.startOffsetCache = {}		# Returns start offset by num.
		
		# Handle wave categories only.
		numsSeen = set()
		for c in self.getCategories( startWaveOnly=True ):
			c.bibSet = c.getMatchSet() - numsSeen
			numsSeen |= c.bibSet
			offsetSecs = c.getStartOffsetSecs()
			for n in c.bibSet:
				self.startOffsetCache[n] = offsetSecs
				self.categoryCache[n] = c

		# Now handle all categories.
		# Bib exclusivity is enforced for component categories based on their wave.
		# Custom categories have no exclusivity rules.		
		waveCategory = None
		waveNumsSeen = set()
		for c in self.getCategories( startWaveOnly=False ):
			if c.catType == Category.CatWave:
				waveCategory = c
				waveNumsSeen = set()
			elif c.catType == Category.CatComponent:
				c.bibSet = c.getMatchSet() - waveNumsSeen
				if waveCategory:
					c.bibSet &= waveCategory.bibSet
				waveNumsSeen |= c.bibSet
			else:	# c.catType == Category.CatCustom
				c.bibSet = c.getMatchSet()

	def hasCategoryCache( self ):
		return getattr(self, 'categoryCache', None) is not None

	def getCategory( self, num ):
		''' Get the start wave category for this rider. '''
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
		if getattr(self, 'categoryCache', None) is None:
			self._buildCategoryCache()		
		return num in category.bibSet
		
	def getStartOffset( self, num ):
		try:
			return self.startOffsetCache[num]
		except KeyError:
			return 0.0
		except (TypeError, AttributeError) as e:
			pass
			
		self._buildCategoryCache()	
		return self.startOffsetCache.get(num, 0.0)
		
	def getEarlyStartOffset( self, num ):
		try:
			return self.riders[num].getEarlyStartOffset()
		except KeyError:
			return None
	
	@memoize
	def getCategoriesInUse( self ):
		catSet = set()
		for num in self.riders.iterkeys():
			category = self.getCategory( num )
			if category:
				catSet.add( category )
		return sorted( catSet, key = Category.key )
	
	def getCategoryMaxLapInUse( self ):
		maxLaps = 0
		for category in self.getCategoriesInUse():
			categoryLaps = self.getNumLapsFromCategory(category)
			if not categoryLaps:
				return None
			maxLaps = max( maxLaps, categoryLaps )
		return maxLaps
	
	@memoize
	def getNumLapsFromCategory( self, category ):
		return category.getNumLaps() if category else None
	
	def getCategoryNumLaps( self, num ):
		try:
			category = self.getCategory( num )
			return self.getNumLapsFromCategory(category) or 1000
		except AttributeError:
			return 1000
			
	def setDistanceForCategories( self, distanceKm ):
		if distanceKm is not None and distanceKm > 0.0:
			distance = distanceKm if self.distanceUnit == self.UnitKm else distanceKm*0.621371
		else:
			distance = None
		for c in self.categories.itervalues():
			c.distance = distance
	
	def resetCategoryCache( self ):
		self.categoryCache = None
		self.startOffsetCache = None
		
	def resetAllCaches( self ):
		self.resetCategoryCache()
		self.resetCache();
		
	def resetRiderCaches( self ):
		for rider in self.riders.itervalues():
			rider.clearCache()
	
	def getRaceIntro( self ):
		intro = [
			u'{}:{}'.format(self.name, self.raceNum),
			u'{}: {} ({})'.format(_('Start'), self.scheduledStart, self.date),
			_('Time Trial') if self.isTimeTrial else _('Mass Start'),
		]
		activeCategories = [c for c in self.categories.itervalues() if c.active]
		if all( c.numLaps for c in activeCategories ):
			activeCategories.sort( key = Category.key )
			intro.append( u'{}: {}'.format(_('Category Laps'), ', '.join( '{}'.format(c.numLaps) for c in activeCategories )) )
		else:
			intro.append( u'{}: {} min'.format(_('Duration'), self.minutes) )
		return u'\n'.join( intro )
	
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
		riders = self.riders
		for e in self.interpolate():
			if riders[e.num].status in finisherStatusSet:
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
						ret[r][e.num] = u'{} {}'.format(lapsDown, _('laps') if lapsDown < -1 else _('lap'))
				iLap += 1
					
		return ret
		
	#----------------------------------------------------------------------------------------
	
	@memoize
	def getCategoryBestLaps( self, category = None ):
		if category:
			# Check if the number of laps is specified.  If so, use that.
			# Otherwise, check if we can figure out the number of laps.
			lap = (self.getNumLapsFromCategory(category) or self.getCategoryRaceLaps().get(category, None))
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
		
		for c in self.categories.itervalues():
			if c != category:
				c.removeNum( num )
				c.normalize()
				
		category.addNum( num )
		category.normalize()
		
		self.adjustAllCategoryWaveNumbers()
		
		self.resetCategoryCache()
		self.setChanged()
		self.setCategoryMask()
		
	@memoize
	def isCategoryEmpty( self, category ):
		inCategory = self.inCategory
		return not (category.active and any(inCategory(num, category) for num in self.riders.iterkeys()) )
	
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
	
	def addUnmatchedTag( self, tag, t ):
		try:
			if len(self.unmatchedTags[tag]) < 200:
				self.unmatchedTags[tag].append( t )
		except KeyError:
			self.unmatchedTags[tag] = [t]
		except TypeError:
			self.unmatchedTags = {tag: [t]}
		
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
		
setDefaultRaceAttr( Race )

def highPrecisionTimes():
	try:
		return race.highPrecisionTimes
	except AttributeError:
		return False

def setCategoryChoice( iSelection, categoryAttribute = None ):
	try:
		setCategoryChoice = race.setCategoryChoice
	except AttributeError:
		return
	setCategoryChoice( iSelection, categoryAttribute )

def getCurrentHtml():
	if not race:
		return None
	htmlFile = os.path.join(Utils.getHtmlFolder(), 'RaceAnimation.html')
	try:
		with io.open(htmlFile, 'r', encoding='utf-8') as fp:
			html = fp.read()
		return Utils.mainWin.addResultsToHtmlStr( html )
	except Exception as e:
		Utils.logException( e, sys.exc_info() )
		return None

def getCurrentTTCountdownHtml():
	if not race or not race.isTimeTrial:
		return None
	htmlFile = os.path.join(Utils.getHtmlFolder(), 'TTCountdown.html')
	try:
		with io.open(htmlFile, 'r', encoding='utf-8') as fp:
			html = fp.read()
		return Utils.mainWin.addTTStartToHtmlStr( html )
	except Exception as e:
		Utils.logException( e, sys.exc_info() )
		return None

def getCurrentTTStartListHtml():
	if not race or not race.isTimeTrial:
		return None
	htmlFile = os.path.join(Utils.getHtmlFolder(), 'TTStartList.html')
	try:
		with io.open(htmlFile, 'r', encoding='utf-8') as fp:
			html = fp.read()
		return Utils.mainWin.addTTStartToHtmlStr( html )
	except Exception as e:
		Utils.logException( e, sys.exc_info() )
		return None

def writeModelUpdate( includeExcel=True, includePDF=True ):
	success = True
	
	'''
	# Make sure the html, TTstart, Excel and pdf files are up-to-date on exit.

	html = getCurrentHtml()
	if not html:
		success = False
	else:
		fname = os.path.splitext(Utils.getFileName())[0] + '.html'
		try:
			with io.open(fname, 'w', encoding='utf-8') as fp:
				fp.write( html )
		except Exception as e:
			success = False

	html = getCurrentTTStartHtml()
	if html:
		fname = os.path.splitext(Utils.getFileName())[0] + '_TTCountdown.html'
		try:
			with io.open(fname, 'w', encoding='utf-8') as fp:
				fp.write( html )
		except Exception as e:
			success = False
	
	mainWin = Utils.getMainWin()
	if not mainWin:
		return success
	
	if includeExcel:
		try:
			mainWin.menuPublishAsExcel( silent=True )
		except Exception as e:
			Utils.logException( e, sys.exc_info() )
			success = False

	if includePDF:
		try:
			mainWin.menuPrintPDF( silent=True )
		except Exception as e:
			Utils.logException( e, sys.exc_info() )
			success = False
	'''
	
	return success
		
if __name__ == '__main__':
	'''
	s = set.union( set(xrange(10)), set(xrange(20,30)) )
	i = SetToIntervals( s )
	ss = IntervalsToSet( i )
	print( s )
	print( i )
	print( ss )
	sys.exit()
	'''
	
	r = newRace()
	
	'''
	for i in xrange(1, 11):
		r.addTime( 10, i*100 )
	r.addTime( 10, 10*100 + 1 )
	print( u'\n'.join( unicode(f) for f in r.interpolate()[:20] ) )
	'''
	
	categories = [
		{'name':'Junior', 'catStr':'1-99', 'startOffset':'00:00', 'distance':0.5, 'gender':'Men', 'raceLaps':10},
	]
	r.setCategories( categories )

	#for i in xrange(1,8):
	#	r.addTime( 10, i * 60 )
	r.addTime( 10, 2 * 60 )
	r.addTime( 10, 3 * 60 )
	r.addTime( 10, 4 * 60 )
	r.addTime( 10, 5 * 60 )
	r.addTime( 10, 6 * 60 )
	r.addTime( 10, 8 * 60 )
	r.addTime( 10, 10*60+1 )
	rider = r.getRider( 10 )
	
	entries = rider.interpolate( 11 * 60 )
	
	print( [(Utils.SecondsToMMSS(e.t), e.interp) for e in entries] )
	sys.exit( 0 )
	
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

