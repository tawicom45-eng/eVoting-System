# Render Deployment Checklist

This guide walks through deploying `university_evoting` to Render using the provided `render.yaml` and configuration.

## Prerequisites
- Repository pushed to GitHub/GitLab and connected to Render
- Render account with organization/team access

## Step 1: Create Web Service

1. Go to **Render Dashboard** → **New** → **Web Service**
2. Select your git repository
3. Configure:
   - **Name**: `university-evoting-web` (or preferred name)
   - **Environment**: Docker
   - **Region**: Choose closest to users
   - **Branch**: `main` (or your deployment branch)
   - **Build Command**: (leave empty — Dockerfile handles it)
   - **Start Command**: `gunicorn evoting_system.wsgi:application -b 0.0.0.0:$PORT --workers 3 --timeout 180`

4. **Environment Variables** (add in Render dashboard):
   ```
   SECRET_KEY=<generate-a-long-random-string>
   DEBUG=False
   ALLOWED_HOSTS=<your-render-service-url>.onrender.com,localhost,127.0.0.1
   
   # Database (attach managed Postgres first, then Render auto-populates this)
   DATABASE_URL=<auto-populated-by-render>
   POSTGRES_DB=evoting
   
   # Redis (attach managed Redis first, then Render auto-populates this)
   REDIS_URL=<auto-populated-by-render>
   CELERY_BROKER_URL=<auto-populated-by-render>
   CELERY_RESULT_BACKEND=<auto-populated-by-render>
   
   # Email (configure your SMTP provider)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=<your-email>
   EMAIL_HOST_PASSWORD=<your-app-password>
   EMAIL_USE_TLS=True
   DEFAULT_FROM_EMAIL=<your-email>
   
   # Site Configuration
   SITE_URL=https://<your-render-service-url>.onrender.com
   ORGANIZATION_NAME=University Elections
   
   # Security (enable in production)
   SECURE_SSL_REDIRECT=True
   SESSION_COOKIE_SECURE=True
   CSRF_COOKIE_SECURE=True
   SECURE_HSTS_SECONDS=31536000
   SECURE_HSTS_INCLUDE_SUBDOMAINS=True
   ```

5. **Instance Type**: Starter (or higher for production load)
6. Click **Create Web Service**

## Step 2: Attach Managed PostgreSQL

1. In the **Web Service** dashboard, go to **Data** (or **Resources**)
2. Click **Create PostgreSQL**
3. Configure:
   - **Name**: `university-evoting-db`
   - **Database**: `evoting`
   - **Region**: Same as web service
   - **Plan**: Starter (or Standard for production)
4. Click **Create Database**
5. Render will automatically set `DATABASE_URL` in the web service environment

## Step 3: Attach Managed Redis

1. In the **Web Service** dashboard, go to **Data** (or **Resources**)
2. Click **Create Redis**
3. Configure:
   - **Name**: `university-evoting-redis`
   - **Region**: Same as web service
   - **Plan**: Starter (or higher for production)
4. Click **Create Redis**
5. Render will automatically set `REDIS_URL` in the web service environment

## Step 4: Verify Web Service Deployment

1. Monitor logs in Render dashboard:
   - Watch for `entrypoint.sh` running migrations and `collectstatic`
   - Check for `gunicorn` startup message
2. Once deployed, test the health endpoint:
   ```bash
   curl https://<your-render-service-url>.onrender.com/health/
   ```
   Expected response: `{"status": "ok", "db": true}`

3. Test login in browser:
   ```
   https://<your-render-service-url>.onrender.com/accounts/login/
   ```

## Step 5: Create Worker Service

1. Go to **Render Dashboard** → **New** → **Web Service** (or **Background Worker**)
2. Select same repository
3. Configure:
   - **Name**: `university-evoting-worker`
   - **Environment**: Docker
   - **Branch**: `main`
   - **Start Command**: `celery -A evoting_system worker -l info`

4. **Environment Variables**: Copy same vars from Web Service (or link to existing Redis/Database)
5. **Instance Type**: Starter
6. Click **Create Service**

## Step 6: Run Post-Deployment Smoke Tests

### Via Render Web Shell:

1. In **Web Service** dashboard, click **Shell**
2. Run:
   ```bash
   cd /app
   python manage.py shell < scripts/verify_300_logins.py
   ```
   Expected: `TOTAL 300 SUCCESS 300 FAIL 0`

3. Check static files:
   ```bash
   ls -la staticfiles/
   ```

4. Verify database migrations:
   ```bash
   python manage.py showmigrations
   ```

## Step 7: Configure Static & Media Files

### Option A: Render Disk (Simple, Limited)
1. Add to **Web Service** environment:
   ```
   STATIC_URL=/staticfiles/
   STATIC_ROOT=/app/staticfiles
   ```
2. Create a persistent disk in Render (Data tab) mounted at `/app/media`
3. Update settings.py to use the disk path

### Option B: AWS S3 (Recommended for Production)
1. Set up AWS S3 bucket and IAM credentials
2. Install `django-storages`:
   ```bash
   pip install django-storages[s3]
   ```
3. Add to environment:
   ```
   USE_S3=True
   AWS_STORAGE_BUCKET_NAME=<your-bucket>
   AWS_S3_REGION_NAME=us-east-1
   AWS_S3_ACCESS_KEY_ID=<your-key>
   AWS_S3_SECRET_ACCESS_KEY=<your-secret>
   AWS_S3_CUSTOM_DOMAIN=<your-bucket>.s3.amazonaws.com
   ```
4. Update `settings.py` to detect `USE_S3` and configure storages

## Step 8: Enable Monitoring & Backups

1. **Database Backups**:
   - In **PostgreSQL** dashboard → **Settings** → Enable **Backups**
   - Set retention to 7-30 days

2. **Service Health Checks**:
   - Already configured in `render.yaml` with `healthCheckPath: /health/`
   - Render will probe every 10 seconds

3. **Alerts** (optional):
   - Set up Render alerts for deployment failures, crashes, CPU/memory thresholds

## Step 9: Domain & SSL

1. Go to **Web Service** → **Settings** → **Custom Domain**
2. Add your domain (e.g., `evoting.university.edu`)
3. Render provides free SSL certificate (auto-renewed)

## Troubleshooting

### 500 errors on deployment
- Check logs for migration failures: `python manage.py migrate --noinput`
- Verify environment variables are set (especially `SECRET_KEY`, `DATABASE_URL`)
- Check database is healthy and migrations applied

### Static files missing
- Run: `python manage.py collectstatic --noinput`
- Verify `STATIC_ROOT` and `STATIC_URL` are configured

### Login returns 400
- Check environment variables (esp. `ALLOWED_HOSTS`)
- Verify database connectivity and user data
- Check logs for rate-limiting or CSRF issues

### Celery worker not processing tasks
- Verify Redis is attached and `REDIS_URL` is set
- Check worker logs for connection errors
- Ensure `CELERY_BROKER_URL` matches Redis URL

## Quick Commands (from Render Web Shell)

```bash
# Check migrations
python manage.py showmigrations

# Verify 300 logins
python manage.py shell < scripts/verify_300_logins.py

# View Django logs
tail -f logs/django_run.log

# Test email (if configured)
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'noreply@university.edu', ['admin@university.edu'])

# Check database
python manage.py dbshell
```

## Security Checklist

- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`
- [ ] Configure email credentials securely (use Render secrets, not in .env)
- [ ] Set up database backups
- [ ] Enable HTTPS (Render auto-provides)
- [ ] Rotate `EMAIL_HOST_PASSWORD` periodically
- [ ] Monitor logs for errors and security warnings

## Next Steps After Deployment

1. Test all user portals (student, staff, admin)
2. Verify email notifications work
3. Test voting workflow end-to-end
4. Set up log monitoring and alerting
5. Plan regular backups and disaster recovery
6. Monitor performance and scale as needed

---

**Questions?** Refer to `DEPLOY_RENDER.md` for detailed env var descriptions and architecture notes.
