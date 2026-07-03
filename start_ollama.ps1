# Set environment variable globally for User (so it persists across reboots)
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0', 'User')

# Set environment variable for the current script session
$env:OLLAMA_HOST = '0.0.0.0'

# Stop any running instances of Ollama
Stop-Process -Name "ollama" -Force -ErrorAction SilentlyContinue

# Wait 2 seconds for clean shutdown
Start-Sleep -Seconds 2

# Start Ollama service in the background
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden

Write-Output "Ollama restarted with OLLAMA_HOST=0.0.0.0 in the background!"
