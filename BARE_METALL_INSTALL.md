# Labelbase Bare Metal Installation Guide

This guide will help you install and run Labelbase directly on macOS and Linux systems, based on the RaspiBlitz installation script.

## Prerequisites

### Common Requirements
- Git
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv
- MySQL/MariaDB server

### System-Specific Requirements

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install python3 mysql git
brew install pkg-config mysql-client
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install required packages
sudo apt install -y \
    mariadb-server \
    mariadb-client \
    default-libmysqlclient-dev \
    build-essential \
    python3 \
    python3-pip \
    python3-venv \
    git \
    libpcre3-dev
```

#### Linux (CentOS/RHEL/Fedora)
```bash
# For CentOS/RHEL 8+
sudo dnf install -y \
    mariadb-server \
    mariadb-devel \
    python3 \
    python3-pip \
    python3-virtualenv \
    git \
    gcc \
    gcc-c++ \
    make

# For older versions, use yum instead of dnf
```

## Installation Steps

### 1. Create Application User (Optional but Recommended)

#### macOS
```bash
# Create a new user (optional on macOS for development)
sudo dscl . -create /Users/labelbase
sudo dscl . -create /Users/labelbase UserShell /bin/bash
sudo dscl . -create /Users/labelbase RealName "Labelbase User"
sudo dscl . -create /Users/labelbase UniqueID 1001
sudo dscl . -create /Users/labelbase PrimaryGroupID 20
sudo dscl . -create /Users/labelbase NFSHomeDirectory /Users/labelbase
sudo createhomedir -c -u labelbase
```

#### Linux
```bash
# Create system user
sudo adduser --system --group --shell /bin/bash --home /home/labelbase labelbase
sudo -u labelbase cp -r /etc/skel/. /home/labelbase/
```

### 2. Start Database Service

#### macOS
```bash
# Start MySQL service
brew services start mysql

# Secure the installation
mysql_secure_installation
```

#### Linux
```bash
# Start MariaDB service
sudo systemctl enable mariadb
sudo systemctl start mariadb

# Secure the installation
sudo mysql_secure_installation
```

### 3. Download and Setup Labelbase

```bash
# Switch to labelbase user (if created) or use your regular user
# sudo su - labelbase  # (if using dedicated user)

# Set variables
LABELBASE_HOME="$HOME"  # or /home/labelbase if using dedicated user
LABELBASE_REPO="https://github.com/Labelbase/Labelbase/"
LABELBASE_VERSION="2.2.1"

# Clone the repository
git clone $LABELBASE_REPO $LABELBASE_HOME/labelbase
cd $LABELBASE_HOME/labelbase

# Checkout specific version
git checkout $LABELBASE_VERSION

# Create virtual environment
python3 -m venv $LABELBASE_HOME/ENV

# Activate virtual environment
source $LABELBASE_HOME/ENV/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install --no-cache-dir -r $LABELBASE_HOME/labelbase/django/requirements.txt
```

### 4. Database Configuration

```bash
# Generate a secure password
MYSQL_PASSWORD=$(openssl rand -base64 32 | tr -d '+/' | fold -w 32 | head -n 1)

# Create exports file
cat > $LABELBASE_HOME/exports.sh << EOF
export MYSQL_PASSWORD=$MYSQL_PASSWORD
export DATABASE_URL=mysql://ulabelbase:$MYSQL_PASSWORD@localhost:3306/labelbase
EOF

chmod 755 $LABELBASE_HOME/exports.sh
```

#### Create Database and User

##### macOS
```bash
# Connect to MySQL
mysql -u root -p

# In MySQL prompt:
CREATE DATABASE labelbase;
CREATE USER 'ulabelbase'@'localhost' IDENTIFIED BY 'YOUR_GENERATED_PASSWORD';
GRANT ALL PRIVILEGES ON labelbase.* TO 'ulabelbase'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

##### Linux
```bash
# Connect to MariaDB
sudo mysql

# In MariaDB prompt:
CREATE DATABASE labelbase;
CREATE USER 'ulabelbase'@'localhost' IDENTIFIED BY 'YOUR_GENERATED_PASSWORD';
GRANT ALL PRIVILEGES ON labelbase.* TO 'ulabelbase'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Note:** Replace `YOUR_GENERATED_PASSWORD` with the password generated in the previous step.

### 5. Django Setup

```bash
# Navigate to Django directory
cd $LABELBASE_HOME/labelbase/django

# Activate virtual environment and load environment variables
source $LABELBASE_HOME/ENV/bin/activate
source $LABELBASE_HOME/exports.sh

# Run Django migrations
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create a superuser (optional)
python manage.py createsuperuser
```

### 6. Running Labelbase

#### Development Mode
```bash
# Activate environment
source $LABELBASE_HOME/ENV/bin/activate
source $LABELBASE_HOME/exports.sh

# Navigate to Django directory
cd $LABELBASE_HOME/labelbase/django

# Run development server
python manage.py runserver 0.0.0.0:8089

# Access at: http://localhost:8089
```

#### Production Mode (using Gunicorn)
```bash
# Install Gunicorn if not already installed
pip install gunicorn

# Run with Gunicorn
source $LABELBASE_HOME/ENV/bin/activate
source $LABELBASE_HOME/exports.sh
cd $LABELBASE_HOME/labelbase/django

gunicorn labellabor.wsgi:application -b 0.0.0.0:8089 --reload
```

## Creating System Services (Optional)

### macOS (using LaunchAgent)

Create a plist file at `~/Library/LaunchAgents/com.labelbase.app.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.labelbase.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /Users/labelbase/labelbase/django && source /Users/labelbase/ENV/bin/activate && source /Users/labelbase/exports.sh && gunicorn labellabor.wsgi:application -b 0.0.0.0:8089</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/labelbase/labelbase.out</string>
    <key>StandardErrorPath</key>
    <string>/Users/labelbase/labelbase.err</string>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.labelbase.app.plist
```

### Linux (using systemd)

Create `/etc/systemd/system/labelbase.service`:

```ini
[Unit]
Description=Labelbase Application
After=mariadb.service

[Service]
Type=simple
User=labelbase
WorkingDirectory=/home/labelbase/labelbase/django
Environment="HOME_PATH=/home/labelbase"
ExecStart=/bin/bash -c 'source /home/labelbase/ENV/bin/activate && source /home/labelbase/exports.sh && gunicorn labellabor.wsgi:application -b 0.0.0.0:8089'
Restart=always
TimeoutSec=120
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable labelbase
sudo systemctl start labelbase
sudo systemctl status labelbase
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Ensure MySQL/MariaDB is running
   - Verify database credentials in `exports.sh`
   - Check if the database user has proper permissions

2. **Python Package Issues**
   - Make sure virtual environment is activated
   - Try upgrading pip: `pip install --upgrade pip`
   - Install packages one by one if requirements.txt fails

3. **Port Already in Use**
   - Change the port in the run command: `gunicorn ... -b 0.0.0.0:8090`
   - Find and kill processes using the port: `lsof -ti:8089 | xargs kill -9`

4. **Permission Errors**
   - Ensure proper ownership of files: `sudo chown -R labelbase:labelbase /home/labelbase`
   - Check file permissions: `chmod 755 /home/labelbase/exports.sh`

### Logs and Debugging

- **Development server logs**: Displayed in terminal
- **Gunicorn logs**: Use `--log-file` flag for logging
- **System service logs** (Linux): `sudo journalctl -u labelbase -f`
- **Database logs**: Check MySQL/MariaDB error logs

### Stopping the Application

```bash
# If running in development mode
Ctrl+C

# If running as system service
# macOS:
launchctl unload ~/Library/LaunchAgents/com.labelbase.app.plist

# Linux:
sudo systemctl stop labelbase
```

## Security Considerations

1. **Firewall Configuration**
   - Only expose necessary ports
   - Consider using a reverse proxy (nginx/apache) for production

2. **Database Security**
   - Use strong passwords
   - Limit database user permissions
   - Consider encrypting database connections

3. **Application Security**
   - Keep dependencies updated
   - Use HTTPS in production
   - Regular security updates

4. **File Permissions**
   - Ensure proper file ownership and permissions
   - Limit access to configuration files

This guide provides a foundation for running Labelbase on bare metal systems. Adjust paths, ports, and configurations according to your specific needs and security requirements.
