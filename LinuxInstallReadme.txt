--------------------------------------------
CrossMgr on Linux: Installation Instructions
--------------------------------------------

Due to the diversity of Linux environments, CrossMgr is released as a
Python Package.

--------------------------------------------
Step 1:  Check you Python version.

Check that you have version Python 2.7.x.
To check what version you have, open a shell window and type:

	 python -V
	 
Most Linux distributions come with Python 2.7.x.  If not, you will have to
upgrade to this version.  

Python 3 will not work.

--------------------------------------------
Step 2:  Install "pip", the Python installer

CrossMgr uses the "pip", the Python package installer.
To check if you have "pip", type:

	pip -h
	
into a shell window.
If you don't have "pip", get it from http://www.pip-installer.org/en/latest/installing.html.
You will need to run the install with "sudo".

--------------------------------------------
Step 3:  Download the CrossMgr Python package.

From https://www.sites.google.com/site/crossmgrsoftware/file-cabinet, download
the CrossMgr python package to a directory called "CrossMgrInstall".
The file name has the form "CrossMgr-N.NN.tar.gz".

--------------------------------------------
Step 4:  Run the pip install

"cd" to your "CrossMgrInstall" directory.  Type:

	sudo pip install CrossMgr-N.NN.tar.gz
	
Where, of course, N.NN corresponds to the CrossMgr version.

Pip will automatically pull additional python packages from pypi.
These are xlrd, xlwt, openpyxl and wxpython.

If this process fails, you may need to install these modules from your Linux distro.

Check your distro for python-xlrd, python xlwt, python-openpyxl
and python-wxgtk.

--------------------------------------------
Step 5:  Run CrossMgr

type:

	CrossMgr &
	
Alternatively, make a desktop shortcut.  Consult your distribution for details.
For a nice desktop icon, see /usr/local/lib/python2.7/dist-packages/CrossMgr/images.
Use CrossMgr.png and/or CrossMgr.ico depending on your system requirements.

