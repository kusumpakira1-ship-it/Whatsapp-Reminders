<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$_GET['api'] = 'tasks';

try {
    require_once __DIR__ . '/index.php';
} catch (Throwable $e) {
    echo "<h1>PHP ERROR CATCHED</h1>";
    echo "<pre>" . $e->getMessage() . "\n" . $e->getTraceAsString() . "</pre>";
}
