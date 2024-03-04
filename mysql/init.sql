-- File: init.sql

-- Create the database
CREATE DATABASE IF NOT EXISTS labelbase;

-- Switch to the database
USE labelbase;

-- Create the user
CREATE USER 'ulabelbase'@'%' IDENTIFIED BY '$MYSQL_PASSWORD';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON labelbase.* TO 'ulabelbase'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
