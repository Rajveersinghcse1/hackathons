#!/bin/bash

# GramSeva - Quick Start Script
# Bash script for Linux/macOS

echo "🚀 GramSeva - Quick Start"
echo "=========================="

# Check if Docker is running
echo ""
echo "📦 Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi
echo "✅ Docker is running"

# Start Docker services
echo ""
echo "🐳 Starting Docker services (PostgreSQL, Redis, MinIO)..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Failed to start Docker services"
    exit 1
fi
echo "✅ Docker services started"

# Wait for PostgreSQL to be ready
echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
max_retries=30
retry_count=0
while [ $retry_count -lt $max_retries ]; do
    if docker-compose exec -T postgres pg_isready -U campusfixit > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready"
        break
    fi
    sleep 1
    retry_count=$((retry_count + 1))
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ PostgreSQL failed to start in time"
    exit 1
fi

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend

# Setup .env
if [ ! -f .env ]; then
    echo "📝 Creating backend .env file..."
    cp .env.example .env
fi

if command -v pnpm &> /dev/null; then
    pnpm install
else
    echo "⚠️  pnpm not found, using npm..."
    npm install
fi
echo "✅ Backend dependencies installed"

# Push database schema
echo ""
echo "🗄️  Setting up database schema..."
npx prisma db push
echo "✅ Database schema applied"

# Seed database
echo ""
echo "🌱 Seeding database with test data..."
npx prisma db seed
echo "✅ Database seeded"

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd ../frontend

# Setup .env
if [ ! -f .env ]; then
    echo "📝 Creating frontend .env file..."
    cp .env.example .env
fi

if command -v pnpm &> /dev/null; then
    pnpm install
else
    echo "⚠️  pnpm not found, using npm..."
    npm install
fi
echo "✅ Frontend dependencies installed"

cd ..

echo ""
echo "========================================="
echo "🎉 Setup Complete!"
echo "========================================="
echo ""
echo "To start the application:"
echo "  1. Backend:  cd backend && pnpm dev"
echo "  2. Frontend: cd frontend && pnpm dev"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:4000"
echo "  MinIO:    http://localhost:9001"
echo ""
echo "Test Accounts:"
echo "  Admin:   sarpanch@gramseva.in / admin123"
echo "  Staff:   engineer1@gramseva.in / staff123"
echo "  Citizen: ramu@gramseva.in / villager123"
echo ""
echo "  Admin:   admin@msrit.edu / admin123"
echo "  Staff:   maintenance1@msrit.edu / staff123"
echo "  Student: rahul@msrit.edu / student123"
echo ""
