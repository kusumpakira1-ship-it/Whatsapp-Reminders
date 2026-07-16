<?php
// ============================================================
// Sunfra Poultry - Whatsapp Reminders & Farm Automation
// Single-file unified backend and frontend
// ============================================================
@opcache_reset();
ini_set('display_errors', 1);
error_reporting(E_ALL);

// 1. Database Connection
// Try to load the database configuration from the parent directory
if (file_exists('../database.php')) {
    require_once '../database.php';
} else {
    // Fallback: If database.php doesn't exist, use an SQLite database for immediate setup
    try {
        $pdo = new PDO('sqlite:' . __DIR__ . '/whatsapp_reminders.sqlite');
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } catch (PDOException $e) {
        die("Database connection failed: " . $e->getMessage());
    }
}


// 2. Initialize Tables
try {
    // MySQL syntax (Primary)
    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_groups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        whatsapp_group_id VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone_number VARCHAR(50) NOT NULL,
        group_id INT NULL,
        whatsapp_group_id VARCHAR(255) NULL,
        report_responsibility VARCHAR(100) NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_custom_alarms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        target_type VARCHAR(20) NOT NULL,
        target_id INT NULL,
        whatsapp_target_id VARCHAR(255) NULL,
        report_type VARCHAR(50) NULL,
        task_notes TEXT NOT NULL,
        trigger_time DATETIME NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_system_settings (
        `key` VARCHAR(50) PRIMARY KEY,
        `value` LONGTEXT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_waha_events (
        id INT AUTO_INCREMENT PRIMARY KEY,
        event_type VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL,
        details TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_unified_reminders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        person_name VARCHAR(255) NOT NULL,
        person_phone VARCHAR(50) NOT NULL,
        whatsapp_group_id VARCHAR(255) NULL,
        report_types TEXT NULL,
        task_notes TEXT NULL,
        trigger_time DATETIME NOT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        frequency VARCHAR(20) DEFAULT 'daily',
        repeat_interval VARCHAR(20) DEFAULT 'none',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_tasks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task_name VARCHAR(255) NOT NULL,
        task_type VARCHAR(50) DEFAULT 'general',
        assigned_person_name VARCHAR(255) NULL,
        assigned_person_phone VARCHAR(100) NULL,
        whatsapp_group_id VARCHAR(255) NULL,
        due_time DATETIME NOT NULL,
        completion_keywords TEXT NULL,
        status VARCHAR(20) DEFAULT 'pending',
        approver_phone VARCHAR(100) NULL,
        completion_details TEXT NULL,
        frequency VARCHAR(20) DEFAULT 'once',
        repeat_interval VARCHAR(20) DEFAULT 'none',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");
} catch (PDOException $e) {
    // Fallback to SQLite syntax if MySQL fails
    try {
        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            whatsapp_group_id VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            group_id INTEGER NULL,
            whatsapp_group_id VARCHAR(255) NULL,
            report_responsibility VARCHAR(100) NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_custom_alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type VARCHAR(20) NOT NULL,
            target_id INTEGER NULL,
            whatsapp_target_id VARCHAR(255) NULL,
            report_type VARCHAR(50) NULL,
            task_notes TEXT NOT NULL,
            trigger_time DATETIME NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_system_settings (
            `key` VARCHAR(50) PRIMARY KEY,
            `value` TEXT NULL
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_waha_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )");

        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_unified_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_name VARCHAR(255) NOT NULL,
            person_phone VARCHAR(50) NOT NULL,
            whatsapp_group_id VARCHAR(255) NULL,
            report_types TEXT NULL,
            task_notes TEXT NULL,
            trigger_time DATETIME NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            frequency VARCHAR(20) DEFAULT 'daily',
            repeat_interval VARCHAR(20) DEFAULT 'none',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");

        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name VARCHAR(255) NOT NULL,
            task_type VARCHAR(50) DEFAULT 'general',
            assigned_person_name VARCHAR(255) NULL,
            assigned_person_phone VARCHAR(100) NULL,
            whatsapp_group_id VARCHAR(255) NULL,
            due_time DATETIME NOT NULL,
            completion_keywords TEXT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            approver_phone VARCHAR(100) NULL,
            completion_details TEXT NULL,
            frequency VARCHAR(20) DEFAULT 'once',
            repeat_interval VARCHAR(20) DEFAULT 'none',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
    } catch (PDOException $e2) {
        // Output the error to help debug
        if (isset($_GET['api'])) {
            header("Content-Type: application/json");
            echo json_encode(['error' => 'Table creation failed: ' . $e->getMessage() . ' | SQLite Fallback failed: ' . $e2->getMessage()]);
            exit;
        }
    }
}

// Run table schema adjustments dynamically (covers live server migration)
try { @$pdo->exec("ALTER TABLE sunfra_custom_alarms ADD COLUMN whatsapp_target_id VARCHAR(255) NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_custom_alarms ADD COLUMN report_type VARCHAR(50) NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_custom_alarms ADD COLUMN frequency VARCHAR(20) DEFAULT 'once'"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_custom_alarms ADD COLUMN repeat_interval VARCHAR(20) DEFAULT 'none'"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_custom_alarms MODIFY COLUMN target_id INT NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_employees ADD COLUMN whatsapp_group_id VARCHAR(255) NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_employees MODIFY COLUMN group_id INT NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_system_settings MODIFY COLUMN `value` LONGTEXT NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_system_settings MODIFY COLUMN `value` TEXT NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_unified_reminders ADD COLUMN frequency VARCHAR(20) DEFAULT 'daily'"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_unified_reminders ADD COLUMN repeat_interval VARCHAR(20) DEFAULT 'none'"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_tasks ADD COLUMN frequency VARCHAR(20) DEFAULT 'once'"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_tasks ADD COLUMN repeat_interval VARCHAR(20) DEFAULT 'none'"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_tasks ADD COLUMN approver_phone VARCHAR(100) NULL"); } catch (Exception $e) {}
try { @$pdo->exec("ALTER TABLE sunfra_tasks ADD COLUMN completion_details TEXT NULL"); } catch (Exception $e) {}

// 4. AUTO-RESET ONCE PER DAY (midnight equivalent on Hostinger server)
//    Checks if today's reset already ran. If not, advances all sent/skipped
//    recurring reminders to their next future date and resets to 'pending'.
//    Runs on first page load after midnight each day — no cron job needed.
try {
    $IST_OFFSET = 5.5 * 3600; // IST = UTC+5:30
    $now_ist = new DateTime('@' . (time() + $IST_OFFSET));
    $today_ist = $now_ist->format('Y-m-d');

    // Check last reset date stored in DB
    $chk = $pdo->prepare("SELECT value FROM sunfra_system_settings WHERE `key` = 'last_midnight_reset'");
    $chk->execute();
    $last_reset = $chk->fetchColumn();

    if ($last_reset !== $today_ist) {
        // Run the reset
        $stmt = $pdo->query("SELECT id, trigger_time, frequency FROM sunfra_unified_reminders WHERE status IN ('sent','skipped') AND (frequency IS NULL OR frequency != 'once')");
        $overdue = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $now_utc = new DateTime();
        foreach ($overdue as $r) {
            $freq = strtolower($r['frequency'] ?? 'daily');
            $dt = new DateTime($r['trigger_time']);
            $advanced = false;
            while ($dt <= $now_utc) {
                if ($freq === 'weekly')       { $dt->modify('+7 days'); }
                elseif ($freq === 'monthly')  { $dt->modify('+1 month'); }
                elseif ($freq === 'yearly')   { $dt->modify('+1 year'); }
                else                          { $dt->modify('+1 day'); } // daily default
                $advanced = true;
            }
            if ($advanced) {
                $upd = $pdo->prepare("UPDATE sunfra_unified_reminders SET trigger_time = ?, status = 'pending' WHERE id = ?");
                $upd->execute([$dt->format('Y-m-d H:i:s'), $r['id']]);
            }
        }
        // Mark today's reset as done
        $exists = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = 'last_midnight_reset'");
        $exists->execute();
        if ($exists->fetchColumn() > 0) {
            $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = 'last_midnight_reset'")->execute([$today_ist]);
        } else {
            $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES ('last_midnight_reset', ?)")->execute([$today_ist]);
        }
    }
} catch (Exception $e) { /* silent fail - never break the page */ }

// 5. AUTO-COMPLETE TASKS: Check WhatsApp messages for completion replies.
//    - Individual tasks: checks sunfra_raw_messages by sender phone
//    - Group tasks: checks sunfra_whatsapp_messages by group_id
//    Runs on every page load on Hostinger (24/7).
try {
    $pending_tasks_stmt = $pdo->query("SELECT id, task_name, assigned_person_phone, whatsapp_group_id, due_time, completion_keywords FROM sunfra_tasks WHERE status IN ('pending', 'overdue')");
    $pending_tasks = $pending_tasks_stmt->fetchAll(PDO::FETCH_ASSOC);

    $default_keywords = ['done', 'completed', 'finish', 'finished', 'ok done', 'complete', 'ho gaya', 'ho gya', 'kar diya', '✅', 'done✅'];

    // Pre-calculate pending task counts per group/phone to handle "done" ambiguity
    $group_task_counts = [];
    $phone_task_counts = [];
    foreach ($pending_tasks as $t) {
        if (!empty($t['whatsapp_group_id'])) {
            $gid = $t['whatsapp_group_id'];
            $group_task_counts[$gid] = ($group_task_counts[$gid] ?? 0) + 1;
        }
        if (!empty($t['assigned_person_phone'])) {
            foreach (explode(',', $t['assigned_person_phone']) as $ph) {
                $digits = preg_replace('/\D/', '', $ph);
                if (strlen($digits) === 10) $digits = '91' . $digits;
                if ($digits) $phone_task_counts[$digits] = ($phone_task_counts[$digits] ?? 0) + 1;
            }
        }
    }

    foreach ($pending_tasks as $task) {
        // Build completion keyword list
        $keywords = $default_keywords;
        if (!empty($task['completion_keywords'])) {
            $custom = array_map('trim', explode(',', strtolower($task['completion_keywords'])));
            $keywords = array_merge($keywords, $custom);
        }

        // Generate task-identifying keywords from the task name (e.g. "Silo Cleaning" -> "silo", "cleaning")
        $task_name_words = explode(' ', strtolower(preg_replace('/[^a-zA-Z0-9\s]/', '', $task['task_name'])));
        $task_identifiers = [];
        foreach ($task_name_words as $w) {
            if (strlen($w) > 3 && !in_array($w, ['task', 'check', 'please', 'update', 'submit', 'report'])) {
                $task_identifiers[] = $w;
            }
        }

        $since = $task['due_time'] ?? date('Y-m-d H:i:s', strtotime('-24 hours'));
        $all_messages = [];
        $matched = false;
        $is_ambiguous = false;

        // === CHECK GROUP ===
        if (!empty($task['whatsapp_group_id'])) {
            $grp_id = $task['whatsapp_group_id'];
            if (($group_task_counts[$grp_id] ?? 0) > 1) $is_ambiguous = true;
            
            if (strpos($grp_id, '@') === false) $grp_id .= '@g.us';
            $msg_stmt = $pdo->prepare("SELECT message_text FROM sunfra_whatsapp_messages WHERE group_id = ? AND timestamp >= ? ORDER BY timestamp DESC LIMIT 30");
            $msg_stmt->execute([$grp_id, $since]);
            $all_messages = array_merge($all_messages, $msg_stmt->fetchAll(PDO::FETCH_COLUMN));
        }

        // === CHECK INDIVIDUAL ===
        if (!empty($task['assigned_person_phone'])) {
            $phones_raw = array_map('trim', explode(',', $task['assigned_person_phone']));
            $phone_patterns = [];
            foreach ($phones_raw as $ph) {
                $digits = preg_replace('/\D/', '', $ph);
                if (strlen($digits) === 10) $digits = '91' . $digits;
                if ($digits) {
                    $phone_patterns[] = $digits;
                    if (($phone_task_counts[$digits] ?? 0) > 1) $is_ambiguous = true;
                }
            }
            if (!empty($phone_patterns)) {
                $sender_conditions = implode(' OR ', array_fill(0, count($phone_patterns), "sender LIKE ?"));
                $msg_stmt = $pdo->prepare("SELECT raw_text FROM sunfra_raw_messages WHERE timestamp >= ? AND ($sender_conditions) ORDER BY timestamp DESC LIMIT 20");
                $params = [$since];
                foreach ($phone_patterns as $ph) { $params[] = '%' . $ph . '%'; }
                $msg_stmt->execute($params);
                $all_messages = array_merge($all_messages, $msg_stmt->fetchAll(PDO::FETCH_COLUMN));
            }
        }

        if (empty($all_messages)) continue;

        // Check messages for completion logic
        foreach ($all_messages as $msg_text) {
            $msg_lower = strtolower(trim($msg_text ?? ''));
            
            // 1. Does it have a completion word? ("done", "completed", etc.)
            $has_completion = false;
            foreach ($keywords as $kw) {
                if ($kw && strpos($msg_lower, trim($kw)) !== false) {
                    $has_completion = true;
                    break;
                }
            }

            if ($has_completion) {
                // 2. If ambiguous (multiple tasks), it MUST contain a task identifier word (e.g. "silo")
                if ($is_ambiguous && !empty($task_identifiers)) {
                    $has_identifier = false;
                    foreach ($task_identifiers as $id_kw) {
                        if (strpos($msg_lower, $id_kw) !== false) {
                            $has_identifier = true;
                            break;
                        }
                    }
                    if ($has_identifier) {
                        $matched = true;
                        break;
                    }
                } else {
                    // Not ambiguous (only 1 task pending) OR no identifiable words in task name
                    $matched = true;
                    break;
                }
            }
        }

        if ($matched) {
            $pdo->prepare("UPDATE sunfra_tasks SET status = 'completed', completion_details = 'Auto-completed: WhatsApp reply detected' WHERE id = ?")->execute([$task['id']]);
        }
    }
} catch (Exception $e) { /* silent fail */ }


// 5. Simple REST API Router
if (isset($_GET['api'])) {
    header("Content-Type: application/json");
    $method = $_SERVER['REQUEST_METHOD'];
    $route = $_GET['api'];

    try {
        if ($route === 'temp_read_file' && $method === 'GET') {
            header("Content-Type: text/plain");
            $f = $_GET['file'];
            $path = __DIR__ . '/' . $f;
            if (file_exists($path)) {
                echo file_get_contents($path);
            } else {
                echo "File not found";
            }
            exit;
        }
        if ($route === 'reminders' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM sunfra_unified_reminders ORDER BY trigger_time DESC");
            $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            $waha_file = __DIR__ . '/waha_groups.json';
            $waha_groups = file_exists($waha_file) ? json_decode(file_get_contents($waha_file), true)['groups'] ?? [] : [];
            
            foreach ($rows as &$row) {
                $row['whatsapp_id'] = preg_match('/^\d{10}$/', $row['person_phone']) ? "91{$row['person_phone']}@c.us" : "{$row['person_phone']}@c.us";
                $row['group_name'] = 'No Group / Private Only';
                if ($row['whatsapp_group_id']) {
                    foreach ($waha_groups as $g) {
                        if ($g['id'] === $row['whatsapp_group_id']) {
                            $row['group_name'] = $g['name'];
                            break;
                        }
                    }
                }
            }
            echo json_encode($rows);
        }
        elseif ($route === 'reminders' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("INSERT INTO sunfra_unified_reminders (person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, repeat_interval, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')");
            $stmt->execute([
                $data['person_name'],
                $data['person_phone'],
                !empty($data['whatsapp_group_id']) ? $data['whatsapp_group_id'] : null,
                $data['report_types'] ?? null,
                $data['task_notes'],
                $data['trigger_time'],
                $data['frequency'] ?? 'daily',
                $data['repeat_interval'] ?? 'none'
            ]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^reminders\/(\d+)$/', $route, $matches) && $method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("UPDATE sunfra_unified_reminders SET person_name = ?, person_phone = ?, whatsapp_group_id = ?, report_types = ?, task_notes = ?, trigger_time = ?, frequency = ?, repeat_interval = ?, status = 'pending' WHERE id = ?");
            $stmt->execute([
                $data['person_name'],
                $data['person_phone'],
                !empty($data['whatsapp_group_id']) ? $data['whatsapp_group_id'] : null,
                $data['report_types'] ?? null,
                $data['task_notes'],
                $data['trigger_time'],
                $data['frequency'] ?? 'daily',
                $data['repeat_interval'] ?? 'none',
                $matches[1]
            ]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^reminders\/(\d+)$/', $route, $matches) && $method === 'DELETE') {
            $pdo->prepare("DELETE FROM sunfra_unified_reminders WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^reminders\/(\d+)\/trigger$/', $route, $matches) && $method === 'POST') {
            $pdo->prepare("UPDATE sunfra_unified_reminders SET status = 'sent' WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^reminders\/(\d+)\/instant$/', $route, $matches) && $method === 'POST') {
            $pdo->prepare("UPDATE sunfra_unified_reminders SET trigger_time = NOW(), status = 'pending' WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'reminders/reset-daily' && $method === 'POST') {
            // Advance trigger_time for all sent/skipped recurring reminders (same as Python midnight_reset_job)
            $stmt = $pdo->query("SELECT id, trigger_time, frequency FROM sunfra_unified_reminders WHERE status IN ('sent','skipped') AND frequency != 'once'");
            $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
            $count = 0;
            foreach ($rows as $r) {
                $freq = strtolower($r['frequency']);
                $dt = new DateTime($r['trigger_time']);
                $now = new DateTime();
                while ($dt <= $now) {
                    if ($freq === 'daily') {
                        $dt->modify('+1 day');
                    } elseif ($freq === 'weekly') {
                        $dt->modify('+7 days');
                    } elseif ($freq === 'monthly') {
                        $dt->modify('+1 month');
                    } elseif ($freq === 'yearly') {
                        $dt->modify('+1 year');
                    } else {
                        $dt->modify('+1 day');
                    }
                }
                $newTime = $dt->format('Y-m-d H:i:s');
                $upd = $pdo->prepare("UPDATE sunfra_unified_reminders SET trigger_time = ?, status = 'pending' WHERE id = ?");
                $upd->execute([$newTime, $r['id']]);
                $count++;
            }
            echo json_encode(['success' => true, 'reset_count' => $count]);
        }
        elseif ($route === 'settings/task_types' && $method === 'GET') {
            $stmt = $pdo->prepare("SELECT value FROM sunfra_system_settings WHERE `key` = 'custom_task_types'");
            $stmt->execute();
            $val = $stmt->fetchColumn();
            if ($val) {
                echo $val;
            } else {
                echo json_encode(["Silo Cleaning / Check", "Wednesday Meeting Checklist", "Feed Formula (Requires Approval)"]);
            }
        }
        elseif ($route === 'settings/task_types' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $val_str = json_encode($data['task_types']);
            
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = 'custom_task_types'");
            $stmt->execute();
            if ($stmt->fetchColumn() > 0) {
                $stmt2 = $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = 'custom_task_types'");
                $stmt2->execute([$val_str]);
            } else {
                $stmt2 = $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES ('custom_task_types', ?)");
                $stmt2->execute([$val_str]);
            }
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'tasks' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM sunfra_tasks ORDER BY due_time DESC");
            $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            $waha_file = __DIR__ . '/waha_groups.json';
            $waha_groups = file_exists($waha_file) ? json_decode(file_get_contents($waha_file), true)['groups'] ?? [] : [];
            
            foreach ($rows as &$row) {
                $row['group_name'] = 'No Group / Private Only';
                if ($row['whatsapp_group_id']) {
                    foreach ($waha_groups as $g) {
                        if ($g['id'] === $row['whatsapp_group_id']) {
                            $row['group_name'] = $g['name'];
                            break;
                        }
                    }
                }
            }
            echo json_encode($rows);
        }
        elseif ($route === 'tasks' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("INSERT INTO sunfra_tasks (task_name, task_type, assigned_person_name, assigned_person_phone, whatsapp_group_id, due_time, completion_keywords, status, approver_phone, frequency, repeat_interval) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?, ?, ?)");
            $stmt->execute([
                $data['task_name'],
                $data['task_type'],
                $data['assigned_person_name'] ?? null,
                $data['assigned_person_phone'] ?? null,
                !empty($data['whatsapp_group_id']) ? $data['whatsapp_group_id'] : null,
                $data['due_time'],
                $data['completion_keywords'] ?? null,
                $data['approver_phone'] ?? null,
                $data['frequency'] ?? 'once',
                $data['repeat_interval'] ?? 'none'
            ]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^tasks\/(\d+)$/', $route, $matches) && $method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("UPDATE sunfra_tasks SET task_name = ?, task_type = ?, assigned_person_name = ?, assigned_person_phone = ?, whatsapp_group_id = ?, due_time = ?, completion_keywords = ?, status = 'pending', approver_phone = ?, frequency = ?, repeat_interval = ? WHERE id = ?");
            $stmt->execute([
                $data['task_name'],
                $data['task_type'],
                $data['assigned_person_name'] ?? null,
                $data['assigned_person_phone'] ?? null,
                !empty($data['whatsapp_group_id']) ? $data['whatsapp_group_id'] : null,
                $data['due_time'],
                $data['completion_keywords'] ?? null,
                $data['approver_phone'] ?? null,
                $data['frequency'] ?? 'once',
                $data['repeat_interval'] ?? 'none',
                $matches[1]
            ]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^tasks\/(\d+)$/', $route, $matches) && $method === 'DELETE') {
            $pdo->prepare("DELETE FROM sunfra_tasks WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^tasks\/(\d+)\/complete$/', $route, $matches) && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $details = $data['details'] ?? 'Manually completed';
            $stmt = $pdo->prepare("UPDATE sunfra_tasks SET status = 'completed', completion_details = ? WHERE id = ?");
            $stmt->execute([$details, $matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'employees' && $method === 'GET') {
            $stmt = $pdo->query("SELECT id, name, phone_number FROM sunfra_employees ORDER BY name ASC");
            echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
        }
        elseif ($route === 'employees' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("INSERT INTO sunfra_employees (name, phone_number) VALUES (?, ?) ON DUPLICATE KEY UPDATE name = ?");
            $stmt->execute([$data['name'], $data['phone'], $data['name']]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'employees' && $method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("UPDATE sunfra_employees SET name = ?, phone_number = ? WHERE phone_number = ?");
            $stmt->execute([$data['name'], $data['phone'], $data['old_phone']]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'employees' && $method === 'DELETE') {
            $phone = $_GET['phone'];
            $stmt = $pdo->prepare("DELETE FROM sunfra_employees WHERE phone_number = ? OR phone_number = ?");
            $stmt->execute([$phone, '91' . $phone]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'settings/report_types' && $method === 'GET') {
            $stmt = $pdo->prepare("SELECT value FROM sunfra_system_settings WHERE `key` = 'custom_report_types'");
            $stmt->execute();
            $val = $stmt->fetchColumn();
            if ($val) {
                echo $val;
            } else {
                echo json_encode(["Production", "Feed", "Expenses", "Sales", "Profit and Loss"]);
            }
        }
        elseif ($route === 'settings/report_types' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $val_str = json_encode($data['report_types']);
            
            // Check if key exists
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = 'custom_report_types'");
            $stmt->execute();
            if ($stmt->fetchColumn() > 0) {
                $stmt2 = $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = 'custom_report_types'");
                $stmt2->execute([$val_str]);
            } else {
                $stmt2 = $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES ('custom_report_types', ?)");
                $stmt2->execute([$val_str]);
            }
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'waha/status' && $method === 'GET') {
            $stmt = $pdo->prepare("SELECT value FROM sunfra_system_settings WHERE `key` = 'waha_status'");
            $stmt->execute();
            $status = $stmt->fetchColumn() ?: 'UNKNOWN';
            
            $stmt = $pdo->prepare("SELECT value FROM sunfra_system_settings WHERE `key` = 'waha_qr_base64'");
            $stmt->execute();
            $qr = $stmt->fetchColumn() ?: '';
            
            echo json_encode([
                'status' => $status,
                'qr_code' => $qr
            ]);
        }
        elseif ($route === 'waha/status' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $status = $data['status'] ?? 'UNKNOWN';
            $qr = $data['qr_code'] ?? '';
            
            // Upsert status
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = 'waha_status'");
            $stmt->execute();
            if ($stmt->fetchColumn() > 0) {
                $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = 'waha_status'")->execute([$status]);
            } else {
                $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES ('waha_status', ?)")->execute([$status]);
            }
            
            // Upsert qr_code
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = 'waha_qr_base64'");
            $stmt->execute();
            if ($stmt->fetchColumn() > 0) {
                $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = 'waha_qr_base64'")->execute([$qr]);
            } else {
                $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES ('waha_qr_base64', ?)")->execute([$qr]);
            }
            
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'waha/events' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM sunfra_waha_events ORDER BY timestamp DESC LIMIT 50");
            echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
        }
        elseif ($route === 'settings/waha' && $method === 'GET') {
            $keys = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_pass', 'smtp_to', 'waha_alert_phone'];
            $settings = [];
            foreach ($keys as $k) {
                $stmt = $pdo->prepare("SELECT value FROM sunfra_system_settings WHERE `key` = ?");
                $stmt->execute([$k]);
                $settings[$k] = $stmt->fetchColumn() ?: '';
            }
            if (!empty($settings['smtp_pass'])) {
                $settings['smtp_pass'] = '********';
            }
            echo json_encode($settings);
        }
        elseif ($route === 'settings/waha' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $keys = ['smtp_host', 'smtp_port', 'smtp_user', 'smtp_to', 'waha_alert_phone'];
            foreach ($keys as $k) {
                if (isset($data[$k])) {
                    $stmt = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = ?");
                    $stmt->execute([$k]);
                    if ($stmt->fetchColumn() > 0) {
                        $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = ?")->execute([$data[$k], $k]);
                    } else {
                        $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES (?, ?)")->execute([$k, $data[$k]]);
                    }
                }
            }
            if (isset($data['smtp_pass']) && $data['smtp_pass'] !== '********') {
                $stmt = $pdo->prepare("SELECT COUNT(*) FROM sunfra_system_settings WHERE `key` = 'smtp_pass'");
                $stmt->execute();
                if ($stmt->fetchColumn() > 0) {
                    $pdo->prepare("UPDATE sunfra_system_settings SET value = ? WHERE `key` = 'smtp_pass'")->execute([$data['smtp_pass']]);
                } else {
                    $pdo->prepare("INSERT INTO sunfra_system_settings (`key`, value) VALUES ('smtp_pass', ?)")->execute([$data['smtp_pass']]);
                }
            }
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'waha/groups' && $method === 'GET') {
            $file = __DIR__ . '/waha_groups.json';
            $hidden_file = __DIR__ . '/hidden_groups.json';
            $groups_data = file_exists($file) ? json_decode(file_get_contents($file), true) : ['groups' => []];
            $hidden_data = file_exists($hidden_file) ? json_decode(file_get_contents($hidden_file), true) : [];
            
            echo json_encode([
                'status' => 'success',
                'groups' => $groups_data['groups'] ?? [],
                'hidden_groups' => $hidden_data
            ]);
        }
        elseif ($route === 'waha/contacts' && $method === 'GET') {
            $contacts = [];
            
            // 1. Fetch from employees
            $stmt = $pdo->query("SELECT name, phone_number FROM sunfra_employees WHERE phone_number IS NOT NULL AND phone_number != ''");
            while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $phone = preg_replace('/\D/', '', $row['phone_number']);
                if (strlen($phone) == 12 && strpos($phone, '91') === 0) {
                    $phone = substr($phone, 2);
                }
                if (strlen($phone) >= 10) {
                    $contacts[$phone] = trim($row['name']);
                }
            }
            
            // 2. Fetch from raw_messages sender list
            $stmt = $pdo->query("SELECT DISTINCT sender FROM sunfra_raw_messages WHERE sender IS NOT NULL AND sender LIKE '%(%)%'");
            while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
                $sender = $row['sender'];
                if (preg_match('/(?:\[.*?\]\s*)?([^(\n]+?)\s*\((\d+)\)/', $sender, $matches)) {
                    $name = trim($matches[1]);
                    $phone = trim($matches[2]);
                    if (strlen($phone) == 12 && strpos($phone, '91') === 0) {
                        $phone = substr($phone, 2);
                    }
                    if (strlen($phone) >= 10 && $name !== '' && strtolower($name) !== 'none') {
                        if (!isset($contacts[$phone]) || $contacts[$phone] === 'Unknown Contact') {
                            $contacts[$phone] = $name;
                        }
                    }
                }
            }
            
            // 3. Convert to list format
            $list = [];
            foreach ($contacts as $phone => $name) {
                $list[] = [
                    'name' => $name,
                    'phone' => $phone
                ];
            }
            
            usort($list, function($a, $b) {
                return strcasecmp($a['name'], $b['name']);
            });
            
            echo json_encode(['status' => 'success', 'contacts' => $list]);
        }
        elseif ($route === 'waha/groups/visibility' && $method === 'POST') {
            $data = file_get_contents('php://input');
            file_put_contents(__DIR__ . '/hidden_groups.json', $data);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'waha/groups/sync' && $method === 'POST') {
            $data = file_get_contents('php://input');
            file_put_contents(__DIR__ . '/waha_groups.json', $data);
            echo json_encode(['success' => true]);
        }
        else {
            http_response_code(404);
            echo json_encode(['error' => 'Not found']);
        }
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['error' => $e->getMessage()]);
    }
    exit;
}

// 4. Load contacts for HTML rendering (server-side only)
$waha_contacts = [];
try {
    $contacts_map = [];
    
    // 1. Fetch registered employees only (excluding raw message logs as requested)
    $stmt = $pdo->query("SELECT name, phone_number FROM sunfra_employees WHERE phone_number IS NOT NULL AND phone_number != ''");
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
        $phone = preg_replace('/\D/', '', $row['phone_number']);
        if (strlen($phone) == 12 && strpos($phone, '91') === 0) {
            $phone = substr($phone, 2);
        }
        if (strlen($phone) >= 10) {
            $contacts_map[$phone] = trim($row['name']);
        }
    }
    
    foreach ($contacts_map as $phone => $name) {
        $waha_contacts[] = [
            'name' => $name,
            'phone' => $phone
        ];
    }
    
    usort($waha_contacts, function($a, $b) {
        return strcasecmp($a['name'], $b['name']);
    });
} catch (Exception $e) {
    // Fail silently
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reminders</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-start: #f8fafc;
            --bg-end: #e2e8f0;
            --card-bg: rgba(255, 255, 255, 0.7);
            --card-border: rgba(255, 255, 255, 0.9);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --danger-color: #ef4444;
            --success-color: #10b981;
            --glass-bg: rgba(255, 255, 255, 0.4);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, var(--bg-start), var(--bg-end));
            color: var(--text-primary);
            line-height: 1.6;
            min-height: 100vh;
        }

        .app-container { display: flex; min-height: 100vh; }

        /* Sidebar */
        .sidebar {
            width: 260px;
            background: var(--card-bg);
            border-right: 1px solid var(--card-border);
            padding: 2rem 0;
            display: flex;
            flex-direction: column;
            backdrop-filter: blur(10px);
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2.5rem;
            background: linear-gradient(to right, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
        }

        .sidebar nav { display: flex; flex-direction: column; gap: 0.5rem; padding: 0 1.5rem; }

        .nav-item {
            padding: 0.85rem 1.2rem;
            color: var(--text-secondary);
            text-decoration: none;
            border-radius: 10px;
            transition: all 0.3s ease;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .nav-item:hover {
            background-color: rgba(59, 130, 246, 0.1);
            color: var(--text-primary);
            transform: translateX(4px);
        }

        .nav-item.active {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            color: white;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        /* Main Content */
        .main-content {
            flex: 1;
            padding: 2.5rem 3.5rem;
            overflow-y: auto;
        }

        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3.5rem;
        }

        header h1 { font-size: 2.2rem; font-weight: 600; }

        .user-profile {
            background: var(--card-bg);
            padding: 0.6rem 1.2rem;
            border-radius: 20px;
            border: 1px solid var(--card-border);
            font-size: 0.95rem;
            font-weight: 500;
            backdrop-filter: blur(5px);
        }

        /* Views */
        .view { display: none; animation: slideUp 0.4s ease-out; }
        .view.active { display: block; }

        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        /* Cards */
        .card {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 2rem;
            border: 1px solid var(--card-border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(10px);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
            width: 100%;
        }

        .stat-card {
            transition: transform 0.3s ease;
        }
        
        .stat-card:hover { transform: translateY(-5px); }
        .stat-card h3 { color: var(--text-secondary); font-size: 0.9rem; text-transform: uppercase; margin-bottom: 0.5rem; }
        .stat-value { font-size: 3rem; font-weight: 700; color: var(--primary-color); }

        /* Tables */
        .table-card {
            padding: 0;
            overflow-x: auto;
            overflow-y: auto;
            max-height: 70vh;
        }
        .data-table { width: 100%; border-collapse: collapse; }
        .data-table th, .data-table td { padding: 1.2rem 1.5rem; text-align: left; border-bottom: 1px solid var(--card-border); }
        
        .data-table th {
            background: rgba(0,0,0,0.03);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .data-table tbody tr { transition: background-color 0.2s; }
        .data-table tbody tr:hover { background: rgba(0,0,0,0.02); }

        /* Buttons */
        .btn {
            padding: 0.7rem 1.4rem;
            border: none;
            border-radius: 8px;
            font-family: inherit;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
            color: white;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4); }

        .btn-secondary { background: transparent; color: var(--text-secondary); border: 1px solid rgba(0,0,0,0.1); }
        .btn-secondary:hover { color: var(--text-primary); border-color: rgba(0,0,0,0.3); background: rgba(0,0,0,0.05); }

        .btn-danger {
            background: rgba(239, 68, 68, 0.1);
            color: #fca5a5;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .btn-danger:hover { background: var(--danger-color); color: white; }

        /* Modals */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--glass-bg);
            backdrop-filter: blur(8px);
            z-index: 100;
            align-items: center;
            justify-content: center;
            opacity: 0;
            transition: opacity 0.3s ease;
        }

        .modal.active { display: flex; opacity: 1; }

        .modal-content {
            width: 450px;
            max-height: 90vh;
            overflow-y: auto;
            overflow-x: hidden;
            transform: scale(0.95);
            transition: transform 0.3s ease;
        }
        
        .modal-content::-webkit-scrollbar {
            width: 6px;
        }
        .modal-content::-webkit-scrollbar-track {
            background: transparent;
        }
        .modal-content::-webkit-scrollbar-thumb {
            background: rgba(59, 130, 246, 0.3);
            border-radius: 4px;
        }
        .modal-content::-webkit-scrollbar-thumb:hover {
            background: rgba(59, 130, 246, 0.5);
        }
        
        .modal.active .modal-content { transform: scale(1); }
        .modal-content h3 { margin-bottom: 2rem; font-size: 1.4rem; color: var(--text-primary); }

        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.6rem; color: var(--text-secondary); font-size: 0.95rem; }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.1);
            background: rgba(255,255,255,0.8);
            color: var(--text-primary);
            font-family: inherit;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            background: #fff;
        }

        .modal-actions { display: flex; justify-content: flex-end; gap: 1rem; margin-top: 2.5rem; }
        
        .badge {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 0.75rem;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .badge-blue { background: rgba(59, 130, 246, 0.1); color: #2563eb; border: 1px solid rgba(59,130,246,0.2); }
        .badge-green { background: rgba(16, 185, 129, 0.1); color: #059669; border: 1px solid rgba(16,185,129,0.2); }
        .badge-orange { background: rgba(245, 158, 11, 0.1); color: #d97706; border: 1px solid rgba(245,158,11,0.2); }
        .badge-gray { background: rgba(107, 114, 128, 0.15); color: #4b5563; border: 1px solid rgba(107,114,128,0.25); }
        .badge-yellow { background: rgba(234, 179, 8, 0.1); color: #ca8a04; border: 1px solid rgba(234,179,8,0.2); }
        .badge-red { background: rgba(239, 68, 68, 0.1); color: #dc2626; border: 1px solid rgba(239,68,68,0.2); }


        /* Responsive Design */
        @media (max-width: 768px) {
            .app-container { flex-direction: column; }
            .sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--card-border); padding: 1rem 0; }
            .sidebar nav { flex-direction: row; flex-wrap: wrap; justify-content: center; padding: 0 1rem; }
            .nav-item { padding: 0.6rem 0.8rem; font-size: 0.9rem; }
            .main-content { padding: 1.5rem 1rem; }
            header { flex-direction: column; align-items: flex-start; gap: 1rem; margin-bottom: 2rem; }
            header h1 { font-size: 1.8rem; }
            .header-row { flex-direction: column; align-items: flex-start; gap: 1rem; }
            .stat-card { width: 100%; margin-right: 0; margin-bottom: 1rem; }
            .card { padding: 1.5rem 1rem; }
            .data-table { display: block; overflow-x: auto; white-space: nowrap; }
            
            /* Modal responsiveness & Auto-zoom prevention */
            .modal { align-items: flex-start; overflow-y: auto; padding: 2rem 0.5rem; }
            .modal-content { width: 100%; max-width: 480px; padding: 1.5rem; margin: 0 auto; }
            #reminderDatetimeSection > div { flex-direction: column; gap: 0.5rem; }
            #reminderDatetimeSection input { width: 100%; flex: none; }
            .form-group input, .form-group select, .form-group textarea { font-size: 16px !important; }
        }
    </style>
</head>

<body>
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="logo">Farm Reminders</div>
            <nav>
                <a href="#" class="nav-item active" data-target="dashboard">Dashboard</a>
                <a href="#" class="nav-item" data-target="reminders_view">Reminders</a>
                <a href="#" class="nav-item" data-target="tasks_view">Tasks & Approvals</a>
                <a href="#" class="nav-item" data-target="waha_settings_view">WAHA Status & Settings</a>
            </nav>
        </aside>
        <!-- Main Content -->
        <main class="main-content">
            <!-- Dashboard View -->
            <section id="dashboard" class="view active">
            <header>
                <h1>Management Dashboard</h1>
                <div class="user-profile" id="waha-status-indicator" style="display: flex; align-items: center; gap: 8px; cursor: pointer;" onclick="openWahaQrFromIndicator()">
                    <span class="status-dot" id="waha-status-dot" style="width: 12px; height: 12px; border-radius: 50%; background-color: #94a3b8; display: inline-block; transition: background-color 0.3s ease;"></span> 
                    <span id="waha-status-text" style="font-weight: 600;">Checking WAHA...</span>
                </div>
            </header>
                <h2 style="font-size: 1.2rem; margin-bottom: 1rem; color: var(--text-color);">Reminders Overview</h2>
                <div class="stats-grid" style="margin-bottom: 2rem;">
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'reminders_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Reminders">
                        <h3>Unique Members</h3>
                        <div class="stat-value" id="stat-employees">0</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'reminders_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Reminders">
                        <h3>Groups Used</h3>
                        <div class="stat-value" id="stat-groups">0</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'reminders_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Reminders">
                        <h3>Total Reminders</h3>
                        <div class="stat-value" id="stat-alarms">0</div>
                    </div>
                </div>

                <h2 style="font-size: 1.2rem; margin-bottom: 1rem; color: var(--text-color);">Tasks & Approvals Overview</h2>
                <div class="stats-grid">
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'tasks_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Tasks & Approvals">
                        <h3>Unique Members</h3>
                        <div class="stat-value" id="stat-task-employees">0</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'tasks_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Tasks & Approvals">
                        <h3>Groups Used</h3>
                        <div class="stat-value" id="stat-task-groups">0</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'tasks_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Tasks & Approvals">
                        <h3>Total Tasks</h3>
                        <div class="stat-value" id="stat-tasks">0</div>
                    </div>
                </div>
            </section>
            
            <!-- Reminders View -->
            <section id="reminders_view" class="view">
                <div class="header-row">
                    <h2>Reminders Management</h2>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <button class="btn btn-primary" onclick="openReminderModal()" style="margin: 0;">+ Create Reminder</button>
                        <button class="btn btn-secondary" onclick="openVisibilityModal()" style="margin: 0;">Filter Groups</button>
                        <button class="btn btn-secondary" onclick="resetDailyReminders()" style="margin: 0; background: rgba(245,158,11,0.12); color: #b45309; border: 1px solid rgba(245,158,11,0.3);" title="Advance all Daily/Weekly/Monthly reminders to next scheduled date">🔄 Reset Recurring</button>
                        <input type="text" id="remindersSearchInput" placeholder="Search..." oninput="filterRemindersTable()" style="padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); width: 150px; font-size: 0.9rem; background: white; margin: 0; box-sizing: border-box;">
                    </div>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Name & Phone</th>
                                <th>WhatsApp Group</th>
                                <th>Assigned Reports</th>
                                <th>Task / Notes</th>
                                <th>Frequency</th>
                                <th>Nagging</th>
                                <th>Trigger Time</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="reminders-tbody"></tbody>
                    </table>
                </div>
            </section>
            
            <!-- Tasks & Approvals View -->
            <section id="tasks_view" class="view">
                <div class="header-row">
                    <h2>Tasks &amp; Approvals Management</h2>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <button class="btn btn-primary" onclick="openCreateTaskModal()" style="margin: 0;">+ Create Task</button>
                        <button class="btn btn-secondary" onclick="openVisibilityModal()" style="margin: 0;">Filter Groups</button>
                        <input type="text" id="tasksSearchInput" placeholder="Search..." oninput="filterTasksTable()" style="padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); width: 150px; font-size: 0.9rem; background: white; margin: 0; box-sizing: border-box;">
                    </div>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Name &amp; Phone</th>
                                <th>WhatsApp Group</th>
                                <th>Assigned Tasks</th>
                                <th>Task / Custom Message</th>
                                <th>Frequency</th>
                                <th>Nagging</th>
                                <th>Trigger Time</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="tasks-tbody"></tbody>
                    </table>
                </div>
            </section>


            
            <!-- WAHA Settings View -->
            <section id="waha_settings_view" class="view">
                <div class="header-row">
                    <h2>WAHA Status &amp; Settings</h2>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary" onclick="checkWahaStatus(true)" style="margin: 0;">&#x21bb; Refresh</button>
                        <button class="btn btn-primary" onclick="openAlertSettingsModal()" style="margin: 0;">&#9881; Configure Alerts</button>
                    </div>
                </div>

                <!-- Status Card (full width) -->
                <div class="card" style="margin-bottom: 1.5rem;">
                    <div style="display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span class="status-dot" id="waha-view-status-dot" style="width: 16px; height: 16px; border-radius: 50%; background-color: #94a3b8; display: inline-block; flex-shrink: 0;"></span>
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px;">WAHA Session Status</div>
                                <div style="font-size: 1.4rem; font-weight: 700;" id="waha-view-status-text">UNKNOWN</div>
                            </div>
                        </div>
                        <div style="flex: 1; min-width: 200px; display: flex; gap: 2rem; flex-wrap: wrap; border-left: 1px solid rgba(0,0,0,0.06); padding-left: 1.5rem;">
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary);">Session</div>
                                <div style="font-weight: 600;">default</div>
                            </div>
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary);">Alert Email</div>
                                <div style="font-weight: 600;" id="info-smtp-to">kusumpakira1@gmail.com</div>
                            </div>
                            <div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary);">Alert Phone</div>
                                <div style="font-weight: 600;" id="info-waha-phone">7259510983</div>
                            </div>
                        </div>
                    </div>
                    <!-- QR Code (shows only when needed) -->
                    <div id="waha-qr-container-inline" style="margin-top: 1.5rem; background: #fff7ed; border: 1px solid #fed7aa; padding: 1.25rem; border-radius: 12px; text-align: center; display: none;">
                        <p style="font-weight: 700; margin-bottom: 1rem; color: #c2410c;">&#9888; QR Code Scan Required — Scan to reconnect WhatsApp</p>
                        <div id="waha-qr-img-inline"></div>
                    </div>
                </div>

                <!-- Connection Events -->
                <div class="card">
                    <h3 style="font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">Connection History &amp; Events</h3>
                    <div class="table-card" style="max-height: 320px;">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Event</th>
                                    <th>Status</th>
                                    <th>Details</th>
                                </tr>
                            </thead>
                            <tbody id="waha-events-tbody">
                                <tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">No events yet.</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </section>
        </main>
    </div>

    <!-- Create Task Modal -->
    <div id="createTaskModal" class="modal">
        <div class="modal-content card" style="width: 480px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.08); padding-bottom: 0.8rem; margin-bottom: 1.5rem;">
                <h3 id="task-modal-title" style="margin: 0; font-size: 1.4rem;">Create Task</h3>
                <span class="close-modal" onclick="closeCreateTaskModal()" style="font-size: 1.8rem; cursor: pointer; color: var(--text-secondary);">&times;</span>
            </div>
            <form id="task-form" onsubmit="handleTaskSubmit(event)">
                <input type="hidden" id="task-id">
                
                <div class="form-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <label style="font-weight: 600; margin: 0;">Assign Members</label>
                        <button type="button" class="btn" onclick="showAddManualMemberForm()" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2); border-radius: 6px; cursor: pointer; font-weight: 600;">[ + Add New Member ]</button>
                    </div>
                    
                    <!-- Search bar and members checkbox container -->
                    <input type="text" id="taskMemberSearchInput" placeholder="Search members..." oninput="filterTaskMembersList()" style="width: 100%; padding: 0.6rem; margin-bottom: 0.5rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-size: 0.9rem; background: white; color: var(--text-primary); box-sizing: border-box;">
                    
                    <div id="taskMembersCheckboxContainer" style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 180px; overflow-y: auto; padding: 0.75rem; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; background: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                        <!-- Checkboxes populated dynamically -->
                    </div>
                </div>

                <div class="form-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <label style="font-weight: 600; margin: 0;">Assigned Tasks</label>
                        <button type="button" class="btn" onclick="showAddCustomTaskForm()" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2); border-radius: 6px; cursor: pointer; font-weight: 600;">[ + Add Custom Task ]</button>
                    </div>
                    
                    <!-- Form to add new custom task type (initially hidden) -->
                    <div id="customTaskFormContainer" style="display: none; background: rgba(0,0,0,0.03); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.05); margin-bottom: 0.75rem; gap: 0.5rem; flex-direction: column;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-secondary);">Add Custom Task Type</div>
                        <div style="display: flex; gap: 0.5rem;">
                            <input type="text" id="newTaskTypeInput" placeholder="Add custom task type..." style="flex: 1; padding: 0.5rem; font-size: 0.9rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1); background: white;">
                        </div>
                        <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.25rem;">
                            <button type="button" class="btn btn-secondary" onclick="hideAddCustomTaskForm()" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; border-radius: 6px;">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="addNewTaskTypeCheckbox()" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; border-radius: 6px;">Add</button>
                        </div>
                    </div>
                    
                    <div id="taskTypesCheckboxContainer" style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 150px; overflow-y: auto; padding: 0.5rem; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; background: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                        <!-- Checkboxes populated dynamically -->
                    </div>
                </div>

                <div class="form-group" id="task-message-group" style="display: none;">
                    <label style="font-weight: 600;">Custom Text Message</label>
                    <textarea id="task-name" placeholder="Type your own custom message to remind them..." style="width: 100%; height: 100px; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); background: white;"></textarea>
                </div>

                <div class="form-group">
                    <label style="font-weight: 600;">WhatsApp Group (Optional)</label>
                    <select id="task-group-id" style="width: 100%;">
                        <option value="">No Group / Private Only</option>
                        <!-- Group options populated dynamically -->
                    </select>
                </div>

                <div class="form-group" id="task-approver-row" style="display: none;">
                    <label style="font-weight: 600;">Approver Manager Phone</label>
                    <input type="text" id="task-approver-phone" placeholder="e.g. 9346763549" style="width: 100%;">
                </div>

                <div class="form-group" id="taskDatetimeSection">
                    <label style="font-weight: 600;">Trigger Time</label>
                    <input type="datetime-local" id="task-due-time" required style="width: 100%;">
                </div>

                <div class="form-group">
                    <label style="font-weight: 600;">Frequency</label>
                    <select id="task-frequency" style="width: 100%;">
                        <option value="once">Once</option>
                        <option value="daily" selected>Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                    </select>
                </div>

                <div class="form-group">
                    <label style="font-weight: 600;">Repeat Interval (Nagging)</label>
                    <select id="task-repeat-interval" style="width: 100%;">
                        <option value="none" selected>None / No Nagging</option>
                        <option value="5m">Every 5 Minutes</option>
                        <option value="10m">Every 10 Minutes</option>
                        <option value="15m">Every 15 Minutes</option>
                        <option value="30m">Every 30 Minutes</option>
                        <option value="1h">Every 1 Hour</option>
                    </select>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeCreateTaskModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Task</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Reminder Modal -->
    <div id="reminderModal" class="modal">
        <div class="modal-content card">
            <h3 id="reminderModalTitle">Create Reminder</h3>
            <form id="reminderForm" onsubmit="handleReminderSubmit(event)">
                <input type="hidden" id="editReminderId">
                <div class="form-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <label style="font-weight: 600; margin: 0;">Assign Members</label>
                        <button type="button" class="btn" onclick="showAddManualMemberForm()" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2); border-radius: 6px; cursor: pointer; font-weight: 600;">[ + Add New Member ]</button>
                    </div>
                    
                    <!-- Form to add new manual member (initially hidden) -->
                    <div id="manualMemberFormContainer" style="display: none; background: rgba(0,0,0,0.03); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.05); margin-bottom: 0.75rem; gap: 0.5rem; flex-direction: column;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-secondary);">Add New Member Details</div>
                        <div style="display: flex; gap: 0.5rem;">
                            <input type="text" id="manualMemberName" placeholder="Name" style="flex: 1; padding: 0.5rem; font-size: 0.9rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1); background: white;">
                            <input type="text" id="manualMemberPhone" placeholder="Phone (10 digits)" maxlength="10" oninput="this.value = this.value.replace(/[^0-9]/g, '')" style="flex: 1; padding: 0.5rem; font-size: 0.9rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1); background: white;">
                        </div>
                        <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.25rem;">
                            <button type="button" class="btn btn-secondary" onclick="hideAddManualMemberForm()" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; border-radius: 6px;">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="addNewManualMemberToList()" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; border-radius: 6px;">Add to List</button>
                        </div>
                    </div>

                    <!-- Search bar and members checkbox container -->
                    <input type="text" id="memberSearchInput" placeholder="Search members..." oninput="filterMembersList()" style="width: 100%; padding: 0.6rem; margin-bottom: 0.5rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-size: 0.9rem; background: white; color: var(--text-primary); box-sizing: border-box;">
                    
                    <div id="membersCheckboxContainer" style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 180px; overflow-y: auto; padding: 0.75rem; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; background: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                        <!-- Checkboxes populated dynamically -->
                    </div>
                </div>
                
                <div class="form-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <label style="font-weight: 600; margin: 0;">Assigned Reports</label>
                        <button type="button" class="btn" onclick="showAddCustomReportForm()" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2); border-radius: 6px; cursor: pointer; font-weight: 600;">[ + Add Custom Report ]</button>
                    </div>
                    
                    <!-- Form to add new custom report type (initially hidden) -->
                    <div id="customReportFormContainer" style="display: none; background: rgba(0,0,0,0.03); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.05); margin-bottom: 0.75rem; gap: 0.5rem; flex-direction: column;">
                        <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-secondary);">Add Custom Report Type</div>
                        <div style="display: flex; gap: 0.5rem;">
                            <input type="text" id="newReportTypeInput" placeholder="Add custom report type..." style="flex: 1; padding: 0.5rem; font-size: 0.9rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1); background: white;">
                        </div>
                        <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.25rem;">
                            <button type="button" class="btn btn-secondary" onclick="hideAddCustomReportForm()" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; border-radius: 6px;">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="addNewReportTypeCheckbox()" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; border-radius: 6px;">Add</button>
                        </div>
                    </div>

                    <div id="reportCheckboxesContainer" style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 150px; overflow-y: auto; padding: 0.5rem; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; background: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                        <!-- Checkboxes populated dynamically -->
                    </div>
                </div>

                <div class="form-group">
                    <label>WhatsApp Group (Optional)</label>
                    <select id="remGroupSelect">
                        <option value="">No Group / Private Only</option>
                        <!-- Group options populated dynamically -->
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Task / Notes</label>
                    <textarea id="remNotes" required placeholder="What should they do?" rows="3"></textarea>
                </div>
                
                <div id="reminderDatetimeSection" class="form-group">
                    <label>Select Date & Time</label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="date" id="remDate" style="flex: 2;" required>
                        <input type="time" id="remTime" style="flex: 1;" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label>Schedule Frequency</label>
                    <select id="remFrequency" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; background: transparent; color: var(--text-primary);">
                        <option value="once">Once</option>
                        <option value="daily" selected>Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                        <option value="yearly">Yearly</option>
                    </select>
                </div>
                
                <div class="form-group" id="reminderRepeatSection">
                    <label>Repeat Reminder (Nagging)</label>
                    <select id="remRepeatInterval" style="width: 100%; padding: 0.75rem; border: 1px solid var(--border-color); border-radius: 8px; background: transparent; color: var(--text-primary);">
                        <option value="none">Send Once (No Repeat)</option>
                        <option value="5m">Repeat every 5 Minutes</option>
                        <option value="10m">Repeat every 10 Minutes</option>
                        <option value="15m">Repeat every 15 Minutes</option>
                        <option value="30m">Repeat every 30 Minutes</option>
                        <option value="1h">Repeat every 1 Hour</option>
                    </select>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('reminderModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Reminder</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Visibility Modal -->
    <div id="visibilityModal" class="modal">
        <div class="modal-content card" style="max-width: 500px; max-height: 80vh; display: flex; flex-direction: column;">
            <h3>Filter WhatsApp Groups</h3>
            <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 1rem;">Uncheck groups that you want to hide from the reminder dropdown list.</p>
            <input type="text" id="groupSearchInput" placeholder="Search groups..." oninput="filterVisibilityList()" style="margin-bottom: 1rem; width: 100%; padding: 0.7rem; border: 1px solid var(--border-color); border-radius: 8px; background: transparent; color: var(--text-primary); box-sizing: border-box;">
            <div id="visibilityListContainer" style="flex: 1; overflow-y: auto; margin-bottom: 1rem; border: 1px solid var(--border-color); border-radius: 8px; padding: 0.5rem;">
                <!-- Dynamically populated checkbox list -->
            </div>
            <div class="modal-actions" style="margin-top: auto;">
                <button type="button" class="btn btn-secondary" onclick="closeModal('visibilityModal')">Close</button>
                <button type="button" class="btn btn-primary" onclick="saveGroupVisibility()">Save Settings</button>
            </div>
        </div>
    </div>
    <!-- WAHA QR Code Scan Modal -->
    <div id="wahaQrModal" class="modal">
        <div class="modal-content card" style="max-width: 420px; text-align: center;">
            <h3 style="margin-bottom: 1rem;">Scan WhatsApp QR Code</h3>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.95rem;">
                Your WhatsApp Bot is currently disconnected. Please scan the QR code below using WhatsApp on your phone to reconnect.
            </p>
            <div id="modal-qr-container" style="background: #f8fafc; padding: 1.5rem; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; width: 100%; box-sizing: border-box; min-height: 250px;">
                <div id="modal-qr-placeholder">Loading QR Code...</div>
            </div>
            <div style="display: flex; gap: 0.5rem; justify-content: center; margin-top: 1.5rem;">
                <button type="button" class="btn btn-secondary" onclick="closeModal('wahaQrModal')">Close</button>
                <button type="button" class="btn btn-primary" onclick="checkWahaStatus(true)">Refresh QR</button>
            </div>
        </div>
    </div>

    <!-- Alert Settings Modal -->
    <div id="alertSettingsModal" class="modal">
        <div class="modal-content card" style="width: 480px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="margin: 0;">&#9881; Alert &amp; SMTP Configuration</h3>
                <button type="button" onclick="closeModal('alertSettingsModal')" style="background: none; border: none; font-size: 1.4rem; cursor: pointer; color: var(--text-secondary); line-height: 1;">&times;</button>
            </div>
            <form id="wahaSettingsForm" onsubmit="saveWahaSettings(event)">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div class="form-group" style="margin: 0;">
                        <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Alert Phone (WhatsApp)</label>
                        <input type="text" id="settingAlertPhone" placeholder="7259510983" style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;">
                    </div>
                    <div class="form-group" style="margin: 0;">
                        <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Alert Email</label>
                        <input type="email" id="settingAlertEmail" placeholder="kusumpakira1@gmail.com" style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;">
                    </div>
                </div>

                <div style="border-top: 1px solid rgba(0,0,0,0.06); padding-top: 1rem; margin-top: 0.5rem;">
                    <p style="font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 1rem; text-transform: uppercase; letter-spacing: 0.5px;">SMTP Email Sender</p>
                    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div class="form-group" style="margin: 0;">
                            <label style="font-size: 0.85rem; display: block; margin-bottom: 0.4rem;">SMTP Host</label>
                            <input type="text" id="settingSmtpHost" placeholder="smtp.gmail.com" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;">
                        </div>
                        <div class="form-group" style="margin: 0;">
                            <label style="font-size: 0.85rem; display: block; margin-bottom: 0.4rem;">Port</label>
                            <input type="number" id="settingSmtpPort" placeholder="587" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;">
                        </div>
                    </div>
                    <div class="form-group" style="margin-bottom: 1rem;">
                        <label style="font-size: 0.85rem; display: block; margin-bottom: 0.4rem;">SMTP Username</label>
                        <input type="text" id="settingSmtpUser" placeholder="your_email@gmail.com" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;">
                    </div>
                    <div class="form-group" style="margin-bottom: 0;">
                        <label style="font-size: 0.85rem; display: block; margin-bottom: 0.4rem;">SMTP Password / App Password</label>
                        <input type="password" id="settingSmtpPass" placeholder="Your app password" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;">
                    </div>
                </div>

                <div style="display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.75rem;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('alertSettingsModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">&#10003; Save Settings</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        const API_URL = '?api=';
        let waha_groups = [];
        let hidden_groups = [];
        let employees = [];
        let alarms = [];
        let report_types = [];
        let task_types = [];
        
        let all_contacts = <?php echo json_encode($waha_contacts); ?> || [];
        let manual_added_contacts = [];

        function escapeHtml(string) {
            return String(string).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
        }

        function renderMembersChecklist(selectedPhones = null, selectedTaskPhones = null) {
            const containerRem = document.getElementById('membersCheckboxContainer');
            const containerTask = document.getElementById('taskMembersCheckboxContainer');
            
            if (selectedPhones === null) {
                selectedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(cb => cb.value);
            }
            if (selectedTaskPhones === null) {
                selectedTaskPhones = Array.from(document.querySelectorAll('.task-member-checkbox:checked')).map(cb => cb.value);
            }
            
            // Combine database contacts with manually added ones
            const combined = [...all_contacts, ...manual_added_contacts];
            
            // De-duplicate by phone
            const uniqueContacts = [];
            const seen = new Set();
            combined.forEach(c => {
                if (!seen.has(c.phone)) {
                    seen.add(c.phone);
                    uniqueContacts.push(c);
                }
            });
            
            // Sort alphabetically by name
            uniqueContacts.sort((a, b) => a.name.localeCompare(b.name));
            
            if (containerRem) {
                containerRem.innerHTML = '';
                uniqueContacts.forEach(c => {
                    const checked = selectedPhones.includes(c.phone) ? 'checked' : '';
                    containerRem.innerHTML += `
                        <div class="member-checkbox-item" data-phone="${c.phone}" data-name="${c.name.toLowerCase()}" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.03);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="member-${c.phone}" value="${c.phone}" data-name="${c.name}" ${checked} class="member-checkbox" style="width:16px; height:16px; cursor:pointer;">
                                <label for="member-${c.phone}" style="cursor:pointer; font-size:0.95rem; color:var(--text-primary); font-weight:500;">
                                    ${c.name} <span style="font-weight:400; color:var(--text-secondary); font-size:0.85rem;">(${c.phone})</span>
                                </label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editMemberOption('${c.phone}', '${escapeHtml(c.name)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteMemberOption('${c.phone}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }

            if (containerTask) {
                containerTask.innerHTML = '';
                uniqueContacts.forEach(c => {
                    const checked = selectedTaskPhones.includes(c.phone) ? 'checked' : '';
                    containerTask.innerHTML += `
                        <div class="task-member-checkbox-item" data-phone="${c.phone}" data-name="${c.name.toLowerCase()}" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.03);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="task-member-${c.phone}" value="${c.phone}" data-name="${c.name}" ${checked} class="task-member-checkbox" style="width:16px; height:16px; cursor:pointer;">
                                <label for="task-member-${c.phone}" style="cursor:pointer; font-size:0.95rem; color:var(--text-primary); font-weight:500;">
                                    ${c.name} <span style="font-weight:400; color:var(--text-secondary); font-size:0.85rem;">(${c.phone})</span>
                                </label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editMemberOption('${c.phone}', '${escapeHtml(c.name)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteMemberOption('${c.phone}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        function filterTaskMembersList() {
            const query = document.getElementById('taskMemberSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.task-member-checkbox-item');
            items.forEach(item => {
                const name = item.getAttribute('data-name');
                const phone = item.getAttribute('data-phone');
                if (name.includes(query) || phone.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function filterMembersList() {
            const query = document.getElementById('memberSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.member-checkbox-item');
            items.forEach(item => {
                const name = item.getAttribute('data-name');
                const phone = item.getAttribute('data-phone');
                if (name.includes(query) || phone.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function showAddManualMemberForm() {
            const container = document.getElementById('manualMemberFormContainer');
            container.style.display = 'flex';
            document.getElementById('manualMemberName').focus();
        }
        
        function hideAddManualMemberForm() {
            const container = document.getElementById('manualMemberFormContainer');
            container.style.display = 'none';
            document.getElementById('manualMemberName').value = '';
            document.getElementById('manualMemberPhone').value = '';
        }
        
        async function addNewManualMemberToList() {
            const name = document.getElementById('manualMemberName').value.trim();
            const phone = document.getElementById('manualMemberPhone').value.trim();
            
            if (!name || phone.length !== 10) {
                return alert("Please enter a valid Name and 10-digit Phone Number");
            }
            
            // Save to database
            try {
                await fetch(API_URL + 'employees', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name: name, phone: phone })
                });
            } catch (err) {
                console.error("Failed to save new member:", err);
            }
            
            // Add to manual contacts
            manual_added_contacts.push({ name: name, phone: phone });
            
            // Re-render, keeping currently checked selections plus the new one
            const checkedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(cb => cb.value);
            checkedPhones.push(phone);
            
            renderMembersChecklist(checkedPhones);
            hideAddManualMemberForm();
        }

        async function editMemberOption(phone, currentName) {
            const newName = prompt("Edit Member Name:", currentName);
            if (newName === null) return;
            const cleanName = newName.trim();
            if (!cleanName) return alert("Name cannot be empty");
            
            const newPhone = prompt("Edit Member Phone (10 digits):", phone);
            if (newPhone === null) return;
            const cleanPhone = newPhone.trim().replace(/[^0-9]/g, '');
            if (cleanPhone.length !== 10) return alert("Phone must be exactly 10 digits");
            
            try {
                await fetch(API_URL + 'employees', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: cleanName,
                        phone: cleanPhone,
                        old_phone: phone
                    })
                });
                
                // Update local arrays
                all_contacts = all_contacts.map(c => c.phone === phone ? {name: cleanName, phone: cleanPhone} : c);
                manual_added_contacts = manual_added_contacts.map(c => c.phone === phone ? {name: cleanName, phone: cleanPhone} : c);
                
                // Keep selected checked
                const checkedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked'))
                    .map(cb => cb.value === phone ? cleanPhone : cb.value);
                
                renderMembersChecklist(checkedPhones);
            } catch (err) {
                console.error("Failed to edit member:", err);
            }
        }

        async function deleteMemberOption(phone) {
            if (!confirm("Are you sure you want to delete this member from the database?")) return;
            
            try {
                await fetch(API_URL + 'employees&phone=' + phone, {
                    method: 'DELETE'
                });
                
                // Remove from local arrays
                all_contacts = all_contacts.filter(c => c.phone !== phone);
                manual_added_contacts = manual_added_contacts.filter(c => c.phone !== phone);
                
                const checkedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked'))
                    .map(cb => cb.value)
                    .filter(p => p !== phone);
                    
                renderMembersChecklist(checkedPhones);
            } catch (err) {
                console.error("Failed to delete member:", err);
            }
        }

        async function editReportOption(oldName) {
            const newName = prompt("Edit Report Type Name:", oldName);
            if (newName === null) return;
            const cleanName = newName.trim();
            if (!cleanName) return alert("Name cannot be empty");
            if (cleanName === oldName) return;
            
            // Update in report_types list
            report_types = report_types.map(r => r === oldName ? cleanName : r);
            try {
                await fetch(API_URL + 'settings/report_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({report_types: report_types})
                });
                
                // Re-render keeping selection
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked'))
                    .map(cb => cb.value === oldName ? cleanName : cb.value);
                renderReportCheckboxes(checked);
                updateNotesFromCheckedReports();
            } catch (err) {
                console.error("Failed to edit report type:", err);
            }
        }

        async function deleteReportOption(name) {
            if (!confirm(`Are you sure you want to delete report type "${name}"?`)) return;
            
            report_types = report_types.filter(r => r !== name);
            try {
                await fetch(API_URL + 'settings/report_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({report_types: report_types})
                });
                
                // Re-render keeping selection
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked'))
                    .map(cb => cb.value)
                    .filter(v => v !== name);
                renderReportCheckboxes(checked);
                updateNotesFromCheckedReports();
            } catch (err) {
                console.error("Failed to delete report type:", err);
            }
        }

        function showAddCustomReportForm() {
            const container = document.getElementById('customReportFormContainer');
            if (container) {
                container.style.display = 'flex';
                document.getElementById('newReportTypeInput').focus();
            }
        }
        
        function hideAddCustomReportForm() {
            const container = document.getElementById('customReportFormContainer');
            if (container) {
                container.style.display = 'none';
                document.getElementById('newReportTypeInput').value = '';
            }
        }

        async function editTaskOption(oldName) {
            const newName = prompt("Edit Task Type Name:", oldName);
            if (newName === null) return;
            const cleanName = newName.trim();
            if (!cleanName) return alert("Name cannot be empty");
            if (cleanName === oldName) return;
            
            task_types = task_types.map(t => t === oldName ? cleanName : t);
            try {
                await fetch(API_URL + 'settings/task_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_types: task_types})
                });
                
                const checked = Array.from(document.querySelectorAll('.task-report-checkbox:checked'))
                    .map(cb => cb.value === oldName ? cleanName : cb.value);
                renderTaskCheckboxes(checked);
                handleTaskTypeCheckboxChange();
            } catch (err) {
                console.error("Failed to edit task type:", err);
            }
        }

        async function deleteTaskOption(name) {
            if (!confirm(`Are you sure you want to delete task type "${name}"?`)) return;
            
            task_types = task_types.filter(t => t !== name);
            try {
                await fetch(API_URL + 'settings/task_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_types: task_types})
                });
                
                const checked = Array.from(document.querySelectorAll('.task-report-checkbox:checked'))
                    .map(cb => cb.value)
                    .filter(v => v !== name);
                renderTaskCheckboxes(checked);
                handleTaskTypeCheckboxChange();
            } catch (err) {
                console.error("Failed to delete task type:", err);
            }
        }

        function showAddCustomTaskForm() {
            const container = document.getElementById('customTaskFormContainer');
            if (container) {
                container.style.display = 'flex';
                document.getElementById('newTaskTypeInput').focus();
            }
        }
        
        function hideAddCustomTaskForm() {
            const container = document.getElementById('customTaskFormContainer');
            if (container) {
                container.style.display = 'none';
                document.getElementById('newTaskTypeInput').value = '';
            }
        }

        async function addNewTaskTypeCheckbox() {
            const input = document.getElementById('newTaskTypeInput');
            const cleanName = input.value.trim();
            if (!cleanName) return alert("Please type a task name first");
            
            if (!task_types.includes(cleanName)) {
                task_types.push(cleanName);
                try {
                    await fetch(API_URL + 'settings/task_types', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({task_types: task_types})
                    });
                } catch (e) {
                    console.error("Failed to save task type:", e);
                }
                const checked = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value);
                checked.push(cleanName);
                renderTaskCheckboxes(checked);
                handleTaskTypeCheckboxChange();
                hideAddCustomTaskForm();
            } else {
                alert("This task type already exists!");
            }
        }

        async function loadReportTypesDropdowns() {
            try {
                const res = await fetch(API_URL + 'settings/report_types');
                report_types = await res.json();
            } catch (err) {
                report_types = ["Production", "Feed", "Expenses", "Sales", "Profit and Loss"];
            }
            renderReportCheckboxes([]);
        }

        async function loadTaskTypesDropdowns() {
            try {
                const res = await fetch(API_URL + 'settings/task_types');
                task_types = await res.json();
            } catch (err) {
                task_types = ["Silo Cleaning / Check", "Wednesday Meeting Checklist", "Feed Formula (Requires Approval)"];
            }
            renderTaskCheckboxes([]);
        }

        function renderReportCheckboxes(selected = null) {
            const containerRem = document.getElementById('reportCheckboxesContainer');
            if (selected === null) {
                selected = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
            }
            if (containerRem) {
                containerRem.innerHTML = '';
                report_types.forEach(r => {
                    const checked = selected.includes(r) ? 'checked' : '';
                    containerRem.innerHTML += `
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.02);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="report-${r}" value="${r}" ${checked} class="report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="updateNotesFromCheckedReports()">
                                <label for="report-${r}" style="cursor:pointer; font-size:0.9rem; color:var(--text-primary); font-weight:500;">${r}</label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editReportOption('${escapeHtml(r)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteReportOption('${escapeHtml(r)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        function renderTaskCheckboxes(selectedTasks = null) {
            const containerTask = document.getElementById('taskTypesCheckboxContainer');
            if (selectedTasks === null) {
                selectedTasks = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value);
            }
            if (containerTask) {
                containerTask.innerHTML = '';
                // Append special Personal option
                const personalChecked = selectedTasks.includes('Personal') ? 'checked' : '';
                containerTask.innerHTML += `
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.02); background: rgba(59,130,246,0.03);">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <input type="checkbox" id="task-report-Personal" value="Personal" ${personalChecked} class="task-report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="handleTaskTypeCheckboxChange()">
                            <label for="task-report-Personal" style="cursor:pointer; font-size:0.9rem; color:var(--primary-color); font-weight:600;">Personal (Custom Message)</label>
                        </div>
                    </div>
                `;

                task_types.forEach(t => {
                    const checked = selectedTasks.includes(t) ? 'checked' : '';
                    containerTask.innerHTML += `
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.02);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="task-report-${t}" value="${t}" ${checked} class="task-report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="handleTaskTypeCheckboxChange()">
                                <label for="task-report-${t}" style="cursor:pointer; font-size:0.9rem; color:var(--text-primary); font-weight:500;">${t}</label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editTaskOption('${escapeHtml(t)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteTaskOption('${escapeHtml(t)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        function updateNotesFromCheckedReports() {
            const checked = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
            const notesTextarea = document.getElementById('remNotes');
            if (checked.length > 0) {
                notesTextarea.value = `Please submit the ${checked.join(', ')} report(s).`;
            } else {
                notesTextarea.value = '';
            }
        }

        async function addNewReportTypeCheckbox() {
            const input = document.getElementById('newReportTypeInput');
            const cleanName = input.value.trim();
            if (!cleanName) return alert("Please type a report name first");
            
            if (!report_types.includes(cleanName)) {
                report_types.push(cleanName);
                try {
                    await fetch(API_URL + 'settings/report_types', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({report_types: report_types})
                    });
                } catch (e) {
                    console.error("Failed to save report type:", e);
                }
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
                checked.push(cleanName); // auto select new one
                renderReportCheckboxes(checked);
                updateNotesFromCheckedReports();
                hideAddCustomReportForm();
            } else {
                alert("This report type already exists!");
            }
        }

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                e.currentTarget.classList.add('active');
                
                const targetView = e.currentTarget.getAttribute('data-target');
                document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                document.getElementById(targetView).classList.add('active');

                if (targetView === 'tasks_view') {
                    fetchTasks();
                } else if (targetView === 'godown_inventory_view') {
                    fetchInventory();
                }
            });
        });

        function openModal(modalId) { document.getElementById(modalId).classList.add('active'); }
        function closeModal(modalId) { document.getElementById(modalId).classList.remove('active'); }

        function parseLocalStatusTime(dateStr) {
            if (!dateStr) return new Date();
            const normalized = dateStr.replace(/-/g, '/').replace('T', ' ');
            return new Date(normalized);
        }

        function formatDateTime(isoString) {
            if (!isoString) return '-';
            const dt = parseLocalStatusTime(isoString);
            return dt.toLocaleString('en-IN', {
                timeZone: 'Asia/Kolkata',
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }) + ' IST';
        }

        function formatIST(rawDbTimestamp) {
            // DB stores timestamps as "2026-07-11 08:30:00" (UTC or local server time)
            if (!rawDbTimestamp) return '-';
            // Treat as UTC by appending Z if no timezone info
            const normalized = rawDbTimestamp.replace(' ', 'T');
            const hasZ = normalized.endsWith('Z') || normalized.includes('+');
            const dt = new Date(hasZ ? normalized : normalized + 'Z');
            if (isNaN(dt)) return rawDbTimestamp; // fallback if unparseable
            return dt.toLocaleString('en-IN', {
                timeZone: 'Asia/Kolkata',
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            }) + ' IST';
        }

        let reminders = [];
        async function fetchReminders() {
            const res = await fetch(API_URL + 'reminders');
            reminders = await res.json();
            const tbody = document.getElementById('reminders-tbody');
            tbody.innerHTML = '';
            
            reminders.forEach(r => {
                const badgeClass = r.status === 'sent' ? 'badge-green' : (r.status === 'pending' ? 'badge-orange' : (r.status === 'skipped' ? 'badge-gray' : ''));
                const groupText = r.whatsapp_group_id ? `<strong style="color:var(--primary-color)">${r.group_name}</strong>` : `<span style="color:var(--text-secondary)">No Group / Private Only</span>`;
                const reportsText = r.report_types ? r.report_types.split(',').map(rep => `<span class="badge badge-blue" style="margin-right:0.25rem; font-size:0.7rem; display:inline-block; margin-top:2px;">${rep.trim()}</span>`).join(' ') : '<span style="color:var(--text-secondary)">Custom Notes Only</span>';
                
                const names = (r.person_name || '').split(',').map(n => n.trim());
                const phones = (r.person_phone || '').split(',').map(p => p.trim());
                const formattedAssignees = names.map((name, idx) => {
                    const phone = phones[idx] || '';
                    return `${name} (${phone})`;
                }).join(', ');

                tbody.innerHTML += `<tr>
                    <td><strong>${formattedAssignees}</strong></td>
                    <td>${groupText}</td>
                    <td>${reportsText}</td>
                    <td>${r.task_notes}</td>
                    <td style="text-transform: capitalize; font-weight: 500;">${r.frequency || 'daily'}</td>
                    <td style="text-transform: capitalize; font-weight: 500; color: #b45309;">${r.repeat_interval && r.repeat_interval !== 'none' ? r.repeat_interval : 'None'}</td>
                    <td>${formatDateTime(r.trigger_time)}</td>
                    <td><span class="badge ${badgeClass}">${r.status}</span></td>
                    <td>
                        <button class="btn btn-secondary" onclick="editReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Edit</button> 
                        <button class="btn btn-secondary" onclick="triggerReminderNow(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2); margin: 0;">Trigger Now</button>
                        <button class="btn btn-danger" onclick="deleteReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Delete</button>
                    </td>
                </tr>`;
            });
            
            document.getElementById('stat-employees').innerText = new Set(reminders.map(r => r.person_phone)).size;
            document.getElementById('stat-groups').innerText = new Set(reminders.map(r => r.whatsapp_group_id).filter(g => g)).size;
            document.getElementById('stat-alarms').innerText = reminders.length;
        }

        function filterRemindersTable() {
            const query = document.getElementById('remindersSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#reminders-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        function filterTasksTable() {
            const query = document.getElementById('tasksSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#tasks-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        async function fetchWahaGroups() {
            try {
                const res = await fetch(API_URL + 'waha/groups');
                const data = await res.json();
                if (data.status === 'success') {
                    waha_groups = data.groups || [];
                    hidden_groups = data.hidden_groups || [];
                    waha_groups.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
                } else {
                    waha_groups = [];
                    hidden_groups = [];
                }
            } catch (err) {
                waha_groups = [];
                hidden_groups = [];
            }
            updateGroupSelect();
        }

        function updateGroupSelect() {
            const select = document.getElementById('remGroupSelect');
            if (select) {
                select.innerHTML = '<option value="">No Group / Private Only</option>';
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => { select.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
            }
            const taskSelect = document.getElementById('task-group-id');
            if (taskSelect) {
                taskSelect.innerHTML = '<option value="">No Group / Private Only</option>';
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => { taskSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
            }
        }

        function openReminderModal() {
            document.getElementById('reminderForm').reset();
            document.getElementById('editReminderId').value = '';
            document.getElementById('reminderModalTitle').innerText = 'Create Reminder';
            document.getElementById('memberSearchInput').value = '';
            hideAddManualMemberForm();
            hideAddCustomReportForm();
            
            manual_added_contacts = [];
            renderMembersChecklist([]);
            renderReportCheckboxes([]);
            
            // Pre-populate with current local date and time by default
            const now = new Date();
            const format = n => String(n).padStart(2, '0');
            document.getElementById('remDate').value = `${now.getFullYear()}-${format(now.getMonth() + 1)}-${format(now.getDate())}`;
            document.getElementById('remTime').value = `${format(now.getHours())}:${format(now.getMinutes())}`;
            
            openModal('reminderModal');
        }

        function editReminder(id) {
            const r = reminders.find(x => x.id == id);
            if (!r) return;
            document.getElementById('editReminderId').value = r.id;
            document.getElementById('reminderModalTitle').innerText = 'Edit Reminder';
            document.getElementById('memberSearchInput').value = '';
            hideAddManualMemberForm();
            hideAddCustomReportForm();
            
            // Ensure all edited persons exist in checklist contacts and are checked
            const phones = (r.person_phone || '').split(',').map(p => p.trim());
            const names = (r.person_name || '').split(',').map(n => n.trim());
            
            phones.forEach((phone, idx) => {
                const name = names[idx] || phone;
                if (phone) {
                    const exists = [...all_contacts, ...manual_added_contacts].some(c => c.phone === phone);
                    if (!exists) {
                        manual_added_contacts.push({ name: name, phone: phone });
                    }
                }
            });
            
            renderMembersChecklist(phones);
            
            document.getElementById('remGroupSelect').value = r.whatsapp_group_id || '';
            document.getElementById('remNotes').value = r.task_notes;
            
            const selectedReports = r.report_types ? r.report_types.split(',').map(s => s.trim()) : [];
            renderReportCheckboxes(selectedReports);
            
            document.getElementById('remFrequency').value = r.frequency || 'daily';
            document.getElementById('remRepeatInterval').value = r.repeat_interval || 'none';
            
            const dt = parseLocalStatusTime(r.trigger_time);
            const format = n => String(n).padStart(2, '0');
            document.getElementById('remDate').value = `${dt.getFullYear()}-${format(dt.getMonth() + 1)}-${format(dt.getDate())}`;
            document.getElementById('remTime').value = `${format(dt.getHours())}:${format(dt.getMinutes())}`;
            
            openModal('reminderModal');
        }

        async function handleReminderSubmit(e) {
            e.preventDefault();
            const d = document.getElementById('remDate').value;
            const t = document.getElementById('remTime').value;
            if (!d || !t) return alert("Please select a date and time");
            const triggerTime = `${d}T${t}:00`;

            const checkedReports = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
            const reportTypesStr = checkedReports.length > 0 ? checkedReports.join(',') : null;

            // Get selected members
            const checkedMembers = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(cb => ({
                name: cb.getAttribute('data-name'),
                phone: cb.value
            }));

            if (checkedMembers.length === 0) {
                return alert("Please select at least one member to assign");
            }

            const names = checkedMembers.map(m => m.name).join(', ');
            const phones = checkedMembers.map(m => m.phone).join(', ');

            const editId = document.getElementById('editReminderId').value;
            
            if (editId) {
                // Edit Mode: Update reminder
                const url = API_URL + 'reminders/' + editId;
                await fetch(url, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        person_name: names,
                        person_phone: phones,
                        whatsapp_group_id: document.getElementById('remGroupSelect').value || null,
                        report_types: reportTypesStr,
                        task_notes: document.getElementById('remNotes').value,
                        trigger_time: triggerTime,
                        frequency: document.getElementById('remFrequency').value,
                        repeat_interval: document.getElementById('remRepeatInterval').value
                    })
                });
            } else {
                // Create Mode: Create a single reminder with all checked members
                const url = API_URL + 'reminders';
                await fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        person_name: names,
                        person_phone: phones,
                        whatsapp_group_id: document.getElementById('remGroupSelect').value || null,
                        report_types: reportTypesStr,
                        task_notes: document.getElementById('remNotes').value,
                        trigger_time: triggerTime,
                        frequency: document.getElementById('remFrequency').value,
                        repeat_interval: document.getElementById('remRepeatInterval').value
                    })
                });
            }
            
            closeModal('reminderModal');
            fetchReminders();
        }

        async function deleteReminder(id) {
            if(confirm("Delete reminder?")) {
                await fetch(API_URL + 'reminders/' + id, {method: 'DELETE'});
                fetchReminders();
            }
        }

        async function resetDailyReminders() {
            const res = await fetch(API_URL + 'reminders/reset-daily', {method: 'POST'});
            const data = await res.json();
            if (data.success) {
                alert(`✅ Done! ${data.reset_count} recurring reminder(s) advanced to their next scheduled date and set to Pending.`);
                fetchReminders();
            } else {
                alert('❌ Reset failed. Please try again.');
            }
        }

        async function triggerReminderNow(id) {
            if(confirm("Trigger now?")) {
                await fetch(API_URL + 'reminders/' + id + '/instant', {method: 'POST'});
                fetchReminders();
            }
        }

        function openVisibilityModal() {
            const container = document.getElementById('visibilityListContainer');
            container.innerHTML = '';
            const sorted = [...waha_groups].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
            sorted.forEach(g => {
                const checked = !hidden_groups.includes(g.id) ? 'checked' : '';
                container.innerHTML += `
                    <div class="group-vis-item" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.05);">
                        <input type="checkbox" id="vis-${g.id}" value="${g.id}" ${checked} class="group-vis-checkbox" style="width: 18px; height: 18px; cursor: pointer;">
                        <label for="vis-${g.id}" style="font-weight: 500; cursor: pointer; user-select: none; color: var(--text-primary); font-size: 0.95rem;">${g.name || 'Unnamed Group'}</label>
                    </div>
                `;
            });
            document.getElementById('groupSearchInput').value = '';
            openModal('visibilityModal');
        }

        function filterVisibilityList() {
            const q = document.getElementById('groupSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.group-vis-item');
            items.forEach(item => {
                const label = item.querySelector('label').innerText.toLowerCase();
                item.style.display = label.includes(q) ? 'flex' : 'none';
            });
        }
        
        async function saveGroupVisibility() {
            const checkboxes = document.querySelectorAll('.group-vis-checkbox');
            const hidden = [];
            checkboxes.forEach(cb => {
                if (!cb.checked) hidden.push(cb.value);
            });
            
            await fetch(API_URL + 'waha/groups/visibility', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(hidden)
            });
            
            hidden_groups = hidden;
            updateGroupSelect();
            closeModal('visibilityModal');
            fetchReminders();
        }

        let lastWahaStatus = '';
        async function checkWahaStatus(forceModal = false) {
            try {
                const response = await fetch(API_URL + 'waha/status');
                const data = await response.json();
                
                const status = data.status || 'UNKNOWN';
                const qrCode = data.qr_code || '';

                // ── Colour coding ─────────────────────────────────────────────
                const dotColor = status === 'WORKING'
                    ? 'var(--success-color)'
                    : (status === 'SCAN_QR_CODE' ? 'var(--danger-color)'
                    : (status === 'STOPPED' || status === 'FAILED' ? '#ef4444' : '#94a3b8'));

                const headerDot = document.getElementById('waha-status-dot');
                if (headerDot) headerDot.style.backgroundColor = dotColor;
                const headerText = document.getElementById('waha-status-text');
                if (headerText) headerText.innerText = `WAHA: ${status}`;
                const viewDot = document.getElementById('waha-view-status-dot');
                if (viewDot) viewDot.style.backgroundColor = dotColor;
                const viewText = document.getElementById('waha-view-status-text');
                if (viewText) viewText.innerText = status;

                // ── Status Banner (shown in WAHA status view) ─────────────────
                let banner = document.getElementById('waha-status-banner');
                if (!banner) {
                    banner = document.createElement('div');
                    banner.id = 'waha-status-banner';
                    banner.style.cssText = 'margin-bottom:1.25rem; padding:0.9rem 1.2rem; border-radius:10px; font-weight:600; font-size:0.95rem; display:none;';
                    const card = document.querySelector('#waha_settings_view .card');
                    if (card) card.parentNode.insertBefore(banner, card);
                }

                if (status === 'STOPPED' || status === 'FAILED') {
                    banner.style.display = 'block';
                    banner.style.background = '#fef2f2';
                    banner.style.border = '1px solid #fecaca';
                    banner.style.color = '#dc2626';
                    banner.innerHTML = '&#9888; <strong>WhatsApp Bot is ' + status + '.</strong> Auto-restart is in progress (every 5 min). The QR code will appear here automatically once WAHA is ready. Check your email for alerts.';
                } else if (status === 'SCAN_QR_CODE') {
                    banner.style.display = 'block';
                    banner.style.background = '#fff7ed';
                    banner.style.border = '1px solid #fed7aa';
                    banner.style.color = '#c2410c';
                    banner.innerHTML = '&#128247; <strong>QR Scan Required!</strong> Scan the QR code below using WhatsApp on your phone to reconnect the bot.';
                } else if (status === 'WORKING') {
                    banner.style.display = 'block';
                    banner.style.background = '#f0fdf4';
                    banner.style.border = '1px solid #bbf7d0';
                    banner.style.color = '#16a34a';
                    banner.innerHTML = '&#10003; <strong>WhatsApp Bot is Online and Working.</strong> All reminders are being sent normally.';
                } else {
                    banner.style.display = 'none';
                }

                // ── QR Code display ───────────────────────────────────────────
                const inlineContainer = document.getElementById('waha-qr-container-inline');
                const inlineImg = document.getElementById('waha-qr-img-inline');
                const modalContainer = document.getElementById('modal-qr-container');

                if (status === 'SCAN_QR_CODE') {
                    if (inlineContainer) inlineContainer.style.display = 'block';
                    if (qrCode) {
                        const qrImgHtml = `<img src="${qrCode}" style="max-width:280px; border:1px solid rgba(0,0,0,0.1); border-radius:8px;" alt="Scan WhatsApp QR">`;
                        if (inlineImg) inlineImg.innerHTML = qrImgHtml;
                        if (modalContainer) modalContainer.innerHTML = qrImgHtml;
                    } else {
                        if (inlineImg) inlineImg.innerHTML = '<p style="color:#94a3b8; font-size:0.9rem;">&#8635; QR loading... refresh in a moment.</p>';
                        if (modalContainer) modalContainer.innerHTML = '<div id="modal-qr-placeholder">&#8635; QR loading... please wait.</div>';
                    }
                    // Auto-open modal on state change
                    if ((lastWahaStatus !== 'SCAN_QR_CODE' || forceModal) && !document.getElementById('wahaQrModal').classList.contains('active')) {
                        openModal('wahaQrModal');
                    }
                } else {
                    if (inlineContainer) inlineContainer.style.display = 'none';
                    closeModal('wahaQrModal');
                }

                lastWahaStatus = status;
            } catch (err) {
                console.error("Failed to check WAHA status:", err);
            }
        }
        
        function openWahaQrFromIndicator() {
            if (lastWahaStatus === 'SCAN_QR_CODE') {
                openModal('wahaQrModal');
            } else {
                checkWahaStatus(true);
            }
        }
        
        async function loadWahaEvents() {
            try {
                const response = await fetch(API_URL + 'waha/events');
                const events = await response.json();
                
                const tbody = document.getElementById('waha-events-tbody');
                if (!tbody) return;
                
                if (events.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">No connection events logged yet.</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                events.forEach(e => {
                    tbody.innerHTML += `
                        <tr>
                        <td style="font-weight: 500; white-space: nowrap;">${formatIST(e.timestamp)}</td>
                            <td><span style="padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; background: rgba(59,130,246,0.1); color: var(--primary-color);">${e.event_type}</span></td>
                            <td><span style="font-weight: 600; color: ${e.status === 'WORKING' ? 'var(--success-color)' : 'var(--danger-color)'}">${e.status}</span></td>
                            <td style="color: var(--text-secondary); font-size: 0.9rem;">${escapeHtml(e.details || '')}</td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error("Failed to load WAHA events:", err);
            }
        }
        
        async function loadWahaSettings() {
            try {
                const response = await fetch(API_URL + 'settings/waha');
                const settings = await response.json();
                
                document.getElementById('settingAlertPhone').value = settings.waha_alert_phone || '';
                document.getElementById('settingAlertEmail').value = settings.smtp_to || '';
                document.getElementById('settingSmtpHost').value = settings.smtp_host || '';
                document.getElementById('settingSmtpPort').value = settings.smtp_port || '';
                document.getElementById('settingSmtpUser').value = settings.smtp_user || '';
                document.getElementById('settingSmtpPass').value = settings.smtp_pass || '';
                
                if (settings.smtp_to) document.getElementById('info-smtp-to').innerText = settings.smtp_to;
                if (settings.waha_alert_phone) document.getElementById('info-waha-phone').innerText = settings.waha_alert_phone;
            } catch (err) {
                console.error("Failed to load WAHA settings:", err);
            }
        }
        
        async function saveWahaSettings(e) {
            e.preventDefault();
            try {
                const payload = {
                    waha_alert_phone: document.getElementById('settingAlertPhone').value,
                    smtp_to: document.getElementById('settingAlertEmail').value,
                    smtp_host: document.getElementById('settingSmtpHost').value,
                    smtp_port: document.getElementById('settingSmtpPort').value,
                    smtp_user: document.getElementById('settingSmtpUser').value,
                    smtp_pass: document.getElementById('settingSmtpPass').value
                };
                
                const response = await fetch(API_URL + 'settings/waha', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const res = await response.json();
                if (res.success) {
                    closeModal('alertSettingsModal');
                    loadWahaSettings();
                    // Show a non-blocking success toast
                    const toast = document.createElement('div');
                    toast.innerText = '✓ Alert settings saved!';
                    toast.style.cssText = 'position:fixed;bottom:2rem;right:2rem;background:#10b981;color:white;padding:0.75rem 1.5rem;border-radius:10px;font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,0.15);z-index:9999;transition:opacity 0.4s;';
                    document.body.appendChild(toast);
                    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 400); }, 2500);
                } else {
                    alert("Failed to save settings.");
                }
            } catch (err) {
                console.error("Failed to save WAHA settings:", err);
                alert("Error saving settings.");
            }
        }

        function openAlertSettingsModal() {
            loadWahaSettings();
            openModal('alertSettingsModal');
        }
        let tasksList = [];

        async function fetchTasks() {
            try {
                const res = await fetch(API_URL + 'tasks');
                tasksList = await res.json();
                renderTasks(tasksList);
            } catch (err) {
                console.error("Error fetching tasks:", err);
            }
        }

        function renderTasks(tasks) {
            const tbody = document.getElementById('tasks-tbody');
            tbody.innerHTML = '';
            
            // Map JID to Group Names
            const groups_list = waha_groups || [];

            const nowTs = new Date().getTime();
            tasks.forEach(t => {
                // Auto-detect overdue client-side: if due_time is in past and not completed
                const dueTs = t.due_time ? new Date(t.due_time.replace(/-/g, '/').replace('T', ' ')).getTime() : null;
                if (t.status === 'pending' && dueTs && dueTs < nowTs) {
                    t.status = 'overdue';
                }
                let badgeClass = 'badge-gray';
                if (t.status === 'completed') badgeClass = 'badge-green';
                else if (t.status === 'overdue') badgeClass = 'badge-red';
                else if (t.status === 'pending_approval') badgeClass = 'badge-yellow';

                // Find group name
                let groupName = 'Private Only / No Group';
                if (t.whatsapp_group_id) {
                    const found = groups_list.find(g => g.id === t.whatsapp_group_id);
                    if (found) {
                        groupName = found.name;
                    } else {
                        groupName = t.whatsapp_group_id.split('@')[0];
                    }
                }

                // Assigned Task badge
                let taskTypeLabel = t.task_type.toUpperCase();
                if (t.task_type === 'general') taskTypeLabel = 'SILO CLEANING';
                else if (t.task_type === 'meeting') taskTypeLabel = 'WED MEETING';
                else if (t.task_type === 'approval') taskTypeLabel = 'FEED APPROVAL';
                else if (t.task_type === 'personal') taskTypeLabel = 'PERSONAL';

                const names = (t.assigned_person_name || '').split(',').map(n => n.trim()).filter(Boolean);
                const phones = (t.assigned_person_phone || '').split(',').map(p => p.trim()).filter(Boolean);
                const formattedAssignees = names.length > 0 ? names.map((name, idx) => {
                    const phone = phones[idx] || '';
                    return `${name} (${phone})`;
                }).join(', ') : (t.assigned_person_name || 'Group Member');

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${formattedAssignees}</strong></td>
                        <td>${groupName}</td>
                        <td><span class="badge badge-blue">${taskTypeLabel}</span></td>
                        <td>
                            <div style="max-width:250px; font-size:0.9rem;">
                                ${t.task_name}
                                ${t.approver_phone ? `<br><small style="color:var(--text-secondary)">Approver: ${t.approver_phone}</small>` : ''}
                            </div>
                        </td>
                        <td style="text-transform: capitalize; font-weight: 500;">${t.frequency || 'once'}</td>
                        <td style="text-transform: capitalize; font-weight: 500; color: #b45309;">${t.repeat_interval && t.repeat_interval !== 'none' ? t.repeat_interval : 'None'}</td>
                        <td>${formatDateTime(t.due_time)}</td>
                        <td><span class="badge ${badgeClass}" style="text-transform: uppercase;">${t.status}</span></td>
                        <td>
                            <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
                                <button class="btn btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="editTask(${t.id})">Edit</button>
                                ${t.status !== 'completed' ? `<button class="btn btn-primary" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="completeTask(${t.id})">Done</button>` : ''}
                                <button class="btn" style="padding:0.25rem 0.5rem; font-size:0.8rem; background:#fee2e2; color:#ef4444; border:1px solid #fca5a5; margin:0;" onclick="deleteTask(${t.id})">Delete</button>
                                ${t.completion_details ? `<button class="btn" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="alert('Completion Details:\\n\\n' + \`${t.completion_details.replace(/'/g, "\\'")}\`)">Details</button>` : ''}
                            </div>
                        </td>
                    </tr>
                `;
            });
            
            // Populate Tasks & Approvals dashboard stats
            const uniqueTaskPhones = new Set();
            tasks.forEach(t => {
                if (t.assigned_person_phone) {
                    t.assigned_person_phone.split(',').forEach(p => uniqueTaskPhones.add(p.trim()));
                }
            });
            uniqueTaskPhones.delete(''); // remove empty if any
            
            const taskStatEmployees = document.getElementById('stat-task-employees');
            if (taskStatEmployees) taskStatEmployees.innerText = uniqueTaskPhones.size;
            
            const taskStatGroups = document.getElementById('stat-task-groups');
            if (taskStatGroups) taskStatGroups.innerText = new Set(tasks.map(t => t.whatsapp_group_id).filter(g => g)).size;
            
            const statTasks = document.getElementById('stat-tasks');
            if (statTasks) statTasks.innerText = tasks.length;
        }

        function openCreateTaskModal() {
            document.getElementById('task-id').value = '';
            document.getElementById('task-form').reset();
            document.getElementById('task-modal-title').innerText = "Create Task";
            
            // Populate groups select options dynamically (filtering hidden ones)
            const groupSelect = document.getElementById('task-group-id');
            groupSelect.innerHTML = '<option value="">No Group / Private Only</option>';
            if (waha_groups) {
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => {
                    groupSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`;
                });
            }

            renderMembersChecklist([], []);
            renderTaskCheckboxes([]);
            handleTaskTypeCheckboxChange();
            openModal('createTaskModal');
        }

        function closeCreateTaskModal() {
            closeModal('createTaskModal');
        }

        function handleTaskTypeCheckboxChange() {
            const personalCheckbox = document.getElementById('task-report-Personal');
            const messageGroup = document.getElementById('task-message-group');
            const approverRow = document.getElementById('task-approver-row');
            
            if (personalCheckbox && personalCheckbox.checked) {
                messageGroup.style.display = 'block';
            } else {
                messageGroup.style.display = 'none';
            }
            
            const checkedTypes = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value.toLowerCase());
            const hasFeed = checkedTypes.some(t => t.includes('feed') || t.includes('formula'));
            if (hasFeed) {
                approverRow.style.display = 'block';
            } else {
                approverRow.style.display = 'none';
            }
        }

        async function handleTaskSubmit(e) {
            e.preventDefault();
            const taskId = document.getElementById('task-id').value;
            
            // Get selected members
            const selectedMembers = Array.from(document.querySelectorAll('.task-member-checkbox:checked'));
            const phones = selectedMembers.map(cb => cb.value).join(', ');
            const names = selectedMembers.map(cb => cb.getAttribute('data-name')).join(', ');
            
            // Get selected task/report types
            const checkedTaskTypes = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value).join(', ');
            
            const groupSelectVal = document.getElementById('task-group-id').value;
            
            if (!phones && !groupSelectVal) {
                alert("Please select either a member or a WhatsApp group!");
                return;
            }
            
            if (!checkedTaskTypes) {
                alert("Please select at least one Assigned Task / Report type!");
                return;
            }
            
            let taskName = '';
            const personalChecked = document.getElementById('task-report-Personal')?.checked;
            if (personalChecked) {
                taskName = document.getElementById('task-name').value.trim();
                if (!taskName) {
                    alert("Please type a custom text message for your Personal reminder!");
                    return;
                }
            } else {
                taskName = checkedTaskTypes;
            }
            
            const payload = {
                task_name: taskName,
                task_type: checkedTaskTypes,
                assigned_person_name: names || null,
                assigned_person_phone: phones || null,
                whatsapp_group_id: groupSelectVal || null,
                due_time: document.getElementById('task-due-time').value,
                completion_keywords: null,
                approver_phone: document.getElementById('task-approver-phone').value || null,
                frequency: document.getElementById('task-frequency').value,
                repeat_interval: document.getElementById('task-repeat-interval').value
            };

            try {
                const url = taskId ? (API_URL + 'tasks/' + taskId) : (API_URL + 'tasks');
                const method = taskId ? 'PUT' : 'POST';
                const res = await fetch(url, {
                    method: method,
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    closeCreateTaskModal();
                    fetchTasks();
                } else {
                    alert("Error saving task: " + (data.error || JSON.stringify(data)));
                }
            } catch (err) {
                console.error("Error submitting task:", err);
            }
        }

        async function editTask(id) {
            const t = tasksList.find(x => x.id === id);
            if (!t) return;
            
            // Re-populate groups list first (filtering hidden ones)
            const groupSelect = document.getElementById('task-group-id');
            groupSelect.innerHTML = '<option value="">No Group / Private Only</option>';
            if (waha_groups) {
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => {
                    groupSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`;
                });
            }
            
            document.getElementById('task-id').value = t.id;
            document.getElementById('task-group-id').value = t.whatsapp_group_id || '';
            
            if (t.due_time) {
                const dt = new Date(t.due_time);
                const tzoffset = dt.getTimezoneOffset() * 60000;
                const localISOTime = (new Date(dt.getTime() - tzoffset)).toISOString().slice(0, 16);
                document.getElementById('task-due-time').value = localISOTime;
            }
            
            document.getElementById('task-frequency').value = t.frequency || 'once';
            document.getElementById('task-repeat-interval').value = t.repeat_interval || 'none';
            document.getElementById('task-approver-phone').value = t.approver_phone || '';
            
            // Parse assigned person phones & names
            const selectedPhones = (t.assigned_person_phone || '').split(',').map(p => p.trim()).filter(Boolean);
            renderMembersChecklist([], selectedPhones);
            
            // Parse assigned task/report types
            const selectedTasks = (t.task_type || '').split(',').map(x => x.trim()).filter(Boolean);
            renderTaskCheckboxes(selectedTasks);
            
            // Set custom message value if Personal was checked
            if (selectedTasks.includes('Personal')) {
                document.getElementById('task-name').value = t.task_name || '';
            } else {
                document.getElementById('task-name').value = '';
            }
            
            document.getElementById('task-modal-title').innerText = "Edit Task";
            handleTaskTypeCheckboxChange();
            openModal('createTaskModal');
        }

        async function completeTask(id) {
            if (!confirm("Are you sure you want to mark this task as completed?")) return;
            try {
                const res = await fetch(API_URL + `tasks/${id}/complete`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({details: "Manually marked completed from dashboard"})
                });
                const data = await res.json();
                if (data.success) {
                    fetchTasks();
                } else {
                    alert('Failed to mark as done. Please try again.');
                }
            } catch (err) {
                console.error("Error completing task:", err);
            }
        }

        async function deleteTask(id) {
            if (!confirm("Are you sure you want to delete this task?")) return;
            try {
                const res = await fetch(API_URL + `tasks/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.success) {
                    fetchTasks();
                }
            } catch (err) {
                console.error("Error deleting task:", err);
            }
        }

        window.onload = async () => {
            await fetchWahaGroups();
            await loadReportTypesDropdowns();
            await loadTaskTypesDropdowns();
            await fetchReminders();
            await fetchTasks();
            renderMembersChecklist([]);
            
            // WAHA Session Monitoring Init
            await checkWahaStatus();
            await loadWahaEvents();
            await loadWahaSettings();
            
            // Periodically check status (every 60s) and events (every 2 min)
            setInterval(() => checkWahaStatus(), 60000);
            setInterval(() => loadWahaEvents(), 120000);
        };
    </script>
</body>

</html>
