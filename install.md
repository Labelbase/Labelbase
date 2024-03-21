# Labelbase Dockerized Installation Guide

This guide provides instructions on installing and running Labelbase using Docker on your local machine or server.

## Install and Run Docker

Ensure Docker is installed and running on your machine.

Download Docker from Docker's official website and follow the installation instructions for your OS.

For Debian VM on DigitalOcean, use:

```bash
# Update and upgrade the system (upgrade if using a fresh system or if you're confident with the process)
apt-get update && apt-get upgrade

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```


**Note:** Use Docker version >=25.0.4.

Install necessary tools and check if everything is working as expected.

```
apt-get install docker-compose --yes
apt-get install git --yes
apt-get install nginx --yes
apt-get install certbot --yes
apt-get install python3-certbot-nginx --yes

# Check installed versions
docker --version
nginx -v


```

Then create a certificate for your domain. We are using my.labelbase.space in this example.

```bash

# Set up Certbot with nginx
certbot --nginx -d my.labelbase.space

```

## Get the Sources from GitHub

Clone the Labelbase repository:

```bash
git clone https://github.com/Labelbase/Labelbase/
cd Labelbase
```



## Set up MySQL Environment Variables

### Option A: Automatic Setup (Recommended)
Generate MySQL environment variables using OpenSSL:

Run `./make-exports.sh` script to generate exports.sh.

### Option B: Manual Setup
Create `exports.sh` with MySQL passwords as environment variables:

```bash
#!/bin/bash
# Export passwords for Labelbase
export MYSQL_ROOT_PASSWORD="<YOUR ROOT PASSWORD>"
export MYSQL_PASSWORD="<YOUR MYSQL PASSWORD>"
```

Don't forget to back up `exports.sh`!

## Build and Run Labelbase

Source environment variables and run Labelbase:
```bash
source exports.sh && ./build-and-run-labelbase.sh
```

## Accessing Labelbase
### Locally

Access Labelbase locally at http://127.0.0.1:8080 or http://localhost:8080.

For server access on localhost, install lynx and run `lynx 127.0.0.1:8080`.

### From the Internet
Configure nginx to link your domain to the running Labelbase instance.

Edit `/etc/nginx/sites-enabled/default` and replace the existing `location /` block with:

```bash
location / {
    proxy_pass http://localhost:8080;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
}
```

Restart `nginx`, then access your domain (or IP address) in your browser.
