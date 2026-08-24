<?php
/**
 * Standalone API Endpoint: Trigger Custom WhatsApp Reminder
 * URL: https://sunfragroup.com/kusum/Whatsapp_Rem/api/trigger_reminder.php
 * 
 * Supports JSON POST, Form POST, and GET requests.
 * Fields:
 *  - phone / recipient / whatsapp_group_id
 *  - name / person_name
 *  - message / text / task_notes
 *  - trigger_time / time / due_time (Optional, defaults to NOW)
 *  - frequency / freq (Optional, defaults to 'once')
 *  - repeat_interval / interval (Optional, defaults to 'none')
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// 1. Read input payload (JSON or $_REQUEST)
$input_json = json_decode(file_get_contents('php://input'), true);
if (!is_array($input_json)) {
    $input_json = [];
}

$raw_phone = trim($input_json['phone'] ?? $input_json['phone_number'] ?? $input_json['whatsapp_group_id'] ?? $input_json['recipient'] ?? $_REQUEST['phone'] ?? $_REQUEST['phone_number'] ?? $_REQUEST['whatsapp_group_id'] ?? $_REQUEST['recipient'] ?? '');
$person_name = trim($input_json['name'] ?? $input_json['person_name'] ?? $input_json['title'] ?? $_REQUEST['name'] ?? $_REQUEST['person_name'] ?? $_REQUEST['title'] ?? '');
$message_text = trim($input_json['message'] ?? $input_json['text'] ?? $input_json['task_notes'] ?? $input_json['notes'] ?? $_REQUEST['message'] ?? $_REQUEST['text'] ?? $_REQUEST['task_notes'] ?? $_REQUEST['notes'] ?? '');
$trigger_time_input = trim($input_json['trigger_time'] ?? $input_json['time'] ?? $input_json['due_time'] ?? $_REQUEST['trigger_time'] ?? $_REQUEST['time'] ?? $_REQUEST['due_time'] ?? '');
$frequency = strtolower(trim($input_json['frequency'] ?? $input_json['freq'] ?? $_REQUEST['frequency'] ?? $_REQUEST['freq'] ?? 'once'));
$repeat_interval = strtolower(trim($input_json['repeat_interval'] ?? $input_json['interval'] ?? $_REQUEST['repeat_interval'] ?? $_REQUEST['interval'] ?? 'none'));

if (empty($raw_phone) || empty($message_text)) {
    http_response_code(400);
    echo json_encode([
        'status' => 'error',
        'message' => 'Missing required fields: phone (or recipient) and message (or text) are required.',
        'example_payload' => [
            'phone' => '7259510983',
            'name' => 'Kusum',
            'message' => 'Your custom text message here',
            'trigger_time' => date('Y-m-d H:i:s'),
            'frequency' => 'once'
        ]
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    exit;
}

// 2. Format Target Phone / Group JID
$clean_target = preg_replace('/[^\d@a-zA-Z\.\-_]/', '', $raw_phone);
if (strpos($clean_target, '@g.us') !== false) {
    $target_jid = $clean_target;
    $target_type = 'group';
} else {
    $digits = preg_replace('/[^\d]/', '', $clean_target);
    if (strlen($digits) == 10) {
        $digits = '91' . $digits;
    }
    $target_jid = $digits . '@c.us';
    $target_type = 'employee';
}

// 3. Format Trigger Time (Default: NOW in IST +05:30)
date_default_timezone_set('Asia/Kolkata');
if (!empty($trigger_time_input)) {
    $ts = strtotime($trigger_time_input);
    if ($ts !== false) {
        $trigger_time = date('Y-m-d H:i:s', $ts);
    } else {
        $trigger_time = date('Y-m-d H:i:s');
    }
} else {
    $trigger_time = date('Y-m-d H:i:s');
}

// Combine Person Name into Message if provided
$final_message = $message_text;
if (!empty($person_name) && strpos(strtolower($message_text), strtolower($person_name)) === false) {
    $final_message = "🔔 *Reminder for {$person_name}*\n\n" . $message_text;
}

// 4. Database Connection & Record Creation
$host = '145.223.17.70';
$db   = 'u632391467_kusumpakira';
$user = 'u632391467_kusumpakira';
$pass = 'Kusum@2026Bb!';
$charset = 'utf8mb4';

$alarm_id = null;
try {
    $pdo = new PDO("mysql:host=$host;dbname=$db;charset=$charset", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_PERSISTENT => true
    ]);

    $stmt = $pdo->prepare("INSERT INTO sunfra_custom_alarms (target_type, whatsapp_target_id, report_type, frequency, repeat_interval, task_notes, trigger_time, status, created_at) VALUES (:target_type, :whatsapp_target_id, :report_type, :frequency, :repeat_interval, :task_notes, :trigger_time, 'pending', NOW())");
    $stmt->execute([
        ':target_type' => $target_type,
        ':whatsapp_target_id' => $target_jid,
        ':report_type' => 'Custom API Reminder',
        ':frequency' => $frequency,
        ':repeat_interval' => $repeat_interval,
        ':task_notes' => $final_message,
        ':trigger_time' => $trigger_time
    ]);
    $alarm_id = $pdo->lastInsertId();

    // Also save in sunfra_unified_reminders for unified tracking
    try {
        $stmt_unif = $pdo->prepare("INSERT INTO sunfra_unified_reminders (person_name, whatsapp_group_id, report_types, trigger_time, frequency, status, created_at) VALUES (:person_name, :whatsapp_group_id, :report_types, :trigger_time, :frequency, 'pending', NOW())");
        $stmt_unif->execute([
            ':person_name' => !empty($person_name) ? $person_name : 'Custom Reminder',
            ':whatsapp_group_id' => $target_jid,
            ':report_types' => $final_message,
            ':trigger_time' => $trigger_time,
            ':frequency' => $frequency
        ]);
    } catch (\Exception $e_unif) {}

} catch (\Exception $e) {
    // If MySQL connection fails, continue to dispatch WAHA message if trigger_time is now
}

// 5. Send Immediate WAHA Message if Trigger Time is Now (or within 2 minutes)
$waha_sent = false;
$now_ts = time();
$trigger_ts = strtotime($trigger_time);
if (abs($now_ts - $trigger_ts) <= 120) {
    $waha_url = getenv('WAHA_URL') ? getenv('WAHA_URL') : 'http://localhost:3000';
    $payload_waha = json_encode([
        'chatId' => $target_jid,
        'text' => $final_message,
        'session' => 'default'
    ]);

    $ch = curl_init("{$waha_url}/api/sendText");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload_waha);
    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
    curl_setopt($ch, CURLOPT_TIMEOUT, 10);
    $res_waha = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code == 200 || $http_code == 201) {
        $waha_sent = true;
        // Update alarm status to sent
        if ($alarm_id && isset($pdo)) {
            try {
                $upd = $pdo->prepare("UPDATE sunfra_custom_alarms SET status = 'sent' WHERE id = :id");
                $upd->execute([':id' => $alarm_id]);
            } catch (\Exception $ex) {}
        }
    }
}

// 6. Return JSON Response
http_response_code(200);
echo json_encode([
    'status' => 'success',
    'message' => $waha_sent ? 'Reminder triggered and sent to WhatsApp immediately!' : 'Reminder scheduled successfully for the background queue!',
    'alarm_id' => $alarm_id,
    'data' => [
        'phone_input' => $raw_phone,
        'target_jid' => $target_jid,
        'person_name' => $person_name,
        'message_text' => $final_message,
        'trigger_time' => $trigger_time,
        'frequency' => $frequency,
        'repeat_interval' => $repeat_interval,
        'immediate_whatsapp_sent' => $waha_sent
    ]
], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
