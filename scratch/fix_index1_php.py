import sys, os

file_path = r'C:\Users\sunfra\AppData\Roaming\Antigravity IDE\User\globalStorage\humy2833.ftp-simple\remote-workspace-temp\cedad10937994543724efa30b6e53514\index1.php'

with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    code = f.read()

target_block = """        if ($apiAction === 'check_queue') {
            @ob_clean();
            header('Content-Type: application/json; charset=utf-8');
            try {
                $rows = $db->query("SELECT * FROM sunfra_custom_alarms ORDER BY id DESC LIMIT 10")->fetchAll();
                echo json_encode(['success' => true, 'count' => count($rows), 'rows' => $rows], JSON_PRETTY_PRINT);
            } catch (Throwable $e) {
                echo json_encode(['success' => false, 'error' => $e->getMessage()]);
            }
            exit;
        }
            @ob_clean();
            header('Content-Type: application/json; charset=utf-8');"""

replacement_block = """        if ($apiAction === 'check_queue') {
            @ob_clean();
            header('Content-Type: application/json; charset=utf-8');
            try {
                $rows = $db->query("SELECT * FROM sunfra_custom_alarms ORDER BY id DESC LIMIT 10")->fetchAll();
                echo json_encode(['success' => true, 'count' => count($rows), 'rows' => $rows], JSON_PRETTY_PRINT);
            } catch (Throwable $e) {
                echo json_encode(['success' => false, 'error' => $e->getMessage()]);
            }
            exit;
        }

        if ($apiAction === 'send_now' || $apiAction === 'dispatch_group') {
            @ob_clean();
            header('Content-Type: application/json; charset=utf-8');"""

if target_block in code:
    new_code = code.replace(target_block, replacement_block)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("FIXED index1.php successfully!")
else:
    print("Target block not found, searching with regex...")
    import re
    new_code = re.sub(
        r"if\s*\(\$apiAction\s*===\s*'check_queue'\)\s*\{.*?exit;\s*\}\s*@ob_clean\(\);",
        replacement_block,
        code,
        flags=re.DOTALL
    )
    if new_code != code:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_code)
        print("FIXED index1.php via regex!")
    else:
        print("Could not locate block in index1.php")
