$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$python = Join-Path $root ".tools\python\python.exe"

if (-not (Test-Path $python)) {
  Write-Host "Embedded Python not found. Bootstrapping..."
  New-Item -ItemType Directory -Force -Path ".tools\python" | Out-Null
  $zipPath = ".tools\python\python-embed.zip"
  Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip" -OutFile $zipPath
  Expand-Archive -Path $zipPath -DestinationPath ".tools\python" -Force
  Remove-Item $zipPath

  $pth = Get-ChildItem ".tools\python" -Filter "python*._pth" | Select-Object -First 1
  (Get-Content $pth.FullName) -replace "^#import site", "import site" | Set-Content $pth.FullName

  Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile ".tools\python\get-pip.py"
  & $python ".tools\python\get-pip.py"
  & $python -m pip install -r "requirements.txt"
}

Write-Host "Starting Tariff Refund AI at http://127.0.0.1:8000"
& $python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
