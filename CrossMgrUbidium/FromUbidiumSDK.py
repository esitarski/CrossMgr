import os
import re
import io
import sys
import glob
import shutil
import subprocess
from pathlib import Path

ubidium_src = '../ubidium-sdk-v0.9.7'
ubidium_dest = 'UbidiumSDK'

def FromUbidiumSDK():
	assert os.path.isdir(ubidium_src), f'Error: missing ubidium sdk diretory {ubidium_src}'
	
	if not os.path.isdir(ubidium_dest):
		os.mkdir( ubidium_dest )
	
	# Add python module file.
	Path( ubidium_dest, '__init__.py' ).touch()
	
	#-------------------------------------------------------------------
	# Combine all the certificates into one python file for convenience.
	#
	d = os.path.join( ubidium_src, 'cert', 'ca-cert' )
	with open(os.path.join(ubidium_dest,'Certificates.py'), 'w', encoding='utf-8') as srcFile:
		srcFile.write( 'Certificates={\n' )
		for fname in glob.glob( os.path.join(d, '*.*')):
			with open(fname, 'r', encoding='utf-8') as f:
				contents = f.read()
			srcFile.write( f"'{os.path.basename(fname)}':'''{contents}'''.encode('utf-8'),\n" )
		srcFile.write( '}\n' )
	
	#-------------------------------------------------------------------
	# Copy the proto files to make a local copy.
	#
	shutil.copytree( os.path.join(ubidium_src, 'python', 'proto'), os.path.join(ubidium_dest, 'proto'), dirs_exist_ok=True )
	
	#-------------------------------------------------------------------
	# Compile them into python interface files.
	#
	# python3 -m grpc_tools.protoc -I<PATH_TO_PROTOS> --python_out=<OUTPUT_DIR> --pyi_out=<OUTPUT_DIR> --grpc_python_out=<OUTPUT_DIR> <PATH_TO_PROTOS>*.proto
	python_out = os.path.join(ubidium_dest, "ubidium")
	args = [
		sys.executable,
		'-m', 'grpc_tools.protoc',
		f'-I{os.path.join(ubidium_dest, "proto")}',
		f'--python_out={python_out}',
		f'--pyi_out={python_out}',
		f'--grpc_python_out={python_out}',
	] + glob.glob( os.path.join(ubidium_dest, 'proto', '*.proto') )
	subprocess.check_output( args )
		
	#-------------------------------------------------------------------
	# Fix up import statements in the generated code to support a __init__.py python module.
	#
	os.chdir( os.path.join(ubidium_dest,'ubidium') )
	re_import = re.compile( '(' + '|'.join( f'^import {os.path.splitext(fname)[0]}' for fname in glob.glob('*.py') ) + ')' )
	for fname in (glob.glob('*.py') + glob.glob('*.pyi')):
		output = io.StringIO()
		with open(fname, 'r', encoding='utf-8') as f:
			for line in f:
				m = re_import.search( line )
				if m:
					line = 'from . ' + line
				output.write( line )
		with open(fname, 'w', encoding='utf-8') as f:
			f.write( output.getvalue() )

	# Add python module file.
	Path( ubidium_dest, 'ubidium', '__init__.py' ).touch()
	
if __name__ == '__main__':
	FromUbidiumSDK()
