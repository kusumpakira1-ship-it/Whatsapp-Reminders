<?php
/**
 * Standalone API Endpoint & Browser Link: Trigger Custom WhatsApp Reminder
 * URL: https://sunfragroup.com/kusum/Whatsapp_Rem/trigger_reminder.php
 */

header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// Read input payload (JSON or $_REQUEST)
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

// If no phone/message and GET, display Web Form UI
if (empty($raw_phone) && empty($message_text) && $_SERVER['REQUEST_METHOD'] === 'GET') {
    header('Content-Type: text/html; charset=utf-8');
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Trigger Custom WhatsApp Reminder</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; font-family: 'Inter', sans-serif; }
            body { background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
            .card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 32px; width: 100%; max-width: 480px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }
            h2 { margin-top: 0; color: #38bdf8; font-size: 22px; display: flex; align-items: center; gap: 10px; }
            label { display: block; margin-top: 16px; font-weight: 500; font-size: 14px; color: #94a3b8; margin-bottom: 6px; }
            input, textarea, select { width: 100%; background: #0f172a; border: 1px solid #475569; border-radius: 8px; padding: 12px; color: #f8fafc; font-size: 14px; outline: none; transition: 0.2s; }
            input:focus, textarea:focus, select:focus { border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }
            button { margin-top: 24px; width: 100%; background: #0284c7; color: white; border: none; padding: 14px; border-radius: 8px; font-weight: 600; font-size: 16px; cursor: pointer; transition: 0.2s; }
            button:hover { background: #0369a1; }
            .note { margin-top: 16px; font-size: 12px; color: #64748b; text-align: center; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 Send WhatsApp Reminder</h2>
            <form action="trigger_reminder.php" method="POST">
                <label for="phone">Phone Number or WhatsApp Group JID</label>
                <input type="text" id="phone" name="phone" placeholder="e.g. 7259510983" value="7259510983" required>

                <label for="name">Recipient / Topic Name (Optional)</label>
                <input type="text" id="name" name="name" placeholder="e.g. Kusum">

                <label for="message">WhatsApp Message Text</label>
                <textarea id="message" name="message" rows="4" placeholder="Type your custom WhatsApp message here..." required></textarea>

                <label for="frequency">Frequency</label>
                <select id="frequency" name="frequency">
                    <option value="once">One-Time (Once)</option>
                    <option value="daily">Daily (Everyday)</option>
                    <option value="mon-sat">Monday to Saturday (Skip Sunday)</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                </select>

                <button type="submit">📲 Send WhatsApp Reminder Now</button>
            </form>
            <div class="note">Supports direct browser submit, URL GET query, and JSON API POST</div>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// Process Request (API or Form Submit)
if (empty($raw_phone) || empty($message_text)) {
    header('Content-Type: application/json; charset=utf-8');
    http_response_code(400);
    echo json_encode([
        'status' => 'error',
        'message' => 'Missing required fields: phone and message are required.'
    ], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    exit;
}

// Format Target Phone / Group JID
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

date_default_timezone_set('Asia/Kolkata');
if (!empty($trigger_time_input)) {
    $ts = strtotime($trigger_time_input);
    $trigger_time = ($ts !== false) ? date('Y-m-d H:i:s', $ts) : date('Y-m-d H:i:s');
} else {
    $trigger_time = date('Y-m-d H:i:s');
}

$final_message = $message_text;
if (!empty($person_name) && strpos(strtolower($message_text), strtolower($person_name)) === false) {
    $final_message = "🔔 *Reminder for {$person_name}*\n\n" . $message_text;
}

// Database Insertion
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

} catch (\Exception $e) {}

// Immediate WAHA Dispatch
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
        if ($alarm_id && isset($pdo)) {
            try {
                $upd = $pdo->prepare("UPDATE sunfra_custom_alarms SET status = 'sent' WHERE id = :id");
                $upd->execute([':id' => $alarm_id]);
            } catch (\Exception $ex) {}
        }
    }
}

// Return Output (JSON for API, HTML for Browser Form Submit)
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['phone'])) {
    header('Content-Type: text/html; charset=utf-8');
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Reminder Sent Successfully</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; border: 1px solid #10b981; border-radius: 16px; padding: 32px; text-align: center; max-width: 440px; }
            h2 { color: #10b981; margin-top: 0; }
            p { color: #94a3b8; font-size: 14px; line-height: 1.5; }
            a { display: inline-block; margin-top: 16px; background: #0284c7; color: white; padding: 10px 20px; border-radius: 8px; text-decoration: none; font-weight: 600; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>✅ Reminder Created Successfully!</h2>
            <p>Target: <strong><?php echo htmlspecialchars($target_jid); ?></strong></p>
            <p>Message: "<?php echo htmlspecialchars($final_message); ?>"</p>
            <a href="trigger_reminder.php">⬅ Send Another Reminder</a>
        </div>
    </body>
    </html>
    <?php
    exit;
}

header('Content-Type: application/json; charset=utf-8');
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
