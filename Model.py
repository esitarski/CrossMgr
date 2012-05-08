from __future__ import print_function
import random
import itertools
import datetime
import Utils
import re
import csv
import bisect
import math
import copy
import operator
import sys
import functools
import thread
from os.path import commonprefix

maxInterpolateTime = 2.0*60.0*60.0	# 2 hours.

lock = thread.allocate_lock()

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
		self.func = func
		
	def __call__(self, *args):
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
	memoize.clear()
	race = r

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
class Category(object):

	badRangeCharsRE = re.compile( '[^0-9,\-]' )

	def _getStr( self ):
		s = [str(i[0]) if i[0] == i[1] else '%d-%d' % i for i in self.intervals]
		s.extend( str(-e) for e in sorted(list(self.exclude)) )
		return ','.join( s )

	def _setStr( self, s ):
		s = Category.badRangeCharsRE.sub( '', str(s) )
		self.intervals = []
		self.exclude = set()
		fields = s.split(',')
		for f in fields:
			if not f:
				continue
			try:
				bounds = f.split( '-' )
				if not bounds:
					continue

				# Negative numbers are exceptions to remove from the ranges.
				if not bounds[0]:
					if len(bounds) > 1:
						self.exclude.add( int(bounds[1]) )
					continue

				bounds = [int(b) for b in bounds if b is not None and b != '']
				if not bounds:
					continue

				if len(bounds) > 2:			# Ignore numbers that are not in proper x-y format.
					del bounds[2:]
				elif len(bounds) == 1:
					bounds.append( bounds[0] )
				if bounds[0] > bounds[1]:
					bounds[0], bounds[1] = bounds[1], bounds[0]
				self.intervals.append( tuple(bounds) )
			except:
				# Ignore any parsing errors.
				pass
				
		self.intervals.sort()

	catStr = property(_getStr, _setStr)

	def getMask( self ):
		''' Return the common number prefix for all intervals (None if non-existent). '''
		mask = None
		for i in self.intervals:
			for k in i:
				num = str(k)
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

	def __init__( self, active, name, catStr = '', startOffset = '00:00', numLaps = None, sequence = 0 ):
		self.active = False
		active = str(active).strip()
		if active and active[0] in 'TtYy1':
			self.active = True
		self.name = name
		self.catStr = catStr
		self.startOffset = startOffset
		try:
			self._numLaps = int(numLaps)
		except (ValueError, TypeError):
			self._numLaps = None
		try:
			self.sequence = int(sequence)
		except (ValueError, TypeError):
			self.sequence = 0
		
	def __setstate( self, d ):
		self.__dict__.update(d)
		i = getattr( self, 'intervals', None )
		if i:
			i.sort()
		
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
		if i > 0:
			i -= 1
		for j in xrange(i, min(i+2,len(self.intervals)) ):
			if self.intervals[j][0] <= num <= self.intervals[j][1]:
				return True
		return False

	def __cmp__( self, c ):
		for attr in ['sequence', 'name', 'active', 'startOffset', '_numLaps', 'catStr']:
			cCmp = cmp( getattr(self, attr, None), getattr(c, attr, None) )
			if cCmp != 0:
				return cCmp 
		return 0
		
	def removeNum( self, num ):
		if not self.matches(num, True):
			return
		for j in xrange(len(self.intervals)-1, -1, -1):
			if self.intervals[j][0] <= num <= self.intervals[j][1]:
				if self.intervals[j][0] == num:
					self.intervals.pop( j )
					return
		self.exclude.add( num )
		
	def addNum( self, num ):
		self.exclude.discard( num )
		if self.matches(num, True):
			return
		self.intervals.append( (num, num) )
		self.intervals.sort()

	def __repr__( self ):
		return 'Category(active=%s, name="%s", catStr="%s", startOffset="%s", numLaps=%s, sequence=%s)' % (
				str(self.active),
				self.name,
				self.catStr,
				self.startOffset,
				str(self.numLaps),
				str(self.sequence) )

	def getStartOffsetSecs( self ):
		return Utils.StrToSeconds( self.startOffset )

#------------------------------------------------------------------------------------------------------------------

class Entry(object):
	# Store entries as tuples in sort sequence to improve performance.

	__slots__ = ('data')							# Suppress the default dictionary to save space.

	def __init__( self, num, lap, t, interp ):
		self.data = (t, -lap, num, interp)			# -lap sorts most laps covered to the front.

	def __cmp__( self, e ):
		return cmp( self.data, e.data )

	def set( self, e ):
		self.data = copy.copy(e.data)
		
	def __hash__( self ):
		return hash(self.data)

	@property
	def t(self):		return self.data[0]
	@property
	def lap(self):		return -self.data[1]
	@property
	def lapNeg(self):	return self.data[1]		# Negative number of laps (for sorting)
	@property
	def num(self):		return self.data[2]
	@property
	def interp(self):	return self.data[3]

	def __repr__( self ):
		return 'Entry( num=%d, lap=%d, interp=%s, t=%s )' % (self.num, self.lap, str(self.interp), str(self.t))

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
	entriesMax = 22
		
	def __init__( self, num ):
		self.num = num
		self.times = []
		self.status = Rider.Finisher
		self.tStatus = None
		self.autoCorrectLaps = True

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

		# Create a seperate working list.
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

		return iTimes

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

	def interpolate( self, stopTime = maxInterpolateTime ):
		if not self.times or self.status in [Rider.DNS, Rider.DQ]:
			return []
			
		# Check if we need to do any interpolation or if the user wants the raw data.
		if not getattr(self, 'autoCorrectLaps', True):
			iTimes = [None] * (len(self.times) + 1)
			# Add a zero start time for the beginning of the race.
			# This avoids a whole lot of special cases later.
			iTimes[0] = 0.0
			iTimes[1:] = self.times
			return [Entry(t=t, lap=i, num=self.num, interp=False) for i, t in enumerate(iTimes)]

		# Adjust the stop time.
		st = stopTime
		dnfPulledTime = None
		if self.status in [Rider.DNF, Rider.Pulled]:
			# If no given time, use the last recorded time for DNF and Pulled riders.
			dnfPulledTime = self.tStatus if self.tStatus is not None else self.times[-1]
			st = min(st, dnfPulledTime + 0.01)
		
		iTimes = self.getCleanLapTimes()

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
			iMax = max( 1, int(math.ceil(st - tBegin) / expected) )
			iMax = min( iMax, Rider.entriesMax - len(iTimes) )
			iTimes.extend( [(tBegin + expected * i, True) for i in xrange(iMax)] )

		# Remove any entries exceeding the dnfPulledTime.
		if dnfPulledTime is not None and tBegin > dnfPulledTime:
			i = bisect.bisect_right( iTimes, (dnfPulledTime, False) )
			while i < len(iTimes) and iTimes[i][0] <= dnfPulledTime:
				i += 1
			del iTimes[i:]
		
		return [Entry(t=it[0], lap=i, num=self.num, interp=it[1]) for i, it in enumerate(iTimes)]
		
	def hasInterpolatedTime( self, tMax ):
		interpolate = self.interpolate()
		try:
			return any( e.interp for e in interpolate if e.t <= tMax )
		except (ValueError, StopIteration):
			return False

class Race(object):
	finisherStatusList = [Rider.Finisher, Rider.Pulled]
	finisherStatusSet = set( finisherStatusList )
	
	nonFinisherStatusList = [Rider.DNF, Rider.DNS, Rider.DQ, Rider.NP, Rider.OTL]
	nonFinisherStatusSet = set( nonFinisherStatusList )
	
	def __init__( self ):
		self.reset()

	def reset( self ):
		self.name = '<RaceName>'
		self.organizer = '<Organizer>'
		self.raceNum = 1
		self.date = datetime.date.today().strftime('%Y-%m-%d')
		self.scheduledStart = '10:00'
		self.minutes = 60
		self.commissaire = '<Commissaire>'
		self.memo = '<RaceMemo>'

		self.categories = {}
		self.riders = {}
		self.startTime = None
		self.finishTime = None
		self.numLaps = None

		self.isChangedFlag = True
		
		self.tagNums = None
		memoize.clear()
		
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
		race.startTime = datetime.datetime.now()
		race.tagNums = None
		self.setChanged()

	def finishRaceNow( self ):
		race.finishTime = datetime.datetime.now()
		race.tagNums = None
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
		return tCur.seconds + tCur.microseconds / 1000000.0

	def lastRaceTime( self ):
		if self.finishTime is not None:
			t = self.finishTime - self.startTime
			return t.seconds + t.microseconds / 1000000.0
		return self.curRaceTime()

	def addTime( self, num, t = None ):
		if t is None:
			t = self.curRaceTime()
		self.getRider(num).addTime( t )
		self.setChanged()
		return t

	def importTime( self, num, t ):
		self.getRider(num).addTime( t )
		
	def deleteRiderTimes( self, num ):
		try:
			rider = self.riders[num]
			rider.times = []
		except KeyError:
			pass
			
	def deleteRider( self, num ):
		try:
			del self.riders[num]
			self.setChanged()
		except KeyError:
			pass
			
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
			
	def deleteAllRiderTimes( self ):
		for num in self.riders.iterkeys():
			self.deleteRiderTimes( num )
		self.setChanged()

	def deleteTime( self, num, t ):
		if not num in self.riders:
			return
		rider = self.riders[num]
		rider.deleteTime( t )
		# If there are no times for this rider, remove the rider entirely.
		if len(rider.times) == 0:
			del self.riders[num]
		self.setChanged()

	@memoize
	def getLastKnownTime( self ):
		try:
			return max( r.getLastKnownTime() for r in self.riders.itervalues() )
		except ValueError:
			return 0.0

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
		entries.sort()
		return entries

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
		# Find the first occurance of the given lap.
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
		leaderTimes, leaderNums = None, None
		
		entries = self.interpolate()
		if entries:
			leaderTimes = [ 0.0 ]
			leaderNums = [ None ]
			leaderTimesLen = 1
			while 1:
				try:
					e = (e for e in entries if e.lap == leaderTimesLen).next()
					leaderTimes.append( e.t )
					leaderNums.append( e.num )
					leaderTimesLen += 1
				except StopIteration:
					break
		
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
		activeCategories.sort()
		
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
		try:
			riderTime = (e.t for e in self.interpolate() if e.num == num and e.lap == leaderLap).next()
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

	def getCategories( self ):
		activeCategories = [c for c in self.categories.itervalues() if c.active]
		activeCategories.sort()
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
		allCategories.sort()
		return allCategories

	def setActiveCategories( self, active = None ):
		allCategories = self.getAllCategories()
		for i, c in enumerate(allCategories):
			c.active = True if active is None or i in active else False
		self.setChanged()

	def setCategories( self, nameStrTuples ):
		newCategories = dict( (name, Category(active, name, numbers, startOffset, raceLaps, i)) \
			for i, (active, name, numbers, startOffset, raceLaps) in enumerate(nameStrTuples) if name )

		if self.categories != newCategories:
			self.categories = newCategories
			self.resetCategoryCache()
			self.setChanged()
			
		self.setCategoryMask()

	def exportCategories( self, fp ):
		for c in self.categories.itervalues():
			fp.write( '%s|%s\n' % (c.name.replace('|',''), c.catStr) )

	def importCategories( self, fp ):
		categories = []
		for r, line in enumerate(fp):
			if not line:
				continue
			fields = line.strip().split('|')
			categories.append( (True, fields[0], fields[1], '00:00', None) )
		self.setCategories( categories )

	def isRiderInCategory( self, num, catName = None ):
		if not catName or catName == 'All':
			return True
		category = self.categories.get( catName, None )
		return category.matches(num) if category is not None else False

	def hasCategory( self, catName = None ):
		# Check if there is at least one rider in this category.
		if not catName or catName == 'All':
			return True
		return any( self.isRiderInCategory(num, catName) for num in self.riders.iterkeys() )

	def getCategoryName( self, num ):
		c = self.getCategory( num )
		return c.name if c else ''

	def getCategory( self, num ):
		# Check the cache for this rider.
		try:
			return getattr( self, 'categoryCache', None )[num]
		except TypeError:
			self.categoryCache = {}
		except KeyError:
			pass
		
		# If not there, find it and add it to the cache.
			
		# Find the category matching this rider.
		try:
			c = (c for c in self.categories.itervalues() if c.active and c.matches(num)).next()
		except StopIteration:
			self.categoryCache[num] = None	# No matching category.
			return None
		
		# Add this rider to the cache.
		self.categoryCache[num] = c
		
		# Proactively classify all riders in this category as we will likely ask for them soon.
		for r in self.riders.itervalues():
			if r.num not in self.categoryCache and c.matches(r.num):
				self.categoryCache[r.num] = c
				
		return c
	
	def getCategoryNumLaps( self, num ):
		try:
			category = self.getCategory( num )
			return category.getNumLaps() or 1000
		except AttributeError:
			return 1000
	
	def resetCategoryCache( self ):
		self.categoryCache = None
	
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

	def getLastFinisherTime( self ):
		if self.numLaps is not None:
			lap = self.numLaps
		else:
			lap = self.getMaxLap()
		entries = self.interpolateLap( lap, True )
		try:
			return entries[-1].t
		except:
			return 0.0
		
	#---------------------------------------------------------------------------------------

	def getResultsList( self, catName = 'All', lap = None ):
		if not self.riders:
			return []
			
		if lap is None or lap > self.getMaxLap():
			lap = self.getMaxLap()
		if self.numLaps is not None and self.numLaps < lap:
			lap = self.numLaps
			
		category = self.categories.get( catName, None )
		if category and category.numLaps:
			lap = min( lap, category.numLaps )

		entries = self.interpolateLap( lap, True )
		if not entries:
			return []

		# Add the latest known time for every finished or pulled rider.
		finishers = []
		finishNums = set()
		finisherStatusSet = Race.finisherStatusSet
		for e in (e for e in reversed(entries) if e.num not in finishNums):
			finishNums.add( e.num )
			if 	race[e.num].status in finisherStatusSet and \
					(category is None or category == self.getCategory(e.num)):
				finishers.append( e )

		# Sort by laps completed, time and num.
		finishers.sort( key = lambda x: (-x.lap, x.t, x.num) )
		return finishers

	def getPrevNextRiderPositions( self, tRace ):
		if not self.isRunning() or not self.riders:
			return {}, {}
		entries = self.interpolate()
		if not entries:
			return {}, {}
			
		# Split up the entries by category.
		catEntries = {}
		getCategory = self.getCategory
		finisherStatusSet = Race.finisherStatusSet
		for e in entries:
			# Is this a finisher?
			if race[e.num].status not in finisherStatusSet:
				continue
			# Does this lap exceed the laps for this category?
			category = getCategory(e.num)
			#if category:
			#	numLaps = category.getNumLaps()
			#	if numLaps and e.lap > numLaps:
			#		continue
			# Otherwise, add the entry to this category.
			catEntries.setdefault(category, []).append( e )

		# For each category, find the first instance of each rider after the leader's lap.
		catTimesNums = self.getCategoryTimesNums()
		ret = [{},{}]
		for cat, catEntries in catEntries.iteritems():
			catTimes, catNums = catTimesNums[cat]
			iLap = bisect.bisect_right( catTimes, tRace ) - 1
			for r in xrange(2):
				iFirst = bisect.bisect_left( catEntries, Entry(catNums[iLap], iLap, catTimes[iLap], False) )

				seen = {}
				catFinishers = [ seen.setdefault(catEntries[i].num, catEntries[i])
								for i in xrange(iFirst, len(catEntries)) if catEntries[i].num not in seen ]
				catFinishers.sort( key = lambda x: (-x.lap, x.t, x.num) )
				for pos, e in enumerate(catFinishers):
					ret[r][e.num] = pos + 1
				iLap += 1
					
		return ret
		
	#----------------------------------------------------------------------------------------
	
	def getResults( self, catName = 'All' ):
		''' Output: colNames, finishers (includes pulled), dnf, dns, dq '''
		finishers = self.getResultsList( catName )
		if not finishers:
			colnames = []
			results = []
		else:
			# Format the timed results by laps down.
			maxLaps = finishers[0].lap
			results = []
			for e in finishers:
				lapsDown = maxLaps - e.lap
				if lapsDown < 0:
					lapsDown = 0
				# print 'lapsDown=%d e.lap=%d' % (lapsDown, e.lap)
				while lapsDown >= len(results):
					results.append( [] )
				results[lapsDown].append( e )

			# Get the column labels and trim out the empty columns.
			colnames = [ str(-k) if k > 0 else str(maxLaps) for k, r in enumerate(results) if len(r) > 0 ]
			results = [ r for r in results if len(r) > 0 ]

		# Get the DNF, DNS and DQ riders.
		category = self.categories.get( catName, None )
		nonFinishersStatusSet = Race.nonFinisherStatusSet
		ridersSubset = [r for r in self.riders.itervalues()
							if r.status in nonFinishersStatusSet and 
								(category is None or category == self.getCategory(r.num))]
		nonFinishers = []
		for status in Race.nonFinisherStatusList:
			numTimes = [(r.num, r.tStatus if r.tStatus is not None else -sys.float_info.max)
							for r in ridersSubset if r.status == status]
			numTimes.sort( key = lambda x : (-x[1], x[0]) )
			nonFinishers.append( numTimes if numTimes else None )

		return colnames, results, nonFinishers[0], nonFinishers[1], nonFinishers[2]

	@memoize
	def getCategoryBestLaps( self, catName = 'All' ):
		category = self.categories.get( catName, None )
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
		lap = bisect.bisect_left( times, raceTime, len(times) - 1 )
		if lap > 1:
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
		return self.getCategoryBestLaps( category.name if category else 'All' )
	
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
			name = 'Cat%d' % (j+1)
			self.categories[name] = Category(name, str(i) + '-' + str(i+9))

		self.setChanged()

if __name__ == '__main__':
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

	c = Category(True, 'test', '100-150-199,205,-50', '00:00', None)
	print( c )
	print( 'mask=', c.getMask() )
	c = Category(True, 'test', '100-199,-150', None)
	print( 'mask=', c.getMask() )
	c = Category(True, 'test', '1400-1499,-1450', None)
	print( 'mask=', c.getMask() )
	
	r.setCategories( [	(True, 'test1', '1100-1199', '00:00', None),
						(True, 'test2', '1200-1299, 2000,2001,2002', '00:00', None),
						(True, 'test3', '1300-1399', '00:00', None)] )
	print( r.getCategoryMask() )
	print( r.getCategory( 2002 ) )

