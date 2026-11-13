# Deployment Guide: Free Cloud Hosting (Vercel, Render & Supabase)

This repository is architected for zero-cost, high-performance deployment across modern cloud platforms:
- **Frontend SPA**: Hosted on [Vercel](https://vercel.com) (Free Tier with Global Edge CDN).
- **Backend API**: Hosted on [Render](https://render.com) (Free Python Web Service).
- **PostgreSQL Database & Auth**: Hosted on [Supabase](https://supabase.com) (Free Tier PostgreSQL + RLS).

---

## 1. Deploying Frontend on Vercel

The frontend is built with React 18 and Vite. Root and frontend `vercel.json` rewrite configurations are pre-packaged.

### Option A: Via GitHub (Recommended)
1. Push your repository to GitHub.
2. Sign in to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New Project"**.
3. Import your repository.
4. Set the project configuration:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend` (or leave default if using root `vercel.json`)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Under **Environment Variables**, add:
   ```env
   VITE_API_URL=https://<your-render-backend-name>.onrender.com
   ```
6. Click **Deploy**. Vercel will build and provision an edge CDN URL (e.g. `https://aura-speed.vercel.app`).

---

## 2. Deploying Backend FastAPI on Render

A `render.yaml` blueprint and production `Dockerfile` are included in the repository root.

### Deployment Steps:
1. Sign in to [Render Dashboard](https://dashboard.render.com).
2. Click **"New +"** and select **"Web Service"**.
3. Connect your GitHub repository.
4. Configure service parameters:
   - **Name**: `optimized-chatbot-api`
   - **Runtime**: `Python 3` (or Docker)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.api.app:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
5. Add the following **Environment Variables**:
   ```env
   ENVIRONMENT=production
   OPEN_ROUTER_MODEL=google/gemma-3-27b-it:free
   OPEN_ROUTER_API=<your-openrouter-free-api-key>
   CACHE_TTL_SECONDS=3600
   SEMANTIC_SIMILARITY_THRESHOLD=0.75
   PORT=8000
   ```
6. Click **Create Web Service**. Render will install requirements, initialize the SQLite B-Tree index, and expose your HTTPS endpoint.

---

## 3. Configuring Supabase (Database & Auth)

To migrate from local SQLite and browser storage to managed cloud PostgreSQL:

1. Sign up at [Supabase.com](https://supabase.com) and create a free project.
2. Navigate to **SQL Editor** in the Supabase dashboard.
3. Open `supabase/schema.sql` from this repository, paste its contents into the SQL Editor, and click **Run**.
   - This creates:
     - `profiles` (Row-level security policies for users and admins)
     - `chat_sessions` (Multi-turn conversation sessions)
     - `chat_messages` (Message history with tier routing telemetry)
     - `cart_items` (Persistent shopping cart items)
     - `orders` (Checkout records)
     - `telemetry_logs` (System audit events)
4. Retrieve your **Project URL** and **anon public key** from `Settings -> API`.

---

## 4. Local Full-Stack Development

Run both services locally with live reload:

### Terminal 1: Backend
```bash
source .venv/bin/activate
uvicorn src.api.app:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
Open `http://localhost:3000` in your browser. All `/api` queries will proxy automatically to the FastAPI backend.
