import six
import random
from base64 import urlsafe_b64encode, urlsafe_b64decode

SpiceLen = 13

def pair_swap( a ):
	r = list( a )
	for i in range(0, len(r)-1, 2):
		r[i], r[i+1] = r[i+1], r[i]
	return r

def partial_reverse( a ):
	r = list( a )
	i, j = 0, len(r) - 1
	while i < j:
		r[i], r[j] = r[j], r[i]
		i += 2
		j -= 2
	return r

def encode( s ):
	if not s:
		return s
	
	s = s.encode()
	enc = [ random.randint(0,255) for i in range(SpiceLen) ]
	totCur = sum( enc )
	for i, c in enumerate(s):
		j = ord(c) if six.PY2 else c
		v = (j + enc[i%SpiceLen]*(i+1) + totCur + i*7) % 256
		totCur += j
		enc.append( v )
	ret = urlsafe_b64encode(bytes(''.join(chr(e) for e in partial_reverse(pair_swap(enc))))) if six.PY2 else urlsafe_b64encode(bytes(partial_reverse(pair_swap(enc))))
	if six.PY3:
		return ret.decode('ascii')
	else:
		return ret

def decode( s ):
	if not s:
		return s
	
	if not isinstance(s, bytes):
		s = s.encode()
	b = urlsafe_b64decode( s )
	enc = pair_swap(partial_reverse( [ord(c) for c in b] )) if six.PY2 else pair_swap(partial_reverse( b )) 
	totCur = sum( enc[:SpiceLen] )
	dec = []
	for i, v in enumerate(enc[SpiceLen:]):
		j = (v - enc[i%SpiceLen]*(i+1) - totCur - i*7) % 256
		totCur += j
		dec.append( j )
	return ''.join( chr(c) for c in dec )

if __name__ == '__main__':
	s = "this_is_a_test"
	for i in range(10):
		c = encode( s )
		six.print_( s, c, decode(c) )
