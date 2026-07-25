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

if ($env:AUPS_TESTING -ne "1") {
    $venvPython = Join-Path $script:ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        [Console]::Error.WriteLine("Run .\setup.ps1 first")
        exit 2
    }

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
