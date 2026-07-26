$ErrorActionPreference = "Stop"

& (Join-Path $PSScriptRoot "setup.ps1") @args
exit $LASTEXITCODE
