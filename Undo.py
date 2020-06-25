import Model
from Utils import updateUndoStatus
from Utils import logCall
import pickle
import pickletools

class Undo( object ):
	def __init__( self ):
		self.clear()

	def clear( self ):
		self.undoStack = []
		self.iUndo = None
	
	def getState( self ):
		with Model.LockRace() as race:
			if not race or race.isRunning():
				return None
			return pickletools.optimize( pickle.dumps(race, 2) )
	
	def pushState( self ):
		''' Save the state of the model and remove any redo states. '''
		if self.iUndo is not None:
			del self.undoStack[self.iUndo+1:]
			self.iUndo = None
			return False
			
		self.iUndo = None
		sNew = self.getState()
		if not sNew or (self.undoStack and self.undoStack[-1] == sNew):
			return False
		
		self.undoStack.append( sNew )
		updateUndoStatus()
		return True
		
	def setState( self ):
		if self.iUndo is None:
			return
		with Model.LockRace() as race:
			raceNew = pickle.loads( self.undoStack[self.iUndo] )
			Model.setRace( raceNew )
		updateUndoStatus()

	def isUndo( self ):
		if self.iUndo is not None:
			return self.iUndo > 0
		else:
			return self.undoStack

	def isRedo( self ):
		return self.iUndo is not None and self.iUndo != len(self.undoStack) - 1
	
	@logCall
	def doUndo( self ):
		if not self.isUndo():
			return False
		if self.iUndo is None:
			iUndoStart = len(self.undoStack) - 1
			self.pushState()
			self.iUndo = iUndoStart
		else:
			self.iUndo -= 1
		self.setState()
		return True

	@logCall
	def doRedo( self ):
		if not self.isRedo():
			return False
		self.iUndo += 1
		self.setState()
		return True

# Global singleton for this module.
undo = Undo()
