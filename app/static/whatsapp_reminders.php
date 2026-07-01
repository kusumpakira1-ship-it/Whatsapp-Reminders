<?php
// ============================================================
// Sunfra Poultry - Whatsapp Reminders & Farm Automation
// Single-file unified backend and frontend
// ============================================================

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
    // Use IF NOT EXISTS to prevent overwriting
    $pdo->exec("CREATE TABLE IF NOT EXISTS wa_groups (
        id INTEGER PRIMARY KEY AUTO_INCREMENT,
        name VARCHAR(255) NOT NULL,
        whatsapp_group_id VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;");
} catch (PDOException $e) {
    // If it fails (e.g. SQLite doesn't support AUTO_INCREMENT), use SQLite syntax
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
        // Assume MySQL syntax if SQLite fails, it means we are on MySQL
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
    }
}

// 3. Simple REST API Router
if (isset($_GET['api'])) {
    header("Content-Type: application/json");
    $method = $_SERVER['REQUEST_METHOD'];
    $route = $_GET['api'];

    try {
        if ($route === 'groups' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM wa_groups");
            echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
        }
        elseif ($route === 'groups' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("INSERT INTO wa_groups (name, whatsapp_group_id) VALUES (?, ?)");
            $stmt->execute([$data['name'], $data['whatsapp_group_id']]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^groups\/(\d+)$/', $route, $matches) && $method === 'DELETE') {
            $pdo->prepare("DELETE FROM wa_groups WHERE id = ?")->execute([$matches[1]]);
            $pdo->prepare("DELETE FROM wa_employees WHERE group_id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'employees' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM wa_employees");
            echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
        }
        elseif ($route === 'employees' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("INSERT INTO wa_employees (name, phone_number, group_id, report_responsibility) VALUES (?, ?, ?, ?)");
            $stmt->execute([$data['name'], $data['phone_number'], $data['group_id'], $data['report_responsibility']]);
            echo json_encode(['success' => true]);
        }
        elseif (preg_match('/^employees\/(\d+)$/', $route, $matches) && $method === 'DELETE') {
            $pdo->prepare("DELETE FROM wa_employees WHERE id = ?")->execute([$matches[1]]);
            echo json_encode(['success' => true]);
        }
        elseif ($route === 'alarms' && $method === 'GET') {
            $stmt = $pdo->query("SELECT * FROM wa_alarms ORDER BY trigger_time ASC");
            $alarms = $stmt->fetchAll(PDO::FETCH_ASSOC);
            
            // Enrich with target names
            foreach ($alarms as &$alarm) {
                if ($alarm['target_type'] === 'employee') {
                    $stmt2 = $pdo->prepare("SELECT name FROM wa_employees WHERE id = ?");
                    $stmt2->execute([$alarm['target_id']]);
                    $alarm['target_name'] = $stmt2->fetchColumn() ?: 'Unknown Employee';
                } else {
                    $stmt2 = $pdo->prepare("SELECT name FROM wa_groups WHERE id = ?");
                    $stmt2->execute([$alarm['target_id']]);
                    $alarm['target_name'] = $stmt2->fetchColumn() ?: 'Unknown Group';
                }
            }
            echo json_encode($alarms);
        }
        elseif ($route === 'alarms' && $method === 'POST') {
            $data = json_decode(file_get_contents('php://input'), true);
            $stmt = $pdo->prepare("INSERT INTO wa_alarms (target_type, target_id, task_notes, trigger_time) VALUES (?, ?, ?, ?)");
            $stmt->execute([$data['target_type'], $data['target_id'], $data['task_notes'], $data['trigger_time']]);
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
        elseif ($route === 'waha/groups') {
            // Proxies request to WAHA
            $wahaUrl = 'http://waha:3000/api/default/groups';
            $ch = curl_init($wahaUrl);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_HTTPHEADER, ['X-Api-Key: 123']);
            curl_setopt($ch, CURLOPT_TIMEOUT, 5);
            $response = curl_exec($ch);
            if(curl_errno($ch)){
                // Return mock data if WAHA is unreachable (for local testing/Hostinger isolated env)
                echo json_encode([
                    'status' => 'success', 
                    'groups' => [
                        ['id' => '120363048576912345@g.us', 'name' => 'Demo Farm Supervisors'],
                        ['id' => '120363048576954321@g.us', 'name' => 'Demo Egg Collectors']
                    ]
                ]);
            } else {
                $data = json_decode($response, true);
                $formatted = [];
                // WAHA returns either list or dict based on version
                if (is_array($data)) {
                    foreach ($data as $k => $v) {
                        if (is_array($v) && isset($v['id'])) {
                            $formatted[] = ['id' => $v['id'], 'name' => $v['subject'] ?? $v['name'] ?? 'Unnamed'];
                        } else if (is_string($k) && is_array($v)) {
                            $formatted[] = ['id' => $k, 'name' => $v['subject'] ?? $v['name'] ?? 'Unnamed'];
                        }
                    }
                }
                echo json_encode(['status' => 'success', 'groups' => $formatted]);
            }
            curl_close($ch);
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
            --bg-start: #0f172a;
            --bg-end: #1e293b;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --primary-color: #3b82f6;
            --primary-hover: #2563eb;
            --danger-color: #ef4444;
            --success-color: #10b981;
            --glass-bg: rgba(15, 23, 42, 0.7);
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
        .stat-value { font-size: 3rem; font-weight: 700; color: #fff; text-shadow: 0 0 20px rgba(255,255,255,0.2); }

        /* Tables */
        .table-card { padding: 0; overflow: hidden; }
        .data-table { width: 100%; border-collapse: collapse; }
        .data-table th, .data-table td { padding: 1.2rem 1.5rem; text-align: left; border-bottom: 1px solid var(--card-border); }
        
        .data-table th {
            background: rgba(0,0,0,0.3);
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .data-table tbody tr { transition: background-color 0.2s; }
        .data-table tbody tr:hover { background: rgba(255,255,255,0.02); }

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

        .btn-secondary { background: transparent; color: var(--text-secondary); border: 1px solid var(--card-border); }
        .btn-secondary:hover { color: white; border-color: rgba(255,255,255,0.3); background: rgba(255,255,255,0.05); }

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
        .modal-content h3 { margin-bottom: 2rem; font-size: 1.4rem; color: #fff; }

        .form-group { margin-bottom: 1.5rem; }
        .form-group label { display: block; margin-bottom: 0.6rem; color: var(--text-secondary); font-size: 0.95rem; }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 0.85rem 1rem;
            border-radius: 8px;
            border: 1px solid var(--card-border);
            background: rgba(0,0,0,0.2);
            color: white;
            font-family: inherit;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
            background: rgba(0,0,0,0.4);
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
        .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59,130,246,0.3); }
        .badge-green { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16,185,129,0.3); }
        .badge-orange { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.3); }
    </style>
</head>
<body>
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="logo">Farm Auto</div>
            <nav>
                <a href="#" class="nav-item active" data-target="dashboard">Dashboard</a>
                <a href="#" class="nav-item" data-target="groups">WhatsApp Groups</a>
                <a href="#" class="nav-item" data-target="employees">Employees</a>
                <a href="#" class="nav-item" data-target="alarms">Alarms & Tasks</a>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <header>
                <h1>Management Dashboard</h1>
                <div class="user-profile">Admin</div>
            </header>

            <!-- Dashboard View -->
            <section id="dashboard" class="view active">
                <div class="card stat-card">
                    <h3>Total Groups</h3>
                    <div class="stat-value" id="stat-groups">0</div>
                </div>
                <div class="card stat-card">
                    <h3>Total Employees</h3>
                    <div class="stat-value" id="stat-employees">0</div>
                </div>
            </section>

            <!-- Groups View -->
            <section id="groups" class="view">
                <div class="header-row">
                    <h2>Groups Management</h2>
                    <button class="btn btn-primary" onclick="openModal('groupModal')">+ Add Group</button>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Group Name</th>
                                <th>WhatsApp Group ID</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="groups-tbody"></tbody>
                    </table>
                </div>
            </section>

            <!-- Employees View -->
            <section id="employees" class="view">
                <div class="header-row">
                    <h2>Employees Management</h2>
                    <button class="btn btn-primary" onclick="openModal('employeeModal')">+ Add Employee</button>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Name</th>
                                <th>Phone</th>
                                <th>Group</th>
                                <th>Responsibility</th>
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
                    <h2>Alarms & Tasks</h2>
                    <button class="btn btn-primary" onclick="openModal('alarmModal')">+ Create Alarm</button>
                </div>
                <div class="card table-card">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Target</th>
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

    <!-- Group Modal -->
    <div id="groupModal" class="modal">
        <div class="modal-content card">
            <h3>Add New Group</h3>
            <form id="groupForm" onsubmit="handleGroupSubmit(event)">
                <div class="form-group">
                    <label>Select WhatsApp Group</label>
                    <select id="groupWhatsappId" required>
                        <option value="">Loading groups from WhatsApp...</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('groupModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Group</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Employee Modal -->
    <div id="employeeModal" class="modal">
        <div class="modal-content card">
            <h3>Add New Employee</h3>
            <form id="employeeForm" onsubmit="handleEmployeeSubmit(event)">
                <div class="form-group">
                    <label>Employee Name</label>
                    <input type="text" id="empName" required placeholder="e.g., John Doe">
                </div>
                <div class="form-group">
                    <label>Phone Number</label>
                    <input type="text" id="empPhone" required placeholder="e.g., 919876543210">
                </div>
                <div class="form-group">
                    <label>Assign to Group</label>
                    <select id="empGroup" required>
                        <option value="">Select Group...</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Report Responsibility</label>
                    <select id="empReport" required>
                        <option value="egg_collection">Egg Collection (A Report)</option>
                        <option value="feed">Feed (B Report)</option>
                        <option value="expense">Expenses</option>
                        <option value="sales">Sales</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('employeeModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Employee</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Alarm Modal -->
    <div id="alarmModal" class="modal">
        <div class="modal-content card">
            <h3>Create Custom Alarm</h3>
            <form id="alarmForm" onsubmit="handleAlarmSubmit(event)">
                <div class="form-group">
                    <label>Target Type</label>
                    <select id="alarmTargetType" onchange="updateAlarmTargetSelect()" required>
                        <option value="employee">Employee</option>
                        <option value="group">Group</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Select Target</label>
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
                    <input type="datetime-local" id="alarmDatetime" step="1">
                </div>
                
                <div id="alarmTimerSection" class="form-group" style="display:none;">
                    <label>Trigger After:</label>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <input type="number" id="alarmDays" min="0" value="0" style="width: 60px;"> <span style="font-size:0.8rem">D</span>
                        <input type="number" id="alarmHours" min="0" max="23" value="0" style="width: 60px;"> <span style="font-size:0.8rem">H</span>
                        <input type="number" id="alarmMins" min="0" max="59" value="0" style="width: 60px;"> <span style="font-size:0.8rem">M</span>
                        <input type="number" id="alarmSecs" min="0" max="59" value="0" style="width: 60px;"> <span style="font-size:0.8rem">S</span>
                    </div>
                </div>

                <div class="modal-actions">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('alarmModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Alarm</button>
                </div>
            </form>
        </div>
    </div>

    <script>
        const API_URL = '?api=';
        let groups = [];
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

        async function fetchGroups() {
            const res = await fetch(API_URL + 'groups');
            groups = await res.json();
            const tbody = document.getElementById('groups-tbody');
            tbody.innerHTML = '';
            groups.forEach(g => {
                tbody.innerHTML += `<tr>
                    <td>#${g.id}</td>
                    <td><strong>${g.name}</strong></td>
                    <td style="color:var(--text-secondary)">${g.whatsapp_group_id}</td>
                    <td><button class="btn btn-danger" onclick="deleteGroup(${g.id})">Delete</button></td>
                </tr>`;
            });
            document.getElementById('stat-groups').innerText = groups.length;
            updateGroupSelect();
        }

        async function fetchEmployees() {
            const res = await fetch(API_URL + 'employees');
            employees = await res.json();
            const tbody = document.getElementById('employees-tbody');
            tbody.innerHTML = '';
            employees.forEach(e => {
                const gName = groups.find(g => g.id == e.group_id)?.name || 'Unknown';
                tbody.innerHTML += `<tr>
                    <td>#${e.id}</td>
                    <td><strong>${e.name}</strong><br><small style="color:var(--text-secondary)">${e.phone_number}</small></td>
                    <td style="color:var(--text-secondary)">${e.phone_number}</td>
                    <td><span class="badge badge-blue">${gName}</span></td>
                    <td>${e.report_responsibility}</td>
                    <td><button class="btn btn-danger" onclick="deleteEmployee(${e.id})">Delete</button></td>
                </tr>`;
            });
            document.getElementById('stat-employees').innerText = employees.length;
        }

        async function fetchAlarms() {
            const res = await fetch(API_URL + 'alarms');
            alarms = await res.json();
            const tbody = document.getElementById('alarms-tbody');
            tbody.innerHTML = '';
            alarms.forEach(a => {
                const badgeClass = a.status === 'sent' ? 'badge-green' : (a.status === 'pending' ? 'badge-orange' : '');
                const targetText = `<span style="text-transform:capitalize; color:var(--text-secondary)">${a.target_type}</span>: <strong>${a.target_name}</strong>`;
                const btn = a.status === 'pending' ? `<button class="btn btn-primary" onclick="triggerAlarm(${a.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Trigger Now</button>` : '';
                tbody.innerHTML += `<tr>
                    <td>${targetText}</td>
                    <td>${a.task_notes}</td>
                    <td>${new Date(a.trigger_time).toLocaleString()}</td>
                    <td><span class="badge ${badgeClass}">${a.status}</span></td>
                    <td>${btn} <button class="btn btn-danger" onclick="deleteAlarm(${a.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Delete</button></td>
                </tr>`;
            });
        }

        async function fetchWahaGroups() {
            const select = document.getElementById('groupWhatsappId');
            try {
                const res = await fetch(API_URL + 'waha/groups');
                const data = await res.json();
                if (data.status === 'success' && data.groups.length > 0) {
                    select.innerHTML = '<option value="">Select a WhatsApp Group...</option>';
                    data.groups.forEach(g => {
                        select.innerHTML += `<option value="${g.id}">${g.name}</option>`;
                    });
                } else {
                    select.innerHTML = '<option value="">Failed to load groups. Check WAHA connection.</option>';
                }
            } catch (err) {
                select.innerHTML = '<option value="">Error fetching groups</option>';
            }
        }

        function updateGroupSelect() {
            const select = document.getElementById('empGroup');
            select.innerHTML = '<option value="">Select Group...</option>';
            groups.forEach(g => { select.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
        }

        function updateAlarmTargetSelect() {
            const type = document.getElementById('alarmTargetType').value;
            const select = document.getElementById('alarmTargetSelect');
            select.innerHTML = '';
            const list = type === 'employee' ? employees : groups;
            list.forEach(i => select.innerHTML += `<option value="${i.id}">${i.name}</option>`);
        }

        function toggleAlarmMode() {
            const mode = document.querySelector('input[name="alarmMode"]:checked').value;
            document.getElementById('alarmDatetimeSection').style.display = mode === 'datetime' ? 'block' : 'none';
            document.getElementById('alarmTimerSection').style.display = mode === 'timer' ? 'block' : 'none';
        }

        async function handleGroupSubmit(e) {
            e.preventDefault();
            const select = document.getElementById('groupWhatsappId');
            if(!select.value) return alert("Select a group");
            await fetch(API_URL + 'groups', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ name: select.options[select.selectedIndex].text, whatsapp_group_id: select.value })
            });
            closeModal('groupModal'); document.getElementById('groupForm').reset();
            fetchGroups();
        }

        async function handleEmployeeSubmit(e) {
            e.preventDefault();
            await fetch(API_URL + 'employees', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('empName').value,
                    phone_number: document.getElementById('empPhone').value,
                    group_id: document.getElementById('empGroup').value,
                    report_responsibility: document.getElementById('empReport').value
                })
            });
            closeModal('employeeModal'); document.getElementById('employeeForm').reset();
            fetchEmployees();
        }

        async function handleAlarmSubmit(e) {
            e.preventDefault();
            const mode = document.querySelector('input[name="alarmMode"]:checked').value;
            let triggerTime;
            if (mode === 'datetime') {
                triggerTime = document.getElementById('alarmDatetime').value;
                if (!triggerTime) return alert("Please select date and time");
            } else {
                const now = new Date();
                now.setDate(now.getDate() + (parseInt(document.getElementById('alarmDays').value) || 0));
                now.setHours(now.getHours() + (parseInt(document.getElementById('alarmHours').value) || 0));
                now.setMinutes(now.getMinutes() + (parseInt(document.getElementById('alarmMins').value) || 0));
                now.setSeconds(now.getSeconds() + (parseInt(document.getElementById('alarmSecs').value) || 0));
                
                const format = n => String(n).padStart(2, '0');
                triggerTime = `${now.getFullYear()}-${format(now.getMonth()+1)}-${format(now.getDate())}T${format(now.getHours())}:${format(now.getMinutes())}:${format(now.getSeconds())}`;
            }

            await fetch(API_URL + 'alarms', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    target_type: document.getElementById('alarmTargetType').value,
                    target_id: document.getElementById('alarmTargetSelect').value,
                    task_notes: document.getElementById('alarmNotes').value,
                    trigger_time: triggerTime
                })
            });
            closeModal('alarmModal'); document.getElementById('alarmForm').reset();
            fetchAlarms();
        }

        async function deleteGroup(id) { if(confirm("Delete group and its employees?")) { await fetch(API_URL + 'groups/' + id, {method: 'DELETE'}); fetchGroups(); fetchEmployees(); } }
        async function deleteEmployee(id) { if(confirm("Delete employee?")) { await fetch(API_URL + 'employees/' + id, {method: 'DELETE'}); fetchEmployees(); } }
        async function deleteAlarm(id) { if(confirm("Delete alarm?")) { await fetch(API_URL + 'alarms/' + id, {method: 'DELETE'}); fetchAlarms(); } }
        async function triggerAlarm(id) { if(confirm("Trigger now?")) { await fetch(API_URL + 'alarms/' + id + '/trigger', {method: 'POST'}); fetchAlarms(); } }

        window.onload = async () => {
            await fetchGroups();
            await fetchEmployees();
            await fetchWahaGroups();
            await fetchAlarms();
        };
    </script>
</body>
</html>
