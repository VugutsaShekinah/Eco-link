# 🚀 Put ECO-LINK Online (Render) — Simple Guide

Follow these steps in order. It's free and takes about 15 minutes.
By the end you'll have a link like `https://ecolink-xxxx.onrender.com` anyone can open.

---

## Step 1 — Make a Render account
1. Go to **https://render.com**
2. Click **Get Started** → **GitHub** → allow access.

## Step 2 — Start a new Blueprint
1. Click **New +** (top right) → **Blueprint**.
2. Find and pick your repo **Eco-link** → click **Connect**.

Render reads the `render.yaml` file in your project and already knows how to set
everything up (the app **and** the database).

## Step 3 — Type your admin login
Render will ask you to fill in two boxes:

| Box | What to type |
|-----|--------------|
| `DJANGO_SUPERUSER_EMAIL` | an email you'll remember, e.g. `admin@eco-link.co.ke` |
| `DJANGO_SUPERUSER_PASSWORD` | a strong password you'll remember |

This becomes your admin account on the live site.

## Step 4 — Click Apply and wait
1. Click **Apply** (or **Create**).
2. Render builds the site. Wait a few minutes.
3. When you see **Live** (green), it's ready.

While it builds, the **Logs** should show:
```
Seed complete: 1 hub(s) ... 2 manufacturers.
Seed complete: 5 rewards ...
Created admin account: admin@eco-link.co.ke
```

## Step 5 — Open and use your site
1. Click the link at the top (ends in `.onrender.com`).
2. You'll see the ECO-LINK home page. 🎉
3. Click **Log in** and use the admin email + password from Step 3.
4. Go to **Log Drop-off** — the **Main Gate Hub** is in the dropdown. ✅

**That's it — your project is online.**

---

## If something looks wrong

| Problem | Fix |
|---------|-----|
| Dropdown for hub is empty | Open your service → **Manual Deploy** → **Deploy latest commit**, wait for Live, refresh. |
| Can't log in as admin | Go to **Environment** tab, check `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` are set, then redeploy. |
| Page is slow to load | Normal on the free plan — it "sleeps" after 15 min idle and takes ~50s to wake the first time. |
| CSS/logo missing | Redeploy; the build step handles static files automatically. |

## Good to know (free plan)
- The site sleeps when unused and wakes on the next visit (~50s).
- The free database is removed after about 30 days — just create the Blueprint
  again if that happens.

---

## Every time you change the code later
```bash
git add -A
git commit -m "describe your change"
git push
```
Render notices the push and re-deploys automatically.
