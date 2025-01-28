import os
from pathlib import Path
import polib
import argparse

def get_po_paths( root_path=Path('.') ):
	for entry in root_path.iterdir():
		if entry.is_dir() and entry.name != 'site-packages':	# Skip other python modules.
			yield from get_po_paths( entry )
		elif entry.is_file() and entry.suffix == '.po':
			yield entry
		
def po_to_mo( root_dir=None ):
	if not root_dir:
		root_dir = '.'
		
	root_path = Path( root_dir )
	if not (root_path.exists() and root_path.is_dir()):
		return False

	for po_path in get_po_paths( Path(root_dir) ):
		mo_path = Path( os.path.splitext(str(po_path.absolute()))[0] + '.mo' )
		if not mo_path.exists() or po_path.stat().st_mtime_ns > mo_path.stat().st_mtime_ns:
			po_name = str(po_path.resolve())
			mo_name = str(mo_path.resolve())
			print( f'{po_name} --> {mo_name}' )
			polib.pofile( po_name ).save_as_mofile( mo_name )
	
	return True
					
if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		description='Compiles all .po files into .mo files recursively.'
	)
	parser.add_argument( 'dir', nargs='?', default=os.getcwd(), help='Directory to start searching for *.po files.  Defaults to current directory.' )
	args = parser.parse_args()
	
	po_to_mo( args.dir )
