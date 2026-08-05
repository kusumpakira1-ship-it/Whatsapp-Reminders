from waha_service import send_waha_message

group_jid = "120363410607412989@g.us"
grp_msg = (
    "🔔 *Feed Formula Approval Needed*\n\n"
    "*Task:* Feed Formula - Shed 5 (Updated by Mahalakshmi)\n"
    "*Details:* Updated Feed formula for 5th shed (Removed B rice, added maize)\n"
    "*Status:* Pending Approval 🟡\n\n"
    "Please reply with \"send\" or \"approved\" to confirm."
)

r1 = send_waha_message(group_jid, grp_msg)
print(f"Group Message Dispatch Status: {r1}")

approvers = ["917259510983@c.us", "916364817749@c.us", "917204041105@c.us"]
priv_msg = (
    "🔔 *Feed Formula Approval Needed*\n\n"
    "*Task:* Feed Formula - Shed 5 (Updated by Mahalakshmi)\n"
    "*Details:* Updated Feed formula for 5th shed (Removed B rice, added maize)\n"
    "*Status:* Pending Approval 🟡\n\n"
    "Please reply with \"send\" or \"approved\" to confirm."
)

for app in approvers:
    res = send_waha_message(app, priv_msg)
    print(f"Approver {app} Dispatch Status: {res}")
