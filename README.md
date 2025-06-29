# Sagole

## About

Sagole is a full-stack, multi-environment database administration and auditing platform. It provides a modern web interface for browsing, editing, and managing relational database tables, with robust change approval workflows and immutable snapshotting for compliance and auditability.

**Key Features:**
- Multi-environment support (dev, test, prod, etc.)
- Role-based access control (admin/user)
- Change request and approval workflow (admin approval required for edits)
- Immutable, point-in-time table snapshots for audit and rollback
- Dynamic table browsing, filtering, and editing
- Git-style diff viewer for change requests
- Responsive, modern UI built with React and Vite

**Technologies Used:**
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL,JWT Auth, Pydantic
- **Frontend:** React, Vite, Axios, TailwindCSS

## Project Structure

This project is a monorepo with the following structure:

```
repo/
  backend/   # Backend server (FastAPI, PostgreSQL)
  frontend/  # Frontend client (React, Vite)
```

See the README.md files in each directory for more specific information.

## Backend Overview

- **API:** RESTful, environment-aware endpoints (e.g., `/api/v1/dev/tables`)
- **Authentication:** JWT-based, with admin/user roles
- **Change Requests:** All edits are submitted as change requests, requiring admin approval
- **Snapshots:** Every approved change triggers a full-table snapshot, stored immutably for audit and rollback
- **Key Endpoints:**
  - `POST /api/v1/{env}/token` — Login
  - `GET /api/v1/{env}/tables` — List tables
  - `GET /api/v1/{env}/tables/{table}` — Table data (pagination/filtering)
  - `GET /api/v1/{env}/tables/{table}/schema` — Table schema
  - `POST /api/v1/{env}/changes` — Submit change request
  - `GET /api/v1/{env}/changes` — List pending changes (admin)
  - `POST /api/v1/{env}/changes/{id}/approve` — Approve change (admin)
  - `POST /api/v1/{env}/changes/{id}/reject` — Reject change (admin)
  - `GET /api/v1/{env}/tables/{table}/snapshots` — List snapshots
  - `GET /api/v1/{env}/snapshots/{id}` — Get snapshot data

**See [`repo/backend/SNAPSHOT_FUNCTIONALITY.md`](repo/backend/SNAPSHOT_FUNCTIONALITY.md) for a deep dive into the snapshot/audit system.**

## Frontend Overview

- **Modern React SPA** with Vite for fast development
- **Global State Management** via React Context
- **Authentication:** Demo login (admin/user), token-based
- **Environment Selector:** Switch between dev/test/prod
- **Data Browser:**
  - Table list, pagination, filtering, and record editing (admin only)
  - Add record modal (admin only, dynamic form)
  - JSON viewer for complex fields
- **Change Requests:**
  - Git-style diff viewer for pending changes
  - Approve/reject workflow (admin only)
- **Responsive Design:** Mobile-friendly, professional UI
- **Future Features:** Predefined queries, settings, user management, advanced filtering, export, notifications

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/MedDash99/Sagole.git
cd Sagole
```

### 2. Backend Setup

```bash
cd repo/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configure your PostgreSQL connection in environment variables or .env files
# Start the FastAPI server (example):
uvicorn app.main:app --reload
```

### 3. Frontend Setup

```bash
cd repo/frontend
npm install
npm run dev
```

The frontend will run on [http://localhost:5173](http://localhost:5173) and connect to the backend at [http://localhost:8000](http://localhost:8000) by default.

## Usage

- **Login:** Use the demo login for admin access
- **Browse Data:** Select tables, paginate, filter, and view records
- **Edit/Add Records:** Admins can edit or add records (creates change requests)
- **Approve/Reject Changes:** Admins review and approve/reject via the Change Requests view
- **Snapshots:** Every approved change creates a permanent snapshot for audit and rollback
- **Switch Environments:** Use the environment dropdown in the header

## Contributors

[Mendel Dashevsky]

---

For more details, see the documentation in each subdirectory and the [SNAPSHOT_FUNCTIONALITY.md](repo/backend/SNAPSHOT_FUNCTIONALITY.md) for backend audit logic.
