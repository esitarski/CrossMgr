import os
import plistlib

builddir = defines.get('builddir')
if builddir:
	print("Using builddir: {}".format(builddir))
else:
	builddir = '.'
	print("WARNING: builddir is not defined!")

filename = os.path.join(builddir, 'Version.py')
verfile = open(filename, 'r')
line = verfile.readline()
verfile.close()
AppVerName = line.split('=')[1]
AppVerName = AppVerName.replace('"', '')
AppVerName = AppVerName.rstrip()

print("AppVersion: {}".format(AppVerName))

MacApp = AppVerName.split(' ')[0]
MacAppVersion = AppVerName.split(' ')[1]
MacAppFullName = MacApp + '_' + MacAppVersion
print("Mac App Version: {}".format(MacAppVersion))
print("Mac App Fullname: {}".format(MacAppFullName))
#
# Example settings file for dmgbuild
#
# Full docs are at http://dmgbuild.readthedocs.io/en/latest/

# Use like this: dmgbuild -s settings.py "Test Volume" test.dmg

# You can actually use this file for your own application (not just TextEdit)
# by doing e.g.
#
#   dmgbuild -s settings.py -D app=/path/to/My.app "My Application" MyApp.dmg

# .. Useful stuff ..............................................................

application = defines.get('app', 'dist/' + MacApp + '.app')
appname = os.path.basename(application)
print("App:", application)

def icon_from_app(app_path):
	plist_path = os.path.join(app_path, 'Contents', 'Info.plist')
	with open(plist_path, 'rb') as fp:
		plist = plistlib.load(fp)
	icon_name = plist['CFBundleIconFile']
	icon_root,icon_ext = os.path.splitext(icon_name)
	if not icon_ext:
		icon_ext = '.icns'
	icon_name = icon_root + icon_ext
	return os.path.join(app_path, 'Contents', 'Resources', icon_name)

# .. Basics ....................................................................

# Uncomment to override the output filename
filename = MacAppFullName + '.dmg'
print("Filename:", filename)

# Uncomment to override the output volume name
#volume_name = defines.get('volume_name', MacAppFullName)
volume_name = MacAppFullName
print("Volume Name: ", volume_name)

# Volume format (see hdiutil create -help)
format = defines.get('format', 'UDBZ')

# Volume size (must be large enough for your files)
size = defines.get('size', '256M')

# Files to include
files = [ application ]

# Symlinks to create
symlinks = { 'Applications': '/Applications' }

# Volume icon
#
# You can either define icon, in which case that icon file will be copied to the
# image, *or* you can define badge_icon, in which case the icon file you specify
# will be used to badge the system's Removable Disk icon
#
#icon = defines.get("icon", "App.icns")
badge_icon = icon_from_app(application)
icon = badge_icon

print("Icon: ", icon)

# Where to put the icons
icon_locations = {
	appname:        (100, 198),
	'Applications': (400, 198),
	}

# .. Window configuration ......................................................

# Background
#
# This is a STRING containing any of the following:
#
#    #3344ff          - web-style RGB color
#    #34f             - web-style RGB color, short form (#34f == #3344ff)
#    rgb(1,0,0)       - RGB color, each value is between 0 and 1
#    hsl(120,1,.5)    - HSL (hue saturation lightness) color
#    hwb(300,0,0)     - HWB (hue whiteness blackness) color
#    cmyk(0,1,0,0)    - CMYK color
#    goldenrod        - X11/SVG named color
#    builtin-arrow    - A simple built-in background with a blue arrow
#    /foo/bar/baz.png - The path to an image file
#
# The hue component in hsl() and hwb() may include a unit; it defaults to
# degrees ('deg'), but also supports radians ('rad') and gradians ('grad'
# or 'gon').
#
# Other color components may be expressed either in the range 0 to 1, or
# as percentages (e.g. 60% is equivalent to 0.6).
#background = defines.get('background', 'CrossMgrImages/dmgbg.png')
#background = 'builtin-arrow'
background = os.path.join(builddir, MacApp +'Images/dmgbg.png')

print("Background: ", background)

show_status_bar = False
show_tab_view = False
show_toolbar = False
show_pathbar = False
show_sidebar = False
sidebar_width = 180

# Window position in ((x, y), (w, h)) format
window_rect = ((100, 100), (540, 440))

# Select the default view; must be one of
#
#    'icon-view'
#    'list-view'
#    'column-view'
#    'coverflow'
#
default_view = 'icon-view'

# General view configuration
show_icon_preview = False

# Set these to True to force inclusion of icon/list view settings (otherwise
# we only include settings for the default view)
include_icon_view_settings = 'True'
include_list_view_settings = 'auto'

# .. Icon view configuration ...................................................

arrange_by = None
grid_offset = (0, 0)
grid_spacing = 60
scroll_position = (0, 0)
label_pos = 'bottom' # or 'right'
text_size = 12
icon_size = 64

# .. List view configuration ...................................................

# Column names are as follows:
#
#   name
#   date-modified
#   date-created
#   date-added
#   date-last-opened
#   size
#   kind
#   label
#   version
#   comments
# 
list_icon_size = 16
list_text_size = 12
list_scroll_position = (0, 0)
list_sort_by = 'name'
list_use_relative_dates = True
list_calculate_all_sizes = False,
list_columns = ('name', 'date-modified', 'size', 'kind', 'date-added')
list_column_widths = {
	'name': 300,
	'date-modified': 181,
	'date-created': 181,
	'date-added': 181,
	'date-last-opened': 181,
	'size': 97,
	'kind': 115,
	'label': 100,
	'version': 75,
	'comments': 300,
	}
list_column_sort_directions = {
	'name': 'ascending',
	'date-modified': 'descending',
	'date-created': 'descending',
	'date-added': 'descending',
	'date-last-opened': 'descending',
	'size': 'descending',
	'kind': 'ascending',
	'label': 'ascending',
	'version': 'ascending',
	'comments': 'ascending',
	}

