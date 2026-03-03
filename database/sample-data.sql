-- sample-data.sql - Insert sample data for development

-- Insert sample products (if not already in schema.sql)

INSERT IGNORE INTO insurance_products (name, category, coverage_details, base_price) VALUES
('Auto Insurance Basic', 'Auto', 'Basic coverage for your vehicle including liability and collision', 500.00),
('Auto Insurance Premium', 'Auto', 'Comprehensive coverage with roadside assistance and rental car', 800.00),
('Home Insurance Basic', 'Home', 'Coverage for your home structure and personal belongings', 600.00),
('Home Insurance Premium', 'Home', 'Comprehensive home coverage including natural disasters and theft', 950.00),
('Life Insurance Term', 'Life', 'Term life insurance with flexible coverage options', 300.00),
('Health Insurance Basic', 'Health', 'Basic health coverage for individuals and families', 400.00);