mkdir -p backend/app

# Core
mkdir -p backend/app/core
touch backend/app/core/config.py
touch backend/app/core/security.py
touch backend/app/core/dependencies.py

# DB
mkdir -p backend/app/db
touch backend/app/db/base.py
touch backend/app/db/session.py
touch backend/app/db/models.py

# Routers
mkdir -p backend/app/routers
touch backend/app/routers/auth.py
touch backend/app/routers/orgs.py
touch backend/app/routers/projects.py
touch backend/app/routers/tasks.py
touch backend/app/routers/activity.py

# Schemas
mkdir -p backend/app/schemas
touch backend/app/schemas/auth.py
touch backend/app/schemas/org.py
touch backend/app/schemas/project.py
touch backend/app/schemas/task.py

# Services
mkdir -p backend/app/services
touch backend/app/services/rbac.py
touch backend/app/services/activity.py

# Backend root files
touch backend/app/main.py
touch backend/requirements.txt
touch backend/.env

# ================= FRONTEND =================
mkdir -p frontend/app

# App routes (Next.js App Router)
mkdir -p frontend/app/login
mkdir -p frontend/app/dashboard
mkdir -p frontend/app/projects/[id]

touch frontend/app/layout.tsx
touch frontend/app/page.tsx
touch frontend/app/login/page.tsx
touch frontend/app/dashboard/page.tsx
touch frontend/app/projects/[id]/page.tsx

# Lib
mkdir -p frontend/lib
touch frontend/lib/api.ts
touch frontend/lib/auth.ts

# Components
mkdir -p frontend/components
touch frontend/components/Navbar.tsx
touch frontend/components/TaskBoard.tsx
touch frontend/components/RoleGuard.tsx

# Middleware
touch frontend/middleware.ts