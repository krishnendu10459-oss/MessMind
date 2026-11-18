# 🍲 AI-Powered Food Waste Prediction System

> **A Complete Web-Based Decision Support System for College Mess Operations**  
> *Reduces mess food waste through predictive meal demand modeling, real-time consumption logging, and food waste analytics.*

---

## 📌 Problem Statement
In college hostels and institutions, mess operators face daily uncertainty regarding how many students will actually attend meals. Cooking too much leads to massive food and financial waste; cooking too little leaves students hungry. 

### 💡 The Solution
This software system leverages historical consumption trends, expected attendance, day of the week, meal type, and menu items to **forecast actual meal demand using machine learning (Random Forest Regression)**. 

Mess administrators can:
1. **Predict required meal portions** before cooking begins with a 5% kitchen safety buffer.
2. **Log actual meals cooked vs. meals consumed** after dining hours.
3. **Edit, update, and manage historical logs** with live recalculations.
4. **Track food waste percentages and cost impacts** across days and menus via Chart.js.
5. **Receive actionable human-verified surplus food advisories** for local NGO/donation outreach.
6. **Monitor database connectivity and engine health** via `/api/health` and live dashboard indicator.

---

## 🖥️ Web Application Pages (UI/UX)

| Page | URL Route | Description & Features |
|:---|:---|:---|
| **📊 Dashboard** | `/dashboard` or `/` | High-level KPI cards (Total Prepared, Consumed, Wasted, Waste %), Recent Activity table, and interactive Chart.js graphs. |
| **📝 Daily Entry** | `/entry` | Kitchen log form for attendance, menu, prepared count, and actual consumption with real-time client-side waste calculations. |
| **🔮 AI Prediction** | `/predict` | Connects directly to the trained Random Forest model. Displays predicted consumption, 5% buffer cook recommendation, heuristic ensemble uncertainty range, and recent forecast logs. |
| **📈 Waste Analytics**| `/analytics` | In-depth waste trends, daily/weekly/monthly stats, menu-wise waste comparison bar chart, and meal session distribution. |
| **🗂️ Historical Records**| `/records` | Searchable table of past mess records with 20-record pagination, date range filters, menu search, record editing (`/records/edit/<id>`), deletion, and CSV export. |
| **🍲 Surplus Advisory**| `/surplus` | Flags batches with high unconsumed food (&ge; 20 portions) for physical safety inspection before coordinating with local NGOs. |
| **🩺 Health & Diagnostics**| `/api/health` | REST endpoint reporting database connectivity, active engine, record counts, and sanitized connection URI. |

---

## 🗄️ Database Architecture: Dual-Database Governance

The system uses **Flask-SQLAlchemy 3.1.1** and **PyMySQL**, supporting two operating modes with strict data consistency controls:

1. **MySQL Mode (Primary Production Standard):**
   - Configured via environment variables (`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`) or direct `DATABASE_URL`.
   - Passwords with special characters (`@`, `#`, `:`, `/`, `%`, `&`) are automatically URL-encoded via `urllib.parse.quote_plus`.
   - Connection resilience with `pool_recycle=280` and `pool_pre_ping=True`.
   - Full setup guide available in [database/MYSQL_SETUP.md](database/MYSQL_SETUP.md).

2. **SQLite Mode (Zero-Config Development):**
   - Active for local development in `database/food_waste.db`.
   - Requires zero external database installation for instant local testing.

3. **Deterministic Failover Governance (Anti-Silent Failover):**
   - **Production Mode:** MySQL is mandatory. If MySQL is unreachable, startup aborts immediately. SQLite fallback is strictly prohibited.
   - **Development Mode:** `ALLOW_SQLITE_FALLBACK=false` by default. Startup halts with clear diagnostic steps if MySQL fails, preventing silent database switching. Controlled fallback to SQLite occurs only if explicitly enabled (`ALLOW_SQLITE_FALLBACK=true`).
   - The active database engine is determined deterministically once at startup and never changed per-request.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| **Language** | Python 3.14.5 | Backend logic, data engineering, ML modeling |
| **Web Framework** | Flask 3.1.3 (Jinja2) | Lightweight web server and RESTful routing |
| **Database** | MySQL (Primary) + SQLite (Dev Fallback) | Relational storage for mess records, predictions, and advisories |
| **ORM & Migrations**| Flask-SQLAlchemy 3.1.1, Flask-Migrate 4.1.0, Alembic | Database abstraction, foreign keys, migrations |
| **Machine Learning** | Scikit-learn 1.9.1, Pandas 3.1.1, NumPy 2.5.4, Joblib | Preprocessing, Random Forest Regressor |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) | Responsive SaaS dashboard layout |
| **Data Visualization**| Chart.js 4.4 | Interactive trend charts, waste breakdowns |
| **Testing** | Pytest 9.2.0 | Automated unit, integration, security, and edge-case test suite (**42 tests passing**) |

---

## 🚀 Beginner Quick-Start Guide (Step-by-Step)

### Step 1: Open Terminal in Project Folder
```bash
cd MessMind
```

### Step 2: Activate the Virtual Environment
```bash
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Windows Command Prompt:
.\venv\Scripts\activate.bat
```

### Step 3: Initialize Database (Creates Tables & Seeds Sample Records)
```bash
python database/init_db.py --seed
```

### Step 4: Run Automated Tests
```bash
python -m pytest -v
```

### Step 5: Start the Web Application
```bash
python run.py
```
Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 📋 Important Constraints & Design Principles
- **Software-only project:** No hardware or IoT scales required.
- **No paid external APIs:** Fully self-contained local stack.
- **Genuine ML Model:** Real Random Forest Regressor trained on 720 historical records, evaluated on an 80/20 chronological split (MAE 13.22, R² 0.985), with an empirical 100% coverage heuristic uncertainty range.
- **Synthetic Dataset Transparency:** Clearly documented as synthetic campus data; operational advisory advises kitchen staff to verify sudden campus events.
- **Application Security:** Session-based CSRF tokens on all state-modifying requests, parameterized ORM queries, XSS auto-escaping, sanitized `/api/health` filesystem paths, and custom production error pages (400, 403, 404, 500).
- **Human-Verified Food Safety:** Unconsumed meals flagged for human safety verification before donation coordination.
