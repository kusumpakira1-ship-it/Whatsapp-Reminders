# WhatsApp Business Automation System

This is a complete Docker-based WhatsApp Business automation system tailored for egg trading management. It leverages **WAHA** (WhatsApp HTTP API) for messaging, a scalable **Python/FastAPI** backend for asynchronous logic, **Google Gemini AI** for intelligence, and **MySQL 8** for data storage.

## Features
- **WAHA Integration**: Receives and sends WhatsApp messages automatically.
- **FastAPI Webhook**: Asynchronously processes incoming payloads and routes media.
- **Google Gemini AI (Vision & NLP)**: 
  - Extracts farm names, transaction types, prices, and quantities from text in multiple languages.
  - Automatically performs OCR on images of handwritten receipts and invoices.
  - Parses uploaded PDF/Excel documents.
- **Automated Cron Jobs**: Background `APScheduler` aggregates data and generates daily PDF and Excel manager reports, delivering them via WhatsApp at 11:00 PM.

## Project Structure
```
/project
├── docker-compose.yml
├── .env
├── sql/
│   └── schema.sql (Initial DB Schema)
├── app/
│   ├── Dockerfile (FastAPI Container)
│   ├── requirements.txt
│   ├── main.py (Webhook routing)
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py (SQLAlchemy Schema)
│   └── services/
│       ├── ai_processor.py (Gemini API logic)
│       ├── report_generator.py (PDF/Excel generation)
│       ├── scheduler.py (11 PM Job)
│       └── waha_service.py
```

## How to Run
1. Make sure your `.env` contains `GEMINI_API_KEY` and MySQL database credentials.
2. Run `docker compose up -d --build`.
3. Open `http://localhost:3000/dashboard` and start a WAHA session by scanning the QR Code.
4. Update the WAHA Webhook URL to point to `http://fastapi_backend:8000/webhook` and check `message.any`.

Your system is now live and processing messages into the remote MySQL database!
