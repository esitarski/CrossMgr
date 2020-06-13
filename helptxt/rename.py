import os
import glob
import subprocess

for fname_txt in glob.glob("./*.txt"):
	fname_md = os.path.splitext(os.path.basename(fname_txt))[0] + '.md'
	subprocess.run(["git", "mv", fname_txt, fname_md])
