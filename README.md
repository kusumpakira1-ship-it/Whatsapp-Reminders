# WhatsApp Business Automation System

This is a complete Docker-based WhatsApp Business automation system tailored for egg trading management. It leverages WAHA (WhatsApp HTTP API) for messaging, a PHP 8.3 backend for logic, and MySQL 8 for data storage.

## Features
- **WAHA Integration**: Receives and sends WhatsApp messages.
- **PHP Webhook**: Processes incoming messages.
- **AI Parser (Heuristics)**: Extracts farm names, transaction types, prices, and quantities from text like "Farm1 sold 100 trays at 520".
- **Profit/Loss Engine**: Calculates daily sales, purchases, transport, commission, and net profit.
- **Automated Cron Jobs**: Sends daily manager reports (8 PM) and hourly reminders.

## Project Structure
```
/project
├── docker-compose.yml
├── .env
├── php/
│ ├── Dockerfile
│ ├── webhook.php
│ ├── send_message.php
│ ├── ai_parser.php
│ ├── profit_engine.php
│ ├── reminder_job.php
│ ├── report_job.php
│ └── config.php
├── sql/
│ └── schema.sql
└── README.md
```

## Deployment Instructions

### Option 1: Windows (Local or Server)

1. **Install Docker Desktop**: Download and install Docker Desktop for Windows from [docker.com](https://www.docker.com/products/docker-desktop/).
2. **Start Docker**: Open the application and ensure the Docker engine is running in the background.
3. **Open Terminal**: Open PowerShell or Command Prompt, and navigate to the project folder where `docker-compose.yml` is located:
   ```cmd
   cd "C:\Users\sunfra\Desktop\Whatsapp Reminders"
   ```
4. **Configure variables**: Open the `.env` file and update your `DB_PASS` and `MANAGER_PHONE`.
5. **Start Containers**:
   ```cmd
   docker compose up -d --build
   ```

### Option 2: Ubuntu 24.04 VPS (Production)

#### 1. Install Docker & Docker Compose
Connect to your VPS via SSH and run:
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker packages
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 2. Prepare the Project
Clone or copy this project to your VPS. Navigate to the project directory:
```bash
cd /path/to/whatsapp_automation
```

Configure your environment variables:
```bash
# Update .env file with your secure DB_PASS and actual MANAGER_PHONE
nano .env
```
*Note: Make sure MANAGER_PHONE is in international format without the '+' sign (e.g., 919876543210).*

### 3. Start Containers
Build and run the stack:
```bash
sudo docker compose up -d --build
```
This will start WAHA (port 3000), PHP backend (port 8080), MySQL (port 3306), and phpMyAdmin (port 8081). The SQL schema is automatically imported on the first run.

### 4. Connect WAHA
1. Open WAHA Dashboard in your browser: `http://<your-vps-ip>:3000/dashboard`
2. Start the `default` session.
3. Scan the QR code with your WhatsApp Business app (Linked Devices).

### 5. Configure Webhook
In the WAHA Dashboard (or via API):
1. Navigate to the Webhooks section.
2. Set the Webhook URL to: `http://php_app:80/webhook.php` (Using the internal Docker hostname).
3. Subscribe to the `message.any` or `message` event.

### 6. Test the Message Flow
1. Send a message to your WAHA-connected WhatsApp number from another number: 
   `Farm1 sold 100 trays at 520`
2. Go to phpMyAdmin: `http://<your-vps-ip>:8081` (Log in with user: `root` and password from `.env`).
3. Check the `whatsapp_auto` database -> `whatsapp_messages` and `sales` tables. The data should be parsed and inserted.

### 7. Cron Jobs Setup
The PHP Docker container automatically sets up cron jobs.
- The `reminder_job.php` runs every hour.
- The `report_job.php` runs every day at 20:00 (8 PM container time).
Check cron logs inside the container if needed:
```bash
sudo docker exec -it php_app tail -f /var/log/cron.log
```
