-- Create Flocks table
CREATE TABLE IF NOT EXISTS sunfra_flocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shed_name VARCHAR(50) NOT NULL UNIQUE,
    hatch_date DATE NOT NULL,
    initial_chicks INT NOT NULL DEFAULT 0,
    batch_id VARCHAR(50) NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create Standards table loaded from Excel/read file
CREATE TABLE IF NOT EXISTS sunfra_book_standards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    week INT NOT NULL,
    day INT NOT NULL UNIQUE,
    vaccine TEXT NULL,
    expected_production_pct DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    expected_body_weight_g INT NOT NULL DEFAULT 0,
    expected_feed_g INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Add Vaccine Group settings key if not present
INSERT IGNORE INTO sunfra_system_settings (`key`, `value`) 
VALUES ('vaccine_group_whatsapp_id', '');
