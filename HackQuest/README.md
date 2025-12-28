# GramSeva 🔧

**Hyperlocal Infrastructure Issue Reporting & Resolution Platform**

A transparent, accountable system for reporting and tracking village infrastructure issues with photo verification, GPS tagging, and public accountability.

## 🎯 Problem Statement

Village infrastructure issues (broken roads, water leaks, sanitation issues, electrical hazards) go unreported or unresolved for weeks because citizens lack a direct, transparent channel to report problems and track accountability of local administration.

## ✨ Key Features

- **30-second issue reporting** — Photo + GPS + category, done
- **Public issue board** — Every citizen sees all open issues
- **3D village heat map** — Visual representation of problem zones
- **Automatic escalation** — Unresolved issues auto-escalate after 48/72 hours
- **Resolution proof** — Administration must upload "fixed" photo to close
- **Gamification** — Top reporters get recognition

## 🏗️ Architecture

```
Frontend (Next.js + shadcn/ui + Three.js)
           │
           ▼
    API Gateway (Fastify)
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
 Issues  Users  Notifications
           │
    ┌──────┼──────┐
    ▼      ▼      ▼
PostgreSQL MinIO  Redis
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14, React, TypeScript |
| UI | shadcn/ui, Tailwind CSS |
| 3D | Three.js, React Three Fiber |
| Maps | Leaflet, OpenStreetMap |
| Backend | Node.js, Fastify |
| Database | PostgreSQL 16 + PostGIS |
| Storage | MinIO (S3-compatible) |
| Cache | Redis |
| Containers | Docker, Docker Compose |

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- pnpm

### Development Setup

```bash
# Clone and enter directory
cd GramSeva

# Start all services
docker-compose up -d

# Install frontend dependencies
cd frontend
pnpm install
pnpm dev

# Install backend dependencies (in new terminal)
cd backend
pnpm install
pnpm dev
```

### Access Points
- **Frontend**: http://localhost:3000
- **API**: http://localhost:4000
- **MinIO Console**: http://localhost:9001

## 📁 Project Structure

```
GramSeva/
├── docker-compose.yml      # All containerized services
├── frontend/               # Next.js application
│   ├── app/               # App router pages
│   ├── components/        # React components
│   └── lib/               # Utilities
├── backend/               # Fastify API server
│   ├── src/
│   │   ├── routes/       # API routes
│   │   ├── services/     # Business logic
│   │   └── db/           # Database queries
│   └── prisma/           # Database schema
└── docs/                  # Documentation
```

## 👥 User Roles

1. **Citizen/Reporter** — Report issues, track status, upvote
2. **Village Staff** — View assignments, resolve issues, upload proof
3. **Admin** — Dashboard, analytics, staff management, escalation

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | User registration |
| POST | /api/auth/login | User login |
| GET | /api/issues | List all issues |
| POST | /api/issues | Create new issue |
| GET | /api/issues/:id | Get issue details |
| PATCH | /api/issues/:id | Update issue status |
| POST | /api/issues/:id/upvote | Upvote an issue |
| GET | /api/stats | Get dashboard stats |

## 🔒 Accountability Features

- All issues publicly visible
- Photo proof required for closure
- Immutable timestamps
- Complete activity audit log
- Auto-escalation after 48 hours
- Public resolution metrics

## 📈 Scalability Path

1. **Phase 1**: Single village deployment
2. **Phase 2**: Multi-tenant for multiple villages
3. **Phase 3**: District integration

## 📄 License

MIT License — Free for educational and civic use.

## 🤝 Contributing

Built for a hackathon, designed for real-world impact.
