# Labelbase Backup and Migration Guide

A comprehensive guide for safely backing up your Labelbase database and running Django migrations.

## Table of Contents
- [Why Backup?](#why-backup)
- [Quick Backup](#quick-backup)
- [Automated Backup Script](#automated-backup-script)
- [Running Migrations Safely](#running-migrations-safely)
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

There is also the `config.ini`  holding the encryption and other important data.

```bash
# Navigate to Labelbase directory
cd Labelbase

# Source environment variables
source exports.sh

# Create backup with timestamp
docker-compose exec -T labelbase_django cat /app/config.ini > backup_$(date +%Y%m%d_%H%M%S)_config.ini
```
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

echo -e "${YELLOW}Starting backup...${NC}"
echo "Backup file: $BACKUP_FILE"

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
    echo "Location: ${BACKUP_FILE}.gz"

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
3. ✓ Use appropriate file permissions:
   ```bash
   chmod 600 exports.sh
   chmod 700 backups/
   chmod 600 backups/*.sql.gz
   ```

### Regular Maintenance
1. ✓ Run backups before any system updates
2. ✓ Test restore process quarterly
3. ✓ Monitor backup file sizes (unexpected changes may indicate issues)
4. ✓ Keep backup logs for troubleshooting

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
# Create backup
./backup-labelbase.sh

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
