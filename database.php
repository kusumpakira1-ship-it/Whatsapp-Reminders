<?php
// Hostinger MySQL Connection with Persistent Connections & Failover Protection
$host = '145.223.17.70';
$db   = 'u632391467_kusumpakira';
$user = 'u632391467_kusumpakira';
$pass = 'Kusum@2026Bb!';
$charset = 'utf8mb4';

$dsn = "mysql:host=$host;dbname=$db;charset=$charset";
$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    PDO::ATTR_EMULATE_PREPARES   => false,
    PDO::ATTR_PERSISTENT         => true, // REUSE OPEN CONNECTIONS TO PREVENT 500 MAX CONNECTIONS PER HOUR LIMIT
];

$pdo = null;
try {
    $pdo = new PDO($dsn, $user, $pass, $options);
    $pdo->query("SELECT 1");
} catch (\Exception $e) {
    $pdo = null;
    // If MySQL hourly connection quota (1226) or connection fails, fallback seamlessly to SQLite
    $sqlite_paths = [
        __DIR__ . '/whatsapp_reminders.sqlite',
        __DIR__ . '/frontend/whatsapp_reminders.sqlite',
        dirname(__DIR__) . '/whatsapp_reminders.sqlite'
    ];
    foreach ($sqlite_paths as $spath) {
        if (file_exists($spath)) {
            try {
                $pdo = new PDO('sqlite:' . $spath);
                $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
                break;
            } catch (\Exception $sqle) {}
        }
    }
}

