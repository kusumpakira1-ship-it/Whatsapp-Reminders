"""
Test PHP website verification for 17 Aug 2026
"""
import sys
sys.path.append(r'c:\Users\sunfra\Desktop\Whatsapp New Reminders\backend')
sys.stdout.reconfigure(encoding='utf-8')

import subprocess

cmd = ['php', '-r', """
require_once 'c:/Users/sunfra/Desktop/Whatsapp New Reminders/index.php';
$pdo = get_db_connection();
$date = '2026-08-17';
$stmt = $pdo->prepare("SELECT * FROM sunfra_unified_reminders WHERE active = 1");
$stmt->execute();
$reminders = $stmt->fetchAll(PDO::FETCH_ASSOC);

$groups_map = get_all_sunfra_groups($pdo);

$stmt_raw = $pdo->prepare("SELECT * FROM sunfra_raw_messages WHERE DATE(timestamp) = ?");
$stmt_raw->execute([$date]);
$raw_messages = $stmt_raw->fetchAll(PDO::FETCH_ASSOC);

$stmt_proc = $pdo->prepare("SELECT * FROM sunfra_processed_data WHERE DATE(processed_time) = ?");
$stmt_proc->execute([$date]);
$processed_data = $stmt_proc->fetchAll(PDO::FETCH_ASSOC);

foreach ($reminders as $r) {
    if (strpos($r['person_name'], 'Accounts Poultry') !== false || strpos($r['person_name'], 'Corporate') !== false || strpos($r['task_notes'] ?? '', 'Corporate') !== false) {
        echo "=== REMINDER: " . $r['person_name'] . " (" . $r['report_types'] . ") ===\n";
        $ver = verify_report_submission_status($r, $date, $raw_messages, $processed_data, $groups_map);
        print_r($ver['sub_reports_status']);
        echo "\n";
    }
}
"""]

res = subprocess.run(cmd, capture_output=True, text=True)
print("PHP STDOUT:")
print(res.stdout)
print("PHP STDERR:")
print(res.stderr)
