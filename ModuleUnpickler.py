import pickle

class ModuleUnpickler( pickle.Unpickler ):
	def __init__( self, *args, **kwargs ):
		self.baseModule = kwargs.pop( 'module' ) + '.'
		self.super_find_class = pickle.Unpickler.find_class
		pickle.Unpickler.__init__( self, *args, **kwargs )
	
	def find_class( self, module, name ):
		try:
			return self.super_find_class( self, module, name )
		except ImportError:
			pass
		
		if module.startswith(self.baseModule):
			return self.super_find_class( self, module.split('.', 1)[1], name )
		else:
			return self.super_find_class( self, self.baseModule + module, name )
