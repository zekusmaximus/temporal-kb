# VPS Setup Guide - Step by Step

I'll walk you through setting up on **Hetzner Cloud** (best value at €3.79/month ≈ $4). The process is similar for other providers.

---

## Step 1: Create Hetzner Account & Server

### 1.1 Sign Up
1. Go to https://www.hetzner.com/cloud
2. Click "Sign up" → Create account
3. Verify email
4. Add payment method (credit card or PayPal)

### 1.2 Create SSH Key (on your local machine)

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your_email@example.com"
# Press Enter for default location (~/.ssh/id_ed25519)
# Set a passphrase (recommended) or leave empty

# Display public key (copy this)
cat ~/.ssh/id_ed25519.pub
```

### 1.3 Create Server
1. Login to Hetzner Cloud Console
2. Click "New Project" → Name it "temporal-kb"
3. Click "Add Server"
4. **Location:** Choose closest to you (Ashburn, VA for US East)
5. **Image:** Ubuntu 24.04
6. **Type:** Shared vCPU → **CX22** (2 vCPU, 4GB RAM, 40GB disk - €3.79/month)
7. **SSH Key:** Click "Add SSH Key" → Paste your public key from above
8. **Firewall:** Skip for now (we'll configure with ufw)
9. **Backups:** Enable (€1.00/month extra - recommended)
10. **Name:** temporal-kb-server
11. Click "Create & Buy Now"

**Wait 1-2 minutes for server to provision. Note the IP address shown.**

---

## Step 2: Initial Server Configuration

### 2.1 Connect to Server

```bash
# Replace with your server IP
ssh root@YOUR_SERVER_IP

# First time you'll see:
# "The authenticity of host... can't be established"
# Type: yes

# You should now see: root@temporal-kb-server:~#
```

### 2.2 Update System & Install Dependencies

```bash
# Update package list and upgrade
apt update && apt upgrade -y

# Install required packages
apt install -y \
    python3.12 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    ufw \
    htop \
    nano

# Verify installations
python3 --version    # Should show Python 3.12.x
psql --version       # Should show PostgreSQL 16.x
nginx -v            # Should show nginx version
```

### 2.3 Create Application User

```bash
# Create user for running the application
useradd -m -s /bin/bash kbuser

# Set password for the user
passwd kbuser
# Enter a strong password twice

# Add user to sudo group (for administrative tasks)
usermod -aG sudo kbuser

# Verify user was created
id kbuser
```

---

## Step 3: Configure PostgreSQL

### 3.1 Create Database & User

```bash
# Switch to postgres user
sudo -u postgres psql

# You should see: postgres=#
```

```sql
-- Create database
CREATE DATABASE temporal_kb;

-- Create user with strong password (CHANGE THIS!)
CREATE USER kbuser WITH PASSWORD 'your_very_secure_password_here_123!';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE temporal_kb TO kbuser;

-- Connect to the database
\c temporal_kb

-- Grant schema privileges (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO kbuser;

-- Exit postgres
\q
```

### 3.2 Test Database Connection

```bash
# Test connection as kbuser
psql -U kbuser -d temporal_kb -h localhost

# If successful, you'll see: temporal_kb=>
# Exit with: \q
```

### 3.3 Configure PostgreSQL for Remote Connections (if needed later)

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/16/main/postgresql.conf

# Find and change:
# listen_addresses = 'localhost'
# To:
# listen_addresses = '*'

# Edit pg_hba.conf for authentication
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Add this line at the end:
# host    all             all             0.0.0.0/0               scram-sha-256

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

## Step 4: Deploy Application

### 4.1 Switch to Application User

```bash
# Switch to kbuser
su - kbuser

# You should now see: kbuser@temporal-kb-server:~$
```

### 4.2 Transfer Application Code

**Option A: From Local Machine (Recommended)**

```bash
# On your LOCAL machine (new terminal), from temporal-kb directory
# Replace with your server IP
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='venv' --exclude='data' \
  ./ kbuser@YOUR_SERVER_IP:~/temporal-kb/

# Enter kbuser password when prompted
```

**Option B: Via Git (if you have it in a repo)**

```bash
# On the SERVER (as kbuser)
cd ~
git clone https://github.com/yourusername/temporal-kb.git
cd temporal-kb
```

### 4.3 Setup Python Environment

```bash
# Still on server as kbuser
cd ~/temporal-kb

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see: (venv) kbuser@temporal-kb-server:~/temporal-kb$

# Upgrade pip
pip install --upgrade pip

# Install application
pip install -e .

# If you get errors, install dependencies individually:
pip install \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    psycopg2-binary \
    pydantic \
    pydantic-settings \
    pyyaml \
    python-dateutil \
    click \
    rich \
    chromadb \
    sentence-transformers \
    gitpython \
    python-multipart

# Verify installation
kb --help
```

### 4.4 Configure Application

```bash
# Create data directory
mkdir -p ~/kb-data

# Create .env file
nano ~/temporal-kb/.env
```

Paste this configuration (replace password and domain):

```bash
# Database
KB_POSTGRES_URL=postgresql://kbuser:your_very_secure_password_here_123!@localhost:5432/temporal_kb

# Paths
KB_DATA_DIR=/home/kbuser/kb-data

# API Configuration
KB_API_HOST=0.0.0.0
KB_API_PORT=8000
KB_API_CORS_ORIGINS=["https://yourdomain.com","https://api.yourdomain.com"]

# Features
KB_GIT_ENABLED=true
KB_SEMANTIC_SEARCH_ENABLED=true
KB_EMBEDDING_MODEL=all-MiniLM-L6-v2

# Logging
KB_LOG_LEVEL=INFO
KB_LOG_FILE=/home/kbuser/kb-data/kb.log

# Security (generate with: python -c "import secrets; print(secrets.token_hex(32))")
KB_JWT_SECRET=your_jwt_secret_here_generate_a_random_one
KB_API_KEYS=["your-api-key-for-mobile-app"]
```

Save and exit (Ctrl+X, Y, Enter)

### 4.5 Initialize Database

```bash
# Initialize the knowledge base
cd ~/temporal-kb
source venv/bin/activate
kb init

# You should see:
# ✓ Knowledge base initialized at /home/kbuser/kb-data
```

### 4.6 Test API Manually

```bash
# Start the API server
kb serve

# Should see:
# INFO:     Started server process
# INFO:     Uvicorn running on http://0.0.0.0:8000

# Leave this running and open a NEW terminal
# SSH to server again:
ssh kbuser@YOUR_SERVER_IP

# Test the API:
curl http://localhost:8000/health

# Should return: {"status":"healthy","timestamp":"...","version":"0.1.0"}

# Stop the server in the first terminal: Ctrl+C
```

---

## Step 5: Setup Systemd Service (Run API Permanently)

### 5.1 Create Service File

```bash
# Back to root user
exit  # Exit from kbuser

# Create systemd service file
sudo nano /etc/systemd/system/temporal-kb.service
```

Paste this:

```ini
[Unit]
Description=Temporal Knowledge Base API
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=simple
User=kbuser
Group=kbuser
WorkingDirectory=/home/kbuser/temporal-kb
Environment="PATH=/home/kbuser/temporal-kb/venv/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/kbuser/temporal-kb/.env

ExecStart=/home/kbuser/temporal-kb/venv/bin/uvicorn kb.api.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 2 \
    --log-level info

Restart=always
RestartSec=10
StandardOutput=append:/home/kbuser/kb-data/api.log
StandardError=append:/home/kbuser/kb-data/api-error.log

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, Y, Enter)

### 5.2 Enable and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable temporal-kb

# Start the service
sudo systemctl start temporal-kb

# Check status
sudo systemctl status temporal-kb

# Should show:
# ● temporal-kb.service - Temporal Knowledge Base API
#      Active: active (running) since...

# Test it's working
curl http://localhost:8000/health

# View logs
sudo journalctl -u temporal-kb -f
# Press Ctrl+C to stop viewing logs
```

---

## Step 6: Setup Nginx Reverse Proxy

### 6.1 Configure Nginx

```bash
# Create nginx configuration
sudo nano /etc/nginx/sites-available/temporal-kb
```

Paste this (replace `yourdomain.com` with your actual domain):

```nginx
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    listen 80;
    server_name api.yourdomain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/temporal-kb-access.log;
    error_log /var/log/nginx/temporal-kb-error.log;

    # API proxy
    location / {
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket support (for future features)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint (no auth required)
    location /health {
        proxy_pass http://localhost:8000/health;
        access_log off;
    }
}
```

Save and exit.

### 6.2 Enable Site & Test Configuration

```bash
# Create symbolic link to enable site
sudo ln -s /etc/nginx/sites-available/temporal-kb /etc/nginx/sites-enabled/

# Remove default site if exists
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Should show:
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Reload nginx
sudo systemctl reload nginx
```

---

## Step 7: Configure Domain & SSL

### 7.1 Setup DNS (Do this in your domain registrar)

Add an A record:
- **Type:** A
- **Name:** api (or @ for root domain)
- **Value:** YOUR_SERVER_IP
- **TTL:** 300 (5 minutes)

Wait 5-10 minutes for DNS to propagate. Test:

```bash
# On your local machine
nslookup api.yourdomain.com

# Should show your server IP
```

### 7.2 Setup SSL Certificate (Let's Encrypt)

```bash
# On the server
# Install SSL certificate
sudo certbot --nginx -d api.yourdomain.com

# You'll be asked:
# 1. Email address: your@email.com
# 2. Agree to terms: Y
# 3. Share email with EFF: N (your choice)
# 4. Redirect HTTP to HTTPS: 2 (Redirect)

# Should see: Successfully received certificate

# Test auto-renewal
sudo certbot renew --dry-run

# Should show: Congratulations, all simulated renewals succeeded
```

### 7.3 Test HTTPS

```bash
# From your local machine
curl https://api.yourdomain.com/health

# Should return: {"status":"healthy",...}
```

---

## Step 8: Configure Firewall

```bash
# Allow SSH (port 22)
sudo ufw allow 22/tcp

# Allow HTTP (port 80)
sudo ufw allow 80/tcp

# Allow HTTPS (port 443)
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Type: y

# Check status
sudo ufw status

# Should show:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere
```

---

## Step 9: Test Full Setup

### 9.1 Test API Endpoints

```bash
# From your local machine

# Health check
curl https://api.yourdomain.com/health

# Create an entry (replace YOUR_API_KEY with value from .env)
curl -X POST https://api.yourdomain.com/api/v1/entries \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "title": "Test Entry",
    "content": "This is a test entry from the API",
    "entry_type": "note",
    "tags": ["test"]
  }'

# Search entries
curl "https://api.yourdomain.com/api/v1/search?q=test" \
  -H "X-API-Key: YOUR_API_KEY"

# Get recent entries
curl "https://api.yourdomain.com/api/v1/search/recent?limit=5" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 9.2 Test API Documentation

Open in browser:
- **Swagger UI:** https://api.yourdomain.com/docs
- **ReDoc:** https://api.yourdomain.com/redoc

---

## Step 10: Setup Monitoring & Maintenance

### 10.1 Setup Automatic Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-kb.sh
```

```bash
#!/bin/bash

# Backup script for Temporal KB
BACKUP_DIR="/home/kbuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="temporal_kb"
DB_USER="kbuser"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL database
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup data directory
tar -czf $BACKUP_DIR/data_$DATE.tar.gz /home/kbuser/kb-data

# Keep only last 7 days of backups
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "data_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-kb.sh

# Test backup
sudo -u kbuser /usr/local/bin/backup-kb.sh

# Setup daily backup with cron
sudo crontab -e -u kbuser

# Add this line (runs daily at 2 AM):
0 2 * * * /usr/local/bin/backup-kb.sh >> /home/kbuser/kb-data/backup.log 2>&1
```

### 10.2 Monitor Service Health

```bash
# View API logs
sudo journalctl -u temporal-kb -f

# Check service status
sudo systemctl status temporal-kb

# Check nginx status
sudo systemctl status nginx

# Check PostgreSQL status
sudo systemctl status postgresql

# Monitor system resources
htop
```

### 10.3 Useful Management Commands

```bash
# Restart API
sudo systemctl restart temporal-kb

# View API logs
sudo journalctl -u temporal-kb -n 100 --no-pager

# Check disk space
df -h

# Check memory usage
free -h

# Monitor PostgreSQL
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Update application code
su - kbuser
cd ~/temporal-kb
git pull  # or rsync from local
source venv/bin/activate
pip install -e .
exit
sudo systemctl restart temporal-kb
```

---

## Step 11: Mobile App Configuration

Now that your API is running, update your mobile app to use it:

```typescript
// app/services/api.ts

const API_BASE_URL = 'https://api.yourdomain.com/api/v1';
const API_KEY = 'your-api-key-for-mobile-app';  // From .env file

// Rest of the API client code from earlier...
```

---

## Troubleshooting

### API Not Starting

```bash
# Check logs
sudo journalctl -u temporal-kb -n 50

# Check if port is already in use
sudo netstat -tlnp | grep 8000

# Test manually
su - kbuser
cd ~/temporal-kb
source venv/bin/activate
kb serve
```

### Database Connection Issues

```bash
# Test database connection
psql -U kbuser -d temporal_kb -h localhost

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

### Nginx/SSL Issues

```bash
# Test nginx config
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Renew SSL certificate
sudo certbot renew
```

### High Memory Usage

```bash
# Check memory
free -h

# Restart services if needed
sudo systemctl restart temporal-kb
```

---

## Security Checklist

- ✅ SSH key authentication (no password login)
- ✅ Firewall configured (ufw)
- ✅ SSL/TLS certificate installed
- ✅ API key authentication
- ✅ Rate limiting enabled (nginx)
- ✅ PostgreSQL not exposed to internet
- ✅ Regular backups configured
- ✅ Non-root user for application

**Optional but recommended:**
- Setup fail2ban for brute force protection
- Configure automatic security updates
- Setup monitoring (e.g., Netdata, Grafana)

---

## Your VPS is Now Ready! 🎉

**API Endpoint:** `https://api.yourdomain.com`

**Next Steps:**
1. Test all endpoints via Swagger UI: `https://api.yourdomain.com/docs`
2. Build the mobile app (I can help with this next)
3. Import your existing data if you have any

**API Key for Mobile App:** Check `/home/kbuser/temporal-kb/.env` → `KB_API_KEYS`

Want me to help you build the React Native mobile app now?