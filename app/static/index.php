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
    $pdo->exec("CREATE TABLE IF NOT EXISTS wa_groups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        whatsapp_group_id VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->exec("CREATE TABLE IF NOT EXISTS wa_employees (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        phone_number VARCHAR(50) NOT NULL,
        group_id INT,
        report_responsibility VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");

    $pdo->exec("CREATE TABLE IF NOT EXISTS wa_alarms (
        id INT AUTO_INCREMENT PRIMARY KEY,
        target_type VARCHAR(50),
        target_id INT,
        task_notes TEXT,
        trigger_time DATETIME,
        status VARCHAR(50) DEFAULT 'pending',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");
} catch (PDOException $e) {
    // Fallback to SQLite syntax if MySQL fails
    try {
        $pdo->exec("CREATE TABLE IF NOT EXISTS wa_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            whatsapp_group_id VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS wa_employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            phone_number VARCHAR(50) NOT NULL,
            group_id INTEGER,
            report_responsibility VARCHAR(100),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )");
        $pdo->exec("CREATE TABLE IF NOT EXISTS wa_alarms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type VARCHAR(50),
            target_id INTEGER,
            task_notes TEXT,
            trigger_time DATETIME,
            status VARCHAR(50) DEFAULT 'pending',
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
    // Add columns dynamically for the architecture update
    try { $pdo->exec("ALTER TABLE wa_employees ADD COLUMN whatsapp_group_id VARCHAR(255)"); } catch (Exception $e) {}
    try { $pdo->exec("ALTER TABLE wa_alarms ADD COLUMN whatsapp_target_id VARCHAR(255)"); } catch (Exception $e) {}

// 3. Simple REST API Router
if (isset($_GET['api'])) {
    header("Content-Type: application/json");
    $method = $_SERVER['REQUEST_METHOD'];
    $route = $_GET['api'];

    try {
        if ($route === 'employees' && $method === 'GET') {
            $stmt = $pdo->query("SELECT a.*, e.name, e.phone_number FROM wa_alarms a JOIN wa_employees e ON a.target_id = e.id WHERE a.target_type = 'employee' ORDER BY a.trigger_time ASC");
            $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
            foreach ($rows as &$row) {
                $phone = $row['phone_number'];
                $row['whatsapp_id'] = preg_match('/^\d{10}$/', $phone) ? "91{$phone}@c.us" : "{$phone}@c.us";
            }
            echo json_encode($rows);
        }
        elseif ($route === 'employees' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            // 1. Create or get member
            $stmt = $pdo->prepare("INSERT INTO wa_employees (name, phone_number, whatsapp_group_id, report_responsibility) VALUES (?, ?, '', '')");
            $stmt->execute([$data['name'], $data['phone_number']]);
            $member_id = $pdo->lastInsertId();
            
            // 2. Create reminder for member
            $stmt2 = $pdo->prepare("INSERT INTO wa_alarms (target_type, target_id, task_notes, trigger_time) VALUES ('employee', ?, ?, ?)");
            $stmt2->execute([$member_id, $data['task_notes'], $data['trigger_time']]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^employees\/(\d+)$/', $route, $matches) && $method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("UPDATE wa_employees e JOIN wa_alarms a ON a.target_id = e.id SET e.name = ?, e.phone_number = ?, a.task_notes = ?, a.trigger_time = ? WHERE a.id = ?");
            $stmt->execute([$data['name'], $data['phone_number'], $data['task_notes'], $data['trigger_time'], $matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^employees\/(\d+)$/', $route, $matches) && $method === 'DELETE') {
            $pdo->prepare("DELETE FROM wa_alarms WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        
        elseif ($route === 'alarms' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM wa_alarms WHERE target_type = 'group' ORDER BY trigger_time ASC");
            $alarms = $stmt->fetchAll(PDO::FETCH_ASSOC);
            // Enrich with target names and whatsapp_id for the live bridge
            $waha_file = __DIR__ . '/waha_groups.json';
            $waha_groups = file_exists($waha_file) ? json_decode(file_get_contents($waha_file), true)['groups'] ?? [] : [];
            
            foreach ($alarms as &$alarm) {
                    $alarm['target_id'] = $alarm['whatsapp_target_id']; // For frontend edit modal
                    $alarm['whatsapp_id'] = $alarm['whatsapp_target_id'];
                    $alarm['target_name'] = 'Unknown Group';
                    foreach ($waha_groups as $g) {
                        if ($g['id'] === $alarm['whatsapp_target_id']) {
                            $alarm['target_name'] = $g['name'];
                            break;
                        }
                    }
                    
                }
            echo json_encode($alarms);
        }
        elseif ($route === 'bridge/alarms' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM wa_alarms WHERE status = 'pending' ORDER BY trigger_time ASC");
            $alarms = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            $waha_file = __DIR__ . '/waha_groups.json';
            $waha_groups = file_exists($waha_file) ? json_decode(file_get_contents($waha_file), true)['groups'] ?? [] : [];
            
            foreach ($alarms as &$alarm) {
                if ($alarm['target_type'] === 'employee') {
                    $stmt2 = $pdo->prepare("SELECT phone_number FROM wa_employees WHERE id = ?");
                    $stmt2->execute([$alarm['target_id']]);
                    $phone = $stmt2->fetchColumn();
                    if ($phone) {
                        $alarm['whatsapp_id'] = preg_match('/^\d{10}$/', $phone) ? "91{$phone}@c.us" : "{$phone}@c.us";
                    } else {
                        $alarm['whatsapp_id'] = null;
                    }
                } else {
                    $alarm['whatsapp_id'] = $alarm['whatsapp_target_id'];
                }
            }
            echo json_encode($alarms);
        }
        elseif ($route === 'alarms' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $target_id = $data['target_type'] === 'employee' ? $data['target_id'] : null;
            $whatsapp_target_id = $data['target_type'] === 'group' ? $data['target_id'] : null;
            
            $stmt = $pdo->prepare("INSERT INTO wa_alarms (target_type, target_id, whatsapp_target_id, task_notes, trigger_time) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute([$data['target_type'], $target_id, $whatsapp_target_id, $data['task_notes'], $data['trigger_time']]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^alarms\/(\d+)$/', $route, $matches) && $method === 'PUT') {
            $data = json_decode(file_get_contents('php://input'), true);
            $target_id = $data['target_type'] === 'employee' ? $data['target_id'] : null;
            $whatsapp_target_id = $data['target_type'] === 'group' ? $data['target_id'] : null;
            
            $stmt = $pdo->prepare("UPDATE wa_alarms SET target_type = ?, target_id = ?, whatsapp_target_id = ?, task_notes = ?, trigger_time = ? WHERE id = ?");
            $stmt->execute([$data['target_type'], $target_id, $whatsapp_target_id, $data['task_notes'], $data['trigger_time'], $matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^alarms\/(\d+)$/', $route, $matches) && $method === 'DELETE') {
            $pdo->prepare("DELETE FROM wa_alarms WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^alarms\/(\d+)\/trigger$/', $route, $matches) && $method === 'POST') {
            $pdo->prepare("UPDATE wa_alarms SET status = 'sent' WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^alarms\/(\d+)\/instant$/', $route, $matches) && $method === 'POST') {
            $pdo->prepare("UPDATE wa_alarms SET trigger_time = CURRENT_TIMESTAMP, status = 'pending' WHERE id = ?")->execute([$matches[1]]);
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

        .stat-card {
            display: inline-block;
            width: 280px;
            margin-right: 2rem;
            margin-bottom: 2rem;
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
            transform: scale(0.95);
            transition: transform 0.3s ease;
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
            
            /* Modal responsiveness */
            .modal-content { width: 95%; padding: 1.5rem; margin: 1rem; }
            #alarmDatetimeSection > div { flex-wrap: wrap; }
            #alarmDatetimeSection input[type="date"] { flex: 100%; min-width: 100%; }
            #alarmTimerSection > div { flex-wrap: wrap; justify-content: center; }
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
                <a href="#" class="nav-item" data-target="employees">WhatsApp Members</a>
                <a href="#" class="nav-item" data-target="alarms">WhatsApp Groups</a>
            </nav>
        </aside>
        <!-- Main Content -->
        <main class="main-content">
            <!-- Dashboard View -->
            <section id="dashboard" class="view active">
            <header>
                <h1>Management Dashboard</h1>
            </header>
                <div style="display: flex; gap: 1.5rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'employees\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Members">
                        <h3>Total Members</h3>
                        <div class="stat-value" id="stat-employees">0</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'alarms\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Groups">
                        <h3>Groups Used</h3>
                        <div class="stat-value" id="stat-groups">0</div>
                    </div>
                    <div class="card stat-card" onclick="document.querySelector('.nav-item[data-target=\'alarms\']').click()" style="cursor: pointer; margin-right: 0;" title="Go to Alarms">
                        <h3>Total Reminders</h3>
                        <div class="stat-value" id="stat-alarms">0</div>
                    </div>
                </div>
            </section>
            <!-- Employees View -->
            <section id="employees" class="view">
                <div class="header-row">
                    <h2>Members Management</h2>
                    <button class="btn btn-primary" onclick="openModal('employeeModal')">+ Add Member</button>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Phone</th>
                                <th>Task / Notes</th>
                                <th>Trigger Time</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="employees-tbody"></tbody>
                    </table>
                </div>
            </section>

            <!-- Alarms View -->
            <section id="alarms" class="view">
                <div class="header-row">
                    <h2>Groups Management</h2>
                    <div style="display: flex; gap: 0.5rem;">
                        <button class="btn btn-secondary" onclick="openVisibilityModal()">Filter Groups</button>
                        <button class="btn btn-primary" onclick="openModal('alarmModal')">+ Create Reminder</button>
                    </div>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Group</th>
                                <th>Task / Notes</th>
                                <th>Trigger Time</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="alarms-tbody"></tbody>
                    </table>
                </div>
            </section>
        </main>
    </div>

    <!-- Employee Modal -->
    <div id="employeeModal" class="modal">
        <div class="modal-content card">
            <h3 id="employeeModalTitle">Create Member Reminder</h3>
            <form id="employeeForm" onsubmit="handleEmployeeSubmit(event)">
                <input type="hidden" id="editEmployeeId">
                <div class="form-group">
                    <label>Member Name</label>
                    <input type="text" id="empName" required placeholder="e.g., John Doe">
                </div>
                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="text" id="empPhone" required pattern="[0-9]{10}" maxlength="10" placeholder="e.g., 9876543210" oninput="this.value = this.value.replace(/[^0-9]/g, '')">
                </div>
                <div class="form-group">
                    <label>Task / Notes</label>
                    <textarea id="empNotes" required placeholder="What should they do?" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label>Schedule Mode</label>
                    <div class="radio-group" style="display: flex; gap: 1rem; margin-top: 0.5rem;">
                        <label><input type="radio" name="empAlarmMode" value="datetime" checked onchange="toggleEmpAlarmMode()"> Specific Date & Time</label>
                        <label><input type="radio" name="empAlarmMode" value="timer" onchange="toggleEmpAlarmMode()"> Timer</label>
                    </div>
                </div>
                <div id="empDatetimeSection" class="form-group">
                    <label>Select Date & Time</label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="date" id="empDate" style="flex: 2;" required>
                        <input type="time" id="empTime" style="flex: 1;" required>
                    </div>
                </div>
                <div id="empTimerSection" class="form-group" style="display:none;">
                    <label>Set Timer</label>
                    <div style="display: flex; gap: 1rem;">
                        <div style="text-align: center;">
                            <input type="number" id="empDays" min="0" value="0" style="width: 60px; text-align: center;">
                            <div style="font-size: 12px; color: #666;">Days</div>
                        </div>
                        <div style="text-align: center;">
                            <input type="number" id="empHours" min="0" max="23" value="0" style="width: 60px; text-align: center;">
                            <div style="font-size: 12px; color: #666;">Hrs</div>
                        </div>
                        <div style="text-align: center;">
                            <input type="number" id="empMins" min="0" max="59" value="0" style="width: 60px; text-align: center;">
                            <div style="font-size: 12px; color: #666;">Mins</div>
                        </div>
                        <div style="text-align: center;">
                            <input type="number" id="empSecs" min="0" max="59" value="0" style="width: 60px; text-align: center;">
                            <div style="font-size: 12px; color: #666;">Secs</div>
                        </div>
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('employeeModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Reminder</button>
                </div>
            </form>
        </div>
    </div>
    <!-- Alarm Modal -->
    <div id="alarmModal" class="modal">
        <div class="modal-content card">
            <h3 id="alarmModalTitle">Create Custom Reminder</h3>
            <form id="alarmForm" onsubmit="handleAlarmSubmit(event)">
                <input type="hidden" id="editAlarmId">
                <div class="form-group">
                    <label>Select WhatsApp Group</label>
                    <select id="alarmTargetSelect" required></select>
                </div>
                <div class="form-group">
                    <label>Task / Notes</label>
                    <textarea id="alarmNotes" required placeholder="What should they do?" rows="3"></textarea>
                </div>
                
                <div class="form-group">
                    <label>Schedule Mode</label>
                    <div style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                        <label><input type="radio" name="alarmMode" value="datetime" checked onchange="toggleAlarmMode()"> Specific Date & Time</label>
                        <label><input type="radio" name="alarmMode" value="timer" onchange="toggleAlarmMode()"> Timer</label>
                    </div>
                </div>
                
                <div id="alarmDatetimeSection" class="form-group">
                    <label>Select Date & Time</label>
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="date" id="alarmDate" style="flex: 2;" required>
                        <input type="time" id="alarmTime" style="flex: 1;" required>
                    </div>
                </div>
                
                <div id="alarmTimerSection" class="form-group" style="display:none;">
                    <label>Trigger After:</label>
                    <div style="display: flex; gap: 1rem; align-items: center;">
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.2rem;">
                            <input type="number" id="alarmDays" min="0" value="0" style="width: 60px; text-align: center;">
                            <span style="font-size:0.85rem; color: var(--text-secondary);">Day</span>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.2rem;">
                            <input type="number" id="alarmHours" min="0" max="23" value="0" style="width: 60px; text-align: center;">
                            <span style="font-size:0.85rem; color: var(--text-secondary);">Hour</span>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.2rem;">
                            <input type="number" id="alarmMins" min="0" max="59" value="0" style="width: 60px; text-align: center;">
                            <span style="font-size:0.85rem; color: var(--text-secondary);">Min</span>
                        </div>
                        <div style="display: flex; flex-direction: column; align-items: center; gap: 0.2rem;">
                            <input type="number" id="alarmSecs" min="0" max="59" value="0" style="width: 60px; text-align: center;">
                            <span style="font-size:0.85rem; color: var(--text-secondary);">Sec</span>
                        </div>
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('alarmModal')">Cancel</button>
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
            // MySQL dateStr is like "2026-07-01 15:30:00" or "2026-07-01T15:30:00"
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

        function updateTotalRemindersCount() {
            const statAlarms = document.getElementById('stat-alarms');
            if (statAlarms) {
                statAlarms.innerText = (alarms ? alarms.length : 0) + (employees ? employees.length : 0);
            }
        }

        async function fetchEmployees() {
            const res = await fetch(API_URL + 'employees');
            employees = await res.json();
            const tbody = document.getElementById('employees-tbody');
            tbody.innerHTML = '';
            employees.forEach(e => {
                const badgeClass = e.status === 'sent' ? 'badge-green' : (e.status === 'pending' ? 'badge-orange' : '');
                tbody.innerHTML += `<tr>
                    <td><strong>${e.name}</strong></td>
                    <td style="color:var(--text-secondary)">${e.phone_number}</td>
                    <td>${e.task_notes}</td>
                    <td>${formatDateTime(e.trigger_time)}</td>
                    <td><span class="badge ${badgeClass}">${e.status}</span></td>
                    <td><button class="btn btn-secondary" onclick="editEmployee(${e.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Edit</button> <button class="btn btn-danger" onclick="deleteEmployee(${e.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Delete</button></td>
                </tr>`;
            });
            document.getElementById('stat-employees').innerText = employees.length;
            updateTotalRemindersCount();
        }

        async function fetchAlarms() {
            const res = await fetch(API_URL + 'alarms');
            alarms = await res.json();
            const tbody = document.getElementById('alarms-tbody');
            tbody.innerHTML = '';
            alarms.forEach(a => {
                const badgeClass = a.status === 'sent' ? 'badge-green' : (a.status === 'pending' ? 'badge-orange' : '');
                const targetText = `<strong>${a.target_name}</strong>`;
                tbody.innerHTML += `<tr>
                    <td>${targetText}</td>
                    <td>${a.task_notes}</td>
                    <td>${formatDateTime(a.trigger_time)}</td>
                    <td><span class="badge ${badgeClass}">${a.status}</span></td>
                    <td><button class="btn btn-secondary" onclick="editAlarm(${a.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Edit</button> <button class="btn btn-danger" onclick="deleteAlarm(${a.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Delete</button></td>
                </tr>`;
            });
            updateTotalRemindersCount();
            const statGroups = document.getElementById('stat-groups');
            if (statGroups) {
                const uniqueGroupsCount = new Set(alarms.map(a => a.target_id).filter(id => id)).size;
                statGroups.innerText = uniqueGroupsCount;
            }
        }

        async function fetchWahaGroups() {
            try {
                const res = await fetch(API_URL + 'waha/groups');
                const data = await res.json();
                if (data.status === 'success') {
                    waha_groups = data.groups || [];
                    hidden_groups = data.hidden_groups || [];
                    // Sort alphabetically
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
            updateAlarmTargetSelect();
        }

        function updateGroupSelect() {
            const select = document.getElementById('empGroup');
            if (select) {
                select.innerHTML = '<option value="">Select a WhatsApp Group...</option>';
                waha_groups.forEach(g => { select.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
            }
        }

        function updateAlarmTargetSelect() {
            const select = document.getElementById('alarmTargetSelect');
            if (select) {
                select.innerHTML = '<option value="">Select a WhatsApp Group...</option>';
                const list = waha_groups.filter(g => !hidden_groups.includes(g.id));
                // Sort alphabetically
                const sortedList = [...list].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
                sortedList.forEach(i => select.innerHTML += `<option value="${i.id}">${i.name}</option>`);
            }
        }

        function toggleAlarmMode() {
            const mode = document.querySelector('input[name="alarmMode"]:checked').value;
            document.getElementById('alarmDatetimeSection').style.display = mode === 'datetime' ? 'block' : 'none';
            document.getElementById('alarmTimerSection').style.display = mode === 'timer' ? 'block' : 'none';
        }
        function toggleEmpAlarmMode() {
            const mode = document.querySelector('input[name="empAlarmMode"]:checked').value;
            document.getElementById('empDatetimeSection').style.display = mode === 'datetime' ? 'block' : 'none';
            document.getElementById('empTimerSection').style.display = mode === 'timer' ? 'block' : 'none';
        }
        function editEmployee(id) {
            const e = employees.find(x => x.id == id);
            if (!e) return;
            document.getElementById('editEmployeeId').value = e.id;
            document.getElementById('employeeModalTitle').innerText = 'Edit Member Reminder';
            document.getElementById('empName').value = e.name;
            document.getElementById('empPhone').value = e.phone_number;
            document.getElementById('empNotes').value = e.task_notes;
            
            document.querySelector('input[name="empAlarmMode"][value="datetime"]').checked = true;
            toggleEmpAlarmMode();
            
            const dt = parseLocalStatusTime(e.trigger_time);
            const format = n => String(n).padStart(2, '0');
            document.getElementById('empDate').value = `${dt.getFullYear()}-${format(dt.getMonth() + 1)}-${format(dt.getDate())}`;
            document.getElementById('empTime').value = `${format(dt.getHours())}:${format(dt.getMinutes())}`;
            
            openModal('employeeModal');
        }

        async function handleEmployeeSubmit(e) {
            e.preventDefault();
            const mode = document.querySelector('input[name="empAlarmMode"]:checked').value;
            let triggerTime;
            if (mode === 'datetime') {
                const d = document.getElementById('empDate').value;
                const t = document.getElementById('empTime').value;
                if (!d || !t) return alert("Please select a date and time");
                triggerTime = `${d}T${t}:00`;
            } else {
                const now = new Date();
                now.setDate(now.getDate() + (parseInt(document.getElementById('empDays').value) || 0));
                now.setHours(now.getHours() + (parseInt(document.getElementById('empHours').value) || 0));
                now.setMinutes(now.getMinutes() + (parseInt(document.getElementById('empMins').value) || 0));
                now.setSeconds(now.getSeconds() + (parseInt(document.getElementById('empSecs').value) || 0));
                
                const format = n => String(n).padStart(2, '0');
                triggerTime = `${now.getFullYear()}-${format(now.getMonth()+1)}-${format(now.getDate())}T${format(now.getHours())}:${format(now.getMinutes())}:${format(now.getSeconds())}`;
            }

            const editId = document.getElementById('editEmployeeId').value;
            const method = editId ? 'PUT' : 'POST';
            const url = API_URL + 'employees' + (editId ? '/' + editId : '');

            await fetch(url, {
                method: method, headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('empName').value,
                    phone_number: document.getElementById('empPhone').value,
                    task_notes: document.getElementById('empNotes').value,
                    trigger_time: triggerTime
                })
            });
            closeModal('employeeModal'); 
            document.getElementById('employeeForm').reset();
            document.getElementById('editEmployeeId').value = '';
            document.getElementById('employeeModalTitle').innerText = 'Create Member Reminder';
            fetchEmployees();
        }
        async function handleAlarmSubmit(e) {
            e.preventDefault();
            const mode = document.querySelector('input[name="alarmMode"]:checked').value;
            let triggerTime;
            if (mode === 'datetime') {
                const d = document.getElementById('alarmDate').value;
                const t = document.getElementById('alarmTime').value;
                if (!d || !t) return alert("Please select a date and time");
                triggerTime = `${d}T${t}:00`;
            } else {
                const now = new Date();
                now.setDate(now.getDate() + (parseInt(document.getElementById('alarmDays').value) || 0));
                now.setHours(now.getHours() + (parseInt(document.getElementById('alarmHours').value) || 0));
                now.setMinutes(now.getMinutes() + (parseInt(document.getElementById('alarmMins').value) || 0));
                now.setSeconds(now.getSeconds() + (parseInt(document.getElementById('alarmSecs').value) || 0));
                
                const format = n => String(n).padStart(2, '0');
                triggerTime = `${now.getFullYear()}-${format(now.getMonth()+1)}-${format(now.getDate())}T${format(now.getHours())}:${format(now.getMinutes())}:${format(now.getSeconds())}`;
            }

            const editId = document.getElementById('editAlarmId').value;
            const apiMethod = editId ? 'PUT' : 'POST';
            const url = API_URL + 'alarms' + (editId ? '/' + editId : '');

            await fetch(url, {
                method: apiMethod, headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    target_type: 'group',
                    target_id: document.getElementById('alarmTargetSelect').value,
                    task_notes: document.getElementById('alarmNotes').value,
                    trigger_time: triggerTime
                })
                
            });
            closeModal('alarmModal'); 
            document.getElementById('alarmForm').reset();
            document.getElementById('editAlarmId').value = '';
            document.getElementById('alarmModalTitle').innerText = 'Create Custom Reminder';
            fetchAlarms();
        }

        function editAlarm(id) {
            const a = alarms.find(x => x.id == id);
            if (!a) return;
            document.getElementById('editAlarmId').value = a.id;
            document.getElementById('alarmModalTitle').innerText = 'Edit Reminder';
            updateAlarmTargetSelect();
            document.getElementById('alarmTargetSelect').value = a.target_id;
            document.getElementById('alarmNotes').value = a.task_notes;
            
            document.querySelector('input[name="alarmMode"][value="datetime"]').checked = true;
            toggleAlarmMode();
            const dt = parseLocalStatusTime(a.trigger_time);
            const format = n => String(n).padStart(2, '0');
            document.getElementById('alarmDate').value = `${dt.getFullYear()}-${format(dt.getMonth() + 1)}-${format(dt.getDate())}`;
            document.getElementById('alarmTime').value = `${format(dt.getHours())}:${format(dt.getMinutes())}`;
            
            openModal('alarmModal');
        }

        async function deleteEmployee(id) { if(confirm("Delete member?")) { await fetch(API_URL + 'employees/' + id, {method: 'DELETE'}); fetchEmployees(); } }
        async function deleteAlarm(id) { if(confirm("Delete reminder?")) { await fetch(API_URL + 'alarms/' + id, {method: 'DELETE'}); fetchAlarms(); } }
        async function triggerAlarm(id) { if(confirm("Trigger now?")) { await fetch(API_URL + 'alarms/' + id + '/instant', {method: 'POST'}); fetchAlarms(); fetchEmployees(); } }

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
                if (!cb.checked) {
                    hidden.push(cb.value);
                }
            });
            
            await fetch(API_URL + 'waha/groups/visibility', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(hidden)
            });
            
            hidden_groups = hidden;
            updateAlarmTargetSelect();
            closeModal('visibilityModal');
            
            const statGroups = document.getElementById('stat-groups');
            if (statGroups) {
                const uniqueGroupsCount = new Set(alarms.map(a => a.target_id).filter(id => id)).size;
                statGroups.innerText = uniqueGroupsCount;
            }
        }

        window.onload = async () => {
            await fetchWahaGroups();
            await fetchEmployees();
            await fetchAlarms();
        };
    </script>
</body>
</html>
