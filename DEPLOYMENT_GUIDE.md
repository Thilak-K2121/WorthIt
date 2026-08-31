# WorthIt: Cloud Deployment Guide
> **Complete Step-by-Step Guide for Supabase (PostgreSQL) + Render (Backend & Frontend)**

---

## 🏗️ Architecture Overview

- **Database:** Supabase (Cloud Managed PostgreSQL)
- **Backend API:** Render (Web Service — Python 3.12 / FastAPI / Uvicorn)
- **Frontend App:** Render (Static Site — React + Vite SPA)

---

## ⚡ Step 1: Create Supabase PostgreSQL Database (Free Tier)

1. Go to [supabase.com](https://supabase.com) and log in / create a free account.
2. Click **New Project**:
   - **Name:** `worthit-db`
   - **Database Password:** *(Set a strong password and save it)*
   - **Region:** Choose closest to your users (e.g. `ap-south-1` Mumbai or `us-east-1` N. Virginia)
   - **Pricing Plan:** Free
3. Once the database is provisioned (approx. 1–2 minutes):
   - Go to **Project Settings** (gear icon) $\rightarrow$ **Database**.
   - Scroll to **Connection String** $\rightarrow$ select **URI** (or **Session Pooler**).
   - Copy the string:
     ```text
     postgresql://postgres.[your-project-ref]:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
     ```
   - Replace `[YOUR-PASSWORD]` with your actual database password.

> 💡 **Auto-Migration Note:** When the backend starts up, FastAPI automatically runs `Base.metadata.create_all()` and seeds all foundational issue categories. You do **not** need to manually run any SQL tables!

---

## 🚀 Step 2: Push Code to Your GitHub Repository

Ensure your repository is pushed to GitHub under your own account:
```bash
git add .
git commit -m "feat: complete WorthIt full-stack platform ready for cloud deployment"
git branch -M main
git remote add origin https://github.com/Thilak-K2121/WorthIt.git
git push -u origin main --force
```

---

## 🐍 Step 3: Deploy Backend on Render (Web Service)

1. Go to [dashboard.render.com](https://dashboard.render.com) and log in with GitHub.
2. Click **New +** $\rightarrow$ **Web Service**.
3. Connect your repository: `Thilak-K2121/WorthIt`.
4. Fill in the deployment details:
   - **Name:** `worthit-backend` (or `worthit-api`)
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Region:** Same as Supabase (e.g. *Singapore* or *Oregon*)
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** Free

5. Scroll down to **Environment Variables** $\rightarrow$ click **Add Environment Variable**:

| Key | Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql://postgres...` | Your Supabase connection string from Step 1 |
| `TAVILY_API_KEY` | `tvly-dev-...` | Your Tavily Search API key |
| `GEMINI_API_KEY` | `AQ.Ab8RN...` | Your Google Gemini API key |
| `ENVIRONMENT` | `production` | Production mode |
| `DEBUG` | `false` | Disable debug logs |
| `CORS_ORIGINS` | `*` | Allows your frontend to communicate with API |

6. Click **Create Web Service**.
7. Render will build and launch your backend in 2–3 minutes. Once live, note your backend URL:
   ```text
   https://worthit-backend.onrender.com
   ```

---

## ⚛️ Step 4: Deploy Frontend on Render (Static Site)

1. In Render Dashboard, click **New +** $\rightarrow$ **Static Site**.
2. Select the same repository: `Thilak-K2121/WorthIt`.
3. Fill in the static site configuration:
   - **Name:** `worthit-app` (or `worthit`)
   - **Root Directory:** `frontend`
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     npm install && npm run build
     ```
   - **Publish Directory:** `dist`

4. Add **Environment Variables**:

| Key | Value |
| :--- | :--- |
| `VITE_API_BASE_URL` | `https://worthit-backend.onrender.com/api/v1` |

*(Replace `worthit-backend.onrender.com` with your actual backend URL from Step 3)*

5. Under **Redirects/Rewrites**:
   - The included `frontend/public/_redirects` file automatically handles single-page client routing (`/* -> /index.html 200`).

6. Click **Create Static Site**.

---

## ✅ Step 5: Verification & Live Test

Once both services deploy:
1. Open your frontend URL: `https://worthit-app.onrender.com`.
2. Navigate to **Discovery** (`/admin`) $\rightarrow$ click **`Run Discovery`** to verify live internet scraping with Tavily + Gemini directly into your Supabase PostgreSQL database.
3. Submit a new experience report on `/submit` to verify real-time database writes.
4. Verify `/compare` and `/products` load from the cloud database.
