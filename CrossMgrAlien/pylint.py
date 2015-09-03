import glob
import os
import sys
import subprocess
import StringIO

cmd = 'pylint'

def dopylint( fname = None ):
	with open( 'pylint_output.txt', 'w' ) as output:
		for f in sorted(glob.glob('*.py')):
			if fname is not None:
				if fname != os.path.basename(f):
					continue
			out, err = subprocess.Popen( [cmd, '--errors-only', f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT ).communicate()
			for line in out.split('\n'):
				if "Undefined variable '_' (undefined-variable)" not in line:
					print line
					output.write( '{}\n'.format(line) )
			output.flush()

if __name__  == '__main__':
	try:
		dopylint( sys.argv[1] )
	except IndexError:
		dopylint()