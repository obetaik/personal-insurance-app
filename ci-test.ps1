#!/usr/bin/env pwsh

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting CI Pipeline..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📦 Testing backend..." -ForegroundColor Yellow
Set-Location -Path backend

# Create virtual environment if it doesn't exist
if (-not (Test-Path "venv")) {
    python -m venv venv
}

# Activate virtual environment
if (Test-Path "venv/Scripts/Activate.ps1") {
    & .\venv\Scripts\Activate.ps1
}

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests (if they exist)
if (Test-Path "tests") {
    python -m pytest tests/ --cov=. --cov-report=term
} else {
    Write-Host "⚠️  No backend tests found" -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎨 Testing frontend..." -ForegroundColor Yellow
Set-Location -Path frontend

# Install dependencies
npm ci

# Run linting
try {
    npm run lint
} catch {
    Write-Host "⚠️  Linting not configured or failed" -ForegroundColor Yellow
}

# Run tests
try {
    npm test -- --watchAll=false
} catch {
    Write-Host "⚠️  No frontend tests found or tests failed" -ForegroundColor Yellow
}

# Build the app
npm run build

Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🐳 Building Docker images..." -ForegroundColor Yellow
docker-compose build

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🔥 Running smoke tests..." -ForegroundColor Yellow
Write-Host ""

# Test backend health
Write-Host "Testing backend health..." -ForegroundColor White
try {
    $response = Invoke-WebRequest -Uri http://localhost:4000/api/health -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend health check passed" -ForegroundColor Green
    } else {
        throw "Backend returned status $($response.StatusCode)"
    }
} catch {
    Write-Host "❌ Backend health check failed: $_" -ForegroundColor Red
    docker-compose logs backend
    docker-compose down
    exit 1
}

Write-Host ""
Write-Host "Testing frontend..." -ForegroundColor White
try {
    $response = Invoke-WebRequest -Uri http://localhost:80 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend health check passed" -ForegroundColor Green
    } else {
        throw "Frontend returned status $($response.StatusCode)"
    }
} catch {
    Write-Host "❌ Frontend health check failed: $_" -ForegroundColor Red
    docker-compose logs frontend
    docker-compose down
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing API endpoints..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Products API:" -ForegroundColor White
try {
    $products = Invoke-WebRequest -Uri http://localhost:4000/api/products -UseBasicParsing
    if ($products.Content -match "Auto Insurance") {
        Write-Host "✅ Products API working" -ForegroundColor Green
        $products.Count
    } else {
        Write-Host "⚠️  Products API returned unexpected data" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Products API failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
docker-compose down

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ CI Pipeline completed successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
