# Labelbase Backup and Migration Guide

A comprehensive guide for safely backing up your Labelbase database and running Django migrations.

## Table of Contents
- [Why Backup?](#why-backup)
- [Quick Backup](#quick-backup)
- [Automated Backup Script](#automated-backup-script)
- [Running Migrations Safely](#running-migrations-safely)
- [Upgrading Labelbase](#upgrading-labelbase)
- [Restoring from Backup](#restoring-from-backup)
- [Scheduled Backups](#scheduled-backups)
- [Best Practices](#best-practices)

---

## Why Backup?

**Always backup before running migrations!** Migrations can:
- Alter database table structures in irreversible ways
- Delete data if there are bugs in the migration code
- Fail mid-execution, leaving your database inconsistent
- Introduce conflicts with existing data

A backup takes 30 seconds. Recovery without one could take hours or days.

---

## Quick Backup

From your Labelbase directory:

```bash
# Navigate to Labelbase directory
cd Labelbase

# Source environment variables
source exports.sh

# Create backup with timestamp
docker-compose exec -T labelbase_mysql mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" labelbase > backup_$(date +%Y%m%d_%H%M%S).sql
```

This creates a backup file like `backup_20250119_143022.sql`.

### Backup config.ini (Important!)

The `config.ini` file contains encryption keys and other critical settings. Always back it up too:

```bash
# Navigate to Labelbase directory
cd Labelbase

# Source environment variables
source exports.sh

# Create backup with timestamp
docker-compose exec -T labelbase_django cat /app/config.ini > backup_$(date +%Y%m%d_%H%M%S)_config.ini
```

This creates a backup file like `backup_20250119_143022_config.ini`.

---

## Automated Backup Script

Create a reusable backup script that handles everything automatically.

### Create the Script

Save this as `backup-labelbase.sh` in your Labelbase directory:

```bash
#!/bin/bash

# Labelbase Database Backup Script
# Usage: ./backup-labelbase.sh

# Configuration
LABELBASE_DIR="/path/to/Labelbase"  # CHANGE THIS to your actual path
BACKUP_DIR="$LABELBASE_DIR/backups"
KEEP_BACKUPS=10  # Number of backups to keep

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to Labelbase directory
cd "$LABELBASE_DIR" || exit 1

# Source environment variables for MySQL passwords
if [ ! -f "exports.sh" ]; then
    echo -e "${RED}✗ Error: exports.sh not found!${NC}"
    echo "Make sure you're in the Labelbase directory and exports.sh exists."
    exit 1
fi

source exports.sh

# Check if MySQL password is set
if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    echo -e "${RED}✗ Error: MYSQL_ROOT_PASSWORD not set!${NC}"
    echo "Make sure exports.sh contains the MySQL password."
    exit 1
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/labelbase_backup_$TIMESTAMP.sql"
CONFIG_BACKUP_FILE="$BACKUP_DIR/config_backup_$TIMESTAMP.ini"

echo -e "${YELLOW}Starting backup...${NC}"
echo "Database backup: $BACKUP_FILE"
echo "Config backup: $CONFIG_BACKUP_FILE"

# Backup config.ini first (contains encryption keys!)
echo "Backing up config.ini..."
docker-compose exec -T labelbase_django cat /app/config.ini > "$CONFIG_BACKUP_FILE"

if [ $? -eq 0 ] && [ -s "$CONFIG_BACKUP_FILE" ]; then
    echo -e "${GREEN}✓ Config backup successful${NC}"
else
    echo -e "${YELLOW}⚠ Config backup failed or file is empty${NC}"
fi

# Create database backup
docker-compose exec -T labelbase_mysql mysqldump \
    -u root \
    -p"${MYSQL_ROOT_PASSWORD}" \
    --single-transaction \
    --quick \
    --lock-tables=false \
    labelbase > "$BACKUP_FILE"

# Check if backup was successful
if [ $? -eq 0 ] && [ -s "$BACKUP_FILE" ]; then
    echo -e "${GREEN}✓ Backup successful!${NC}"

    # Get file size
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "Backup size: $SIZE"

    # Compress backup to save space
    echo "Compressing backup..."
    gzip "$BACKUP_FILE"

    if [ $? -eq 0 ]; then
        COMPRESSED_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
        echo -e "${GREEN}✓ Compressed to: $COMPRESSED_SIZE${NC}"
        echo "Backup location: ${BACKUP_FILE}.gz"
    else
        echo -e "${YELLOW}⚠ Compression failed, keeping uncompressed backup${NC}"
    fi

    # Clean up old backups (keep only last N backups)
    echo "Cleaning up old backups (keeping last $KEEP_BACKUPS)..."
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/labelbase_backup_*.sql.gz 2>/dev/null | wc -l)

    if [ "$BACKUP_COUNT" -gt "$KEEP_BACKUPS" ]; then
        ls -t "$BACKUP_DIR"/labelbase_backup_*.sql.gz | tail -n +$((KEEP_BACKUPS + 1)) | xargs -r rm
        echo -e "${GREEN}✓ Cleaned up old backups${NC}"
    else
        echo "No cleanup needed ($BACKUP_COUNT backups exist)"
    fi

    echo ""
    echo -e "${GREEN}=== Backup Complete ===${NC}"
    echo "Database: ${BACKUP_FILE}.gz"
    echo "Config: ${CONFIG_BACKUP_FILE}"

else
    echo -e "${RED}✗ Backup failed!${NC}"

    # Remove empty or failed backup file
    [ -f "$BACKUP_FILE" ] && rm "$BACKUP_FILE"

    echo "Troubleshooting:"
    echo "1. Check if MySQL container is running: docker-compose ps"
    echo "2. Check MySQL logs: docker-compose logs labelbase_mysql"
    echo "3. Verify password in exports.sh"
    exit 1
fi
```

### Make Script Executable

```bash
chmod +x backup-labelbase.sh
```

### Edit Configuration

Open `backup-labelbase.sh` and change this line to your actual Labelbase path:

```bash
LABELBASE_DIR="/path/to/Labelbase"  # CHANGE THIS!
```

For example:
```bash
LABELBASE_DIR="/root/Labelbase"
# or
LABELBASE_DIR="/home/username/Labelbase"
```

### Run the Backup

```bash
./backup-labelbase.sh
```

You'll see output like:
```
Starting backup...
Backup file: /path/to/Labelbase/backups/labelbase_backup_20250119_143022.sql
✓ Backup successful!
Backup size: 15M
Compressing backup...
✓ Compressed to: 3.2M
Backup location: /path/to/Labelbase/backups/labelbase_backup_20250119_143022.sql.gz
Cleaning up old backups (keeping last 10)...
No cleanup needed (3 backups exist)

=== Backup Complete ===
Location: /path/to/Labelbase/backups/labelbase_backup_20250119_143022.sql.gz
```

---

## Running Migrations Safely

**Always follow this order:**

### Step 1: Create a Backup

```bash
./backup-labelbase.sh
```

### Step 2: Check Migration Status

```bash
source exports.sh
docker-compose exec labelbase_django python manage.py showmigrations
```

This shows which migrations are applied (marked with `[X]`) and pending (marked with `[ ]`).

### Step 3: Review Pending Migrations

Look for any unapplied migrations. If you see pending migrations for critical apps, review them carefully.

### Step 4: Apply Migrations

```bash
# If you've modified models, create new migrations first
docker-compose exec labelbase_django python manage.py makemigrations

# Apply all pending migrations
docker-compose exec labelbase_django python manage.py migrate
```

### Step 5: Verify Application

After migrations complete:
1. Check for any error messages
2. Visit your Labelbase site
3. Test critical functionality
4. Check Django logs: `docker-compose logs labelbase_django`

### Step 6: If Something Goes Wrong

If migrations fail or break functionality, restore from backup (see below).

---

## Upgrading Labelbase

When new versions of Labelbase are released, follow this workflow to safely upgrade.

### Complete Upgrade Workflow

**Step 1: Backup First (Critical!)**

```bash
cd Labelbase
./backup-labelbase.sh
```

**Step 2: Pull Latest Code**

```bash
git pull origin master
```

**Step 3: Rebuild Containers (if needed)**

If dependencies or Docker configuration changed:

```bash
source exports.sh && docker-compose up --build -d
```

Or use the main script:

```bash
source exports.sh && ./build-and-run-labelbase.sh
```

**⚠️ IMPORTANT**: These commands are SAFE - they rebuild containers but preserve your data in Docker volumes. Your database and uploaded files are NOT deleted.

**❌ DANGER ZONE - Commands that DELETE data:**
```bash
# NEVER run these unless you want to lose ALL data:
docker-compose down -v    # The -v flag deletes volumes = data loss!
docker volume prune       # Deletes unused volumes
docker system prune -a    # Nuclear option - deletes everything
```

**Step 4: Apply Migrations and collect static files **

```bash
source exports.sh
docker-compose exec labelbase_django python manage.py showmigrations
docker-compose exec labelbase_django python manage.py migrate
docker-compose exec labelbase_django python  manage.py collectstatic --noinput

```

**Step 5: Restart Services**

```bash
docker-compose restart labelbase_django
```

**Step 6: Verify Everything Works**

1. Visit your Labelbase site
2. Test critical functionality
3. Check logs: `docker-compose logs -f labelbase_django`

### Quick Upgrade Script

Create `update-and-migrate.sh` for a streamlined upgrade process:

```bash
#!/bin/bash

# Labelbase Quick Update & Migration Script
# Usage: source exports.sh && ./update-and-migrate.sh

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}=== Labelbase Update & Migrate ===${NC}"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Not in Labelbase directory (docker-compose.yml not found)${NC}"
    exit 1
fi

# Check env vars
if [[ -z "${MYSQL_ROOT_PASSWORD}" ]]; then
    echo -e "${RED}Error: Run 'source exports.sh' first!${NC}"
    exit 1
fi

# Step 1: Backup
echo -e "${YELLOW}Step 1: Creating backup...${NC}"
if [ -f "backup-labelbase.sh" ]; then
    ./backup-labelbase.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}Backup failed! Aborting upgrade.${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ Warning: backup-labelbase.sh not found, skipping backup${NC}"
    read -p "Continue without backup? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo "Upgrade cancelled."
        exit 0
    fi
fi

# Step 2: Pull latest code
echo ""
echo -e "${YELLOW}Step 2: Pulling latest changes...${NC}"
git pull origin master

if [ $? -ne 0 ]; then
    echo -e "${RED}Git pull failed!${NC}"
    exit 1
fi

# Step 3: Check for pending migrations
echo ""
echo -e "${YELLOW}Step 3: Checking for migrations...${NC}"
PENDING=$(docker-compose exec -T labelbase_django python manage.py showmigrations --plan 2>/dev/null | grep "\[ \]" | wc -l)

if [ $PENDING -gt 0 ]; then
    echo -e "${YELLOW}Found $PENDING pending migration(s)${NC}"

    # Show what will be migrated
    echo "Pending migrations:"
    docker-compose exec -T labelbase_django python manage.py showmigrations | grep "\[ \]"

    echo ""
    read -p "Apply migrations now? (y/n): " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Applying migrations..."
        docker-compose exec -T labelbase_django python manage.py migrate --noinput

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ Migrations applied successfully${NC}"
        else
            echo -e "${RED}✗ Migrations failed!${NC}"
            echo "Check logs: docker-compose logs labelbase_django"
            exit 1
        fi
    else
        echo -e "${YELLOW}⚠ Skipping migrations${NC}"
        echo "Run manually later: docker-compose exec labelbase_django python manage.py migrate"
    fi
else
    echo -e "${GREEN}✓ No pending migrations${NC}"
fi

# Step 4: Restart Django
echo ""
echo -e "${YELLOW}Step 4: Restarting Django...${NC}"
docker-compose restart labelbase_django

echo ""
echo -e "${GREEN}=== Update Complete! ===${NC}"
echo "Check logs: docker-compose logs -f labelbase_django"
echo "Visit your site to verify everything works"
```

Make it executable:

```bash
chmod +x update-and-migrate.sh
```

### Using the Quick Upgrade Script

```bash
# Navigate to Labelbase
cd Labelbase

# Source environment and run update
source exports.sh && ./update-and-migrate.sh
```

The script will:
1. ✓ Create automatic backup
2. ✓ Pull latest code from git
3. ✓ Detect pending migrations
4. ✓ Ask for confirmation before applying
5. ✓ Restart services
6. ✓ Provide verification steps

### When to Rebuild vs. Restart

**Just restart** (`docker-compose restart`) when:
- Only Django code changed (Python files)
- No dependency updates
- No Dockerfile changes
- Fastest option

**Full rebuild** (`docker-compose up --build -d`) when:
- requirements.txt changed
- Dockerfile modified
- New system packages needed
- Docker configuration changed

**Data Safety Note**: Both `restart` and `--build` are SAFE - they preserve your data. Docker stores your database and files in **volumes** that persist across rebuilds.

If unsure, rebuild - it's safer and only takes a minute longer.

### What Actually Deletes Data

Only these commands delete data (requires `-v` flag):

```bash
# DANGER: This deletes ALL data including database!
docker-compose down -v

# To safely stop without deleting data, use:
docker-compose down          # Safe - keeps volumes
docker-compose stop          # Safe - just stops containers
```

**Rule of thumb**: If you see `-v` flag, your data is at risk!

### Rollback After Failed Upgrade

If something goes wrong:

```bash
# 1. Stop services
docker-compose down

# 2. Restore previous code
git reset --hard HEAD~1

# 3. Restore database
./restore-labelbase.sh backups/labelbase_backup_TIMESTAMP.sql.gz

# 4. Restart
source exports.sh && docker-compose up -d
```

---

## Restoring from Backup

If something goes wrong, you can restore your database from a backup.

### Quick Restore

```bash
# Navigate to Labelbase directory
cd Labelbase

# Source environment variables
source exports.sh

# Stop Django to prevent conflicts
docker-compose stop labelbase_django

# Decompress and restore backup
gunzip -c backups/labelbase_backup_20250119_143022.sql.gz | \
    docker-compose exec -T labelbase_mysql mysql -u root -p"${MYSQL_ROOT_PASSWORD}" labelbase

# Restart all services
docker-compose up -d

# Check logs
docker-compose logs -f labelbase_django
```

### Restore Script (Optional)

Create `restore-labelbase.sh`:

```bash
#!/bin/bash

# Labelbase Database Restore Script
# Usage: ./restore-labelbase.sh <backup-file>

LABELBASE_DIR="/path/to/Labelbase"  # CHANGE THIS
BACKUP_FILE="$1"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if backup file provided
if [ -z "$BACKUP_FILE" ]; then
    echo -e "${RED}✗ Error: No backup file specified${NC}"
    echo "Usage: ./restore-labelbase.sh <backup-file>"
    echo ""
    echo "Available backups:"
    ls -lh "$LABELBASE_DIR/backups/"*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    echo -e "${RED}✗ Error: Backup file not found: $BACKUP_FILE${NC}"
    exit 1
fi

# Change to Labelbase directory
cd "$LABELBASE_DIR" || exit 1

# Source environment variables
source exports.sh

echo -e "${YELLOW}⚠ WARNING: This will overwrite your current database!${NC}"
echo "Backup file: $BACKUP_FILE"
read -p "Are you sure you want to continue? (yes/no): " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

echo "Stopping Django container..."
docker-compose stop labelbase_django

echo "Restoring database..."

# Check if file is compressed
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | \
        docker-compose exec -T labelbase_mysql mysql -u root -p"${MYSQL_ROOT_PASSWORD}" labelbase
else
    cat "$BACKUP_FILE" | \
        docker-compose exec -T labelbase_mysql mysql -u root -p"${MYSQL_ROOT_PASSWORD}" labelbase
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Database restored successfully${NC}"
else
    echo -e "${RED}✗ Restore failed${NC}"
    exit 1
fi

echo "Restarting services..."
docker-compose up -d

# Optional: Restore config.ini if you have a backup from the same time
# CONFIG_FILE="${BACKUP_FILE%_backup_*}_config_backup_${BACKUP_FILE##*_backup_}"
# CONFIG_FILE="${CONFIG_FILE%.sql.gz}.ini"
# if [ -f "$CONFIG_FILE" ]; then
#     echo "Found config backup: $CONFIG_FILE"
#     read -p "Restore config.ini too? (y/n) " -n 1 -r
#     echo
#     if [[ $REPLY =~ ^[Yy]$ ]]; then
#         cat "$CONFIG_FILE" | docker-compose exec -T labelbase_django bash -c "cat > /app/config.ini"
#         echo -e "${GREEN}✓ Config restored${NC}"
#         docker-compose restart labelbase_django
#     fi
# fi

echo ""
echo -e "${GREEN}=== Restore Complete ===${NC}"
echo "Check logs with: docker-compose logs -f labelbase_django"
```

Make executable and configure:
```bash
chmod +x restore-labelbase.sh
# Edit LABELBASE_DIR in the script
```

Usage:
```bash
./restore-labelbase.sh backups/labelbase_backup_20250119_143022.sql.gz
```

---

## Scheduled Backups

### Using Cron (Linux/Unix)

Automate daily backups at 2 AM:

```bash
# Edit crontab
crontab -e

# Add this line (adjust path to your Labelbase directory)
0 2 * * * cd /path/to/Labelbase && ./backup-labelbase.sh >> /var/log/labelbase-backup.log 2>&1
```

This runs the backup script daily at 2:00 AM and logs output to `/var/log/labelbase-backup.log`.

### Verify Cron Job

```bash
# List current cron jobs
crontab -l

# Check backup log
tail -f /var/log/labelbase-backup.log
```

### Alternative: Weekly Backups

```bash
# Every Sunday at 3 AM
0 3 * * 0 cd /path/to/Labelbase && ./backup-labelbase.sh >> /var/log/labelbase-backup.log 2>&1
```

---

## Best Practices

### Before Migrations
1. ✓ **Always create a backup first**
2. ✓ Review what migrations will be applied
3. ✓ Have a rollback plan ready
4. ✓ Test migrations on a development copy if possible
5. ✓ Schedule migrations during low-traffic periods

### Backup Storage
1. ✓ Keep backups in multiple locations
2. ✓ Regularly test your restore process
3. ✓ Keep at least 7-10 recent backups
4. ✓ Store critical backups off-server (external drive, cloud storage)
5. ✓ Monitor backup script success/failure

### Security
1. ✓ Protect `exports.sh` - it contains database passwords
2. ✓ Secure backup files - they contain all your data
3. ✓ Protect `config.ini` backups - they contain encryption keys
4. ✓ Use appropriate file permissions:
   ```bash
   chmod 600 exports.sh
   chmod 700 backups/
   chmod 600 backups/*.sql.gz
   chmod 600 backups/*_config.ini
   ```

### Regular Maintenance
1. ✓ Run backups before any system updates
2. ✓ Test restore process quarterly
3. ✓ Monitor backup file sizes (unexpected changes may indicate issues)
4. ✓ Keep backup logs for troubleshooting

### Docker Data Safety
1. ✓ **SAFE commands** (preserve data):
   - `docker-compose up --build -d` - Rebuild containers
   - `docker-compose restart` - Restart services
   - `docker-compose down` - Stop without deleting volumes
   - `docker-compose stop` - Pause containers
2. ✓ **DANGEROUS commands** (delete data):
   - `docker-compose down -v` - ⚠️ Deletes ALL volumes/data
   - `docker volume prune` - ⚠️ Removes unused volumes
   - `docker system prune -a` - ⚠️ Nuclear option
3. ✓ **Remember**: The `-v` flag means "delete volumes" = data loss!

---

## Troubleshooting

### "MYSQL_ROOT_PASSWORD not set"

**Cause**: `exports.sh` not sourced or doesn't contain password

**Solution**:
```bash
# Check if exports.sh exists
ls -la exports.sh

# Source it
source exports.sh

# Verify password is set
echo $MYSQL_ROOT_PASSWORD
```

### "Access denied for user 'root'"

**Cause**: Wrong password in `exports.sh`

**Solution**:
1. Check MySQL container logs: `docker-compose logs labelbase_mysql`
2. Verify password in `exports.sh` matches what MySQL expects
3. If lost, you may need to reset MySQL root password

### Backup File is Empty or Very Small

**Cause**: MySQL container not running or database empty

**Solution**:
```bash
# Check container status
docker-compose ps

# Check MySQL logs
docker-compose logs labelbase_mysql

# Verify database exists
docker-compose exec labelbase_mysql mysql -u root -p -e "SHOW DATABASES;"
```

### Restore Fails with "Unknown Database"

**Cause**: Database doesn't exist in MySQL

**Solution**:
```bash
# Create database first
docker-compose exec labelbase_mysql mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS labelbase;"

# Then restore
./restore-labelbase.sh backups/your_backup.sql.gz
```

---

## Complete Safe Migration Workflow

Here's the complete workflow combining backup and migration:

```bash
# 1. Navigate to Labelbase
cd Labelbase

# 2. Create backup
./backup-labelbase.sh

# 3. Source environment
source exports.sh

# 4. Check what migrations will run
docker-compose exec labelbase_django python manage.py showmigrations

# 5. Apply migrations
docker-compose exec labelbase_django python manage.py makemigrations
docker-compose exec labelbase_django python manage.py migrate

# 6. Check for errors
docker-compose logs labelbase_django | tail -50

# 7. Test your application
# Visit site and verify functionality

# 8. If problems occur, restore:
# ./restore-labelbase.sh backups/labelbase_backup_TIMESTAMP.sql.gz
```

---

## Quick Command Reference

```bash
# Quick upgrade (recommended)
source exports.sh && ./update-and-migrate.sh

# Manual upgrade workflow
./backup-labelbase.sh
git pull origin master
source exports.sh && docker-compose up --build -d
docker-compose exec labelbase_django python manage.py migrate
docker-compose restart labelbase_django

# Create backup (database + config.ini)
./backup-labelbase.sh

# Manual database backup
docker-compose exec -T labelbase_mysql mysqldump -u root -p"${MYSQL_ROOT_PASSWORD}" labelbase > backup_$(date +%Y%m%d_%H%M%S).sql

# Manual config.ini backup
docker-compose exec -T labelbase_django cat /app/config.ini > backup_$(date +%Y%m%d_%H%M%S)_config.ini

# List backups
ls -lh backups/

# Check migration status
docker-compose exec labelbase_django python manage.py showmigrations

# Apply migrations
docker-compose exec labelbase_django python manage.py migrate

# Restore backup
./restore-labelbase.sh backups/labelbase_backup_20250119_143022.sql.gz

# View recent Django logs
docker-compose logs labelbase_django | tail -100

# Access MySQL directly
docker-compose exec labelbase_mysql mysql -u root -p labelbase
```

---

## Additional Resources

- [Labelbase Development Guide](DEVELOPMENT_GUIDE.md)
- [Django Migrations Documentation](https://docs.djangoproject.com/en/stable/topics/migrations/)
- [mysqldump Documentation](https://dev.mysql.com/doc/refman/8.0/en/mysqldump.html)

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Docker logs: `docker-compose logs -f`
3. Verify all services are running: `docker-compose ps`
4. Check Labelbase GitHub issues: https://github.com/Labelbase/Labelbase/issues

---

**Remember: A backup today saves recovery tomorrow. Always backup before migrations!**
