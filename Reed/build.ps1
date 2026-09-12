# Reed Mod - One-click Build & Deploy Script
# Usage:
#   .\build.ps1            Build DLL + deploy Reed and RitsuLib to game
#   .\build.ps1 -Pack     Build + pack PCK + deploy
#   .\build.ps1 -Debug    Use Debug config (default: Release)
#   .\build.ps1 -SkipBuild Skip build, deploy existing files only

param(
    [switch]$Pack,
    [switch]$Debug,
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"

# -- Path Configuration --
$ScriptDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$Sts2Dir     = "E:/Program Files/Steam/steamapps/common/Slay the Spire 2"
$ModsDir     = Join-Path $Sts2Dir "mods"
$ReedModDir  = Join-Path $ModsDir "Reed"
$RitsuModDir = Join-Path $ModsDir "STS2-RitsuLib"

# RitsuLib from NuGet cache
$RitsuNupkg    = "C:/Users/LXW/.nuget/packages/sts2.ritsulib/0.5.20"
$RitsuDll       = Join-Path $RitsuNupkg "lib/net9.0/STS2-RitsuLib.dll"
$RitsuManifest = Join-Path $RitsuNupkg "contentFiles/any/any/mod_manifest.json"

# Build config
$Config    = if ($Debug) { "Debug" } else { "Release" }
$OutputDll = Join-Path $ScriptDir ".godot/mono/temp/bin/$Config/Reed.dll"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Reed Mod - Build & Deploy" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Game dir: $Sts2Dir"
Write-Host "  Config:   $Config"
Write-Host ""

# -- Step 1: Build DLL --
if (-not $SkipBuild) {
    Write-Host "[1/4] Building DLL ($Config)..." -ForegroundColor Yellow
    $dotnet = "C:\Program Files\dotnet\dotnet.exe"
    & $dotnet build "$ScriptDir\Reed.csproj" -c $Config --no-incremental 2>&1 | ForEach-Object { Write-Host $_ }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build FAILED!" -ForegroundColor Red
        exit 1
    }
    Write-Host "  -> Build OK: $OutputDll" -ForegroundColor Green
} else {
    Write-Host "[1/4] Skipping build" -ForegroundColor DarkGray
}

# -- Step 2: Pack PCK (optional) --
if ($Pack) {
    Write-Host "[2/4] Packing PCK..." -ForegroundColor Yellow

    $props = Get-Content (Join-Path $ScriptDir "Directory.Build.props") -Raw
    $godotExe = $null
    if ($props -match '<GodotExe>(.+?)</GodotExe>') {
        $godotExe = $matches[1]
    }

    if (-not $godotExe -or -not (Test-Path $godotExe)) {
        Write-Host "  Godot/MegaDot not found, skipping PCK" -ForegroundColor DarkYellow
        Write-Host "  Set GodotExe path in Directory.Build.props" -ForegroundColor DarkYellow
    } else {
        # Redirect Godot's user profile paths to local dirs to avoid sandbox permission issues
        $godotDir = Split-Path -Parent $godotExe
        $env:APPDATA = Join-Path $godotDir "appdata"
        $env:LOCALAPPDATA = Join-Path $godotDir "localappdata"
        $env:USERPROFILE = Join-Path $godotDir "userprofile"
        foreach ($d in @($env:APPDATA, $env:LOCALAPPDATA, $env:USERPROFILE)) {
            if (-not (Test-Path $d)) {
                New-Item -ItemType Directory -Path $d -Force | Out-Null
            }
        }
        Push-Location $ScriptDir
        & $godotExe --headless --export-pack "Windows Desktop" "Reed.pck" 2>&1 | ForEach-Object { Write-Host $_ }
        $packResult = $LASTEXITCODE
        Pop-Location
        if ($packResult -ne 0) {
            Write-Host "  PCK pack FAILED!" -ForegroundColor Red
            exit 1
        }
        Write-Host "  -> PCK packed OK" -ForegroundColor Green
    }
} else {
    Write-Host "[2/4] Skipping PCK (use -Pack to enable)" -ForegroundColor DarkGray
}

# -- Step 3: Deploy Reed mod --
Write-Host "[3/4] Deploying Reed mod..." -ForegroundColor Yellow

# Clean target directory to remove stale files (prevents JSON scan errors)
if (Test-Path $ReedModDir) {
    Write-Host "  Cleaning old files in $ReedModDir..." -ForegroundColor DarkGray
    Get-ChildItem -Path $ReedModDir -Recurse -Force | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue
} else {
    New-Item -ItemType Directory -Path $ReedModDir -Force | Out-Null
    Write-Host "  Created: $ReedModDir" -ForegroundColor DarkGray
}

# Copy DLL
$dllSource = $null
if (Test-Path $OutputDll) {
    $dllSource = $OutputDll
} else {
    $debugDll = Join-Path $ScriptDir ".godot/mono/temp/bin/Debug/Reed.dll"
    if (Test-Path $debugDll) {
        $dllSource = $debugDll
        Write-Host "  (Using Debug build)" -ForegroundColor DarkGray
    }
}

if ($dllSource) {
    Copy-Item $dllSource (Join-Path $ReedModDir "Reed.dll") -Force
    Write-Host "  -> Reed.dll copied" -ForegroundColor Green
} else {
    Write-Host "  Reed.dll not found! Build first." -ForegroundColor Red
    exit 1
}

# Copy manifest
$reedJson = Join-Path $ScriptDir "Reed.json"
Copy-Item $reedJson (Join-Path $ReedModDir "Reed.json") -Force
Write-Host "  -> Reed.json copied" -ForegroundColor Green

# Copy PCK (if exists)
$reedPck = Join-Path $ScriptDir "Reed.pck"
if (Test-Path $reedPck) {
    Copy-Item $reedPck (Join-Path $ReedModDir "Reed.pck") -Force
    Write-Host "  -> Reed.pck copied" -ForegroundColor Green
} else {
    Write-Host "  Reed.pck not found (resources not packed, has_pck=true)" -ForegroundColor DarkYellow
}

# -- Step 4: Deploy RitsuLib framework --
Write-Host "[4/4] Deploying RitsuLib framework..." -ForegroundColor Yellow

if (-not (Test-Path $RitsuDll)) {
    Write-Host "  RitsuLib DLL not found: $RitsuDll" -ForegroundColor Red
    Write-Host "  Run 'dotnet restore' first" -ForegroundColor DarkYellow
    exit 1
}

if (-not (Test-Path $RitsuModDir)) {
    New-Item -ItemType Directory -Path $RitsuModDir -Force | Out-Null
    Write-Host "  Created: $RitsuModDir" -ForegroundColor DarkGray
}

# Check if update needed
$targetRitsuDll = Join-Path $RitsuModDir "STS2-RitsuLib.dll"
$needCopy = $true
if (Test-Path $targetRitsuDll) {
    $srcHash = (Get-FileHash $RitsuDll -Algorithm MD5).Hash
    $dstHash = (Get-FileHash $targetRitsuDll -Algorithm MD5).Hash
    if ($srcHash -eq $dstHash) {
        $needCopy = $false
    }
}

if ($needCopy) {
    Copy-Item $RitsuDll $targetRitsuDll -Force
    Write-Host "  -> STS2-RitsuLib.dll copied" -ForegroundColor Green
} else {
    Write-Host "  -> STS2-RitsuLib.dll already up-to-date" -ForegroundColor DarkGray
}

# Copy RitsuLib manifest
$targetRitsuManifest = Join-Path $RitsuModDir "STS2-RitsuLib.json"
if (Test-Path $RitsuManifest) {
    Copy-Item $RitsuManifest $targetRitsuManifest -Force
    Write-Host "  -> STS2-RitsuLib.json copied" -ForegroundColor Green
} else {
    Write-Host "  RitsuLib manifest not found in NuGet, creating..." -ForegroundColor DarkYellow
    $manifest = @{
        id = "STS2-RitsuLib"
        name = "RitsuLib"
        author = "OLC"
        description = "A shared Slay the Spire 2 mod framework library."
        version = "0.5.18"
        has_pck = $false
        has_dll = $true
        affects_gameplay = $false
        dependencies = @()
        min_game_version = "0.111.0"
    } | ConvertTo-Json -Depth 5
    $manifest | Out-File -FilePath $targetRitsuManifest -Encoding ascii
    Write-Host "  -> STS2-RitsuLib.json created" -ForegroundColor Green
}

# -- Done --
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Deploy Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Deployed to: $ModsDir" -ForegroundColor White
Write-Host "  - Reed/              (mod DLL + manifest)"
if (Test-Path (Join-Path $ReedModDir "Reed.pck")) {
    Write-Host "  - Reed/Reed.pck      (resource pack)" -ForegroundColor Green
} else {
    Write-Host "  - Reed/Reed.pck      (MISSING! use -Pack)" -ForegroundColor DarkYellow
}
Write-Host "  - STS2-RitsuLib/     (framework DLL + manifest)"
Write-Host ""
Write-Host "Launch the game to load the mod." -ForegroundColor Cyan
Write-Host ""
