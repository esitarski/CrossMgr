--------------------------------------------
CrossMgr on Linux: Installation Instructions
--------------------------------------------

Due to the diversity of Linux environments, CrossMgr is released as a
Python Package.

If you are installing CrossMgr for the first time, start at Step 1.
If you are upgrading CrossMgr to a more recent version, repeat steps Steps 4-5.

--------------------------------------------
Step 1:  Check you Python version.

Check that you have version Python 2.7.x.
To check what version you have, open a shell window and type:

	 python -V
	 
Most Linux distributions come with Python 2.7.x.  If not, you will have to
upgrade to this version.  

Python 3 will not work.

--------------------------------------------
Step 2:  Check that you have "pip", the Python installer

CrossMgr uses the "pip", the Python package installer.
To check if you have "pip", type:

	pip -h
	
into a shell window.
If you don't have "pip", get it from http://www.pip-installer.org/en/latest/installing.html.
You will need to run the install with "sudo".

--------------------------------------------
Step 3:  Install wxPython

Unfortunately, wxPython must be manually installed on Linux.
Fortunately, this is not a big deal.  Open a terminal.  Enter (or cut-and-paste):

    sudo apt-get install python-wxgtk2.8 python-wxtools wx2.8-i18n

--------------------------------------------
Step 4:  Download the CrossMgr Python package.

From https://www.sites.google.com/site/crossmgrsoftware/file-cabinet, download
the file "PIP-Install-CrossMgr-N.NN.tar.gz" python package to a directory called "CrossMgrInstall"
(the N.NN is the version).

--------------------------------------------
Step 5:  Run the pip install

"cd" to your "CrossMgrInstall" directory.  Enter:

	sudo pip install PIP-Install-CrossMgr-N.NN.tar.gz
	
Where, of course, N.NN corresponds to the CrossMgr version.

Pip will automatically pull additional python packages from pypi.
These are xlrd, xlwt, whoosh, openpyxl and wxpython.

If this process fails, you may need to install these modules from your Linux distro.

Check your distro for python-xlrd, python-xlwt, python-qrcode, python-openpyxl
and python-wxgtk.

--------------------------------------------
Step 6:  Run CrossMgr

type:

	CrossMgr &
	
--------------------------------------------
Step 7:  Make a desktop launcher.

This depends on your Linux distribution.

On Ubuntu, see http://askubuntu.com/questions/78730/how-do-i-add-a-custom-launcher.

Briefly, from a terminal, enter:

	gnome-desktop-item-edit ~/Desktop/ --create-new
	
If this doesn't work, you may have to install it with:

	sudo apt-get install gnome-panel
	
Type in the information to the dialog to launch CrossMgr.
For the command, enter:

	/usr/local/bin/CrossMgr

To customize the launch icon, click on the default "spring" icon in the
upper left of the dialog.
Browse to "/usr/local/CrossMgrImages/CrossMgr.png".

--------------------------------------------
Step 8:  Uninstalling CrossMgr.
	
If you need to uninstall CrossMgr, type the command:

	sudo pip uninstall CrossMgr

This will clean up the installed files.

--------------------------------------------
Step 9:  Upgrading CrossMgr.
	
If you want to upgrade CrossMgr, just download the latest version and follow
the installation instructions.

CrossMgr is always backwards-compatible with its data files.
