from waha_service import send_waha_message

group_jid = "120363111757096162@g.us"
msg = (
    "⚠️ *Task Overdue Alert*\n\n"
    "Hi Team,\n"
    "The deadline for task *\"Silo Empty and Cleaning\"* has passed.\n\n"
    "Please complete this work and reply to this message with *\"done\"* or *\"completed\"* once finished."
)
res = send_waha_message(group_jid, msg)
print(f"Formatted Silo Alert Send Status: {res}")
