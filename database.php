<?php
// Remote MySQL database connection configuration
try {
    $pdo = new PDO("mysql:host=145.223.17.70;dbname=u632391467_kusumpakira;charset=utf8mb4", "u632391467_kusumpakira", "Kusum@2026Bb!");
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}
