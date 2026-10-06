<?php
// task_allotment/api.php
header('Content-Type: application/json; charset=utf-8');
require_once __DIR__ . '/db.php';

$pdo = get_task_db();
$action = $_GET['action'] ?? $_POST['action'] ?? '';

try {
    switch ($action) {

        // --- MEMBERS API ---
        case 'get_members':
            $stmt = $pdo->query("SELECT * FROM task_allotment_members ORDER BY name ASC");
            echo json_encode(['success' => true, 'data' => $stmt->fetchAll()]);
            break;

        case 'add_member':
            $name = trim($_POST['name'] ?? '');
            $phone = trim($_POST['phone'] ?? '');
            if (!$name || !$phone) {
                echo json_encode(['success' => false, 'message' => 'Name and phone number are required']);
                exit;
            }
            $stmt = $pdo->prepare("INSERT INTO task_allotment_members (name, phone) VALUES (?, ?)");
            $stmt->execute([$name, $phone]);
            echo json_encode(['success' => true, 'id' => $pdo->lastInsertId(), 'name' => $name, 'phone' => $phone]);
            break;

        case 'update_member':
            $id = intval($_POST['id'] ?? 0);
            $name = trim($_POST['name'] ?? '');
            $phone = trim($_POST['phone'] ?? '');
            if (!$id || !$name || !$phone) {
                echo json_encode(['success' => false, 'message' => 'Invalid parameters']);
                exit;
            }
            $stmt = $pdo->prepare("UPDATE task_allotment_members SET name = ?, phone = ? WHERE id = ?");
            $stmt->execute([$name, $phone, $id]);
            echo json_encode(['success' => true]);
            break;

        case 'delete_member':
            $id = intval($_POST['id'] ?? 0);
            if (!$id) {
                echo json_encode(['success' => false, 'message' => 'Invalid ID']);
                exit;
            }
            $stmt = $pdo->prepare("DELETE FROM task_allotment_members WHERE id = ?");
            $stmt->execute([$id]);
            echo json_encode(['success' => true]);
            break;

        // --- TASK PRESETS API ---
        case 'get_presets':
            $stmt = $pdo->query("SELECT * FROM task_allotment_presets ORDER BY title ASC");
            echo json_encode(['success' => true, 'data' => $stmt->fetchAll()]);
            break;

        case 'add_preset':
            $title = trim($_POST['title'] ?? '');
            if (!$title) {
                echo json_encode(['success' => false, 'message' => 'Task title is required']);
                exit;
            }
            $stmt = $pdo->prepare("INSERT INTO task_allotment_presets (title) VALUES (?)");
            $stmt->execute([$title]);
            echo json_encode(['success' => true, 'id' => $pdo->lastInsertId(), 'title' => $title]);
            break;

        case 'update_preset':
            $id = intval($_POST['id'] ?? 0);
            $title = trim($_POST['title'] ?? '');
            if (!$id || !$title) {
                echo json_encode(['success' => false, 'message' => 'Invalid parameters']);
                exit;
            }
            $stmt = $pdo->prepare("UPDATE task_allotment_presets SET title = ? WHERE id = ?");
            $stmt->execute([$title, $id]);
            echo json_encode(['success' => true]);
            break;

        case 'delete_preset':
            $id = intval($_POST['id'] ?? 0);
            if (!$id) {
                echo json_encode(['success' => false, 'message' => 'Invalid ID']);
                exit;
            }
            $stmt = $pdo->prepare("DELETE FROM task_allotment_presets WHERE id = ?");
            $stmt->execute([$id]);
            echo json_encode(['success' => true]);
            break;

        // --- TASK ALLOTMENT API ---
        case 'allot_tasks':
            $inputJson = file_get_contents('php://input');
            $payload = json_decode($inputJson, true) ?: $_POST;

            $memberIds = $payload['member_ids'] ?? [];
            $tasks = $payload['tasks'] ?? [];
            $group = $payload['whatsapp_group'] ?? 'No Group / Private Only';
            $notes = trim($payload['notes'] ?? '');
            $assignedDate = date('Y-m-d');

            if (empty($memberIds) || empty($tasks)) {
                echo json_encode(['success' => false, 'message' => 'Select at least one member and one task.']);
                exit;
            }

            // Fetch member details
            $inClause = implode(',', array_map('intval', $memberIds));
            $members = $pdo->query("SELECT * FROM task_allotment_members WHERE id IN ($inClause)")->fetchAll();

            $createdCount = 0;
            $stmt = $pdo->prepare("INSERT INTO task_allotments 
                (member_id, member_name, member_phone, task_title, whatsapp_group, notes, assigned_date, status) 
                VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')");

            foreach ($members as $m) {
                $assignedTasksList = [];
                foreach ($tasks as $t) {
                    $stmt->execute([
                        $m['id'],
                        $m['name'],
                        $m['phone'],
                        $t,
                        $group,
                        $notes,
                        $assignedDate
                    ]);
                    $createdCount++;
                    $assignedTasksList[] = "  • " . $t;
                }

                // Send Instant WhatsApp Notification to assigned member
                $mPhone = preg_replace('/[^\d]/', '', $m['phone']);
                if (strlen($mPhone) == 10) {
                    $mPhone = '91' . $mPhone;
                }
                $targetJid = $mPhone ? ($mPhone . '@c.us') : '';

                $taskBulletPoints = implode("\n", $assignedTasksList);
                $notifyMsg = "🔔 *NEW TASK ASSIGNED*\n\n";
                $notifyMsg .= "Hello *{$m['name']}*,\n\n";
                $notifyMsg .= "You have been assigned the following task(s):\n";
                $notifyMsg .= "{$taskBulletPoints}\n";
                if ($notes) {
                    $notifyMsg .= "\n📝 *Notes*: {$notes}\n";
                }

                $notifyMsg .= "\n👉 To mark a task done, reply with the Task Name and *\"Completed\"* or *\"Done\"* once finished.";

                send_whatsapp_task_notification($pdo, $targetJid, $m['name'], $m['phone'], $notifyMsg);
            }

            echo json_encode([
                'success' => true, 
                'message' => "Successfully allotted $createdCount task(s) to " . count($members) . " member(s) and sent WhatsApp notifications!"
            ]);
            break;

        case 'get_allotments':
            $date = $_GET['date'] ?? date('Y-m-d');
            $stmt = $pdo->prepare("SELECT * FROM task_allotments WHERE assigned_date = ? ORDER BY id DESC");
            $stmt->execute([$date]);
            echo json_encode(['success' => true, 'data' => $stmt->fetchAll()]);
            break;

        case 'toggle_status':
            $id = intval($_POST['id'] ?? 0);
            $status = $_POST['status'] ?? 'completed'; // 'completed', 'failed', 'pending'
            $completedAt = ($status === 'completed') ? date('Y-m-d H:i:s') : null;

            $stmt = $pdo->prepare("UPDATE task_allotments SET status = ?, completed_at = ? WHERE id = ?");
            $stmt->execute([$status, $completedAt, $id]);
            echo json_encode(['success' => true]);
            break;

        case 'delete_allotment':
            $id = intval($_POST['id'] ?? 0);
            $stmt = $pdo->prepare("DELETE FROM task_allotments WHERE id = ?");
            $stmt->execute([$id]);
            echo json_encode(['success' => true]);
            break;

        // --- FETCH GROUPS (FOR DROPDOWN) ---
        case 'get_groups':
            $groups = [];
            try {
                $gStmt = $pdo->query("SELECT name FROM sunfra_groups ORDER BY name ASC");
                $groups = $gStmt->fetchAll(PDO::FETCH_COLUMN);
            } catch (\Exception $e) {}
            if (empty($groups)) {
                $groups = ['General Farm Updates', 'Management Group', 'Operations WhatsApp'];
            }
            echo json_encode(['success' => true, 'data' => $groups]);
            break;

        // --- 10:30 SUMMARY REPORT GENERATOR ---
        case 'get_summary_report':
            $targetDate = $_GET['date'] ?? date('Y-m-d');
            
            // Check for WhatsApp completions from raw messages
            sync_whatsapp_completions($pdo, $targetDate);

            // Fetch tasks for target date
            $stmt = $pdo->prepare("SELECT * FROM task_allotments WHERE assigned_date = ? ORDER BY member_name ASC");
            $stmt->execute([$targetDate]);
            $allotments = $stmt->fetchAll();

            // Group by Member
            $grouped = [];
            foreach ($allotments as $row) {
                $grouped[$row['member_name']][] = $row;
            }

            $dateFormatted = date('d M Y', strtotime($targetDate));
            $weekStart = date('Y-m-d', strtotime('monday this week', strtotime($targetDate)));
            $weekEnd = date('Y-m-d', strtotime('sunday this week', strtotime($targetDate)));
            $monthStart = date('Y-m-01', strtotime($targetDate));
            $monthEnd = date('Y-m-t', strtotime($targetDate));

            $memberReports = [];
            $allReportsCombined = "";

            if (empty($grouped)) {
                $allReportsCombined = "📋 *DAILY TASK SUMMARY REPORT*\n📅 *Date*: {$dateFormatted}\n----------------------------------------\n\n_No tasks were allotted for today._\n";
            } else {
                foreach ($grouped as $memberName => $tasksList) {
                    $mId = $tasksList[0]['member_id'];
                    $mPhone = $tasksList[0]['member_phone'];

                    // Calculate metrics specifically for this member
                    $fTodayStmt = $pdo->prepare("SELECT COUNT(*) FROM task_allotments WHERE member_name = ? AND assigned_date = ? AND status = 'failed'");
                    $fTodayStmt->execute([$memberName, $targetDate]);
                    $failedToday = $fTodayStmt->fetchColumn();

                    $fWeekStmt = $pdo->prepare("SELECT COUNT(*) FROM task_allotments WHERE member_name = ? AND assigned_date BETWEEN ? AND ? AND status = 'failed'");
                    $fWeekStmt->execute([$memberName, $weekStart, $weekEnd]);
                    $failedWeek = $fWeekStmt->fetchColumn();

                    $fMonthStmt = $pdo->prepare("SELECT COUNT(*) FROM task_allotments WHERE member_name = ? AND assigned_date BETWEEN ? AND ? AND status = 'failed'");
                    $fMonthStmt->execute([$memberName, $monthStart, $monthEnd]);
                    $failedMonth = $fMonthStmt->fetchColumn();

                    $totalTasks = count($tasksList);

                    // Build member individual report
                    $mReportText = "📋 *DAILY TASK SUMMARY REPORT*\n";
                    $mReportText .= "📅 *Date*: {$dateFormatted}\n";
                    $mReportText .= "----------------------------------------\n\n";
                    $mReportText .= "👤 *{$memberName}*:\n";
                    foreach ($tasksList as $t) {
                        $icon = ($t['status'] === 'completed') ? "✔️" : "❌";
                        $statusTxt = ($t['status'] === 'completed') ? "Completed" : "Failed / Pending";
                        $mReportText .= "  • {$t['task_title']}: {$icon} {$statusTxt}\n";
                    }
                    $mReportText .= "\n----------------------------------------\n";
                    $mReportText .= "❌ Failed today: {$failedToday}\n";
                    $mReportText .= "❌ Failed this week: {$failedWeek}\n";
                    $mReportText .= "❌ Failed this month: {$failedMonth}\n";
                    $mReportText .= "📋 Total tasks: {$totalTasks}\n";

                    $memberReports[] = [
                        'member_name' => $memberName,
                        'member_phone' => $mPhone,
                        'report_text' => $mReportText
                    ];

                    $allReportsCombined .= $mReportText . "\n========================================\n\n";
                }
            }

            echo json_encode([
                'success' => true,
                'date' => $targetDate,
                'member_reports' => $memberReports,
                'report_text' => trim($allReportsCombined)
            ]);
            break;

        default:
            echo json_encode(['success' => false, 'message' => 'Invalid action']);
            break;
    }
} catch (\Exception $e) {
    echo json_encode(['success' => false, 'error' => $e->getMessage()]);
}

/**
 * Auto-detects WhatsApp messages sent by members containing Task Name & "completed", "done", etc.
 */
function sync_whatsapp_completions($pdo, $assignedDate) {
    try {
        // Query pending tasks for today
        $stmt = $pdo->prepare("SELECT * FROM task_allotments WHERE assigned_date = ? AND status = 'pending' ORDER BY id ASC");
        $stmt->execute([$assignedDate]);
        $pending = $stmt->fetchAll();

        if (empty($pending)) return;

        // Group pending tasks by member phone/name
        $pendingByMember = [];
        foreach ($pending as $t) {
            $key = strtolower($t['member_name']);
            $pendingByMember[$key][] = $t;
        }

        // Try reading raw messages from sunfra_raw_messages or sunfra_whatsapp_messages
        $msgs = [];
        try {
            $mStmt = $pdo->prepare("SELECT sender, raw_text FROM sunfra_raw_messages WHERE DATE(created_at) = ?");
            $mStmt->execute([$assignedDate]);
            $msgs = $mStmt->fetchAll();
        } catch (\Exception $ex) {
            try {
                $mStmt = $pdo->prepare("SELECT sender_id as sender, message_text as raw_text FROM sunfra_whatsapp_messages WHERE DATE(timestamp) = ?");
                $mStmt->execute([$assignedDate]);
                $msgs = $mStmt->fetchAll();
            } catch (\Exception $ex2) {}
        }

        if (empty($msgs)) return;

        $completionKeywords = ['completed', 'done', 'finished', 'complete', 'khatam', 'ho gaya'];

        foreach ($pendingByMember as $memberName => $memberTasks) {
            $mPhone = preg_replace('/[^0-9]/', '', $memberTasks[0]['member_phone']);

            foreach ($msgs as $msg) {
                $text = strtolower($msg['raw_text'] ?? '');
                $sender = preg_replace('/[^0-9]/', '', $msg['sender'] ?? '');

                // Verify sender match (by phone or name in message)
                $phoneMatch = ($mPhone && strpos($sender, $mPhone) !== false);
                $nameMatch = (strpos($text, $memberName) !== false);

                if (!$phoneMatch && !$nameMatch) continue;

                // Check completion keyword
                $hasKeyword = false;
                foreach ($completionKeywords as $kw) {
                    if (strpos($text, $kw) !== false) {
                        $hasKeyword = true;
                        break;
                    }
                }

                if (!$hasKeyword) continue;

                // Match ALWAYS by Task Name / Task Title Keywords
                foreach ($memberTasks as $mt) {
                    $tTitle = strtolower($mt['task_title']);
                    
                    // Exact or substring match of full Task Name
                    $exactNameMatch = (strpos($text, $tTitle) !== false);
                    
                    // Word-by-word term match from Task Name
                    $words = array_filter(explode(' ', $tTitle), function($w) { return strlen($w) >= 3; });
                    $wordMatchCount = 0;
                    foreach ($words as $w) {
                        if (strpos($text, $w) !== false) {
                            $wordMatchCount++;
                        }
                    }

                    if ($exactNameMatch || ($wordMatchCount > 0 && $wordMatchCount >= count($words)/2)) {
                        $upd = $pdo->prepare("UPDATE task_allotments SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?");
                        $upd->execute([$mt['id']]);
                    }
                }

                // Single pending task fallback
                if (count($memberTasks) === 1 && $hasKeyword) {
                    $targetTask = $memberTasks[0];
                    $upd = $pdo->prepare("UPDATE task_allotments SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?");
                    $upd->execute([$targetTask['id']]);
                }
            }
        }
    } catch (\Exception $e) {}
}

/**
 * Sends instant WhatsApp task assignment notification to member via WAHA API and records fallback log.
 */
function send_whatsapp_task_notification($pdo, $targetJid, $personName, $personPhone, $messageText) {
    if (!$targetJid) return;

    $wahaUrls = [
        "http://host.docker.internal:3000/api/sendText",
        "http://waha:3000/api/sendText",
        "http://127.0.0.1:3000/api/sendText",
        "http://localhost:3000/api/sendText"
    ];

    $wahaPayload = json_encode([
        "session" => "default",
        "chatId" => $targetJid,
        "text" => $messageText
    ]);

    foreach ($wahaUrls as $wahaUrl) {
        try {
            $ch = curl_init($wahaUrl);
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            curl_setopt($ch, CURLOPT_POST, true);
            curl_setopt($ch, CURLOPT_POSTFIELDS, $wahaPayload);
            curl_setopt($ch, CURLOPT_HTTPHEADER, [
                "Content-Type: application/json",
                "X-Api-Key: 123"
            ]);
            curl_setopt($ch, CURLOPT_TIMEOUT, 4);
            $res = curl_exec($ch);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($code == 200 || $code == 201) {
                break;
            }
        } catch (\Exception $e) {}
    }

    // Queue into DB for fallback and audit log
    try {
        $stmt = $pdo->prepare("INSERT INTO sunfra_unified_reminders (person_name, person_phone, whatsapp_group_id, report_types, task_notes, trigger_time, frequency, repeat_interval, status, created_at) VALUES (?, ?, ?, 'Task Assignment Notification', ?, CURRENT_TIMESTAMP, 'once', 'none', 'sent', CURRENT_TIMESTAMP)");
        $stmt->execute([$personName, $personPhone, $targetJid, $messageText]);
    } catch (\Exception $e) {}
}
