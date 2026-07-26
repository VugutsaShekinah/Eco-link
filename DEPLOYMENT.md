# 🌐 ECO-LINK Deployment Guide

Production deployment on an **Ubuntu Server** with **Gunicorn** (application
server) behind **Nginx** (reverse proxy), and **PostgreSQL** (report §3.4).
This is a reference guide — adapt paths and domains to your host.

```
Browser ⇄ Nginx (HTTPS, static files) ⇄ Gunicorn (Django/WSGI) ⇄ PostgreSQL
```

---

## 1. Server prerequisites
```bash
sudo apt update
sudo apt install python3-venv python3-pip postgresql nginx git
```

## 2. Get the code and install
```bash
git clone <your-repo-url> /opt/ecolink
cd /opt/ecolink
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

## 3. PostgreSQL
```bash
sudo -u postgres psql
CREATE DATABASE ecolink_db;
CREATE USER ecolink_user WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE ecolink_db TO ecolink_user;
\q
```

## 4. Environment (`.env` in project root)
```ini
SECRET_KEY=<a fresh 50-char random key>
DEBUG=False
ALLOWED_HOSTS=eco-link.co.ke,www.eco-link.co.ke
DB_NAME=ecolink_db
DB_USER=ecolink_user
DB_PASSWORD=strong-password
DB_HOST=127.0.0.1
DB_PORT=5432
```
> With `DEBUG=False`, `settings.py` automatically enables HTTPS redirect, secure
> cookies, and HSTS.

## 5. Migrate, collect static, seed
```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py seed_hubs
python manage.py seed_rewards
```

## 6. Gunicorn (systemd service)
Create `/etc/systemd/system/ecolink.service`:
```ini
[Unit]
Description=ECO-LINK Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/ecolink
ExecStart=/opt/ecolink/venv/bin/gunicorn ecolink.wsgi:application \
          --bind unix:/run/ecolink.sock --workers 3

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl enable --now ecolink
```

## 7. Nginx
Create `/etc/nginx/sites-available/ecolink`:
```nginx
server {
    listen 80;
    server_name eco-link.co.ke www.eco-link.co.ke;

    location /static/ {
        alias /opt/ecolink/staticfiles/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/ecolink.sock;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/ecolink /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```

## 8. HTTPS (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d eco-link.co.ke -d www.eco-link.co.ke
```

---

## Deployment checklist
- [ ] `DEBUG=False` and a fresh `SECRET_KEY` in `.env`
- [ ] `ALLOWED_HOSTS` set to your domain(s)
- [ ] `python manage.py check --deploy` passes
- [ ] `collectstatic` run; Nginx serves `/static/`
- [ ] PostgreSQL backups scheduled (report §3.2.2.3)
- [ ] HTTPS certificate installed and redirecting
