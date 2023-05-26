
class ValueContext( object ):
	__slots__ = ['value', 'context']
	
	def __init__( self, value=0, context=None ):
		self.value = value
		self.context = context if isinstance(context, list) else [context] if context is not None else []
		
	def __iadd__( self, vc ):
		self.value += vc.value
		self.context.extend( vc.context )
		return self
		
	def __add__( self, vc ):
		return ValueContext( self.value + vc.value, self.context + vc.context )
		
	def __lt__(self, vc):
		return self.value <  vc.value
		
	def __le__(self, vc):
		return self.value <= vc.value
		
	def __eq__(self, vc):
		return self.value == vc.value
		
	def __ne__(self, vc):
		return self.value != vc.value
		
	def __ge__(self, vc):
		return self.value >= vc.value
		
	def __gt__(self, vc):
		return self.value >  vc.value
	
	def __repr__( self ):
		return 'ValueContext({}, {})'.format( self.value, self.context )
		#return u'{}'.format(self.value)

if __name__ == '__main__':
	v = ValueContext(10, 100)
	print( v )
	v += ValueContext(20, 200)
	print( v )
	v += ValueContext(30, 300)
	print( v )
	
