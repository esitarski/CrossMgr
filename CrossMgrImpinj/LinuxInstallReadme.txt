--------------------------------------------
CrossMgrImpinj on Linux: Installation Instructions
--------------------------------------------

Due to the diversity of Linux environments, CrossMgrImpinj is released as a
Python Package.

If you are installing CrossMgrImpinj for the first time, start at Step 1.
If you are upgrading CrossMgrImpinj to a more recent version, repeat steps Steps 4-5.

--------------------------------------------
Step 1:  Install CrossMgr

Follow all the instructions to install CrossMgr on Linux.
This includes the steps of getting the correct Python version, installing pip, and installing wxPython.

--------------------------------------------
Step 2:  Download the pyllrp package.

From www.sites.google.com/site/crossmgrsoftware, go to Downloads, All Platforms and download
the "PIP-Install-CrossMgrImpinj-N.N.N.tar.gz" python package to a directory called "CrossMgrImpinjInstall"
(the N.N.N is the version).

--------------------------------------------
Step 3:  Run the pyllrp pip install

"cd" to your "CrossMgrImpinjInstall" directory.  Enter:

    sudo pip install pip-install-pllrp-N.N.N.tar.gz

Where, of course, N.N.N corresponds to the pyllrp version.

Pip will automatically download the python packages that pyllrp needs.

--------------------------------------------
Step 4:  Download the CrossMgrImpinj Python package.

From www.sites.google.com/site/crossmgrsoftware, go to Downloads, All Platforms and download
the "pip-Install-pyllrp-N.N.N.tar.gz" python package to a directory called "CrossMgrImpinjInstall"
(the N.N.N is the version).

--------------------------------------------
Step 5:  Run the CrossMgrImpinj pip install

"cd" to your "CrossMgrImpinjInstall" directory.  Enter:

    sudo pip install PIP-Install-CrossMgrImpinj-N.N.N.tar.gz

Where, of course, N.N.N corresponds to the CrossMgrImpinj version.

Pip will automatically download the python packages that CrossMgrImpinj needs.

If this process fails, you may need to install these modules from your Linux distro.

--------------------------------------------
Step 6:  Run CrossMgrImpinj

type:

    CrossMgrImpinj &

--------------------------------------------
Step 7:  Make a desktop launcher.

This depends on your Linux distribution.

On Ubuntu, see http://askubuntu.com/questions/78730/how-do-i-add-a-custom-launcher

Briefly, from a terminal, enter:

    gnome-desktop-item-edit ~/Desktop/ --create-new

If this doesn't work, you may have to install it with:

    sudo apt-get install gnome-panel

Type in the information to the dialog to launch CrossMgrImpinj.
For the command, enter:

    /usr/local/bin/CrossMgrImpinj

To customize the launch icon, click on the default "spring" icon in the
upper left of the dialog.
Browse to "/usr/local/CrossMgrImpinjImages/CrossMgrImpinj.png".

--------------------------------------------
Step 8:  Uninstalling CrossMgrImpinj.

To uninstall CrossMgrImpinj, type the command:

    sudo pip uninstall CrossMgrImpinj

This will clean up all the installed files.

--------------------------------------------
Step 9:  Upgrading CrossMgrImpinj.

Follow instructions 4 and 4.
You do not need to install wxPython or CrossMgr again.
