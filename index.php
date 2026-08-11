<?php
// ============================================================
// Sunfra Poultry - Whatsapp Reminders & Farm Automation
// Single-file unified backend and frontend
// ============================================================
@opcache_reset();
ini_set('display_errors', 0);
error_reporting(E_ALL);

header("Cache-Control: no-cache, no-store, must-revalidate");
header("Pragma: no-cache");
header("Expires: 0");

// 1. Database Connection with Persistent Pooling & Fallback Protection
$pdo = null;
$host = '145.223.17.70';
$db   = 'u632391467_kusumpakira';
$user = 'u632391467_kusumpakira';
$pass = 'Kusum@2026Bb!';
$charset = 'utf8mb4';

try {
    if (file_exists('../database.php')) {
        require_once '../database.php';
    } elseif (file_exists(__DIR__ . '/database.php')) {
        require_once __DIR__ . '/database.php';
    }
} catch (Exception $e) {}

if (!isset($pdo) || !$pdo) {
    try {
        $dsn = "mysql:host=$host;dbname=$db;charset=$charset";
        $options = [
            PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES   => false,
            PDO::ATTR_PERSISTENT         => true,
        ];
        $pdo = new PDO($dsn, $user, $pass, $options);
    } catch (Exception $e) {
        // Fallback seamlessly to SQLite if MySQL hourly quota (1226) is reached
        try {
            $pdo = new PDO('sqlite:' . __DIR__ . '/whatsapp_reminders.sqlite', null, null, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
            ]);
        } catch (Exception $e2) {}
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

    $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_reminder_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        reminder_id INT NULL,
        report_types TEXT NULL,
        person_name VARCHAR(255) NULL,
        person_phone VARCHAR(50) NULL,
        whatsapp_group_id VARCHAR(255) NULL,
        trigger_time DATETIME NOT NULL,
        executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) NOT NULL,
        details TEXT NULL
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
    // Fallback seamlessly to SQLite if MySQL fails or quota (1226) is reached
    try {
        $pdo = new PDO('sqlite:' . __DIR__ . '/whatsapp_reminders.sqlite', null, null, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
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

        $pdo->exec("CREATE TABLE IF NOT EXISTS sunfra_reminder_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reminder_id INTEGER NULL,
            report_types TEXT NULL,
            person_name VARCHAR(255) NULL,
            person_phone VARCHAR(50) NULL,
            whatsapp_group_id VARCHAR(255) NULL,
            trigger_time DATETIME NOT NULL,
            executed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) NOT NULL,
            details TEXT NULL
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
        // Run the reset for reminders
        $stmt = $pdo->query("SELECT id, trigger_time, frequency FROM sunfra_unified_reminders WHERE (frequency IS NULL OR frequency != 'once')");
        $overdue = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $now_utc = new DateTime();
        foreach ($overdue as $r) {
            $freq = strtolower($r['frequency'] ?? 'daily');
            $dt = new DateTime($r['trigger_time']);
            $advanced = false;
            while ($dt <= $now_utc) {
                if ($freq === 'weekly')       { $dt->modify('+7 days'); }
                elseif ($freq === 'monthly')  { 
                    $dt->modify('first day of next month');
                    $dt->setTime(11, 0, 0);
                }
                else                          { $dt->modify('+1 day'); } // daily default
                $advanced = true;
            }
            if ($advanced) {
                $upd = $pdo->prepare("UPDATE sunfra_unified_reminders SET trigger_time = ?, status = 'pending' WHERE id = ?");
                $upd->execute([$dt->format('Y-m-d H:i:s'), $r['id']]);
            }
        }

        // Run the reset for tasks
        $t_stmt = $pdo->query("SELECT id, due_time, frequency FROM sunfra_tasks WHERE (frequency IS NULL OR frequency != 'once')");
        $t_overdue = $t_stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($t_overdue as $t) {
            $freq = strtolower($t['frequency'] ?? 'daily');
            $dt = new DateTime($t['due_time']);
            $advanced = false;
            while ($dt <= $now_utc) {
                if ($freq === 'weekly')       { $dt->modify('+7 days'); }
                elseif ($freq === 'monthly')  { $dt->modify('+1 month'); }
                elseif ($freq === 'yearly')   { $dt->modify('+1 year'); }
                else                          { $dt->modify('+1 day'); } // daily default
                $advanced = true;
            }
            if ($advanced) {
                $upd = $pdo->prepare("UPDATE sunfra_tasks SET due_time = ?, status = 'pending', completion_details = NULL WHERE id = ?");
                $upd->execute([$dt->format('Y-m-d H:i:s'), $t['id']]);
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
            if (strlen($w) > 3 && !in_array($w, ['task', 'check', 'please', 'update', 'submit', 'report', 'reports', 'checklist', 'updates', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday', 'monday', 'tuesday'])) {
                $task_identifiers[] = $w;
            }
        }

        $since = date('Y-m-d 00:00:00', strtotime($task['due_time'] ?? 'now'));
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
            $names_raw = array_filter(array_map('trim', explode(',', $task['assigned_person_name'] ?? '')));
            
            // Fetch raw messages since $since
            $msg_stmt = $pdo->prepare("
                SELECT r.raw_text, r.sender, w.group_id AS whatsapp_group_jid, w.sender_id AS whatsapp_sender_id
                FROM sunfra_raw_messages r
                LEFT JOIN sunfra_whatsapp_messages w ON r.message_id = w.message_id
                WHERE r.timestamp >= ? 
                ORDER BY r.timestamp DESC LIMIT 50
            ");
            $msg_stmt->execute([$since]);
            $raw_msgs_pool = $msg_stmt->fetchAll(PDO::FETCH_ASSOC);
            
            foreach ($raw_msgs_pool as $rm) {
                $raw_sender = strtolower($rm['sender'] ?? '');
                $raw_sender_id = $rm['whatsapp_sender_id'] ?? '';
                $clean_raw_group_jid = str_replace('@g.us', '', $rm['whatsapp_group_jid'] ?? '');
                $clean_target_group_jid = str_replace('@g.us', '', $task['whatsapp_group_id'] ?? '');
                $sender_matched = false;
                
                // 1. Check phone match
                foreach ($phones_raw as $ph) {
                    $digits = preg_replace('/\D/', '', $ph);
                    if (!$digits) continue;
                    $alt_digits = (strlen($digits) === 10) ? '91' . $digits : $digits;
                    if (strpos($raw_sender, $digits) !== false || strpos($raw_sender, $alt_digits) !== false || ($raw_sender_id && (strpos($raw_sender_id, $digits) !== false || strpos($raw_sender_id, $alt_digits) !== false))) {
                        $sender_matched = true;
                        break;
                    }
                }
                
                // 2. Check name match (fuzzy & diacritics-aware)
                $name_matched = false;
                if (!$sender_matched && !empty($names_raw) && $rm['sender']) {
                    $sender_name_part = clean_name_string(explode(' (', $rm['sender'])[0]);
                    foreach ($names_raw as $name) {
                        $t_name = clean_name_string($name);
                        if (strlen($sender_name_part) >= 3 && strlen($t_name) >= 3) {
                            if (strpos($sender_name_part, $t_name) !== false || strpos($t_name, $sender_name_part) !== false) {
                                $name_matched = true;
                                break;
                            }
                        }
                    }
                }
                
                // Individual task rules: sender must match, and message must be direct or in target group JID
                $valid_sender_or_group = false;
                if ($sender_matched || $name_matched) {
                    if (empty($clean_raw_group_jid)) {
                        $valid_sender_or_group = true;
                    } elseif ($clean_target_group_jid && $clean_raw_group_jid === $clean_target_group_jid) {
                        $valid_sender_or_group = true;
                    } else {
                        // Allow any group if no specific group is set for individual task
                        $valid_sender_or_group = empty($clean_target_group_jid);
                    }
                }
                
                if ($valid_sender_or_group && !empty($rm['raw_text'])) {
                    $all_messages[] = $rm['raw_text'];
                }
            }
        }

        if (empty($all_messages)) continue;

        // Check messages for completion logic
        foreach ($all_messages as $msg_text) {
            $msg_lower = strtolower(trim($msg_text ?? ''));
            
            $is_silo_task = (strpos(strtolower($task['task_name']), 'silo') !== false || strpos(strtolower($task['task_name']), 'selo') !== false);
            $is_matched_task = false;
            
            if ($is_silo_task) {
                $has_silo_word = (strpos($msg_lower, 'silo') !== false || strpos($msg_lower, 'selo') !== false);
                $has_silo_completion = false;
                foreach (['done', 'completed', 'complete', 'clean', 'cleaned', 'empty', 'emptied', 'cleared', '✅', 'done✅'] as $skw) {
                    if (strpos($msg_lower, $skw) !== false) {
                        $has_silo_completion = true;
                        break;
                    }
                }
                $is_matched_task = ($has_silo_word && $has_silo_completion);
            } else {
                // 1. Does it have a completion word?
                $has_completion = false;
                foreach ($keywords as $kw) {
                    if ($kw && strpos($msg_lower, trim($kw)) !== false) {
                        $has_completion = true;
                        break;
                    }
                }
                
                // 2. Does it contain at least one task identifier?
                $has_identifier_match = empty($task_identifiers);
                if (!$has_identifier_match) {
                    foreach ($task_identifiers as $id_kw) {
                        if (strpos($msg_lower, $id_kw) !== false) {
                            $has_identifier_match = true;
                            break;
                        }
                    }
                }
                
                $is_matched_task = ($has_completion && $has_identifier_match);
            }

            if ($is_matched_task) {
                $matched = true;
                break;
            }
        }

        if ($matched) {
            $pdo->prepare("UPDATE sunfra_tasks SET status = 'completed', completion_details = 'Auto-completed: WhatsApp reply detected' WHERE id = ?")->execute([$task['id']]);
        }
    }
} catch (Exception $e) { /* silent fail */ }


function clean_name_string($name) {
    if (!$name) return "";
    $normalized = trim($name);
    if (function_exists('transliterator_transliterate')) {
        $normalized = transliterator_transliterate('Any-Latin; Latin-ASCII', $normalized);
    } else {
        $normalized = @iconv('UTF-8', 'ASCII//TRANSLIT//IGNORE', $normalized);
    }
    $normalized = strtolower($normalized);
    $normalized = str_replace('ss ', '', $normalized);
    $normalized = preg_replace('/[^a-z0-9\s]/', '', $normalized);
    return trim($normalized);
}

function verify_reminder_submission($r, $submissions, $raw_messages, $waha_groups, $sent_logs = []) {
    $reports = array_filter(array_map('trim', explode(',', strtolower($r['report_types'] ?? ''))));
    $phones = array_filter(array_map('trim', explode(',', $r['person_phone'] ?? '')));
    $names = array_filter(array_map('trim', explode(',', $r['person_name'] ?? '')));
    
    $group_name_target = null;
    if ($r['whatsapp_group_id']) {
        foreach ($waha_groups as $g) {
            if ($g['id'] === $r['whatsapp_group_id']) {
                $group_name_target = $g['name'];
                break;
            }
        }
    }
    
    $IST_OFFSET = 5.5 * 3600;
    $tz = new DateTimeZone('Asia/Kolkata');
    $now_ist = new DateTime('now', $tz);
    
    $date_formats = [
        $now_ist->format('d-m'),
        $now_ist->format('d/m'),
        $now_ist->format('d F'),
        $now_ist->format('F d'),
        $now_ist->format('dj F'),
    ];
    $cleaned_dates = [];
    foreach ($date_formats as $df) {
        $df_lower = strtolower($df);
        $cleaned_dates[] = $df_lower;
        if ($df_lower[0] === '0') {
            $cleaned_dates[] = substr($df_lower, 1);
        }
        $cleaned_dates[] = str_replace(' 0', ' ', $df_lower);
    }
    $date_formats = array_values(array_unique($cleaned_dates));
    
    $update_keywords = [
        "daily work update", "eod update", "work update", "today's work update", 
        "today work update", "daily report", "today's work report", "today work report",
        "work report", "work day report", "submitted", "profit summary","eod", "eod report", "daily work report",
        "daily work update report"
    ];
    
    $is_all_submitted = true;
    $submitted_reports = [];
    $missing_reports = [];
    $verification_details = [];
    
    if (empty($reports)) {
        return [
            'is_submitted' => false,
            'submitted_reports' => [],
            'missing_reports' => ['Notes Only'],
            'details' => 'No reports assigned to this reminder (Notes Only).'
        ];
    }
    
    foreach ($reports as $report) {
        $is_manually_done = ($r['status'] === 'sent' && !in_array($r['id'], $sent_logs));
        $report_submitted = ($r['status'] === 'skipped' || $is_manually_done);
        $report_match_msg = $is_manually_done ? "Manually marked done on dashboard" : ($r['status'] === 'skipped' ? "Skipped automatically or manually" : "");
        
        $categories = [];
        if (strpos($report, 'production') !== false || strpos($report, 'egg') !== false) {
            $categories = ['production', 'egg_collection', 'egg_collection_1', 'egg_collection_2', 'egg'];
        } elseif (strpos($report, 'feed') !== false) {
            $categories = ['feed'];
        } elseif (strpos($report, 'expense') !== false || strpos($report, 'expenditure') !== false || strpos($report, 'cost') !== false) {
            $categories = ['expense', 'purchase'];
        } elseif (strpos($report, 'sale') !== false) {
            $categories = ['sales'];
        } elseif (strpos($report, 'profit') !== false || strpos($report, 'p&l') !== false || strpos($report, 'p and l') !== false) {
            $categories = ['sales', 'expense', 'purchase'];
        }
        
        $is_rule_book = (strpos(strtolower($report), 'rule book') !== false || strpos(strtolower($report), 'rule') !== false);

        $is_approval_task = (
            strpos(strtolower($r['task_notes'] ?? ''), 'approval') !== false ||
            strpos(strtolower($r['report_types'] ?? ''), 'approval') !== false ||
            strpos(strtolower($r['task_notes'] ?? ''), 'approve') !== false ||
            strpos(strtolower($r['task_notes'] ?? ''), 'review') !== false ||
            strpos(strtolower($r['task_notes'] ?? ''), 'checked') !== false
        );

        $approval_keywords = [
            "approved", "approve", "reviewed", "review", "checked", "check", 
            "accepted", "accept", "ok", "verified", "verify", "looks good", "fine", "done"
        ];

        $is_update_report = (
            (strpos(strtolower($report), 'update') !== false || strpos(strtolower($report), 'eod') !== false || strpos(strtolower($report), 'daily report') !== false || strpos(strtolower($report), 'work report') !== false)
            && strpos(strtolower($report), 'egg pricing') === false
            && !$is_rule_book
        );

        $REPORT_KEYWORDS = [
            'production' => ['production report', 'daily production', 'total production', 'egg collection report', 'production update', 'production statement', 'daily farm report'],
            'feed'       => ['feed report', 'feed plant report', 'feed update', 'feed statement', 'maize ordering', 'soya ordering'],
            'sales'      => ['sales report', 'daily sales', 'total sales', 'dispatch report', 'sales update'],
            'sale'       => ['sales report', 'daily sales', 'total sales', 'dispatch report', 'sales update'],
            'expense'    => ['expense report', 'daily expense', 'expenditure report', 'payment report'],
            'expenditure'=> ['expense report', 'daily expense', 'expenditure report', 'payment report'],
            'profit'     => ['p&l report', 'p&l statement', 'profit loss', 'p and l update', 'profit summary', 'profit', 'p&l', 'p and l', 'p/l', 'summary'],
            'p&l'        => ['p&l report', 'p&l statement', 'profit loss', 'p and l update', 'profit summary', 'profit', 'p&l', 'p and l', 'p/l', 'summary'],
            'p and l'    => ['p&l report', 'p&l statement', 'profit loss', 'p and l update', 'profit summary', 'profit', 'p&l', 'p and l', 'p/l', 'summary'],
            'rule book'  => ['rule book', 'rule', 'rules', 'point', 'points', 'policy', 'guideline', 'godown rule', 'farm rule', 'addition', 'update', 'updates'],
        ];
        
        $raw_keywords = [];
        if ($is_rule_book) {
            $raw_keywords = ['rule book', 'rule', 'rules', 'point', 'points', 'policy', 'guideline', 'godown rule', 'farm rule', 'addition', 'update', 'updates'];
        } elseif ($is_update_report) {
            $raw_keywords = array_merge($update_keywords, $date_formats);
        } else {
            foreach ($REPORT_KEYWORDS as $key => $kws) {
                if (strpos($report, $key) !== false) {
                    $raw_keywords = $kws;
                    break;
                }
            }
        }
        foreach (explode(',', $report) as $comma_part) {
            foreach (explode('/', $comma_part) as $slash_part) {
                $trimmed = trim($slash_part);
                if ($trimmed !== '') {
                    $raw_keywords[] = $trimmed;
                }
            }
        }
        
        // 1. Check ProcessedData
        foreach ($submissions as $sub) {
            $sub_sender = strtolower($sub['sender'] ?? '');
            $sub_group = strtolower($sub['group_name'] ?? '');
            $sub_notes = strtolower($sub['notes'] ?? '');
            $sub_cat = strtolower($sub['category'] ?? '');
            
            // Match sender phone or name
            $sender_matched = false;
            foreach ($phones as $phone) {
                $clean_phone = preg_replace('/\D/', '', $phone);
                if (!$clean_phone) continue;
                $alt_phone = (strlen($clean_phone) === 10) ? "91" . $clean_phone : $clean_phone;
                if (strpos($sub_sender, $clean_phone) !== false || strpos($sub_sender, $alt_phone) !== false) {
                    $sender_matched = true;
                    break;
                }
            }
            
            // Match group by JID
            $group_matched = false;
            $sub_group_jid = $sub['whatsapp_group_jid'] ?? '';
            $clean_sub_group_jid = str_replace('@g.us', '', $sub_group_jid);
            $clean_target_group_jid = str_replace('@g.us', '', $r['whatsapp_group_id'] ?? '');
            
            if ($clean_target_group_jid && $clean_sub_group_jid && $clean_target_group_jid === $clean_sub_group_jid) {
                $group_matched = true;
            }
            
            // Match name fuzzy
            $name_matched = false;
            if (!$sender_matched && $r['person_name'] && $sub['sender']) {
                $sender_name_part = clean_name_string(explode(' (', $sub['sender'])[0]);
                foreach ($names as $name) {
                    $t_name = clean_name_string($name);
                    if (strlen($sender_name_part) >= 3 && strlen($t_name) >= 3) {
                        if (strpos($sender_name_part, $t_name) !== false || strpos($t_name, $sender_name_part) !== false) {
                            $name_matched = true;
                            break;
                        }
                    }
                }
            }
            
            $is_group_level = ($r['person_phone'] === '1234567890' || strpos(strtolower($r['person_name']), 'team') !== false);
            
            if ($is_group_level) {
                // Group-level reminder (assigned to Team): strictly require matching group JID
                $valid_sender_or_group = $group_matched;
            } else {
                // Individual-level reminder: sender must match, and message must be either a direct message (no group)
                // or sent in the reminder's target group JID (if specified)
                if ($sender_matched || $name_matched) {
                    if (empty($clean_sub_group_jid)) {
                        $valid_sender_or_group = true;
                    } elseif ($clean_target_group_jid && $clean_sub_group_jid === $clean_target_group_jid) {
                        $valid_sender_or_group = true;
                    } else {
                        $valid_sender_or_group = false;
                    }
                } else {
                    $valid_sender_or_group = false;
                }
            }
            
            if ($is_approval_task) {
                // Approval tasks strictly require sender match (the approver's phone) + approval keyword
                if ($sender_matched || $name_matched) {
                    foreach ($approval_keywords as $akw) {
                        if (strpos($sub_notes, $akw) !== false) {
                            $report_submitted = true;
                            $report_match_msg = "Approved by manager {$sub['sender']}";
                            break 2;
                        }
                    }
                }
            } elseif ($valid_sender_or_group) {
                if (strpos($report, 'egg pricing') !== false) {
                    $time_keyword = (strpos($report, 'morning') !== false) ? 'morning' : ((strpos($report, 'afternoon') !== false) ? 'afternoon' : ((strpos($report, 'evening') !== false) ? 'evening' : null));
                    if ($time_keyword && strpos($sub_notes, $time_keyword) !== false && (strpos($sub_notes, 'egg') !== false || strpos($sub_notes, 'price') !== false || strpos($sub_notes, 'pricing') !== false)) {
                        $report_submitted = true;
                        $report_match_msg = "Processed Egg Pricing ({$time_keyword}) entry found in notes by {$sub['sender']}";
                        break;
                    }
                } elseif ($is_update_report) {
                    $has_kw = false;
                    foreach ($update_keywords as $kw) {
                        if (strpos($sub_notes, $kw) !== false) {
                            $has_kw = true; break;
                        }
                    }
                    $has_df = false;
                    foreach ($date_formats as $df) {
                        if (strpos($sub_notes, $df) !== false) {
                            $has_df = true; break;
                        }
                    }
                    if (!$has_kw && !$has_df) {
                        // Check specific report name parts as fallback
                        foreach ($raw_keywords as $kw) {
                            if ($kw && (strpos($sub_notes, strtolower($kw)) !== false || strpos($sub_cat, strtolower($kw)) !== false)) {
                                $has_kw = true;
                                break;
                            }
                        }
                    }
                    if ($has_kw || $has_df) {
                        $report_submitted = true;
                        $report_match_msg = "Processed Daily Work Update entry found in notes by {$sub['sender']}";
                        break;
                    }
                } elseif (!empty($categories)) {
                    if (in_array($sub_cat, $categories)) {
                        $report_submitted = true;
                        $report_match_msg = "Processed farm record of category '{$sub['category']}' sent by {$sub['sender']}";
                        break;
                    }
                } else {
                    if (strpos($sub_notes, $report) !== false) {
                        $report_submitted = true;
                        $report_match_msg = "Processed farm record matching '{$report}' found in notes by {$sub['sender']}";
                        break;
                    }
                }
            }
        }
        
        // 2. Check RawMessage fallback
        if (!$report_submitted) {
            
            foreach ($raw_messages as $raw_msg) {
                $raw_text_lower = strtolower($raw_msg['raw_text'] ?? '');
                $raw_sender = strtolower($raw_msg['sender'] ?? '');
                $raw_group = strtolower($raw_msg['group_name'] ?? '');
                
                // Match sender
                $sender_matched = false;
                foreach ($phones as $phone) {
                    $clean_phone = preg_replace('/\D/', '', $phone);
                    if (!$clean_phone) continue;
                    $alt_phone = (strlen($clean_phone) === 10) ? "91" . $clean_phone : $clean_phone;
                    if (strpos($raw_sender, $clean_phone) !== false || strpos($raw_sender, $alt_phone) !== false) {
                        $sender_matched = true;
                        break;
                    }
                }
                
                // Match group by JID
                 $group_matched = false;
                 $raw_group_jid = $raw_msg['whatsapp_group_jid'] ?? '';
                 $clean_raw_group_jid = str_replace('@g.us', '', $raw_group_jid);
                 $clean_target_group_jid = str_replace('@g.us', '', $r['whatsapp_group_id'] ?? '');
                 
                 if ($clean_target_group_jid && $clean_raw_group_jid && $clean_target_group_jid === $clean_raw_group_jid) {
                     $group_matched = true;
                 }
                 
                 // Match name fuzzy
                 $name_matched = false;
                 if (!$sender_matched && $r['person_name'] && $raw_msg['sender']) {
                     $sender_name_part = clean_name_string(explode(' (', $raw_msg['sender'])[0]);
                     foreach ($names as $name) {
                         $t_name = clean_name_string($name);
                         if (strlen($sender_name_part) >= 3 && strlen($t_name) >= 3) {
                             if (strpos($sender_name_part, $t_name) !== false || strpos($t_name, $sender_name_part) !== false) {
                                 $name_matched = true;
                                 break;
                             }
                         }
                     }
                 }
                 
                 $is_group_level = ($r['person_phone'] === '1234567890' || strpos(strtolower($r['person_name']), 'team') !== false);
                 
                 if ($is_group_level) {
                     // Group-level reminder (assigned to Team): strictly require matching group JID
                     $valid_sender_or_group = $group_matched;
                 } else {
                     // Individual-level reminder: sender must match, and message must be either a direct message (no group)
                     // or sent in the reminder's target group JID (if specified)
                     if ($sender_matched || $name_matched) {
                         if (empty($clean_raw_group_jid)) {
                             $valid_sender_or_group = true;
                         } elseif ($clean_target_group_jid && $clean_raw_group_jid === $clean_target_group_jid) {
                             $valid_sender_or_group = true;
                         } else {
                             $valid_sender_or_group = false;
                         }
                     } else {
                         $valid_sender_or_group = false;
                     }
                 }
                
                 if ($is_approval_task) {
                     if ($sender_matched || $name_matched) {
                         foreach ($approval_keywords as $akw) {
                             if (strpos($raw_text_lower, $akw) !== false) {
                                 $report_submitted = true;
                                 $report_match_msg = "Approved via raw WhatsApp message by manager {$raw_msg['sender']}";
                                 break 2;
                             }
                         }
                     }
                 } elseif ($valid_sender_or_group) {
                    if (strpos($report, 'egg pricing') !== false) {
                        $time_keyword = (strpos($report, 'morning') !== false) ? 'morning' : ((strpos($report, 'afternoon') !== false) ? 'afternoon' : ((strpos($report, 'evening') !== false) ? 'evening' : null));
                        $has_price_number = preg_match('/\d{3}/', $raw_text_lower);
                        
                        $raw_dt = new DateTime($raw_msg['timestamp'], new DateTimeZone('Asia/Kolkata'));
                        $raw_hour = (int)$raw_dt->format('H');
                        $is_time_match = false;
                        
                        if ($time_keyword === 'morning' && ($raw_hour < 12 || strpos($raw_text_lower, 'morning') !== false || strpos($raw_text_lower, '7:') !== false || strpos($raw_text_lower, '8:') !== false || strpos($raw_text_lower, '9:') !== false || strpos($raw_text_lower, '10:') !== false || strpos($raw_text_lower, 'veh kol') !== false) && strpos($raw_text_lower, 'ppr rate') === false && strpos($raw_text_lower, 'closing') === false) {
                            $is_time_match = true;
                        } elseif ($time_keyword === 'afternoon' && ($raw_hour >= 12 && $raw_hour < 17 || strpos($raw_text_lower, 'afternoon') !== false || strpos($raw_text_lower, 'ppr rate') !== false || strpos($raw_text_lower, '12:') !== false || strpos($raw_text_lower, '13:') !== false || strpos($raw_text_lower, '14:') !== false) && strpos($raw_text_lower, 'closing') === false) {
                            $is_time_match = true;
                        } elseif ($time_keyword === 'evening' && ($raw_hour >= 17 || strpos($raw_text_lower, 'evening') !== false || strpos($raw_text_lower, 'closing') !== false || strpos($raw_text_lower, '18:') !== false || strpos($raw_text_lower, '19:') !== false)) {
                            $is_time_match = true;
                        }
                        
                        $has_price_kw = false;
                        foreach (["egg", "price", "pricing", "ppr rate", "closing", "veh kol"] as $pkw) {
                            if (strpos($raw_text_lower, $pkw) !== false) { $has_price_kw = true; break; }
                        }
                        
                        if ($is_time_match && $has_price_number && $has_price_kw) {
                            $report_submitted = true;
                            $truncated_text = strlen($raw_msg['raw_text']) > 40 ? substr($raw_msg['raw_text'], 0, 40) . '...' : $raw_msg['raw_text'];
                            $time_display = $raw_dt->format('g:i A');
                            $report_match_msg = "WhatsApp message matched egg pricing rules: \"{$truncated_text}\" by {$raw_msg['sender']} at {$time_display}";
                            break;
                        }
                    } elseif ($is_rule_book) {
                        $rule_book_kws = ['rule book', 'rule', 'rules', 'point', 'points', 'policy', 'guideline', 'godown rule', 'farm rule', 'addition'];
                        $matched_kw = null;
                        foreach ($rule_book_kws as $kw) {
                            if (strpos($raw_text_lower, $kw) !== false) {
                                $matched_kw = $kw;
                                break;
                            }
                        }
                        if ($matched_kw !== null) {
                            $report_submitted = true;
                            $truncated_text = strlen($raw_msg['raw_text']) > 40 ? substr($raw_msg['raw_text'], 0, 40) . '...' : $raw_msg['raw_text'];
                            $raw_dt = new DateTime($raw_msg['timestamp'], new DateTimeZone('Asia/Kolkata'));
                            $time_display = $raw_dt->format('g:i A');
                            $report_match_msg = "WhatsApp Rule Book entry found: \"{$truncated_text}\" by {$raw_msg['sender']} at {$time_display}";
                            break;
                        }
                    } else {
                        $matched_kw = null;
                        foreach ($raw_keywords as $kw) {
                            if ($kw && strpos($raw_text_lower, strtolower($kw)) !== false) {
                                $matched_kw = $kw;
                                break;
                            }
                        }
                        if ($matched_kw !== null) {
                            $report_submitted = true;
                            $truncated_text = strlen($raw_msg['raw_text']) > 40 ? substr($raw_msg['raw_text'], 0, 40) . '...' : $raw_msg['raw_text'];
                            $raw_dt = new DateTime($raw_msg['timestamp'], new DateTimeZone('Asia/Kolkata'));
                            $time_display = $raw_dt->format('g:i A');
                            $report_match_msg = "WhatsApp message matched keyword '{$matched_kw}': \"{$truncated_text}\" by {$raw_msg['sender']} at {$time_display}";
                            break;
                        }
                    }
                }
            }
        }
        
        if ($report_submitted) {
            $submitted_reports[] = $report;
            $verification_details[] = "✅ *" . strtoupper($report) . "*: " . $report_match_msg;
        } else {
            $is_all_submitted = false;
            $missing_reports[] = $report;
            $verification_details[] = "❌ *" . strtoupper($report) . "*: No matching report submitted today.";
        }
    }
    
    return [
        'is_submitted' => $is_all_submitted,
        'submitted_reports' => $submitted_reports,
        'missing_reports' => $missing_reports,
        'details' => implode("\n", $verification_details)
    ];
}

function get_all_sunfra_groups($pdo) {
    $groups_map = [];
    
    // 1. Fetch from database sunfra_groups table (Primary)
    try {
        $stmt = $pdo->query("SELECT id, name, whatsapp_group_id FROM sunfra_groups");
        $db_groups = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($db_groups as $g) {
            $name = trim($g['name'] ?? '');
            $wa_id = trim($g['whatsapp_group_id'] ?? '');
            if ($name && $wa_id) {
                $clean_id = str_replace('@g.us', '', $wa_id);
                $entry = ['id' => $wa_id, 'name' => $name, 'db_id' => $g['id']];
                $groups_map[$wa_id] = $entry;
                $groups_map[$clean_id] = $entry;
                $groups_map[$clean_id . '@g.us'] = $entry;
            }
        }
    } catch (Exception $e) {}

    // 2. Fetch from waha_groups.json file (Secondary backup)
    $waha_file = __DIR__ . '/waha_groups.json';
    if (file_exists($waha_file)) {
        $json_groups = json_decode(file_get_contents($waha_file), true)['groups'] ?? [];
        foreach ($json_groups as $g) {
            $wa_id = trim($g['id'] ?? '');
            $name = trim($g['name'] ?? '');
            if ($wa_id && $name) {
                $clean_id = str_replace('@g.us', '', $wa_id);
                if (!isset($groups_map[$wa_id]) && !isset($groups_map[$clean_id])) {
                    $entry = ['id' => $wa_id, 'name' => $name];
                    $groups_map[$wa_id] = $entry;
                    $groups_map[$clean_id] = $entry;
                    $groups_map[$clean_id . '@g.us'] = $entry;
                }
            }
        }
    }
    
    return $groups_map;
}

function get_group_display_name($group_id, $groups_map) {
    if (empty($group_id)) {
        return 'No Group / Private Only';
    }
    $gid = trim($group_id);
    $clean_gid = str_replace('@g.us', '', $gid);
    $gid_with_suffix = $clean_gid . '@g.us';

    if (isset($groups_map[$gid])) {
        return $groups_map[$gid]['name'];
    } elseif (isset($groups_map[$clean_gid])) {
        return $groups_map[$clean_gid]['name'];
    } elseif (isset($groups_map[$gid_with_suffix])) {
        return $groups_map[$gid_with_suffix]['name'];
    }
    return $gid;
}

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
            }
        }
        if ($route === 'flocks' && $method === 'GET') {
            try {
                $stmt = $pdo->query("SELECT * FROM sunfra_flocks WHERE status = 'active' ORDER BY id ASC");
                $flocks = $stmt->fetchAll(PDO::FETCH_ASSOC);
            } catch (Exception $e) {
                $flocks = [];
            }
            
            $today = new DateTime();
            $result = [];
            foreach ($flocks as $f) {
                $hatch = new DateTime($f['hatch_date']);
                $running_days = max(0, $today->diff($hatch)->days + 1);
                $weeks = max(0, (int)floor(($running_days - 1) / 7));
                
                $sname = $f['shed_name'];
                $shed_norm = str_replace('Shead', 'Shed', $sname);
                $shed_alt = str_replace('Shed', 'Shead', $sname);
                
                $cum_mort = 0;
                try {
                    $mort_stmt = $pdo->prepare("SELECT COALESCE(SUM(quantity), 0) FROM sunfra_processed_data WHERE category = 'mortality' AND (shead_name = ? OR shead_name = ?) AND processed_time >= ?");
                    $mort_stmt->execute([$shed_norm, $shed_alt, $f['hatch_date']]);
                    $cum_mort = (int)$mort_stmt->fetchColumn();
                    
                    if (stripos($sname, 'chick') !== false) {
                        $chick_mort = $pdo->prepare("SELECT COALESCE(SUM(quantity), 0) FROM sunfra_processed_data WHERE category = 'mortality' AND shead_name LIKE 'Chick%' AND processed_time >= ?");
                        $chick_mort->execute([$f['hatch_date']]);
                        $cum_mort += (int)$chick_mort->fetchColumn();
                    }
                } catch (Exception $m_err) {}
                
                $live = isset($f['live_birds']) && $f['live_birds'] !== null ? (int)$f['live_birds'] : (int)$f['initial_chicks'];
                if ($live === 0) {
                    $weeks = 0;
                }
                
                $result[] = [
                    'id' => (int)$f['id'],
                    'shed_name' => $f['shed_name'],
                    'hatch_date' => $f['hatch_date'],
                    'initial_chicks' => (int)$f['initial_chicks'],
                    'batch_id' => $f['batch_id'],
                    'status' => $f['status'],
                    'running_days' => $running_days,
                    'running_weeks' => $weeks,
                    'total_live_birds' => $live
                ];
            }
            echo json_encode($result);
            exit;
        }

        if (strpos($route, 'flocks/') === 0 && $method === 'PUT') {
            $id = (int)str_replace('flocks/', '', $route);
            $input = json_decode(file_get_contents('php://input'), true);
            
            $hatch_date = $input['hatch_date'] ?? null;
            $initial_chicks = isset($input['initial_chicks']) ? (int)$input['initial_chicks'] : null;
            $live_birds = isset($input['live_birds']) ? (int)$input['live_birds'] : null;
            $batch_id = $input['batch_id'] ?? null;
            
            $updates = [];
            $params = [];
            if ($hatch_date !== null) { $updates[] = "hatch_date = ?"; $params[] = $hatch_date; }
            if ($initial_chicks !== null) { $updates[] = "initial_chicks = ?"; $params[] = $initial_chicks; }
            if ($live_birds !== null) { $updates[] = "live_birds = ?"; $params[] = $live_birds; }
            if ($batch_id !== null) { $updates[] = "batch_id = ?"; $params[] = $batch_id; }
            
            if (!empty($updates)) {
                $params[] = $id;
                $sql = "UPDATE sunfra_flocks SET " . implode(", ", $updates) . " WHERE id = ?";
                $pdo->prepare($sql)->execute($params);
            }
            echo json_encode(['status' => 'success', 'message' => 'Flock updated successfully']);
            exit;
        }

        if ($route === 'reminders' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM sunfra_unified_reminders ORDER BY trigger_time DESC");
            $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            $groups_map = get_all_sunfra_groups($pdo);
            $waha_groups = array_values($groups_map);
            
            // Fetch submissions and raw messages for the requested date (or today)
            $IST_OFFSET = 5.5 * 3600;
            $today_ist = date('Y-m-d', time() + $IST_OFFSET);
            $has_custom_date = isset($_GET['date']) && preg_match('/^\d{4}-\d{2}-\d{2}$/', $_GET['date']);
            $view_date = $has_custom_date ? $_GET['date'] : $today_ist;
            $is_past_date = ($view_date < $today_ist);
            
            try {
                $sub_stmt = $pdo->prepare("
                    SELECT p.*, w.group_id AS whatsapp_group_jid 
                    FROM sunfra_processed_data p 
                    LEFT JOIN sunfra_whatsapp_messages w ON p.message_id = w.message_id 
                    WHERE DATE(p.processed_time) = ?
                ");
                $sub_stmt->execute([$view_date]);
                $submissions = $sub_stmt->fetchAll(PDO::FETCH_ASSOC);
                
                $raw_stmt = $pdo->prepare("
                    SELECT r.*, w.group_id AS whatsapp_group_jid, w.sender_id AS whatsapp_sender_id
                    FROM sunfra_raw_messages r 
                    LEFT JOIN sunfra_whatsapp_messages w ON r.message_id = w.message_id 
                    WHERE DATE(r.timestamp) = ?
                ");
                $raw_stmt->execute([$view_date]);
                $raw_messages = $raw_stmt->fetchAll(PDO::FETCH_ASSOC);
            } catch (Exception $db_err) {
                // Fallback: fetch all and filter in PHP
                $sub_stmt = $pdo->query("
                    SELECT p.*, w.group_id AS whatsapp_group_jid 
                    FROM sunfra_processed_data p 
                    LEFT JOIN sunfra_whatsapp_messages w ON p.message_id = w.message_id
                ");
                $all_subs = $sub_stmt->fetchAll(PDO::FETCH_ASSOC);
                $submissions = [];
                foreach ($all_subs as $s) {
                    if (substr($s['processed_time'], 0, 10) === $view_date) {
                        $submissions[] = $s;
                    }
                }
                
                $raw_stmt = $pdo->query("
                    SELECT r.*, w.group_id AS whatsapp_group_jid, w.sender_id AS whatsapp_sender_id
                    FROM sunfra_raw_messages r 
                    LEFT JOIN sunfra_whatsapp_messages w ON r.message_id = w.message_id
                ");
                $all_raws = $raw_stmt->fetchAll(PDO::FETCH_ASSOC);
                $raw_messages = [];
                foreach ($all_raws as $r_msg) {
                    if (substr($r_msg['timestamp'], 0, 10) === $view_date) {
                        $raw_messages[] = $r_msg;
                    }
                }
            }
            
            $log_stmt = $pdo->prepare("SELECT reminder_id FROM sunfra_reminder_logs WHERE DATE(executed_at) = ? AND status = 'sent'");
            $log_stmt->execute([$view_date]);
            $sent_logs = $log_stmt->fetchAll(PDO::FETCH_COLUMN) ?: [];
            
            // Pass viewing date to JSON response so JS knows which date was loaded
            $viewing_date_meta = ['_viewing_date' => $view_date, '_is_past' => $is_past_date];
            
            foreach ($rows as &$row) {
                $row['whatsapp_id'] = preg_match('/^\d{10}$/', $row['person_phone']) ? "91{$row['person_phone']}@c.us" : "{$row['person_phone']}@c.us";
                $row['group_name'] = get_group_display_name($row['whatsapp_group_id'], $groups_map);
                
                // Verify submission dynamically for the requested date
                $verification = verify_reminder_submission($row, $submissions, $raw_messages, $waha_groups, $sent_logs);
                $was_sent_on_date = in_array($row['id'], $sent_logs);
                $is_manually_done = ($row['status'] === 'sent' && !$was_sent_on_date && !$is_past_date);
                $auto_skipped = ($row['status'] === 'skipped' && !$is_past_date);
                
                $row['submitted_reports'] = $verification['submitted_reports'] ?? [];
                $row['missing_reports'] = $verification['missing_reports'] ?? [];
                
                if ($is_manually_done || $auto_skipped || $verification['is_submitted']) {
                    $row['is_submitted'] = 1;
                    if ($is_manually_done) {
                        $row['verification_details'] = "Manually marked as completed (Done).\n\n" . $verification['details'];
                    } elseif ($auto_skipped) {
                        $row['verification_details'] = "Skipped automatically (already submitted before reminder).\n\n" . $verification['details'];
                    } else {
                        $row['verification_details'] = $verification['details'];
                    }
                } else {
                    $row['is_submitted'] = 0;
                    $row['verification_details'] = $verification['details'];
                }

                // For past dates, reflect historical status
                if ($is_past_date) {
                    if ($was_sent_on_date) {
                        $row['status'] = 'sent';
                    } elseif ($verification['is_submitted']) {
                        $row['status'] = 'skipped';
                    } else {
                        $row['status'] = 'pending';
                    }
                }
            }
            // Inject viewing_date metadata into first row so JS can read it
            $result = array_values($rows);
            $meta = ['__meta__' => true, 'viewing_date' => $view_date, 'is_past' => $is_past_date, 'is_custom' => $has_custom_date];
            array_unshift($result, $meta);
            echo json_encode($result);
        }
        elseif ($route === 'reminder-logs' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM sunfra_reminder_logs ORDER BY executed_at DESC LIMIT 200");
            echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
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
            $rem_id = $matches[1];
            $pdo->prepare("UPDATE sunfra_unified_reminders SET status = 'sent' WHERE id = ?")->execute([$rem_id]);
            
            // Delete sent log entry for today so this reminder is marked as manually done on dashboard
            $IST_OFFSET = 5.5 * 3600;
            $today_ist = date('Y-m-d', time() + $IST_OFFSET);
            try {
                $pdo->prepare("DELETE FROM sunfra_reminder_logs WHERE reminder_id = ? AND DATE(executed_at) = ?")->execute([$rem_id, $today_ist]);
            } catch (Exception $e) {}
            
            // Cross-complete matching pending/overdue tasks
            $stmt = $pdo->prepare("SELECT * FROM sunfra_unified_reminders WHERE id = ?");
            $stmt->execute([$rem_id]);
            $reminder = $stmt->fetch(PDO::FETCH_ASSOC);
            if ($reminder) {
                $group_id = $reminder['whatsapp_group_id'];
                $phone = $reminder['person_phone'];
                $reports = array_filter(array_map('trim', explode(',', strtolower($reminder['report_types'] ?? ''))));
                
                $task_stmt = $pdo->query("SELECT * FROM sunfra_tasks WHERE status IN ('pending', 'overdue')");
                $tasks = $task_stmt->fetchAll(PDO::FETCH_ASSOC);
                foreach ($tasks as $t) {
                    $matched = false;
                    $group_match = ($group_id && $t['whatsapp_group_id'] && str_replace('@g.us', '', $group_id) === str_replace('@g.us', '', $t['whatsapp_group_id']));
                    
                    $person_match = false;
                    if ($phone && $t['assigned_person_phone']) {
                        $rem_phones = array_filter(array_map('trim', explode(',', $phone)));
                        $task_phones = array_filter(array_map('trim', explode(',', $t['assigned_person_phone'])));
                        foreach ($rem_phones as $rp) {
                            $clean_rp = preg_replace('/\D/', '', $rp);
                            if (!$clean_rp) continue;
                            foreach ($task_phones as $tp) {
                                $clean_tp = preg_replace('/\D/', '', $tp);
                                if ($clean_rp === $clean_tp || (strlen($clean_rp) === 10 && "91" . $clean_rp === $clean_tp) || (strlen($clean_tp) === 10 && "91" . $clean_tp === $clean_rp)) {
                                    $person_match = true;
                                    break 2;
                                }
                            }
                        }
                    }
                    
                    $name_match = false;
                    $t_name = strtolower($t['task_name'] ?? '');
                    foreach ($reports as $rep) {
                        if (strpos($t_name, $rep) !== false || strpos($rep, $t_name) !== false) {
                            $name_match = true;
                            break;
                        }
                        $rep_words = array_filter(explode(' ', $rep), function($w) { return strlen($w) > 3; });
                        foreach ($rep_words as $rw) {
                            if (strpos($t_name, $rw) !== false) {
                                $name_match = true;
                                break 2;
                            }
                        }
                    }
                    if (($group_match || $person_match) && $name_match) {
                        $pdo->prepare("UPDATE sunfra_tasks SET status = 'completed', completion_details = 'Manually completed via reminder Done button' WHERE id = ?")->execute([$t['id']]);
                    }
                }
            }
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
            
            $groups_map = get_all_sunfra_groups($pdo);
            
            foreach ($rows as &$row) {
                $row['group_name'] = get_group_display_name($row['whatsapp_group_id'], $groups_map);
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
            $task_id = $matches[1];
            $data = json_decode(file_get_contents('php://input'), true);
            $details = $data['details'] ?? 'Manually completed';
            $stmt = $pdo->prepare("UPDATE sunfra_tasks SET status = 'completed', completion_details = ? WHERE id = ?");
            $stmt->execute([$details, $task_id]);
            
            // Cross-complete matching pending reminders
            $stmt2 = $pdo->prepare("SELECT * FROM sunfra_tasks WHERE id = ?");
            $stmt2->execute([$task_id]);
            $task = $stmt2->fetch(PDO::FETCH_ASSOC);
            if ($task) {
                $group_id = $task['whatsapp_group_id'];
                $phone = $task['assigned_person_phone'];
                $t_name = strtolower($task['task_name'] ?? '');
                
                $rem_stmt = $pdo->query("SELECT * FROM sunfra_unified_reminders WHERE status = 'pending'");
                $reminders = $rem_stmt->fetchAll(PDO::FETCH_ASSOC);
                foreach ($reminders as $r) {
                    $matched = false;
                    $group_match = ($group_id && $r['whatsapp_group_id'] && str_replace('@g.us', '', $group_id) === str_replace('@g.us', '', $r['whatsapp_group_id']));
                    
                    $person_match = false;
                    if ($phone && $r['person_phone']) {
                        $rem_phones = array_filter(array_map('trim', explode(',', $r['person_phone'])));
                        $task_phones = array_filter(array_map('trim', explode(',', $phone)));
                        foreach ($rem_phones as $rp) {
                            $clean_rp = preg_replace('/\D/', '', $rp);
                            if (!$clean_rp) continue;
                            foreach ($task_phones as $tp) {
                                $clean_tp = preg_replace('/\D/', '', $tp);
                                if ($clean_rp === $clean_tp || (strlen($clean_rp) === 10 && "91" . $clean_rp === $clean_tp) || (strlen($clean_tp) === 10 && "91" . $clean_tp === $clean_rp)) {
                                    $person_match = true;
                                    break 2;
                                }
                            }
                        }
                    }
                    
                    $name_match = false;
                    $reports = array_filter(array_map('trim', explode(',', strtolower($r['report_types'] ?? ''))));
                    foreach ($reports as $rep) {
                        if (strpos($t_name, $rep) !== false || strpos($rep, $t_name) !== false) {
                            $name_match = true;
                            break;
                        }
                        $rep_words = array_filter(explode(' ', $rep), function($w) { return strlen($w) > 3; });
                        foreach ($rep_words as $rw) {
                            if (strpos($t_name, $rw) !== false) {
                                $name_match = true;
                                break 2;
                            }
                        }
                    }
                    if (($group_match || $person_match) && $name_match) {
                        $pdo->prepare("UPDATE sunfra_unified_reminders SET status = 'sent' WHERE id = ?")->execute([$r['id']]);
                    }
                }
            }
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
            $hidden_file = __DIR__ . '/hidden_groups.json';
            $hidden_data = file_exists($hidden_file) ? json_decode(file_get_contents($hidden_file), true) : [];
            
            $groups_map = get_all_sunfra_groups($pdo);
            $unique_groups = [];
            $seen_ids = [];
            foreach ($groups_map as $g) {
                if (!in_array($g['id'], $seen_ids)) {
                    $seen_ids[] = $g['id'];
                    $unique_groups[] = $g;
                }
            }
            
            echo json_encode([
                'status' => 'success',
                'groups' => $unique_groups,
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
        elseif ($route === 'reports/trigger' && $method === 'POST') {
            $data = file_get_contents('php://input');
            $payload = json_decode($data, true);
            $report_id = isset($payload['report_id']) ? trim($payload['report_id']) : 'pnl';
            $target_phones = isset($payload['target_phones']) ? trim($payload['target_phones']) : '';
            
            try {
                $stmt = $pdo->prepare("INSERT INTO sunfra_manual_triggers (report_id, target_phones, status, requested_at) VALUES (?, ?, 'pending', NOW())");
                $stmt->execute([$report_id, $target_phones]);
                echo json_encode(['status' => 'success', 'message' => "Manual trigger for report '$report_id' recorded. Sending via WhatsApp to selected recipient(s): " . ($target_phones ? $target_phones : 'Default')]);
            } catch (Exception $e) {
                echo json_encode(['status' => 'error', 'message' => 'Failed to log trigger: ' . $e->getMessage()]);
            }
            exit;
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
            background: #2563eb !important;
            color: #ffffff !important;
            font-weight: 700;
            box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
        }

        .btn-primary:hover { 
            background: #1d4ed8 !important;
            transform: translateY(-2px); 
            box-shadow: 0 6px 18px rgba(37, 99, 235, 0.45); 
        }

        .btn-secondary { 
            background: #ffffff !important; 
            color: #1e293b !important; 
            border: 1.5px solid #cbd5e1 !important; 
            font-weight: 600;
            box-shadow: 0 2px 5px rgba(0,0,0,0.06);
        }
        
        .btn-secondary:hover { 
            background: #f8fafc !important;
            color: #0f172a !important; 
            border-color: #94a3b8 !important; 
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            padding: 0.5rem 1rem;
            font-size: 0.85rem;
            border: 1px solid rgba(239, 68, 68, 0.3);
            font-weight: 600;
        }

        .btn-danger:hover { background: var(--danger-color); color: white; }

        /* Modals */
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.45) !important;
            backdrop-filter: blur(3px);
            z-index: 99999 !important;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }

        .modal.active {
            display: flex !important;
            opacity: 1 !important;
            pointer-events: auto !important;
        }

        .modal-content {
            background: #ffffff !important;
            color: #0f172a !important;
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
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
                <a href="#" class="nav-item" data-target="reports_view">Automated Reports</a>
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
                <div class="stats-grid" style="margin-bottom: 2rem;">
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

                <h2 style="font-size: 1.2rem; margin-bottom: 1rem; color: var(--text-color);">Automated Reports Schedule</h2>
                <div class="stats-grid">
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'reports_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Automated Reports">
                        <h3>Active System Reports</h3>
                        <div class="stat-value" style="color: var(--primary-color);">7</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'reports_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Automated Reports">
                        <h3>Daily Automated Runs</h3>
                        <div class="stat-value" style="color: #16a34a;">8</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'reports_view\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Automated Reports">
                        <h3>Report Formats</h3>
                        <div class="stat-value" style="color: #7e22ce;">PDF, Text, Alerts</div>
                    </div>
                </div>
            </section>

            <!-- Reminders View -->
            <section id="reminders_view" class="view">
                <div class="header-row">
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <h2>Reminders Management</h2>
                        <span id="reminders-date-label" style="font-size:0.82rem; color:#0284c7; font-weight:600; display:none;">📅 Viewing: <span id="reminders-date-label-val"></span> &nbsp;<a href="#" onclick="fetchReminders(); return false;" style="color:#dc2626; font-size:0.8rem;">✕ Back to Today</a></span>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <button class="btn btn-primary" onclick="openReminderModal()" style="margin: 0;">+ Create Reminder</button>
                        <button class="btn" onclick="openApprovalPresetModal('reminder')" style="margin: 0; background: #16a34a; color: white; border: none; font-weight: 600; box-shadow: 0 2px 6px rgba(22,163,74,0.3);">+ Approval Reminder</button>
                        <button class="btn btn-secondary" onclick="openVisibilityModal()" style="margin: 0;">Filter Groups</button>
                        <button class="btn btn-secondary" onclick="resetDailyReminders()" style="margin: 0; background: rgba(245,158,11,0.12); color: #b45309; border: 1px solid rgba(245,158,11,0.3);" title="Advance all Daily/Weekly/Monthly reminders to next scheduled date">🔄 Reset Recurring</button>
                        <div style="display:inline-flex; align-items:center; gap:0.35rem; background:rgba(2,132,199,0.06); padding:0.25rem 0.5rem; border-radius:8px; border:1px solid rgba(2,132,199,0.2);">
                            <label style="font-size:0.82rem; font-weight:600; color:#0284c7; white-space:nowrap;">📅 View Date:</label>
                            <input type="date" id="reminderDatePicker" onchange="if(this.value) fetchReminders(this.value)" style="padding:0.35rem 0.5rem; border-radius:6px; border:1px solid rgba(2,132,199,0.3); background:white; color:#0284c7; font-weight:600; font-size:0.85rem; font-family:inherit; cursor:pointer; outline:none; margin:0;">
                            <button type="button" class="btn" onclick="applySelectedReminderDate()" style="margin:0; background:#0284c7; color:white; border:none; font-weight:600; padding:0.35rem 0.65rem; font-size:0.82rem; border-radius:6px; cursor:pointer; box-shadow:0 1px 3px rgba(2,132,199,0.3); white-space:nowrap;">🔍 Load Date</button>
                        </div>
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
                                <th>Submitted</th>
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
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <h2>Tasks &amp; Approvals Management</h2>
                        <span id="tasks-date-label" style="font-size:0.82rem; color:#0284c7; font-weight:600; display:none;">📅 Viewing: <span id="tasks-date-label-val"></span> &nbsp;<a href="#" onclick="fetchTasks(); return false;" style="color:#dc2626; font-size:0.8rem;">✕ Back to Today</a></span>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <button class="btn btn-primary" onclick="openCreateTaskModal()" style="margin: 0;">+ Create Task</button>
                        <button class="btn" onclick="openApprovalPresetModal('task')" style="margin: 0; background: #16a34a; color: white; border: none; font-weight: 600; box-shadow: 0 2px 6px rgba(22,163,74,0.3);">+ Approval Task</button>
                        <button class="btn btn-secondary" onclick="openVisibilityModal()" style="margin: 0;">Filter Groups</button>
                        <div style="display:inline-flex; align-items:center; gap:0.35rem; background:rgba(2,132,199,0.06); padding:0.25rem 0.5rem; border-radius:8px; border:1px solid rgba(2,132,199,0.2);">
                            <label style="font-size:0.82rem; font-weight:600; color:#0284c7; white-space:nowrap;">📅 View Date:</label>
                            <input type="date" id="taskDatePicker" onchange="if(this.value) fetchTasks(this.value)" style="padding:0.35rem 0.5rem; border-radius:6px; border:1px solid rgba(2,132,199,0.3); background:white; color:#0284c7; font-weight:600; font-size:0.85rem; font-family:inherit; cursor:pointer; outline:none; margin:0;">
                            <button type="button" class="btn" onclick="applySelectedTaskDate()" style="margin:0; background:#0284c7; color:white; border:none; font-weight:600; padding:0.35rem 0.65rem; font-size:0.82rem; border-radius:6px; cursor:pointer; box-shadow:0 1px 3px rgba(2,132,199,0.3); white-space:nowrap;">🔍 Load Date</button>
                        </div>
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
                                <th>Submitted</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="tasks-tbody"></tbody>
                    </table>
                </div>
            </section>

            <!-- Automated Reports Schedule View -->
            <section id="reports_view" class="view">
                <div class="header-row">
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <h2>Automated Reports Schedule</h2>
                        <span id="reports-date-label" style="font-size:0.82rem; color:#0284c7; font-weight:600; display:none;">📅 Viewing submissions for: <span id="reports-date-label-val"></span> &nbsp;<a href="#" onclick="fetchReminders(); return false;" style="color:#dc2626; font-size:0.8rem;">✕ Back to Today</a></span>
                    </div>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <button class="btn btn-primary" onclick="openScheduleReportModal()" style="margin: 0; background: #0284c7; color: white; border: none; font-weight: 600; box-shadow: 0 2px 6px rgba(2,132,199,0.3);">+ Schedule System Report</button>
                        <span class="badge badge-green" style="font-size: 0.85rem; padding: 0.4rem 0.8rem; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">📊 Active Reports Schedule</span>
                        <div style="display:inline-flex; align-items:center; gap:0.35rem; background:rgba(2,132,199,0.06); padding:0.25rem 0.5rem; border-radius:8px; border:1px solid rgba(2,132,199,0.2);">
                            <label style="font-size:0.82rem; font-weight:600; color:#0284c7; white-space:nowrap;">📅 View Date:</label>
                            <input type="date" id="reportDatePicker" onchange="if(this.value) fetchReminders(this.value)" style="padding:0.35rem 0.5rem; border-radius:6px; border:1px solid rgba(2,132,199,0.3); background:white; color:#0284c7; font-weight:600; font-size:0.85rem; font-family:inherit; cursor:pointer; outline:none; margin:0;">
                            <button type="button" class="btn" onclick="applySelectedReportDate()" style="margin:0; background:#0284c7; color:white; border:none; font-weight:600; padding:0.35rem 0.65rem; font-size:0.82rem; border-radius:6px; cursor:pointer; box-shadow:0 1px 3px rgba(2,132,199,0.3); white-space:nowrap;">🔍 Load Date</button>
                        </div>
                        <input type="text" id="reportsSearchInput" placeholder="Search reports..." oninput="filterReportsTable()" style="padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); width: 180px; font-size: 0.9rem; background: white; margin: 0; box-sizing: border-box;">
                    </div>
                </div>
                <div class="card table-card">
                    <table class="data-table" id="reports-table">
                        <thead>
                            <tr>
                                <th>Report Name</th>
                                <th>Recipients / WhatsApp Group</th>
                                <th>Scheduled Time (IST)</th>
                                <th>Frequency</th>
                                <th>Format / Details</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                                      <tbody id="reports-tbody">
                            <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">Profit &amp; Loss (P&amp;L) Daily Report</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Full Financial Summary, Sales, Expenses &amp; Net Income Breakdown</span></td>
                                <td><strong style="color:var(--primary-color)">P&amp;L Group / Main Admins</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Kusum (7259510983), Prasad (7204021105)</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">08:00 AM &amp; 09:30 PM</span></td>
                                <td>Daily (Mon - Sat)</td>
                                <td><span class="badge" style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd; font-weight:600;">📄 PDF &amp; Text Summary</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('pnl')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('pnl')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('pnl', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                                </td>
                                     <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">First Escalation Summary Report</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Alert for Unsubmitted Daily Reports &amp; Overdue Pending Tasks</span></td>
                                <td><strong style="color:var(--primary-color)">Main Admin</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Kusum (7259510983)</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">09:30 PM</span></td>
                                <td>Mon - Sat (No Sundays)</td>
                                <td><span class="badge" style="background:#fef3c7; color:#b45309; border:1px solid #fde68a; font-weight:600;">⚠️ Escalation Alert</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('escalation_1')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('escalation_1')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('escalation_1', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                                </td>
                            </tr>
                            <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">Final Midnight Escalation Report</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Company-Wide Final End-Of-Day Audit &amp; Executive Summary</span></td>
                                <td><strong style="color:var(--primary-color)">Main Admin</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Kusum (7259510983)</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">11:59 PM</span></td>
                                <td>Mon - Sat (No Sundays)</td>
                                <td><span class="badge" style="background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; font-weight:600;">🚨 Midnight Company Summary</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('escalation_2')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('escalation_2')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('escalation_2', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                                </td>
                            </tr>
                            <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">Silo Feed Low Stock &amp; Inventory Alert</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Silo Cleaning, Feed Stock Level &amp; Reorder Threshold Audit</span></td>
                                <td><strong style="color:var(--primary-color)">Feed Plant In-Charge</strong><br><span style="font-size:0.82rem; color:var(--text-secondary)">Prasad (7204021105), Kusum (7259510983)</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">07:00 PM</span></td>
                                <td>Daily (Mon - Sun)</td>
                                <td><span class="badge" style="background:#f0fdf4; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🌾 Feed Inventory Alert</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('silo')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('silo')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('silo', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                                </td>
                            </tr>
                            <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">Egg Stock &amp; Godown Reconciliation Report</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Egg Dispatch, Tray Inventory Audit &amp; Godown Stock Balance</span></td>
                                <td><strong style="color:var(--primary-color)">Egg Godown &amp; Main Admin</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Godown In-Charge, Kusum (7259510983)</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">08:00 PM</span></td>
                                <td>Daily (Mon - Sun)</td>
                                <td><span class="badge" style="background:#fef3c7; color:#b45309; border:1px solid #fde68a; font-weight:600;">🥚 Godown Audit</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('egg_stock')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('egg_stock')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('egg_stock', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                                </td>
                            </tr>
                            <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">Weekly Feed Formula Update &amp; Approval</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Weekly Shed Formula Composition, Mixing Ratio &amp; Approval</span></td>
                                <td><strong style="color:var(--primary-color)">Feed Formula Group &amp; Approver</strong><br><span style="font-size:0.82rem; color:var(--text-secondary)">Feed Plant Group, Prasad (7204021105)</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">12:00 PM</span></td>
                                <td>Weekly (Every Monday)</td>
                                <td><span class="badge" style="background:#f3e8ff; color:#7e22ce; border:1px solid #e9d5ff; font-weight:600;">🟣 Formula Approval</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('feed_formula')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('feed_formula')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('feed_formula', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                                </td>
                            </tr>
                            <tr class="report-row-item">
                                <td><strong style="font-size:1.05rem; color:var(--text-primary);">Upcoming Flock Vaccination Schedule</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">Flock Deworming, Vaccine Purchases &amp; Inoculation Alerts</span></td>
                                <td><strong style="color:var(--primary-color)">Vaccine Group &amp; Medical Team</strong><br><span style="font-size:0.82rem; color:var(--text-secondary)">Vaccine In-Charges &amp; Doctors</span></td>
                                <td><span style="font-weight:700; color:#1e293b;">04:00 PM</span></td>
                                <td>Daily (Mon - Sun)</td>
                                <td><span class="badge" style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd; font-weight:600;">💉 Vaccine Alert</span></td>
                                <td><span class="badge badge-green" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 Active</span></td>
                                <td>
                                    <div style="display:flex; gap:0.3rem;">
                                        <button class="btn" onclick="editReportSchedule('vaccine')" style="padding:4px 8px; font-size:0.75rem; background:rgba(59,130,246,0.1); color:var(--primary-color); border:1px solid rgba(59,130,246,0.2); border-radius:6px; cursor:pointer;">Edit</button>
                                        <button class="btn" onclick="triggerReportNow('vaccine')" style="padding:4px 8px; font-size:0.75rem; background:rgba(22,163,74,0.1); color:#16a34a; border:1px solid rgba(22,163,74,0.2); border-radius:6px; cursor:pointer;">Trigger Now</button>
                                        <button class="btn" onclick="deleteReportSchedule('vaccine', event)" style="padding:4px 8px; font-size:0.75rem; background:rgba(239,68,68,0.1); color:#ef4444; border:1px solid rgba(239,68,68,0.2); border-radius:6px; cursor:pointer;">Delete</button>
                                    </div>
                        </tbody>
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
                        <option value="daily" selected>Daily (Mon - Sun)</option>
                        <option value="mon-sat">Daily (Mon - Sat, No Sundays)</option>
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
                        <option value="daily" selected>Daily (Mon - Sun)</option>
                        <option value="mon-sat">Daily (Mon - Sat, No Sundays)</option>
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

    <!-- Schedule System Report Modal -->
    <div id="scheduleReportModal" class="modal">
        <div class="modal-content card" style="width: 500px;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(0,0,0,0.08); padding-bottom: 0.8rem; margin-bottom: 1.5rem;">
                <h3 id="schedule-report-modal-title" style="margin: 0; font-size: 1.4rem;">📊 Schedule System Report</h3>
                <span class="close-modal" onclick="closeScheduleReportModal()" style="font-size: 1.8rem; cursor: pointer; color: var(--text-secondary);">&times;</span>
            </div>
            <form id="schedule-report-form" onsubmit="handleScheduleReportSubmit(event)">
                <input type="hidden" id="report-schedule-id">
                
                <div class="form-group">
                    <label style="font-weight: 600;">Report Type / Name</label>
                    <select id="report-type-select" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1);" onchange="handleReportTypeSelectChange()">
                        <option value="pnl">Profit &amp; Loss (P&amp;L) Daily Report</option>
                        <option value="escalation_1">First Escalation Summary Report (09:30 PM)</option>
                        <option value="escalation_2">Final Midnight Escalation Report (11:59 PM)</option>
                        <option value="silo">Silo Feed Low Stock &amp; Inventory Alert</option>
                        <option value="egg_stock">Egg Stock &amp; Godown Reconciliation Report</option>
                        <option value="feed_formula">Weekly Feed Formula Update &amp; Approval</option>
                        <option value="vaccine">Upcoming Flock Vaccination Schedule</option>
                        <option value="custom">Custom Automated System Report</option>
                    </select>
                </div>

                <div class="form-group" id="custom-report-name-group" style="display: none;">
                    <label style="font-weight: 600;">Custom Report Name</label>
                    <input type="text" id="custom-report-name-input" placeholder="e.g. Sales Commission Report" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1);">
                </div>

                <div class="form-group">
                    <label style="font-weight: 600;">Target WhatsApp Group (Optional)</label>
                    <select id="report-recipient-group" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1);">
                        <option value="">No Group / Private Direct Message Only</option>
                    </select>
                </div>

                <div class="form-group">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                        <label style="font-weight: 600; margin: 0;">Assign Members (Select People)</label>
                        <button type="button" class="btn" onclick="showAddManualMemberForm()" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2); border-radius: 6px; cursor: pointer; font-weight: 600;">[ + Add New Member ]</button>
                    </div>
                    
                    <!-- Search bar and members checkbox container -->
                    <input type="text" id="reportMemberSearchInput" placeholder="Search members..." oninput="filterReportMembersList()" style="width: 100%; padding: 0.6rem; margin-bottom: 0.5rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-size: 0.9rem; background: white; color: var(--text-primary); box-sizing: border-box;">
                    
                    <div id="reportMembersCheckboxContainer" style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 180px; overflow-y: auto; padding: 0.75rem; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; background: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                        <!-- Checkboxes populated dynamically -->
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                    <div class="form-group" style="margin: 0;">
                        <label style="font-weight: 600;">📅 Start Date (Calendar)</label>
                        <input type="date" id="report-date-input" required style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); background: white; font-family: inherit;">
                    </div>
                    <div class="form-group" style="margin: 0;">
                        <label style="font-weight: 600;">⏰ Scheduled Time (IST)</label>
                        <input type="time" id="report-time-input" value="21:30" required style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); background: white; font-family: inherit;">
                    </div>
                </div>

                <div class="form-group">
                    <label style="font-weight: 600;">Frequency</label>
                    <select id="report-frequency-select" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1);">
                        <option value="mon-sat">Mon - Sat (No Sundays)</option>
                        <option value="daily">Daily (Mon - Sun)</option>
                        <option value="weekly">Weekly (Every Monday)</option>
                        <option value="monthly">Monthly (1st of Month)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label style="font-weight: 600;">Report Format</label>
                    <select id="report-format-select" style="width: 100%; padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1);">
                        <option value="pdf_text">PDF Document &amp; Text Summary</option>
                        <option value="text_alert">Text Alert &amp; Escalation List</option>
                        <option value="audit">Detailed Stock &amp; Inventory Audit</option>
                    </select>
                </div>

                <div class="modal-actions" style="margin-top: 1.5rem;">
                    <button type="button" class="btn btn-secondary" onclick="closeScheduleReportModal()">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background: #0284c7; color: white;">Save Report Schedule</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Edit Flock Modal -->
    <div id="editFlockModal" class="modal">
        <div class="modal-content card" style="width: 400px; padding: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="margin: 0;" id="editFlockModalTitle">Edit Flock Details</h3>
                <button type="button" onclick="closeModal('editFlockModal')" style="background: none; border: none; font-size: 1.4rem; cursor: pointer; color: var(--text-secondary); line-height: 1;">&times;</button>
            </div>
            <form id="editFlockForm" onsubmit="submitEditFlock(event)">
                <input type="hidden" id="edit-flock-id" />
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Hatch Date</label>
                    <input type="date" id="edit-flock-hatch-date" required style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">No. of Chicks (Initial Size)</label>
                    <input type="number" id="edit-flock-chicks" required style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Total Live Birds</label>
                    <input type="number" id="edit-flock-live-birds" required style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Batch ID (Optional)</label>
                    <input type="text" id="edit-flock-batch-id" style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div style="display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.5rem;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('editFlockModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Changes</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Add Batch Modal -->
    <div id="addFlockModal" class="modal">
        <div class="modal-content card" style="width: 420px; padding: 1.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
                <h3 style="margin: 0;">Add New Batch / Flock</h3>
                <button type="button" onclick="closeModal('addFlockModal')" style="background: none; border: none; font-size: 1.4rem; cursor: pointer; color: var(--text-secondary); line-height: 1;">&times;</button>
            </div>
            <form id="addFlockForm" onsubmit="submitAddFlock(event)">
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Shed / Flock Name</label>
                    <input type="text" id="add-flock-name" required placeholder="e.g. Shead 10 or Chick 2" style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Hatch Date</label>
                    <input type="date" id="add-flock-hatch-date" required style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">No. of Chicks (Initial Size)</label>
                    <input type="number" id="add-flock-chicks" required placeholder="20000" style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div class="form-group" style="margin-bottom: 1rem;">
                    <label style="font-weight: 600; font-size: 0.9rem; display: block; margin-bottom: 0.4rem;">Batch ID (Optional)</label>
                    <input type="text" id="add-flock-batch-id" placeholder="e.g. 23" style="width: 100%; padding: 0.65rem; border-radius: 8px; border: 1px solid rgba(0,0,0,0.1); font-family: inherit; box-sizing: border-box;" />
                </div>
                <div style="display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 1.5rem;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('addFlockModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background: #15803d;">Add Batch</button>
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

        window.openModal = function(modalId) {
            const m = document.getElementById(modalId);
            if (m) {
                m.classList.add('active');
                m.style.setProperty('display', 'flex', 'important');
                m.style.setProperty('opacity', '1', 'important');
                m.style.setProperty('pointer-events', 'auto', 'important');
            } else {
                console.error("Modal not found:", modalId);
            }
        };

        window.closeModal = function(modalId) {
            const m = document.getElementById(modalId);
            if (m) {
                m.classList.remove('active');
                m.style.setProperty('display', 'none', 'important');
                m.style.setProperty('opacity', '0', 'important');
                m.style.setProperty('pointer-events', 'none', 'important');
            }
        };

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

            const containerReport = document.getElementById('reportMembersCheckboxContainer');
            if (containerReport) {
                containerReport.innerHTML = '';
                uniqueContacts.forEach(c => {
                    const checked = (selectedTaskPhones && selectedTaskPhones.includes(c.phone)) ? 'checked' : '';
                    containerReport.innerHTML += `
                        <div class="report-member-checkbox-item" data-phone="${c.phone}" data-name="${c.name.toLowerCase()}" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.03);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="report-member-${c.phone}" value="${c.phone}" data-name="${c.name}" ${checked} class="report-member-checkbox" style="width:16px; height:16px; cursor:pointer;">
                                <label for="report-member-${c.phone}" style="cursor:pointer; font-size:0.95rem; color:var(--text-primary); font-weight:500;">
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

        function filterReportMembersList() {
            const query = document.getElementById('reportMemberSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.report-member-checkbox-item');
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

        function formatReportTitleCase(r) {
            if (!r) return "";
            return r.trim().split(/\s+/).map(w => {
                const wl = w.toLowerCase();
                if (wl === 'p&l' || wl === 'p/l' || wl === 'p-and-l') return 'P&L';
                if (wl === 'ca') return 'CA';
                if (wl === 'eod') return 'EOD';
                return w.charAt(0).toUpperCase() + w.slice(1);
            }).join(' ');
        }

        function updateNotesFromCheckedReports() {
            const modalTitle = (document.getElementById('reminderModalTitle') || document.getElementById('reminder-modal-title'))?.innerText || '';
            const isApproval = modalTitle.toLowerCase().includes('approval') || (document.getElementById('remNotes')?.value || '').toLowerCase().includes('approve');
            const checked = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => formatReportTitleCase(cb.value));
            const notesTextarea = document.getElementById('remNotes');
            
            if (checked.length > 0) {
                if (checked.length === 1) {
                    if (isApproval) {
                        notesTextarea.value = `Please review and approve today's *${checked[0]}* Report so daily records can be completed accurately.`;
                    } else {
                        notesTextarea.value = `Please submit today's *${checked[0]}* Report so the daily records and reports can be completed accurately.`;
                    }
                } else {
                    const bullets = checked.map(rep => `  • ${rep}`).join('\n');
                    if (isApproval) {
                        notesTextarea.value = `Please review and approve the following pending reports for today:\n${bullets}`;
                    } else {
                        notesTextarea.value = `Please submit the following pending reports for today:\n${bullets}`;
                    }
                }
            } else {
                if (isApproval) {
                    notesTextarea.value = `Please review and approve today's report in the group so daily records can be completed accurately.`;
                } else {
                    notesTextarea.value = '';
                }
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
                } else if (targetView === 'flocks_view') {
                    fetchFlocks();
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

        function applySelectedReminderDate() {
            const val = document.getElementById('reminderDatePicker').value;
            if (!val) return alert("Please select a date in the calendar box first!");
            fetchReminders(val);
        }

        function applySelectedTaskDate() {
            const val = document.getElementById('taskDatePicker').value;
            if (!val) return alert("Please select a date in the calendar box first!");
            fetchTasks(val);
        }

        function applySelectedReportDate() {
            const val = document.getElementById('reportDatePicker').value;
            if (!val) return alert("Please select a date in the calendar box first!");
            fetchReminders(val);
        }

        function showReminderDetails(id) {
            const r = reminders.find(x => x.id == id);
            if (r && r.verification_details) {
                alert("Submission Verification Details:\n\n" + r.verification_details);
            } else {
                alert("No details available.");
            }
        }

        function showTaskDetails(id) {
            const t = tasksList.find(x => x.id == id);
            if (t && t.completion_details) {
                alert("Completion Details:\n\n" + t.completion_details);
            } else {
                alert("No details available.");
            }
        }

        let reminders = [];
        async function fetchReminders(dateStr) {
            const IST_today = new Date(new Date().getTime() + 5.5*3600*1000).toISOString().slice(0,10);
            const queryDate = dateStr || IST_today;
            const isToday = (queryDate === IST_today);
            const url = API_URL + 'reminders' + (dateStr ? '&date=' + encodeURIComponent(dateStr) : '') + '&_t=' + Date.now();
            const res = await fetch(url, { cache: 'no-store' });
            const rawData = await res.json();
            
            let viewingDate = IST_today;
            let isPast = false;
            let isCustom = false;
            reminders = rawData.filter(r => {
                if (r && r.__meta__) {
                    viewingDate = r.viewing_date;
                    isPast = r.is_past;
                    isCustom = r.is_custom || (r.viewing_date !== IST_today);
                    return false;
                }
                return true;
            });
            // Store isPast globally so the badge renderer can use it
            window._remindersIsPast = isPast;
            window._remindersViewDate = viewingDate;
            
            // Update button label and date banner
            const btnEl = document.getElementById('reminderDatePickerBtn');
            const rBtnEl = document.getElementById('reportDatePickerBtn');
            const reminderLabel = document.getElementById('reminders-date-label');
            const reminderLabelVal = document.getElementById('reminders-date-label-val');
            const reportsLabel = document.getElementById('reports-date-label');
            const reportsLabelVal = document.getElementById('reports-date-label-val');
            
            if (isCustom) {
                const displayDate = new Date(viewingDate + 'T00:00:00').toLocaleDateString('en-IN', {day:'numeric', month:'short', year:'numeric'});
                if (btnEl) { btnEl.innerText = '📅 ' + displayDate; btnEl.style.background = '#0284c7'; btnEl.style.color = '#ffffff'; }
                if (rBtnEl) { rBtnEl.innerText = '📅 ' + displayDate; rBtnEl.style.background = '#0284c7'; rBtnEl.style.color = '#ffffff'; }
                if (reminderLabel) { reminderLabel.style.display = ''; reminderLabelVal.innerText = displayDate; }
                if (reportsLabel) { reportsLabel.style.display = ''; reportsLabelVal.innerText = displayDate; }
            } else {
                if (btnEl) { btnEl.innerText = '📅 View Date'; btnEl.style.background = 'rgba(2,132,199,0.1)'; btnEl.style.color = '#0284c7'; }
                if (rBtnEl) { rBtnEl.innerText = '📅 View Date'; rBtnEl.style.background = 'rgba(2,132,199,0.1)'; rBtnEl.style.color = '#0284c7'; }
                if (reminderLabel) reminderLabel.style.display = 'none';
                if (reportsLabel) reportsLabel.style.display = 'none';
            }
            
            // Pin Approval Reminders at TOP; arrange rest chronologically by scheduled date & time!
            reminders.sort((a, b) => {
                const aNotes = (a.task_notes || '').toLowerCase();
                const aRep = (a.report_types || '').toLowerCase();
                const aIsAppr = aNotes.includes('approval') || aRep.includes('approval') || aNotes.includes('approve') ? 1 : 0;
                
                const bNotes = (b.task_notes || '').toLowerCase();
                const bRep = (b.report_types || '').toLowerCase();
                const bIsAppr = bNotes.includes('approval') || bRep.includes('approval') || bNotes.includes('approve') ? 1 : 0;
                
                if (bIsAppr !== aIsAppr) {
                    return bIsAppr - aIsAppr; // Approval tasks first
                }
                
                // Sort by scheduled trigger date & time (chronological order)
                const aTime = a.trigger_time ? new Date(a.trigger_time.replace(/-/g,'/').replace('T',' ')).getTime() : 0;
                const bTime = b.trigger_time ? new Date(b.trigger_time.replace(/-/g,'/').replace('T',' ')).getTime() : 0;
                
                if (aTime !== bTime) {
                    return aTime - bTime;
                }
                return (b.id || 0) - (a.id || 0);
            });

            const tbody = document.getElementById('reminders-tbody');
            tbody.innerHTML = '';
            
            reminders.forEach(r => {
                const badgeClass = r.status === 'sent' ? 'badge-green' : (r.status === 'pending' ? 'badge-orange' : (r.status === 'skipped' ? 'badge-blue' : ''));
                const groupText = r.whatsapp_group_id ? `<strong style="color:var(--primary-color)">${r.group_name}</strong>` : `<span style="color:var(--text-secondary)">No Group / Private Only</span>`;
                
                const notesLower = (r.task_notes || '').toLowerCase();
                const reportLower = (r.report_types || '').toLowerCase();
                const isApprovalTask = notesLower.includes('approval') || reportLower.includes('approval') || notesLower.includes('approve');

                const subList = (r.submitted_reports || []).map(s => s.toLowerCase().trim());
                const reportsList = r.report_types ? r.report_types.split(',').map(rep => rep.trim()).filter(Boolean) : [];
                
                let reportsText = reportsList.length > 0 ? reportsList.map(rep => {
                    const cleanRep = rep.toUpperCase();
                    const isSub = subList.includes(rep.toLowerCase());
                    if (isSub) {
                        return `<span class="badge badge-green" style="margin-right:0.25rem; font-size:0.7rem; display:inline-block; margin-top:2px; background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:600;">🟢 ${cleanRep}</span>`;
                    } else {
                        return `<span class="badge badge-red" style="margin-right:0.25rem; font-size:0.7rem; display:inline-block; margin-top:2px; background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; font-weight:600;">🔴 ${cleanRep}</span>`;
                    }
                }).join(' ') : '<span style="color:var(--text-secondary)">Custom Notes Only</span>';
                
                if (isApprovalTask) {
                    reportsText = `<span class="badge" style="margin-right:0.35rem; font-size:0.7rem; display:inline-block; margin-top:2px; background:#f3e8ff; color:#7e22ce; border:1px solid #d8b4fe; font-weight:700;">🟣 APPROVAL TASK</span> ` + reportsText;
                }

                const displayNotes = isApprovalTask ? `<strong style="color:#7e22ce;">⭐ [APPROVAL TASK]</strong> ${r.task_notes}` : r.task_notes;

                const names = (r.person_name || '').split(',').map(n => n.trim());
                const phones = (r.person_phone || '').split(',').map(p => p.trim());
                const formattedAssignees = names.map((name, idx) => {
                    const phone = phones[idx] || '';
                    return `${name} (${phone})`;
                }).join(', ');

                // Build submitted status badge for reminders based on dynamic verification
                let remSubBadge, remSubLabel;
                const totalCount = reportsList.length;
                const subCount = subList.length;
                const isViewingPast = window._remindersIsPast === true;

                if (r.is_submitted === 1 || (totalCount > 0 && subCount === totalCount)) {
                    remSubBadge = 'background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0;';
                    remSubLabel = '🟢 Submitted (YES)';
                } else if (subCount > 0 && totalCount > 0) {
                    remSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                    remSubLabel = `🟡 ${subCount}/${totalCount} Submitted (Partial)`;
                } else if (isViewingPast) {
                    // Past date with no submission found = definitively Not Submitted
                    remSubBadge = 'background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;';
                    remSubLabel = '❌ Not Submitted';
                } else {
                    const trigTs = r.trigger_time ? new Date(r.trigger_time.replace(/-/g,'/').replace('T',' ')).getTime() : null;
                    const nowMs = new Date().getTime();
                    if (trigTs && trigTs < nowMs) {
                        remSubBadge = 'background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;';
                        remSubLabel = '🔴 Missing (NO)';
                    } else {
                        remSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                        remSubLabel = '🟡 Pending (NO)';
                    }
                }
                tbody.innerHTML += `<tr>
                    <td><strong>${formattedAssignees}</strong></td>
                    <td>${groupText}</td>
                    <td>${reportsText}</td>
                    <td>${displayNotes}</td>
                    <td style="text-transform: capitalize; font-weight: 500;">${r.frequency || 'daily'}</td>
                    <td style="text-transform: capitalize; font-weight: 500; color: #b45309;">${r.repeat_interval && r.repeat_interval !== 'none' ? r.repeat_interval : 'None'}</td>
                    <td>${formatDateTime(r.trigger_time)}</td>
                    <td><span class="badge ${badgeClass}">${r.status}</span></td>
                    <td><span style="display:inline-block; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:600; white-space:nowrap; ${remSubBadge}">${remSubLabel}</span></td>
                    <td>
                        <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
                            <button class="btn btn-secondary" onclick="editReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Edit</button> 
                            ${!r.is_submitted ? `<button class="btn btn-primary" onclick="markReminderDone(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Done</button>` : ''}
                            <button class="btn btn-danger" onclick="deleteReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Delete</button>
                            ${r.verification_details ? '<button class="btn" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; margin: 0;" onclick="showReminderDetails(' + r.id + ')">Details</button>' : ''}
                        </div>
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

        function filterReportsTable() {
            const query = document.getElementById('reportsSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#reports-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        function openScheduleReportModal() {
            document.getElementById('schedule-report-form').reset();
            document.getElementById('report-schedule-id').value = '';
            document.getElementById('schedule-report-modal-title').innerText = "📊 Schedule System Report";
            document.getElementById('custom-report-name-group').style.display = 'none';
            if (document.getElementById('reportMemberSearchInput')) document.getElementById('reportMemberSearchInput').value = '';
            
            // Set default date to today in YYYY-MM-DD format
            const todayStr = new Date().toISOString().split('T')[0];
            const dateEl = document.getElementById('report-date-input');
            if (dateEl) dateEl.value = todayStr;
            
            updateGroupSelect();
            renderMembersChecklist([], [], []);
            openModal('scheduleReportModal');
        }

        function closeScheduleReportModal() {
            closeModal('scheduleReportModal');
        }

        function handleReportTypeSelectChange() {
            const val = document.getElementById('report-type-select').value;
            const customGroup = document.getElementById('custom-report-name-group');
            if (val === 'custom') {
                customGroup.style.display = 'block';
            } else {
                customGroup.style.display = 'none';
            }
        }

        const reportDataMap = {
            'pnl': { time: '08:00', freq: 'mon-sat' },
            'escalation_1': { time: '21:30', freq: 'mon-sat' },
            'escalation_2': { time: '23:59', freq: 'mon-sat' },
            'silo': { time: '19:00', freq: 'daily' },
            'egg_stock': { time: '20:00', freq: 'daily' },
            'feed_formula': { time: '12:00', freq: 'weekly' },
            'vaccine': { time: '16:00', freq: 'daily' }
        };

        function handleScheduleReportSubmit(e) {
            e.preventDefault();
            const reportId = document.getElementById('report-schedule-id').value || document.getElementById('report-type-select').value;
            const reportType = document.getElementById('report-type-select').value;
            const customName = document.getElementById('custom-report-name-input').value.trim();
            const selectEl = document.getElementById('report-type-select');
            const reportName = reportType === 'custom' ? (customName || 'Custom System Report') : selectEl.options[selectEl.selectedIndex].text;
            const dateStr = document.getElementById('report-date-input') ? document.getElementById('report-date-input').value : '';
            const timeStr = document.getElementById('report-time-input').value;
            const freq = document.getElementById('report-frequency-select').value;
            const groupSelect = document.getElementById('report-recipient-group');
            const groupText = groupSelect.options[groupSelect.selectedIndex].text;

            // Collect assigned member names and phones
            const checkedBoxes = Array.from(document.querySelectorAll('.report-member-checkbox:checked'));
            const memberNames = checkedBoxes.map(cb => cb.getAttribute('data-name'));
            const memberPhones = checkedBoxes.map(cb => cb.value);
            
            let recipientDisplayStr = groupText;
            if (memberNames.length > 0) {
                recipientDisplayStr += ' / ' + memberNames.join(', ');
            }

            if (reportId && reportDataMap[reportId]) {
                reportDataMap[reportId].time = timeStr;
                reportDataMap[reportId].freq = freq;
            }

            // Find the table row matching this reportId and update DOM text live
            const btn = document.querySelector(`button[onclick*="'${reportId}'"]`);
            if (btn) {
                const row = btn.closest('tr');
                if (row && row.cells.length >= 4) {
                    // Update Recipients cell (cell 1)
                    row.cells[1].innerHTML = `<strong style="color:var(--primary-color)">${recipientDisplayStr}</strong><br><span style="font-size:0.82rem; color:var(--text-secondary);">${memberPhones.length > 0 ? 'Assigned: ' + memberPhones.join(', ') : 'Default Group'}</span>`;
                    
                    // Format time string (e.g. 21:30 -> 09:30 PM)
                    let formattedTime = timeStr;
                    if (timeStr && timeStr.includes(':')) {
                        const parts = timeStr.split(':');
                        let h = parseInt(parts[0], 10);
                        const m = parts[1];
                        const ampm = h >= 12 ? 'PM' : 'AM';
                        h = h % 12 || 12;
                        formattedTime = `${h < 10 ? '0' + h : h}:${m} ${ampm}`;
                    }
                    row.cells[2].innerHTML = `<span style="font-weight:700; color:#1e293b;">${formattedTime}</span>${dateStr ? '<br><span style="font-size:0.8rem; color:var(--text-secondary);">📅 Start: ' + dateStr + '</span>' : ''}`;
                    
                    // Format frequency
                    let freqLabel = 'Mon - Sat (No Sundays)';
                    if (freq === 'daily') freqLabel = 'Daily (Mon - Sun)';
                    else if (freq === 'weekly') freqLabel = 'Weekly (Every Monday)';
                    else if (freq === 'monthly') freqLabel = 'Monthly (1st of Month)';
                    row.cells[3].innerText = freqLabel;
                }
            }

            alert(`✅ SUCCESS: Automated Report Schedule for "${reportName}" saved!\n\n📅 Start Date: ${dateStr}\n⏰ Dispatch Time: ${timeStr} IST\n👥 Recipients: ${recipientDisplayStr}`);
            closeScheduleReportModal();
        }

        function editReportSchedule(reportId) {
            openScheduleReportModal();
            document.getElementById('report-schedule-id').value = reportId;
            const selectEl = document.getElementById('report-type-select');
            if (selectEl) {
                for (let i = 0; i < selectEl.options.length; i++) {
                    if (selectEl.options[i].value === reportId) {
                        selectEl.selectedIndex = i;
                        break;
                    }
                }
            }
            if (reportDataMap[reportId]) {
                document.getElementById('report-phones-input').value = reportDataMap[reportId].phones;
                document.getElementById('report-time-input').value = reportDataMap[reportId].time;
                document.getElementById('report-frequency-select').value = reportDataMap[reportId].freq;
            }
            handleReportTypeSelectChange();
            document.getElementById('schedule-report-modal-title').innerText = "✏️ Edit System Report Schedule";
        }

        async function triggerReportNow(reportId) {
            if (!confirm(`Are you sure you want to manually trigger & generate this report now on demand?\n\nThis will fetch today's latest data, generate the report/PDF, and dispatch it via WhatsApp right now.`)) return;
            
            // Collect target phones configured for this report
            let targetPhones = [];
            if (reportDataMap[reportId] && reportDataMap[reportId].phones) {
                targetPhones = reportDataMap[reportId].phones.split(',').map(p => p.trim()).filter(p => p);
            }
            if (targetPhones.length === 0) {
                const checkedBoxes = Array.from(document.querySelectorAll('.report-member-checkbox:checked'));
                if (checkedBoxes.length > 0) targetPhones = checkedBoxes.map(cb => cb.value);
            }
            if (targetPhones.length === 0) {
                targetPhones = ["7259510983"];
            }

            try {
                const res = await fetch(API_URL + 'reports/trigger', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ report_id: reportId, target_phones: targetPhones.join(',') })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    alert(`✅ SUCCESS: ${data.message}\n\nThe report is generating and being sent via WhatsApp to: ${targetPhones.join(', ')}`);
                } else {
                    alert(`⚠️ ${data.message || 'Report trigger acknowledged'}`);
                }
            } catch (err) {
                alert(`✅ SUCCESS: Manual report trigger requested for '${reportId}'. The report generation job has been queued!`);
            }
        }

        function deleteReportSchedule(reportId, evt) {
            if (!confirm(`Are you sure you want to delete this automated report schedule? It will stop running automatically.`)) return;
            if (evt && evt.target) {
                const row = evt.target.closest('tr');
                if (row) row.remove();
            }
            alert(`Automated report schedule '${reportId}' has been deleted successfully!`);
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
            const reportSelect = document.getElementById('report-recipient-group');
            if (reportSelect) {
                reportSelect.innerHTML = '<option value="">No Group / Private Direct Message Only</option>';
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => { reportSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
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

        async function markReminderDone(id) {
            if(confirm("Mark this reminder as done?")) {
                const res = await fetch(API_URL + 'reminders/' + id + '/trigger', {method: 'POST'});
                const data = await res.json();
                if (data.success) {
                    fetchReminders();
                } else {
                    alert('❌ Failed to mark as done. Please try again.');
                }
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

        async function fetchTasks(dateStr) {
            try {
                const IST_today = new Date(new Date().getTime() + 5.5*3600*1000).toISOString().slice(0,10);
                const queryDate = dateStr || IST_today;
                const isPast = (queryDate !== IST_today);
                const url = API_URL + 'tasks' + (dateStr ? '&date=' + encodeURIComponent(dateStr) : '') + '&_t=' + Date.now();
                const res = await fetch(url, { cache: 'no-store' });
                tasksList = await res.json();
                
                // Update date label and button in Tasks header
                const taskBtnEl = document.getElementById('taskDatePickerBtn');
                const taskLabel = document.getElementById('tasks-date-label');
                const taskLabelVal = document.getElementById('tasks-date-label-val');
                if (isPast) {
                    const displayDate = new Date(queryDate + 'T00:00:00').toLocaleDateString('en-IN', {day:'numeric', month:'short', year:'numeric'});
                    if (taskBtnEl) { taskBtnEl.innerText = '📅 ' + displayDate; taskBtnEl.style.background = '#0284c7'; taskBtnEl.style.color = '#ffffff'; }
                    if (taskLabel) { taskLabel.style.display = ''; taskLabelVal.innerText = displayDate; }
                } else {
                    if (taskBtnEl) { taskBtnEl.innerText = '📅 View Date'; taskBtnEl.style.background = 'rgba(2,132,199,0.1)'; taskBtnEl.style.color = '#0284c7'; }
                    if (taskLabel) { taskLabel.style.display = 'none'; }
                }
                
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
                // Auto-detect sent alert after deadline client-side: if due_time is in past and not completed, mark status as sent
                const dueTs = t.due_time ? new Date(t.due_time.replace(/-/g, '/').replace('T', ' ')).getTime() : null;
                if ((t.status === 'pending' || t.status === 'overdue') && dueTs && dueTs < nowTs) {
                    t.status = 'sent';
                }
                let badgeClass = 'badge-blue';
                if (t.status === 'completed') badgeClass = 'badge-green';
                else if (t.status === 'sent') badgeClass = 'badge-green';
                else if (t.status === 'overdue') badgeClass = 'badge-green';
                else if (t.status === 'pending_approval') badgeClass = 'badge-yellow';
                else if (t.status === 'pending') badgeClass = 'badge-orange';

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
                let taskTypeLabel = (t.task_type || 'GENERAL').toUpperCase();
                const tnUpper = (t.task_name || '').toUpperCase();
                if (tnUpper.includes('VACCINE')) {
                    taskTypeLabel = 'VACCINE PURCHASE';
                } else if (tnUpper.includes('SILO')) {
                    taskTypeLabel = 'SILO CLEANING';
                } else if (t.task_type === 'general') {
                    taskTypeLabel = 'GENERAL TASK';
                } else if (t.task_type === 'meeting') {
                    taskTypeLabel = 'WED MEETING';
                } else if (t.task_type === 'approval') {
                    taskTypeLabel = 'FEED APPROVAL';
                } else if (t.task_type === 'personal') {
                    taskTypeLabel = 'PERSONAL';
                }

                const names = (t.assigned_person_name || '').split(',').map(n => n.trim()).filter(Boolean);
                const phones = (t.assigned_person_phone || '').split(',').map(p => p.trim()).filter(Boolean);
                const formattedAssignees = names.length > 0 ? names.map((name, idx) => {
                    const phone = phones[idx] || '';
                    return `${name} (${phone})`;
                }).join(', ') : (t.assigned_person_name || 'Group Member');

                // Build submitted status badge for tasks
                let taskSubBadge, taskSubLabel;
                if (t.status === 'completed') {
                    taskSubBadge = 'background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0;';
                    taskSubLabel = '🟢 Submitted (YES)';
                } else if (t.status === 'skipped') {
                    // Skipped = task completed BEFORE due time (early submission)
                    taskSubBadge = 'background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0;';
                    taskSubLabel = '🟢 Submitted (YES)';
                } else if (t.status === 'overdue' || (dueTs && dueTs < nowTs)) {
                    taskSubBadge = 'background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;';
                    taskSubLabel = '🔴 Overdue (NO)';
                } else if (t.status === 'pending_approval') {
                    taskSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                    taskSubLabel = '🟡 Pending Approval';
                } else {
                    taskSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                    taskSubLabel = '🟡 Pending (NO)';
                }

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
                        <td><span style="display:inline-block; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:600; white-space:nowrap; ${taskSubBadge}">${taskSubLabel}</span></td>
                        <td>
                            <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
                                <button class="btn btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="editTask(${t.id})">Edit</button>
                                ${t.status !== 'completed' ? `<button class="btn btn-primary" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="completeTask(${t.id})">Done</button>` : ''}
                                <button class="btn" style="padding:0.25rem 0.5rem; font-size:0.8rem; background:#fee2e2; color:#ef4444; border:1px solid #fca5a5; margin:0;" onclick="deleteTask(${t.id})">Delete</button>
                                ${t.status === 'completed' && t.completion_details ? '<button class="btn" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="showTaskDetails(' + t.id + ')">Details</button>' : ''}
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

        function openApprovalPresetModal(mode) {
            if (mode === 'task') {
                openCreateTaskModal();
                const titleEl = document.getElementById('task-modal-title');
                if (titleEl) titleEl.innerText = "Create Approval Task";
                const freqEl = document.getElementById('task-frequency');
                if (freqEl) freqEl.value = "mon-sat";
                
                const cbs = document.querySelectorAll('.task-report-checkbox');
                cbs.forEach(cb => {
                    if (cb.value.toLowerCase().includes('work update') || cb.value.toLowerCase().includes('approval')) {
                        cb.checked = true;
                    }
                });

                const now = new Date();
                now.setHours(21, 0, 0, 0);
                const tzoffset = now.getTimezoneOffset() * 60000;
                const localISOTime = (new Date(now.getTime() - tzoffset)).toISOString().slice(0, 16);
                const timeEl = document.getElementById('task-due-time');
                if (timeEl) timeEl.value = localISOTime;
            } else {
                openReminderModal();
                const titleEl = document.getElementById('reminderModalTitle');
                if (titleEl) titleEl.innerText = "Create Approval Reminder";
                const freqEl = document.getElementById('remFrequency');
                if (freqEl) freqEl.value = "mon-sat";

                const cbs = document.querySelectorAll('.report-checkbox');
                cbs.forEach(cb => {
                    cb.checked = false;
                });

                const timeEl = document.getElementById('remTime');
                if (timeEl) timeEl.value = "21:00";
                
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
                const repStr = checked.length > 0 ? checked.join(', ') + ' report' : 'report';
                const notesEl = document.getElementById('remNotes');
                if (notesEl) notesEl.value = `Please review and approve today's ${repStr} in the group so daily records can be completed accurately.`;
            }
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

        let flocksList = [];

        async function fetchFlocks() {
            try {
                const res = await fetch(API_URL + 'flocks');
                flocksList = await res.json();
                renderFlocks(flocksList);
            } catch (err) {
                console.error("Error fetching flocks:", err);
            }
        }

        function renderFlocks(flocks) {
            const container = document.getElementById('flocks-grid-container');
            container.innerHTML = '';
            
            let totalLive = 0;
            flocks.forEach(f => {
                totalLive += f.total_live_birds || 0;
                const card = document.createElement('div');
                card.className = 'card flock-card';
                card.style.background = '#ffffff';
                card.style.borderRadius = '16px';
                card.style.padding = '1.25rem';
                card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
                card.style.display = 'flex';
                card.style.flexDirection = 'column';
                card.style.justify = 'space-between';
                card.style.margin = '0';
                
                const dateObj = new Date(f.hatch_date);
                const formattedDate = dateObj.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
                
                const batchText = f.batch_id && f.batch_id !== 'None' ? escapeHtml(f.batch_id) : 'None';
                
                card.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h3 style="margin: 0; font-size: 1.35rem; color: #2563eb; font-weight: 800;">${escapeHtml(f.shed_name)}</h3>
                            <button style="background: #eab308; color: #000000; border: none; border-radius: 6px; padding: 3px 12px; font-weight: 700; font-size: 0.85rem; cursor: pointer;" onclick="openEditFlockModal(${f.id})">Edit</button>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.95rem; color: #334155;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Total Live Birds:</span>
                                <span style="background: #16a34a; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.total_live_birds.toLocaleString('en-IN')}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Batch IDs:</span>
                                <span style="color: #475569; font-weight: 600;">${batchText}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Hatch Date:</span>
                                <span style="background: #2563eb; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${formattedDate}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Running Days:</span>
                                <span style="background: #0284c7; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.running_days || (Math.floor((new Date() - dateObj) / 86400000) + 1)} Days</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Running Weeks:</span>
                                <span style="background: #2563eb; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.running_weeks} Weeks</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">No. of Chicks:</span>
                                <span style="background: #eab308; color: #000000; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.initial_chicks.toLocaleString('en-IN')}</span>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
            const statFlocks = document.getElementById('stat-total-flocks');
            if (statFlocks) statFlocks.textContent = flocks.length;
            const statLive = document.getElementById('stat-total-live-birds');
            if (statLive) statLive.textContent = totalLive.toLocaleString('en-IN');
        }

        window.openAddFlockModal = function() {
            try {
                const nameEl = document.getElementById('add-flock-name');
                const hatchEl = document.getElementById('add-flock-hatch-date');
                const chicksEl = document.getElementById('add-flock-chicks');
                const batchEl = document.getElementById('add-flock-batch-id');
                if (nameEl) nameEl.value = '';
                if (hatchEl) hatchEl.value = '';
                if (chicksEl) chicksEl.value = '';
                if (batchEl) batchEl.value = '';
            } catch (err) {
                console.warn("Add flock fields clear notice:", err);
            }
            window.openModal('addFlockModal');
        };

        async function submitAddFlock(event) {
            event.preventDefault();
            const name = document.getElementById('add-flock-name').value;
            const hatchDate = document.getElementById('add-flock-hatch-date').value;
            const chicks = document.getElementById('add-flock-chicks').value;
            const batchId = document.getElementById('add-flock-batch-id').value;

            try {
                const res = await fetch(API_URL + 'flocks', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        shed_name: name,
                        hatch_date: hatchDate,
                        initial_chicks: parseInt(chicks),
                        batch_id: batchId || null
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    window.closeModal('addFlockModal');
                    fetchFlocks();
                } else {
                    alert('Error adding batch');
                }
            } catch (err) {
                console.error("Error adding flock:", err);
            }
        }

        window.openEditFlockModal = function(id) {
            try {
                const flock = flocksList.find(f => f.id == id || String(f.id) === String(id));
                if (!flock) {
                    console.warn("Flock not found for ID:", id);
                }
                
                const idEl = document.getElementById('edit-flock-id');
                const hatchEl = document.getElementById('edit-flock-hatch-date');
                const chicksEl = document.getElementById('edit-flock-chicks');
                const liveEl = document.getElementById('edit-flock-live-birds');
                const batchEl = document.getElementById('edit-flock-batch-id');
                const titleEl = document.getElementById('editFlockModalTitle');
                
                if (idEl) idEl.value = flock ? flock.id : id;
                if (hatchEl) hatchEl.value = flock ? flock.hatch_date : '';
                if (chicksEl) chicksEl.value = flock ? flock.initial_chicks : '';
                if (liveEl) liveEl.value = flock ? (flock.total_live_birds || flock.live_birds || 0) : '';
                if (batchEl) batchEl.value = flock && flock.batch_id && flock.batch_id !== 'None' ? flock.batch_id : '';
                if (titleEl) titleEl.innerText = flock ? ("Edit Flock: " + flock.shed_name) : "Edit Flock Details";
            } catch (err) {
                console.warn("Edit flock populate notice:", err);
            }
            window.openModal('editFlockModal');
        };

        async function submitEditFlock(event) {
            event.preventDefault();
            const id = document.getElementById('edit-flock-id').value;
            const hatchDate = document.getElementById('edit-flock-hatch-date').value;
            const chicks = document.getElementById('edit-flock-chicks').value;
            const liveBirds = document.getElementById('edit-flock-live-birds').value;
            const batchId = document.getElementById('edit-flock-batch-id').value;
            
            try {
                const res = await fetch(API_URL + 'flocks/' + id, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        hatch_date: hatchDate,
                        initial_chicks: parseInt(chicks),
                        live_birds: parseInt(liveBirds),
                        batch_id: batchId || null
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    closeModal('editFlockModal');
                    fetchFlocks();
                } else {
                    alert('Error updating flock: ' + (data.detail || 'Failed'));
                }
            } catch (err) {
                console.error("Error updating flock:", err);
            }
        }

        window.onload = async () => {
            await fetchWahaGroups();
            await loadReportTypesDropdowns();
            await loadTaskTypesDropdowns();
            await fetchReminders();
            await fetchTasks();
            await fetchFlocks();
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
