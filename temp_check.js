
        const API_URL = '?api=';
        let waha_groups = [];
        let hidden_groups = [];
        let employees = [];
        let alarms = [];
        let report_types = [];
        let task_types = [];
        
        let all_contacts = [] || [];
        let manual_added_contacts = [];

        function escapeHtml(string) {
            return String(string).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
        }

        window.openModal = function(modalId) {
            const m = document.getElementById(modalId);
            if (m) {
                m.classList.add('active');
                m.style.setProperty('display', 'flex', 'important');
                m.style.setProperty('opacity', '1', 'important');
                m.style.setProperty('pointer-events', 'auto', 'important');
            } else {
                console.error("Modal not found:", modalId);
            }
        };

        window.closeModal = function(modalId) {
            const m = document.getElementById(modalId);
            if (m) {
                m.classList.remove('active');
                m.style.setProperty('display', 'none', 'important');
                m.style.setProperty('opacity', '0', 'important');
                m.style.setProperty('pointer-events', 'none', 'important');
            }
        };

        function renderMembersChecklist(selectedPhones = null, selectedTaskPhones = null) {
            const containerRem = document.getElementById('membersCheckboxContainer');
            const containerTask = document.getElementById('taskMembersCheckboxContainer');
            
            if (selectedPhones === null) {
                selectedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(cb => cb.value);
            }
            if (selectedTaskPhones === null) {
                selectedTaskPhones = Array.from(document.querySelectorAll('.task-member-checkbox:checked')).map(cb => cb.value);
            }
            
            // Combine database contacts with manually added ones
            const combined = [...all_contacts, ...manual_added_contacts];
            
            // De-duplicate by phone
            const uniqueContacts = [];
            const seen = new Set();
            combined.forEach(c => {
                if (!seen.has(c.phone)) {
                    seen.add(c.phone);
                    uniqueContacts.push(c);
                }
            });
            
            // Sort alphabetically by name
            uniqueContacts.sort((a, b) => a.name.localeCompare(b.name));
            
            if (containerRem) {
                containerRem.innerHTML = '';
                uniqueContacts.forEach(c => {
                    const checked = selectedPhones.includes(c.phone) ? 'checked' : '';
                    containerRem.innerHTML += `
                        <div class="member-checkbox-item" data-phone="${c.phone}" data-name="${c.name.toLowerCase()}" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.03);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="member-${c.phone}" value="${c.phone}" data-name="${c.name}" ${checked} class="member-checkbox" style="width:16px; height:16px; cursor:pointer;">
                                <label for="member-${c.phone}" style="cursor:pointer; font-size:0.95rem; color:var(--text-primary); font-weight:500;">
                                    ${c.name} <span style="font-weight:400; color:var(--text-secondary); font-size:0.85rem;">(${c.phone})</span>
                                </label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editMemberOption('${c.phone}', '${escapeHtml(c.name)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteMemberOption('${c.phone}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }

            if (containerTask) {
                containerTask.innerHTML = '';
                uniqueContacts.forEach(c => {
                    const checked = selectedTaskPhones.includes(c.phone) ? 'checked' : '';
                    containerTask.innerHTML += `
                        <div class="task-member-checkbox-item" data-phone="${c.phone}" data-name="${c.name.toLowerCase()}" style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.03);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="task-member-${c.phone}" value="${c.phone}" data-name="${c.name}" ${checked} class="task-member-checkbox" style="width:16px; height:16px; cursor:pointer;">
                                <label for="task-member-${c.phone}" style="cursor:pointer; font-size:0.95rem; color:var(--text-primary); font-weight:500;">
                                    ${c.name} <span style="font-weight:400; color:var(--text-secondary); font-size:0.85rem;">(${c.phone})</span>
                                </label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editMemberOption('${c.phone}', '${escapeHtml(c.name)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteMemberOption('${c.phone}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        function filterTaskMembersList() {
            const query = document.getElementById('taskMemberSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.task-member-checkbox-item');
            items.forEach(item => {
                const name = item.getAttribute('data-name');
                const phone = item.getAttribute('data-phone');
                if (name.includes(query) || phone.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function filterMembersList() {
            const query = document.getElementById('memberSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.member-checkbox-item');
            items.forEach(item => {
                const name = item.getAttribute('data-name');
                const phone = item.getAttribute('data-phone');
                if (name.includes(query) || phone.includes(query)) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function showAddManualMemberForm() {
            const container = document.getElementById('manualMemberFormContainer');
            container.style.display = 'flex';
            document.getElementById('manualMemberName').focus();
        }
        
        function hideAddManualMemberForm() {
            const container = document.getElementById('manualMemberFormContainer');
            container.style.display = 'none';
            document.getElementById('manualMemberName').value = '';
            document.getElementById('manualMemberPhone').value = '';
        }
        
        async function addNewManualMemberToList() {
            const name = document.getElementById('manualMemberName').value.trim();
            const phone = document.getElementById('manualMemberPhone').value.trim();
            
            if (!name || phone.length !== 10) {
                return alert("Please enter a valid Name and 10-digit Phone Number");
            }
            
            // Save to database
            try {
                await fetch(API_URL + 'employees', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name: name, phone: phone })
                });
            } catch (err) {
                console.error("Failed to save new member:", err);
            }
            
            // Add to manual contacts
            manual_added_contacts.push({ name: name, phone: phone });
            
            // Re-render, keeping currently checked selections plus the new one
            const checkedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(cb => cb.value);
            checkedPhones.push(phone);
            
            renderMembersChecklist(checkedPhones);
            hideAddManualMemberForm();
        }

        async function editMemberOption(phone, currentName) {
            const newName = prompt("Edit Member Name:", currentName);
            if (newName === null) return;
            const cleanName = newName.trim();
            if (!cleanName) return alert("Name cannot be empty");
            
            const newPhone = prompt("Edit Member Phone (10 digits):", phone);
            if (newPhone === null) return;
            const cleanPhone = newPhone.trim().replace(/[^0-9]/g, '');
            if (cleanPhone.length !== 10) return alert("Phone must be exactly 10 digits");
            
            try {
                await fetch(API_URL + 'employees', {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: cleanName,
                        phone: cleanPhone,
                        old_phone: phone
                    })
                });
                
                // Update local arrays
                all_contacts = all_contacts.map(c => c.phone === phone ? {name: cleanName, phone: cleanPhone} : c);
                manual_added_contacts = manual_added_contacts.map(c => c.phone === phone ? {name: cleanName, phone: cleanPhone} : c);
                
                // Keep selected checked
                const checkedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked'))
                    .map(cb => cb.value === phone ? cleanPhone : cb.value);
                
                renderMembersChecklist(checkedPhones);
            } catch (err) {
                console.error("Failed to edit member:", err);
            }
        }

        async function deleteMemberOption(phone) {
            if (!confirm("Are you sure you want to delete this member from the database?")) return;
            
            try {
                await fetch(API_URL + 'employees&phone=' + phone, {
                    method: 'DELETE'
                });
                
                // Remove from local arrays
                all_contacts = all_contacts.filter(c => c.phone !== phone);
                manual_added_contacts = manual_added_contacts.filter(c => c.phone !== phone);
                
                const checkedPhones = Array.from(document.querySelectorAll('.member-checkbox:checked'))
                    .map(cb => cb.value)
                    .filter(p => p !== phone);
                    
                renderMembersChecklist(checkedPhones);
            } catch (err) {
                console.error("Failed to delete member:", err);
            }
        }

        async function editReportOption(oldName) {
            const newName = prompt("Edit Report Type Name:", oldName);
            if (newName === null) return;
            const cleanName = newName.trim();
            if (!cleanName) return alert("Name cannot be empty");
            if (cleanName === oldName) return;
            
            // Update in report_types list
            report_types = report_types.map(r => r === oldName ? cleanName : r);
            try {
                await fetch(API_URL + 'settings/report_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({report_types: report_types})
                });
                
                // Re-render keeping selection
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked'))
                    .map(cb => cb.value === oldName ? cleanName : cb.value);
                renderReportCheckboxes(checked);
                updateNotesFromCheckedReports();
            } catch (err) {
                console.error("Failed to edit report type:", err);
            }
        }

        async function deleteReportOption(name) {
            if (!confirm(`Are you sure you want to delete report type "${name}"?`)) return;
            
            report_types = report_types.filter(r => r !== name);
            try {
                await fetch(API_URL + 'settings/report_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({report_types: report_types})
                });
                
                // Re-render keeping selection
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked'))
                    .map(cb => cb.value)
                    .filter(v => v !== name);
                renderReportCheckboxes(checked);
                updateNotesFromCheckedReports();
            } catch (err) {
                console.error("Failed to delete report type:", err);
            }
        }

        function showAddCustomReportForm() {
            const container = document.getElementById('customReportFormContainer');
            if (container) {
                container.style.display = 'flex';
                document.getElementById('newReportTypeInput').focus();
            }
        }
        
        function hideAddCustomReportForm() {
            const container = document.getElementById('customReportFormContainer');
            if (container) {
                container.style.display = 'none';
                document.getElementById('newReportTypeInput').value = '';
            }
        }

        async function editTaskOption(oldName) {
            const newName = prompt("Edit Task Type Name:", oldName);
            if (newName === null) return;
            const cleanName = newName.trim();
            if (!cleanName) return alert("Name cannot be empty");
            if (cleanName === oldName) return;
            
            task_types = task_types.map(t => t === oldName ? cleanName : t);
            try {
                await fetch(API_URL + 'settings/task_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_types: task_types})
                });
                
                const checked = Array.from(document.querySelectorAll('.task-report-checkbox:checked'))
                    .map(cb => cb.value === oldName ? cleanName : cb.value);
                renderTaskCheckboxes(checked);
                handleTaskTypeCheckboxChange();
            } catch (err) {
                console.error("Failed to edit task type:", err);
            }
        }

        async function deleteTaskOption(name) {
            if (!confirm(`Are you sure you want to delete task type "${name}"?`)) return;
            
            task_types = task_types.filter(t => t !== name);
            try {
                await fetch(API_URL + 'settings/task_types', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_types: task_types})
                });
                
                const checked = Array.from(document.querySelectorAll('.task-report-checkbox:checked'))
                    .map(cb => cb.value)
                    .filter(v => v !== name);
                renderTaskCheckboxes(checked);
                handleTaskTypeCheckboxChange();
            } catch (err) {
                console.error("Failed to delete task type:", err);
            }
        }

        function showAddCustomTaskForm() {
            const container = document.getElementById('customTaskFormContainer');
            if (container) {
                container.style.display = 'flex';
                document.getElementById('newTaskTypeInput').focus();
            }
        }
        
        function hideAddCustomTaskForm() {
            const container = document.getElementById('customTaskFormContainer');
            if (container) {
                container.style.display = 'none';
                document.getElementById('newTaskTypeInput').value = '';
            }
        }

        async function addNewTaskTypeCheckbox() {
            const input = document.getElementById('newTaskTypeInput');
            const cleanName = input.value.trim();
            if (!cleanName) return alert("Please type a task name first");
            
            if (!task_types.includes(cleanName)) {
                task_types.push(cleanName);
                try {
                    await fetch(API_URL + 'settings/task_types', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({task_types: task_types})
                    });
                } catch (e) {
                    console.error("Failed to save task type:", e);
                }
                const checked = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value);
                checked.push(cleanName);
                renderTaskCheckboxes(checked);
                handleTaskTypeCheckboxChange();
                hideAddCustomTaskForm();
            } else {
                alert("This task type already exists!");
            }
        }

        async function loadReportTypesDropdowns() {
            try {
                const res = await fetch(API_URL + 'settings/report_types');
                report_types = await res.json();
            } catch (err) {
                report_types = ["Production", "Feed", "Expenses", "Sales", "Profit and Loss"];
            }
            renderReportCheckboxes([]);
        }

        async function loadTaskTypesDropdowns() {
            try {
                const res = await fetch(API_URL + 'settings/task_types');
                task_types = await res.json();
            } catch (err) {
                task_types = ["Silo Cleaning / Check", "Wednesday Meeting Checklist", "Feed Formula (Requires Approval)"];
            }
            renderTaskCheckboxes([]);
        }

        function renderReportCheckboxes(selected = null) {
            const containerRem = document.getElementById('reportCheckboxesContainer');
            if (selected === null) {
                selected = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
            }
            if (containerRem) {
                containerRem.innerHTML = '';
                report_types.forEach(r => {
                    const checked = selected.includes(r) ? 'checked' : '';
                    containerRem.innerHTML += `
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.02);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="report-${r}" value="${r}" ${checked} class="report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="updateNotesFromCheckedReports()">
                                <label for="report-${r}" style="cursor:pointer; font-size:0.9rem; color:var(--text-primary); font-weight:500;">${r}</label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editReportOption('${escapeHtml(r)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteReportOption('${escapeHtml(r)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        function renderTaskCheckboxes(selectedTasks = null) {
            const containerTask = document.getElementById('taskTypesCheckboxContainer');
            if (selectedTasks === null) {
                selectedTasks = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value);
            }
            if (containerTask) {
                containerTask.innerHTML = '';
                // Append special Personal option
                const personalChecked = selectedTasks.includes('Personal') ? 'checked' : '';
                containerTask.innerHTML += `
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.02); background: rgba(59,130,246,0.03);">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <input type="checkbox" id="task-report-Personal" value="Personal" ${personalChecked} class="task-report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="handleTaskTypeCheckboxChange()">
                            <label for="task-report-Personal" style="cursor:pointer; font-size:0.9rem; color:var(--primary-color); font-weight:600;">Personal (Custom Message)</label>
                        </div>
                    </div>
                `;

                task_types.forEach(t => {
                    const checked = selectedTasks.includes(t) ? 'checked' : '';
                    containerTask.innerHTML += `
                        <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid rgba(0,0,0,0.02);">
                            <div style="display: flex; align-items: center; gap: 0.5rem;">
                                <input type="checkbox" id="task-report-${t}" value="${t}" ${checked} class="task-report-checkbox" style="width:16px; height:16px; cursor:pointer;" onchange="handleTaskTypeCheckboxChange()">
                                <label for="task-report-${t}" style="cursor:pointer; font-size:0.9rem; color:var(--text-primary); font-weight:500;">${t}</label>
                            </div>
                            <div style="display: flex; gap: 0.25rem;">
                                <button type="button" class="btn" onclick="editTaskOption('${escapeHtml(t)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(59,130,246,0.2); background: rgba(59,130,246,0.05); color: var(--primary-color); cursor: pointer; margin: 0;">Edit</button>
                                <button type="button" class="btn" onclick="deleteTaskOption('${escapeHtml(t)}')" style="padding: 2px 6px; font-size: 0.75rem; border-radius: 4px; border: 1px solid rgba(239,68,68,0.2); background: rgba(239,68,68,0.05); color: #ef4444; cursor: pointer; margin: 0;">Delete</button>
                            </div>
                        </div>
                    `;
                });
            }
        }

        function updateNotesFromCheckedReports() {
            const checked = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
            const notesTextarea = document.getElementById('remNotes');
            if (checked.length > 0) {
                notesTextarea.value = `Please submit the ${checked.join(', ')} report(s).`;
            } else {
                notesTextarea.value = '';
            }
        }

        async function addNewReportTypeCheckbox() {
            const input = document.getElementById('newReportTypeInput');
            const cleanName = input.value.trim();
            if (!cleanName) return alert("Please type a report name first");
            
            if (!report_types.includes(cleanName)) {
                report_types.push(cleanName);
                try {
                    await fetch(API_URL + 'settings/report_types', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({report_types: report_types})
                    });
                } catch (e) {
                    console.error("Failed to save report type:", e);
                }
                const checked = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
                checked.push(cleanName); // auto select new one
                renderReportCheckboxes(checked);
                updateNotesFromCheckedReports();
                hideAddCustomReportForm();
            } else {
                alert("This report type already exists!");
            }
        }

        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
                e.currentTarget.classList.add('active');
                
                const targetView = e.currentTarget.getAttribute('data-target');
                document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
                document.getElementById(targetView).classList.add('active');

                if (targetView === 'tasks_view') {
                    fetchTasks();
                } else if (targetView === 'godown_inventory_view') {
                    fetchInventory();
                } else if (targetView === 'flocks_view') {
                    fetchFlocks();
                }
            });
        });

        function openModal(modalId) { document.getElementById(modalId).classList.add('active'); }
        function closeModal(modalId) { document.getElementById(modalId).classList.remove('active'); }

        function parseLocalStatusTime(dateStr) {
            if (!dateStr) return new Date();
            const normalized = dateStr.replace(/-/g, '/').replace('T', ' ');
            return new Date(normalized);
        }

        function formatDateTime(isoString) {
            if (!isoString) return '-';
            const dt = parseLocalStatusTime(isoString);
            return dt.toLocaleString('en-IN', {
                timeZone: 'Asia/Kolkata',
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }) + ' IST';
        }

        function formatIST(rawDbTimestamp) {
            // DB stores timestamps as "2026-07-11 08:30:00" (UTC or local server time)
            if (!rawDbTimestamp) return '-';
            // Treat as UTC by appending Z if no timezone info
            const normalized = rawDbTimestamp.replace(' ', 'T');
            const hasZ = normalized.endsWith('Z') || normalized.includes('+');
            const dt = new Date(hasZ ? normalized : normalized + 'Z');
            if (isNaN(dt)) return rawDbTimestamp; // fallback if unparseable
            return dt.toLocaleString('en-IN', {
                timeZone: 'Asia/Kolkata',
                day: '2-digit',
                month: 'short',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            }) + ' IST';
        }

        function showReminderDetails(id) {
            const r = reminders.find(x => x.id == id);
            if (r && r.verification_details) {
                alert("Submission Verification Details:\n\n" + r.verification_details);
            } else {
                alert("No details available.");
            }
        }

        function showTaskDetails(id) {
            const t = tasksList.find(x => x.id == id);
            if (t && t.completion_details) {
                alert("Completion Details:\n\n" + t.completion_details);
            } else {
                alert("No details available.");
            }
        }

        let reminders = [];
        async function fetchReminders() {
            const res = await fetch(API_URL + 'reminders');
            reminders = await res.json();
            const tbody = document.getElementById('reminders-tbody');
            tbody.innerHTML = '';
            
            reminders.forEach(r => {
                const badgeClass = r.status === 'sent' ? 'badge-green' : (r.status === 'pending' ? 'badge-orange' : (r.status === 'skipped' ? 'badge-blue' : ''));
                const groupText = r.whatsapp_group_id ? `<strong style="color:var(--primary-color)">${r.group_name}</strong>` : `<span style="color:var(--text-secondary)">No Group / Private Only</span>`;
                const reportsText = r.report_types ? r.report_types.split(',').map(rep => `<span class="badge badge-blue" style="margin-right:0.25rem; font-size:0.7rem; display:inline-block; margin-top:2px;">${rep.trim()}</span>`).join(' ') : '<span style="color:var(--text-secondary)">Custom Notes Only</span>';
                
                const names = (r.person_name || '').split(',').map(n => n.trim());
                const phones = (r.person_phone || '').split(',').map(p => p.trim());
                const formattedAssignees = names.map((name, idx) => {
                    const phone = phones[idx] || '';
                    return `${name} (${phone})`;
                }).join(', ');

                // Build submitted status badge for reminders based on dynamic verification
                let remSubBadge, remSubLabel;
                if (r.is_submitted) {
                    remSubBadge = 'background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0;';
                    remSubLabel = '🟢 Submitted (YES)';
                } else {
                    // Check if it is overdue (pending but trigger_time is in the past)
                    const trigTs = r.trigger_time ? new Date(r.trigger_time.replace(/-/g,'/').replace('T',' ')).getTime() : null;
                    const nowMs = new Date().getTime();
                    if (trigTs && trigTs < nowMs) {
                        remSubBadge = 'background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;';
                        remSubLabel = '🔴 Missing (NO)';
                    } else {
                        remSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                        remSubLabel = '🟡 Pending (NO)';
                    }
                }
                tbody.innerHTML += `<tr>
                    <td><strong>${formattedAssignees}</strong></td>
                    <td>${groupText}</td>
                    <td>${reportsText}</td>
                    <td>${r.task_notes}</td>
                    <td style="text-transform: capitalize; font-weight: 500;">${r.frequency || 'daily'}</td>
                    <td style="text-transform: capitalize; font-weight: 500; color: #b45309;">${r.repeat_interval && r.repeat_interval !== 'none' ? r.repeat_interval : 'None'}</td>
                    <td>${formatDateTime(r.trigger_time)}</td>
                    <td><span class="badge ${badgeClass}">${r.status}</span></td>
                    <td><span style="display:inline-block; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:600; white-space:nowrap; ${remSubBadge}">${remSubLabel}</span></td>
                    <td>
                        <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
                            <button class="btn btn-secondary" onclick="editReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Edit</button> 
                            ${r.status === 'pending' ? `<button class="btn btn-primary" onclick="markReminderDone(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Done</button>` : ''}
                            <button class="btn btn-danger" onclick="deleteReminder(${r.id})" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; margin: 0;">Delete</button>
                            ${r.verification_details ? '<button class="btn" style="padding: 0.3rem 0.6rem; font-size: 0.8rem; background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; margin: 0;" onclick="showReminderDetails(' + r.id + ')">Details</button>' : ''}
                        </div>
                    </td>
                </tr>`;
            });
            
            document.getElementById('stat-employees').innerText = new Set(reminders.map(r => r.person_phone)).size;
            document.getElementById('stat-groups').innerText = new Set(reminders.map(r => r.whatsapp_group_id).filter(g => g)).size;
            document.getElementById('stat-alarms').innerText = reminders.length;
        }

        function filterRemindersTable() {
            const query = document.getElementById('remindersSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#reminders-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        function filterTasksTable() {
            const query = document.getElementById('tasksSearchInput').value.toLowerCase();
            const rows = document.querySelectorAll('#tasks-tbody tr');
            rows.forEach(row => {
                const text = row.innerText.toLowerCase();
                if (text.includes(query)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        }

        async function fetchWahaGroups() {
            try {
                const res = await fetch(API_URL + 'waha/groups');
                const data = await res.json();
                if (data.status === 'success') {
                    waha_groups = data.groups || [];
                    hidden_groups = data.hidden_groups || [];
                    waha_groups.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
                } else {
                    waha_groups = [];
                    hidden_groups = [];
                }
            } catch (err) {
                waha_groups = [];
                hidden_groups = [];
            }
            updateGroupSelect();
        }

        function updateGroupSelect() {
            const select = document.getElementById('remGroupSelect');
            if (select) {
                select.innerHTML = '<option value="">No Group / Private Only</option>';
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => { select.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
            }
            const taskSelect = document.getElementById('task-group-id');
            if (taskSelect) {
                taskSelect.innerHTML = '<option value="">No Group / Private Only</option>';
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => { taskSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`; });
            }
        }

        function openReminderModal() {
            document.getElementById('reminderForm').reset();
            document.getElementById('editReminderId').value = '';
            document.getElementById('reminderModalTitle').innerText = 'Create Reminder';
            document.getElementById('memberSearchInput').value = '';
            hideAddManualMemberForm();
            hideAddCustomReportForm();
            
            manual_added_contacts = [];
            renderMembersChecklist([]);
            renderReportCheckboxes([]);
            
            // Pre-populate with current local date and time by default
            const now = new Date();
            const format = n => String(n).padStart(2, '0');
            document.getElementById('remDate').value = `${now.getFullYear()}-${format(now.getMonth() + 1)}-${format(now.getDate())}`;
            document.getElementById('remTime').value = `${format(now.getHours())}:${format(now.getMinutes())}`;
            
            openModal('reminderModal');
        }

        function editReminder(id) {
            const r = reminders.find(x => x.id == id);
            if (!r) return;
            document.getElementById('editReminderId').value = r.id;
            document.getElementById('reminderModalTitle').innerText = 'Edit Reminder';
            document.getElementById('memberSearchInput').value = '';
            hideAddManualMemberForm();
            hideAddCustomReportForm();
            
            // Ensure all edited persons exist in checklist contacts and are checked
            const phones = (r.person_phone || '').split(',').map(p => p.trim());
            const names = (r.person_name || '').split(',').map(n => n.trim());
            
            phones.forEach((phone, idx) => {
                const name = names[idx] || phone;
                if (phone) {
                    const exists = [...all_contacts, ...manual_added_contacts].some(c => c.phone === phone);
                    if (!exists) {
                        manual_added_contacts.push({ name: name, phone: phone });
                    }
                }
            });
            
            renderMembersChecklist(phones);
            
            document.getElementById('remGroupSelect').value = r.whatsapp_group_id || '';
            document.getElementById('remNotes').value = r.task_notes;
            
            const selectedReports = r.report_types ? r.report_types.split(',').map(s => s.trim()) : [];
            renderReportCheckboxes(selectedReports);
            
            document.getElementById('remFrequency').value = r.frequency || 'daily';
            document.getElementById('remRepeatInterval').value = r.repeat_interval || 'none';
            
            const dt = parseLocalStatusTime(r.trigger_time);
            const format = n => String(n).padStart(2, '0');
            document.getElementById('remDate').value = `${dt.getFullYear()}-${format(dt.getMonth() + 1)}-${format(dt.getDate())}`;
            document.getElementById('remTime').value = `${format(dt.getHours())}:${format(dt.getMinutes())}`;
            
            openModal('reminderModal');
        }

        async function handleReminderSubmit(e) {
            e.preventDefault();
            const d = document.getElementById('remDate').value;
            const t = document.getElementById('remTime').value;
            if (!d || !t) return alert("Please select a date and time");
            const triggerTime = `${d}T${t}:00`;

            const checkedReports = Array.from(document.querySelectorAll('.report-checkbox:checked')).map(cb => cb.value);
            const reportTypesStr = checkedReports.length > 0 ? checkedReports.join(',') : null;

            // Get selected members
            const checkedMembers = Array.from(document.querySelectorAll('.member-checkbox:checked')).map(cb => ({
                name: cb.getAttribute('data-name'),
                phone: cb.value
            }));

            if (checkedMembers.length === 0) {
                return alert("Please select at least one member to assign");
            }

            const names = checkedMembers.map(m => m.name).join(', ');
            const phones = checkedMembers.map(m => m.phone).join(', ');

            const editId = document.getElementById('editReminderId').value;
            
            if (editId) {
                // Edit Mode: Update reminder
                const url = API_URL + 'reminders/' + editId;
                await fetch(url, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        person_name: names,
                        person_phone: phones,
                        whatsapp_group_id: document.getElementById('remGroupSelect').value || null,
                        report_types: reportTypesStr,
                        task_notes: document.getElementById('remNotes').value,
                        trigger_time: triggerTime,
                        frequency: document.getElementById('remFrequency').value,
                        repeat_interval: document.getElementById('remRepeatInterval').value
                    })
                });
            } else {
                // Create Mode: Create a single reminder with all checked members
                const url = API_URL + 'reminders';
                await fetch(url, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        person_name: names,
                        person_phone: phones,
                        whatsapp_group_id: document.getElementById('remGroupSelect').value || null,
                        report_types: reportTypesStr,
                        task_notes: document.getElementById('remNotes').value,
                        trigger_time: triggerTime,
                        frequency: document.getElementById('remFrequency').value,
                        repeat_interval: document.getElementById('remRepeatInterval').value
                    })
                });
            }
            
            closeModal('reminderModal');
            fetchReminders();
        }

        async function deleteReminder(id) {
            if(confirm("Delete reminder?")) {
                await fetch(API_URL + 'reminders/' + id, {method: 'DELETE'});
                fetchReminders();
            }
        }

        async function resetDailyReminders() {
            const res = await fetch(API_URL + 'reminders/reset-daily', {method: 'POST'});
            const data = await res.json();
            if (data.success) {
                alert(`✅ Done! ${data.reset_count} recurring reminder(s) advanced to their next scheduled date and set to Pending.`);
                fetchReminders();
            } else {
                alert('❌ Reset failed. Please try again.');
            }
        }

        async function markReminderDone(id) {
            if(confirm("Mark this reminder as done?")) {
                const res = await fetch(API_URL + 'reminders/' + id + '/trigger', {method: 'POST'});
                const data = await res.json();
                if (data.success) {
                    fetchReminders();
                } else {
                    alert('❌ Failed to mark as done. Please try again.');
                }
            }
        }

        function openVisibilityModal() {
            const container = document.getElementById('visibilityListContainer');
            container.innerHTML = '';
            const sorted = [...waha_groups].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
            sorted.forEach(g => {
                const checked = !hidden_groups.includes(g.id) ? 'checked' : '';
                container.innerHTML += `
                    <div class="group-vis-item" style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.05);">
                        <input type="checkbox" id="vis-${g.id}" value="${g.id}" ${checked} class="group-vis-checkbox" style="width: 18px; height: 18px; cursor: pointer;">
                        <label for="vis-${g.id}" style="font-weight: 500; cursor: pointer; user-select: none; color: var(--text-primary); font-size: 0.95rem;">${g.name || 'Unnamed Group'}</label>
                    </div>
                `;
            });
            document.getElementById('groupSearchInput').value = '';
            openModal('visibilityModal');
        }

        function filterVisibilityList() {
            const q = document.getElementById('groupSearchInput').value.toLowerCase();
            const items = document.querySelectorAll('.group-vis-item');
            items.forEach(item => {
                const label = item.querySelector('label').innerText.toLowerCase();
                item.style.display = label.includes(q) ? 'flex' : 'none';
            });
        }
        
        async function saveGroupVisibility() {
            const checkboxes = document.querySelectorAll('.group-vis-checkbox');
            const hidden = [];
            checkboxes.forEach(cb => {
                if (!cb.checked) hidden.push(cb.value);
            });
            
            await fetch(API_URL + 'waha/groups/visibility', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(hidden)
            });
            
            hidden_groups = hidden;
            updateGroupSelect();
            closeModal('visibilityModal');
            fetchReminders();
        }

        let lastWahaStatus = '';
        async function checkWahaStatus(forceModal = false) {
            try {
                const response = await fetch(API_URL + 'waha/status');
                const data = await response.json();
                
                const status = data.status || 'UNKNOWN';
                const qrCode = data.qr_code || '';

                // ── Colour coding ─────────────────────────────────────────────
                const dotColor = status === 'WORKING'
                    ? 'var(--success-color)'
                    : (status === 'SCAN_QR_CODE' ? 'var(--danger-color)'
                    : (status === 'STOPPED' || status === 'FAILED' ? '#ef4444' : '#94a3b8'));

                const headerDot = document.getElementById('waha-status-dot');
                if (headerDot) headerDot.style.backgroundColor = dotColor;
                const headerText = document.getElementById('waha-status-text');
                if (headerText) headerText.innerText = `WAHA: ${status}`;
                const viewDot = document.getElementById('waha-view-status-dot');
                if (viewDot) viewDot.style.backgroundColor = dotColor;
                const viewText = document.getElementById('waha-view-status-text');
                if (viewText) viewText.innerText = status;

                // ── Status Banner (shown in WAHA status view) ─────────────────
                let banner = document.getElementById('waha-status-banner');
                if (!banner) {
                    banner = document.createElement('div');
                    banner.id = 'waha-status-banner';
                    banner.style.cssText = 'margin-bottom:1.25rem; padding:0.9rem 1.2rem; border-radius:10px; font-weight:600; font-size:0.95rem; display:none;';
                    const card = document.querySelector('#waha_settings_view .card');
                    if (card) card.parentNode.insertBefore(banner, card);
                }

                if (status === 'STOPPED' || status === 'FAILED') {
                    banner.style.display = 'block';
                    banner.style.background = '#fef2f2';
                    banner.style.border = '1px solid #fecaca';
                    banner.style.color = '#dc2626';
                    banner.innerHTML = '&#9888; <strong>WhatsApp Bot is ' + status + '.</strong> Auto-restart is in progress (every 5 min). The QR code will appear here automatically once WAHA is ready. Check your email for alerts.';
                } else if (status === 'SCAN_QR_CODE') {
                    banner.style.display = 'block';
                    banner.style.background = '#fff7ed';
                    banner.style.border = '1px solid #fed7aa';
                    banner.style.color = '#c2410c';
                    banner.innerHTML = '&#128247; <strong>QR Scan Required!</strong> Scan the QR code below using WhatsApp on your phone to reconnect the bot.';
                } else if (status === 'WORKING') {
                    banner.style.display = 'block';
                    banner.style.background = '#f0fdf4';
                    banner.style.border = '1px solid #bbf7d0';
                    banner.style.color = '#16a34a';
                    banner.innerHTML = '&#10003; <strong>WhatsApp Bot is Online and Working.</strong> All reminders are being sent normally.';
                } else {
                    banner.style.display = 'none';
                }

                // ── QR Code display ───────────────────────────────────────────
                const inlineContainer = document.getElementById('waha-qr-container-inline');
                const inlineImg = document.getElementById('waha-qr-img-inline');
                const modalContainer = document.getElementById('modal-qr-container');

                if (status === 'SCAN_QR_CODE') {
                    if (inlineContainer) inlineContainer.style.display = 'block';
                    if (qrCode) {
                        const qrImgHtml = `<img src="${qrCode}" style="max-width:280px; border:1px solid rgba(0,0,0,0.1); border-radius:8px;" alt="Scan WhatsApp QR">`;
                        if (inlineImg) inlineImg.innerHTML = qrImgHtml;
                        if (modalContainer) modalContainer.innerHTML = qrImgHtml;
                    } else {
                        if (inlineImg) inlineImg.innerHTML = '<p style="color:#94a3b8; font-size:0.9rem;">&#8635; QR loading... refresh in a moment.</p>';
                        if (modalContainer) modalContainer.innerHTML = '<div id="modal-qr-placeholder">&#8635; QR loading... please wait.</div>';
                    }
                    // Auto-open modal on state change
                    if ((lastWahaStatus !== 'SCAN_QR_CODE' || forceModal) && !document.getElementById('wahaQrModal').classList.contains('active')) {
                        openModal('wahaQrModal');
                    }
                } else {
                    if (inlineContainer) inlineContainer.style.display = 'none';
                    closeModal('wahaQrModal');
                }

                lastWahaStatus = status;
            } catch (err) {
                console.error("Failed to check WAHA status:", err);
            }
        }
        
        function openWahaQrFromIndicator() {
            if (lastWahaStatus === 'SCAN_QR_CODE') {
                openModal('wahaQrModal');
            } else {
                checkWahaStatus(true);
            }
        }
        
        async function loadWahaEvents() {
            try {
                const response = await fetch(API_URL + 'waha/events');
                const events = await response.json();
                
                const tbody = document.getElementById('waha-events-tbody');
                if (!tbody) return;
                
                if (events.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-secondary);">No connection events logged yet.</td></tr>';
                    return;
                }
                
                tbody.innerHTML = '';
                events.forEach(e => {
                    tbody.innerHTML += `
                        <tr>
                        <td style="font-weight: 500; white-space: nowrap;">${formatIST(e.timestamp)}</td>
                            <td><span style="padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: 600; background: rgba(59,130,246,0.1); color: var(--primary-color);">${e.event_type}</span></td>
                            <td><span style="font-weight: 600; color: ${e.status === 'WORKING' ? 'var(--success-color)' : 'var(--danger-color)'}">${e.status}</span></td>
                            <td style="color: var(--text-secondary); font-size: 0.9rem;">${escapeHtml(e.details || '')}</td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error("Failed to load WAHA events:", err);
            }
        }
        
        async function loadWahaSettings() {
            try {
                const response = await fetch(API_URL + 'settings/waha');
                const settings = await response.json();
                
                document.getElementById('settingAlertPhone').value = settings.waha_alert_phone || '';
                document.getElementById('settingAlertEmail').value = settings.smtp_to || '';
                document.getElementById('settingSmtpHost').value = settings.smtp_host || '';
                document.getElementById('settingSmtpPort').value = settings.smtp_port || '';
                document.getElementById('settingSmtpUser').value = settings.smtp_user || '';
                document.getElementById('settingSmtpPass').value = settings.smtp_pass || '';
                
                if (settings.smtp_to) document.getElementById('info-smtp-to').innerText = settings.smtp_to;
                if (settings.waha_alert_phone) document.getElementById('info-waha-phone').innerText = settings.waha_alert_phone;
            } catch (err) {
                console.error("Failed to load WAHA settings:", err);
            }
        }
        
        async function saveWahaSettings(e) {
            e.preventDefault();
            try {
                const payload = {
                    waha_alert_phone: document.getElementById('settingAlertPhone').value,
                    smtp_to: document.getElementById('settingAlertEmail').value,
                    smtp_host: document.getElementById('settingSmtpHost').value,
                    smtp_port: document.getElementById('settingSmtpPort').value,
                    smtp_user: document.getElementById('settingSmtpUser').value,
                    smtp_pass: document.getElementById('settingSmtpPass').value
                };
                
                const response = await fetch(API_URL + 'settings/waha', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const res = await response.json();
                if (res.success) {
                    closeModal('alertSettingsModal');
                    loadWahaSettings();
                    // Show a non-blocking success toast
                    const toast = document.createElement('div');
                    toast.innerText = '✓ Alert settings saved!';
                    toast.style.cssText = 'position:fixed;bottom:2rem;right:2rem;background:#10b981;color:white;padding:0.75rem 1.5rem;border-radius:10px;font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,0.15);z-index:9999;transition:opacity 0.4s;';
                    document.body.appendChild(toast);
                    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 400); }, 2500);
                } else {
                    alert("Failed to save settings.");
                }
            } catch (err) {
                console.error("Failed to save WAHA settings:", err);
                alert("Error saving settings.");
            }
        }

        function openAlertSettingsModal() {
            loadWahaSettings();
            openModal('alertSettingsModal');
        }
        let tasksList = [];

        async function fetchTasks() {
            try {
                const res = await fetch(API_URL + 'tasks');
                tasksList = await res.json();
                renderTasks(tasksList);
            } catch (err) {
                console.error("Error fetching tasks:", err);
            }
        }

        function renderTasks(tasks) {
            const tbody = document.getElementById('tasks-tbody');
            tbody.innerHTML = '';
            
            // Map JID to Group Names
            const groups_list = waha_groups || [];

            const nowTs = new Date().getTime();
            tasks.forEach(t => {
                // Auto-detect overdue client-side: if due_time is in past and not completed
                const dueTs = t.due_time ? new Date(t.due_time.replace(/-/g, '/').replace('T', ' ')).getTime() : null;
                if (t.status === 'pending' && dueTs && dueTs < nowTs) {
                    t.status = 'overdue';
                }
                let badgeClass = 'badge-blue';
                if (t.status === 'completed') badgeClass = 'badge-green';
                else if (t.status === 'overdue') badgeClass = 'badge-red';
                else if (t.status === 'pending_approval') badgeClass = 'badge-yellow';
                else if (t.status === 'pending') badgeClass = 'badge-orange';

                // Find group name
                let groupName = 'Private Only / No Group';
                if (t.whatsapp_group_id) {
                    const found = groups_list.find(g => g.id === t.whatsapp_group_id);
                    if (found) {
                        groupName = found.name;
                    } else {
                        groupName = t.whatsapp_group_id.split('@')[0];
                    }
                }

                // Assigned Task badge
                let taskTypeLabel = t.task_type.toUpperCase();
                if (t.task_type === 'general') taskTypeLabel = 'SILO CLEANING';
                else if (t.task_type === 'meeting') taskTypeLabel = 'WED MEETING';
                else if (t.task_type === 'approval') taskTypeLabel = 'FEED APPROVAL';
                else if (t.task_type === 'personal') taskTypeLabel = 'PERSONAL';

                const names = (t.assigned_person_name || '').split(',').map(n => n.trim()).filter(Boolean);
                const phones = (t.assigned_person_phone || '').split(',').map(p => p.trim()).filter(Boolean);
                const formattedAssignees = names.length > 0 ? names.map((name, idx) => {
                    const phone = phones[idx] || '';
                    return `${name} (${phone})`;
                }).join(', ') : (t.assigned_person_name || 'Group Member');

                // Build submitted status badge for tasks
                let taskSubBadge, taskSubLabel;
                if (t.status === 'completed') {
                    taskSubBadge = 'background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0;';
                    taskSubLabel = '🟢 Submitted (YES)';
                } else if (t.status === 'skipped') {
                    // Skipped = task completed BEFORE due time (early submission)
                    taskSubBadge = 'background:#dcfce7; color:#16a34a; border:1px solid #bbf7d0;';
                    taskSubLabel = '🟢 Submitted (YES)';
                } else if (t.status === 'overdue') {
                    taskSubBadge = 'background:#fee2e2; color:#dc2626; border:1px solid #fca5a5;';
                    taskSubLabel = '🔴 Overdue (NO)';
                } else if (t.status === 'pending_approval') {
                    taskSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                    taskSubLabel = '🟡 Pending Approval';
                } else {
                    taskSubBadge = 'background:#fefce8; color:#ca8a04; border:1px solid #fde68a;';
                    taskSubLabel = '🟡 Pending (NO)';
                }

                tbody.innerHTML += `
                    <tr>
                        <td><strong>${formattedAssignees}</strong></td>
                        <td>${groupName}</td>
                        <td><span class="badge badge-blue">${taskTypeLabel}</span></td>
                        <td>
                            <div style="max-width:250px; font-size:0.9rem;">
                                ${t.task_name}
                                ${t.approver_phone ? `<br><small style="color:var(--text-secondary)">Approver: ${t.approver_phone}</small>` : ''}
                            </div>
                        </td>
                        <td style="text-transform: capitalize; font-weight: 500;">${t.frequency || 'once'}</td>
                        <td style="text-transform: capitalize; font-weight: 500; color: #b45309;">${t.repeat_interval && t.repeat_interval !== 'none' ? t.repeat_interval : 'None'}</td>
                        <td>${formatDateTime(t.due_time)}</td>
                        <td><span class="badge ${badgeClass}" style="text-transform: uppercase;">${t.status}</span></td>
                        <td><span style="display:inline-block; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:600; white-space:nowrap; ${taskSubBadge}">${taskSubLabel}</span></td>
                        <td>
                            <div style="display:flex; gap:0.25rem; flex-wrap:wrap;">
                                <button class="btn btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="editTask(${t.id})">Edit</button>
                                ${t.status !== 'completed' ? `<button class="btn btn-primary" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="completeTask(${t.id})">Done</button>` : ''}
                                <button class="btn" style="padding:0.25rem 0.5rem; font-size:0.8rem; background:#fee2e2; color:#ef4444; border:1px solid #fca5a5; margin:0;" onclick="deleteTask(${t.id})">Delete</button>
                                ${t.completion_details ? '<button class="btn" style="padding:0.25rem 0.5rem; font-size:0.8rem; margin:0;" onclick="showTaskDetails(' + t.id + ')">Details</button>' : ''}
                            </div>
                        </td>
                    </tr>
                `;
            });
            
            // Populate Tasks & Approvals dashboard stats
            const uniqueTaskPhones = new Set();
            tasks.forEach(t => {
                if (t.assigned_person_phone) {
                    t.assigned_person_phone.split(',').forEach(p => uniqueTaskPhones.add(p.trim()));
                }
            });
            uniqueTaskPhones.delete(''); // remove empty if any
            
            const taskStatEmployees = document.getElementById('stat-task-employees');
            if (taskStatEmployees) taskStatEmployees.innerText = uniqueTaskPhones.size;
            
            const taskStatGroups = document.getElementById('stat-task-groups');
            if (taskStatGroups) taskStatGroups.innerText = new Set(tasks.map(t => t.whatsapp_group_id).filter(g => g)).size;
            
            const statTasks = document.getElementById('stat-tasks');
            if (statTasks) statTasks.innerText = tasks.length;
        }

        function openCreateTaskModal() {
            document.getElementById('task-id').value = '';
            document.getElementById('task-form').reset();
            document.getElementById('task-modal-title').innerText = "Create Task";
            
            // Populate groups select options dynamically (filtering hidden ones)
            const groupSelect = document.getElementById('task-group-id');
            groupSelect.innerHTML = '<option value="">No Group / Private Only</option>';
            if (waha_groups) {
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => {
                    groupSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`;
                });
            }

            renderMembersChecklist([], []);
            renderTaskCheckboxes([]);
            handleTaskTypeCheckboxChange();
            openModal('createTaskModal');
        }

        function closeCreateTaskModal() {
            closeModal('createTaskModal');
        }

        function handleTaskTypeCheckboxChange() {
            const personalCheckbox = document.getElementById('task-report-Personal');
            const messageGroup = document.getElementById('task-message-group');
            const approverRow = document.getElementById('task-approver-row');
            
            if (personalCheckbox && personalCheckbox.checked) {
                messageGroup.style.display = 'block';
            } else {
                messageGroup.style.display = 'none';
            }
            
            const checkedTypes = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value.toLowerCase());
            const hasFeed = checkedTypes.some(t => t.includes('feed') || t.includes('formula'));
            if (hasFeed) {
                approverRow.style.display = 'block';
            } else {
                approverRow.style.display = 'none';
            }
        }

        async function handleTaskSubmit(e) {
            e.preventDefault();
            const taskId = document.getElementById('task-id').value;
            
            // Get selected members
            const selectedMembers = Array.from(document.querySelectorAll('.task-member-checkbox:checked'));
            const phones = selectedMembers.map(cb => cb.value).join(', ');
            const names = selectedMembers.map(cb => cb.getAttribute('data-name')).join(', ');
            
            // Get selected task/report types
            const checkedTaskTypes = Array.from(document.querySelectorAll('.task-report-checkbox:checked')).map(cb => cb.value).join(', ');
            
            const groupSelectVal = document.getElementById('task-group-id').value;
            
            if (!phones && !groupSelectVal) {
                alert("Please select either a member or a WhatsApp group!");
                return;
            }
            
            if (!checkedTaskTypes) {
                alert("Please select at least one Assigned Task / Report type!");
                return;
            }
            
            let taskName = '';
            const personalChecked = document.getElementById('task-report-Personal')?.checked;
            if (personalChecked) {
                taskName = document.getElementById('task-name').value.trim();
                if (!taskName) {
                    alert("Please type a custom text message for your Personal reminder!");
                    return;
                }
            } else {
                taskName = checkedTaskTypes;
            }
            
            const payload = {
                task_name: taskName,
                task_type: checkedTaskTypes,
                assigned_person_name: names || null,
                assigned_person_phone: phones || null,
                whatsapp_group_id: groupSelectVal || null,
                due_time: document.getElementById('task-due-time').value,
                completion_keywords: null,
                approver_phone: document.getElementById('task-approver-phone').value || null,
                frequency: document.getElementById('task-frequency').value,
                repeat_interval: document.getElementById('task-repeat-interval').value
            };

            try {
                const url = taskId ? (API_URL + 'tasks/' + taskId) : (API_URL + 'tasks');
                const method = taskId ? 'PUT' : 'POST';
                const res = await fetch(url, {
                    method: method,
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                if (data.success) {
                    closeCreateTaskModal();
                    fetchTasks();
                } else {
                    alert("Error saving task: " + (data.error || JSON.stringify(data)));
                }
            } catch (err) {
                console.error("Error submitting task:", err);
            }
        }

        async function editTask(id) {
            const t = tasksList.find(x => x.id === id);
            if (!t) return;
            
            // Re-populate groups list first (filtering hidden ones)
            const groupSelect = document.getElementById('task-group-id');
            groupSelect.innerHTML = '<option value="">No Group / Private Only</option>';
            if (waha_groups) {
                const visible = waha_groups.filter(g => !hidden_groups.includes(g.id));
                visible.forEach(g => {
                    groupSelect.innerHTML += `<option value="${g.id}">${g.name}</option>`;
                });
            }
            
            document.getElementById('task-id').value = t.id;
            document.getElementById('task-group-id').value = t.whatsapp_group_id || '';
            
            if (t.due_time) {
                const dt = new Date(t.due_time);
                const tzoffset = dt.getTimezoneOffset() * 60000;
                const localISOTime = (new Date(dt.getTime() - tzoffset)).toISOString().slice(0, 16);
                document.getElementById('task-due-time').value = localISOTime;
            }
            
            document.getElementById('task-frequency').value = t.frequency || 'once';
            document.getElementById('task-repeat-interval').value = t.repeat_interval || 'none';
            document.getElementById('task-approver-phone').value = t.approver_phone || '';
            
            // Parse assigned person phones & names
            const selectedPhones = (t.assigned_person_phone || '').split(',').map(p => p.trim()).filter(Boolean);
            renderMembersChecklist([], selectedPhones);
            
            // Parse assigned task/report types
            const selectedTasks = (t.task_type || '').split(',').map(x => x.trim()).filter(Boolean);
            renderTaskCheckboxes(selectedTasks);
            
            // Set custom message value if Personal was checked
            if (selectedTasks.includes('Personal')) {
                document.getElementById('task-name').value = t.task_name || '';
            } else {
                document.getElementById('task-name').value = '';
            }
            
            document.getElementById('task-modal-title').innerText = "Edit Task";
            handleTaskTypeCheckboxChange();
            openModal('createTaskModal');
        }

        async function completeTask(id) {
            if (!confirm("Are you sure you want to mark this task as completed?")) return;
            try {
                const res = await fetch(API_URL + `tasks/${id}/complete`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({details: "Manually marked completed from dashboard"})
                });
                const data = await res.json();
                if (data.success) {
                    fetchTasks();
                } else {
                    alert('Failed to mark as done. Please try again.');
                }
            } catch (err) {
                console.error("Error completing task:", err);
            }
        }

        async function deleteTask(id) {
            if (!confirm("Are you sure you want to delete this task?")) return;
            try {
                const res = await fetch(API_URL + `tasks/${id}`, { method: 'DELETE' });
                const data = await res.json();
                if (data.success) {
                    fetchTasks();
                }
            } catch (err) {
                console.error("Error deleting task:", err);
            }
        }

        let flocksList = [];

        async function fetchFlocks() {
            try {
                const res = await fetch(API_URL + 'flocks');
                flocksList = await res.json();
                renderFlocks(flocksList);
            } catch (err) {
                console.error("Error fetching flocks:", err);
            }
        }

        function renderFlocks(flocks) {
            const container = document.getElementById('flocks-grid-container');
            container.innerHTML = '';
            
            let totalLive = 0;
            flocks.forEach(f => {
                totalLive += f.total_live_birds || 0;
                const card = document.createElement('div');
                card.className = 'card flock-card';
                card.style.background = '#ffffff';
                card.style.borderRadius = '16px';
                card.style.padding = '1.25rem';
                card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.06)';
                card.style.display = 'flex';
                card.style.flexDirection = 'column';
                card.style.justify = 'space-between';
                card.style.margin = '0';
                
                const dateObj = new Date(f.hatch_date);
                const formattedDate = dateObj.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
                
                const batchText = f.batch_id && f.batch_id !== 'None' ? escapeHtml(f.batch_id) : 'None';
                
                card.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                            <h3 style="margin: 0; font-size: 1.35rem; color: #2563eb; font-weight: 800;">${escapeHtml(f.shed_name)}</h3>
                            <button style="background: #eab308; color: #000000; border: none; border-radius: 6px; padding: 3px 12px; font-weight: 700; font-size: 0.85rem; cursor: pointer;" onclick="openEditFlockModal(${f.id})">Edit</button>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 10px; font-size: 0.95rem; color: #334155;">
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Total Live Birds:</span>
                                <span style="background: #16a34a; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.total_live_birds.toLocaleString('en-IN')}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Running Weeks:</span>
                                <span style="background: #2563eb; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.running_weeks} Weeks</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Batch IDs:</span>
                                <span style="color: #475569; font-weight: 600;">${batchText}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">Hatch Date:</span>
                                <span style="background: #2563eb; color: #ffffff; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${formattedDate}</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span style="font-weight: 700; color: #1e293b;">No. of Chicks:</span>
                                <span style="background: #eab308; color: #000000; padding: 2px 8px; border-radius: 12px; font-weight: 800; font-size: 0.85rem;">${f.initial_chicks.toLocaleString('en-IN')}</span>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
            const statFlocks = document.getElementById('stat-total-flocks');
            if (statFlocks) statFlocks.textContent = flocks.length;
            const statLive = document.getElementById('stat-total-live-birds');
            if (statLive) statLive.textContent = totalLive.toLocaleString('en-IN');
        }

        window.openAddFlockModal = function() {
            document.getElementById('add-flock-name').value = '';
            document.getElementById('add-flock-hatch-date').value = '';
            document.getElementById('add-flock-chicks').value = '';
            document.getElementById('add-flock-batch-id').value = '';
            window.openModal('addFlockModal');
        };

        async function submitAddFlock(event) {
            event.preventDefault();
            const name = document.getElementById('add-flock-name').value;
            const hatchDate = document.getElementById('add-flock-hatch-date').value;
            const chicks = document.getElementById('add-flock-chicks').value;
            const batchId = document.getElementById('add-flock-batch-id').value;

            try {
                const res = await fetch(API_URL + 'flocks', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        shed_name: name,
                        hatch_date: hatchDate,
                        initial_chicks: parseInt(chicks),
                        batch_id: batchId || null
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    window.closeModal('addFlockModal');
                    fetchFlocks();
                } else {
                    alert('Error adding batch');
                }
            } catch (err) {
                console.error("Error adding flock:", err);
            }
        }

        window.openEditFlockModal = function(id) {
            const flock = flocksList.find(f => f.id == id || String(f.id) === String(id));
            if (!flock) {
                console.warn("Flock not found for ID:", id);
                return;
            }
            
            document.getElementById('edit-flock-id').value = flock.id;
            document.getElementById('edit-flock-hatch-date').value = flock.hatch_date;
            document.getElementById('edit-flock-chicks').value = flock.initial_chicks;
            document.getElementById('edit-flock-live-birds').value = flock.total_live_birds || 0;
            document.getElementById('edit-flock-batch-id').value = flock.batch_id && flock.batch_id !== 'None' ? flock.batch_id : '';
            
            document.getElementById('editFlockModalTitle').innerText = "Edit Flock: " + flock.shed_name;
            window.openModal('editFlockModal');
        };

        async function submitEditFlock(event) {
            event.preventDefault();
            const id = document.getElementById('edit-flock-id').value;
            const hatchDate = document.getElementById('edit-flock-hatch-date').value;
            const chicks = document.getElementById('edit-flock-chicks').value;
            const liveBirds = document.getElementById('edit-flock-live-birds').value;
            const batchId = document.getElementById('edit-flock-batch-id').value;
            
            try {
                const res = await fetch(API_URL + 'flocks/' + id, {
                    method: 'PUT',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        hatch_date: hatchDate,
                        initial_chicks: parseInt(chicks),
                        live_birds: parseInt(liveBirds),
                        batch_id: batchId || null
                    })
                });
                const data = await res.json();
                if (data.status === 'success') {
                    closeModal('editFlockModal');
                    fetchFlocks();
                } else {
                    alert('Error updating flock: ' + (data.detail || 'Failed'));
                }
            } catch (err) {
                console.error("Error updating flock:", err);
            }
        }

        window.onload = async () => {
            await fetchWahaGroups();
            await loadReportTypesDropdowns();
            await loadTaskTypesDropdowns();
            await fetchReminders();
            await fetchTasks();
            await fetchFlocks();
            renderMembersChecklist([]);
            
            // WAHA Session Monitoring Init
            await checkWahaStatus();
            await loadWahaEvents();
            await loadWahaSettings();
            
            // Periodically check status (every 60s) and events (every 2 min)
            setInterval(() => checkWahaStatus(), 60000);
            setInterval(() => loadWahaEvents(), 120000);
        };
    