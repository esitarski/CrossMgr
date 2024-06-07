import os

def UpdateDependencies():
	with open('Dependencies.py', encoding='utf8') as d:
		for line in d:
			line = line.strip()
			if not line:
				continue
			
			fname = line.split()[1] + '.py'
			print( f'copying: {fname}' )
			
			try:
				os.remove( fname )
			except Exception:
				pass
			
			with open(os.path.join('..', fname), encoding='utf8') as fc:
				contents = fc.read()
			if fname in ('Utils.py', 'HelpIndex.py'):
				contents = contents.replace("'CrossMgr", "'SeriesMgr").replace('CrossMgrImages', 'SeriesMgrImages')
			with open(fname, 'w', encoding='utf8') as fc:
				fc.write( contents )
			
if __name__ == '__main__':
	UpdateDependencies()
