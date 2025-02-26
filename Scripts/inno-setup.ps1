function GetProgramFilesDirs()
{
	$drives = (Get-PSDrive -PSProvider FileSystem | Where-Object Name -ne 'Temp').Root
	$searchProgramFilesDirs = @('Program Files', 'Program Files (x86)')
	$dirs = @()
	foreach ($drive in $drives)
	{
		foreach ($dir in $searchProgramFilesDirs)
		{
			$checkDir = "$drive\$dir\Inno Setup 6"
			if (Test-Path -Path $checkDir)
			{
				$dirs += $checkDir
			}
		}
	}
	return $dirs
}

function GetInnoRegistryDir()
{
	$apps=(Get-ChildItem HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\* | % { Get-ItemProperty $_.PsPath } | Select DisplayName, InstallLocation | Sort-Object Displayname -Descending)

	foreach ($app in $apps)
	{
		if ($app.DisplayName -like 'Inno Setup version 6*')
		{
			return $app.InstallLocation
		}
	}
	return $null
}

function GetInnoSearchDirs($printOutput)
{
	$searchDirs = @()

	# Scan the registry for innosetup 6.x
	$regpath = GetInnoRegistryDir
	if (![string]::IsNullOrEmpty($regpath))
	{
		if ($printOutput -eq $true)
		{
			Write-Host "InnoSetup 6 is defined in registry as installed at $regpath"
		}
		$searchDirs += $regpath
	}

	$pfdirs = GetProgramFilesDirs
	$searchDirs = $searchDirs + $pfdirs
	$searchDirs += "$env:LOCALAPPDATA\Programs\Inno Setup 6"
	$searchDirs += "$env:APPDATA\Programs\Inno Setup 6"
	return $searchDirs
}

function GetInnoDir()
{
	$searchDirs = GetInnoSearchDirs
	foreach ($innolocation in $searchDirs) {
		if (Test-Path -Path $innolocation) {
			return $innolocation
		}
	}
	return $null
}

function CheckInnoSetupAvailable($printFoundOutput)
{
	$innolocation = GetInnoDir
	if (![string]::IsNullOrEmpty($innolocation))
	{
		$inno = "${innolocation}\ISCC.exe"
		if (Test-Path -Path "$inno" -PathType Leaf)
		{
			if ($printFoundOutput -eq $true)
			{
				Write-Host "Found InnoSetup 6 installed at $innolocation"
			}
			return $inno
		}
	}

	Write-Host "Cant find Inno Setup 6.x! Is it installed? Aborting...."
	exit 1
}
