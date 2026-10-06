<?php
// task_allotment/cron_1030_report.php
// Automated daily 10:30 PM Summary Report Cron Job
// Sends member summary reports directly to Manager (917259510983@c.us)

require_once __DIR__ . '/db.php';

date_default_timezone_set('Asia/Kolkata');
$targetDate = date('Y-m-d');
$managerJid = '917259510983@c.us'; // Target manager recipient

// 1. Fetch Report JSON from local API logic
$apiUrl = "http://127.0.0.1/task_allotment/api.php?action=get_summary_report&date=" . $targetDate;
$reportData = null;

$ch = curl_init($apiUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 10);
$res = curl_exec($ch);
curl_close($ch);

if ($res) {
    $reportData = json_decode($res, true);
}

if (!$reportData || empty($reportData['member_reports'])) {
    echo "No member reports found for {$targetDate}.\n";
    exit;
}

$memberReports = $reportData['member_reports'];

$wahaUrls = [
    "http://host.docker.internal:3000/api/sendText",
    "http://waha:3000/api/sendText",
    "http://127.0.0.1:3000/api/sendText",
    "http://localhost:3000/api/sendText"
];

foreach ($memberReports as $item) {
    $memberName = $item['member_name'];
    $mReportText = $item['report_text'];

    echo "\n----------------------------------------\n";
    echo "Sending 10:30 Summary Report for {$memberName} to Manager ({$managerJid})...\n";
    echo $mReportText . "\n";

    $wahaPayload = json_encode([
        "session" => "default",
        "chatId" => $managerJid,
        "text" => $mReportText
    ]);

    $sent = false;
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
            curl_setopt($ch, CURLOPT_TIMEOUT, 5);
            $res = curl_exec($ch);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);

            if ($code == 200 || $code == 201) {
                $sent = true;
                echo "SUCCESS: Summary report for {$memberName} sent to {$managerJid} via {$wahaUrl}\n";
                break;
            }
        } catch (\Exception $e) {}
    }

    if (!$sent) {
        echo "NOTE: WAHA dispatch returned error for {$memberName}.\n";
    }
}
