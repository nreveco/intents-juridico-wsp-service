param(
  [switch]$Db,
  [switch]$System,
  [switch]$Quick,
  [switch]$All
)

$ErrorActionPreference = 'Stop'

Write-Host "WhatsApp AI Automation - Test Suite" -ForegroundColor Cyan
Write-Host ""

# Verificar que Python esté disponible
try {
  $null = python --version
} catch {
  Write-Host "ERROR: Python no está instalado o no está en PATH" -ForegroundColor Red
  exit 1
}

if ($Quick) {
  Write-Host "Ejecutando test rápido de conexión..." -ForegroundColor Yellow
  python test_db_connection.py --quick
  exit $LASTEXITCODE
}

if ($Db -or $All) {
  Write-Host "Ejecutando verificación de base de datos..." -ForegroundColor Yellow
  python test_db_connection.py
  if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Test de base de datos falló" -ForegroundColor Red
    exit 1
  }
  Write-Host ""
}

if ($System -or $All) {
  Write-Host "Ejecutando test completo del sistema..." -ForegroundColor Yellow
  python test_system.py
  if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Test del sistema falló" -ForegroundColor Red
    exit 1
  }
  Write-Host ""
}

if (-not $Db -and -not $System -and -not $All -and -not $Quick) {
  Write-Host "Uso:" -ForegroundColor Yellow
  Write-Host "  test.cmd -Quick     # Test rápido de conexión" -ForegroundColor Gray
  Write-Host "  test.cmd -Db        # Verificar base de datos" -ForegroundColor Gray
  Write-Host "  test.cmd -System    # Test completo del sistema" -ForegroundColor Gray
  Write-Host "  test.cmd -All       # Ejecutar todos los tests" -ForegroundColor Gray
  Write-Host ""
  Write-Host "Ejecutando test rápido por defecto..." -ForegroundColor Cyan
  python test_db_connection.py --quick
}

Write-Host "Todos los tests completados" -ForegroundColor Green
