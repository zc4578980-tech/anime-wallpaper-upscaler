$ErrorActionPreference = "Stop"
$env:AUPS_TESTING = "1"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
. (Join-Path $projectRoot "setup.ps1")

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

function Assert-Equal {
    param(
        [Parameter(Mandatory = $true)]
        $Expected,

        [Parameter(Mandatory = $true)]
        $Actual,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    if ($Expected -ne $Actual) {
        throw "FAIL: $Message (expected '$Expected', got '$Actual')"
    }
    Write-Host "PASS: $Message"
}

function Assert-Throws {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$Action,

        [Parameter(Mandatory = $true)]
        [string]$Message
    )

    try {
        & $Action
    }
    catch {
        Write-Host "PASS: $Message"
        return
    }
    throw "FAIL: $Message (no exception was raised)"
}

function New-TestManifest {
    param(
        [Parameter(Mandatory = $true)]
        [byte[]]$Content,

        [string[]]$RequiredFiles = @("realesrgan-ncnn-vulkan.exe")
    )

    $contentPath = Join-Path $script:testRoot "expected.bin"
    [System.IO.File]::WriteAllBytes($contentPath, $Content)
    return [pscustomobject]@{
        assetUrl = "https://example.invalid/runtime.zip"
        assetName = "runtime.zip"
        assetSize = $Content.Length
        sha256 = (Get-FileHash -LiteralPath $contentPath -Algorithm SHA256).Hash.ToLowerInvariant()
        installDirectory = "runtime"
        requiredFiles = $RequiredFiles
    }
}

$script:testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("aups-setup-tests-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $script:testRoot | Out-Null

try {
    $expectedContent = [byte[]](1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
    $manifest = New-TestManifest -Content $expectedContent
    $downloads = Join-Path $script:testRoot "network\downloads"
    $partialPath = Join-Path $downloads "runtime.zip.partial"

    $interruptedRequest = {
        param($Uri, $Destination, $ResumeFrom)
        [System.IO.Directory]::CreateDirectory((Split-Path -Parent $Destination)) | Out-Null
        [System.IO.File]::WriteAllBytes($Destination, [byte[]](1, 2, 3, 4))
        throw "simulated network interruption"
    }
    Assert-Throws -Message "network interruption reports failure" -Action {
        Get-VerifiedUpstreamArchive -Manifest $manifest -DownloadsDirectory $downloads -RequestInvoker $interruptedRequest -MaximumAttempts 1
    }
    Assert-True (Test-Path -LiteralPath $partialPath -PathType Leaf) "undersized partial is retained"
    Assert-Equal 4 (Get-Item -LiteralPath $partialPath).Length "retained partial stays bounded"

    $script:observedResume = -1
    $resumedRequest = {
        param($Uri, $Destination, $ResumeFrom)
        $script:observedResume = $ResumeFrom
        $stream = [System.IO.File]::Open($Destination, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write)
        try {
            $remaining = [byte[]](5, 6, 7, 8, 9, 10)
            $stream.Write($remaining, 0, $remaining.Length)
        }
        finally {
            $stream.Dispose()
        }
        return 206
    }
    $archive = Get-VerifiedUpstreamArchive -Manifest $manifest -DownloadsDirectory $downloads -RequestInvoker $resumedRequest -MaximumAttempts 1
    Assert-Equal 4 $script:observedResume "retry resumes from the retained byte count"
    Assert-Equal (Join-Path $downloads "runtime.zip") $archive "verified partial is promoted to a ZIP archive"
    Assert-True (-not (Test-Path -LiteralPath $partialPath)) "verified partial no longer remains"
    Assert-Equal $manifest.sha256 (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() "resumed archive passes SHA-256 verification"

    $sizeDownloads = Join-Path $script:testRoot "size\downloads"
    New-Item -ItemType Directory -Path $sizeDownloads -Force | Out-Null
    $sizePartial = Join-Path $sizeDownloads "runtime.zip.partial"
    [System.IO.File]::WriteAllBytes($sizePartial, [byte[]](0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
    Assert-Throws -Message "oversized archive is rejected" -Action {
        Get-VerifiedUpstreamArchive -Manifest $manifest -DownloadsDirectory $sizeDownloads -RequestInvoker { throw "must not download" } -MaximumAttempts 1
    }
    Assert-True (-not (Test-Path -LiteralPath $sizePartial)) "oversized archive is deleted"

    $digestDownloads = Join-Path $script:testRoot "digest\downloads"
    New-Item -ItemType Directory -Path $digestDownloads -Force | Out-Null
    $digestPartial = Join-Path $digestDownloads "runtime.zip.partial"
    [System.IO.File]::WriteAllBytes($digestPartial, [byte[]](10, 9, 8, 7, 6, 5, 4, 3, 2, 1))
    Assert-Throws -Message "digest-mismatched archive is rejected" -Action {
        Get-VerifiedUpstreamArchive -Manifest $manifest -DownloadsDirectory $digestDownloads -RequestInvoker { throw "must not download" } -MaximumAttempts 1
    }
    Assert-True (-not (Test-Path -LiteralPath $digestPartial)) "digest-mismatched archive is deleted"

    $zipSource = Join-Path $script:testRoot "zip-source"
    $zipDownloads = Join-Path $script:testRoot "zip-install\tools\.downloads"
    New-Item -ItemType Directory -Path $zipSource, $zipDownloads -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $zipSource "realesrgan-ncnn-vulkan.exe") -Value "test executable"
    $sourceZip = Join-Path $script:testRoot "source-runtime.zip"
    Compress-Archive -Path (Join-Path $zipSource "*") -DestinationPath $sourceZip
    $zipBytes = [System.IO.File]::ReadAllBytes($sourceZip)
    $zipManifest = New-TestManifest -Content $zipBytes
    $zipToolRoot = Join-Path $script:testRoot "zip-install\tools"
    $zipRequest = {
        param($Uri, $Destination, $ResumeFrom)
        [System.IO.File]::WriteAllBytes($Destination, $zipBytes)
        return 200
    }
    $zipInstall = Install-UpstreamRuntime -Manifest $zipManifest -ToolRoot $zipToolRoot -RequestInvoker $zipRequest
    Assert-True (Test-Path -LiteralPath (Join-Path $zipInstall "realesrgan-ncnn-vulkan.exe") -PathType Leaf) "verified ZIP extracts through the staging install"
    Assert-True (-not (Test-Path -LiteralPath (Join-Path $zipToolRoot ".runtime.staging"))) "staging directory is removed after atomic install"

    $toolRoot = Join-Path $script:testRoot "existing\tools"
    $runtimeRoot = Join-Path $toolRoot "runtime"
    New-Item -ItemType Directory -Path $runtimeRoot -Force | Out-Null
    Set-Content -LiteralPath (Join-Path $runtimeRoot "realesrgan-ncnn-vulkan.exe") -Value "existing"
    $before = (Get-Item -LiteralPath (Join-Path $runtimeRoot "realesrgan-ncnn-vulkan.exe")).LastWriteTimeUtc
    $installed = Install-UpstreamRuntime -Manifest $manifest -ToolRoot $toolRoot -RequestInvoker { throw "valid install must not download" }
    Assert-Equal $runtimeRoot $installed "valid existing runtime is reused"
    Assert-Equal $before (Get-Item -LiteralPath (Join-Path $runtimeRoot "realesrgan-ncnn-vulkan.exe")).LastWriteTimeUtc "valid existing runtime is untouched"

    $modelManifest = [pscustomobject]@{
        requiredFiles = @(
            "realesrgan-ncnn-vulkan.exe",
            "models/realesr-animevideov3-x2.param",
            "models/realesr-animevideov3-x2.bin",
            "models/realesr-animevideov3-x3.param",
            "models/realesr-animevideov3-x3.bin",
            "models/realesrgan-x4plus-anime.param",
            "models/realesrgan-x4plus-anime.bin"
        )
    }
    $modelRuntime = Join-Path $script:testRoot "model-validation"
    foreach ($relativePath in $modelManifest.requiredFiles) {
        $requiredPath = Join-Path $modelRuntime $relativePath
        New-Item -ItemType Directory -Path (Split-Path -Parent $requiredPath) -Force | Out-Null
        Set-Content -LiteralPath $requiredPath -Value "fixture"
    }
    Assert-True (Test-RuntimeInstall -InstallPath $modelRuntime -Manifest $modelManifest) "runtime is valid only after the executable and every pinned model file exist"
    Remove-Item -LiteralPath (Join-Path $modelRuntime "models/realesr-animevideov3-x3.bin") -Force
    Assert-True (-not (Test-RuntimeInstall -InstallPath $modelRuntime -Manifest $modelManifest)) "a missing pinned model invalidates the runtime and requires automatic repair"

    $script:observedWingetArguments = @()
    $expectedLauncher = [pscustomobject]@{
        Command = "C:\Users\Test\Python312\python.exe"
        PrefixArguments = @()
    }
    $installedLauncher = Install-PythonWithWinget `
        -Accepted `
        -WingetInvoker {
            param([string[]]$Arguments)
            $script:observedWingetArguments = @($Arguments)
            return 0
        } `
        -LauncherResolver { return $expectedLauncher }
    Assert-Equal $expectedLauncher.Command $installedLauncher.Command "winget bootstrap returns the newly installed Python launcher"
    Assert-True ($script:observedWingetArguments -contains "Python.Python.3.12") "winget bootstrap pins the official Python 3.12 package"
    Assert-True ($script:observedWingetArguments -contains "--scope") "winget bootstrap declares an installation scope"
    Assert-True ($script:observedWingetArguments -contains "user") "winget bootstrap installs Python for the current user"
    Assert-True ($script:observedWingetArguments -contains "--accept-package-agreements") "winget bootstrap accepts package agreements only after user consent"
    Assert-True ($script:observedWingetArguments -contains "--accept-source-agreements") "winget bootstrap accepts source agreements only after user consent"

    $cmdLauncher = [pscustomobject]@{
        Command = (Get-Command "cmd.exe").Source
        PrefixArguments = @("/d", "/c")
    }
    $warningWasRejected = $false
    try {
        Invoke-PythonLauncher `
            -Launcher $cmdLauncher `
            -Arguments @("echo benign pip warning 1>&2 & exit /b 0")
    }
    catch {
        $warningWasRejected = $true
    }
    Assert-True (-not $warningWasRejected) "native stderr warnings do not fail a successful Python command"
    Assert-Throws -Message "nonzero native exit code still fails a Python command" -Action {
        Invoke-PythonLauncher `
            -Launcher $cmdLauncher `
            -Arguments @("echo dependency failure 1>&2 & exit /b 7")
    }
    $global:LASTEXITCODE = 0

    $installerEntry = Get-Content -LiteralPath (Join-Path $projectRoot "install.cmd") -Raw
    Assert-True ($installerEntry -match "setup\.ps1") "double-click installer delegates to the reviewed PowerShell setup"
    Assert-True ($installerEntry -notmatch "AcceptUpstreamLicense") "double-click installer does not bypass upstream license confirmation"

    $source = Join-Path $script:testRoot "skill-source"
    $existingSource = Join-Path $script:testRoot "existing-skill-source"
    $destination = Join-Path $script:testRoot "skill-destination"
    New-Item -ItemType Directory -Path $source, $existingSource | Out-Null
    New-Item -ItemType Junction -Path $destination -Target $existingSource | Out-Null

    $skillWarnings = @()
    $skillResult = Install-AgentSkill `
        -ProjectRoot $source `
        -Destination $destination `
        -WarningVariable skillWarnings
    $preservedTarget = @((Get-Item -LiteralPath $destination -Force).Target) | Select-Object -First 1
    $preservedTarget = [System.IO.Path]::GetFullPath($preservedTarget).TrimEnd("\")
    Assert-True ($null -eq $skillResult) "a non-matching existing skill link is skipped without failing setup"
    Assert-Equal ([System.IO.Path]::GetFullPath($existingSource).TrimEnd("\")) $preservedTarget "the existing skill link target is preserved"
    Assert-True (($skillWarnings -join "`n") -match "kept unchanged") "the skipped skill registration explains that the existing path was preserved"

    $directoryDestination = Join-Path $script:testRoot "skill-directory"
    New-Item -ItemType Directory -Path $directoryDestination | Out-Null
    Set-Content -LiteralPath (Join-Path $directoryDestination "keep.txt") -Value "do not overwrite"
    Assert-Throws -Message "explicit replacement still refuses a non-junction skill path" -Action {
        Install-AgentSkill -ProjectRoot $source -Destination $directoryDestination -ReplaceSkillLink
    }
    Assert-True (Test-Path -LiteralPath (Join-Path $directoryDestination "keep.txt") -PathType Leaf) "a non-junction skill path is never overwritten"
}
finally {
    if (Test-Path -LiteralPath $script:testRoot) {
        Remove-Item -LiteralPath $script:testRoot -Recurse -Force
    }
    Remove-Item Env:AUPS_TESTING -ErrorAction SilentlyContinue
}
