# WhatsApp Business Automation & Poultry Farm Management System

This is a complete, enterprise-grade, Docker-based WhatsApp automation system tailored for egg trading and poultry farm management. It integrates **WAHA** (WhatsApp HTTP API) for messaging, **FastAPI** for core webhook backend logic, **Ollama / Google Gemini** for intelligent AI extraction, and **MySQL** for persistent database storage.

---

## 🏗️ System Architecture

```
                      +-------------------+
                      |   WhatsApp App    |
                      +---------+---------+
                                |
                                | (Message Sent)
                                v
                      +---------+---------+
                      |    WAHA Core      | (Port 3000)
                      +---------+---------+
                                |
                                | (HTTP Webhook POST)
                                v
  +-------------------------------------------------------+
  |                   fastapi_backend (Port 8000)         |
  |                                                       |
  |  +---------------+  +---------------+  +-----------+  |
  |  |  Webhook API  |  | AI Processor  |  | Scheduler |  |
  |  +-------+-------+  +-------+-------+  +-----+-----+  |
  +----------|------------------|----------------|--------+
             |                  | (Ollama query) |
             | (SQLAlchemy)     v                | (11 PM Job triggers)
             |            +-----+-----+          |
             |            |  Ollama   |          |
             |            |  Service  |          |
             |            +-----------+          |
             v                                   |
    +--------+--------+                          |
    |    MySQL DB     |                          |
    | (145.223.17.70) | <────────────────────────+ (Generates PDF/XLSX
    +-----------------+                            and dispatches via WAHA)
```

---

## 📁 File Structure & Core Codebases

### 1. Root Configurations
- [.env](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/.env): Environment variables containing MySQL credentials, AI providers, WAHA details, and API keys.
- [docker-compose.yml](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/docker-compose.yml): orchestrates the core containers: WAHA, FastAPI, and phpMyAdmin.

### 2. FastAPI Application Base (`/app`)
- [Dockerfile](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/Dockerfile): Alpine-based python build that sets up FastAPI dependencies (e.g., mysqlclient, reportlab, pandas, openpyxl).
- [main.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/main.py): Entry webhook router. Receives payload events, sanitizes inputs, handles commands (`!report`, `!manager add`), downloads media files, and inserts data into the MySQL database.
- [messages.json](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/messages.json): A local JSON log backup of all arriving messages and their respective AI extractions.

### 3. Database Layer (`/app/db`)
- [database.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/db/database.py): Initializes the SQLAlchemy engine connecting to the remote MySQL host.
- [models.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/db/models.py): Defines DB schemas:
  - `RawMessage`: Original payload log.
  - `ProcessedData`: Extracted farm activity (sheads, collections, mortality, feed, medicine, sales, expenses).
  - `ReportRecipient`: Contacts who receive scheduled reports.
- [update_db.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/update_db.py): Runs migrations to add database columns or modify category enum boundaries.

### 4. Application Services (`/app/services`)
- [ai_processor.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/services/ai_processor.py): Deals with AI integration. Supports two backends:
  - **Gemini**: Directly calls the Google Gemini API with the full system prompt.
  - **Ollama**: Calls local `llama3` running on the host machine using a compressed high-speed prompt to prevent CPU timeouts.
- [report_generator.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/services/report_generator.py): Extracts records from MySQL and formats daily summaries.
  - Generates highly detailed **Excel** spreadsheet tables with dynamic tabs for Egg Collections, Feed & Materials, Medicine, Sales, and P&L.
  - Generates standard **PDF** reports using ReportLab.
  - Outputs a **WhatsApp summary** message listing collections, dispatches, feed, medicine, sales, and total profit/loss calculations.
- [scheduler.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/services/scheduler.py): Runs `APScheduler` background jobs:
  - **6:00 PM**: Send reminders to supervisors to input their farm data.
  - **11:00 PM**: Compile daily report, generate PDF/Excel files, and send them via WAHA.
  - **Weekly/Monthly**: Triggers scheduled financial summaries.
- [waha_service.py](file:///c:/Users/sunfra/Desktop/Whatsapp%20Reminders/app/services/waha_service.py): Wraps WAHA endpoints (`/api/sendText`, `/api/sendFile`, `/api/download`) to handle message sending and media downloads.

---

## 🛠️ Configuration & Setup

### 1. Environment Variables (.env)
```env
# WAHA API configuration
WAHA_URL=http://waha:3000
WAHA_SESSION=default

# Remote MySQL configuration
DB_HOST=145.223.17.70
DB_NAME=u632391467_yaswanth
DB_USER=u632391467_yaswanth
DB_PASS=Yaswanth@2026Cc!

# AI Core configurations (gemini or ollama)
AI_PROVIDER=ollama
GEMINI_API_KEY=AIza...
OLLAMA_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3
OLLAMA_VISION_MODEL=llava
```

### 2. Running the System
```powershell
# 1. Start Docker Desktop on Windows
# 2. Build and start containers
docker compose up -d --build
```

---

## 🤖 AI Categories & Message Syntax

Supervisors can send WhatsApp messages in English, Hindi, Telugu, or broken English. The AI automatically classifies them into the correct fields:

| Category | Description | Example Message |
|---|---|---|
| `egg_collection_1` | Morning / 1st Collection | `Shead 3 morning 250 trays` |
| `egg_collection_2` | Evening / 2nd Collection | `Shead 3 evening 210 trays` |
| `hen_weight` | Hen weight measurement | `Shead 2 hen weight 1.85 kg` |
| `mortality` | Bird deaths | `Shead 1 dead 3 chickens` |
| `feed` | Feed given / consumed | `10 bags feed shead 2` |
| `medicine` | Medicine / Vaccines | `Viracid spray 1kg shead 8` |
| `sales` | Egg sales revenue | `Sold 4000 trays at 5.20 rate` |
| `egg_loaded` | Eggs dispatched / loaded | `Loaded 100 trays to truck` |
| `egg_unloaded` | Returned eggs | `Received 30 trays wapas` |

---

## 💬 WhatsApp Chat Commands

Supervisors and Managers can query or configure the bot directly from their chat:
- `!manager add`: Registers the current chat or group to receive the scheduled 6 PM reminders and 11 PM reports.
- `!report daily`: Generates the P&L report for today immediately and sends it to the chat along with the PDF and Excel sheets.
- `!report weekly`: Generates a summary for the past 7 days.
- `!report monthly`: Generates a summary for the past 30 days.

---

## 🔧 Troubleshooting & Diagnostics

### 1. Check Container Status
```powershell
docker ps
```
Should show three containers active: `fastapi_backend` (Port 8000), `waha` (Port 3000), and `phpmyadmin` (Port 8081).

### 2. View Backend Logs
```powershell
docker logs fastapi_backend --tail 50 -f
```

### 3. Verify Database Migration
If you add new categories or run database modifications:
```powershell
docker exec fastapi_backend python update_db.py
```

### 4. Local Ollama Connection Timeout
If you run Ollama on CPU and get timeouts:
- We set the timeout limit to **300 seconds** (5 minutes).
- We serve a **lightweight system prompt (~140 tokens)** to Ollama to speed up prompt evaluation.
- Ensure Ollama is listening on all network interfaces by starting it with the environment variable `OLLAMA_HOST=0.0.0.0`.
