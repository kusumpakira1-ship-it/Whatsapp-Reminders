<?php
// ─── Timezone: Asia/Kolkata ───────────────────────────────────────────────
date_default_timezone_set('Asia/Kolkata');

require_once __DIR__ . '/db.php';

// ─── Create Table if Not Exists ───────────────────────────────────────────
function createTable(mysqli $db): void {
    $sql = "CREATE TABLE IF NOT EXISTS `mac_devices` (
        `id`          INT UNSIGNED     NOT NULL AUTO_INCREMENT,
        `name`        VARCHAR(100)     NOT NULL,
        `mac_address` VARCHAR(17)      NOT NULL UNIQUE,
        `status`      ENUM('active','inactive','pending') NOT NULL DEFAULT 'active',
        `created_at`  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;";
    $db->query($sql);
}

// ─── Generate Random MAC Address ──────────────────────────────────────────
function randomMAC(): string {
    $mac = [];
    for ($i = 0; $i < 6; $i++) {
        $mac[] = strtoupper(sprintf('%02X', random_int(0, 255)));
    }
    return implode(':', $mac);
}

// ─── Generate Random Device Name ──────────────────────────────────────────
function randomName(): string {
    $prefixes = ['Device', 'Node', 'Unit', 'Hub', 'Sensor', 'Gateway', 'Module', 'Panel'];
    $suffix   = strtoupper(bin2hex(random_bytes(3)));
    return $prefixes[array_rand($prefixes)] . '-' . $suffix;
}

// ─── Random Status ────────────────────────────────────────────────────────
function randomStatus(): string {
    $statuses = ['active', 'inactive', 'pending'];
    return $statuses[array_rand($statuses)];
}

// ─── Headers ──────────────────────────────────────────────────────────────
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$db     = getDB();
createTable($db);

$method = strtoupper($_SERVER['REQUEST_METHOD']);
$action = strtolower($_GET['action'] ?? '');

// ─── Route: GET /api.php?action=add ──────────────────────────────────────
if ($method === 'GET' && $action === 'add') {
    $mac    = randomMAC();
    $name   = randomName();
    $status = randomStatus();
    $now    = date('Y-m-d H:i:s');   // Asia/Kolkata time

    $stmt = $db->prepare(
        "INSERT INTO `mac_devices` (`name`, `mac_address`, `status`, `created_at`)
         VALUES (?, ?, ?, ?)"
    );
    $stmt->bind_param('ssss', $name, $mac, $status, $now);

    if ($stmt->execute()) {
        echo json_encode([
            'success'    => true,
            'message'    => 'Record inserted successfully.',
            'data'       => [
                'id'         => $db->insert_id,
                'name'       => $name,
                'mac_address'=> $mac,
                'status'     => $status,
                'created_at' => $now,
                'timezone'   => 'Asia/Kolkata'
            ]
        ], JSON_PRETTY_PRINT);
    } else {
        http_response_code(409);
        echo json_encode([
            'success' => false,
            'error'   => $stmt->error
        ], JSON_PRETTY_PRINT);
    }
    $stmt->close();

// ─── Route: GET /api.php?action=view ─────────────────────────────────────
} elseif ($method === 'GET' && $action === 'view') {
    $result  = $db->query("SELECT * FROM `mac_devices` ORDER BY `id` DESC");
    $rows    = [];
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
    }
    echo json_encode([
        'success'  => true,
        'timezone' => 'Asia/Kolkata',
        'total'    => count($rows),
        'data'     => $rows
    ], JSON_PRETTY_PRINT);

// ─── Route: GET /api.php?action=delete&id=X ──────────────────────────────
} elseif ($method === 'GET' && $action === 'delete' && isset($_GET['id'])) {
    $id   = (int) $_GET['id'];
    $stmt = $db->prepare("DELETE FROM `mac_devices` WHERE `id` = ?");
    $stmt->bind_param('i', $id);
    $stmt->execute();
    echo json_encode([
        'success'       => true,
        'deleted_id'    => $id,
        'affected_rows' => $stmt->affected_rows
    ], JSON_PRETTY_PRINT);
    $stmt->close();

// ─── Route: POST /api.php?action=manual_add ──────────────────────────────
// Accepts: name, mac_address, status from form/POST body or GET params
} elseif ($action === 'manual_add') {
    // Read from POST (form submit) or GET (URL params)
    $input = $_SERVER['REQUEST_METHOD'] === 'POST' ? $_POST : $_GET;

    $name   = trim($input['name']        ?? '');
    $mac    = strtoupper(trim($input['mac_address'] ?? ''));
    $status = strtolower(trim($input['status']      ?? 'active'));
    $now    = date('Y-m-d H:i:s'); // Asia/Kolkata time

    // ── Validate ──────────────────────────────────────────────────────────
    $errors = [];

    if ($name === '') {
        $errors[] = 'name is required.';
    } elseif (strlen($name) > 100) {
        $errors[] = 'name must be 100 characters or less.';
    }

    // MAC format: XX:XX:XX:XX:XX:XX
    if ($mac === '') {
        $errors[] = 'mac_address is required.';
    } elseif (!preg_match('/^([0-9A-F]{2}:){5}[0-9A-F]{2}$/', $mac)) {
        $errors[] = 'mac_address format invalid. Use XX:XX:XX:XX:XX:XX (e.g. A3:F9:C1:D4:E5:11)';
    }

    if (!in_array($status, ['active', 'inactive', 'pending'])) {
        $errors[] = 'status must be: active, inactive, or pending.';
    }

    if (!empty($errors)) {
        http_response_code(422);
        echo json_encode([
            'success' => false,
            'errors'  => $errors
        ], JSON_PRETTY_PRINT);
    } else {
        $stmt = $db->prepare(
            "INSERT INTO `mac_devices` (`name`, `mac_address`, `status`, `created_at`)
             VALUES (?, ?, ?, ?)"
        );
        $stmt->bind_param('ssss', $name, $mac, $status, $now);

        if ($stmt->execute()) {
            echo json_encode([
                'success' => true,
                'message' => 'Device added manually.',
                'data'    => [
                    'id'          => $db->insert_id,
                    'name'        => $name,
                    'mac_address' => $mac,
                    'status'      => $status,
                    'created_at'  => $now,
                    'timezone'    => 'Asia/Kolkata'
                ]
            ], JSON_PRETTY_PRINT);
        } else {
            http_response_code(409);
            echo json_encode([
                'success' => false,
                'error'   => $stmt->error
            ], JSON_PRETTY_PRINT);
        }
        $stmt->close();
    }

// ─── Route: Unknown ───────────────────────────────────────────────────────
} else {
    http_response_code(400);
    echo json_encode([
        'success'  => false,
        'message'  => 'Unknown action.',
        'endpoints'=> [
            'Random add'  => '/api.php?action=add',
            'Manual add'  => '/api.php?action=manual_add&name=MyDevice&mac_address=AA:BB:CC:DD:EE:FF&status=active',
            'View all'    => '/api.php?action=view',
            'Delete by ID'=> '/api.php?action=delete&id=1'
        ]
    ], JSON_PRETTY_PRINT);
}

$db->close();
