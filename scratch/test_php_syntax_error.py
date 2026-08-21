"""
Capture local PHP error on index.php using xampp php if available
"""
import subprocess
import os

php_bin = 'php'
if os.path.exists(r'C:\xampp\php\php.exe'):
    php_bin = r'C:\xampp\php\php.exe'

cmd = [php_bin, '-r', """
ini_set('display_errors', 1);
error_reporting(E_ALL);
$_GET['api'] = 'reminders';
$_SERVER['REQUEST_METHOD'] = 'GET';
require_once 'c:/Users/sunfra/Desktop/Whatsapp New Reminders/index.php';
"""]

try:
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("PHP STDOUT:", res.stdout)
    print("PHP STDERR:", res.stderr)
except Exception as e:
    print("Error:", e)
