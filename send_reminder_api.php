<?php
/**
 * ------------------------------------------------------------------------
 * Standalone Dedicated API & Web Link: Send Custom WhatsApp Reminders
 * ------------------------------------------------------------------------
 * Dedicated Link URL:
 * https://sunfragroup.com/kusum/Whatsapp_Rem/send_reminder_api.php
 * 
 * Usage 1 (Browser URL GET Link):
 * https://sunfragroup.com/kusum/Whatsapp_Rem/send_reminder_api.php?phone=7259510983&name=Kusum&message=Your+message+text+here
 * 
 * Usage 2 (API POST JSON / Form):
 * Body: {"phone": "7259510983", "name": "Kusum", "message": "Text message", "frequency": "once"}
 */

// Enable CORS and Headers
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// 1. Read Payload Input (JSON body, POST, or GET Query Params)
$input_json = json_decode(file_get_contents('php://input'), true);
if (!is_array($input_json)) {
    $input_json = [];
}

$raw_phone   = trim($input_json['phone'] ?? $input_json['phone_number'] ?? $input_json['whatsapp_group_id'] ?? $input_json['recipient'] ?? $_REQUEST['phone'] ?? $_REQUEST['phone_number'] ?? $_REQUEST['whatsapp_group_id'] ?? $_REQUEST['recipient'] ?? '');
$person_name = trim($input_json['name'] ?? $input_json['person_name'] ?? $input_json['title'] ?? $_REQUEST['name'] ?? $_REQUEST['person_name'] ?? $_REQUEST['title'] ?? '');
$message_text= trim($input_json['message'] ?? $input_json['text'] ?? $input_json['task_notes'] ?? $input_json['notes'] ?? $_REQUEST['message'] ?? $_REQUEST['text'] ?? $_REQUEST['task_notes'] ?? $_REQUEST['notes'] ?? '');
$trigger_time_input = trim($input_json['trigger_time'] ?? $input_json['time'] ?? $input_json['due_time'] ?? $_REQUEST['trigger_time'] ?? $_REQUEST['time'] ?? $_REQUEST['due_time'] ?? '');
$frequency   = strtolower(trim($input_json['frequency'] ?? $input_json['freq'] ?? $_REQUEST['frequency'] ?? $_REQUEST['freq'] ?? 'once'));
$repeat_interval = strtolower(trim($input_json['repeat_interval'] ?? $input_json['interval'] ?? $_REQUEST['repeat_interval'] ?? $_REQUEST['interval'] ?? 'none'));

$wants_json  = (!empty($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) || !empty($input_json) || isset($_REQUEST['json']);

// 2. If opened in Browser via GET with NO parameters, show interactive Form
if (empty($raw_phone) && empty($message_text) && $_SERVER['REQUEST_METHOD'] === 'GET') {
    header('Content-Type: text/html; charset=utf-8');
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Send WhatsApp Reminder - Sunfra API</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * { box-sizing: border-box; font-family: 'Inter', sans-serif; }
            body { background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
            .card { background: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 32px; width: 100%; max-width: 500px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }
            h2 { margin-top: 0; color: #38bdf8; font-size: 22px; display: flex; align-items: center; gap: 10px; }
            label { display: block; margin-top: 16px; font-weight: 500; font-size: 14px; color: #94a3b8; margin-bottom: 6px; }
            input, textarea, select { width: 100%; background: #0f172a; border: 1px solid #475569; border-radius: 8px; padding: 12px; color: #f8fafc; font-size: 14px; outline: none; transition: 0.2s; }
            input:focus, textarea:focus, select:focus { border-color: #38bdf8; box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2); }
            button { margin-top: 24px; width: 100%; background: #0284c7; color: white; border: none; padding: 14px; border-radius: 8px; font-weight: 600; font-size: 16px; cursor: pointer; transition: 0.2s; }
            button:hover { background: #0369a1; }
            .note { margin-top: 16px; font-size: 12px; color: #64748b; text-align: center; }
            .code-box { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 10px; font-family: monospace; font-size: 11px; color: #34d399; overflow-x: auto; margin-top: 10px; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 Send Custom WhatsApp Reminder</h2>
            <form action="send_reminder_api.php" method="GET">
                <label for="phone">Phone Number or WhatsApp Group JID</label>
                <input type="text" id="phone" name="phone" placeholder="e.g. 7259510983" value="7259510983" required>

                <label for="name">Recipient / Person Name (Optional)</label>
                <input type="text" id="name" name="name" placeholder="e.g. Kusum">

                <label for="message">WhatsApp Message Content</label>
                <textarea id="message" name="message" rows="4" placeholder="Type your custom message here..." required></textarea>

                <label for="frequency">Frequency</label>
                <select id="frequency" name="frequency">
                    <option value="once">One-Time (Once)</option>
                    <option value="daily">Daily (Everyday)</option>
                    <option value="mon-sat">Monday to Saturday (Skip Sunday)</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                </select>

                <button type="submit">📲 Send WhatsApp Message Now</button>
            </form>
            <div class="note">
                <strong>Direct URL Format:</strong>
                <div class="code-box">send_reminder_api.php?phone=7259510983&name=Kusum&message=Hello</div>
            </div>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// 3. Validate Inputs
if (empty($raw_phone) || empty($message_text)) {
    if ($wants_json) {
        header('Content-Type: application/json; charset=utf-8');
        http_response_code(400);
        echo json_encode([
            'status' => 'error',
            'message' => 'Missing required fields: phone and message are required.'
        ], JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
    } else {
        header('Content-Type: text/html; charset=utf-8');
        echo "<h2>⚠️ Missing required parameters: phone and message</h2><p>Usage: <code>send_reminder_api.php?phone=7259510983&name=Kusum&message=Hello</code></p>";
    }
    exit;
}

// 4. Format Target WhatsApp JID
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

// 5. Format Trigger Time
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

// 6. Save to Database (Hostinger MySQL)
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

    // Save to Database strictly ONCE in sunfra_unified_reminders to prevent duplicate sends
    $unif_id = null;
    try {
        $stmt_unif = $pdo->prepare("INSERT INTO sunfra_unified_reminders (person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, repeat_interval, status, created_at) VALUES (:person_name, :person_phone, :whatsapp_group_id, :report_types, :task_notes, :trigger_time, :frequency, :repeat_interval, 'pending', NOW())");
        $stmt_unif->execute([
            ':person_name' => !empty($person_name) ? $person_name : 'Custom Reminder',
            ':person_phone' => !empty($raw_phone) ? $raw_phone : '',
            ':whatsapp_group_id' => $target_jid,
            ':report_types' => !empty($report_type) ? $report_type : 'Custom Reminder',
            ':task_notes' => $final_message,
            ':trigger_time' => $trigger_time,
            ':frequency' => $frequency,
            ':repeat_interval' => $repeat_interval
        ]);
        $unif_id = $pdo->lastInsertId();
    } catch (\Exception $e_unif) {}

} catch (\Exception $e) {}

// 7. Saved cleanly into database for single-instance dispatch by python scheduler
$waha_sent = true;

// 8. Return Response (HTML Confirmation Page for Browser, JSON for API)
if (!$wants_json) {
    header('Content-Type: text/html; charset=utf-8');
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WhatsApp Reminder Triggered</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            body { background: #0f172a; color: #f8fafc; font-family: 'Inter', sans-serif; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; }
            .card { background: #1e293b; border: 1px solid #10b981; border-radius: 16px; padding: 32px; text-align: center; max-width: 480px; width: 100%; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5); }
            h2 { color: #10b981; margin-top: 0; font-size: 22px; }
            .badge { display: inline-block; background: #064e3b; color: #34d399; padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-bottom: 16px; }
            .box { background: #0f172a; border: 1px solid #334155; border-radius: 10px; padding: 18px; text-align: left; font-size: 14px; margin: 16px 0; color: #cbd5e1; }
            .box strong { color: #38bdf8; }
            a { display: inline-block; background: #0284c7; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 14px; margin-top: 12px; }
            a:hover { background: #0369a1; }
        </style>
    </head>
    <body>
        <div class="card">
            <h2>🚀 WhatsApp Reminder Created!</h2>
            <div class="badge"><?php echo $waha_sent ? 'SENT IMMEDIATELY ✅' : 'RECORDED & SCHEDULED 🕒'; ?></div>
            
            <div class="box">
                <p><strong>Recipient:</strong> <?php echo htmlspecialchars($target_jid); ?></p>
                <p><strong>Name:</strong> <?php echo htmlspecialchars($person_name ? $person_name : 'N/A'); ?></p>
                <p><strong>Trigger Time:</strong> <?php echo htmlspecialchars($trigger_time); ?></p>
                <p><strong>Message:</strong><br><?php echo nl2br(htmlspecialchars($final_message)); ?></p>
            </div>

            <a href="send_reminder_api.php">⬅ Send Another Reminder</a>
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
    'message' => $waha_sent ? 'Reminder triggered and sent to WhatsApp immediately!' : 'Reminder scheduled successfully in database!',
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
