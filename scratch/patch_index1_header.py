import os

file_path = r'C:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\index1.php'

handler_code = """
// ─── Standalone API & URL Link Reminder Trigger Handler ──────────────────────
if ((!empty($_REQUEST['phone']) || !empty($_GET['phone'])) && (!empty($_REQUEST['message']) || !empty($_GET['message']) || !empty($_REQUEST['text']) || !empty($_GET['text']))) {
    header('Access-Control-Allow-Origin: *');
    header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

    $input_json = json_decode(file_get_contents('php://input'), true);
    if (!is_array($input_json)) { $input_json = []; }

    $raw_phone   = trim($input_json['phone'] ?? $input_json['phone_number'] ?? $input_json['whatsapp_group_id'] ?? $input_json['recipient'] ?? $_REQUEST['phone'] ?? $_REQUEST['phone_number'] ?? $_REQUEST['whatsapp_group_id'] ?? $_REQUEST['recipient'] ?? '');
    $person_name = trim($input_json['name'] ?? $input_json['person_name'] ?? $input_json['title'] ?? $_REQUEST['name'] ?? $_REQUEST['person_name'] ?? $_REQUEST['title'] ?? '');
    $message_text= trim($input_json['message'] ?? $input_json['text'] ?? $input_json['task_notes'] ?? $input_json['notes'] ?? $_REQUEST['message'] ?? $_REQUEST['text'] ?? $_REQUEST['task_notes'] ?? $_REQUEST['notes'] ?? '');
    $trigger_time_input = trim($input_json['trigger_time'] ?? $input_json['time'] ?? $input_json['due_time'] ?? $_REQUEST['trigger_time'] ?? $_REQUEST['time'] ?? $_REQUEST['due_time'] ?? '');
    $frequency   = strtolower(trim($input_json['frequency'] ?? $input_json['freq'] ?? $_REQUEST['frequency'] ?? $_REQUEST['freq'] ?? 'once'));
    $repeat_interval = strtolower(trim($input_json['repeat_interval'] ?? $input_json['interval'] ?? $_REQUEST['repeat_interval'] ?? $_REQUEST['interval'] ?? 'none'));

    $wants_json  = (!empty($_SERVER['HTTP_ACCEPT']) && strpos($_SERVER['HTTP_ACCEPT'], 'application/json') !== false) || !empty($input_json) || isset($_REQUEST['json']);

    if (!empty($raw_phone) && !empty($message_text)) {
        $clean_target = preg_replace('/[^\\d@a-zA-Z\\.\\-_]/', '', $raw_phone);
        if (strpos($clean_target, '@g.us') !== false) {
            $target_jid = $clean_target;
            $target_type = 'group';
        } else {
            $digits = preg_replace('/[^\\d]/', '', $clean_target);
            if (strlen($digits) == 10) { $digits = '91' . $digits; }
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
            $final_message = "🔔 *Reminder for {$person_name}*\\n\\n" . $message_text;
        }

        $alarm_id = null;
        $host = '145.223.17.70';
        $db   = 'u632391467_kusumpakira';
        $user = 'u632391467_kusumpakira';
        $pass = 'Kusum@2026Bb!';
        $charset = 'utf8mb4';

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
            } catch (\\Exception $e_unif) {}

        } catch (\\Exception $e) {}

        $waha_sent = false;
        $now_ts = time();
        $trigger_ts = strtotime($trigger_time);
        if (abs($now_ts - $trigger_ts) <= 120) {
            $payload_waha = json_encode([
                'chatId' => $target_jid,
                'text' => $final_message,
                'session' => 'default'
            ]);

            $endpoints = ['http://127.0.0.1:3000/api/sendText', 'http://localhost:3000/api/sendText'];
            foreach ($endpoints as $endpoint_url) {
                try {
                    $ch = curl_init($endpoint_url);
                    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
                    curl_setopt($ch, CURLOPT_POST, true);
                    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload_waha);
                    curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json', 'X-Api-Key: 123']);
                    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
                    $res_waha = curl_exec($ch);
                    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
                    curl_close($ch);

                    if ($http_code == 200 || $http_code == 201) {
                        $waha_sent = true;
                        if ($alarm_id && isset($pdo)) {
                            try {
                                $upd = $pdo->prepare("UPDATE sunfra_custom_alarms SET status = 'sent' WHERE id = :id");
                                $upd->execute([':id' => $alarm_id]);
                            } catch (\\Exception $ex) {}
                        }
                        break;
                    }
                } catch (\\Exception $ex_waha) {}
            }
        }

        if (!$wants_json) {
            header('Content-Type: text/html; charset=utf-8');
            ?>
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
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
                    <div class="badge"><?php echo $waha_sent ? 'SENT IMMEDIATELY ✅' : 'RECORDED & QUEUED IN DATABASE 🕒'; ?></div>
                    
                    <div class="box">
                        <p><strong>Recipient:</strong> <?php echo htmlspecialchars($target_jid); ?></p>
                        <p><strong>Name:</strong> <?php echo htmlspecialchars($person_name ? $person_name : 'N/A'); ?></p>
                        <p><strong>Trigger Time:</strong> <?php echo htmlspecialchars($trigger_time); ?></p>
                        <p><strong>Message:</strong><br><?php echo nl2br(htmlspecialchars($final_message)); ?></p>
                    </div>

                    <a href="javascript:history.back()">⬅ Go Back</a>
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
        exit;
    }
}
"""

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

if 'Standalone API & URL Link Reminder Trigger Handler' not in code:
    marker = "date_default_timezone_set('Asia/Kolkata');"
    if marker in code:
        new_code = code.replace(marker, marker + "\n" + handler_code)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print("Inserted URL link trigger handler right at top of index1.php!")
    else:
        print("Marker not found in index1.php")
else:
    print("Already inserted handler in index1.php")
