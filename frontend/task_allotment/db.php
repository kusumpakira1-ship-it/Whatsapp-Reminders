<?php
// task_allotment/db.php
// Connects to MySQL with automatic fallback to local SQLite database

function get_task_db() {
    static $pdo = null;
    if ($pdo !== null) {
        return $pdo;
    }

    $host = '145.223.17.70';
    $db   = 'u632391467_kusumpakira';
    $user = 'u632391467_kusumpakira';
    $pass = 'Kusum@2026Bb!';
    $charset = 'utf8mb4';

    $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
    $options = [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
        PDO::ATTR_PERSISTENT         => true,
    ];

    try {
        $pdo = new PDO($dsn, $user, $pass, $options);
        $pdo->query("SELECT 1");
    } catch (\Exception $e) {
        $pdo = null;
        $sqlite_paths = [
            __DIR__ . '/../whatsapp_reminders.sqlite',
            __DIR__ . '/whatsapp_reminders.sqlite',
            dirname(__DIR__) . '/whatsapp_reminders.sqlite'
        ];
        foreach ($sqlite_paths as $spath) {
            if (file_exists($spath)) {
                try {
                    $pdo = new PDO('sqlite:' . $spath);
                    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
                    break;
                } catch (\Exception $sqle) {}
            }
        }
    }

    if (!$pdo) {
        // Fallback: create sqlite file in current directory if needed
        $spath = __DIR__ . '/whatsapp_reminders.sqlite';
        $pdo = new PDO('sqlite:' . $spath);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }

    init_task_tables($pdo);
    return $pdo;
}

function init_task_tables($pdo) {
    $driver = $pdo->getAttribute(PDO::ATTR_DRIVER_NAME);
    $auto_inc = ($driver === 'sqlite') ? 'INTEGER PRIMARY KEY AUTOINCREMENT' : 'INT AUTO_INCREMENT PRIMARY KEY';

    // 1. Members Table
    $pdo->exec("CREATE TABLE IF NOT EXISTS task_allotment_members (
        id $auto_inc,
        name VARCHAR(255) NOT NULL,
        phone VARCHAR(50) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )");

    // 2. Task Presets Table
    $pdo->exec("CREATE TABLE IF NOT EXISTS task_allotment_presets (
        id $auto_inc,
        title VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )");

    // 3. Task Allotments Table
    $pdo->exec("CREATE TABLE IF NOT EXISTS task_allotments (
        id $auto_inc,
        member_id INT,
        member_name VARCHAR(255) NOT NULL,
        member_phone VARCHAR(50) NOT NULL,
        task_title VARCHAR(255) NOT NULL,
        whatsapp_group VARCHAR(255) DEFAULT 'No Group / Private Only',
        notes TEXT,
        assigned_date DATE NOT NULL,
        due_time VARCHAR(20) DEFAULT '22:30',
        status VARCHAR(50) DEFAULT 'pending',
        completed_at DATETIME NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )");

    // Seed initial members and presets if empty
    $count_members = $pdo->query("SELECT COUNT(*) FROM task_allotment_members")->fetchColumn();
    if ($count_members == 0) {
        $pdo->exec("INSERT INTO task_allotment_members (name, phone) VALUES 
            ('Akshay', '9019713446'),
            ('Balaji', '9493928388'),
            ('Divya', '9381255565')");
    }

    $count_presets = $pdo->query("SELECT COUNT(*) FROM task_allotment_presets")->fetchColumn();
    if ($count_presets == 0) {
        $pdo->exec("INSERT INTO task_allotment_presets (title) VALUES 
            ('Profit & Loss summary'),
            ('Daily updates'),
            ('Surrounding & Cleanliness Task')");
    }
}
