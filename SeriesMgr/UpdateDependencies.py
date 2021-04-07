import os
import shutil

def UpdateDependencies():
	with open('Dependencies.py') as d:
		for line in d:
			line = line.strip()
			if not line:
				continue
			fname = line.split()[1] + '.py'
			print( 'copying: {}'.format(fname) )
			if fname == 'Utils.py':
				with open(os.path.join('..', fname)) as fc:
					text = fc.read()
				with open(fname, 'w') as fc:
					fc.write( text.replace("'CrossMgr", "'SeriesMgr") )
			else:
				shutil.copy( os.path.join( '..', fname), '.' )
			
if __name__ == '__main__':
	UpdateDependencies()