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
4. Render asks you to fill the two "sync: false" values — enter your desired
   admin login:
   - `DJANGO_SUPERUSER_EMAIL` → e.g. `admin@eco-link.co.ke`
   - `DJANGO_SUPERUSER_PASSWORD` → a strong password
5. Render now builds the app: installs packages, collects static files, runs
   migrations, then **`deploy_setup`** which **seeds the collection hub, rewards,
   and manufacturers and creates your admin account**. Watch the **Logs** tab.

> **Why this matters:** Render's **free tier has no Shell**, so you can't run
> `seed_hubs`/`createsuperuser` by hand. `deploy_setup` runs automatically on
> every deploy (it's idempotent — no duplicates), so the hub always exists and
> the drop-off dropdown is never empty.

## Step 4 — Open your site and log in
When the service shows **Live**, open the URL
(`https://ecolink-XXXX.onrender.com`). Log in with the admin email/password you
set in Step 3. The Main Gate hub, rewards, and manufacturers are already there.

### Add sample participants (optional)
Want a populated leaderboard for a demo? In the Render **Environment** tab add
`RUN_SEED_DEMO=1`, then **Manual Deploy → Deploy latest commit**. The deploy
seeds a few named participants with drop-offs. Remove the variable afterwards so
it doesn't re-run needlessly.

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
