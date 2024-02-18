-- File: init.sql

-- Create the database
CREATE DATABASE IF NOT EXISTS labelbase;

-- Switch to the database
USE labelbase;

-- Create the user
CREATE USER 'ulabelbase'@'%' IDENTIFIED BY '10almm6a62ec3z8jm4jjw6dny5';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON labelbase.* TO 'ulabelbase'@'%';

-- Flush privileges to apply changes
FLUSH PRIVILEGES;
