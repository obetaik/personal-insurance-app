-- This runs automatically when MySQL container starts
CREATE DATABASE IF NOT EXISTS insurance_db;
CREATE USER IF NOT EXISTS 'app_user'@'%' IDENTIFIED BY 'app_password';
GRANT ALL PRIVILEGES ON insurance_db.* TO 'app_user'@'%';
FLUSH PRIVILEGES;