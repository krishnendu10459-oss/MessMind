# 🗄️ MySQL Database Setup & Configuration Guide

This guide provides step-by-step instructions for college viva evaluation, local deployment, and database administration of the **AI-Powered Food Waste Prediction System**.

---

## 1. Architecture Overview: Dual-Database Governance

The project implements a **hardened dual-database architecture** managed via SQLAlchemy and PyMySQL:
- **MySQL Mode (Primary Production Standard):** Configured for formal college project evaluation and production deployment.
- **SQLite Mode (Local Development Baseline):** Pre-configured out of the box in `database/food_waste.db` for rapid local testing without external services.

### Deterministic Failover Policy
To prevent silent database switching and data divergence:
1. **Production Mode (`FLASK_ENV=production`):** MySQL is mandatory. If MySQL is unreachable, startup aborts immediately with a diagnostic error. SQLite fallback is strictly prohibited.
2. **Development Mode (`FLASK_ENV=development`):**
   - Default: `ALLOW_SQLITE_FALLBACK=false`. If MySQL is unreachable, startup halts with actionable instructions.
   - Controlled Fallback: If `ALLOW_SQLITE_FALLBACK=true` is explicitly set in `.env`, the application gracefully falls back to SQLite and marks system health as `degraded`.

---

## 2. Setting Up MySQL on Your Machine

### Option A: Using MySQL Server & MySQL Workbench (Recommended)
1. Download and install [MySQL Community Server](https://dev.mysql.com/downloads/mysql/).
2. During installation, set a password for the `root` user (remember this password).
3. Open **MySQL Command Line Client** or **MySQL Workbench**.

### Option B: Using XAMPP
1. Download and install [XAMPP](https://www.apachefriends.org/).
2. Open XAMPP Control Panel and click **Start** next to **MySQL** (default port `3306`, user `root`, no password).

---

## 3. Database Initialization Commands

### Step 1: Create the Database in MySQL
Log into MySQL:
```bash
mysql -u root -p
```
Run the following SQL commands:
```sql
CREATE DATABASE IF NOT EXISTS food_waste_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;
EXIT;
```

### Step 2: Import the Table Schema
From the project root directory, run:
```bash
mysql -u root -p food_waste_db < database/schema.sql
```
*(Alternatively, copy and paste the contents of `database/schema.sql` directly into MySQL Workbench query tab and execute).*

---

## 4. Connecting the Flask Application to MySQL

1. Open `.env` in the project root.
2. Update the database configuration section:
```env
# Set to 'mysql'
DB_TYPE=mysql

# Failover policy (keep false for strict integrity)
ALLOW_SQLITE_FALLBACK=false

# MySQL Connection Details
DB_HOST=localhost
DB_PORT=3306
DB_NAME=food_waste_db
DB_USER=root
DB_PASSWORD=your_actual_mysql_password_here
```

### Password Special Characters Support
If your MySQL password contains special characters (e.g. `@`, `#`, `:`, `/`, `%`, `&`), the application automatically URL-encodes it using `urllib.parse.quote_plus`. No manual escaping is required.

---

## 5. Automated Table Verification & Seeding

Run the project initialization utility to verify MySQL connectivity and populate historical records:
```powershell
# 1. Activate environment
.\venv\Scripts\Activate.ps1

# 2. Run initialization with sample data seeding
python database/init_db.py --seed
```

Expected Output:
```text
=================================================================
🛠️ DATABASE INITIALIZATION UTILITY
=================================================================
Target Database Type : MYSQL
Connection Target    : localhost:3306/food_waste_db
-----------------------------------------------------------------
✅ Connection check passed!
✅ Schema verification: All tables exist.
🌱 Seeding Database with Historical Mess Records...
✅ Successfully inserted 180 mess records into database.
🎉 Database is ready for operations!
=================================================================
```

---

## 6. Schema Migrations with Flask-Migrate (Alembic)

The project includes pre-configured database migration support:
```powershell
# Check current migration revision
flask db current

# Upgrade database to latest schema revision
flask db upgrade

# Generate new migration when models change
flask db migrate -m "Description of change"
```

---

## 7. Real-Time Database Health & Status Monitoring

A diagnostic REST endpoint is available for health and connectivity verification:
- URL: `GET http://127.0.0.1:5000/api/health`
- Response Example:
```json
{
  "status": "healthy",
  "database": {
    "active_type": "mysql",
    "connected": true,
    "masked_target": "mysql+pymysql://root:****@localhost:3306/food_waste_db?charset=utf8mb4",
    "fallback_active": false,
    "allow_fallback_configured": false
  },
  "records": {
    "mess_records": 181,
    "prediction_logs": 1,
    "surplus_advisories": 15
  },
  "environment": "development",
  "error": null
}
```
In the web dashboard, a persistent status badge at the bottom of the navigation sidebar displays the active database engine (`DB: MYSQL` or `DB: SQLITE`) and links directly to `/api/health`.
