# Nanakwaku Boateng Boakye-Akyeampong | 10022200167
# Part A — Config B: PDF windows 800 chars, overlap 100 (smaller windows)
# Usage: .\run_streamlit_config_b.ps1
# Stop any running Streamlit first (Ctrl+C), then run this from the project folder.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$env:PDF_CHUNK_CHARS = "800"
$env:PDF_CHUNK_OVERLAP = "100"

Write-Host "Using PDF_CHUNK_CHARS=$env:PDF_CHUNK_CHARS PDF_CHUNK_OVERLAP=$env:PDF_CHUNK_OVERLAP"
Write-Host "In the app: enable 'Rebuild search index' and click 'Reload index' after start."
Write-Host ""

$st = Join-Path $PSScriptRoot ".venv\Scripts\streamlit.exe"
if (-not (Test-Path $st)) {
    Write-Error "Missing .venv. Run: python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt"
}
& $st run ca_10022200167.py
