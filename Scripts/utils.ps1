function RequireProgram($program)
{
	if ( [string]::IsNullOrEmpty($program) ) {
		Get-PSCallStack
		Write-Host "No program specified. Aborting..."
		exit 1
	}
}

function GetBuildDir($program)
{
	RequireProgram($program)
	$builddir = '.'
	if ($program -ne 'CrossMgr')
	{
		$builddir = $program
	}
	return $builddir
}
