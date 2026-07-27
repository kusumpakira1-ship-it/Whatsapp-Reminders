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

try {
    $pdo = new PDO($dsn, $user, $pass, $options);
} catch (\PDOException $e) {
    // If MySQL hourly connection quota (1226) or server fails, fallback gracefully to SQLite
    try {
        $sqlite_path = __DIR__ . '/whatsapp_reminders.sqlite';
        $pdo = new PDO('sqlite:' . $sqlite_path);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    } catch (\PDOException $sqle) {
        // Fallback initialized
    }
}
