// State
let groups = [];
let employees = [];

// Navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        
        // Update active nav
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
        e.target.classList.add('active');
        
        // Update active view
        const targetView = e.target.getAttribute('data-target');
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.getElementById(targetView).classList.add('active');
    });
});

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// API Calls
async function fetchGroups() {
    try {
        const res = await fetch('/api/groups');
        groups = await res.json();
        renderGroups();
        updateGroupSelect();
        updateDashboard();
    } catch (err) {
        console.error("Error fetching groups:", err);
    }
}

async function fetchEmployees() {
    try {
        const res = await fetch('/api/employees');
        employees = await res.json();
        renderEmployees();
        updateDashboard();
    } catch (err) {
        console.error("Error fetching employees:", err);
    }
}

async function fetchWahaGroups() {
    const select = document.getElementById('groupWhatsappId');
    try {
        const res = await fetch('/api/waha/groups');
        const data = await res.json();
        
        if (data.status === 'success' && data.groups.length > 0) {
            select.innerHTML = '<option value="">Select a WhatsApp Group...</option>';
            data.groups.forEach(g => {
                select.innerHTML += `<option value="${g.id}">${g.name}</option>`;
            });
        } else {
            select.innerHTML = '<option value="">Failed to load groups. Check WAHA connection.</option>';
        }
    } catch (err) {
        console.error("Error fetching WAHA groups:", err);
        select.innerHTML = '<option value="">Error fetching groups</option>';
    }
}

let alarms = [];

async function fetchAlarms() {
    try {
        const res = await fetch('/api/alarms');
        alarms = await res.json();
        renderAlarms();
    } catch (err) {
        console.error("Error fetching alarms:", err);
    }
}

// Render functions
function renderGroups() {
    const tbody = document.getElementById('groups-tbody');
    tbody.innerHTML = '';
    
    groups.forEach(group => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${group.id}</td>
            <td><strong>${group.name}</strong></td>
            <td>${group.whatsapp_group_id}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteGroup(${group.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderEmployees() {
    const tbody = document.getElementById('employees-tbody');
    tbody.innerHTML = '';
    
    employees.forEach(emp => {
        const groupName = groups.find(g => g.id === emp.group_id)?.name || 'Unknown';
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${emp.id}</td>
            <td><strong>${emp.name}</strong></td>
            <td>${emp.phone_number}</td>
            <td><span style="background: rgba(59, 130, 246, 0.2); color: #3b82f6; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem;">${groupName}</span></td>
            <td>${emp.report_responsibility}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteEmployee(${emp.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderAlarms() {
    const tbody = document.getElementById('alarms-tbody');
    tbody.innerHTML = '';
    
    alarms.forEach(alarm => {
        const tr = document.createElement('tr');
        const statusColor = alarm.status === 'sent' ? 'green' : (alarm.status === 'pending' ? 'orange' : 'gray');
        const statusBadge = `<span style="background: ${statusColor}; color: white; padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; text-transform: uppercase;">${alarm.status}</span>`;
        
        const triggerTime = new Date(alarm.trigger_time).toLocaleString();
        
        tr.innerHTML = `
            <td style="text-transform: capitalize;">${alarm.target_type}</td>
            <td><strong>${alarm.target_name}</strong></td>
            <td>${alarm.task_notes}</td>
            <td>${triggerTime}</td>
            <td>${statusBadge}</td>
            <td>
                ${alarm.status === 'pending' ? `<button class="btn btn-primary" onclick="triggerAlarm(${alarm.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Trigger Now</button>` : ''}
                <button class="btn btn-danger" onclick="deleteAlarm(${alarm.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem;">Delete</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function updateGroupSelect() {
    const select = document.getElementById('empGroup');
    select.innerHTML = '<option value="">Select Group...</option>';
    groups.forEach(g => {
        select.innerHTML += `<option value="${g.id}">${g.name}</option>`;
    });
}

function updateDashboard() {
    document.getElementById('stat-groups').innerText = groups.length;
    document.getElementById('stat-employees').innerText = employees.length;
}

// Form Handlers
async function handleGroupSubmit(e) {
    e.preventDefault();
    const select = document.getElementById('groupWhatsappId');
    const whatsappId = select.value;
    const name = select.options[select.selectedIndex].text;
    
    if (!whatsappId) {
        alert("Please select a group first.");
        return;
    }
    
    try {
        await fetch('/api/groups', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, whatsapp_group_id: whatsappId })
        });
        closeModal('groupModal');
        document.getElementById('groupForm').reset();
        fetchGroups();
    } catch (err) {
        console.error("Error creating group:", err);
        alert("Failed to create group");
    }
}

async function handleEmployeeSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('empName').value;
    const phone = document.getElementById('empPhone').value;
    const groupId = parseInt(document.getElementById('empGroup').value);
    const report = document.getElementById('empReport').value;
    
    try {
        await fetch('/api/employees', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                phone_number: phone,
                group_id: groupId,
                report_responsibility: report
            })
        });
        closeModal('employeeModal');
        document.getElementById('employeeForm').reset();
        fetchEmployees();
    } catch (err) {
        console.error("Error creating employee:", err);
        alert("Failed to create employee");
    }
}

async function handleAlarmSubmit(e) {
    e.preventDefault();
    const targetType = document.getElementById('alarmTargetType').value;
    const targetId = document.getElementById('alarmTargetSelect').value;
    const taskNotes = document.getElementById('alarmNotes').value;
    const mode = document.querySelector('input[name="alarmMode"]:checked').value;
    
    let triggerTime;
    if (mode === 'datetime') {
        const dtInput = document.getElementById('alarmDatetime').value;
        if (!dtInput) { alert("Please select a date and time"); return; }
        // Send exactly what the user typed (e.g. "2026-06-30T18:40") so the backend treats it as IST
        triggerTime = dtInput;
    } else {
        const days = parseInt(document.getElementById('alarmDays').value) || 0;
        const hours = parseInt(document.getElementById('alarmHours').value) || 0;
        const mins = parseInt(document.getElementById('alarmMins').value) || 0;
        const secs = parseInt(document.getElementById('alarmSecs').value) || 0;
        
        if (days === 0 && hours === 0 && mins === 0 && secs === 0) {
            alert("Please set a timer greater than 0");
            return;
        }
        const now = new Date();
        now.setDate(now.getDate() + days);
        now.setHours(now.getHours() + hours);
        now.setMinutes(now.getMinutes() + mins);
        now.setSeconds(now.getSeconds() + secs);
        
        // Format to YYYY-MM-DDTHH:mm:ss in local time (IST) to send to backend
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hr = String(now.getHours()).padStart(2, '0');
        const mn = String(now.getMinutes()).padStart(2, '0');
        const sc = String(now.getSeconds()).padStart(2, '0');
        triggerTime = `${year}-${month}-${day}T${hr}:${mn}:${sc}`;
    }

    try {
        await fetch('/api/alarms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_type: targetType,
                target_id: parseInt(targetId),
                task_notes: taskNotes,
                trigger_time: triggerTime
            })
        });
        closeModal('alarmModal');
        document.getElementById('alarmForm').reset();
        fetchAlarms();
    } catch (err) {
        console.error("Error creating alarm:", err);
        alert("Failed to create alarm.");
    }
}

function updateAlarmTargetSelect() {
    const type = document.getElementById('alarmTargetType').value;
    const select = document.getElementById('alarmTargetSelect');
    select.innerHTML = '';
    
    if (type === 'employee') {
        employees.forEach(e => select.innerHTML += `<option value="${e.id}">${e.name}</option>`);
    } else {
        groups.forEach(g => select.innerHTML += `<option value="${g.id}">${g.name}</option>`);
    }
}

function toggleAlarmMode() {
    const mode = document.querySelector('input[name="alarmMode"]:checked').value;
    if (mode === 'datetime') {
        document.getElementById('alarmDatetimeSection').style.display = 'block';
        document.getElementById('alarmTimerSection').style.display = 'none';
    } else {
        document.getElementById('alarmDatetimeSection').style.display = 'none';
        document.getElementById('alarmTimerSection').style.display = 'block';
    }
}

async function triggerAlarm(id) {
    if(confirm("Are you sure you want to trigger this alarm right now?")) {
        await fetch(`/api/alarms/${id}/trigger`, { method: 'POST' });
        fetchAlarms();
    }
}

async function deleteAlarm(id) {
    if(confirm("Are you sure you want to delete this alarm?")) {
        await fetch(`/api/alarms/${id}`, { method: 'DELETE' });
        fetchAlarms();
    }
}

async function deleteGroup(id) {
    if(confirm("Are you sure you want to delete this group? It will also delete all assigned employees.")) {
        await fetch(`/api/groups/${id}`, { method: 'DELETE' });
        fetchGroups();
        fetchEmployees();
    }
}

async function deleteEmployee(id) {
    if(confirm("Are you sure you want to delete this employee?")) {
        await fetch(`/api/employees/${id}`, { method: 'DELETE' });
        fetchEmployees();
    }
}

// Init
window.onload = () => {
    fetchGroups();
    fetchEmployees();
    fetchWahaGroups();
    fetchAlarms();
};
