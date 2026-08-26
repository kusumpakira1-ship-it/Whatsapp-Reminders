<?php
/**
 * Standalone Localhost Weight Indicator Device API Link & Telemetry Connector
 * Localhost Endpoint: http://localhost/Whatsapp_Rem/api_weight_indicator_device.php
 * Root Localhost Endpoint: http://localhost/api_weight_indicator_device.php
 * 
 * Provides live server timestamps, weight telemetry indicator values (kg, status badges),
 * MAC addresses monitoring, filtering (Date From/To, MAC Address), Action Buttons metadata,
 * AND device data ingestion (POST / GET weight readings from devices).
 * 
 * IMPORTANT: Standalone API script. Does NOT modify any existing code or existing links.
 */

ini_set('display_errors', '0');
error_reporting(E_ALL);

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

date_default_timezone_set('Asia/Kolkata');

function getDatabaseConnection() {
    static $pdo = null;
    if ($pdo !== null) return $pdo;

    $dbName = 'u632391467_kusumpakira';
    $user   = 'u632391467_kusumpakira';
    $pass   = 'Kusum@2026Bb!';

    $hosts = ['localhost', '127.0.0.1', '145.223.17.70'];
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

    $sqlitePath = __DIR__ . '/mac_water_monitoring.sqlite';
    try {
        $pdo = new PDO('sqlite:' . $sqlitePath, null, null, [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
    } catch (Throwable $eSqlite) {
        $pdo = null;
    }

    return $pdo;
}

function cleanMacAddress($mac) {
    if (empty($mac)) return 'ALL';
    $hex = strtoupper(preg_replace('/[^0-9A-Fa-f]/', '', $mac));
    if (strlen($hex) !== 12) {
        return strtoupper(trim($mac));
    }
    return implode('-', str_split($hex, 2));
}

function parseDateParam($dateStr, $timeSuffix = '00:00:00') {
    if (empty($dateStr)) return null;
    $dateStr = trim($dateStr);
    
    if (preg_match('/^(\d{2})[- \/](\d{2})[- \/](\d{4})$/', $dateStr, $m)) {
        return "{$m[3]}-{$m[2]}-{$m[1]} {$timeSuffix}";
    }
    if (preg_match('/^(\d{4})[- \/](\d{2})[- \/](\d{2})$/', $dateStr, $m)) {
        return "{$m[1]}-{$m[2]}-{$m[3]} {$timeSuffix}";
    }
    
    $ts = strtotime($dateStr);
    return $ts ? date('Y-m-d H:i:s', $ts) : null;
}

$pdo = getDatabaseConnection();

// Receive input data (Support GET, POST Form, and POST JSON Payload)
$jsonInput = json_decode(file_get_contents('php://input'), true) ?: [];
$input = array_merge($_GET, $_POST, $jsonInput);

$action = strtolower(trim($input['action'] ?? 'read'));

// DEVICE WEIGHT DATA INGESTION (Posting weight data from IoT / Scale device)
if ($action === 'post_weight' || $action === 'push_telemetry' || (isset($input['mac_address']) && isset($input['weight_value']) && $_SERVER['REQUEST_METHOD'] === 'POST')) {
    $mac = cleanMacAddress($input['mac_address'] ?? $input['mac'] ?? '');
    $weight = isset($input['weight_value']) ? (float)$input['weight_value'] : (isset($input['weight_kg']) ? (float)$input['weight_kg'] : (float)($input['water_level'] ?? 0));
    $status = strtoupper(trim($input['status'] ?? 'ON'));
    $location = trim($input['location'] ?? 'Localhost POS Scale');
    $deviceName = trim($input['device_name'] ?? 'Scale (' . $mac . ')');
    $currentTime = date('Y-m-d H:i:s');

    if (empty($mac) || $mac === 'ALL') {
        echo json_encode([
            'success' => false,
            'message' => 'Error: mac_address parameter is required for submitting weight data.'
        ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        exit;
    }

    try {
        // 1. Update or Insert into mac_devices
        $checkStmt = $pdo->prepare("SELECT id FROM mac_devices WHERE mac_address = ?");
        $checkStmt->execute([$mac]);
        $existing = $checkStmt->fetch();

        if ($existing) {
            $updStmt = $pdo->prepare("UPDATE mac_devices SET water_level = ?, status = ?, location = ?, updated_at = ? WHERE mac_address = ?");
            $updStmt->execute([$weight, $status, $location, $currentTime, $mac]);
        } else {
            $insStmt = $pdo->prepare("INSERT INTO mac_devices (name, mac_address, location, water_level, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)");
            $insStmt->execute([$deviceName, $mac, $location, $weight, $status, $currentTime, $currentTime]);
        }

        // 2. Log entry into device_readings
        try {
            $logStmt = $pdo->prepare("INSERT INTO device_readings (mac_address, location, water_level, status, timestamp) VALUES (?, ?, ?, ?, ?)");
            $logStmt->execute([$mac, $location, $weight, $status, $currentTime]);
        } catch (Throwable $eLog) {}

        // Calculate Indicator Badge for the posted reading
        if ($weight <= 10.0) {
            $badge = '⚠️ LOW WEIGHT ALERT (< 10 kg)';
        } elseif ($weight > 10.0 && $weight <= 75.0) {
            $badge = '⚖️ OPTIMAL TARGET WEIGHT';
        } else {
            $badge = '🚨 OVERWEIGHT WARNING (> 75 kg)';
        }

        echo json_encode([
            'success' => true,
            'message' => 'Weight scale telemetry data recorded successfully.',
            'timestamp_info' => [
                'current_server_timestamp' => $currentTime,
                'formatted_date_time'      => date('d/m/Y, H:i:s', strtotime($currentTime)),
                'timezone'                 => 'Asia/Kolkata',
                'unix_timestamp'           => time()
            ],
            'device_info' => [
                'mac_address'            => $mac,
                'location'               => $location,
                'weight_indicator_value' => round($weight, 2),
                'unit'                   => 'kg',
                'formatted_weight'       => number_format($weight, 2) . ' kg',
                'status_badge'           => $badge,
                'power_status'           => $status
            ],
            'action_buttons' => [
                'read_telemetry' => [
                    'label'    => '📊 Read All Telemetry',
                    'endpoint' => 'api_weight_indicator_device.php',
                    'method'   => 'GET'
                ],
                'post_reading' => [
                    'label'    => '⚖️ Post New Weight Reading',
                    'endpoint' => 'api_weight_indicator_device.php?action=post_weight',
                    'method'   => 'POST'
                ]
            ]
        ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        exit;
    } catch (Throwable $ePost) {
        echo json_encode([
            'success' => false,
            'message' => 'Error recording weight telemetry data: ' . $ePost->getMessage()
        ], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        exit;
    }
}

// DEFAULT READ TELEMETRY ACTION (GET Device Data with Timestamps, MACs, Indicator Values, Action Buttons)
$startDateParam = trim($input['filter_from'] ?? $input['start_date'] ?? $input['from'] ?? '');
$endDateParam   = trim($input['filter_to'] ?? $input['end_date'] ?? $input['to'] ?? '');
$macFilterParam = cleanMacAddress(trim($input['mac_address'] ?? $input['mac'] ?? 'ALL'));

$fromDate = parseDateParam($startDateParam, '00:00:00');
$toDate   = parseDateParam($endDateParam, '23:59:59');

$devicesSql = "SELECT * FROM mac_devices WHERE 1=1";
$devicesParams = [];

if (!empty($macFilterParam) && $macFilterParam !== 'ALL') {
    $devicesSql .= " AND mac_address = ?";
    $devicesParams[] = $macFilterParam;
}

if ($fromDate) {
    $devicesSql .= " AND updated_at >= ?";
    $devicesParams[] = $fromDate;
}

if ($toDate) {
    $devicesSql .= " AND updated_at <= ?";
    $devicesParams[] = $toDate;
}

$devicesSql .= " ORDER BY updated_at DESC, id DESC";

try {
    $stmt = $pdo->prepare($devicesSql);
    $stmt->execute($devicesParams);
    $rawDevices = $stmt->fetchAll();
} catch (Throwable $eDev) {
    $rawDevices = [];
}

$processedDevices = [];
$statTotal        = count($rawDevices);
$statOnCount      = 0;
$statOffCount     = 0;
$statLowWeight    = 0;
$totalWeightKg    = 0.0;

foreach ($rawDevices as $dev) {
    $rawVal   = (float)$dev['water_level'];
    $weightKg = ($rawVal >= 0) ? round($rawVal, 2) : 0.0;
    $status   = strtoupper($dev['status']);
    
    if ($status === 'ON') {
        $statOnCount++;
        $statusIndicator = '🟢 SCALE ONLINE (ON)';
    } else {
        $statOffCount++;
        $statusIndicator = '🔴 SCALE OFFLINE (OFF)';
    }

    if ($rawVal < 0) {
        $weightIndicator = '⚪ PENDING WEIGHT SCALE TELEMETRY';
    } elseif ($weightKg <= 10.0) {
        $statLowWeight++;
        $weightIndicator = '⚠️ LOW WEIGHT ALERT (< 10 kg)';
    } elseif ($weightKg > 10.0 && $weightKg <= 75.0) {
        $weightIndicator = '⚖️ OPTIMAL TARGET WEIGHT';
    } else {
        $weightIndicator = '🚨 OVERWEIGHT WARNING (> 75 kg)';
    }

    if ($rawVal >= 0) {
        $totalWeightKg += $weightKg;
    }

    $processedDevices[] = [
        'device_id'              => (int)$dev['id'],
        'device_name'            => $dev['name'],
        'mac_address'            => $dev['mac_address'],
        'scale_location'         => $dev['location'],
        'weight_indicator'       => [
            'value'              => $weightKg,
            'unit'               => 'kg',
            'formatted_weight'   => $rawVal >= 0 ? number_format($weightKg, 2) . ' kg' : 'N/A',
            'status_badge'       => $weightIndicator
        ],
        'power_status_indicator' => [
            'state'              => $status,
            'status_label'       => $statusIndicator
        ],
        'last_updated_timestamp' => $dev['updated_at'] ?? $dev['created_at'],
        'created_at_timestamp'   => $dev['created_at']
    ];
}

$macList = [];
try {
    $macStmt = $pdo->query("SELECT DISTINCT mac_address, name, location FROM mac_devices ORDER BY name ASC");
    $macList = $macStmt->fetchAll();
} catch (Throwable $eMac) {}

$readings = [];
try {
    $readingsSql = "SELECT * FROM device_readings WHERE 1=1";
    $readingsParams = [];
    if (!empty($macFilterParam) && $macFilterParam !== 'ALL') {
        $readingsSql .= " AND mac_address = ?";
        $readingsParams[] = $macFilterParam;
    }
    $readingsSql .= " ORDER BY timestamp DESC, id DESC LIMIT 50";
    $rStmt = $pdo->prepare($readingsSql);
    $rStmt->execute($readingsParams);
    $rawReadings = $rStmt->fetchAll();

    foreach ($rawReadings as $r) {
        $wVal = (float)$r['water_level'];
        $readings[] = [
            'id'               => (int)$r['id'],
            'mac_address'      => $r['mac_address'],
            'location'         => $r['location'],
            'weight_value_kg'  => $wVal >= 0 ? $wVal : 0,
            'formatted_weight' => $wVal >= 0 ? number_format($wVal, 2) . ' kg' : 'N/A',
            'status'           => $r['status'],
            'timestamp'        => $r['timestamp']
        ];
    }
} catch (Throwable $eRead) {}

echo json_encode([
    'success' => true,
    'api_title' => 'Sunfra Localhost Weight Indicator & Scale Device API',
    'timestamp_info' => [
        'current_server_timestamp' => date('Y-m-d H:i:s'),
        'formatted_date_time'      => date('d/m/Y, H:i:s'),
        'timezone'                 => 'Asia/Kolkata',
        'unix_timestamp'           => time()
    ],
    'indicator_summary' => [
        'total_weight_scales'  => $statTotal,
        'active_online_scales' => $statOnCount,
        'offline_scales'       => $statOffCount,
        'low_weight_alerts'    => $statLowWeight,
        'total_accumulated_wt' => round($totalWeightKg, 2) . ' kg'
    ],
    'applied_filters' => [
        'filter_from' => $startDateParam ?: null,
        'filter_to'   => $endDateParam ?: null,
        'mac_address' => $macFilterParam
    ],
    'action_buttons' => [
        'add_device' => [
            'label'    => '➕ Add Weight Scale',
            'action'   => 'openAddDeviceModal',
            'endpoint' => 'index1.php?api=add_device',
            'method'   => 'POST'
        ],
        'customization_filter' => [
            'label'      => '⚙️ Customization Filters',
            'from_field' => 'Filter Date & Time (From)',
            'to_field'   => 'Filter Date & Time (To)',
            'mac_select' => 'MAC Address Filter'
        ],
        'apply_filter' => [
            'label'  => '🔍 Apply Filter',
            'action' => 'applyFilters',
            'method' => 'GET',
            'endpoint' => 'api_weight_indicator_device.php?mac=MAC_ADDRESS&from=YYYY-MM-DD&to=YYYY-MM-DD'
        ],
        'reset_filter' => [
            'label'  => '🔄 Reset Filter',
            'action' => 'resetFilters',
            'endpoint' => 'api_weight_indicator_device.php'
        ],
        'post_weight_reading' => [
            'label'    => '⚖️ Submit Weight Reading From Device',
            'action'   => 'postWeight',
            'endpoint' => 'api_weight_indicator_device.php?action=post_weight',
            'method'   => 'POST',
            'payload_example' => [
                'mac_address'  => 'AA-BB-CC-DD-EE-FF',
                'weight_value' => 25.5,
                'status'       => 'ON',
                'location'     => 'Counter 1 Scale'
            ]
        ]
    ],
    'weight_devices' => $processedDevices,
    'mac_list'       => $macList,
    'weight_telemetry_readings' => $readings
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
exit;
