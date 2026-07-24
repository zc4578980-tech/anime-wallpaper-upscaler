$ErrorActionPreference = "Stop"

python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
Write-Host "Python dependencies installed. Configure REALESRGAN_TOOL_DIR before running the skill."
