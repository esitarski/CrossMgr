----------------------------------------------
CrossMgr on the Mac: Installation Instructions
----------------------------------------------

CrossMgr is released as a Python Package on the Mac.

The install requires some one-time configuration, and you need to be connected to the internet.
After that, upgrades are easy.

If you are installing CrossMgr for the first time, start at Step 1.
If you are upgrading CrossMgr to a more recent version, repeat steps Steps 4-5.

--------------------------------------------
Step 1:  Check you Python version.

Check that you have version Python 2.7.x available on your Mac.
To check what version you have, open a shell window and type:

	 python -V

Older Mac distributions came with Python 2.5.x.  If so, you will have to
upgrade to version 2.7.x.

You can get Python for the Mac for free from here:  http://www.python.org/getit/  

Make sure you get Python 2.7.x - Python 3 will not work.

--------------------------------------------
Step 2:  Check that you have "pip", the Python installer

CrossMgr uses the "pip", the Python package installer.
To check if you have "pip", type:

	pip -h

into a shell window.
If you don't have "pip", get it for free from http://www.pip-installer.org/en/latest/installing.html and follow the instructions.

--------------------------------------------
Step 3:  Install wxPython

Unfortunately, wxPython must be manually installed on the Mac.
Fortunately, this is not a big deal.  Open a terminal.  Enter (or cut-and-paste):

    sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n

Of course, this is also free.
--------------------------------------------
Step 4:  Download the CrossMgr Python package.

From https://www.sites.google.com/site/crossmgrsoftware/file-cabinet, download
the "PIP-Install-CrossMgr-N.N.N.tar.gz" python package to a directory called "CrossMgrInstall"
(the N.N.N is the version).

--------------------------------------------
Step 5:  Run the pip install

"cd" to your "CrossMgrInstall" directory.  Enter:

	sudo pip install PIP-Install-CrossMgr-N.N.N.tar.gz
	
Where, of course, N.N.N corresponds to the CrossMgr version.

Pip will automatically pull additional python packages from pypi.
These are xlrd, xlwt, whoosh, qrcode and openpyxl.

If this process fails, you may need to install these modules manually from www.pypi.org.

--------------------------------------------
Step 6:  Run CrossMgr

type:

	CrossMgr &

--------------------------------------------
Step 7:  Make an alias.

Follow the Mac instructions for how to make an alias for CrossMgr.
For a nice icon, use /usr/local/CrossMgrImages/CrossMgr.png

--------------------------------------------
Step 8:  Uninstalling CrossMgr.
	
If you need to uninstall CrossMgr, from a shell window, type the command:

	sudo pip uninstall CrossMgr

This will clean up all installed files.

--------------------------------------------
Step 7:  Upgrading CrossMgr.
	
If you want to upgrade CrossMgr, repeat Steps 4-5.

CrossMgr is always backwards-compatible with its data files.
