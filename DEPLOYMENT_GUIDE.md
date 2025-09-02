# Deployment Guide

## Overview
This guide provides comprehensive instructions for deploying SarvanOM in various environments, from development to production.

## Deployment Options

### 1. Local Development
- **Purpose**: Development and testing
- **Resources**: Minimal
- **Setup Time**: 15 minutes

### 2. Docker Development
- **Purpose**: Isolated development environment
- **Resources**: Medium
- **Setup Time**: 10 minutes

### 3. Production Server
- **Purpose**: Production deployment
- **Resources**: High
- **Setup Time**: 45 minutes

### 4. Cloud Deployment
- **Purpose**: Scalable production deployment
- **Resources**: Variable
- **Setup Time**: 60 minutes

## Local Development Deployment

### Prerequisites
```bash
# Python 3.11+
python --version

# Node.js 18+
node --version

# Git
git --version
```

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/sarvanom.git
cd sarvanom
```

#### 2. Setup Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Setup Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

#### 4. Configure Environment
```bash
# Copy template
cp env.docker.template .env

# Edit with your configuration
nano .env
```

#### 5. Start Services
```bash
# Start backend
python -m uvicorn services.gateway.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend (new terminal)
cd frontend
npm run dev
```

## Docker Development Deployment

### Prerequisites
```bash
# Docker 20.10+
docker --version

# Docker Compose 2.0+
docker-compose --version
```

### Step-by-Step Setup

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/sarvanom.git
cd sarvanom
```

#### 2. Configure Environment
```bash
# Copy template
cp env.docker.template .env

# Edit configuration
nano .env
```

#### 3. Start Services
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

#### 4. Verify Deployment
```bash
# Test API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

## Production Server Deployment

### Prerequisites
- Ubuntu 20.04+ server
- 8GB+ RAM
- 50GB+ storage
- Public IP address
- Domain name (optional)

### Step-by-Step Setup

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx redis-server postgresql postgresql-contrib git curl

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### 2. Setup PostgreSQL
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE sarvanom;"
sudo -u postgres psql -c "CREATE USER sarvanom_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sarvanom TO sarvanom_user;"
```

#### 3. Setup Redis
```bash
# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
```

#### 4. Deploy Application
```bash
# Clone repository
cd /opt
sudo git clone https://github.com/your-org/sarvanom.git
sudo chown -R $USER:$USER sarvanom
cd sarvanom

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd frontend
npm install
npm run build
cd ..
```

#### 5. Configure Environment
```bash
# Copy production template
cp env.docker.template .env.prod

# Edit with production values
nano .env.prod

# Set production environment
export ENV_FILE=.env.prod
```

#### 6. Setup Systemd Services

##### Backend Service
```bash
sudo nano /etc/systemd/system/sarvanom-backend.service
```

```ini
[Unit]
Description=SarvanOM Backend Service
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=sarvanom
WorkingDirectory=/opt/sarvanom
Environment=PATH=/opt/sarvanom/venv/bin
ExecStart=/opt/sarvanom/venv/bin/python -m uvicorn services.gateway.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

##### Frontend Service
```bash
sudo nano /etc/systemd/system/sarvanom-frontend.service
```

```ini
[Unit]
Description=SarvanOM Frontend Service
After=network.target

[Service]
Type=simple
User=sarvanom
WorkingDirectory=/opt/sarvanom/frontend
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 7. Start Services
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start services
sudo systemctl start sarvanom-backend
sudo systemctl start sarvanom-frontend

# Enable services
sudo systemctl enable sarvanom-backend
sudo systemctl enable sarvanom-frontend

# Check status
sudo systemctl status sarvanom-backend
sudo systemctl status sarvanom-frontend
```

#### 8. Configure Nginx
```bash
sudo nano /etc/nginx/sites-available/sarvanom
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
    }
}
```

#### 9. Enable Site
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/sarvanom /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 10. Setup SSL (Let's Encrypt)
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Test renewal
sudo certbot renew --dry-run
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Setup
```bash
# Launch EC2 instance
# - Instance Type: t3.large or larger
# - AMI: Ubuntu 20.04 LTS
# - Storage: 50GB+ GP2
# - Security Group: Allow HTTP(80), HTTPS(443), SSH(22)
```

#### 2. Install Dependencies
```bash
# Same as production server setup
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx redis-server postgresql postgresql-contrib git curl
```

#### 3. Use RDS for PostgreSQL
```bash
# Create RDS instance
# - Engine: PostgreSQL 14+
# - Instance: db.t3.micro (free tier) or larger
# - Storage: 20GB+ GP2
# - Security Group: Allow inbound from EC2 security group
```

#### 4. Use ElastiCache for Redis
```bash
# Create ElastiCache cluster
# - Engine: Redis 6.0+
# - Node Type: cache.t3.micro (free tier) or larger
# - Security Group: Allow inbound from EC2 security group
```

#### 5. Update Environment
```bash
# Edit .env.prod with RDS and ElastiCache endpoints
nano .env.prod
```

### Google Cloud Deployment

#### 1. Compute Engine Setup
```bash
# Create VM instance
# - Machine Type: e2-medium or larger
# - Boot Disk: Ubuntu 20.04 LTS, 50GB+
# - Firewall: Allow HTTP, HTTPS, SSH
```

#### 2. Use Cloud SQL
```bash
# Create Cloud SQL instance
# - Database Version: PostgreSQL 14
# - Machine Type: db-f1-micro (free tier) or larger
# - Storage: 20GB+
```

#### 3. Use Memorystore
```bash
# Create Memorystore instance
# - Version: Redis 6.0
# - Tier: Basic
# - Size: 1GB+
```

### Azure Deployment

#### 1. Virtual Machine Setup
```bash
# Create VM
# - Size: Standard_B2s or larger
# - OS: Ubuntu 20.04 LTS
# - Disk: 50GB+ Premium SSD
# - Network: Allow HTTP, HTTPS, SSH
```

#### 2. Use Azure Database for PostgreSQL
```bash
# Create database
# - Server: Basic tier (free) or larger
# - Version: PostgreSQL 14
# - Storage: 20GB+
```

#### 3. Use Azure Cache for Redis
```bash
# Create cache
# - Pricing Tier: Basic (free) or larger
# - Size: 250MB+
```

## Monitoring and Maintenance

### 1. Log Management
```bash
# View application logs
sudo journalctl -u sarvanom-backend -f
sudo journalctl -u sarvanom-frontend -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Performance Monitoring
```bash
# System resources
htop
iotop
nethogs

# Application metrics
curl http://localhost:8000/metrics
```

### 3. Backup Strategy
```bash
# Database backup
pg_dump -h localhost -U sarvanom_user sarvanom > backup_$(date +%Y%m%d).sql

# Application backup
tar -czf sarvanom_backup_$(date +%Y%m%d).tar.gz /opt/sarvanom

# Automated backup script
sudo crontab -e
# Add: 0 2 * * * /opt/sarvanom/scripts/backup.sh
```

### 4. Update Process
```bash
# Pull latest changes
cd /opt/sarvanom
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Rebuild frontend
cd frontend
npm install
npm run build
cd ..

# Restart services
sudo systemctl restart sarvanom-backend
sudo systemctl restart sarvanom-frontend
```

## Security Considerations

### 1. Firewall Configuration
```bash
# UFW setup
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw status
```

### 2. SSL/TLS Configuration
```bash
# Strong SSL configuration in Nginx
sudo nano /etc/nginx/snippets/ssl-params.conf
```

### 3. Access Control
```bash
# Restrict SSH access
sudo nano /etc/ssh/sshd_config
# Change: PermitRootLogin no
# Add: AllowUsers your_username

# Restart SSH
sudo systemctl restart ssh
```

### 4. Regular Security Updates
```bash
# Automated security updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

## Troubleshooting

### Common Issues

#### 1. Service Won't Start
```bash
# Check logs
sudo journalctl -u sarvanom-backend -n 50

# Check dependencies
sudo systemctl status postgresql
sudo systemctl status redis-server
```

#### 2. Database Connection Issues
```bash
# Test PostgreSQL
psql -h localhost -U sarvanom_user -d sarvanom

# Check PostgreSQL status
sudo systemctl status postgresql
```

#### 3. Frontend Not Loading
```bash
# Check frontend service
sudo systemctl status sarvanom-frontend

# Check Nginx configuration
sudo nginx -t
sudo systemctl status nginx
```

#### 4. SSL Certificate Issues
```bash
# Check certificate
sudo certbot certificates

# Renew manually
sudo certbot renew
```

## Performance Optimization

### 1. Database Optimization
```sql
-- PostgreSQL tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;

-- Reload configuration
SELECT pg_reload_conf();
```

### 2. Application Optimization
```bash
# Gunicorn with multiple workers
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker services.gateway.main:app --bind 0.0.0.0:8000
```

### 3. Nginx Optimization
```nginx
# Enable gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

# Enable caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## Conclusion
This deployment guide covers the essential steps for deploying SarvanOM in various environments. For production deployments, ensure proper security measures, monitoring, and backup strategies are in place.
