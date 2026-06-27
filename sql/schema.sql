-- Drop old tables if they exist from the PHP version
DROP TABLE IF EXISTS ai_extractions;
DROP TABLE IF EXISTS manager_reports;
DROP TABLE IF EXISTS reminders;
DROP TABLE IF EXISTS profit_loss;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS purchases;
DROP TABLE IF EXISTS whatsapp_messages;
DROP TABLE IF EXISTS groups_info;
DROP TABLE IF EXISTS contacts;

-- 1. Whitelist Table
CREATE TABLE IF NOT EXISTS whitelist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(50) NULL,
    group_id VARCHAR(100) NULL,
    enabled_flag BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(phone_number),
    UNIQUE(group_id)
);

-- 2. Raw Messages Table
CREATE TABLE IF NOT EXISTS raw_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255) UNIQUE NOT NULL,
    sender VARCHAR(100) NOT NULL,
    group_name VARCHAR(255) NULL,
    timestamp DATETIME NOT NULL,
    message_type VARCHAR(50) NOT NULL,
    raw_text TEXT NULL,
    media_url TEXT NULL,
    media_path VARCHAR(500) NULL,
    full_webhook_json JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Processed Data Table
CREATE TABLE IF NOT EXISTS processed_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shead_name VARCHAR(255) NULL,
    category ENUM('egg', 'feed', 'medicine', 'mortality', 'sales', 'purchase', 'expense', 'unknown') DEFAULT 'unknown',
    quantity DECIMAL(15, 2) NULL,
    unit VARCHAR(50) NULL,
    notes TEXT NULL,
    sender VARCHAR(100) NOT NULL,
    source_type ENUM('text', 'image', 'document') DEFAULT 'text',
    confidence_score DECIMAL(3, 2) NULL,
    processed_time DATETIME NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES raw_messages(message_id) ON DELETE CASCADE
);

-- 4. Report Recipients Table
CREATE TABLE IF NOT EXISTS report_recipients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
