<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Task Management Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-main: #f8fafc;
            --card-bg: #ffffff;
            --text-dark: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --success: #10b981;
            --success-bg: #dcfce7;
            --warning: #f59e0b;
            --warning-bg: #fef3c7;
            --danger: #ef4444;
            --danger-bg: #fef2f2;
            --border: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }

        body {
            background: var(--bg-main);
            color: var(--text-dark);
            min-height: 100vh;
            padding: 24px;
        }

        .dashboard-container {
            max-width: 1100px;
            margin: 0 auto;
        }

        /* Top Header Bar */
        .top-navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--card-bg);
            padding: 18px 24px;
            border-radius: 16px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            margin-bottom: 24px;
        }

        .brand-title {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-dark);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .nav-actions {
            display: flex;
            gap: 12px;
        }

        .btn-add-tasks {
            background: #2563eb;
            color: #ffffff;
            border: none;
            padding: 10px 18px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: background 0.2s;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
        }

        .btn-add-tasks:hover {
            background: #1d4ed8;
        }

        .btn-secondary {
            background: #f1f5f9;
            color: #334155;
            border: 1px solid var(--border);
            padding: 10px 16px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }

        .btn-secondary:hover {
            background: #e2e8f0;
        }

        /* Analytics Metric Cards Grid */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }

        .metric-card {
            background: var(--card-bg);
            border-radius: 14px;
            padding: 20px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
        }

        .metric-title {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--text-dark);
        }

        .metric-sub {
            font-size: 12px;
            margin-top: 4px;
            color: var(--text-muted);
        }

        /* Task Table Container */
        .table-card {
            background: var(--card-bg);
            border-radius: 16px;
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            padding: 20px;
        }

        .table-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            flex-wrap: wrap;
            gap: 12px;
        }

        .table-title {
            font-size: 18px;
            font-weight: 700;
        }

        .filter-group {
            display: flex;
            gap: 10px;
        }

        .form-control {
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 13px;
            outline: none;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }

        th {
            background: #f8fafc;
            color: var(--text-muted);
            text-align: left;
            padding: 12px 14px;
            font-weight: 600;
            border-bottom: 1px solid var(--border);
            font-size: 12px;
            text-transform: uppercase;
        }

        td {
            padding: 14px;
            border-bottom: 1px solid var(--border);
            color: var(--text-dark);
        }

        tr:hover {
            background: #f8fafc;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }

        .badge-success { background: #dcfce7; color: #166534; }
        .badge-pending { background: #fef3c7; color: #92400e; }
        .badge-danger { background: #fef2f2; color: #991b1b; }

        .btn-mini {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            border: 1px solid var(--border);
            background: #ffffff;
            transition: all 0.2s;
        }

        .btn-mini:hover { background: #f1f5f9; }

        /* Modal */
        .modal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0,0,0,0.4);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            backdrop-filter: blur(4px);
        }

        .modal-overlay.active { display: flex; }

        .modal-card {
            background: #ffffff;
            border-radius: 16px;
            width: 90%;
            max-width: 500px;
            padding: 24px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        }

        .summary-code-box {
            background: #0f172a;
            color: #38bdf8;
            padding: 16px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
    </style>
</head>
<body>

<div class="dashboard-container">
    <!-- Top Navbar -->
    <div class="top-navbar">
        <div class="brand-title">
            📋 Task Management Dashboard
        </div>
        <div class="nav-actions">
            <!-- Prominent [ + Add Tasks ] Button requested by user -->
            <a href="index.php" class="btn-add-tasks">
                <span>➕</span> Add Tasks
            </a>
            <button class="btn-secondary" onclick="openReportsModal()">📊 View 10:30 Reports</button>
        </div>
    </div>

    <!-- Analytics Cards -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-title">📋 Total Tasks Today</div>
            <div class="metric-value" id="cardTotalTasks">0</div>
            <div class="metric-sub">Assigned today</div>
        </div>

        <div class="metric-card">
            <div class="metric-title" style="color: #166534;">✔️ Completed Today</div>
            <div class="metric-value" style="color: #166534;" id="cardCompleted">0</div>
            <div class="metric-sub">Tasks finished</div>
        </div>

        <div class="metric-card">
            <div class="metric-title" style="color: #991b1b;">❌ Failed Today</div>
            <div class="metric-value" style="color: #991b1b;" id="cardFailedToday">0</div>
            <div class="metric-sub">Pending / Failed</div>
        </div>

        <div class="metric-card">
            <div class="metric-title" style="color: #d97706;">📉 Failed This Week</div>
            <div class="metric-value" style="color: #d97706;" id="cardFailedWeek">0</div>
            <div class="metric-sub" id="cardFailedMonth">Month: 0 failed</div>
        </div>
    </div>

    <!-- Task Allotments Live Table -->
    <div class="table-card">
        <div class="table-header">
            <div class="table-title">Live Task Allotments</div>
            <div class="filter-group">
                <input type="date" id="filterDate" class="form-control" onchange="loadDashboardData()">
                <input type="text" id="filterSearch" class="form-control" placeholder="Search member / task..." oninput="filterTable()">
            </div>
        </div>

        <div style="overflow-x: auto;">
            <table>
                <thead>
                    <tr>
                        <th>Member Name</th>
                        <th>Task Assigned</th>
                        <th>WhatsApp Group</th>
                        <th>Assigned Date</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody id="taskTableBody">
                    <tr>
                        <td colspan="6" style="text-align: center; color: #94a3b8; padding: 20px;">Loading task allotments...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>

<!-- Modal: View Member Summary Reports -->
<div class="modal-overlay" id="reportsModal">
    <div class="modal-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 style="font-weight: 700;">📊 Member Summary Reports</h3>
            <button onclick="closeModal()" style="background:none; border:none; font-size:20px; cursor:pointer;">&times;</button>
        </div>
        <div class="summary-code-box" id="reportsContent">Loading individual member reports...</div>
        <div style="display: flex; justify-content: flex-end; margin-top: 16px; gap: 10px;">
            <button class="btn-secondary" onclick="closeModal()">Close</button>
        </div>
    </div>
</div>

<script>
    let allTasks = [];

    document.addEventListener('DOMContentLoaded', () => {
        document.getElementById('filterDate').valueAsDate = new Date();
        loadDashboardData();
    });

    function loadDashboardData() {
        const selectedDate = document.getElementById('filterDate').value;
        
        // Fetch allotments
        fetch(`api.php?action=get_allotments&date=${selectedDate}`)
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    allTasks = res.data;
                    renderTable(allTasks);
                    updateMetrics(allTasks);
                }
            });

        // Fetch 10:30 summary metrics for week/month counters
        fetch(`api.php?action=get_summary_report&date=${selectedDate}`)
            .then(r => r.json())
            .then(res => {
                if (res.success && res.member_reports) {
                    let totalFailedW = 0;
                    let totalFailedM = 0;
                    let totalFailedT = 0;

                    // Compute overall metrics across member reports
                    res.member_reports.forEach(m => {
                        const txt = m.report_text;
                        const matchToday = txt.match(/Failed today:\s*(\d+)/);
                        const matchWeek = txt.match(/Failed this week:\s*(\d+)/);
                        const matchMonth = txt.match(/Failed this month:\s*(\d+)/);

                        if (matchToday) totalFailedT += parseInt(matchToday[1]);
                        if (matchWeek) totalFailedW += parseInt(matchWeek[1]);
                        if (matchMonth) totalFailedM += parseInt(matchMonth[1]);
                    });

                    document.getElementById('cardFailedToday').innerText = totalFailedT;
                    document.getElementById('cardFailedWeek').innerText = totalFailedW;
                    document.getElementById('cardFailedMonth').innerText = `Month: ${totalFailedM} failed`;
                }
            });
    }

    function updateMetrics(list) {
        const total = list.length;
        const completed = list.filter(t => t.status === 'completed').length;
        const pending = list.filter(t => t.status !== 'completed').length;

        document.getElementById('cardTotalTasks').innerText = total;
        document.getElementById('cardCompleted').innerText = completed;
    }

    function renderTable(list) {
        const tbody = document.getElementById('taskTableBody');
        if (list.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #94a3b8; padding: 20px;">No tasks allotted for this date. Click "+ Add Tasks" to assign tasks.</td></tr>';
            return;
        }

        tbody.innerHTML = list.map(item => `
            <tr>
                <td><strong>${escapeHtml(item.member_name)}</strong> <br><span style="font-size:12px; color:#64748b;">${escapeHtml(item.member_phone)}</span></td>
                <td><strong>${escapeHtml(item.task_title)}</strong>${item.notes ? '<br><span style="font-size:12px; color:#64748b;">' + escapeHtml(item.notes) + '</span>' : ''}</td>
                <td>${escapeHtml(item.whatsapp_group)}</td>
                <td>${escapeHtml(item.assigned_date)}</td>
                <td>
                    <span class="badge ${item.status === 'completed' ? 'badge-success' : 'badge-pending'}">
                        ${item.status === 'completed' ? '✔️ Completed' : '⏳ Pending'}
                    </span>
                </td>
                <td>
                    <button class="btn-mini" onclick="toggleStatus(${item.id}, '${item.status === 'completed' ? 'pending' : 'completed'}')">
                        ${item.status === 'completed' ? 'Mark Pending' : 'Mark Done'}
                    </button>
                    <button class="btn-mini" style="color:#ef4444; border-color:#fecaca;" onclick="deleteTask(${item.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    }

    function filterTable() {
        const q = document.getElementById('filterSearch').value.toLowerCase();
        const filtered = allTasks.filter(t => 
            t.member_name.toLowerCase().includes(q) || 
            t.task_title.toLowerCase().includes(q) ||
            t.whatsapp_group.toLowerCase().includes(q)
        );
        renderTable(filtered);
    }

    function toggleStatus(id, newStatus) {
        const formData = new FormData();
        formData.append('action', 'toggle_status');
        formData.append('id', id);
        formData.append('status', newStatus);

        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    loadDashboardData();
                }
            });
    }

    function deleteTask(id) {
        if (!confirm('Are you sure you want to delete this task assignment?')) return;
        const formData = new FormData();
        formData.append('action', 'delete_allotment');
        formData.append('id', id);

        fetch('api.php', { method: 'POST', body: formData })
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    loadDashboardData();
                }
            });
    }

    function openReportsModal() {
        const selectedDate = document.getElementById('filterDate').value;
        document.getElementById('reportsModal').classList.add('active');
        fetch(`api.php?action=get_summary_report&date=${selectedDate}`)
            .then(r => r.json())
            .then(res => {
                if (res.success) {
                    document.getElementById('reportsContent').innerText = res.report_text;
                }
            });
    }

    function closeModal() {
        document.getElementById('reportsModal').classList.remove('active');
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }
</script>

</body>
</html>
