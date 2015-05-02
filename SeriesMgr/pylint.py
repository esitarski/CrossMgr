import glob
import subprocess
import StringIO

cmd = 'pylint'

with open( 'pylint_output.txt', 'w' ) as output:
	for f in sorted(glob.glob('*.py')):
		print f
		out, err = subprocess.Popen( [cmd, '--errors-only', f], stdout=subprocess.PIPE, stderr=subprocess.STDOUT ).communicate()
		for line in out.split('\n'):
			if "Undefined variable '_' (undefined-variable)" not in line:
				print line
				output.write( '{}\n'.format(line) )
		output.flush()
