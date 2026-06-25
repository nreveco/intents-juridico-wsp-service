param(
  [switch]$NoCache,
  [switch]$Prune,
  [switch]$ResetVolumes,
  [switch]$NoPull,
  [switch]$Logs
)

$ErrorActionPreference = 'Stop'

$composeFile = 'docker-compose.yml'
$composeArgs = @('-f', $composeFile)

Write-Host "WhatsApp AI Automation - Docker Manager" -ForegroundColor Cyan
Write-Host "Using compose file: $composeFile" -ForegroundColor Gray
Write-Host ""

# Check if .env exists
$envFile = Join-Path $PSScriptRoot '.env'
if (-not (Test-Path $envFile)) {
  Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
  Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
  $envExample = Join-Path $PSScriptRoot '.env.example'
  if (Test-Path $envExample) {
    Copy-Item $envExample $envFile
    Write-Host "Please edit .env with your credentials before continuing." -ForegroundColor Red
    Write-Host "Required variables:" -ForegroundColor Yellow
    Write-Host "  - WHATSAPP_TOKEN" -ForegroundColor Gray
    Write-Host "  - WHATSAPP_PHONE_NUMBER_ID" -ForegroundColor Gray
    Write-Host "  - WHATSAPP_VERIFY_TOKEN" -ForegroundColor Gray
    Write-Host "  - ADMIN_API_KEY" -ForegroundColor Gray
    Write-Host ""
    pause
    exit 1
  } else {
    Write-Host "ERROR: .env.example not found!" -ForegroundColor Red
    exit 1
  }
}

if ($Prune) {
  Write-Host 'Pruning unused Docker images...' -ForegroundColor Yellow
  docker image prune -f
}

Write-Host 'Stopping and removing containers...' -ForegroundColor Yellow
if ($ResetVolumes) {
  Write-Host 'WARNING: This will delete all data (database, Ollama models)!' -ForegroundColor Red
  $confirm = Read-Host "Are you sure? (yes/no)"
  if ($confirm -eq 'yes') {
    docker compose @composeArgs down --remove-orphans -v
  } else {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
  }
} else {
  docker compose @composeArgs down --remove-orphans
}

Write-Host 'Building and starting services...' -ForegroundColor Green
Write-Host '  - PostgreSQL' -ForegroundColor Gray
Write-Host '  - Ollama (will pull model on first run)' -ForegroundColor Gray
Write-Host '  - FastAPI app' -ForegroundColor Gray
Write-Host '  - Nginx reverse proxy' -ForegroundColor Gray
Write-Host ""

$pullFlag = if ($NoPull) { '--pull=never' } else { '' }

if ($NoCache) {
  Write-Host 'Running full build without cache...' -ForegroundColor Yellow
  $buildArgs = @('--no-cache')
  if ($NoPull) { $buildArgs += '--pull=never' }
  docker compose @composeArgs build @buildArgs
  docker compose @composeArgs up -d --force-recreate --remove-orphans
} else {
  $upArgs = @('-d', '--build', '--force-recreate', '--remove-orphans')
  if ($NoPull) { $upArgs += '--pull=never' }
  docker compose @composeArgs up @upArgs
}

Write-Host ""
Write-Host 'Waiting for services to be ready...' -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host ""
Write-Host 'Current service status:' -ForegroundColor Cyan
docker compose @composeArgs ps

Write-Host ""
Write-Host '============================================' -ForegroundColor Green
Write-Host 'Services are ready!' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Green
Write-Host ""
Write-Host "FastAPI:    http://localhost" -ForegroundColor White
Write-Host "API Docs:   http://localhost/docs" -ForegroundColor White
Write-Host "Ollama:     http://localhost:11434" -ForegroundColor White
Write-Host "PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Load demo data: python seed_demo.py" -ForegroundColor Gray
Write-Host "  2. Expose with ngrok: ngrok http 80" -ForegroundColor Gray
Write-Host "  3. Configure webhook in Meta Developer Console" -ForegroundColor Gray
Write-Host ""
Write-Host "View logs: docker-rebuild.cmd -Logs" -ForegroundColor Gray
Write-Host "Stop:      docker compose down" -ForegroundColor Gray
Write-Host ""

if ($Logs) {
  Write-Host "Following logs (Ctrl+C to stop)..." -ForegroundColor Cyan
  Write-Host ""
  docker compose @composeArgs logs -f --tail=100
}

Write-Host 'Done.' -ForegroundColor Green
