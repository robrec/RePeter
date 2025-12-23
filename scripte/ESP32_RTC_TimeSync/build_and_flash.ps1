# ESP32 RTC TimeSync - Build & Flash Script (PlatformIO)
# Kompiliert und flasht das ESP32_RTC_TimeSync.ino auf einen ESP32-S3

param(
    [string]$Port = "",      # COM Port (leer für automatische Erkennung)
    [switch]$CompileOnly,    # Nur kompilieren, nicht flashen
    [switch]$Monitor         # Nach Upload Serial Monitor starten
)

$ErrorActionPreference = "Stop"
$ProjectDir = $PSScriptRoot

Write-Host "`n=== ESP32 RTC TimeSync - Build & Flash (PlatformIO) ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectDir`n" -ForegroundColor Gray

# Wechsle ins Projektverzeichnis
Set-Location $ProjectDir

# Erstelle PlatformIO src Struktur falls nötig
$srcDir = "$ProjectDir\src"
if (!(Test-Path $srcDir)) {
    New-Item -ItemType Directory -Path $srcDir -Force | Out-Null
}

Write-Host "[1/4] Kopiere Sketch nach src/main.cpp..." -ForegroundColor Yellow

# Kopiere .ino nach src als .cpp (PlatformIO erwartet .cpp in src/)
$inoFile = "$ProjectDir\ESP32_RTC_TimeSync.ino"
$cppFile = "$srcDir\main.cpp"

if (!(Test-Path $inoFile)) {
    Write-Host "  FEHLER: ESP32_RTC_TimeSync.ino nicht gefunden!" -ForegroundColor Red
    exit 1
}

Copy-Item $inoFile $cppFile -Force
Write-Host "  Sketch kopiert" -ForegroundColor Green

# Kompilieren mit verbose output
Write-Host "`n[2/4] Kompiliere mit PlatformIO (verbose)..." -ForegroundColor Yellow
Write-Host "  Dies kann beim ersten Mal einige Minuten dauern (ESP32 Toolchain Download)...`n" -ForegroundColor Gray

# Verwende --verbose für detaillierte Ausgabe
python -m platformio run --verbose

if ($LASTEXITCODE -ne 0) {
    Write-Host "`n  FEHLER: Kompilierung fehlgeschlagen!" -ForegroundColor Red
    exit 1
}

Write-Host "`n  Kompilierung erfolgreich!" -ForegroundColor Green

# Firmware Pfad anzeigen
$firmwarePath = ".pio\build\esp32-s3-devkitc-1\firmware.bin"
if (Test-Path $firmwarePath) {
    $firmwareSize = (Get-Item $firmwarePath).Length / 1KB
    Write-Host "  Firmware: $firmwarePath ($([math]::Round($firmwareSize, 2)) KB)" -ForegroundColor Gray
}

# Flashen (wenn nicht nur Compile-Only)
if (!$CompileOnly) {
    Write-Host "`n[3/4] Flashe auf ESP32..." -ForegroundColor Yellow
    
    if ($Port -eq "") {
        Write-Host "  Automatische Port-Erkennung..." -ForegroundColor Gray
        python -m platformio run --target upload
    } else {
        Write-Host "  Flashe auf $Port..." -ForegroundColor Gray
        python -m platformio run --target upload --upload-port $Port
    }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "`n  FEHLER: Upload fehlgeschlagen!" -ForegroundColor Red
        Write-Host "`n  Tipp: Port manuell angeben mit: .\build_and_flash.ps1 -Port COM3" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "  Upload erfolgreich!" -ForegroundColor Green
    
    # Serial Monitor starten
    if ($Monitor) {
        Write-Host "`n[4/4] Starte Serial Monitor..." -ForegroundColor Yellow
        if ($Port -eq "") {
            python -m platformio device monitor
        } else {
            python -m platformio device monitor --port $Port
        }
    } else {
        Write-Host "`n[4/4] Serial Monitor übersprungen (nutze -Monitor zum Aktivieren)" -ForegroundColor Yellow
    }
} else {
    Write-Host "`n[3/4] Upload übersprungen (CompileOnly Mode)" -ForegroundColor Yellow
    Write-Host "[4/4] Fertig" -ForegroundColor Yellow
}

Write-Host "`n=== Fertig! ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Verwendung:" -ForegroundColor Yellow
Write-Host "  .\build_and_flash.ps1              # Kompilieren und flashen" -ForegroundColor Gray
Write-Host "  .\build_and_flash.ps1 -CompileOnly # Nur kompilieren" -ForegroundColor Gray
Write-Host "  .\build_and_flash.ps1 -Port COM3   # Spezifischer Port" -ForegroundColor Gray
Write-Host "  .\build_and_flash.ps1 -Monitor     # Mit Serial Monitor" -ForegroundColor Gray
Write-Host ""
