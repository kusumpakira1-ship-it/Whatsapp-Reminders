<?php
// ─── Timezone: Asia/Kolkata ───────────────────────────────────────────────
date_default_timezone_set('Asia/Kolkata');
?>
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MAC Device Manager – sunfragroup.com</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  :root {
    --bg:#f0f4ff; --card:#ffffff; --border:#dde3f0;
    --accent:#4f8ef7; --accent2:#7c3aed;
    --green:#16a34a; --yellow:#d97706; --red:#dc2626;
    --text:#1e293b; --muted:#64748b;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;padding:30px 20px;}

  /* Header */
  .header{text-align:center;margin-bottom:32px;}
  .header h1{font-size:2rem;font-weight:700;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
  .header p{font-size:.8rem;color:var(--muted);margin-top:6px;}
  .header p span{color:var(--accent);font-weight:600;}

  /* Stats */
  .stats{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:28px;}
  .stat-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px 28px;text-align:center;min-width:120px;transition:transform .2s;}
  .stat-card:hover{transform:translateY(-3px);}
  .stat-card .num{font-size:1.9rem;font-weight:700;}
  .stat-card .lbl{font-size:.7rem;color:var(--muted);margin-top:3px;text-transform:uppercase;letter-spacing:1px;}
  .num-total{color:var(--accent)}.num-active{color:var(--green)}.num-in{color:var(--red)}.num-pend{color:var(--yellow)}

  /* Tabs */
  .tabs{display:flex;gap:10px;justify-content:center;margin-bottom:24px;flex-wrap:wrap;}
  .tab{padding:10px 24px;border-radius:10px;border:1px solid var(--border);background:var(--card);color:var(--muted);font-size:.875rem;font-weight:600;cursor:pointer;transition:all .2s;font-family:'Inter',sans-serif;}
  .tab.active,.tab:hover{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-color:transparent;}

  /* Add Device Button */
  .btn-add-device{display:inline-flex;align-items:center;gap:8px;padding:11px 22px;border-radius:10px;border:none;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-size:.875rem;font-weight:700;font-family:'Inter',sans-serif;cursor:pointer;transition:filter .2s,transform .15s,box-shadow .2s;box-shadow:0 4px 14px rgba(79,142,247,.35);}
  .btn-add-device:hover{filter:brightness(1.1);transform:translateY(-2px);box-shadow:0 6px 20px rgba(79,142,247,.45);}

  /* Form Modal */
  .form-overlay{display:none;position:fixed;inset:0;background:rgba(15,17,35,.5);backdrop-filter:blur(6px);z-index:900;align-items:center;justify-content:center;padding:20px;}
  .form-overlay.show{display:flex;animation:fadeIn .22s ease;}
  .form-modal{background:#fff;border-radius:22px;padding:36px 38px;max-width:540px;width:100%;box-shadow:0 24px 80px rgba(0,0,0,.18);position:relative;}
  .form-modal-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px;}
  .form-modal-header h2{font-size:1.2rem;font-weight:700;color:#1e293b;display:flex;align-items:center;gap:10px;}
  .form-modal-header h2 span{font-size:1.4rem;}
  .close-btn{background:none;border:none;cursor:pointer;font-size:1.3rem;color:var(--muted);padding:4px;border-radius:6px;transition:background .2s,color .2s;line-height:1;}
  .close-btn:hover{background:#f1f5f9;color:#1e293b;}
  .form-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
  @media(max-width:500px){.form-grid{grid-template-columns:1fr;}}
  .form-group{display:flex;flex-direction:column;gap:6px;}
  label{font-size:.72rem;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;}
  input,select{background:#f8faff;border:1px solid var(--border);color:var(--text);border-radius:9px;padding:11px 14px;font-size:.875rem;font-family:'Inter',sans-serif;outline:none;transition:border-color .2s;}
  input:focus,select:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(79,142,247,.12);}
  input::placeholder{color:var(--muted);}
  select option{background:#ffffff;color:#1e293b;}
  .hint{font-size:.7rem;color:var(--muted);}
  .err-text{font-size:.72rem;color:var(--red);display:none;}
  .form-footer{margin-top:24px;display:flex;gap:12px;}
  .btn-submit{flex:1;padding:13px;border-radius:10px;border:none;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-size:.95rem;font-weight:700;font-family:'Inter',sans-serif;cursor:pointer;transition:filter .2s,transform .15s;}
  .btn-submit:hover{filter:brightness(1.1);transform:translateY(-1px);}
  .btn-submit:disabled{filter:grayscale(1);cursor:not-allowed;transform:none;}
  .btn-cancel-form{padding:13px 20px;border-radius:10px;border:1px solid var(--border);background:#f8faff;color:var(--muted);font-size:.875rem;font-weight:600;font-family:'Inter',sans-serif;cursor:pointer;transition:background .2s;}
  .btn-cancel-form:hover{background:#eef2ff;color:#1e293b;}

  /* Action Buttons */
  .actions{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;margin-bottom:28px;}
  .btn{display:inline-flex;align-items:center;gap:8px;padding:11px 24px;border-radius:10px;border:none;font-family:'Inter',sans-serif;font-size:.875rem;font-weight:600;cursor:pointer;transition:filter .2s,transform .15s;text-decoration:none;}
  .btn:hover{filter:brightness(1.15);transform:translateY(-2px);}
  .btn-rand{background:linear-gradient(135deg,#4f8ef7,#7c3aed);color:#fff;}
  .btn-green{background:linear-gradient(135deg,#22c55e,#16a34a);color:#fff;}

  /* Flash */
  .flash{max-width:820px;margin:0 auto 20px;padding:13px 18px;border-radius:10px;font-size:.875rem;font-weight:500;display:none;}
  .flash.show{display:block;}
  .flash.ok{background:#14532d33;border:1px solid var(--green);color:var(--green);}
  .flash.err{background:#7f1d1d33;border:1px solid var(--red);color:var(--red);}

  /* Table */
  .table-wrap{max-width:1100px;margin:0 auto;overflow-x:auto;border-radius:16px;border:1px solid var(--border);}
  table{width:100%;border-collapse:collapse;font-size:.875rem;background:#fff;}
  thead th{background:#eef2ff;color:var(--muted);text-transform:uppercase;letter-spacing:1px;font-size:.68rem;padding:13px 16px;text-align:left;white-space:nowrap;}
  tbody tr{border-top:1px solid var(--border);transition:background .15s;}
  tbody tr:hover{background:#f5f8ff;}
  tbody td{padding:12px 16px;}
  .mac{font-family:monospace;letter-spacing:1px;color:var(--accent);font-size:.85rem;}
  .badge{display:inline-block;padding:3px 12px;border-radius:99px;font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;}
  .badge-on{background:#14532d55;color:var(--green);border:1px solid #22c55e55;}
  .badge-off{background:#7f1d1d44;color:var(--red);border:1px solid #ef444455;}
  .del-btn{background:none;border:1px solid #ef444466;color:var(--red);border-radius:6px;padding:4px 12px;cursor:pointer;font-size:.72rem;font-family:'Inter',sans-serif;transition:background .2s;}
  .del-btn:hover{background:#ef444422;}
  .edit-btn{background:none;border:1px solid #4f8ef766;color:var(--accent);border-radius:6px;padding:4px 12px;cursor:pointer;font-size:.72rem;font-family:'Inter',sans-serif;transition:background .2s;margin-right:6px;}
  .edit-btn:hover{background:#4f8ef722;}
  .empty{text-align:center;padding:60px 20px;color:var(--muted);font-size:.9rem;}
  .empty span{font-size:2.5rem;display:block;margin-bottom:10px;}
  #loader{display:none;text-align:center;padding:10px;color:var(--muted);font-size:.85rem;}

  /* Custom Confirm Modal */
  .modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.35);backdrop-filter:blur(3px);z-index:999;align-items:center;justify-content:center;}
  .modal-overlay.show{display:flex;animation:fadeIn .2s ease;}
  .modal-box{background:#fff;border-radius:18px;padding:32px 36px;max-width:360px;width:90%;text-align:center;box-shadow:0 20px 60px rgba(0,0,0,.15);}
  .modal-box .modal-icon{font-size:2.5rem;margin-bottom:12px;}
  .modal-box h3{font-size:1.1rem;font-weight:700;color:#1e293b;margin-bottom:8px;}
  .modal-box p{font-size:.875rem;color:#64748b;margin-bottom:24px;}
  .modal-btns{display:flex;gap:12px;justify-content:center;}
  .modal-btn{padding:10px 28px;border-radius:10px;border:none;font-family:'Inter',sans-serif;font-size:.875rem;font-weight:600;cursor:pointer;transition:filter .2s;}
  .modal-btn-cancel{background:#f1f5f9;color:#64748b;}
  .modal-btn-cancel:hover{filter:brightness(.95);}
  .modal-btn-del{background:linear-gradient(135deg,#ef4444,#b91c1c);color:#fff;}
  .modal-btn-del:hover{filter:brightness(1.1);}
</style>
</head>
<body>

<div class="header">
  <h1>📡 MAC Device Manager</h1>
  <p>Timezone: <span>Asia/Kolkata (IST)</span> &nbsp;|&nbsp; sunfragroup.com &nbsp;|&nbsp; Auto-refresh 30s</p>
</div>

<!-- Custom Alerts/Reminders -->
<div id="alert-banner" style="display:none; background:#fee2e2; border:1px solid #ef4444; color:#b91c1c; padding:12px; border-radius:8px; margin:0 auto 20px; max-width:1100px; text-align:center; font-weight:600;">
  ⚠️ REMINDER: One or more devices are OFF or have low water level (25%)!
</div>

<!-- Custom Top Bar -->
<div class="tabs" style="justify-content:space-between; max-width:1100px; margin:0 auto 24px; align-items:center;">
  <div style="font-size:1.1rem; font-weight:700; color:var(--accent);">🕒 <span id="live-clock">--:--:--</span></div>
  <div style="display:flex; gap:10px;">
    <input type="text" id="search-mac" placeholder="Search MAC Address..." onkeyup="filterTable()" style="padding:8px 12px; width:220px;" />
    <button class="tab" onclick="document.getElementById('search-mac').value=''; filterTable();">View All</button>
  </div>
</div>

<!-- Toolbar: Add Device + Refresh -->
<div class="tabs" style="justify-content:space-between;max-width:1100px;margin:0 auto 24px;">
  <button class="btn-add-device" onclick="openFormModal()">➕ &nbsp;Add Device</button>
  <button class="tab" onclick="loadData()">🔄 Refresh</button>
</div>


<!-- Flash message -->
<div class="flash" id="flash"></div>
<div id="loader">⏳ Loading…</div>

<!-- Data Table -->
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Name</th>
        <th>MAC Address</th>
        <th>Location</th>
        <th>Water Level</th>
        <th>Device State</th>
        <th>Created At (IST)</th>
        <th>Action</th>
      </tr>
    </thead>
    <tbody id="tbody">
      <tr><td colspan="8"><div class="empty"><span>⏳</span>Loading…</div></td></tr>
    </tbody>
  </table>
</div>

<script>
// ── API endpoint (same folder as this file) ────────────────────────────────
const API = 'api.php';

// ── Form Modal open/close ──────────────────────────────────────────────────
function openFormModal() {
  document.getElementById('formModal').classList.add('show');
  document.getElementById('f-name').focus();
}
function closeFormModal() {
  document.getElementById('formModal').classList.remove('show');
  // Reset form
  document.getElementById('f-name').value   = '';
  document.getElementById('f-location').value = '';
  document.getElementById('f-mac').value    = '';
  document.getElementById('f-status').value = 'on';
  document.getElementById('f-water').value  = '100%';
  ['name','mac'].forEach(f => {
    const el = document.getElementById('e-'+f);
    if(el){ el.style.display='none'; el.textContent=''; }
  });
}

// ── Flash ──────────────────────────────────────────────────────────────────
function flash(msg, type='ok') {
  const f = document.getElementById('flash');
  f.textContent = msg;
  f.className   = 'flash show ' + type;
  setTimeout(() => f.className = 'flash', 4500);
}

function loader(show) {
  document.getElementById('loader').style.display = show ? 'block' : 'none';
}

// ── Live Clock & Search ────────────────────────────────────────────────────
setInterval(() => {
  const now = new Date();
  document.getElementById('live-clock').textContent = now.toLocaleString('en-IN', { timeZone: 'Asia/Kolkata', dateStyle: 'medium', timeStyle: 'medium' });
}, 1000);

function filterTable() {
  const search = document.getElementById('search-mac').value.toLowerCase();
  const rows = document.querySelectorAll('.data-row');
  rows.forEach(row => {
    const mac = row.getAttribute('data-mac').toLowerCase();
    row.style.display = mac.includes(search) ? '' : 'none';
  });
}

// ── Render table ───────────────────────────────────────────────────────────
function renderTable(data) {
  const t = document.getElementById('tbody');
  if (!data.length) {
    t.innerHTML = '<tr><td colspan="8"><div class="empty"><span>📭</span>No records yet. Add one above!</div></td></tr>';
    document.getElementById('alert-banner').style.display = 'none';
    return;
  }
  
  // Alert logic
  const needsAlert = data.some(r => r.status === 'off' || r.water_level === '25%');
  document.getElementById('alert-banner').style.display = needsAlert ? 'block' : 'none';

  t.innerHTML = data.map(r => `
    <tr class="data-row" id="row-${r.id}" data-mac="${r.mac_address}">
      <td>${r.id}</td>
      <td><b>${r.name}</b></td>
      <td class="mac">${r.mac_address}</td>
      <td>${r.location || '-'}</td>
      <td>${r.water_level || '-'}</td>
      <td><span class="badge badge-${r.status}">${r.status==='on'?'ON':'OFF'}</span></td>
      <td>${r.created_at}</td>
      <td>
        <button class="edit-btn" onclick="openEditModal(${r.id},'${(r.name||'').replace(/'/g,"\\'")}','${(r.location||'').replace(/'/g,"\\'")}','${r.mac_address}','${r.status}','${r.water_level||'100%'}')">✏️ Edit</button>
        <button class="del-btn"  onclick="deleteRecord(${r.id})">🗑 Delete</button>
      </td>
    </tr>`).join('');
  filterTable();
}

// ── Load all data ──────────────────────────────────────────────────────────
async function loadData() {
  loader(true);
  try {
    const res  = await fetch(`${API}?action=view`);
    const json = await res.json();
    if (json.success) { renderTable(json.data); }
    else flash('❌ ' + json.error, 'err');
  } catch(e) { flash('❌ Network error: ' + e.message, 'err'); }
  loader(false);
}

// ── Add Random ─────────────────────────────────────────────────────────────
async function addRandom() {
  loader(true);
  try {
    const res  = await fetch(`${API}?action=add`);
    const json = await res.json();
    if (json.success) {
      flash(`✅ Added → ${json.data.name} | ${json.data.mac_address} | ${json.data.status}`);
      loadData();
    } else flash('❌ ' + json.error, 'err');
  } catch(e) { flash('❌ ' + e.message, 'err'); }
  loader(false);
}

// ── Add Manually ───────────────────────────────────────────────────────────
async function addManual() {
  // Clear errors
  ['name','mac'].forEach(f => {
    const el = document.getElementById('e-'+f);
    el.style.display = 'none';
    el.textContent   = '';
  });

  const name     = document.getElementById('f-name').value.trim();
  const location = document.getElementById('f-location').value.trim();
  const mac      = document.getElementById('f-mac').value.trim().toUpperCase();
  const status   = document.getElementById('f-status').value;
  const water    = document.getElementById('f-water').value;

  // Validate
  let err = false;
  if (!name) {
    document.getElementById('e-name').textContent = '⚠ Device name is required.';
    document.getElementById('e-name').style.display = 'block';
    err = true;
  }
  if (!mac || !/^([0-9A-F]{2}-){5}[0-9A-F]{2}$/.test(mac)) {
    document.getElementById('e-mac').textContent = '⚠ Use format AA-BB-CC-DD-EE-FF';
    document.getElementById('e-mac').style.display = 'block';
    err = true;
  }
  if (err) return;

  const btn = document.getElementById('submitBtn');
  btn.disabled    = true;
  btn.textContent = '⏳ Saving…';

  try {
    const url  = `${API}?action=manual_add&name=${encodeURIComponent(name)}&location=${encodeURIComponent(location)}&mac_address=${encodeURIComponent(mac)}&status=${status}&water_level=${encodeURIComponent(water)}`;
    const res  = await fetch(url);
    const json = await res.json();

    if (json.success) {
      flash(`✅ Saved! → ${json.data.name} | ${json.data.mac_address} | ${json.data.status} | ${json.data.created_at} IST`);
      closeFormModal();
      loadData();
    } else {
      const msg = json.errors ? json.errors.join(' | ') : json.error;
      flash('❌ ' + msg, 'err');
    }
  } catch(e) { flash('❌ ' + e.message, 'err'); }

  btn.disabled    = false;
  btn.textContent = '💾 Save to Database';
}

// ── Edit Modal ─────────────────────────────────────────────────────────────
let editingId = null;

function openEditModal(id, name, location, mac, status, water) {
  editingId = id;
  // Clear edit modal error fields
  ['ee-name','ee-mac'].forEach(f => {
    const el = document.getElementById(f);
    if(el){ el.style.display='none'; el.textContent=''; }
  });
  document.getElementById('edit-id-label').textContent = `Editing Record #${id}`;
  document.getElementById('ef-name').value   = name;
  document.getElementById('ef-location').value = location;
  document.getElementById('ef-mac').value    = mac;
  document.getElementById('ef-status').value = status;
  document.getElementById('ef-water').value  = water;
  document.getElementById('editModal').classList.add('show');
  document.getElementById('ef-name').focus();
}

function closeEditModal() {
  document.getElementById('editModal').classList.remove('show');
  editingId = null;
}

async function saveEdit() {
  const name     = document.getElementById('ef-name').value.trim();
  const location = document.getElementById('ef-location').value.trim();
  const mac      = document.getElementById('ef-mac').value.trim().toUpperCase();
  const status   = document.getElementById('ef-status').value;
  const water    = document.getElementById('ef-water').value;

  // Validate
  let err = false;
  const eName = document.getElementById('ee-name');
  const eMac  = document.getElementById('ee-mac');
  eName.style.display = 'none'; eMac.style.display = 'none';

  if (!name) { eName.textContent='⚠ Name required.'; eName.style.display='block'; err=true; }
  if (!mac || !/^([0-9A-F]{2}-){5}[0-9A-F]{2}$/.test(mac)) {
    eMac.textContent='⚠ Use format AA-BB-CC-DD-EE-FF'; eMac.style.display='block'; err=true;
  }
  if (err) return;

  const btn = document.getElementById('editSaveBtn');
  btn.disabled = true; btn.textContent = '⏳ Updating…';

  try {
    const url  = `${API}?action=update&id=${editingId}&name=${encodeURIComponent(name)}&location=${encodeURIComponent(location)}&mac_address=${encodeURIComponent(mac)}&status=${status}&water_level=${encodeURIComponent(water)}`;
    const res  = await fetch(url);
    const json = await res.json();
    if (json.success) {
      flash(`✅ Updated! → ${json.data.name} | ${json.data.mac_address} | ${json.data.status}`);
      closeEditModal();
      loadData();
    } else {
      const msg = json.errors ? json.errors.join(' | ') : json.error;
      flash('❌ ' + msg, 'err');
    }
  } catch(e) { flash('❌ ' + e.message, 'err'); }

  btn.disabled = false; btn.textContent = '💾 Update Record';
}
let pendingDeleteId = null;

function deleteRecord(id) {
  pendingDeleteId = id;
  document.getElementById('modal-msg').textContent = `Record #${id} will be permanently removed.`;
  document.getElementById('confirmModal').classList.add('show');
  document.getElementById('modal-confirm-btn').onclick = confirmDelete;
}

function closeModal() {
  document.getElementById('confirmModal').classList.remove('show');
  pendingDeleteId = null;
}

async function confirmDelete() {
  const id = pendingDeleteId;
  closeModal();
  try {
    const res  = await fetch(`${API}?action=delete&id=${id}`);
    const json = await res.json();
    if (json.success && json.affected_rows > 0) {
      flash(`🗑 Record #${id} deleted successfully.`);
      loadData();
    } else flash('❌ Record not found.', 'err');
  } catch(e) { flash('❌ ' + e.message, 'err'); }
}

// ── Auto-format MAC as you type (works in both Add & Edit modals) ──────────
document.addEventListener('input', function(e) {
  if (e.target && (e.target.id === 'f-mac' || e.target.id === 'ef-mac')) {
    let v = e.target.value.replace(/[^0-9A-Fa-f]/g, '').toUpperCase();
    v = v.match(/.{1,2}/g)?.join('-') || v;
    e.target.value = v.substring(0, 17);
  }
});

// Init
loadData();
setInterval(loadData, 120000);
</script>
<!-- Add Device Form Modal -->
<div class="form-overlay" id="formModal" onclick="if(event.target===this)closeFormModal()">
  <div class="form-modal">
    <div class="form-modal-header">
      <h2><span>📱</span> Add New Device</h2>
      <button class="close-btn" onclick="closeFormModal()" title="Close">&times;</button>
    </div>
    <div class="form-grid">
      <div class="form-group">
        <label for="f-name">Device Name</label>
        <input id="f-name" type="text" placeholder="e.g. Office-Router" maxlength="100">
        <span class="err-text" id="e-name"></span>
      </div>
      <div class="form-group">
        <label for="f-location">Location</label>
        <input id="f-location" type="text" placeholder="e.g. Tank A" maxlength="100">
      </div>
      <div class="form-group">
        <label for="f-mac">MAC Address</label>
        <input id="f-mac" type="text" placeholder="AA-BB-CC-DD-EE-FF" maxlength="17">
        <span class="hint">💡 Type hex digits — dashes auto-added</span>
        <span class="err-text" id="e-mac"></span>
      </div>
      <div class="form-group">
        <label for="f-water">Water Level</label>
        <select id="f-water">
          <option value="100%">100%</option>
          <option value="75%">75%</option>
          <option value="50%">50%</option>
          <option value="25%">25%</option>
        </select>
      </div>
      <div class="form-group" style="grid-column: 1 / -1;">
        <label for="f-status">Device State</label>
        <select id="f-status">
          <option value="on">✅ ON</option>
          <option value="off">🔴 OFF</option>
        </select>
      </div>
    </div>
    <div class="form-footer">
      <button class="btn-cancel-form" onclick="closeFormModal()">Cancel</button>
      <button class="btn-submit" id="submitBtn" onclick="addManual()">💾 Save to Database</button>
    </div>
  </div>
</div>

<!-- Edit Device Modal -->
<div class="form-overlay" id="editModal" onclick="if(event.target===this)closeEditModal()">
  <div class="form-modal">
    <div class="form-modal-header">
      <h2><span>✏️</span> Edit Device</h2>
      <button class="close-btn" onclick="closeEditModal()" title="Close">&times;</button>
    </div>
    <p id="edit-id-label" style="font-size:.78rem;color:var(--muted);margin-bottom:20px;font-weight:600;"></p>
    <div class="form-grid">
      <div class="form-group">
        <label for="ef-name">Device Name</label>
        <input id="ef-name" type="text" placeholder="e.g. Office-Router" maxlength="100">
        <span class="err-text" id="ee-name"></span>
      </div>
      <div class="form-group">
        <label for="ef-location">Location</label>
        <input id="ef-location" type="text" placeholder="e.g. Tank A" maxlength="100">
      </div>
      <div class="form-group">
        <label for="ef-mac">MAC Address</label>
        <input id="ef-mac" type="text" placeholder="AA-BB-CC-DD-EE-FF" maxlength="17">
        <span class="hint">💡 Type hex digits — dashes auto-added</span>
        <span class="err-text" id="ee-mac"></span>
      </div>
      <div class="form-group">
        <label for="ef-water">Water Level</label>
        <select id="ef-water">
          <option value="100%">100%</option>
          <option value="75%">75%</option>
          <option value="50%">50%</option>
          <option value="25%">25%</option>
        </select>
      </div>
      <div class="form-group" style="grid-column: 1 / -1;">
        <label for="ef-status">Device State</label>
        <select id="ef-status">
          <option value="on">✅ ON</option>
          <option value="off">🔴 OFF</option>
        </select>
      </div>
    </div>
    <div class="form-footer">
      <button class="btn-cancel-form" onclick="closeEditModal()">Cancel</button>
      <button class="btn-submit" id="editSaveBtn" onclick="saveEdit()">💾 Update Record</button>
    </div>
  </div>
</div>

<!-- Delete Confirm Modal -->
<div class="modal-overlay" id="confirmModal">
  <div class="modal-box">
    <div class="modal-icon">🗑️</div>
    <h3>Delete Record?</h3>
    <p id="modal-msg">This action cannot be undone.</p>
    <div class="modal-btns">
      <button class="modal-btn modal-btn-cancel" onclick="closeModal()">Cancel</button>
      <button class="modal-btn modal-btn-del"   id="modal-confirm-btn">Yes, Delete</button>
    </div>
  </div>
</div>

</body>
</html>
