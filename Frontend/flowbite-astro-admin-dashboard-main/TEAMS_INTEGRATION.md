# NBStats Frontend - Teams Integration

## Changes Made

### 1. Created Teams Page and Component
- **`/src/pages/crud/teams.astro`** - New page for Teams CRUD
- **`/src/modules/CrudTeams.astro`** - Teams listing component with table view

### 2. Backend Integration
- **`/src/services/teams.ts`** - Service to fetch teams from backend API
- **`/src/types/entities.ts`** - Added `Teams` and `Team` type definitions
- **`/src/app/constants.ts`** - Updated API_URL to point to backend

### 3. API Configuration
- **`/src/pages/api/[...entity].ts`** - Added `teams/all` endpoint mapping
- **`.env`** - Created environment file with backend URL

### 4. Navigation
- **`/src/app/SideBar.astro`** - Added Teams link in the CRUD dropdown (first item)

## Setup Instructions

### 1. Start Backend API
```bash
cd /Users/luishernandez/Desktop/NBStats/Backend
# Activate your virtual environment if needed
# source venv/bin/activate
uvicorn src.main:app --reload
```

The backend should be running at `http://localhost:8000`

### 2. Start Frontend
```bash
cd /Users/luishernandez/Desktop/NBStats/Frontend/flowbite-astro-admin-dashboard-main
npm install  # if you haven't already
npm run dev
```

The frontend should be running at `http://localhost:4321` (or another port shown in terminal)

### 3. Access Teams Page
- Navigate to the CRUD section in the sidebar
- Click on "Teams" (first option in the dropdown)
- Or go directly to: `http://localhost:4321/crud/teams`

## Team Data Structure

The Teams component displays:
- **Team Name** (full_name) with nickname
- **Abbreviation** (e.g., LAL, GSW)
- **City** and **State**
- **Year Founded**

## Configuration

To change the backend URL, update the `.env` file:
```env
PUBLIC_API_URL=http://localhost:8000/api/v1/
```

## Next Steps

You can now:
1. Add more team-related endpoints (roster, games, etc.)
2. Create detail pages for individual teams
3. Add filtering and search functionality
4. Implement team statistics displays
