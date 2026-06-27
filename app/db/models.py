from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, JSON, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from db.database import Base

class Whitelist(Base):
    __tablename__ = "whitelist"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, index=True)
    group_id = Column(String(100), unique=True, index=True)
    enabled_flag = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class RawMessage(Base):
    __tablename__ = "raw_messages"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    sender = Column(String(100), nullable=False)
    group_name = Column(String(255))
    timestamp = Column(DateTime, nullable=False)
    message_type = Column(String(50), nullable=False)
    raw_text = Column(Text)
    media_url = Column(Text)
    media_path = Column(String(500))
    full_webhook_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

class ProcessedData(Base):
    __tablename__ = "processed_data"
    id = Column(Integer, primary_key=True, index=True)
    shead_name = Column(String(255))
    category = Column(Enum('egg', 'feed', 'medicine', 'mortality', 'sales', 'purchase', 'expense', 'unknown'), default='unknown')
    quantity = Column(DECIMAL(15, 2))
    unit = Column(String(50))
    amount = Column(DECIMAL(15, 2), default=0.0)
    notes = Column(Text)
    sender = Column(String(100), nullable=False)
    group_name = Column(String(255))
    source_type = Column(Enum('text', 'image', 'document'), default='text')
    confidence_score = Column(DECIMAL(3, 2))
    processed_time = Column(DateTime, nullable=False)
    message_id = Column(String(255), ForeignKey("raw_messages.message_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

class ReportRecipient(Base):
    __tablename__ = "report_recipients"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
