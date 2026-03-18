# Run edge without activating venv (works when PowerShell blocks scripts)
$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = Join-Path $root "edge\.venv\Scripts\python.exe"

Set-Location (Join-Path $root "edge")
& $py -m src.main
