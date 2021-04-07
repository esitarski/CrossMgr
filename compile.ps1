<#	
	.NOTES
	===========================================================================
	 Created with: 	SAPIEN Technologies, Inc., PowerShell Studio 2019 v5.6.170
	 Created on:   	12/26/2019 11:07 AM
	 Created by:   	Mark Buckaway
	 Organization: 	
	 Filename:     	
	===========================================================================
	.DESCRIPTION
		A description of the file.
#>

# Command line options
param (
	[switch]$help = $false,
	[string]$environ = "env",
	[string]$pythonexe = "python3.7.exe",
	[switch]$cmgr = $false,
	[switch]$cmgri = $false,
	[switch]$trw = $false,
	[switch]$smgr = $false,
	[switch]$cmgra = $false,
	[switch]$video = $false,
	[switch]$pts = $false,
	[switch]$camera = $false,
	[switch]$all = $false,
	[switch]$versioncmd = $false,
	[switch]$setupenv = $false,
	[switch]$clean = $false,
	[switch]$compile = $false,
	[switch]$pyinst = $false,
	[switch]$copyasset = $false,
	[switch]$package = $false,
	[switch]$everything = $false,
	[switch]$fixsmgr = $false,
	[switch]$tag = $false,
	[switch]$checkver = $false,
	[switch]$locale = $false,
	[switch]$virus = $false,
	[switch]$updatever = $false,
	[switch]$release = $false
)

# Globals
$environ = "env"
$script:pythongood = $false

# Check the python version. Current only 3.7.x.
function CheckPythonVersion
{
	if ($script:pythongood -eq $false)
	{
		$pythonver = ' '
		$result = (Start-Process -Wait -NoNewWindow -RedirectStandardOutput 'pyver.txt' -FilePath "python.exe" -ArgumentList "--version")
		if (!(Test-Path 'pyver.txt'))
		{
			Write-Host "Cant find python version. Aborting..."
			exit 1
		}
		$pythonver = Get-Content 'pyver.txt'
		Remove-Item 'pyver.txt'
		$version = $pythonver.Split(' ')[1]
		$minor = $version.Split('.')[1]
		if ($minor -ne '7')
		{
			Write-Host "Python 3.7.x required, and you have ", $version, "installed. Aborting..."
			exit 1
		}
		Write-Host "Found Python ", $version
		$script:pythongood = $true
	}
	
}
function GetBuildDir($program)
{
	$builddir = '.'
	if ($program -ne 'CrossMgr')
	{
		$builddir = $program
	}
	return $builddir
}

function CheckEnvActive
{
	Write-Host $env:VIRTUAL_ENV
	if (([string]::IsNullOrEmpty($env:VIRTUAL_ENV)) -and (Test-Path -Path $environ))
	{
		$runenv = "$environ\scripts\activate.ps1"
		Invoke-Expression $runenv
		Write-Host "Virtual environment ($env:VIRTUAL_ENV) activated"
	}
	elseif (!([string]::IsNullOrEmpty($env:VIRTUAL_ENV)))
	{
		Write-Host "Using existing environment ($env:VIRTUAL_ENV)"
	}
	else
	{
		Write-Host "Python environment not active. Aborting..."
		exit 1		
	}
	
}

function doPyInstaller($program)
{
	CheckPythonVersion
	CheckEnvActive
	$builddir = GetBuildDir($program)
	$iconpath = "${program}Images"
	$distpath = "dist"
	$buildpath = "build"
	if ($program -ne "CrossMgr")
	{
		$distpath = "..\dist"
		$buildpath = "..\build"
	}
	Set-Location -Path $builddir
	Write-Host "pyinstaller.exe $program.pyw --icon=$iconpath\$program.ico --distpath=$distpath --workpath=$buildpath --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter"
	#Write-Host "pyinstaller.exe $program.pyw --icon=$iconpath\$program.ico --distpath=$distpath --workpath=$buildpath --clean --debug --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter"
	Start-Process -Wait -NoNewWindow -FilePath "pyinstaller.exe" -ArgumentList "$program.pyw --icon=$iconpath\$program.ico --distpath=$distpath --workpath=$buildpath --clean --windowed --noconfirm --exclude-module=tcl --exclude-module=tk --exclude-module=Tkinter --exclude-module=_tkinter"
	$result = $?
	if ($program -ne "CrossMgr")
	{
		Set-Location -Path ".."
	}
	if ($result -eq $false)
	{
		Write-Host "Build failed. Aborting..."
		exit 1
	}
}

function GetVersion($program)
{
	$builddir = GetBuildDir($program)
	if (!(Test-Path -Path "$builddir/Version.py"))
	{
		Write-Host "No version file in ", $builddir, "/Version.py. Aborting..."
		exit 1
	}
	$versionItem = Get-Content "$builddir/Version.py"
	$version = $versionItem.Split(' ')[1].Replace("`"", "")
	Write-Host $program, "Version is", $version
	return $version
}

function Cleanup($program)
{
	Write-Host 'Cleaning up everything...'
	$dirs = @(
		'__pycache__',
		'CrossMgrImpinj/__pycache__',
		'TagReadWrite/__pycache__',
		'CrossMgrAlien/__pycache__',
		'SeriesMgr/__pycache__',
		'PointsRaceMgr/__pycache__',
		'dist',
		'build',
		'release',
		'*.spec'
	)
	foreach ($dir in $dirs)
	{
		Write-Host 'Cleaning: ', $dir
		Remove-Item -Recurse -Force -ErrorAction Ignore $dir
	}
}

function CompileCode($program)
{
	CheckPythonVersion
	CheckEnvActive
	$builddir = GetBuildDir($program)
	Write-Host "Compiling code..."
	Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "-mcompileall -l $builddir"
	if ($? -eq $false)
	{
		Write-Host "Compile failed. Aborting..."
		exit 1
	}
}

function BuildLocale($program)
{
	CheckPythonVersion
	CheckEnvActive
	$builddir = GetBuildDir($program)
	$localepath = "$builddir\${program}Locale"
	$locales = Get-ChildItem -Directory -Path $localepath
	foreach ($locale in $locales)
	{
		$pofile="$localepath\$locale\LC_MESSAGES\messages.po"
		Write-Host "Building Locale: $locale"
		Write-Host "python -mbabel compile -f -d $localepath -l $locale -i $pofile"
		Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "-mbabel compile -f -d $localepath -l $locale -i $pofile"
		if ($? -eq $false)
		{
			Write-Host "Locale $locale failed. Aborting..."
			exit 1
		}
	}
}

function CopyAssets($program)
{
	$builddir = GetBuildDir($program)
	$resourcedir = "dist/$program"
	if (!(Test-Path -Path $resourcedir))
	{
		New-Item -ItemType Directory -Force $resourcedir
	}
	if (Test-Path "$builddir/${program}Images")
	{
		Write-Host "Copying Images to $resourcedir"
		Copy-Item -Recurse -Force -Path "$builddir/${program}Images" -Destination "$resourcedir"
	}
	if (Test-Path "$builddir/${program}Html")
	{
		Write-Host "Copying Html to $resourcedir"
		Copy-Item -Recurse -Force -Path "$builddir/${program}Html" -Destination "$resourcedir"
	}
	if (Test-Path "$builddir/${program}Locale")
	{
		BuildLocale($program)
		Write-Host "Copying Locale to $resourcedir"
		Copy-Item -Recurse -Force -Path "$builddir/${program}Locale" -Destination "$resourcedir"
	}
	if ($program -eq "CrossMgr")
	{
		Copy-Item -Force -Path 'CrossMgrTutorial.pdf' -Destination "$resourcedir"
		if (Test-Path "CrossMgrHelpIndex")
		{
			Remove-Item -Recurse -Force -Path "CrossMgrHelpIndex"
		}
		Write-Host 'Building Help for CrossMgr...'
		Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "buildhelp.py"
		if ($? -eq $false)
		{
			Write-Host "Help Build failed. Aborting..."
			exit 1
		}
		Copy-Item -Recurse -Force -Path "CrossMgrHelpIndex" -Destination "$resourcedir"
	}
	if ($program -eq "CrossMgrVideo")
	{
		Set-Location -Path 'CrossMgrVideo'
		if (Test-Path "CrossMgrHelpIndex")
		{
			Remove-Item -Recurse -Force -Path "CrossMgrHelpIndex"
		}
		Write-Host 'Building Help for CrossMgr...'
		# Copy-Item -Force -Path '..\HelpIndex.py' -Destination 'HelpIndex.py'
		Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "buildhelp.py"
		if ($? -eq $false)
		{
			Write-Host "Help Build failed. Aborting..."
			Set-Location -Path '..'
			exit 1
		}
		# Copy-Item -Force -Recurse -Path "CrossMgrHelpIndex" -Destination "..\${resourcedir}"
		Set-Location -Path '..'
	}
	if ($program -eq "SeriesMgr")
	{
		Set-Location -Path 'SeriesMgr'
		if (Test-Path "CrossMgrHelpIndex")
		{
			Remove-Item -Recurse -Force -Path "CrossMgrHelpIndex"
		}
		Write-Host 'Building Help for SeriesMgr...'
		# Copy-Item -Force -Path '..\HelpIndex.py' -Destination 'HelpIndex.py'
		Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "buildhelp.py"
		if ($? -eq $false)
		{
			Write-Host "Help Build failed. Aborting..."
			Set-Location -Path '..'
			exit 1
		}
		# Copy-Item -Force -Recurse -Path "CrossMgrHelpIndex" -Destination "..\${resourcedir}"
		Set-Location -Path '..'
	}
	# Copy help files last to ensure they are built by now.
	if (Test-Path "$builddir/${program}HtmlDoc")
	{
		Write-Host "Copying HtmlDoc to $resourcedir"
		Copy-Item -Recurse -Force -Path "$builddir/${program}HtmlDoc" -Destination "$resourcedir"
	}
}

function Package($program)
{
	$builddir = GetBuildDir($program)
	$version = GetVersion($program)
	$newinstallname = "${program}_Setup_x64_v${version}".Replace('.', '_')
	$yeartoday = (Get-Date).Year
	$curdir = (Get-Item -Path ".\").FullName
	$sourcepath = "$curdir\dist\$program"
	$releasepath = "$curdir\release"
	$setupversion = $version.Split('-')[0]
	if ($version.Split('-')[1] -eq 'private')
	{
		$setupversion = "${setupversion}.99"
	}
	
	Write-Host "Packaging $program from $sourcepath to $newinstallname in $releasepath..."
	$setup = "AppName=$program
SourceDir=$sourcepath
AppPublisher=Edward Sitarski
AppContact=Edward Sitarski
AppCopyright=Copyright (C) 2004-$yeartoday Edward Sitarski
AppVerName=$program
AppPublisherURL=http://www.sites.google.com/site/crossmgrsoftware/
AppUpdatesURL=http://github.com/estarski/crossmgr/
VersionInfoVersion=$setupversion
VersionInfoCompany=Edward Sitarski
VersionInfoProductName=$program
VersionInfoCopyright=Copyright (C) 2004-$yeartoday Edward Sitarski
OutputBaseFilename=$newinstallname
OutputDir=$releasepath
"
	Set-Content -Path "$builddir\inno_setup.txt" -Value "$setup"
	# Scan the registry for innosetup 6.x
	$apps=(Get-ChildItem HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | % { Get-ItemProperty $_.PsPath } | Select DisplayName, InstallLocation | Sort-Object Displayname -Descending)
	foreach ($app in $apps)
	{
		if ($app.DisplayName -like 'Inno Setup version 6*')
		{
			$innolocaton = $app.InstallLocation
			break
		}
	}
	if (![string]::IsNullOrEmpty($innolocaton) -and (Test-Path -Path $innolocaton))
	{
		Write-Host "InnoSetup 6 installed $innolocaton (registry)"
	}
	elseif (Test-Path -Path 'C:\Program Files (x86)\Inno Setup 6')
	{
		$innolocaton = 'C:\Program Files (x86)\Inno Setup 6\'
		Write-Host "InnoSetup 6 installed $innolocaton (directory)"
	}
	elseif (Test-Path -Path 'C:\Program Files\Inno Setup 6')
	{
		$innolocaton = 'C:\Program Files\Inno Setup 6\'
		Write-Host "InnoSetup 6 installed $innolocaton (directory)"
	}
	elseif (Test-Path -Path 'D:\Program Files (x86)\Inno Setup 6')
	{
		$innolocaton = 'D:\Program Files (x86)\Inno Setup 6\'
		Write-Host "InnoSetup 6 installed $innolocaton (directory)"
	}
	elseif (Test-Path -Path 'D:\Program Files\Inno Setup 6')
	{
		$innolocaton = 'D:\Program Files\Inno Setup 6\'
		Write-Host "InnoSetup 6 installed $innolocaton (directory)"
	}
	else
	{
		Write-Host "Cant find Inno Setup 6.x! Is it installed? Aborting...."
		exit 1
	}
	$inno = "${innolocaton}ISCC.exe"
	Start-Process -Wait -NoNewWindow -FilePath "$inno" -ArgumentList "${builddir}\${program}.iss"
	if ($? -eq $false)
	{
		Write-Host "Inno Setup failed. Aborting..."
		Set-Location -Path '..'
		exit 1
	}
	
}

function EnvSetup($program)
{
	CheckPythonVersion
	if (!(Test-Path -Path 'requirements.txt'))
	{
			Write-Host 'Script must be run from the same directory as the requirements.txt file. Aborting...'
			exit 1
	}
	if ([string]::IsNullOrEmpty($env:VIRTUAL_PATH))
	{
		if (Test-Path -Path $environ)
		{
			Write-Host 'Activing virtual env', $env:VIRTUAL_ENV, '...'
			$runenv = "$environ/scripts/activate.ps1"
			Invoke-Expression $runenv
			if ($? -eq $false)
			{
				Write-Host 'Virtual env activation failed. Aborting...'
				exit 1
			}
		}
		else
		{
			Write-Host "Creating Virtual env", $environ
			Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "-mpip install virtualenv"
			if ($? -eq $false)
			{
				Write-Host 'Virtual env setup failed. Aborting...'
				exit 1
			}
			Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "-mvirtualenv $environ"
			if ($? -eq $false)
			{
				Write-Host 'Virtual env setup failed. Aborting...'
				exit 1
			}
			$runenv = "$environ/scripts/activate.ps1"
			Invoke-Expression $runenv
			if ($? -eq $false)
			{
				Write-Host 'Virtual env activation failed. Aborting...'
				exit 1
			}
		}
	}
	else
	{
		Write-Host 'Already using', $env:VIRTUAL_ENV
	}
	$result = (Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "-mpip install pywin32")
	$result = (Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "-mpip install -r requirements.txt")
	if ($? -eq $false)
	{
		Write-Host 'Pip requirements.txt setup failed. Aborting...'
		exit 1
	}
	
}

function updateVersion($programs)
{
	if ($programs.Length -eq 0)
	{
		Write-Host "No programs selected"
		exit 1
	}
	if (-not [string]::IsNullOrEmpty($env:GITHUB_REF))
	{
		Write-Host "GITHUB_REF=$env:GITHUB_REF"
		foreach ($program in $programs)
		{
			$builddir = GetBuildDir($program)
			$version = GetVersion($program)
			$githubref = $env:GITHUB_REF.Split('/')
			$version = $version.Split('-')[0]
			$shortsha=$env:GITHUB_SHA.SubString(0,7)
			if ($githubref[1] -eq 'heads' -and $githubref[2] -eq 'dev')
			{
				$appvername = "AppVerName=`"$program $version-beta-$shortsha`""
				$version="${version}-beta-${shortsha}"
			}
			if ($githubref[1] -eq 'tags')
			{
				$verno = $githubref[2].Split('-')[0]
				$refdate = $githubref[2].Split('-')[1]
				$major = $verno.Split('.')[0]
				$minor = $verno.Split('.')[1]
				$release = $verno.Split('.')[2]
				if ($major -ne 'v3' -or [string]::IsNullOrEmpty($minor) -or [string]::IsNullOrEmpty($release) -or [string]::IsNullOrEmpty($refdate))
				{
					Write-Host "Invalid Tag format. Must be v3.0.3-20200101010101. Refusing to build!"
					exit 1
				}
				$appvername = "AppVerName=`"$program $version-$refdate`""
				$version = $githubref[2]
			}
			Write-Host "$program version is now $version"
			Set-Content -Path "$builddir\Version.py" -Value "$appvername"
		}
		
	}
	
}
function BuildAll($programs)
{
	CheckPythonVersion
	CheckEnvActive
	if ($programs.Length -eq 0)
	{
		Write-Host "No programs selected. -cmgr, -cmgri, -cmgra, -trw, -smgr, -pts or -all required"
		exit 1
	}
	Cleanup
	updateVersion($programs)
	foreach ($program in $programs)
	{
		if (($program -eq "SeriesMgr") -or ($program -eq "CrossMgrVideo"))
		{
			FixSeriesMgrFiles($program)
		}
		CompileCode($program)
		doPyInstaller($program)
		CopyAssets($program)
		Package($program)
	}
}

function FixSeriesMgrFiles($program)
{
	Write-Host "Fixing dependencies for $program"
	$dependsfile = Get-Content "$program\Dependencies.py"
	Set-Location -Path "$program"
	foreach ($line in $dependsfile)
	{
		$file = $line.Split(' ')[1]
		Write-Host "Linking ..\${file}.py to ${file}.py"
		# We could do a symlink, but that requires developer mode. Ug
		#New-Item -Path "..\${file}.py" -ItemType SymbolicLink -Value "${file}.py"
		Copy-Item -Path "..\${file}.py" -Destination "${file}.py"
	}
	Set-Location -Path '..'
}

function Virustotal
{
	CheckPythonVersion
	CheckEnvActive
	Write-Host "Sending files to VirusTotal..."
	$files = Get-ChildItem -Path "release\*.exe"
	
	foreach ($file in $files)
	{
		Write-Host "Uploading $file to VirusTotal..."
		Start-Process -Wait -NoNewWindow -FilePath "python.exe" -ArgumentList "VirusTotalSubmit.py -v $file"
	}
		
}

function DoRelease
{
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "rev-parse --abbrev-ref HEAD --" -RedirectStandardOutput out.txt
	$text = Get-Content -Path out.txt
	Remove-Item 'out.txt'
	$current_branch = $text[0]
	if ($current_branch -ne 'dev')
	{
		Write-Host "Unable to do release on $current_branch. You must be on the dev branch to cut a release"
		exit 1
	}
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "diff-index HEAD --" -RedirectStandardOutput out.txt
	$changes = Get-Content -Path out.txt
	Remove-Item 'out.txt'
	if (![string]::IsNullOrEmpty($changes))
	{
		Write-Host "$current_branch has uncommitted changes. Refusing to release. Checkin your code."
		exit 1
	}
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "rev-parse $current_branch" -RedirectStandardOutput out.txt
	$text = Get-Content -Path out.txt
	Remove-Item 'out.txt'
	$local = $text
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "rev-parse origin/$current_branch" -RedirectStandardOutput out.txt
	$text = Get-Content -Path out.txt
	Remove-Item 'out.txt'
	$remote = $text
	Write-Host "$local vs $remote"
	if ($local -ne $remote)
	{
		Write-Host "$current_branch is not in sync with origin. Please push your changes."
		exit 1
	}
	
	$version = GetVersion('CrossMgr')
	$versionno = $version.Split('-')[0]
	$date = Get-Date -format "yyyyMMddHHmmss"
	$tagname = "v$versionno-$date"
	Write-Host "Tagging with $tagname"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "checkout master"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "merge dev -m `"Release $tagname`""
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "push"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "tag $tagname"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "push origin $tagname"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "checkout dev"
}

function TagRelease
{
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "rev-parse --abbrev-ref HEAD --" -RedirectStandardOutput out.txt
	$text = Get-Content -Path out.txt
	Remove-Item 'out.txt'
	$current_branch = $text[0]
	if ($current_branch -ne 'master')
	{
		Write-Host "Unable to do release on $current_branch. You must be on the master branch to tag a release"
		exit 1
	}
	$version = GetVersion('CrossMgr')
	$versionno = $version.Split('-')[0]
	$date = Get-Date -format "yyyyMMddHHmmss"
	$tagname = "v$versionno-$date"
	Write-Host "Tagging with $tagname"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "tag $tagname"
	Start-Process -Wait -NoNewWindow -FilePath "git.exe" -ArgumentList "push origin $tagname"
}

function doHelp
{
	Write-Host '
	compile.ps1 [-help]
	-help              - Help
	-environ [env]     - Use Environment ($env:VIRTUAL_ENV)
	-pythonexe [pythonexe]  - Python version (Default $pythonver)
	-cmgr        - Build CrossMgr
	-cmgri       - Build CrossMgrImpinj
	-trw         - Build TagReadWrite
	-smgr        - Build SeriesMgr
	-cmgra       - Build CrossMgrAlien
	-video       - Build CrossMgrVideo
	-cam         - Build CrossMgrCamera (NOT COMPLETE)
	-pts         - Build PointsRaceMgr
	-all         - Build all programs
	
	-checkver     - check python version
	-version      - Get versions
	-setupenv     - Setup environment
	-clean        - Clean up everything
	-compile      - Compile code
	-locale       - Build locale files
	-pyinstall    - Run pyinstaller
	-copy         - Copy Assets to dist directory
	-package      - Package application
	-everything   - Build everything and package
    -virus        - Send releases to VirusTotal
	-fix          - Fix SeriesMgr files
	
	-tag          - Tag for release
	
	To setup the build environment after a fresh checkout, use:
	compile.ps1 -setupenv
	
	To build all the applications and package them, use:
	compile.ps1 -all -everything
	'
	exit 1
}

if ($help -eq $true)
{
	doHelp
}

$programs = @()

if ($release -eq $true)
{
	doRelease
	exit 1
}

if ($tag -eq $true)
{
	tagRelease
	exit 1
}

if ($checkver)
{
	CheckPythonVersion
	exit 1
}

if ((($clean -eq $false) -and ($setupenv -eq $false) -and ($fix -eq $false)) -and
		($cmgr -eq $false) -and
		($cmgri -eq $false) -and
		($trw -eq $false) -and
		($smgr -eq $false) -and
		($cmgra -eq $false) -and
		($video -eq $false) -and
		($cam -eq $false) -and
		($pts -eq $false) -and
		($all -eq $false))
{
	Write-Host "You must specify a program to build or -all"
	doHelp
}

if ($cmgr -eq $true)
{
	$programs += 'CrossMgr'
}

if ($cmgri -eq $true)
{
	$programs += 'CrossMgrImpinj'
}

if ($trw -eq $true)
{
	$programs += 'TagReadWrite'
}

if ($smgr -eq $true)
{
	$programs += 'SeriesMgr'
}
if ($cmgra -eq $true)
{
	$programs += 'CrossMgrAlien'
}
if ($video -eq $true)
{
	$programs += 'CrossMgrVideo'
}
if ($cam -eq $true)
{
	Write-Host "CrossMgrCamera has not been ported to Python 3 and currently is not supported"
	exit 1
	#$programs += 'CrossMgrCamera'
}
if ($pts -eq $true)
{
	$programs += 'PointsRaceMgr'
}
if ($all -eq $true)
{
	$programs = @(
		'CrossMgr',
		'CrossMgrImpinj',
		'TagReadWrite',
		'SeriesMgr',
		'CrossMgrAlien',
		'CrossMgrVideo',
		'PointsRaceMgr'
		)
}
if ($setupenv -eq $true)
{
	EnvSetup
}

if ($fixsmgr -eq $true)
{
	FixSeriesMgrFiles("SeriesMgr")
	FixSeriesMgrFiles("CrossMgrVideo")
#	FixSeriesMgrFiles("CrossMgrCamera")
}

if ($clean -eq $true)
{
	Cleanup
}

if ($everything -eq $false)
{
	if ($versioncmd -eq $true)
	{
		foreach ($program in $programs)
		{
			$version = GetVersion($program)
		}
	}
	if ($compile -eq $true)
	{
		foreach ($program in $programs)
		{
			CompileCode($program)
		}
	}
	if ($locale -eq $true)
	{
		foreach ($program in $programs)
		{
			BuildLocale($program)
		}
	}
	if ($pyinst -eq $true)
	{
		foreach ($program in $programs)
		{
			doPyInstaller($program)
		}
	}
	if ($copyasset -eq $true)
	{
		foreach ($program in $programs)
		{
			CopyAssets($program)
		}
	}
	if ($package -eq $true)
	{
		foreach ($program in $programs)
		{
			Package($program)
		}
	}
	if ($updatever -eq $true)
	{
		updateVersion($programs)
	}
}
else
{
	BuildAll($programs)
}
if ($virus -eq $true)
{
	Virustotal
}

