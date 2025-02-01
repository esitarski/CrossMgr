. .\Scripts\utils.ps1

function GetVersionFilePath($program)
{
	RequireProgram($program)
	$builddir = GetBuildDir($program)
	$VersionFilePath = "$builddir/Version.py"
	return $VersionFilePath
}

function GetVersionFileContents($program)
{
	RequireProgram($program)
	$VersionFile = GetVersionFilePath($program)
	if (!(Test-Path -Path $VersionFile))
	{
		Get-PSCallStack
		Write-Host "No version file at ", $VersionFile,". Aborting..."
		exit 1
	}

	$versionItem = Get-Content $VersionFile
	if ([string]::IsNullOrEmpty($versionItem))
	{
		Get-PSCallStack
		Write-Host "Version file at", $VersionFile, "is empty. Aborting..."
		exit 1
	}
	return $versionItem
}

function GetVersion($program)
{
	RequireProgram($program)
	$versionItem = GetVersionFileContents($program)
	$version = $versionItem.Split(' ')[1].Replace("`"", "")
	return $version
}

function WriteVersionFile($program, $appVersionString)
{
	if ([string]::IsNullOrEmpty($appVersionString))
	{
		Write-Host "No version string for program", $program, ". Aborting..."
		Get-PSCallStack
		exit 1
	}
	$VersionFile = GetVersionFilePath($program)

	$appvername = "AppVerName=`"$program $appVersionString`""
	Write-Host "Writing", $appvername,"to version file", $VersionFile

	Set-Content -Path $VersionFile -Value $appvername
}

function updateProgramVersion($program) {
	RequireProgram($program)
	$version = GetVersion($program)
	if ([string]::IsNullOrEmpty($version))
	{
		Write-Host "Failed getting version for", $program,". Aborting..."
		exit 1
	}
	if (IsDevelopmentBranch) {
		$shortsha=$env:GITHUB_SHA.SubString(0,7)
		$appVersionString="${version}-beta-${shortsha}"
		Write-Host "Updating version of", $program, "from development branch to", $appVersionString
	} elseif (IsTag) {
		$refdate = ValidateTag
		$appVersionString="${version}-${refdate}"
		Write-Host "Updating version of", $program, "from tag to", $version
	} else {
		Write-Host "Not a development branch or tag. Using version", $version
		$appVersionString = $version
	}
	WriteVersionFile $program $appVersionString
}

function updateVersion($programs)
{
	if ($programs.Length -eq 0)
	{
		Write-Host "No programs selected"
		exit 1
	}
	if ([string]::IsNullOrEmpty($env:GITHUB_REF))
	{
		Write-Host "No GITHUB_REF - not updating versions."
		return 0
	}

	Write-Host "GITHUB_REF=$env:GITHUB_REF"
	foreach ($program in $programs)
	{
		updateProgramVersion $program
	}
}
