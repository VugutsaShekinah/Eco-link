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
You don't need to type anything here — just click through. A ready-to-use admin
account is created for you automatically (see Step 5).

## Step 4 — Click Apply and wait
1. Click **Apply** (or **Create**).
2. Render builds the site. Wait a few minutes.
3. When you see **Live** (green), it's ready.

While it builds, the **Logs** should show:
```
Seed complete: 1 hub(s) ... 2 manufacturers.
Seed complete: 5 rewards ...
Created admin login:  admin@eco-link.co.ke  /  EcoLink2026!  <-- DEFAULT login
```

## Step 5 — Open and log in
1. Click the link at the top (ends in `.onrender.com`).
2. You'll see the ECO-LINK home page. 🎉
3. Click **Log in** and use the **default admin login**:

   | | |
   |---|---|
   | **Email** | `admin@eco-link.co.ke` |
   | **Password** | `EcoLink2026!` |

4. Go to **Log Drop-off** — the **Main Gate Hub** is in the dropdown. ✅

**That's it — your project is online, and you can log in as admin.**

> 🔒 **Change this password** once you're in (top-right **CHANGE PASSWORD** on the
> `/admin/` page), since it's written in this guide. To use your *own* email and
> password instead, add `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD`
> in Render's **Environment** tab and redeploy.

---

## If something looks wrong

| Problem | Fix |
|---------|-----|
| Dropdown for hub is empty, or can't log in as admin | Open your service → **Manual Deploy** → **Deploy latest commit**, wait for Live, then use the default admin login above. |
| Page is slow to load | Normal on the free plan — it "sleeps" after 15 min idle and takes ~50s to wake the first time. |
| CSS/logo missing | Redeploy; the build step handles static files automatically. |

## Sharing your site with other people
You do **not** share your admin login. Just send them the link — each person
makes their own account:
1. They open the link and click **Register**.
2. They choose **Student**, **Staff**, or **Community** and set their own email + password.
3. They can log drop-offs, earn eco-points, redeem rewards, and see the leaderboard.

Only **your** admin account can verify drop-offs, record sales, and open the Admin
Dashboard — regular users are automatically blocked from those pages.

> **Tip:** a drop-off a user logs stays **Pending** until you (admin) verify it,
> then their eco-points appear. To promote someone else to admin, open `/admin/`
> → **Users** → their account → set **Role = Administrator** and tick **is staff**
> and **is superuser** → **Save**.

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
