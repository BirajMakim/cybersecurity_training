# Deployment Guide for Cybersecurity Training Platform

This guide will help you deploy the Cybersecurity Training Platform to production.

## Prerequisites

1. A production server (e.g., DigitalOcean, AWS, or any VPS)
2. Domain name (optional but recommended)
3. PostgreSQL database
4. SMTP server for emails
5. SSL certificate (Let's Encrypt recommended)

## Server Setup

1. Update your server:
```bash
sudo apt update && sudo apt upgrade -y
```

2. Install required packages:
```bash
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib
```

3. Create a PostgreSQL database:
```bash
sudo -u postgres psql
CREATE DATABASE your_db_name;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';
ALTER ROLE your_db_user SET client_encoding TO 'utf8';
ALTER ROLE your_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your_db_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your_db_name TO your_db_user;
\q
```

## Application Setup

1. Create a project directory:
```bash
mkdir /var/www/cybersecurity_training
cd /var/www/cybersecurity_training
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Clone your repository:
```bash
git clone your-repository-url .
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a .env file:
```bash
nano .env
```

Add the following environment variables:
```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=your-smtp-server
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email
```

6. Collect static files:
```bash
python manage.py collectstatic
```

7. Run migrations:
```bash
python manage.py migrate
```

8. Create a superuser:
```bash
python manage.py createsuperuser
```

## Gunicorn Setup

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/cybersecurity_training.service
```

Add the following content:
```ini
[Unit]
Description=Gunicorn daemon for Cybersecurity Training Platform
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/cybersecurity_training
ExecStart=/var/www/cybersecurity_training/venv/bin/gunicorn --workers 3 --bind unix:/var/www/cybersecurity_training/cybersecurity_training.sock cybersecurity_training.wsgi:application

[Install]
WantedBy=multi-user.target
```

2. Start and enable the service:
```bash
sudo systemctl start cybersecurity_training
sudo systemctl enable cybersecurity_training
```

## Nginx Setup

1. Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/cybersecurity_training
```

Add the following configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/cybersecurity_training;
    }

    location /media/ {
        root /var/www/cybersecurity_training;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/cybersecurity_training/cybersecurity_training.sock;
    }
}
```

2. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/cybersecurity_training /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## SSL Setup (Let's Encrypt)

1. Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

2. Obtain SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Final Steps

1. Set proper permissions:
```bash
sudo chown -R www-data:www-data /var/www/cybersecurity_training
sudo chmod -R 755 /var/www/cybersecurity_training
```

2. Restart all services:
```bash
sudo systemctl restart cybersecurity_training
sudo systemctl restart nginx
```

## Monitoring and Maintenance

1. Check application logs:
```bash
sudo journalctl -u cybersecurity_training
```

2. Check Nginx logs:
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

3. Regular maintenance:
- Keep your system updated
- Monitor disk space
- Backup your database regularly
- Check SSL certificate expiration

## Backup Strategy

1. Database backup:
```bash
pg_dump -U your_db_user your_db_name > backup.sql
```

2. Files backup:
```bash
tar -czf backup.tar.gz /var/www/cybersecurity_training
```

## Troubleshooting

1. If the application is not running:
```bash
sudo systemctl status cybersecurity_training
```

2. If Nginx is not working:
```bash
sudo nginx -t
sudo systemctl status nginx
```

3. Check file permissions:
```bash
ls -la /var/www/cybersecurity_training
```

For any issues, check the logs mentioned in the Monitoring section. 