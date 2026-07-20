from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Text, Enum, JSON, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from database import Base

class SystemSetting(Base):
    __tablename__ = "sunfra_system_settings"
    key = Column(String(50), primary_key=True, index=True)
    value = Column(Text)

class CustomAlarm(Base):
    __tablename__ = "sunfra_custom_alarms"
    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String(20), nullable=False) # 'employee' or 'group'
    target_id = Column(Integer, nullable=True) # Can be null for group target using whatsapp_target_id
    whatsapp_target_id = Column(String(255), nullable=True)
    report_type = Column(String(50), nullable=True)
    frequency = Column(String(20), default='once') # 'once', 'daily', 'weekly', 'monthly', 'yearly', 'timer'
    repeat_interval = Column(String(20), default='none') # 'none', '5m', '10m', '15m', '30m', '1h'
    task_notes = Column(Text, nullable=False)
    trigger_time = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending') # 'pending', 'sent', 'cancelled'
    created_at = Column(DateTime, default=func.now())

class Whitelist(Base):
    __tablename__ = "sunfra_whitelist"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, index=True)
    group_id = Column(String(100), unique=True, index=True)
    enabled_flag = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class RawMessage(Base):
    __tablename__ = "sunfra_raw_messages"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    sender = Column(String(100), nullable=False)
    group_name = Column(String(255))
    timestamp = Column(DateTime, nullable=False)
    message_type = Column(String(50), nullable=False)
    raw_text = Column(Text)
    media_path = Column(String(500))
    full_webhook_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())

class WhatsAppMessage(Base):
    __tablename__ = "sunfra_whatsapp_messages"
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String(255), unique=True, index=True, nullable=False)
    group_id = Column(String(255), index=True, nullable=False)
    sender_id = Column(String(255), index=True, nullable=False)
    message_text = Column(Text)
    timestamp = Column(DateTime, nullable=False)

class ProcessedData(Base):
    __tablename__ = "sunfra_processed_data"
    id = Column(Integer, primary_key=True, index=True)
    shead_name = Column(String(255))
    category = Column(Enum(
        'egg_collection_1', # Morning (1st) egg collection
        'egg_collection_2', # Evening (2nd) egg collection
        'egg_collection',   # General egg collection (unspecified round)
        'hen_weight',       # Hen body weight measurement
        'mortality',        # Hen/bird deaths
        'egg_loaded',       # Eggs dispatched / loaded onto trucks
        'egg_unloaded',     # Eggs received / returned / unloaded
        'production',       # General flock stats
        'sales',            # Egg sales revenue
        'feed',             # Feed / fodder given
        'raw_material',     # Other farm input materials
        'medicine',         # Medicine / vaccines / treatments
        'expense',          # General operational expenses
        'purchase',         # Equipment / asset purchases
        'egg',              # Legacy general egg record
        'unknown'           # Cannot be classified
    ), default='unknown')
    quantity = Column(DECIMAL(15, 2))
    unit = Column(String(50))
    amount = Column(DECIMAL(15, 2), default=0.0)
    notes = Column(Text)
    sender = Column(String(100), nullable=False)
    group_name = Column(String(255))
    source_type = Column(Enum('text', 'image', 'document'), default='text')
    confidence_score = Column(DECIMAL(3, 2))
    processed_time = Column(DateTime, nullable=False)
    message_id = Column(String(255), ForeignKey("sunfra_raw_messages.message_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())

class ReportRecipient(Base):
    __tablename__ = "sunfra_report_recipients"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(50), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Group(Base):
    __tablename__ = "sunfra_groups"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    whatsapp_group_id = Column(String(255), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=func.now())

class Employee(Base):
    __tablename__ = "sunfra_employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=False)
    group_id = Column(Integer, ForeignKey("sunfra_groups.id", ondelete="CASCADE"), nullable=True)
    whatsapp_group_id = Column(String(255), nullable=True)
    report_responsibility = Column(String(100), nullable=True) # e.g. 'egg_collection', 'feed', 'sales'
    created_at = Column(DateTime, default=func.now())

class UnifiedReminder(Base):
    __tablename__ = "sunfra_unified_reminders"
    id = Column(Integer, primary_key=True, index=True)
    person_name = Column(String(255), nullable=False)
    person_phone = Column(String(50), nullable=False)
    whatsapp_group_id = Column(String(255), nullable=True)
    report_types = Column(Text, nullable=True)
    task_notes = Column(Text, nullable=True)
    trigger_time = Column(DateTime, nullable=False)
    status = Column(String(20), default='pending')
    frequency = Column(String(20), default='daily')
    repeat_interval = Column(String(20), default='none')
    created_at = Column(DateTime, default=func.now())

class ReminderLog(Base):
    __tablename__ = "sunfra_reminder_logs"
    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey("sunfra_unified_reminders.id", ondelete="SET NULL"), nullable=True)
    report_types = Column(Text, nullable=True)
    person_name = Column(String(255), nullable=True)
    person_phone = Column(String(50), nullable=True)
    whatsapp_group_id = Column(String(255), nullable=True)
    trigger_time = Column(DateTime, nullable=False)
    executed_at = Column(DateTime, default=func.now())
    status = Column(String(20), nullable=False) # 'sent' or 'skipped'
    details = Column(Text, nullable=True)


class Task(Base):
    __tablename__ = "sunfra_tasks"
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(255), nullable=False)
    task_type = Column(String(50), default='general') # 'general', 'approval', 'meeting', 'cleaning', 'personal'
    assigned_person_name = Column(String(255), nullable=True)
    assigned_person_phone = Column(String(100), nullable=True)
    whatsapp_group_id = Column(String(255), nullable=True)
    due_time = Column(DateTime, nullable=False)
    completion_keywords = Column(Text, nullable=True) # e.g. "done, cleaned"
    status = Column(String(20), default='pending') # 'pending', 'pending_approval', 'completed', 'overdue'
    approver_phone = Column(String(100), nullable=True)
    completion_details = Column(Text, nullable=True) # E.g., Wednesday meeting points covered
    frequency = Column(String(20), default='once')
    repeat_interval = Column(String(20), default='none')
    created_at = Column(DateTime, default=func.now())

class EggGodownInventory(Base):
    __tablename__ = "sunfra_egg_godown_inventory"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    opening_balance = Column(Integer, default=0)
    closing_balance = Column(Integer, default=0)
    total_produced = Column(Integer, default=0)

class WAHAEvent(Base):
    __tablename__ = "sunfra_waha_events"
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False) # e.g. 'disconnected', 'reconnected', 'stopped_restart', 'working'
    status = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())



