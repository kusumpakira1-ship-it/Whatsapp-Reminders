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
        `value` VARCHAR(255) NULL
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
            `value` VARCHAR(255) NULL
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

// 3. Simple REST API Router
if (isset($_GET['api'])) {
    header("Content-Type: application/json");
    $method = $_SERVER['REQUEST_METHOD'];
    $route = $_GET['api'];

    try {
        if ($route === 'reminders' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM sunfra_unified_reminders ORDER BY trigger_time ASC");
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
            $pdo->prepare("UPDATE sunfra_unified_reminders SET trigger_time = CONVERT_TZ(NOW(), '+00:00', '+05:30'), status = 'pending' WHERE id = ?")->execute([$matches[1]]);
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
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Farm Automation Management</title>
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
        .table-card { padding: 0; overflow: hidden; }
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
            </nav>
        </aside>
        <!-- Main Content -->
        <main class="main-content">
            <!-- Dashboard View -->
            <section id="dashboard" class="view active">
            <header>
                <h1>Management Dashboard</h1>
            </header>
                <div class="stats-grid">
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
            </section>
            
            <!-- Reminders View -->
            <section id="reminders_view" class="view">
                <div class="header-row">
                    <h2>Reminders Management</h2>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary" onclick="openVisibilityModal()">Filter Groups</button>
                        <button class="btn btn-primary" onclick="openReminderModal()">+ Create Reminder</button>
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
                                <th>Trigger Time</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="reminders-tbody"></tbody>
                    </table>
                </div>
            </section>
        </main>
    </div>

    <!-- Reminder Modal -->
    <div id="reminderModal" class="modal">
        <div class="modal-content card">
            <h3 id="reminderModalTitle">Create Reminder</h3>
            <form id="reminderForm" onsubmit="handleReminderSubmit(event)">
                <input type="hidden" id="editReminderId">
                <div class="form-group">
                    <label>Person Name</label>
                    <input type="text" id="remPersonName" required placeholder="e.g., Kusum">
                </div>
                <div class="form-group">
                    <label>Person Phone Number</label>
                    <input type="text" id="remPersonPhone" required pattern="[0-9]{10}" maxlength="10" placeholder="e.g., 7259510983" oninput="this.value = this.value.replace(/[^0-9]/g, '')">
                </div>
                
                <div class="form-group">
                    <label style="margin-bottom: 0.8rem; font-weight: 600;">Assigned Report Types (Multiple)</label>
                    <div id="reportCheckboxesContainer" style="display: flex; flex-direction: column; gap: 0.5rem; max-height: 150px; overflow-y: auto; padding: 0.5rem; border: 1px solid rgba(0,0,0,0.1); border-radius: 8px; background: rgba(255,255,255,0.8); margin-bottom: 0.5rem;">
                        <!-- Checkboxes populated dynamically -->
                    </div>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" id="newReportTypeInput" placeholder="Add custom report type..." style="padding: 0.5rem; border-radius: 6px; border: 1px solid rgba(0,0,0,0.1); font-size: 0.9rem;">
                        <button type="button" class="btn btn-secondary" onclick="addNewReportTypeCheckbox()" style="padding: 0.5rem 1rem; font-size: 0.9rem;">+ Add</button>
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
                        <option value="daily">Daily</option>
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
    <script>
        const API_URL = '?api=';
        let waha_groups = [];
        let hidden_groups = [];
        let employees = [];
        let alarms = [];
        let report_types = [];

        async function loadReportTypesDropdowns() {
            try {
                const res = await fetch(API_URL + 'settings/report_types');
                report_types = await res.json();
            } catch (err) {
                report_types = ["Production", "Feed", "Expenses", "Sales", "Profit and Loss"];
            }
            renderReportCheckboxes([]);
        }

        function renderReportCheckboxes(selected = []) {
            const container = document.getElementById('reportCheckboxesContainer');
            container.innerHTML = '';
            report_types.forEach(r => {
                const checked = selected.includes(r) ? 'checked' : '';
                container.innerHTML += `
                    <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.25rem 0;">
                        <input type="checkbox" id="report-${r}" value="${r}" ${checked} class="report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="updateNotesFromCheckedReports()">
                        <label for="report-${r}" style="cursor:pointer; font-size:0.9rem; color:var(--text-primary); font-weight:500;">${r}</label>
                    </div>
                `;
            });
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
                input.value = '';
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
            const dt = parseLocalStatusTime(isoString);
            return dt.toLocaleString('en-US', {
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        }

        let reminders = [];
        async function fetchReminders() {
            const res = await fetch(API_URL + 'reminders');
            reminders = await res.json();
            const tbody = document.getElementById('reminders-tbody');
            tbody.innerHTML = '';
            
            reminders.forEach(r => {
                const badgeClass = r.status === 'sent' ? 'badge-green' : (r.status === 'pending' ? 'badge-orange' : '');
                const groupText = r.whatsapp_group_id ? `<strong style="color:var(--primary-color)">${r.group_name}</strong>` : `<span style="color:var(--text-secondary)">No Group / Private Only</span>`;
                const reportsText = r.report_types ? r.report_types.split(',').map(rep => `<span class="badge badge-blue" style="margin-right:0.25rem; font-size:0.7rem; display:inline-block; margin-top:2px;">${rep.trim()}</span>`).join(' ') : '<span style="color:var(--text-secondary)">Custom Notes Only</span>';
                
                tbody.innerHTML += `<tr>
                    <td><strong>${r.person_name}</strong><br><small style="color:var(--text-secondary)">${r.person_phone}</small></td>
                    <td>${groupText}</td>
                    <td>${reportsText}</td>
                    <td>${r.task_notes}</td>
                    <td>${formatDateTime(r.trigger_time)}</td>
                    <td><span class="badge ${badgeClass}">${r.status}</span></td>
                    <td>
                        <button class="btn btn-secondary" onclick="editReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Edit</button> 
                        <button class="btn btn-secondary" onclick="triggerReminderNow(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; background: rgba(59,130,246,0.1); color: var(--primary-color); border: 1px solid rgba(59,130,246,0.2);">Trigger Now</button>
                        <button class="btn btn-danger" onclick="deleteReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Delete</button>
                    </td>
                </tr>`;
            });
            
            document.getElementById('stat-employees').innerText = new Set(reminders.map(r => r.person_phone)).size;
            document.getElementById('stat-groups').innerText = new Set(reminders.map(r => r.whatsapp_group_id).filter(g => g)).size;
            document.getElementById('stat-alarms').innerText = reminders.length;
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
        }

        function openReminderModal() {
            document.getElementById('reminderForm').reset();
            document.getElementById('editReminderId').value = '';
            document.getElementById('reminderModalTitle').innerText = 'Create Reminder';
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
            document.getElementById('remPersonName').value = r.person_name;
            document.getElementById('remPersonPhone').value = r.person_phone;
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

            const editId = document.getElementById('editReminderId').value;
            const method = editId ? 'PUT' : 'POST';
            const url = API_URL + 'reminders' + (editId ? '/' + editId : '');

            await fetch(url, {
                method: method,
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    person_name: document.getElementById('remPersonName').value,
                    person_phone: document.getElementById('remPersonPhone').value,
                    whatsapp_group_id: document.getElementById('remGroupSelect').value || null,
                    report_types: reportTypesStr,
                    task_notes: document.getElementById('remNotes').value,
                    trigger_time: triggerTime,
                    frequency: document.getElementById('remFrequency').value,
                    repeat_interval: document.getElementById('remRepeatInterval').value
                })
            });
            closeModal('reminderModal');
            fetchReminders();
        }

        async function deleteReminder(id) {
            if(confirm("Delete reminder?")) {
                await fetch(API_URL + 'reminders/' + id, {method: 'DELETE'});
                fetchReminders();
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

        window.onload = async () => {
            await fetchWahaGroups();
            await loadReportTypesDropdowns();
            await fetchReminders();
        };
    </script>
</body>
</html>
