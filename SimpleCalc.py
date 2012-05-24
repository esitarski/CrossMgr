
import math
import re

tokNum = 'n'
tokError = 'e'
tokEnd = '$'

reTime = re.compile(
	'(?:[0-9]+:[0-5][0-9]:[0-5][0-9])|(?:[0-5]?[0-9]:[0-5][0-9])(?:\.[0-9]+)?' )
	# ------[HHH]H:MM:SS--------------   ------[M]M:SS---------  ---[.ddddddd]---
reNum = re.compile(
	'[0-9]*\.?[0-9]+' )
	# [ddd][.]d[ddd]
reWhitespace = re.compile( '[ \r\t]+' )
singleCharTokens = set( c for c in '+-*/()' )

class TimeEvalError( Exception ):
	def __init__( self, error, line, col, i ):
		self.error = error
		self.line = line
		self.col = col
		self.i = i
		
	def __repr__( self ):
		return '%s in %d:%d %d' % self.error, self.line, self.col, self.i

class TimeEvalEmptyExpressionError( TimeEvalError ):
	def __init__( self ):
		TimeEvalError.__init__( self, 'empty expression', 0, 0, 0 )
		
class TimeEvalSyntaxError( TimeEvalError ):
	def __init__( self, error, line, col, i ):
		TimeEvalError.__init__( self, error, line, col, i )
		
class TimeEvalDivideByZeroError( TimeEvalError ):
	def __init__( self, line, col, i ):
		TimeEvalError.__init__( self, 'divide by zero error', line, col, i )

class TimeEval( object ):
	def  __init__( self, str = None ):
		self.clear()

	def clear( self ):
		self.parser = None
		self.tok, self.value, self.line, self.col, self.i = None, None, 0, 0, 0
		
	def parse( self, str ):
		line, col = 0, 0
		i, iMax = 0, len(str)
		while i < iMax:
			# Skip whitespace.
			m = reWhitespace.match( str, i )
			if m:
				col += len(m.group(0))
				i += len(m.group(0))
				continue
				
			# Match time format.
			m = reTime.match( str, i )
			if m:
				x = 0.0
				for f in m.group(0).split(':'):
					x = x * 60.0 + float(f)
				yield tokNum, x, line, col, i
				col += len(m.group(0))
				i += len(m.group(0))
				continue

			# Match pure numbers.
			m = reNum.match( str, i )
			if m:
				yield tokNum, float(m.group(0)), line, col, i
				col += len(m.group(0))
				i += len(m.group(0))
				continue

			c = str[i]
			
			# Process single char tokens.
			if c in singleCharTokens:
				yield c, None, line, col, i
				col += 1
				i += 1
				continue
				
			# Skip newlines, but adjust the line and col counters.
			if c == '\n':
				line += 1
				col = 1
				i += 1
				continue
				
			raise TimeEvalSyntaxError( 'invalid char', line, col, i )
				
		yield tokEnd, None, line, col, i
	
	def skip( self ):
		self.tok, self.value, self.line, self.col, self.iStr = self.parser.next()
		
	def expr( self ):
		x = self.factor()
		while self.tok in '+-':
			op = self.tok
			self.skip()
			right = self.factor()
			if op == '+':
				x += right
			else:
				x -= right
		return x
	
	def factor( self ):
		x = self.term()
		while self.tok in '*/':
			op = self.tok
			self.skip()
			lineSave, colSave, iStrSave = self.line, self.col, self.iStr
			tokSave = self
			right = self.factor()
			if op == '*':
				x *= right
			else:
				if right == 0.0:
					raise TimeEvalDivideByZeroError( lineSave, colSave, iStrSave )
				x /= right
		return x
		
	def term( self ):
		if self.tok == '-':
			sgn = -1
			self.skip()
		else:
			sgn = 1
		if self.tok == tokNum:
			x = self.value
			self.skip()
		elif self.tok == '(':
			self.skip()
			x = self.expr()
			if self.tok == ')':
				self.skip()
			else:
				raise TimeEvalSyntaxError( 'missing ")"' , self.line, self.col, self.iStr )
		else:
			if self.tok == tokEnd:
				raise TimeEvalSyntaxError( 'incomplete expression', self.line, self.col, self.iStr )
			else:
				raise TimeEvalSyntaxError( 'invalid token', self.line, self.col, self.iStr )
			
		return sgn * x
	
	def eval( self, str ):
		self.clear()
		self.parser = self.parse( str )
		self.skip()
		if self.tok == tokEnd:
			raise TimeEvalEmptyExpressionError()
		x = self.expr()
		if self.tok != tokEnd:
			raise TimeEvalSyntaxError( 'unrecognized input', self.line, self.col, self.iStr )
		return x
		
	def __call__( self, str ):
		return eval( str )
		
def formatTime( secs, highPrecision = True ):
	if secs is None:
		secs = 0
	if secs < 0:
		sign = '-'
		secs = -secs
	else:
		sign = ''
	f, ss = math.modf(secs)
	secs = int(ss)
	hours = int(secs // (60*60))
	minutes = int( (secs // 60) % 60 )
	secs = secs % 60
	if hours > 0:
		s = "%s%d:%02d:%02d" % (sign, hours, minutes, secs)
	else:
		s = "%s%02d:%02d" % (sign, minutes, secs)
	if highPrecision:
		d = int( f * 100 )
		s += '.%02d' % d
	return s

def testEval( str  ):
	re = TimeEval()
	try:
		x = formatTime( re.eval(str) )
		print str, '=', x
	except TimeEvalEmptyExpressionError:
		print 'empty expression'
	except (TimeEvalSyntaxError, TimeEvalDivideByZeroError) as e:
		print str
		print ' ' * e.i + '^'
		print ' ' * e.i + '|'
		print ' ' * e.i + '+---' + e.error
	print '--------------------------------------------------------------------'

if __name__ == '__main__':
	testEval( '' )
	testEval( '3.1415926 * 3.1415926' )
	testEval( '-1:00:00' )
	testEval( '30:00 - -30:00' )
	testEval( '1:00:00 / 12' )
	testEval( '1:00:00 * 2.5' )
	testEval( '1:75:00 * 2.5' )
	testEval( '1:00:00 * (1+3)' )
	testEval( '1:00:00 + 10 20' )
	testEval( '1:00:00 *' )
	testEval( '23542345234523452345.456345634563456' )
	testEval( '1:00:00 / (30-20-10)' )
	testEval( '1:00:00 / (30-20-10' )
	testEval( '1:00:00 + bla / (30-20-10)' )
	testEval( '1:0:0 / 2' )