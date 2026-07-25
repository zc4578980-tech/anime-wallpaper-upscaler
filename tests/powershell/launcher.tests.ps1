$ErrorActionPreference = "Stop"
$env:AUPS_TESTING = "1"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
. (Join-Path $projectRoot "scripts\run-wallpaper.ps1")

function Assert-SequenceEqual {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Expected,

        [Parameter(Mandatory = $true)]
        [string[]]$Actual,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    if ($Expected.Count -ne $Actual.Count) {
        throw "FAIL: $Message (expected $($Expected.Count) arguments, got $($Actual.Count))"
    }
    for ($index = 0; $index -lt $Expected.Count; $index++) {
        if ($Expected[$index] -cne $Actual[$index]) {
            throw "FAIL: $Message (argument $index expected '$($Expected[$index])', got '$($Actual[$index])')"
        }
    }
    Write-Host "PASS: $Message"
}

try {
    $paths = @(
        "D:\Wallpapers\first image.png",
        "D:\Wallpapers\folder with spaces"
    )

    $arguments = @(ConvertTo-CliArguments -Paths $paths -Scale 3)
    Assert-SequenceEqual `
        -Expected @(
            "--input", $paths[0],
            "--input", $paths[1],
            "--scale", "3"
        ) `
        -Actual $arguments `
        -Message "multiple dropped paths remain intact and scale is emitted once"

    $quietArguments = @(ConvertTo-CliArguments -Paths $paths -Scale 3 -NoOpenOutput)
    Assert-SequenceEqual `
        -Expected @(
            "--input", $paths[0],
            "--input", $paths[1],
            "--scale", "3",
            "--no-open-output"
        ) `
        -Actual $quietArguments `
        -Message "no-open-output is emitted only when requested"
}
finally {
    Remove-Item Env:AUPS_TESTING -ErrorAction SilentlyContinue
}
