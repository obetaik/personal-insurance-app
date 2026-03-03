-- Create tables for insurance application
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    auth0_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


-- Create insurance_products table if it doesn't exist
CREATE TABLE IF NOT EXISTS insurance_products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    coverage_details TEXT,
    base_price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_product_name (name)
);


CREATE TABLE IF NOT EXISTS quotes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    quote_number VARCHAR(50) UNIQUE,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    coverage_amount DECIMAL(12, 2),
    deductible DECIMAL(10, 2),
    additional_options JSON,
    calculated_price DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (product_id) REFERENCES insurance_product(id)
);

CREATE TABLE IF NOT EXISTS policies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    policy_number VARCHAR(50) UNIQUE,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quote_id INT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    premium_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (product_id) REFERENCES insurance_product(id),
    FOREIGN KEY (quote_id) REFERENCES quote(id)
);

CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(100) UNIQUE,
    user_id INT NOT NULL,
    policy_id INT NOT NULL,
    amount DECIMAL(10, 2),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(100),
    status VARCHAR(50) DEFAULT 'Completed',
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (policy_id) REFERENCES policy(id)
);

CREATE TABLE IF NOT EXISTS claims (
    id INT AUTO_INCREMENT PRIMARY KEY,
    claim_number VARCHAR(50) UNIQUE,
    user_id INT NOT NULL,
    policy_id INT NOT NULL,
    incident_date DATE NOT NULL,
    filing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    claim_amount DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'Submitted',
    documents JSON,
    approved_amount DECIMAL(10, 2),
    resolution_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (policy_id) REFERENCES policy(id)
);