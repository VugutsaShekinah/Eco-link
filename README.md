# 🌿 ECO-LINK — Plastic Waste Management System

A web-based platform that connects students, staff, and the community around
**Riara University** with recycling collection hubs and certified recyclers
through an **incentive-driven** model: deposit plastic, earn eco-points, redeem
rewards, and climb a community leaderboard.

> Final Year Project — BSc Business Information Technology, Riara University.
> Built with Python, Django 5, and PostgreSQL.

---

## ✨ Features

| Module | What it does |
|--------|--------------|
| **Accounts** | Email registration with Student / Staff / Community roles; role-based access control. |
| **Drop-offs & Eco-points** | Log plastic deposits with a live points preview; **10 points/kg** awarded on admin verification. |
| **Rewards** | Redeem points for vouchers/certificates; safe, atomic point deduction. |
| **Admin dashboard** | Live stats, one-click drop-off verification, user-status management. |
| **Leaderboard & Impact** | Ranked participants, your row highlighted, programme-wide impact figures. |

---

## 🛠 Tech stack

- **Backend:** Python 3, Django 5.2 (LTS), Django ORM
- **Database:** PostgreSQL
- **Frontend:** Django Templates, Bootstrap 5, HTML5, CSS3, JavaScript
- **Tooling:** Git, coverage.py, Visual Studio Code

---

## 🚀 Getting started (from a fresh clone)

### Prerequisites
- Python 3.11+ (developed on 3.14)
- PostgreSQL 14+ running locally
- Git

### 1. Clone and create a virtual environment
```bash
git clone <your-repo-url> eco-link
cd eco-link
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create the PostgreSQL database
```bash
# In psql or pgAdmin:
CREATE DATABASE ecolink_db;
```

### 4. Configure environment variables
```bash
cp .env.example .env      # Windows: copy .env.example .env
# then edit .env and set DB_PASSWORD (and a SECRET_KEY)
```

### 5. Apply migrations and seed demo data
```bash
python manage.py migrate
python manage.py seed_hubs       # Main Gate collection hub + a recycler
python manage.py seed_rewards    # sample reward catalogue
```

### 6. Create an administrator account
```bash
python manage.py createsuperuser
```

### 7. Run the development server
```bash
python manage.py runserver
```
Open **http://127.0.0.1:8000/**.

---

## 🧪 Testing

```bash
python manage.py test                    # run all tests (54)
python -m coverage run manage.py test    # run under coverage
python -m coverage report                # per-file coverage table (~97%)
python -m coverage html                  # browsable report in htmlcov/
```

---

## 🗺 URL map

| Path | Page | Access |
|------|------|--------|
| `/` | Landing page (or dashboard if logged in) | Public |
| `/register/`, `/login/`, `/logout/` | Authentication | Public |
| `/dashboard/` | User dashboard (balance, history, rank) | Logged in |
| `/dropoffs/log/`, `/dropoffs/mine/` | Log & view drop-offs | Logged in |
| `/rewards/`, `/rewards/mine/` | Reward catalogue & redemptions | Logged in |
| `/leaderboard/` | Community leaderboard & impact | Logged in |
| `/manage/` | Admin dashboard (stats, verify) | **Admin only** |
| `/manage/users/` | Manage user status | **Admin only** |
| `/admin/` | Django admin (hubs, rewards CRUD) | **Admin only** |

---

## 📁 Project structure

```
ecolink/        Project config (settings, root URLs)
accounts/       Custom User model, auth, RBAC, dashboard
hubs/           Hub + Manufacturer models, admin, seed
dropoffs/       DropOff model, points formula, verification signal
rewards/        Reward + Redemption models, atomic redeem service
dashboard/      Administrator dashboard (stats, verify, user mgmt)
leaderboard/    Ranking + impact visualisation
templates/      Django templates (base + per-app)
static/         CSS
docs/           Development notes (HTML source + PDF build)
```

---

## 🔒 Key design decisions

- **Custom User model** keyed on **email** (no username).
- **One eco-points formula** (`dropoffs/points.py`) reused by the model, view, and JS preview.
- **Points awarded via a signal** on verification — works the same from the dashboard or Django admin.
- **Redemption is atomic** (`select_for_update`) to prevent double-spending.
- **Live stats** via ORM aggregates — never stored counters.

---

## 🌐 Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for production notes (Gunicorn + Nginx on
Ubuntu, `collectstatic`, HTTPS, and environment configuration).

---

## 📄 License / attribution

Academic project by Shekinah Vugutsa Onzere, Riara University, 2026.

