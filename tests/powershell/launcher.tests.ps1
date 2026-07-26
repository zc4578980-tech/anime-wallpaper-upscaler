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

function Assert-True {
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Condition,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    if (-not $Condition) {
        throw "FAIL: $Message"
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

    Assert-True ( (Resolve-ScaleAnswer -Answer " 2 ") -eq 2 ) "scale input ignores surrounding whitespace"
    Assert-True ( (Resolve-ScaleAnswer -Answer " ") -eq 4 ) "blank scale input defaults to 4"
    try {
        $null = Resolve-ScaleAnswer -Answer "5"
        throw "FAIL: invalid scale input must fail"
    }
    catch [System.Management.Automation.RuntimeException] {
        Assert-True ($_.Exception.Message -eq "Scale must be 2, 3, or 4.") "invalid scale input reports the existing repair message"
    }

    $testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("aups-launcher-tests-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory -Path $testRoot | Out-Null
    try {
        $manifestDirectory = Join-Path $testRoot "upstream"
        New-Item -ItemType Directory -Path $manifestDirectory | Out-Null
        $manifest = [ordered]@{
            installDirectory = "runtime"
            requiredFiles = @(
                "realesrgan-ncnn-vulkan.exe",
                "models/realesr-animevideov3-x3.param",
                "models/realesr-animevideov3-x3.bin"
            )
        }
        $manifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $manifestDirectory "realesrgan-windows.json")

        Assert-True (-not (Test-InstallationReady -ProjectRoot $testRoot)) "missing local Python and runtime require one-click setup"

        $script:setupCalls = 0
        $setupInvoker = {
            param([string]$ProjectRoot)
            $script:setupCalls++
            $venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
            New-Item -ItemType Directory -Path (Split-Path -Parent $venvPython) -Force | Out-Null
            Set-Content -LiteralPath $venvPython -Value "fixture"
            foreach ($relativePath in $manifest.requiredFiles) {
                $requiredPath = Join-Path (Join-Path $ProjectRoot "tools\runtime") $relativePath
                New-Item -ItemType Directory -Path (Split-Path -Parent $requiredPath) -Force | Out-Null
                Set-Content -LiteralPath $requiredPath -Value "fixture"
            }
            return 0
        }
        Ensure-InstallationReady -ProjectRoot $testRoot -SetupInvoker $setupInvoker
        Assert-True ($script:setupCalls -eq 1) "incomplete installation invokes setup exactly once"
        Assert-True (Test-InstallationReady -ProjectRoot $testRoot) "launcher revalidates Python, executable, and all models after setup"

        Remove-Item -LiteralPath (Join-Path $testRoot "tools\runtime\models\realesr-animevideov3-x3.bin") -Force
        Assert-True (-not (Test-InstallationReady -ProjectRoot $testRoot)) "missing model is detected before processing"
    }
    finally {
        if (Test-Path -LiteralPath $testRoot) {
            Remove-Item -LiteralPath $testRoot -Recurse -Force
        }
    }
}
finally {
    Remove-Item Env:AUPS_TESTING -ErrorAction SilentlyContinue
}
