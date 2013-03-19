import re

reEnum = re.compile( 'enum [^}]*\};' )

with open('enums.py', 'w') as f:
	for e in reEnum.findall( open('out_ltkcpp.h').read() ):
		for line in e.split('\n'):
			if line.startswith( 'enum' ):
				f.write( '\n' )
				f.write( '#---------------------------------------------------------------------------\n' )
				f.write( '# %s\n' % line.split(' ',1)[1].strip()[1:] )
				f.write( '#\n' )
			elif line.startswith( '    ' ):
				f.write( line.split(',')[0].strip() )
				f.write( '\n' )
