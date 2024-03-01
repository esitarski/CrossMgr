import os

def UpdateDependencies():
	with open('Dependencies.py') as d:
		for line in d:
			line = line.strip()
			if not line:
				continue
			
			fname = line.split()[1] + '.py'
			print( 'copying: {}'.format(fname) )
			
			try:
				os.remove( fname )
			except Exception:
				pass
			
			with open(os.path.join('..', fname), encoding='utf-8') as fc:
				contents = fc.read()
			if fname in ('Utils.py', 'HelpIndex.py'):
				contents = contents.replace("'CrossMgr", "'SeriesMgr")
			with open(fname, 'w', encoding='utf-8') as fc:
				fc.write( contents )
			
if __name__ == '__main__':
	UpdateDependencies()
