<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Allotment System</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            --card-bg: #ffffff;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --secondary-btn: #eff6ff;
            --secondary-btn-text: #2563eb;
            --danger: #ef4444;
            --danger-bg: #fef2f2;
            --success: #10b981;
            --text-dark: #1f2937;
            --text-muted: #6b7280;
            --border-color: #e5e7eb;
            --radius: 12px;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background: #f1f5f9;
            color: var(--text-dark);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 24px 16px;
        }

        .main-wrapper {
            width: 100%;
            max-width: 520px;
            background: var(--card-bg);
            border-radius: 20px;
            box-shadow: var(--shadow);
            border: 1px solid rgba(226, 232, 240, 0.8);
            padding: 24px;
        }

        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }

        .app-header h1 {
            font-size: 24px;
            font-weight: 700;
            color: #dc2626; /* Red heading matching red text mockup */
            letter-spacing: -0.5px;
        }

        .report-badge-btn {
            background: #f0fdf4;
            color: #166534;
            border: 1px solid #bbf7d0;
            padding: 6px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }

        .report-badge-btn:hover {
            background: #dcfce7;
        }

        .section-box {
            margin-bottom: 20px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }

        .section-title {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-dark);
        }

        .btn-action-outline {
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }

        .btn-action-outline:hover {
            background: #dbeafe;
        }

        .search-input {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 14px;
            margin-bottom: 10px;
            outline: none;
            transition: border 0.2s;
        }

        .search-input:focus {
            border-color: var(--primary);
        }

        .item-list-box {
            max-height: 180px;
            overflow-y: auto;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 6px;
            background: #fafafa;
        }

        .list-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 10px;
            background: #ffffff;
            border: 1px solid #f1f5f9;
            border-radius: 6px;
            margin-bottom: 6px;
            transition: background 0.15s;
        }

        .list-item:last-child {
            margin-bottom: 0;
        }

        .list-item:hover {
            background: #f8fafc;
        }

        .item-left {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            color: var(--text-dark);
            cursor: pointer;
            user-select: none;
        }

        .item-left input[type="checkbox"] {
            width: 16px;
            height: 16px;
            accent-color: var(--primary);
            cursor: pointer;
        }

        .member-phone {
            color: var(--text-muted);
            font-size: 13px;
        }

        .item-actions {
            display: flex;
            gap: 6px;
        }

        .btn-mini-edit {
            background: #eff6ff;
            color: #2563eb;
            border: 1px solid #bfdbfe;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
        }

        .btn-mini-delete {
            background: #fef2f2;
            color: #ef4444;
            border: 1px solid #fecaca;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
        }

        .form-select, .form-textarea {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            font-size: 14px;
            outline: none;
            background: #ffffff;
        }

        .form-textarea {
            resize: vertical;
            min-height: 80px;
        }

        .btn-submit-main {
            flex: 2;
            background: #2563eb;
            color: #ffffff;
            border: none;
            padding: 12px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 0;
        }

        .btn-submit-main:hover {
            background: #1d4ed8;
        }

        .btn-cancel-main {
            flex: 1;
            background: #f1f5f9;
            color: #475569;
            border: 1px solid #cbd5e1;
            padding: 12px;
            border-radius: 10px;
            font-size: 15px;
            font-weight: 600;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            transition: background 0.2s;
        }

        .btn-cancel-main:hover {
            background: #e2e8f0;
            color: #1e293b;
        }

        /* Modal styling */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.4);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            backdrop-filter: blur(4px);
        }

        .modal-overlay.active {
            display: flex;
        }

        .modal-card {
            background: #ffffff;
            border-radius: 16px;
            width: 90%;
            max-width: 440px;
            padding: 20px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .modal-header h3 {
            font-size: 18px;
            font-weight: 700;
        }

        .modal-close {
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
            color: var(--text-muted);
        }

        .modal-body label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 4px;
            color: var(--text-muted);
        }

        .modal-body input {
            width: 100%;
            padding: 10px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin-bottom: 12px;
        }

        .modal-footer {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 10px;
        }

        .summary-card {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 14px;
            font-family: monospace;
            white-space: pre-wrap;
            font-size: 13px;
            max-height: 250px;
            overflow-y: auto;
        }

        .toast-msg {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1e293b;
            color: #ffffff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            display: none;
            z-index: 1001;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }
    </style>
</head>
<body>

<div class="main-wrapper">
    <!-- Header -->
    <div class="app-header">
        <h1>Add Tasks</h1>
        <div style="display:flex; gap:8px;">
            <a href="dashboard.php" class="report-badge-btn" style="text-decoration:none; background:#eff6ff; color:#2563eb; border-color:#bfdbfe;">📊 Dashboard</a>
            <button class="report-badge-btn" onclick="openReportModal()">📋 10:30 Reports</button>
        </div>
    </div>

    <!-- Section 1: Assign Members -->
    <div class="section-box">
        <div class="section-header">
            <span class="section-title">Assign Members</span>
            <button class="btn-action-outline" onclick="openMemberModal()">[ + Add New Member ]</button>
        </div>
        <input type="text" id="searchMembersInput" class="search-input" placeholder="Search members..." oninput="filterMembers()">
        <div class="item-list-box" id="membersList">
            <!-- Dynamically populated -->
        </div>
    </div>

    <!-- Section 2: Assigned Tasks Presets -->
    <div class="section-box">
        <div class="section-header">
            <span class="section-title">Assigned Tasks</span>
            <button class="btn-action-outline" onclick="openPresetModal()">[ + Add Custom Task ]</button>
        </div>
        <div class="item-list-box" id="presetsList">
            <!-- Dynamically populated -->
        </div>
    </div>

    <!-- Section 3: WhatsApp Group (Optional) -->
    <div class="section-box">
        <div class="section-header">
            <span class="section-title">WhatsApp Group (Optional)</span>
        </div>
        <select id="whatsappGroupSelect" class="form-select">
            <option value="No Group / Private Only">No Group / Private Only</option>
        </select>
    </div>

    <!-- Section 4: Task / Notes -->
    <div class="section-box">
        <div class="section-header">
            <span class="section-title">Task / Notes</span>
        </div>
        <textarea id="taskNotesTextarea" class="form-textarea" placeholder="What should they do?"></textarea>
    </div>

    <!-- Action Buttons (Submit & Cancel) -->
    <div style="display: flex; gap: 12px; margin-top: 16px;">
        <button class="btn-submit-main" style="flex: 2; margin-top: 0;" onclick="allotTasksSubmit()">Allot Tasks & Schedule</button>
        <a href="dashboard.php" style="flex: 1; text-align: center; text-decoration: none; background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; padding: 12px; border-radius: 10px; font-size: 15px; font-weight: 600; display: inline-block; transition: background 0.2s;">Cancel</a>
    </div>

    <!-- Active Tasks Table / Tracker -->
    <div style="margin-top: 30px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
        <div class="section-header">
            <span class="section-title">Today's Task Status</span>
            <button class="btn-action-outline" onclick="loadTodayAllotments()">Refresh</button>
        </div>
        <div id="todayTasksList" style="max-height: 200px; overflow-y: auto;">
            <!-- Dynamically loaded -->
        </div>
    </div>
</div>

<!-- Modal 1: Add/Edit Member -->
<div class="modal-overlay" id="memberModal">
    <div class="modal-card">
        <div class="modal-header">
            <h3 id="memberModalTitle">Add New Member</h3>
            <button class="modal-close" onclick="closeModal('memberModal')">&times;</button>
        </div>
        <div class="modal-body">
            <input type="hidden" id="memberEditId">
            <label>Member Name</label>
            <input type="text" id="memberNameInput" placeholder="e.g. Akshay">
            <label>Phone Number</label>
            <input type="text" id="memberPhoneInput" placeholder="e.g. 9019713446">
        </div>
        <div class="modal-footer">
            <button class="btn-action-outline" onclick="closeModal('memberModal')">Cancel</button>
            <button class="btn-submit-main" style="width: auto; margin:0;" onclick="saveMember()">Save Member</button>
        </div>
    </div>
</div>

<!-- Modal 2: Add/Edit Custom Task Preset -->
<div class="modal-overlay" id="presetModal">
    <div class="modal-card">
        <div class="modal-header">
            <h3 id="presetModalTitle">Add Custom Task</h3>
            <button class="modal-close" onclick="closeModal('presetModal')">&times;</button>
        </div>
        <div class="modal-body">
            <input type="hidden" id="presetEditId">
            <label>Task Title</label>
            <input type="text" id="presetTitleInput" placeholder="e.g. Profit & Loss summary">
        </div>
        <div class="modal-footer">
            <button class="btn-action-outline" onclick="closeModal('presetModal')">Cancel</button>
            <button class="btn-submit-main" style="width: auto; margin:0;" onclick="savePreset()">Save Task</button>
        </div>
    </div>
</div>

<!-- Modal 3: 10:30 PM Summary Report -->
<div class="modal-overlay" id="reportModal">
    <div class="modal-card">
        <div class="modal-header">
            <h3>📊 10:30 PM Daily Summary Report</h3>
            <button class="modal-close" onclick="closeModal('reportModal')">&times;</button>
        </div>
        <div class="modal-body">
            <div class="summary-card" id="summaryReportContent">Loading report...</div>
        </div>
        <div class="modal-footer">
            <button class="btn-action-outline" onclick="copyReportText()">Copy Text</button>
            <button class="btn-submit-main" style="width: auto; margin:0;" onclick="closeModal('reportModal')">Close</button>
        </div>
    </div>
</div>

<div class="toast-msg" id="toastMsg">Action completed successfully</div>

<script>
    let globalMembers = [];
    let globalPresets = [];

    document.addEventListener('DOMContentLoaded', () => {
        loadMembers();
        loadPresets();
        loadGroups();
        loadTodayAllotments();
    });

    function showToast(msg) {
        const t = document.getElementById('toastMsg');
        t.innerText = msg;
        t.style.display = 'block';
        setTimeout(() => { t.style.display = 'none'; }, 3000);
    }

    function closeModal(id) {
        document.getElementById(id).classList.remove('active');
    }

    // --- MEMBERS MANAGEMENT ---
    function loadMembers() {
        fetch('api.php?action=get_members')
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    globalMembers = res.data;
                    renderMembers(globalMembers);
                }
            });
    }

    function renderMembers(list) {
        const container = document.getElementById('membersList');
        if (list.length === 0) {
            container.innerHTML = '<div style="padding: 10px; color: #94a3b8; text-align: center; font-size: 13px;">No members found.</div>';
            return;
        }
        container.innerHTML = list.map(m => `
            <div class="list-item">
                <label class="item-left">
                    <input type="checkbox" class="member-checkbox" value="${m.id}">
                    <span><strong>${escapeHtml(m.name)}</strong> <span class="member-phone">(${escapeHtml(m.phone)})</span></span>
                </label>
                <div class="item-actions">
                    <button class="btn-mini-edit" onclick="editMember(${m.id}, '${escapeHtml(m.name)}', '${escapeHtml(m.phone)}')">Edit</button>
                    <button class="btn-mini-delete" onclick="deleteMember(${m.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }

    function filterMembers() {
        const q = document.getElementById('searchMembersInput').value.toLowerCase();
        const filtered = globalMembers.filter(m => 
            m.name.toLowerCase().includes(q) || m.phone.includes(q)
        );
        renderMembers(filtered);
    }

    function openMemberModal() {
        document.getElementById('memberEditId').value = '';
        document.getElementById('memberNameInput').value = '';
        document.getElementById('memberPhoneInput').value = '';
        document.getElementById('memberModalTitle').innerText = 'Add New Member';
        document.getElementById('memberModal').classList.add('active');
    }

    function editMember(id, name, phone) {
        document.getElementById('memberEditId').value = id;
        document.getElementById('memberNameInput').value = name;
        document.getElementById('memberPhoneInput').value = phone;
        document.getElementById('memberModalTitle').innerText = 'Edit Member';
        document.getElementById('memberModal').classList.add('active');
    }

    function saveMember() {
        const id = document.getElementById('memberEditId').value;
        const name = document.getElementById('memberNameInput').value.trim();
        const phone = document.getElementById('memberPhoneInput').value.trim();

        if (!name || !phone) {
            alert('Please enter both name and phone number.');
            return;
        }

        const formData = new FormData();
        formData.append('action', id ? 'update_member' : 'add_member');
        if (id) formData.append('id', id);
        formData.append('name', name);
        formData.append('phone', phone);

        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    closeModal('memberModal');
                    loadMembers();
                    showToast(id ? 'Member updated' : 'Member added');
                } else {
                    alert(res.message || 'Error saving member');
                }
            });
    }

    function deleteMember(id) {
        if (!confirm('Are you sure you want to delete this member?')) return;
        const formData = new FormData();
        formData.append('action', 'delete_member');
        formData.append('id', id);
        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    loadMembers();
                    showToast('Member deleted');
                }
            });
    }

    // --- PRESETS MANAGEMENT ---
    function loadPresets() {
        fetch('api.php?action=get_presets')
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    globalPresets = res.data;
                    renderPresets(globalPresets);
                }
            });
    }

    function renderPresets(list) {
        const container = document.getElementById('presetsList');
        if (list.length === 0) {
            container.innerHTML = '<div style="padding: 10px; color: #94a3b8; text-align: center; font-size: 13px;">No tasks presets found.</div>';
            return;
        }
        container.innerHTML = list.map(p => `
            <div class="list-item">
                <label class="item-left">
                    <input type="checkbox" class="preset-checkbox" value="${escapeHtml(p.title)}">
                    <span>${escapeHtml(p.title)}</span>
                </label>
                <div class="item-actions">
                    <button class="btn-mini-edit" onclick="editPreset(${p.id}, '${escapeHtml(p.title)}')">Edit</button>
                    <button class="btn-mini-delete" onclick="deletePreset(${p.id})">Delete</button>
                </div>
            </div>
        `).join('');
    }

    function openPresetModal() {
        document.getElementById('presetEditId').value = '';
        document.getElementById('presetTitleInput').value = '';
        document.getElementById('presetModalTitle').innerText = 'Add Custom Task';
        document.getElementById('presetModal').classList.add('active');
    }

    function editPreset(id, title) {
        document.getElementById('presetEditId').value = id;
        document.getElementById('presetTitleInput').value = title;
        document.getElementById('presetModalTitle').innerText = 'Edit Task';
        document.getElementById('presetModal').classList.add('active');
    }

    function savePreset() {
        const id = document.getElementById('presetEditId').value;
        const title = document.getElementById('presetTitleInput').value.trim();

        if (!title) {
            alert('Please enter task title.');
            return;
        }

        const formData = new FormData();
        formData.append('action', id ? 'update_preset' : 'add_preset');
        if (id) formData.append('id', id);
        formData.append('title', title);

        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    closeModal('presetModal');
                    loadPresets();
                    showToast(id ? 'Task updated' : 'Task added');
                } else {
                    alert(res.message || 'Error saving task');
                }
            });
    }

    function deletePreset(id) {
        if (!confirm('Are you sure you want to delete this task preset?')) return;
        const formData = new FormData();
        formData.append('action', 'delete_preset');
        formData.append('id', id);
        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    loadPresets();
                    showToast('Task preset deleted');
                }
            });
    }

    // --- GROUPS ---
    function loadGroups() {
        fetch('api.php?action=get_groups')
            .then(r => r.json())
            .then(res => {
                if (res.success && res.data) {
                    const sel = document.getElementById('whatsappGroupSelect');
                    sel.innerHTML = '<option value="No Group / Private Only">No Group / Private Only</option>' +
                        res.data.map(g => `<option value="${escapeHtml(g)}">${escapeHtml(g)}</option>`).join('');
                }
            });
    }

    // --- ALLOT TASKS ---
    function allotTasksSubmit() {
        const selectedMemberIds = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(c => c.value);
        const selectedTasks = Array.from(document.querySelectorAll('.preset-checkbox:checked')).map(c => c.value);
        const group = document.getElementById('whatsappGroupSelect').value;
        const notes = document.getElementById('taskNotesTextarea').value.trim();

        if (selectedMemberIds.length === 0) {
            alert('Please select at least one member.');
            return;
        }
        if (selectedTasks.length === 0) {
            alert('Please select at least one task preset.');
            return;
        }

        fetch('api.php?action=allot_tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                member_ids: selectedMemberIds,
                tasks: selectedTasks,
                whatsapp_group: group,
                notes: notes
            })
        })
        .then(r => r.json())
        .then(res => {
            if (res.success) {
                showToast(res.message);
                loadTodayAllotments();
                // Clear checkboxes & notes
                document.querySelectorAll('.member-checkbox, .preset-checkbox').forEach(c => c.checked = false);
                document.getElementById('taskNotesTextarea').value = '';
            } else {
                alert(res.message || 'Error allotting tasks');
            }
        });
    }

    // --- TODAY ALLOTMENTS LIST & STATUS ---
    function loadTodayAllotments() {
        fetch('api.php?action=get_allotments')
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    renderTodayAllotments(res.data);
                }
            });
    }

    function renderTodayAllotments(list) {
        const container = document.getElementById('todayTasksList');
        if (list.length === 0) {
            container.innerHTML = '<div style="padding: 10px; color: #94a3b8; font-size: 13px; text-align: center;">No tasks allotted for today yet.</div>';
            return;
        }
        container.innerHTML = list.map(item => `
            <div class="list-item" style="font-size: 13px;">
                <div>
                    <strong>${escapeHtml(item.member_name)}</strong> &bull; ${escapeHtml(item.task_title)}
                    <div style="font-size: 11px; color: #64748b;">Group: ${escapeHtml(item.whatsapp_group)}</div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="padding: 3px 8px; border-radius: 12px; font-weight: 600; font-size: 11px; ${item.status === 'completed' ? 'background:#dcfce7; color:#166534;' : 'background:#fef3c7; color:#92400e;'}">
                        ${item.status === 'completed' ? '✔️ Completed' : '⏳ Pending'}
                    </span>
                    <button class="btn-mini-edit" onclick="toggleTaskStatus(${item.id}, '${item.status === 'completed' ? 'pending' : 'completed'}')">
                        ${item.status === 'completed' ? 'Mark Pending' : 'Mark Done'}
                    </button>
                </div>
            </div>
        `).join('');
    }

    function toggleTaskStatus(id, newStatus) {
        const formData = new FormData();
        formData.append('action', 'toggle_status');
        formData.append('id', id);
        formData.append('status', newStatus);

        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    loadTodayAllotments();
                    showToast('Status updated');
                }
            });
    }

    // --- 10:30 REPORT MODAL ---
    function openReportModal() {
        document.getElementById('reportModal').classList.add('active');
        fetch('api.php?action=get_summary_report')
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    document.getElementById('summaryReportContent').innerText = res.report_text;
                }
            });
    }

    function copyReportText() {
        const txt = document.getElementById('summaryReportContent').innerText;
        navigator.clipboard.writeText(txt);
        showToast('Report copied to clipboard!');
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }
</script>

</body>
</html>
