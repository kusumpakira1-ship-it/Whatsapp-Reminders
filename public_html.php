<?php
// ─── Timezone: Asia/Kolkata ───────────────────────────────────────────────
date_default_timezone_set('Asia/Kolkata');

// Helper PDO Connection
function getDb() {
    static $pdo = null;
    if ($pdo !== null) return $pdo;
    $dbName = 'u632391467_kusumpakira';
    $user   = 'u632391467_kusumpakira';
    $pass   = 'Kusum@2026Bb!';
    $hosts  = ['localhost', '127.0.0.1', '145.223.17.70'];
    foreach ($hosts as $host) {
        try {
            $pdo = new PDO("mysql:host={$host};dbname={$dbName};charset=utf8mb4", $user, $pass, [
                PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
                PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
                PDO::ATTR_TIMEOUT => 2
            ]);
            if ($pdo) return $pdo;
        } catch (Throwable $e) {}
    }
    // Fallback SQLite
    $sqlitePath = __DIR__ . '/mac_water_monitoring.sqlite';
    $pdo = new PDO("sqlite:" . $sqlitePath);
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    $pdo->exec("CREATE TABLE IF NOT EXISTS mac_devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mac_address TEXT UNIQUE,
        device_name TEXT,
        location TEXT,
        water_level INTEGER DEFAULT 50,
        power_status TEXT DEFAULT 'ON',
        last_seen DATETIME,
        created_at DATETIME
    )");
    return $pdo;
}

// REST API & Ingestion Handling
$jsonInput = json_decode(file_get_contents('php://input'), true) ?? [];
$input = array_merge($_GET, $_POST, $jsonInput);

$action = strtolower(trim($input['api'] ?? $input['action'] ?? ''));

if (!empty($action) || isset($input['mac_address']) || isset($input['mac'])) {
    header('Content-Type: application/json; charset=utf-8');
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
        http_response_code(200);
        exit;
    }

    $pdo = getDb();

    if ($action === 'get_devices' && $_SERVER['REQUEST_METHOD'] === 'GET' && !isset($input['mac_address']) && !isset($input['mac'])) {
        try {
            $stmt = $pdo->query("SELECT id, mac_address, location AS device_name, 'Level_sensor' AS location, water_level, status AS power_status, timestamp AS last_seen FROM device_readings ORDER BY timestamp DESC LIMIT 50");
            $devices = $stmt->fetchAll();
            
            if (!$devices) {
                $stmt = $pdo->query("SELECT id, mac_address, name AS device_name, location, water_level, status AS power_status, COALESCE(updated_at, created_at) AS last_seen FROM mac_devices ORDER BY id DESC");
                $devices = $stmt->fetchAll();
            }
            
            echo json_encode(['status' => 'success', 'data' => $devices, 'devices' => $devices, 'success' => true]);
        } catch (Throwable $e) {
            echo json_encode(['status' => 'error', 'message' => $e->getMessage(), 'success' => false]);
        }
        exit;
    }
    elseif ($action === 'add_device') {
        $mac = strtoupper(trim($input['mac_address'] ?? $input['mac'] ?? ''));
        $name = trim($input['device_name'] ?? $input['name'] ?? '');
        $loc = trim($input['location'] ?? 'Level_sensor');
        $water = intval($input['water_level'] ?? 50);
        $power = strtoupper(trim($input['power_status'] ?? $input['status'] ?? 'ON'));
        $now = date('Y-m-d H:i:s');

        try {
            $stmt = $pdo->prepare("INSERT INTO mac_devices (mac_address, device_name, location, water_level, power_status, last_seen, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)");
            $stmt->execute([$mac, $name, $loc, $water, $power, $now, $now]);
            echo json_encode(['status' => 'success', 'message' => 'Device added successfully']);
        } catch (Throwable $e) {
            echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
        }
        exit;
    }
    elseif ($action === 'update_device') {
        $mac = strtoupper(trim($input['mac_address'] ?? $input['mac'] ?? ''));
        $name = trim($input['device_name'] ?? $input['name'] ?? 'Level_sensor');
        $loc = trim($input['location'] ?? 'Level_sensor');
        $water = intval($input['water_level'] ?? 50);
        $power = strtoupper(trim($input['power_status'] ?? $input['status'] ?? 'ON'));
        $now = date('Y-m-d H:i:s');

        try {
            $stmt = $pdo->prepare("INSERT INTO device_readings (mac_address, location, water_level, status, timestamp) VALUES (?, ?, ?, ?, ?)");
            $stmt->execute([$mac, $name, $water, $power, $now]);

            $stmt2 = $pdo->prepare("UPDATE mac_devices SET water_level = ?, status = ?, name = ?, location = ?, updated_at = ? WHERE mac_address = ?");
            $stmt2->execute([$water, $power, $name, $loc, $now, $mac]);

            echo json_encode(['status' => 'success', 'message' => 'Device updated successfully']);
        } catch (Throwable $e) {
            echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
        }
        exit;
    }
    elseif ($action === 'delete_device') {
        $mac = strtoupper(trim($input['mac_address'] ?? $input['mac'] ?? ''));
        try {
            $stmt = $pdo->prepare("DELETE FROM mac_devices WHERE mac_address = ?");
            $stmt->execute([$mac]);
            $stmt2 = $pdo->prepare("DELETE FROM device_readings WHERE mac_address = ?");
            $stmt2->execute([$mac]);
            echo json_encode(['status' => 'success', 'message' => 'Device deleted successfully']);
        } catch (Throwable $e) {
            echo json_encode(['status' => 'error', 'message' => $e->getMessage()]);
        }
        exit;
    }
    elseif ($action === 'telemetry' || $action === 'post_reading' || $action === 'post_weight' || isset($input['mac_address']) || isset($input['mac'])) {
        $mac = strtoupper(trim($input['mac_address'] ?? $input['mac'] ?? ''));
        $location = trim($input['location'] ?? $input['device_name'] ?? 'Level_sensor');
        $waterRaw = $input['water_level'] ?? $input['level'] ?? $input['weight_value'] ?? $input['weight_kg'] ?? 50;
        $water = intval($waterRaw);
        $status = strtoupper(trim($input['power_status'] ?? $input['status'] ?? 'ON'));
        $now = date('Y-m-d H:i:s');

        if (!empty($mac)) {
            // Canonical location name mapping by MAC address
            if ($mac === '40-91-51-C8-0C-C8') {
                $location = 'Kadubeesanahalli';
            } elseif ($mac === 'C4-4F-33-24-7C-59') {
                $location = 'Spice garden';
            }
            // Constrain discrete water levels: 0, 25, 50, 75, 100
            $allowedLevels = [0, 25, 50, 75, 100];
            $closest = 50;
            $minDiff = 999;
            foreach ($allowedLevels as $lvl) {
                $diff = abs($lvl - $water);
                if ($diff < $minDiff) {
                    $minDiff = $diff;
                    $closest = $lvl;
                }
            }
            $water = $closest;

            try {
                $stmt = $pdo->prepare("INSERT INTO device_readings (mac_address, location, water_level, status, timestamp) VALUES (?, ?, ?, ?, ?)");
                $stmt->execute([$mac, $location, $water, $status, $now]);

                $stmt2 = $pdo->prepare("UPDATE mac_devices SET water_level = ?, status = ?, updated_at = ? WHERE mac_address = ?");
                $stmt2->execute([$water, $status, $now, $mac]);

                echo json_encode([
                    'status' => 'success',
                    'success' => true,
                    'message' => 'Telemetry record saved',
                    'data' => ['mac' => $mac, 'location' => $location, 'level' => $water, 'status' => $status, 'timestamp' => $now]
                ]);
            } catch (Throwable $e) {
                echo json_encode(['status' => 'error', 'success' => false, 'message' => $e->getMessage()]);
            }
            exit;
        }
    }
    elseif ($action === 'simulate' && $_SERVER['REQUEST_METHOD'] === 'POST') {
        $now = date('Y-m-d H:i:s');
        $levels = [0, 25, 50, 75, 100];
        try {
            $devices = [['C4-4F-33-24-7C-59', 'Spice garden'], ['40-91-51-C8-0C-C8', 'Kadubeesanahalli']];
            foreach ($devices as $dev) {
                $mac = $dev[0];
                $loc = $dev[1];
                $randLevel = $levels[array_rand($levels)];
                $stmt = $pdo->prepare("INSERT INTO device_readings (mac_address, location, water_level, status, timestamp) VALUES (?, ?, ?, ?, ?)");
                $stmt->execute([$mac, $loc, $randLevel, 'ON', $now]);
                $stmt2 = $pdo->prepare("UPDATE mac_devices SET water_level = ?, status = 'ON', updated_at = ? WHERE mac_address = ?");
                $stmt2->execute([$randLevel, $now, $mac]);
            }
        } catch (Throwable $e) {}
        echo json_encode(['status' => 'success', 'message' => 'Simulated discrete telemetry successfully']);
        exit;
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sunfra Water & MAC Monitoring</title>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f3f6fc;
    --card: #ffffff;
    --border: #e2e8f0;
    --primary: #3b82f6;
    --primary-hover: #2563eb;
    --text-main: #1e293b;
    --text-muted: #64748b;
    --green: #22c55e;
    --red: #ef4444;
    --yellow: #f59e0b;
    --shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.03);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--text-main);
    padding: 2rem 1.5rem;
    min-height: 100vh;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  /* Header Card */
  .header-card {
    background: var(--card);
    border-radius: 16px;
    padding: 1.25rem 1.75rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
  }

  .brand {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .brand-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #3b82f6, #1d4ed8);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.5rem;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
  }

  .brand-info h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: #0f172a;
  }

  .brand-info p {
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 2px;
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .time-badge {
    background: #f8fafc;
    border: 1px solid var(--border);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    color: var(--text-main);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .dot-online {
    width: 8px;
    height: 8px;
    background-color: var(--green);
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 8px var(--green);
  }

  .btn-add {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.88rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
    transition: all 0.2s;
  }

  .btn-add:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(59, 130, 246, 0.35);
  }

  /* Section Card */
  .card {
    background: var(--card);
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
  }

  .card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
  }

  .card-subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 400;
  }

  /* Filters */
  .filter-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1.25rem;
    margin-bottom: 1.25rem;
  }

  .field-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .field-group label {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .form-control {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.88rem;
    color: var(--text-main);
    outline: none;
    transition: border-color 0.2s;
    width: 100%;
  }

  .form-control:focus {
    border-color: var(--primary);
    background: #ffffff;
  }

  .filter-actions {
    display: flex;
    gap: 10px;
  }

  .btn-filter {
    background: #3b82f6;
    color: white;
    border: none;
    padding: 8px 18px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .btn-reset {
    background: #ffffff;
    border: 1px solid var(--border);
    color: var(--text-main);
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.85rem;
    cursor: pointer;
  }

  /* Metric Cards */
  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1.25rem;
  }

  .metric-card {
    background: var(--card);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    border: 1px solid var(--border);
    box-shadow: var(--shadow);
    position: relative;
    overflow: hidden;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .metric-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
  }

  .metric-card.blue::before { background: var(--primary); }
  .metric-card.green::before { background: var(--green); }
  .metric-card.red::before { background: var(--red); }
  .metric-card.orange::before { background: var(--yellow); }

  .metric-info h4 {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }

  .metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: #0f172a;
  }

  .metric-icon {
    font-size: 1.75rem;
    opacity: 0.8;
  }

  /* Table */
  .table-responsive {
    overflow-x: auto;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
    text-align: left;
    font-size: 0.88rem;
  }

  .data-table th {
    background: #f8fafc;
    color: var(--text-muted);
    font-weight: 700;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
  }

  .data-table td {
    padding: 16px;
    border-bottom: 1px solid var(--border);
    vertical-align: middle;
  }

  .mac-badge {
    background: #eff6ff;
    color: #2563eb;
    padding: 4px 10px;
    border-radius: 6px;
    font-family: monospace;
    font-weight: 600;
    font-size: 0.85rem;
    border: 1px solid #bfdbfe;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .location-cell {
    font-weight: 600;
    color: var(--text-main);
  }

  .location-cell span {
    font-weight: 400;
    color: var(--text-muted);
    font-size: 0.8rem;
    display: block;
  }

  .progress-bar-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 180px;
  }

  .progress-bar {
    flex: 1;
    height: 8px;
    background: #e2e8f0;
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #f59e0b, #22c55e);
    border-radius: 4px;
  }

  .badge-status {
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.75rem;
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .badge-on {
    background: #dcfce7;
    color: #15803d;
    border: 1px solid #86efac;
  }

  .badge-off {
    background: #fee2e2;
    color: #991b1b;
    border: 1px solid #fca5a5;
  }

  .btn-action {
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid var(--border);
    background: #ffffff;
    cursor: pointer;
    margin-right: 4px;
  }

  .btn-action.edit { color: var(--primary); border-color: #bfdbfe; background: #eff6ff; }
  .btn-action.delete { color: var(--red); border-color: #fca5a5; background: #fff5f5; }

  /* Modal */
  .modal-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.5);
    backdrop-filter: blur(4px);
    z-index: 999;
    align-items: center;
    justify-content: center;
  }

  .modal-overlay.active { display: flex; }

  .modal {
    background: white;
    border-radius: 20px;
    padding: 2rem;
    width: 100%;
    max-width: 480px;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .modal-header h3 { font-size: 1.2rem; font-weight: 700; }
  .close-modal { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-muted); }
</style>
</head>
<body>

<div class="container">

  <!-- Header Card -->
  <div class="header-card">
    <div class="brand">
      <div class="brand-icon">💧</div>
      <div class="brand-info">
        <h1>Sunfra Water & MAC Monitoring</h1>
        <p>Real-Time MAC Device Telemetry & Automatic WhatsApp Alert System</p>
      </div>
    </div>
    <div class="header-right">
      <div class="time-badge">
        <span class="dot-online"></span>
        <span id="live-clock"><?php echo date('d/m/Y, H:i:s'); ?></span>
      </div>
      <button class="btn-add" onclick="openAddModal()">＋ Add Device</button>
    </div>
  </div>

  <!-- Filters Card -->
  <div class="card">
    <div class="card-title">
      <span>⚙ Customization & Monitoring Filters</span>
      <span class="card-subtitle">Filter by custom Date/Time range or view a particular MAC Address</span>
    </div>
    <div class="filter-grid">
      <div class="field-group">
        <label>Filter Date & Time (From)</label>
        <input type="datetime-local" class="form-control" id="filter-from">
      </div>
      <div class="field-group">
        <label>Filter Date & Time (To)</label>
        <input type="datetime-local" class="form-control" id="filter-to">
      </div>
      <div class="field-group">
        <label>MAC Address Filter</label>
        <select class="form-control" id="filter-mac">
          <option value="">All MAC Addresses</option>
          <option value="C4-4F-33-24-7C-59">C4-4F-33-24-7C-59 (Spice garden)</option>
          <option value="40-91-51-C8-0C-C8">40-91-51-C8-0C-C8 (Kadubeesanahalli)</option>
        </select>
      </div>
    </div>
    <div class="filter-actions">
      <button class="btn-filter" onclick="applyFilters()">🔍 Apply Filter</button>
      <button class="btn-reset" onclick="resetFilters()">🔄 Reset</button>
    </div>
  </div>

  <!-- Metrics Grid -->
  <div class="metrics-grid">
    <div class="metric-card blue">
      <div class="metric-info">
        <h4>Total Monitored Devices</h4>
        <div class="metric-value" id="stat-total">0</div>
      </div>
      <div class="metric-icon">💻</div>
    </div>
    <div class="metric-card green">
      <div class="metric-info">
        <h4>Devices Power ON</h4>
        <div class="metric-value" id="stat-on">0</div>
      </div>
      <div class="metric-icon">⚡</div>
    </div>
    <div class="metric-card red">
      <div class="metric-info">
        <h4>Devices OFF Alerts</h4>
        <div class="metric-value" id="stat-off">0</div>
      </div>
      <div class="metric-icon">🔴</div>
    </div>
    <div class="metric-card orange">
      <div class="metric-info">
        <h4>Water Level ≤ 25% Alerts</h4>
        <div class="metric-value" id="stat-low">0</div>
      </div>
      <div class="metric-icon">⚠️</div>
    </div>
  </div>

  <!-- Telemetry Table Card -->
  <div class="card">
    <div class="card-title">
      <span>📊 MAC Devices & Telemetry Records</span>
      <div>
        <button class="btn-reset" onclick="simulateTelemetry()" style="margin-right: 10px;">⚡ Simulate Telemetry Update API</button>
        <span class="card-subtitle">MAC Format: XX-XX-XX-XX-XX-XX</span>
      </div>
    </div>
    <div class="table-responsive">
      <table class="data-table">
        <thead>
          <tr>
            <th>Last Telemetry Time</th>
            <th>MAC Address</th>
            <th>Device & Location</th>
            <th>Water Level (%)</th>
            <th>Power Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody id="devices-tbody">
          <!-- Dynamic Telemetry Rows -->
        </tbody>
      </table>
    </div>
  </div>

</div>

<!-- Add Device Modal -->
<div class="modal-overlay" id="addModal">
  <div class="modal">
    <div class="modal-header">
      <h3>Add Monitored MAC Device</h3>
      <button class="close-modal" onclick="closeAddModal()">&times;</button>
    </div>
    <form id="addDeviceForm" onsubmit="saveDevice(event)">
      <div class="field-group" style="margin-bottom: 1rem;">
        <label>MAC Address</label>
        <input type="text" class="form-control" id="new-mac" placeholder="e.g. C4-4F-33-24-7C-59" required>
      </div>
      <div class="field-group" style="margin-bottom: 1rem;">
        <label>Device / Location Name</label>
        <input type="text" class="form-control" id="new-name" placeholder="e.g. Spice garden" required>
      </div>
      <div class="field-group" style="margin-bottom: 1rem;">
        <label>Sensor Type / Sub-Location</label>
        <input type="text" class="form-control" id="new-loc" value="Level_sensor" required>
      </div>
      <div class="field-group" style="margin-bottom: 1.5rem;">
        <label>Current Water Level (%)</label>
        <input type="number" class="form-control" id="new-water" value="50" min="0" max="100">
      </div>
      <button type="submit" class="btn-add" style="width: 100%; justify-content: center;">Save Device</button>
    </form>
  </div>
</div>

<!-- Edit Device Modal -->
<div class="modal-overlay" id="editModal">
  <div class="modal">
    <div class="modal-header">
      <h3>Edit Monitored MAC Device</h3>
      <button class="close-modal" onclick="closeEditModal()">&times;</button>
    </div>
    <form id="editDeviceForm" onsubmit="updateDevice(event)">
      <input type="hidden" id="edit-mac">
      <div class="field-group" style="margin-bottom: 1rem;">
        <label>MAC Address</label>
        <input type="text" class="form-control" id="edit-mac-display" readonly style="background:#f1f5f9; color:#64748b;">
      </div>
      <div class="field-group" style="margin-bottom: 1rem;">
        <label>Device / Location Name</label>
        <input type="text" class="form-control" id="edit-name" required>
      </div>
      <div class="field-group" style="margin-bottom: 1rem;">
        <label>Current Water Level (%)</label>
        <select class="form-control" id="edit-water">
          <option value="0">0% (Empty Alert)</option>
          <option value="25">25% (Critical Low Alert)</option>
          <option value="50">50% (Medium Level)</option>
          <option value="75">75% (Good Level)</option>
          <option value="100">100% (Full Level)</option>
        </select>
      </div>
      <div class="field-group" style="margin-bottom: 1.5rem;">
        <label>Power Status</label>
        <select class="form-control" id="edit-status">
          <option value="ON">⚡ ON</option>
          <option value="OFF">🔴 OFF</option>
        </select>
      </div>
      <button type="submit" class="btn-add" style="width: 100%; justify-content: center;">Save Changes</button>
    </form>
  </div>
</div>

<script>
  function updateClock() {
    const now = new Date();
    const d = String(now.getDate()).padStart(2, '0');
    const m = String(now.getMonth() + 1).padStart(2, '0');
    const y = now.getFullYear();
    const h = String(now.getHours()).padStart(2, '0');
    const min = String(now.getMinutes()).padStart(2, '0');
    const s = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('live-clock').innerText = `${d}/${m}/${y}, ${h}:${min}:${s}`;
  }
  setInterval(updateClock, 1000);

  let devicesData = [];

  async function loadDevices() {
    try {
      const res = await fetch('public_html.php?api=get_devices');
      const json = await res.json();
      if ((json.status === 'success' || json.success) && json.data && json.data.length > 0) {
        const map = new Map();
        json.data.forEach(item => {
          if (!map.has(item.mac_address)) {
            map.set(item.mac_address, item);
          }
        });
        devicesData = Array.from(map.values());
      }
    } catch(e) {}
    renderDevices();
  }

  function renderDevices(filterMac = '') {
    const tbody = document.getElementById('devices-tbody');
    tbody.innerHTML = '';
    let filtered = devicesData;
    if (filterMac) {
      filtered = devicesData.filter(d => d.mac_address === filterMac);
    }

    let onCount = 0;
    let offCount = 0;
    let lowCount = 0;

    filtered.forEach(d => {
      const isPowerOn = (d.power_status || 'ON').toUpperCase() === 'ON';
      if (isPowerOn) onCount++; else offCount++;
      if (parseInt(d.water_level || 0) <= 25) lowCount++;

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td style="color: var(--text-muted); font-size: 0.82rem;">${d.last_seen || '<?php echo date('Y-m-d H:i:s'); ?>'}</td>
        <td><span class="mac-badge">💻 ${d.mac_address}</span></td>
        <td class="location-cell">📍 ${d.device_name} <span>${d.location || 'Level_sensor'}</span></td>
        <td>
          <div class="progress-bar-wrap">
            <span style="font-size:0.78rem; color:var(--text-muted); font-weight:600;">Water Level</span>
            <div class="progress-bar"><div class="progress-fill" style="width: ${d.water_level}%;"></div></div>
            <span style="font-weight:700; color:#2563eb; font-size:0.82rem;">${d.water_level}%</span>
          </div>
        </td>
        <td>
          <span class="badge-status ${isPowerOn ? 'badge-on' : 'badge-off'}">
            ${isPowerOn ? '⚡ ON' : '🔴 OFF'}
          </span>
        </td>
        <td>
          <button class="btn-action edit" onclick="openEditModal('${d.mac_address}', '${(d.device_name||'').replace(/'/g, "\\'")}', '${d.water_level}', '${d.power_status}')">✏️ Edit</button>
          <button class="btn-action delete" onclick="deleteDevice('${d.mac_address}')">🗑️ Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    document.getElementById('stat-total').innerText = filtered.length;
    document.getElementById('stat-on').innerText = onCount;
    document.getElementById('stat-off').innerText = offCount;
    document.getElementById('stat-low').innerText = lowCount;
  }

  function openAddModal() { document.getElementById('addModal').classList.add('active'); }
  function closeAddModal() { document.getElementById('addModal').classList.remove('active'); }

  function openEditModal(mac, name, water, status) {
    document.getElementById('edit-mac').value = mac;
    document.getElementById('edit-mac-display').value = mac;
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-water').value = water;
    document.getElementById('edit-status').value = status || 'ON';
    document.getElementById('editModal').classList.add('active');
  }

  function closeEditModal() {
    document.getElementById('editModal').classList.remove('active');
  }

  async function updateDevice(e) {
    e.preventDefault();
    const mac = document.getElementById('edit-mac').value;
    const name = document.getElementById('edit-name').value;
    const water = document.getElementById('edit-water').value;
    const status = document.getElementById('edit-status').value;

    try {
      await fetch('public_html.php?api=update_device', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ mac_address: mac, device_name: name, water_level: parseInt(water), power_status: status })
      });
    } catch(err) {}

    closeEditModal();
    loadDevices();
  }

  async function saveDevice(e) {
    e.preventDefault();
    const mac = document.getElementById('new-mac').value;
    const name = document.getElementById('new-name').value;
    const loc = document.getElementById('new-loc').value;
    const water = document.getElementById('new-water').value;

    const newObj = {
      mac_address: mac,
      device_name: name,
      location: loc,
      water_level: parseInt(water),
      power_status: 'ON',
      last_seen: new Date().toISOString().replace('T', ' ').substring(0, 19)
    };

    try {
      await fetch('public_html.php?api=add_device', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(newObj)
      });
    } catch(e) {}

    devicesData.unshift(newObj);
    renderDevices();
    closeAddModal();
    document.getElementById('addDeviceForm').reset();
  }

  async function simulateTelemetry() {
    try {
      await fetch('public_html.php?api=simulate', { method: 'POST' });
    } catch(e) {}
    loadDevices();
    alert('Simulated live telemetry update successfully!');
  }

  async function deleteDevice(mac) {
    if (confirm(`Are you sure you want to delete MAC Device ${mac}?`)) {
      try {
        await fetch('public_html.php?api=delete_device', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ mac_address: mac })
        });
      } catch(err) {}
      loadDevices();
    }
  }

  function applyFilters() {
    const mac = document.getElementById('filter-mac').value;
    renderDevices(mac);
  }

  function resetFilters() {
    document.getElementById('filter-mac').value = '';
    document.getElementById('filter-from').value = '';
    document.getElementById('filter-to').value = '';
    renderDevices();
  }

  loadDevices();
  setInterval(loadDevices, 10000);
</script>
</body>
</html>
