[CmdletBinding()]
param(
    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Paths
)

$ErrorActionPreference = "Stop"
$script:ProjectRoot = Split-Path -Parent $PSScriptRoot

function ConvertTo-CliArguments {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string[]]$Paths,

        [Parameter(Mandatory = $true)]
        [ValidateSet(2, 3, 4)]
        [int]$Scale,

        [switch]$NoOpenOutput
    )

    $arguments = @()
    foreach ($path in $Paths) {
        $arguments += "--input"
        $arguments += $path
    }
    $arguments += "--scale"
    $arguments += $Scale.ToString([System.Globalization.CultureInfo]::InvariantCulture)
    if ($NoOpenOutput) {
        $arguments += "--no-open-output"
    }
    return $arguments
}

function Test-InstallationReady {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectRoot
    )

    $venvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    $manifestPath = Join-Path $ProjectRoot "upstream\realesrgan-windows.json"
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf) -or
        -not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
        return $false
    }

    try {
        $manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
    }
    catch {
        return $false
    }
    if ([string]::IsNullOrWhiteSpace([string]$manifest.installDirectory) -or
        @($manifest.requiredFiles).Count -eq 0) {
        return $false
    }

    $runtimeRoot = Join-Path (Join-Path $ProjectRoot "tools") $manifest.installDirectory
    foreach ($relativePath in @($manifest.requiredFiles)) {
        if (-not (Test-Path -LiteralPath (Join-Path $runtimeRoot $relativePath) -PathType Leaf)) {
            return $false
        }
    }
    return $true
}

function Invoke-ProjectSetup {
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectRoot
    )

    $setup = Join-Path $ProjectRoot "setup.ps1"
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $setup 2>&1 | Out-Host
    return $LASTEXITCODE
}

function Ensure-InstallationReady {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ProjectRoot,

        [scriptblock]$SetupInvoker
    )

    if (Test-InstallationReady -ProjectRoot $ProjectRoot) {
        return
    }
    if ($null -eq $SetupInvoker) {
        $SetupInvoker = ${function:Invoke-ProjectSetup}
    }

    Write-Host "Required local components are missing or incomplete. Starting one-click setup."
    Write-Host "The setup downloads and verifies the official executable and models automatically."
    [int]$exitCode = & $SetupInvoker -ProjectRoot $ProjectRoot
    if ($exitCode -ne 0) {
        throw "One-click setup exited with code $exitCode."
    }
    if (-not (Test-InstallationReady -ProjectRoot $ProjectRoot)) {
        throw "Setup finished, but Python, the official executable, or a pinned model is still missing."
    }
}

if ($env:AUPS_TESTING -ne "1") {
    try {
        Ensure-InstallationReady -ProjectRoot $script:ProjectRoot
    }
    catch {
        [Console]::Error.WriteLine("One-click setup could not complete: $($_.Exception.Message)")
        [Console]::Error.WriteLine("Double-click install.cmd, then retry the same image or folder.")
        exit 2
    }
    $venvPython = Join-Path $script:ProjectRoot ".venv\Scripts\python.exe"

    $selectedPaths = @($Paths)
    if ($selectedPaths.Count -eq 0) {
        Add-Type -AssemblyName System.Windows.Forms
        $picker = New-Object System.Windows.Forms.OpenFileDialog
        try {
            $picker.Title = "Select wallpapers to upscale"
            $picker.Filter = "Supported images (*.jpg;*.jpeg;*.png;*.webp)|*.jpg;*.jpeg;*.png;*.webp|All files (*.*)|*.*"
            $picker.Multiselect = $true
            if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) {
                exit 0
            }
            $selectedPaths = @($picker.FileNames)
        }
        finally {
            $picker.Dispose()
        }
    }

    $scaleAnswer = Read-Host "Scale [2/3/4] (default 4)"
    if ([string]::IsNullOrWhiteSpace($scaleAnswer)) {
        $scale = 4
    }
    elseif ($scaleAnswer -match "^[234]$") {
        $scale = [int]$scaleAnswer
    }
    else {
        [Console]::Error.WriteLine("Scale must be 2, 3, or 4.")
        exit 2
    }

    $cli = Join-Path $script:ProjectRoot "scripts\upscale_wallpaper.py"
    $cliArguments = @(ConvertTo-CliArguments -Paths $selectedPaths -Scale $scale)
    & $venvPython $cli @cliArguments
    exit $LASTEXITCODE
}
