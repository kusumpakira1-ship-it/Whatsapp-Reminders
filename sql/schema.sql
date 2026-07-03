-- Drop old tables if they exist
DROP TABLE IF EXISTS sunfra_processed_data;
DROP TABLE IF EXISTS sunfra_raw_messages;
DROP TABLE IF EXISTS sunfra_whitelist;
DROP TABLE IF EXISTS sunfra_report_recipients;
DROP TABLE IF EXISTS sunfra_employees;
DROP TABLE IF EXISTS sunfra_groups;
DROP TABLE IF EXISTS sunfra_custom_alarms;
DROP TABLE IF EXISTS sunfra_system_settings;

-- 1. Whitelist Table
CREATE TABLE IF NOT EXISTS sunfra_whitelist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(50) NULL,
    group_id VARCHAR(100) NULL,
    enabled_flag BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(phone_number),
    UNIQUE(group_id)
);

-- 2. Raw Messages Table
CREATE TABLE IF NOT EXISTS sunfra_raw_messages (
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
CREATE TABLE IF NOT EXISTS sunfra_processed_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shead_name VARCHAR(255) NULL,
    category ENUM('egg_collection_1', 'egg_collection_2', 'egg_collection', 'hen_weight', 'mortality', 'egg_loaded', 'egg_unloaded', 'production', 'sales', 'feed', 'raw_material', 'medicine', 'expense', 'purchase', 'egg', 'unknown') DEFAULT 'unknown',
    quantity DECIMAL(15, 2) NULL,
    unit VARCHAR(50) NULL,
    notes TEXT NULL,
    sender VARCHAR(100) NOT NULL,
    source_type ENUM('text', 'image', 'document') DEFAULT 'text',
    confidence_score DECIMAL(3, 2) NULL,
    processed_time DATETIME NOT NULL,
    message_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (message_id) REFERENCES sunfra_raw_messages(message_id) ON DELETE CASCADE
);

-- 4. Report Recipients Table
CREATE TABLE IF NOT EXISTS sunfra_report_recipients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    phone_number VARCHAR(50) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Groups Table
CREATE TABLE IF NOT EXISTS sunfra_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    whatsapp_group_id VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Employees Table
CREATE TABLE IF NOT EXISTS sunfra_employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(50) NOT NULL,
    group_id INT NULL,
    whatsapp_group_id VARCHAR(255) NULL,
    report_responsibility VARCHAR(100) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES sunfra_groups(id) ON DELETE CASCADE
);

-- 7. Custom Alarms Table
CREATE TABLE IF NOT EXISTS sunfra_custom_alarms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    target_type VARCHAR(20) NOT NULL,
    target_id INT NULL,
    whatsapp_target_id VARCHAR(255) NULL,
    report_type VARCHAR(50) NULL,
    frequency VARCHAR(20) DEFAULT 'once',
    repeat_interval VARCHAR(20) DEFAULT 'none',
    task_notes TEXT NOT NULL,
    trigger_time DATETIME NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8. System Settings Table
CREATE TABLE IF NOT EXISTS sunfra_system_settings (
    `key` VARCHAR(50) PRIMARY KEY,
    `value` VARCHAR(255) NULL
);
