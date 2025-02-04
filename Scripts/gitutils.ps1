. .\Scripts\utils.ps1

function IsDevelopmentBranch() {
	$githubref = $env:GITHUB_REF.Split('/')
    $refs = $githubref[1].ToLower()
	if ($refs -ne 'heads') {
        Write-Debug "Refs is not heads", $refs
		return $false
	}
	$branchName = $githubref[2]

    if ( [string]::IsNullOrEmpty($branchName)) {
        return $false
    }
    $allowed = @(
        'dev',
        'develop',
        'fix'
    )
    if ( $allowed -contains $branchName.ToLower() ) {
        return $true
    }

    return $false
}

function IsTag() {
	$githubref = $env:GITHUB_REF.Split('/')
	if ($githubref[1].ToLower() -ne 'tags') {
		return $false
	}
	return $true
}
