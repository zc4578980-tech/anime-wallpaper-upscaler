[CmdletBinding()]
param(
    [switch]$AcceptUpstreamLicense,
    [switch]$SkipSkill,
    [switch]$SkipShortcut,
    [switch]$ReplaceSkillLink
)

$ErrorActionPreference = "Stop"
$script:ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$script:PythonRepair = @"
Install 64-bit Python 3.10 or newer from:
https://www.python.org/downloads/windows/
During installation, enable "Add python.exe to PATH", then open a new PowerShell window.
"@

function Assert-SupportedEnvironment {
    if ($PSVersionTable.PSVersion -lt [version]"5.1") {
        throw "PowerShell 5.1 or newer is required. Windows 10 and 11 include PowerShell 5.1."
    }
    if (-not $IsWindows -and $PSVersionTable.PSEdition -eq "Core") {
        throw "This installer supports 64-bit Windows 10 and 11 only."
    }
    if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
        throw "This installer supports 64-bit Windows 10 and 11 only."
    }
    if (-not [System.Environment]::Is64BitOperatingSystem -or -not [System.Environment]::Is64BitProcess) {
        throw "Run this installer in 64-bit Windows PowerShell on a 64-bit Windows installation."
    }
}

function Get-PythonLauncher {
    $candidates = @(
        [pscustomobject]@{ Command = "python.exe"; PrefixArguments = @() },
        [pscustomobject]@{ Command = "python"; PrefixArguments = @() },
        [pscustomobject]@{ Command = "py.exe"; PrefixArguments = @("-3") },
        [pscustomobject]@{ Command = "py"; PrefixArguments = @("-3") }
    )

    $seen = @{}
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Command -ErrorAction SilentlyContinue
        if ($null -eq $command) {
            continue
        }
        $commandPath = $command.Source
        if ([string]::IsNullOrWhiteSpace($commandPath) -or $seen.ContainsKey($commandPath)) {
            continue
        }
        $seen[$commandPath] = $true
        $probeArguments = @($candidate.PrefixArguments) + @(
            "-c",
            "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
        )
        & $commandPath @probeArguments *> $null
        if ($LASTEXITCODE -eq 0) {
            return [pscustomobject]@{
                Command = $commandPath
                PrefixArguments = @($candidate.PrefixArguments)
            }
        }
    }

    throw "Python 3.10 or newer was not found.`n$script:PythonRepair"
}

function Invoke-PythonLauncher {
    param(
        [Parameter(Mandatory = $true)]
        $Launcher,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $allArguments = @($Launcher.PrefixArguments) + $Arguments
    & $Launcher.Command @allArguments 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code ${LASTEXITCODE}: $($Arguments -join ' ')"
    }
}

function Install-PythonEnvironment {
    param(
        [Parameter(Mandatory = $true)]
        $Launcher,

        [string]$ProjectRoot = $script:ProjectRoot
    )

    $venvRoot = Join-Path $ProjectRoot ".venv"
    $venvPython = Join-Path $venvRoot "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
        Write-Host "Creating project Python environment at $venvRoot"
        Invoke-PythonLauncher -Launcher $Launcher -Arguments @("-m", "venv", $venvRoot) | Out-Host
    }

    & $venvPython -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "The existing .venv does not use Python 3.10 or newer. Remove '$venvRoot' and run setup.ps1 again.`n$script:PythonRepair"
    }

    $requirements = Join-Path $ProjectRoot "requirements.txt"
    Write-Host "Installing Python dependencies into the project environment"
    & $venvPython -m pip install --disable-pip-version-check -r $requirements 2>&1 | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "Python dependency installation failed. Check the network, then run .\setup.ps1 again."
    }
    return $venvPython
}

function Get-UpstreamManifest {
    param(
        [string]$ManifestPath = (Join-Path $script:ProjectRoot "upstream\realesrgan-windows.json")
    )

    if (-not (Test-Path -LiteralPath $ManifestPath -PathType Leaf)) {
        throw "Pinned upstream manifest is missing: $ManifestPath"
    }
    $manifest = Get-Content -LiteralPath $ManifestPath -Raw | ConvertFrom-Json
    foreach ($property in @("assetUrl", "assetName", "assetSize", "sha256", "installDirectory", "requiredFiles")) {
        if ($null -eq $manifest.$property) {
            throw "Pinned upstream manifest is missing '$property': $ManifestPath"
        }
    }
    if ($manifest.sha256 -notmatch "^[0-9a-f]{64}$") {
        throw "Pinned upstream SHA-256 must be 64 lowercase hexadecimal characters."
    }
    if ([int64]$manifest.assetSize -le 0) {
        throw "Pinned upstream asset size must be positive."
    }
    if ([System.IO.Path]::GetFileName([string]$manifest.assetName) -ne [string]$manifest.assetName) {
        throw "Pinned upstream asset name must not contain a path."
    }
    if ([System.IO.Path]::GetFileName([string]$manifest.installDirectory) -ne [string]$manifest.installDirectory) {
        throw "Pinned upstream install directory must not contain a path."
    }
    return $manifest
}

function Test-RuntimeInstall {
    param(
        [Parameter(Mandatory = $true)]
        [string]$InstallPath,

        [Parameter(Mandatory = $true)]
        $Manifest
    )

    if (-not (Test-Path -LiteralPath $InstallPath -PathType Container)) {
        return $false
    }
    foreach ($relativePath in @($Manifest.requiredFiles)) {
        if (-not (Test-Path -LiteralPath (Join-Path $InstallPath $relativePath) -PathType Leaf)) {
            return $false
        }
    }
    return $true
}

function Invoke-HttpDownload {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Uri,

        [Parameter(Mandatory = $true)]
        [string]$Destination,

        [int64]$ResumeFrom = 0
    )

    [System.Net.ServicePointManager]::SecurityProtocol =
        [System.Net.ServicePointManager]::SecurityProtocol -bor [System.Net.SecurityProtocolType]::Tls12
    $request = [System.Net.HttpWebRequest]::Create($Uri)
    $request.AllowAutoRedirect = $true
    $request.Timeout = 20000
    $request.ReadWriteTimeout = 60000
    $request.UserAgent = "anime-wallpaper-upscaler-setup/0.2.0"
    if ($ResumeFrom -gt 0) {
        $request.AddRange($ResumeFrom)
    }

    $response = $null
    $responseStream = $null
    $fileStream = $null
    try {
        $response = [System.Net.HttpWebResponse]$request.GetResponse()
        $statusCode = [int]$response.StatusCode
        $fileMode = [System.IO.FileMode]::Create
        if ($ResumeFrom -gt 0 -and $statusCode -eq 206) {
            $fileMode = [System.IO.FileMode]::Append
        }
        $responseStream = $response.GetResponseStream()
        $fileStream = [System.IO.File]::Open($Destination, $fileMode, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
        $responseStream.CopyTo($fileStream)
        return $statusCode
    }
    finally {
        if ($null -ne $fileStream) { $fileStream.Dispose() }
        if ($null -ne $responseStream) { $responseStream.Dispose() }
        if ($null -ne $response) { $response.Dispose() }
    }
}

function Get-DownloadRepairMessage {
    param(
        [Parameter(Mandatory = $true)]
        $Manifest,

        [Parameter(Mandatory = $true)]
        [string]$PartialPath
    )

    return "Download failed. Check the network and run .\setup.ps1 again.`nOfficial URL: $($Manifest.assetUrl)`nResume file: $PartialPath"
}

function Get-VerifiedUpstreamArchive {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        $Manifest,

        [Parameter(Mandatory = $true)]
        [string]$DownloadsDirectory,

        [scriptblock]$RequestInvoker,

        [ValidateRange(1, 10)]
        [int]$MaximumAttempts = 3
    )

    if ($null -eq $RequestInvoker) {
        $RequestInvoker = ${function:Invoke-HttpDownload}
    }
    New-Item -ItemType Directory -Path $DownloadsDirectory -Force | Out-Null
    $partialPath = Join-Path $DownloadsDirectory ($Manifest.assetName + ".partial")
    $archivePath = Join-Path $DownloadsDirectory $Manifest.assetName
    $expectedSize = [int64]$Manifest.assetSize

    if (Test-Path -LiteralPath $archivePath -PathType Leaf) {
        $cachedSize = (Get-Item -LiteralPath $archivePath).Length
        $cachedDigest = $null
        if ($cachedSize -eq $expectedSize) {
            $cachedDigest = (Get-FileHash -LiteralPath $archivePath -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        if ($cachedSize -eq $expectedSize -and $cachedDigest -eq [string]$Manifest.sha256) {
            return $archivePath
        }
        Remove-Item -LiteralPath $archivePath -Force
        throw "Cached archive does not match the pinned official size and SHA-256. Corrupt data was deleted."
    }

    for ($attempt = 1; $attempt -le $MaximumAttempts; $attempt++) {
        $currentSize = 0L
        if (Test-Path -LiteralPath $partialPath -PathType Leaf) {
            $currentSize = (Get-Item -LiteralPath $partialPath).Length
        }
        if ($currentSize -gt $expectedSize) {
            Remove-Item -LiteralPath $partialPath -Force
            throw "Downloaded archive exceeds the pinned size ($currentSize > $expectedSize bytes). Corrupt data was deleted."
        }
        if ($currentSize -eq $expectedSize) {
            $actualDigest = (Get-FileHash -LiteralPath $partialPath -Algorithm SHA256).Hash.ToLowerInvariant()
            if ($actualDigest -ne [string]$Manifest.sha256) {
                Remove-Item -LiteralPath $partialPath -Force
                throw "Downloaded archive SHA-256 does not match the pinned official asset. Corrupt data was deleted."
            }
            Move-Item -LiteralPath $partialPath -Destination $archivePath
            return $archivePath
        }

        try {
            Write-Host "Downloading official Real-ESRGAN runtime (attempt $attempt/$MaximumAttempts, byte $currentSize)"
            $null = & $RequestInvoker -Uri $Manifest.assetUrl -Destination $partialPath -ResumeFrom $currentSize
        }
        catch {
            $failure = $_
            if (Test-Path -LiteralPath $partialPath -PathType Leaf) {
                $failedSize = (Get-Item -LiteralPath $partialPath).Length
                if ($failedSize -gt $expectedSize) {
                    Remove-Item -LiteralPath $partialPath -Force
                    throw "Downloaded archive exceeds the pinned size after a network failure. Corrupt data was deleted."
                }
                if ($failedSize -eq $expectedSize) {
                    $failedDigest = (Get-FileHash -LiteralPath $partialPath -Algorithm SHA256).Hash.ToLowerInvariant()
                    if ($failedDigest -eq [string]$Manifest.sha256) {
                        Move-Item -LiteralPath $partialPath -Destination $archivePath
                        return $archivePath
                    }
                    Remove-Item -LiteralPath $partialPath -Force
                    throw "Downloaded archive SHA-256 does not match after a network failure. Corrupt data was deleted."
                }
            }
            if ($attempt -eq $MaximumAttempts) {
                throw "$(Get-DownloadRepairMessage -Manifest $Manifest -PartialPath $partialPath)`nNetwork error: $($failure.Exception.Message)"
            }
            Write-Warning "Download interrupted; the bounded partial will be retried. $($failure.Exception.Message)"
            continue
        }

        if (-not (Test-Path -LiteralPath $partialPath -PathType Leaf)) {
            if ($attempt -eq $MaximumAttempts) {
                throw (Get-DownloadRepairMessage -Manifest $Manifest -PartialPath $partialPath)
            }
            continue
        }
        $downloadedSize = (Get-Item -LiteralPath $partialPath).Length
        if ($downloadedSize -gt $expectedSize) {
            Remove-Item -LiteralPath $partialPath -Force
            throw "Downloaded archive exceeds the pinned size ($downloadedSize > $expectedSize bytes). Corrupt data was deleted."
        }
        if ($downloadedSize -lt $expectedSize) {
            if ($attempt -eq $MaximumAttempts) {
                throw "$(Get-DownloadRepairMessage -Manifest $Manifest -PartialPath $partialPath)`nReceived $downloadedSize of $expectedSize bytes."
            }
            Write-Warning "Download is incomplete; retrying from byte $downloadedSize."
            continue
        }

        $digest = (Get-FileHash -LiteralPath $partialPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($digest -ne [string]$Manifest.sha256) {
            Remove-Item -LiteralPath $partialPath -Force
            throw "Downloaded archive SHA-256 does not match the pinned official asset. Corrupt data was deleted."
        }
        Move-Item -LiteralPath $partialPath -Destination $archivePath
        return $archivePath
    }

    throw (Get-DownloadRepairMessage -Manifest $Manifest -PartialPath $partialPath)
}

function Install-UpstreamRuntime {
    [CmdletBinding()]
    param(
        $Manifest = (Get-UpstreamManifest),

        [string]$ToolRoot = (Join-Path $script:ProjectRoot "tools"),

        [scriptblock]$RequestInvoker
    )

    $finalPath = Join-Path $ToolRoot $Manifest.installDirectory
    if (Test-RuntimeInstall -InstallPath $finalPath -Manifest $Manifest) {
        Write-Host "Official Real-ESRGAN runtime is already installed and valid: $finalPath"
        return $finalPath
    }

    $downloadsDirectory = Join-Path $ToolRoot ".downloads"
    $downloadArguments = @{
        Manifest = $Manifest
        DownloadsDirectory = $downloadsDirectory
    }
    if ($null -ne $RequestInvoker) {
        $downloadArguments.RequestInvoker = $RequestInvoker
    }
    $archivePath = Get-VerifiedUpstreamArchive @downloadArguments

    New-Item -ItemType Directory -Path $ToolRoot -Force | Out-Null
    $stagingPath = Join-Path $ToolRoot ("." + $Manifest.installDirectory + ".staging")
    if (Test-Path -LiteralPath $stagingPath) {
        Remove-Item -LiteralPath $stagingPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $stagingPath | Out-Null

    try {
        Expand-Archive -LiteralPath $archivePath -DestinationPath $stagingPath -Force
        if (-not (Test-RuntimeInstall -InstallPath $stagingPath -Manifest $Manifest)) {
            $missing = @($Manifest.requiredFiles | Where-Object {
                -not (Test-Path -LiteralPath (Join-Path $stagingPath $_) -PathType Leaf)
            })
            throw "The verified archive is missing required runtime files after extraction: $($missing -join ', ')"
        }

        $backupPath = $null
        if (Test-Path -LiteralPath $finalPath) {
            $backupPath = $finalPath + ".invalid-" + (Get-Date -Format "yyyyMMdd-HHmmss")
            Move-Item -LiteralPath $finalPath -Destination $backupPath
            Write-Warning "The incomplete previous runtime was preserved at: $backupPath"
        }
        try {
            Move-Item -LiteralPath $stagingPath -Destination $finalPath
        }
        catch {
            if ($null -ne $backupPath -and -not (Test-Path -LiteralPath $finalPath)) {
                Move-Item -LiteralPath $backupPath -Destination $finalPath
            }
            throw
        }
    }
    catch {
        if (Test-Path -LiteralPath $stagingPath) {
            Remove-Item -LiteralPath $stagingPath -Recurse -Force
        }
        throw
    }

    Write-Host "Installed the verified official Real-ESRGAN runtime: $finalPath"
    return $finalPath
}

function Confirm-UpstreamLicenseNotice {
    param(
        [switch]$Accepted,
        [string]$ProjectRoot = $script:ProjectRoot
    )

    $noticePath = Join-Path $ProjectRoot "THIRD_PARTY_NOTICES.md"
    if (-not (Test-Path -LiteralPath $noticePath -PathType Leaf)) {
        throw "Third-party notice is missing: $noticePath"
    }
    Write-Host ""
    Get-Content -LiteralPath $noticePath | Write-Host
    Write-Host ""
    if ($Accepted) {
        Write-Host "Upstream license notice accepted by -AcceptUpstreamLicense."
        return
    }
    $answer = Read-Host "Download the official runtime under these upstream terms? [Y/N]"
    if ($answer -notmatch "^[Yy]$") {
        throw "Setup cancelled. No upstream runtime was downloaded."
    }
}

function Install-AgentSkill {
    [CmdletBinding()]
    param(
        [string]$ProjectRoot = $script:ProjectRoot,
        [string]$Destination = (Join-Path $HOME ".codex\skills\anime-wallpaper-upscale"),
        [switch]$ReplaceSkillLink
    )

    $sourcePath = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd("\")
    if (-not (Test-Path -LiteralPath (Join-Path $sourcePath "SKILL.md") -PathType Leaf) -and $env:AUPS_TESTING -ne "1") {
        throw "Skill source is missing SKILL.md: $sourcePath"
    }
    $destinationPath = [System.IO.Path]::GetFullPath($Destination).TrimEnd("\")
    if (Test-Path -LiteralPath $destinationPath) {
        $existing = Get-Item -LiteralPath $destinationPath -Force
        $target = @($existing.Target) | Select-Object -First 1
        if (-not [string]::IsNullOrWhiteSpace($target)) {
            if (-not [System.IO.Path]::IsPathRooted($target)) {
                $target = Join-Path (Split-Path -Parent $destinationPath) $target
            }
            $target = [System.IO.Path]::GetFullPath($target).TrimEnd("\")
        }
        if ($target -and [string]::Equals($target, $sourcePath, [System.StringComparison]::OrdinalIgnoreCase)) {
            Write-Host "Codex skill link is already correct: $destinationPath"
            return $destinationPath
        }
        if (-not $ReplaceSkillLink) {
            throw "Codex skill destination already exists and was not changed.`nExisting: $destinationPath`nRequested target: $sourcePath`nUse -ReplaceSkillLink only after confirming the existing path is a replaceable junction."
        }
        if (-not ($existing.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            throw "Refusing to remove a non-junction skill path: $destinationPath. Move it manually if replacement is intended."
        }
        Remove-Item -LiteralPath $destinationPath -Force
    }

    New-Item -ItemType Directory -Path (Split-Path -Parent $destinationPath) -Force | Out-Null
    New-Item -ItemType Junction -Path $destinationPath -Target $sourcePath | Out-Null
    Write-Host "Installed Codex skill junction: $destinationPath -> $sourcePath"
    return $destinationPath
}

function New-DesktopShortcut {
    [CmdletBinding()]
    param(
        [string]$ProjectRoot = $script:ProjectRoot,
        [string]$Destination = (Join-Path ([System.Environment]::GetFolderPath("Desktop")) "Anime Wallpaper Upscaler.lnk")
    )

    $launcher = Join-Path $ProjectRoot "scripts\run-wallpaper.cmd"
    if (-not (Test-Path -LiteralPath $launcher -PathType Leaf)) {
        Write-Warning "Drag-and-drop launcher is not present yet; desktop shortcut creation was skipped."
        return $null
    }
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($Destination)
    $shortcut.TargetPath = $launcher
    $shortcut.WorkingDirectory = $ProjectRoot
    $shortcut.Description = "Create screen-ready wallpapers with the official Real-ESRGAN runtime"
    $shortcut.Save()
    Write-Host "Created desktop shortcut: $Destination"
    return $Destination
}

function Invoke-Setup {
    [CmdletBinding()]
    param(
        [switch]$AcceptUpstreamLicense,
        [switch]$SkipSkill,
        [switch]$SkipShortcut,
        [switch]$ReplaceSkillLink
    )

    Assert-SupportedEnvironment
    $launcher = Get-PythonLauncher
    Confirm-UpstreamLicenseNotice -Accepted:$AcceptUpstreamLicense
    $venvPython = Install-PythonEnvironment -Launcher $launcher
    $null = Install-UpstreamRuntime
    if (-not $SkipSkill) {
        $null = Install-AgentSkill -ReplaceSkillLink:$ReplaceSkillLink
    }
    if (-not $SkipShortcut) {
        $null = New-DesktopShortcut
    }

    Write-Host "Running command-line smoke test"
    & $venvPython (Join-Path $script:ProjectRoot "scripts\upscale_wallpaper.py") --help
    if ($LASTEXITCODE -ne 0) {
        throw "Setup smoke test failed with exit code $LASTEXITCODE."
    }
    Write-Host "Setup complete. The official Real-ESRGAN runtime is ready."
}

if ($env:AUPS_TESTING -ne "1") {
    Invoke-Setup @PSBoundParameters
}
