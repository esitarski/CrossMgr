----------------------------------------------
CrossMgr on the Mac: Installation Instructions
----------------------------------------------

CrossMgr is released as a Python Package on the Mac.

The install requires some one-time configuration.
After that, upgrades are easy.

If you are installing CrossMgr for the first time, start at Step 1.
If you are upgrading CrossMgr to a more recent version, repeat steps Steps 3-4.

--------------------------------------------
Step 1:  Check you Python version.

Check that you have version Python 2.7.x available on your Mac.
To check what version you have, open a shell window and type:

	 python -V
	 
Most Mac distributions come with Python 2.5.x.  If so, you will have to
upgrade to version 2.7.x.

You can get Python for the Mac for free from here:  http://www.python.org/getit/  

Make sure you get Python 2.7.x - Python 3 will not work.

--------------------------------------------
Step 2:  Check that you have "pip", the Python installer

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

From a shell window, "cd" to your "CrossMgrInstall" directory.  Type:

	sudo pip install CrossMgr-N.NN.tar.gz
	
Where, of course, N.NN corresponds to the CrossMgr version.

Pip will automatically pull additional python packages from pypi, the Python repository.
These are xlrd, xlwt, openpyxl and wxpython.

If this process fails, you may need to install these modules directly from Pypi.
You can search for, download and install these packages here: http://pypi.python.org/pypi

--------------------------------------------
Step 5:  Run CrossMgr

From a shell window, type:

	CrossMgr &
	
When CrossMgr comes us, click on "Demo|Simulate Race...", and click OK on the confirmation dialog.
After the race starts, click on the Chart screen (F6).
While on this screen, press CTRL-h to check that the help screen comes up.
	
--------------------------------------------
Step 6:  Make an alias.

Check the Mac instructions for how to make an alias for CrossMgr.
For a nice icon, use /usr/local/CrossMgrImages/CrossMgr.png

--------------------------------------------
Step 7:  Uninstalling CrossMgr.
	
If you need to uninstall CrossMgr, from a shell window, type the command:

	sudo pip uninstall CrossMgr

This will clean up the installed files.

--------------------------------------------
Step 7:  Upgrading CrossMgr.
	
If you want to upgrade CrossMgr, repeat Steps 3-4.

CrossMgr is always backwards-compatible with its data files.
