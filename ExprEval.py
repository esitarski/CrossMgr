import ast
import math
import re

whitelist_constructs = (
	ast.Expression, ast.Call, ast.Name, ast.Num, ast.Load,
	ast.Compare,
	ast.BoolOp, ast.And, ast.Or,
	ast.Str, ast.Slice, ast.Set, ast.Dict, ast.IfExp,
	ast.Attribute, ast.Subscript, ast.Index,
	ast.BinOp, ast.UnaryOp,
	ast.operator, ast.unaryop, ast.cmpop,
)

whitelist_references = {
	"__builtins__":None,
	
	'abs':abs,
	'all':all,
	'any':any,
	'max':max,
	'min':min,
	'sum':sum,
	
	'math':math,
	're':re,
	
	'False':False, 'True':True, 'None':None,
}

class ExprEval( object ):
	def __init__( self ):
		self.bytecode = None
		
	def compile( self, expr ):
		''' Parse the expression, check for disallowed constructs, compile to bytecode. '''
		tree = ast.parse( expr, mode='eval' )
		
		for node in ast.walk(tree):
			if not isinstance(node, whitelist_constructs):
				error = "Disallowed construct: {}".format(node.__class__.__name__)
				try:
					col_offset = node.col_offset
					error += ' at position {}'.format(col_offset)
				except AttributeError:
					pass
				raise Exception( error )
				
		self.bytecode = compile( tree, filename='', mode='eval' )

	def eval( self, vars ):
		''' Execute the compiled expression with the given variables and return the result. '''
		return eval( self.bytecode, whitelist_references, vars )

if __name__ == '__main__':
	exprEval = ExprEval()
	exprEval.compile( '5 <= 3 <= 8 or True == False or 2**2 == 5 or (0 if True else 1) or s.startswith("a") and "a" in {"k","J","L"} and {"q":1}[0] and x+math.modf(2.3)[1] and not "a" in "ababa"[2:-3] or 0 < 1' )
	print exprEval.eval( {'s':'astring', 'x': 10 } )