# 🚀 Deploy ECO-LINK to Render (the easy way)

Render hosts your Django app **and** a PostgreSQL database on a free tier, builds
straight from your GitHub repo, and gives you an HTTPS link — no server admin.
This uses the included **`render.yaml`** blueprint, so most of it is automatic.

**Estimated time:** ~15 minutes. **Cost:** free.

---

## What you get
A public URL like `https://ecolink.onrender.com` that anyone can open.

> **Free-tier caveats (fine for a demo):**
> - The app "sleeps" after ~15 min idle; the next visit takes ~50s to wake.
> - Render's free PostgreSQL is removed after ~30 days — just recreate it if needed.

---

## Step 1 — Make sure your code is on GitHub
Already done ✅ (`https://github.com/VugutsaShekinah/Eco-link`). Any future change:
```bash
git add -A
git commit -m "your message"
git push
```
Render redeploys automatically on every push.

## Step 2 — Create a Render account
Go to **https://render.com** → **Get Started** → **Sign in with GitHub** and
authorise it to read your repositories.

## Step 3 — Create the Blueprint
1. In the Render dashboard click **New +** → **Blueprint**.
2. Pick your **Eco-link** repository → **Connect**.
3. Render finds `render.yaml` and shows a plan: one **web service** + one
   **PostgreSQL database**. Click **Apply**.
4. Render now builds the app (installs packages, collects static files, runs
   migrations) and starts it with Gunicorn. Watch the **Logs** tab; the first
   build takes a few minutes.

## Step 4 — Open your site
When the service shows **Live**, click the URL at the top
(`https://ecolink-XXXX.onrender.com`). You'll see the ECO-LINK landing page. 🎉

## Step 5 — Create your admin login + demo data
The fresh database has no users yet. In Render:
1. Open your **ecolink** web service → **Shell** tab.
2. Run:
   ```bash
   python manage.py createsuperuser      # make your admin account
   python manage.py seed_demo            # hub, rewards, sample participants
   ```
3. Back on the site, log in with the admin you just created.

---

## How this maps to what you learned
| Piece | Handled by |
|-------|------------|
| Application server (Gunicorn) | `startCommand` in `render.yaml` |
| Static files (CSS, logo) | WhiteNoise (no Nginx needed) |
| Database (PostgreSQL) | Render managed DB, injected as `DATABASE_URL` |
| HTTPS padlock | Render provides it automatically |
| Secrets (SECRET_KEY) | Render generates it; `DEBUG=False` set |

Render plays the role Nginx + Gunicorn + the server play in `DEPLOYMENT.md` —
just automated for you.

---

## Troubleshooting
- **Build fails on `migrate`** — open the database in Render and confirm it's
  "available", then click **Manual Deploy → Deploy latest commit**.
- **CSS/logo missing** — make sure the build log shows "collectstatic"; WhiteNoise
  serves them (already configured).
- **403 on login** — the app already sets `CSRF_TRUSTED_ORIGINS` for
  `*.onrender.com`; if you use a custom domain, add it there too.
