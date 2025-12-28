# GramSeva - Quick Start Script
# PowerShell script for Windows

Write-Host "🚀 GramSeva - Quick Start" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan

# Check if Docker is running
Write-Host "`n📦 Checking Docker..." -ForegroundColor Yellow
$dockerStatus = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker is running" -ForegroundColor Green

# Start Docker services
Write-Host "`n🐳 Starting Docker services (PostgreSQL, Redis, MinIO)..." -ForegroundColor Yellow
docker-compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start Docker services" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker services started" -ForegroundColor Green

# Wait for PostgreSQL to be ready
Write-Host "`n⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
while ($retryCount -lt $maxRetries) {
    $pgReady = docker-compose exec -T postgres pg_isready -U campusfixit 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL is ready" -ForegroundColor Green
        break
    }
    Start-Sleep -Seconds 1
    $retryCount++
}

if ($retryCount -eq $maxRetries) {
    Write-Host "❌ PostgreSQL failed to start in time" -ForegroundColor Red
    exit 1
}

# Install backend dependencies
Write-Host "`n📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend

# Setup .env
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating backend .env file..." -ForegroundColor Gray
    Copy-Item ".env.example" ".env"
}

pnpm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  pnpm not found, trying npm..." -ForegroundColor Yellow
    npm install
}
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green

# Push database schema
Write-Host "`n🗄️  Setting up database schema..." -ForegroundColor Yellow
npx prisma db push
Write-Host "✅ Database schema applied" -ForegroundColor Green

# Seed database
Write-Host "`n🌱 Seeding database with test data..." -ForegroundColor Yellow
npx prisma db seed
Write-Host "✅ Database seeded" -ForegroundColor Green

# Install frontend dependencies
Write-Host "`n📦 Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location ../frontend

# Setup .env
if (-not (Test-Path ".env")) {
    Write-Host "📝 Creating frontend .env file..." -ForegroundColor Gray
    Copy-Item ".env.example" ".env"
}

pnpm install

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  pnpm not found, trying npm..." -ForegroundColor Yellow
    npm install
}
Write-Host "✅ Frontend dependencies installed" -ForegroundColor Green

Set-Location ..

Write-Host "`n" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "`nTo start the application:" -ForegroundColor White
Write-Host "  1. Backend:  cd backend && pnpm dev" -ForegroundColor Gray
Write-Host "  2. Frontend: cd frontend && pnpm dev" -ForegroundColor Gray
Write-Host "`nAccess the application:" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Blue
Write-Host "  Backend:  http://localhost:4000" -ForegroundColor Blue
Write-Host "  MinIO:    http://localhost:9001" -ForegroundColor Blue
Write-Host "`nTest Accounts:" -ForegroundColor White
Write-Host "  Admin:   sarpanch@gramseva.in / admin123" -ForegroundColor Gray
Write-Host "  Staff:   engineer1@gramseva.in / staff123" -ForegroundColor Gray
Write-Host "  Citizen: ramu@gramseva.in / villager123" -ForegroundColor Gray
Write-Host ""
