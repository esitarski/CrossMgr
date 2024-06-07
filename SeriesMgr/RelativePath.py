import os

def FullToRelative( source, destination_full ):
	# Return a relative file based on the source file.
	# Assume that source and destination_full are full file names.
	if os.path.splitext(source)[1]:	# Assume that if the source ends in a suffix then it is a file.  Get the directory.
		source = os.path.dirname( source )

	# Ensure the relative path starts with a dot.
	try:
		return os.path.join('.', os.path.relpath(destination_full, source) )
	except Exception:
		return destination_full

def RelativeToFull( source, destination_rel ):
	# Return an absolute file based on the the source file.
	
	# If the destional is not a relative path, do nothing.
	if not destination_rel.startswith( '.' ):
		return destination_rel
	
	if os.path.splitext(source)[1]:	# Assume that if the source ends in a suffix then it is a file.  Get the directory.
		source = os.path.dirname( source )
	
	return os.path.normpath( os.path.join(source, destination_rel) )

if __name__ == '__main__':
	source = '/a/b/c/d/e.txt'
	
	destination = '/a/b/c/d/e/f/g.txt'
	destination_rel = FullToRelative(source, destination)
	print( source, destination, destination_rel )
	
	destination_full = RelativeToFull( source, destination_rel )
	print( source, destination_rel, destination_full )
	
	destination = '/a/b/c/g.txt'
	destination_rel = FullToRelative(source, destination)
	print( source, destination, destination_rel )
	
	destination_full = RelativeToFull( source, destination_rel )
	print( source, destination_rel, destination_full )
