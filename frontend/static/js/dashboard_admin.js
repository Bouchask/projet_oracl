const API_URL = "http://localhost:5000/api";
let globalProfs = [], globalSalles = [], globalFilieres = [], globalSemesters = [];

// ==========================================
// 1. INITIALISATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadStudents(); // Charge la vue par défaut
    loadGlobalDropdowns(); 
});

// ==========================================
// 2. MOTEUR UI (SMART VIEW - LISTE OU FORMULAIRE)
// ==========================================

function buildTableHTML(sectionId, title, headers, rowsHtml) {
    if (!rowsHtml || rowsHtml.trim() === "") return null;

    const ths = headers.map(h => `<th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase tracking-wider">${h}</th>`).join('');
    
    return `
        <div class="card fade-in">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-gray-800">${title}</h3>
                <button class="btn-primary text-sm" onclick="toggleView('${sectionId}', 'form')">+ Nouveau</button>
            </div>
            <div class="table-container bg-white rounded-lg shadow overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50"><tr>${ths}</tr></thead>
                    <tbody class="bg-white divide-y divide-gray-200">${rowsHtml}</tbody>
                </table>
            </div>
        </div>
    `;
}

function toggleView(sectionId, mode) {
    const formDiv = document.getElementById(`${sectionId}-form`);
    const listDiv = document.getElementById(`${sectionId}-list`);
    
    if (!formDiv || !listDiv) return;

    if (mode === 'form') {
        formDiv.style.display = 'block';
        listDiv.style.display = 'none';
        
        if (!formDiv.querySelector('.btn-back')) {
            const backBtn = document.createElement('div');
            backBtn.className = "mb-4";
            backBtn.innerHTML = `<button class="text-gray-500 hover:text-gray-700 font-medium btn-back" onclick="toggleView('${sectionId}', 'list')">← Retour à la liste</button>`;
            formDiv.insertBefore(backBtn, formDiv.firstChild);
        }
    } else {
        formDiv.style.display = 'none';
        listDiv.style.display = 'block';
    }
}

function renderSmartView(sectionId, title, headers, rowsHtml) {
    const container = document.getElementById(`${sectionId}-list`);
    if (rowsHtml && rowsHtml.length > 0) {
        container.innerHTML = buildTableHTML(sectionId, title, headers, rowsHtml);
        toggleView(sectionId, 'list');
    } else {
        container.innerHTML = "";
        toggleView(sectionId, 'form');
    }
}

// ==========================================
// 3. NAVIGATION & API
// ==========================================
function showSection(id) {
    document.querySelectorAll('.section-view').forEach(s => { s.classList.remove('active'); s.style.display = 'none'; });
    const target = document.getElementById(id);
    if(target) { target.style.display = 'block'; setTimeout(() => target.classList.add('active'), 10); }

    document.querySelectorAll('.sidebar button').forEach(b => b.classList.remove('active'));
    const activeBtn = Array.from(document.querySelectorAll('.sidebar button')).find(b => b.getAttribute('onclick') && b.getAttribute('onclick').includes(id));
    if(activeBtn) activeBtn.classList.add('active');

    switch(id) {
        case 'students': loadStudents(); break;
        case 'teachers': loadTeachers(); break;
        case 'courses': loadCourses(); break;
        case 'filieres': loadFilieres(); break;
        case 'departments': loadDepartments(); break;
        case 'semesters': loadSemesters(); break;
        case 'salles': loadSalles(); break;
        case 'sections': loadSections(); loadSectionDropdowns(); break;
        case 'audit': loadAudit(); break;
    }
    loadStats();
}

async function fetchAPI(endpoint, method="GET", body=null) {
    try {
        const options = { method: method, headers: {'Content-Type': 'application/json'} };
        if (body) options.body = JSON.stringify(body);
        const res = await fetch(`${API_URL}${endpoint}`, options);
        return await res.json();
    } catch (err) { console.error(err); return {error: "Erreur serveur"}; }
}

function showNotify(msg, isError = false) {
    const notif = document.getElementById('notification');
    notif.textContent = msg;
    notif.className = `fixed top-6 right-6 z-50 px-6 py-4 rounded-xl shadow-lg text-white font-medium animate-bounce ${isError ? 'bg-red-500' : 'bg-green-500'}`;
    notif.style.display = 'block';
    setTimeout(() => { notif.style.display = 'none'; }, 3000);
}

// ==========================================
// 4. MODALE & UPDATE
// ==========================================
let currentUpdateType = "", currentUpdateId = "";

function openModal(title, bodyHtml, updateType, id) { 
    document.getElementById('modalTitle').innerText = title; 
    document.getElementById('modalBody').innerHTML = bodyHtml; 
    currentUpdateType = updateType; 
    currentUpdateId = id; 
    document.getElementById('updateModal').style.display = 'flex'; 
}
function closeModal() { document.getElementById('updateModal').style.display = 'none'; }

async function submitUpdate() {
    let body = {}; let url = ""; 
    const valInput = document.getElementById('new_val');
    const val = valInput ? valInput.value : null;

    // Suppression de la logique "section_update" car on ne modifie plus les sections par ici
    if (currentUpdateType === 'student_pass') { url = '/admin/student/password'; body = { code_apoge: currentUpdateId, new_password: val }; }
    else if (currentUpdateType === 'teacher_pass') { url = '/admin/teacher/password'; body = { code_apoge: currentUpdateId, new_password: val }; }
    else if (currentUpdateType === 'course_credits') { url = '/admin/course/credits'; body = { title: currentUpdateId, credits: val }; }
    else if (currentUpdateType === 'dept_name') { url = '/admin/departement/name'; body = { old_name: currentUpdateId, new_name: val }; }
    else if (currentUpdateType === 'sem_name') { url = '/admin/semester/name'; body = { old_name: currentUpdateId, new_name: val }; }
    else if (currentUpdateType === 'salle_cap') { url = '/admin/salle/capacity'; body = { code: currentUpdateId, capacity: val }; }

    const res = await fetchAPI(url, 'PUT', body);
    if(res && !res.error) { 
        showNotify("Mis à jour avec succès"); 
        closeModal(); 
        const activeId = document.querySelector('.section-view[style*="block"]')?.id || 'students';
        showSection(activeId); 
    } 
    else { showNotify("Erreur: " + (res.error || "Problème"), true); }
}

async function loadGlobalDropdowns() {
    const [fils, sems, depts] = await Promise.all([fetchAPI('/admin/filieres'), fetchAPI('/admin/semesters'), fetchAPI('/admin/departments')]);
    if(fils && !fils.error) globalFilieres = fils; if(sems && !sems.error) globalSemesters = sems;
    populateSelect('std_filiere', globalFilieres, 0, 1); populateSelect('course_filiere', globalFilieres, 0, 1);
    populateSelect('std_semestre', globalSemesters, 0, 1); populateSelect('course_semestre', globalSemesters, 0, 1);
    populateSelect('prof_dept', depts, 0, 1); populateSelect('fil_dept', depts, 0, 1);
}
function populateSelect(id, data, valIdx, textIdx) {
    const el = document.getElementById(id); if(!el) return; el.innerHTML = `<option value="" disabled selected>Choisir...</option>`;
    if(data && !data.error) data.forEach(item => el.innerHTML += `<option value="${item[valIdx]}">${item[textIdx]}</option>`);
}

// ==========================================
// 5. GESTION DES SECTIONS (CORRIGÉE & CLEAN)
// ==========================================

async function loadSectionDropdowns() {
    const [courses, profs, salles] = await Promise.all([fetchAPI('/admin/courses'), fetchAPI('/admin/teachers'), fetchAPI('/admin/salles')]);
    if(courses && !courses.error) populateSelect('sec_course', courses, 0, 1);
    if(profs && !profs.error) { globalProfs = profs; populateSelect('sec_prof', profs, 0, 2); }
    if(salles && !salles.error) { globalSalles = salles; populateSelect('sec_salle', salles, 0, 1); }
}

async function loadSections() {
    const data = await fetchAPI('/admin/sections');
    let rows = "";
    
    if (data && data.length > 0) {
        rows = data.map(s => {
            const start = new Date(s[7]).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
            const end = new Date(s[8]).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
            const percent = Math.round((s[9] / s[10]) * 100);
            let progressColor = percent >= 100 ? "bg-red-500" : percent >= 80 ? "bg-orange-500" : "bg-green-500";
            const safeTitle = s[1].replace(/'/g, "\\'"); 

            return `
            <tr class="hover:bg-gray-50 transition border-b border-gray-100 last:border-0">
                <td class="px-6 py-4 whitespace-nowrap"><div class="flex flex-col"><span class="text-sm font-bold text-gray-900">${s[1]}</span><span class="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md w-fit mt-1">${s[3]}</span></div></td>
                <td class="px-6 py-4 whitespace-nowrap align-middle"><span class="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-50 text-blue-700 border border-blue-100">${s[2]}</span></td>
                <td class="px-6 py-4 whitespace-nowrap align-middle"><div class="flex items-center"><div class="h-8 w-8 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xs font-bold mr-3 ring-2 ring-white">${s[4].charAt(0)}</div><div class="text-sm font-medium text-gray-700">${s[4]}</div></div></td>
                <td class="px-6 py-4 whitespace-nowrap align-middle"><div class="flex flex-col"><span class="text-sm text-gray-900 font-medium">${s[6]}</span><span class="text-xs text-gray-500">${start} - ${end}</span><span class="mt-1 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-50 text-purple-700 w-fit">🚪 ${s[5]}</span></div></td>
                <td class="px-6 py-4 whitespace-nowrap align-middle"><div class="w-32"><div class="flex justify-between text-xs mb-1"><span class="font-semibold text-gray-700">${s[9]}/${s[10]}</span><span class="text-gray-400 font-medium">${percent}%</span></div><div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden"><div class="${progressColor} h-2 rounded-full transition-all duration-500" style="width: ${percent > 100 ? 100 : percent}%"></div></div></div></td>
                
                <td class="px-6 py-4 whitespace-nowrap text-center align-middle">
                    <div class="flex justify-center items-center gap-2">
                        <button onclick="manageRegistrations(${s[0]}, '${safeTitle}')" class="btn-action bg-blue-50 text-blue-600 hover:bg-blue-100 rounded-lg p-2 transition-all" title="Gérer Inscriptions">👥</button>
                        <button onclick="blockSection('${s[0]}')" class="btn-action bg-gray-100 text-gray-600 hover:bg-gray-200 rounded-lg p-2 transition-all" title="Bloquer">🔒</button>
                        <button onclick="deleteItem('/admin/section/${s[0]}')" class="btn-action bg-red-50 text-red-600 hover:bg-red-100 rounded-lg p-2 transition-all" title="Supprimer">🗑️</button>
                    </div>
                </td>
            </tr>`;
        }).join('');
    }
    renderSmartView('sections', 'Liste des Sections', ['Module', 'Sem.', 'Professeur', 'Horaire & Salle', 'Capacité', 'Actions'], rows);
}

async function addSection() {
    const day = "2026-01-01"; 
    const start = `${day} ${document.getElementById('sec_start').value}:00`; 
    const end = `${day} ${document.getElementById('sec_end').value}:00`;
    const body = { course_code: document.getElementById('sec_course').value, semester_id: 1, instructor_id: document.getElementById('sec_prof').value, salle_id: document.getElementById('sec_salle').value, capacity: document.getElementById('sec_cap').value, day: document.getElementById('sec_day').value, start: start, end: end };
    const res = await fetchAPI('/admin/section', 'POST', body);
    if(res && !res.error) { showNotify("Créée !"); loadSections(); } else showNotify("Erreur: Conflit", true);
}

// --- FONCTION BLOCK SECTION CORRIGÉE (FIX 400 ERROR) ---
async function blockSection(id) {
    if(!confirm("Bloquer les inscriptions (Capacité = Inscrits) ?")) return;
    
    // IMPORTANT: Conversion explicite en entier pour éviter l'erreur 400
    const sectionId = parseInt(id); 
    
    const res = await fetchAPI('/admin/section/block', 'PUT', { section_id: sectionId });
    
    if(res && !res.error) { 
        showNotify("✓ Section bloquée"); 
        loadSections(); 
    } else {
        // Affiche l'erreur détaillée si disponible
        showNotify("✕ Erreur: " + (res.error || "Impossible de bloquer"), true);
    }
}

// ==========================================
// 6. GESTION DES INSCRIPTIONS
// ==========================================
async function manageRegistrations(secId, title) {
    const mgr = document.getElementById('registrationManager');
    mgr.style.display = 'block';
    
    const data = await fetchAPI(`/admin/section/${secId}/registrations`);
    let tableHtml = "";

    if(data && data.length > 0) {
        const rows = data.map(r => {
            let statusBadge = `<span class="badge badge-info">${r[4]}</span>`;
            if(r[4] === 'PENDING') statusBadge = `<span class="badge badge-warning">⏳ EN ATTENTE</span>`;
            if(r[4] === 'ACTIVE' || r[4] === 'VALIDE') statusBadge = `<span class="badge badge-success">✓ ACTIF</span>`;
            if(r[4] === 'CANCELLED') statusBadge = `<span class="badge badge-danger">✕ ANNULÉ</span>`;
            
            let actions = "";
            if (r[4] === 'ACTIVE' || r[4] === 'VALIDE') {
                actions = `<button class="text-red-600 hover:text-red-800 text-sm font-bold" onclick="updateStatus(${r[0]}, 'CANCELLED', ${secId}, '${title}')">Annuler</button>`;
            } else if (r[4] === 'PENDING') {
                actions = `<button class="text-green-600 hover:text-green-800 font-bold text-sm" onclick="updateStatus(${r[0]}, 'ACTIVE', ${secId}, '${title}')">Accepter</button>`;
            }

            return `
                <tr class="border-b border-gray-50">
                    <td class="px-6 py-4 font-medium text-gray-900">${r[1]} ${r[2]}</td>
                    <td class="px-6 py-4 text-gray-500">${r[3]}</td>
                    <td class="px-6 py-4 text-gray-500">${new Date(r[5]).toLocaleDateString()}</td>
                    <td class="px-6 py-4">${statusBadge}</td>
                    <td class="px-6 py-4">${actions}</td>
                </tr>`;
        }).join('');

        tableHtml = `
            <div class="card bg-blue-50 border border-blue-100 mt-6 animate-fade-in">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold text-blue-800">Inscriptions : ${title}</h3>
                    <button class="bg-white text-gray-600 hover:text-red-600 px-3 py-1 rounded shadow-sm" onclick="closeRegManager()">Fermer</button>
                </div>
                <div class="table-container bg-white rounded shadow-sm">
                    <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50"><tr>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Etudiant</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Code</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Date</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Statut</th>
                            <th class="px-6 py-3 text-left text-xs font-bold text-gray-500 uppercase">Action</th>
                        </tr></thead>
                        <tbody>${rows}</tbody>
                    </table>
                </div>
            </div>`;
    } else {
        tableHtml = `
            <div class="card bg-gray-50 border border-gray-200 mt-6 p-4 text-center">
                <p class="text-gray-500 mb-2">Aucune inscription pour cette section.</p>
                <button class="btn-secondary text-sm" onclick="closeRegManager()">Fermer</button>
            </div>`;
    }
    
    mgr.innerHTML = tableHtml;
    mgr.scrollIntoView({behavior: 'smooth'});
}
async function updateStatus(regId, status, secId, title) { const res = await fetchAPI('/admin/registration/status', 'PUT', { registration_id: regId, status: status }); if(res && !res.error) manageRegistrations(secId, title); }
function closeRegManager() { document.getElementById('registrationManager').style.display = 'none'; }

// ==========================================
// 7. AUTRES ENTITES
// ==========================================

// --- ETUDIANTS ---
// --- ETUDIANTS (Mise à jour avec Bouton Détails) ---
async function loadStudents() {
    const data = await fetchAPI('/admin/students');
    let rows = "";
    if (data && data.length > 0) {
        rows = data.map(s => `
            <tr class="hover:bg-gray-50 transition border-b border-gray-100 last:border-0">
                <td class="px-6 py-4 font-mono text-gray-500">${s[1]}</td>
                <td class="px-6 py-4 font-bold text-gray-800">${s[3].toUpperCase()} ${s[2]}</td>
                <td class="px-6 py-4 text-gray-600">${s[4]}</td>
                <td class="px-6 py-4"><span class="badge badge-primary">${s[5]}</span></td>
                <td class="px-6 py-4"><span class="badge badge-info">${s[6]}</span></td>
                <td class="px-6 py-4 text-center">
                    <div class="flex justify-center gap-2">
                        <button class="btn-action bg-blue-100 text-blue-600 rounded p-2 hover:bg-blue-200 transition" 
                                onclick="viewStudentDetails(${s[0]})" 
                                title="Voir Dossier & Notes">
                            👁️
                        </button>

                        <button class="btn-action bg-amber-100 text-amber-600 rounded p-2 hover:bg-amber-200 transition" 
                                onclick="openModal('Mot de passe', '<input type=\\'password\\' id=\\'new_val\\' class=\\'w-full border p-2 rounded\\'>', 'student_pass', '${s[1]}')" 
                                title="Changer MDP">
                            🔑
                        </button>
                        <button class="btn-action bg-red-100 text-red-600 rounded p-2 hover:bg-red-200 transition" 
                                onclick="deleteItem('/admin/student/${s[1]}')" 
                                title="Supprimer">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    renderSmartView('students', 'Liste des Étudiants', ['Code', 'Nom', 'Email', 'Filière', 'Semestre', 'Action'], rows);
}

// --- FONCTIONS DÉTAILS / TRANSCRIPT (A ajouter à la fin du fichier JS) ---

async function viewStudentDetails(studentId) {
    // 1. Ouvrir la modale avec un état de chargement
    const modal = document.getElementById('detailsModal');
    const tbody = document.getElementById('transcriptBody');
    
    modal.style.display = 'flex';
    document.getElementById('detail_name').textContent = "Chargement...";
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8"><div class="spinner border-4 border-blue-500 border-t-transparent rounded-full w-8 h-8 mx-auto animate-spin"></div></td></tr>';

    // 2. Appel API
    const res = await fetchAPI(`/admin/student/${studentId}/transcript`);

    if (res && res.info) {
        // Remplir les infos étudiant [0:id, 1:code, 2:prenom, 3:nom, 4:email, 5:fil, 6:sem]
        const s = res.info;
        document.getElementById('detail_name').textContent = `${s[3].toUpperCase()} ${s[2]}`;
        document.getElementById('detail_code').textContent = `Code: ${s[1]}`;
        document.getElementById('detail_email').textContent = s[4];
        document.getElementById('detail_filiere').textContent = `${s[5]} - ${s[6]}`;

        // Remplir le tableau des notes
        tbody.innerHTML = "";
        if (res.transcript && res.transcript.length > 0) {
            res.transcript.forEach(row => {
                // row: [0:cours, 1:semestre, 2:prof, 3:note, 4:statut]
                
                // Note
                let gradeDisplay = `<span class="text-gray-400">-</span>`;
                if (row[3] !== null) {
                    const grade = parseFloat(row[3]);
                    const colorClass = grade >= 10 ? 'text-green-600 font-bold' : 'text-red-600 font-bold';
                    gradeDisplay = `<span class="${colorClass}">${grade}/20</span>`;
                }

                // Statut (Badges)
                let statusBadge = `<span class="px-2 py-1 rounded text-xs font-bold bg-gray-100 text-gray-600">${row[4]}</span>`;
                if(row[4] === 'VALIDE') statusBadge = `<span class="px-2 py-1 rounded text-xs font-bold bg-green-100 text-green-700">VALIDÉ</span>`;
                if(row[4] === 'ACTIVE') statusBadge = `<span class="px-2 py-1 rounded text-xs font-bold bg-blue-100 text-blue-700">EN COURS</span>`;
                if(row[4] === 'RATTRAPAGE') statusBadge = `<span class="px-2 py-1 rounded text-xs font-bold bg-orange-100 text-orange-700">RATTRAPAGE</span>`;

                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50 border-b border-gray-100">
                        <td class="px-6 py-4 font-bold text-blue-600">${row[1]}</td>
                        <td class="px-6 py-4 font-medium text-gray-900">${row[0]}</td>
                        <td class="px-6 py-4 text-sm text-gray-600">👨‍🏫 ${row[2]}</td>
                        <td class="px-6 py-4">${gradeDisplay}</td>
                        <td class="px-6 py-4">${statusBadge}</td>
                    </tr>
                `;
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-gray-500 italic">Aucun cours trouvé pour cet étudiant.</td></tr>`;
        }
    } else {
        alert("Erreur lors du chargement des données.");
        closeDetailsModal();
    }
}

function closeDetailsModal() {
    document.getElementById('detailsModal').style.display = 'none';
}
async function addStudent() {
    const body = { first_name: document.getElementById('std_fname').value, last_name: document.getElementById('std_lname').value, email: document.getElementById('std_email').value, filiere_id: document.getElementById('std_filiere').value, semester_id: document.getElementById('std_semestre').value, password: document.getElementById('std_pass').value };
    const res = await fetchAPI('/admin/student', 'POST', body);
    if(res && !res.error) { showNotify("Ajouté !"); loadStudents(); } else showNotify("Erreur", true);
}

// --- PROFESSEURS ---
// --- PROFESSEURS ---
async function loadTeachers() {
    const data = await fetchAPI('/admin/teachers');
    let rows = "";
    if (data && data.length > 0) {
        rows = data.map(t => `
            <tr class="hover:bg-gray-50 transition border-b border-gray-100 last:border-0">
                <td class="px-6 py-4 font-mono">${t[1]}</td>
                <td class="px-6 py-4 font-bold">${t[2]}</td>
                <td class="px-6 py-4">${t[3]}</td>
                <td class="px-6 py-4 text-blue-600 font-medium">${t[4]}</td>
                <td class="px-6 py-4 text-center">
                    <div class="flex justify-center gap-2">
                        
<button class="btn-action bg-purple-100 text-purple-600 rounded p-2 hover:bg-purple-200 transition" 
        onclick="openChangeDeptModal(${t[0]})" title="Changer Département">
    🏢
</button>
                        <button class="btn-action bg-blue-100 text-blue-600 rounded p-2 hover:bg-blue-200 transition" 
                                onclick="viewTeacherDetails(${t[0]})" title="Voir Sections & Étudiants">
                            👁️
                        </button>

                        <button class="btn-action bg-amber-100 text-amber-600 rounded p-2 hover:bg-amber-200 transition" 
                                onclick="openModal('Mot de passe', '<input type=\\'password\\' id=\\'new_val\\' class=\\'w-full border p-2 rounded\\'>', 'teacher_pass', '${t[1]}')">
                            🔑
                        </button>
                        <button class="btn-action bg-red-100 text-red-600 rounded p-2 hover:bg-red-200 transition" 
                                onclick="deleteItem('/admin/teacher/${t[1]}')">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    renderSmartView('teachers', 'Liste des Professeurs', ['Code', 'Nom', 'Email', 'Département', 'Action'], rows);
}
async function addTeacher() {
    const body = { name: document.getElementById('prof_name').value, email: document.getElementById('prof_email').value, dept_id: document.getElementById('prof_dept').value, password: document.getElementById('prof_pass').value };
    const res = await fetchAPI('/admin/teacher', 'POST', body);
    if(res && !res.error) { showNotify("Ajouté !"); loadTeachers(); } else showNotify("Erreur", true);
}

// --- COURS ---
// --- COURS ---
async function loadCourses() {
    const data = await fetchAPI('/admin/courses');
    let rows = "";
    if (data && data.length > 0) {
        rows = data.map(c => `
            <tr class="hover:bg-gray-50 transition border-b border-gray-100 last:border-0">
                <td class="px-6 py-4 font-mono text-gray-400 text-xs">${c[0]}</td>
                <td class="px-6 py-4 font-bold text-gray-800">${c[1]}</td>
                <td class="px-6 py-4"><span class="badge badge-success">${c[2]} pts</span></td>
                <td class="px-6 py-4 font-medium text-blue-700">${c[3]}</td>
                <td class="px-6 py-4">${c[4]}</td>
                <td class="px-6 py-4 font-mono">${c[5]}h</td>
                <td class="px-6 py-4 text-center">
                    <div class="flex justify-center gap-2">
                        <button class="btn-action bg-blue-100 text-blue-600 rounded p-2 hover:bg-blue-200 transition" 
                                onclick="viewCourseDetails(${c[0]})" title="Voir Progression & Sections">
                            👁️
                        </button>

                        <button class="btn-action bg-amber-100 text-amber-600 rounded p-2 hover:bg-amber-200 transition" 
                                onclick="openModal('Crédits', '<input type=\\'number\\' id=\\'new_val\\' value=\\'${c[2]}\\' class=\\'w-full border p-2 rounded\\'>', 'course_credits', '${c[1]}')">
                            ✏️
                        </button>
                        <button class="btn-action bg-red-100 text-red-600 rounded p-2 hover:bg-red-200 transition" 
                                onclick="deleteItem('/admin/course/${c[1]}')">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    renderSmartView('courses', 'Liste des Cours', ['Code', 'Titre', 'Crédits', 'Filière', 'Semestre', 'Heures', 'Action'], rows);
}
async function addCourse() {
    const body = { title: document.getElementById('course_title').value, credits: document.getElementById('course_credits').value, total_hours: document.getElementById('course_hours').value, filiere_id: document.getElementById('course_filiere').value, semester_id: document.getElementById('course_semestre').value };
    const res = await fetchAPI('/admin/course', 'POST', body);
    if(res && !res.error) { showNotify("Ajouté !"); loadCourses(); } else showNotify("Erreur", true);
}

// --- FILIERES ---
// --- FILIERES ---
async function loadFilieres() {
    const data = await fetchAPI('/admin/filieres');
    let rows = "";
    if (data && data.length) {
        rows = data.map(f => `
            <tr class="hover:bg-gray-50 transition border-b border-gray-100 last:border-0">
                <td class="px-6 py-4 text-gray-500 font-mono text-xs">ID ${f[0]}</td>
                <td class="px-6 py-4 font-bold text-gray-800 text-lg">${f[1]}</td>
                <td class="px-6 py-4 text-blue-600 font-medium">${f[2]}</td>
                <td class="px-6 py-4 text-center">
                    <div class="flex justify-center gap-2">
                        <button class="btn-action bg-blue-100 text-blue-600 rounded p-2 hover:bg-blue-200 transition" 
                                onclick="viewFiliereDetails(${f[0]})" title="Voir Programme">
                            👁️
                        </button>
                        <button class="btn-action bg-red-100 text-red-600 p-2 rounded hover:bg-red-200 transition" 
                                onclick="deleteItem('/admin/filiere/${f[0]}')">
                            🗑️
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }
    renderSmartView('filieres', 'Liste des Filières', ['ID', 'Nom', 'Département', 'Action'], rows);
}
async function addFiliere() { const res = await fetchAPI('/admin/filiere', 'POST', { name: document.getElementById('fil_name').value, dept_id: document.getElementById('fil_dept').value }); if(res && !res.error) { showNotify("Ajouté"); loadFilieres(); } }

// --- DEPARTEMENTS ---
async function loadDepartments() {
    const data = await fetchAPI('/admin/departments');
    let rows = "";
    if(data && data.length) rows = data.map(d => `<tr class="hover:bg-gray-50"><td class="px-6 py-4">${d[0]}</td><td class="px-6 py-4 font-bold">${d[1]}</td><td class="px-6 py-4 text-center"><button class="btn-action bg-amber-100 text-amber-600 p-2 rounded mr-2" onclick="openModal('Renommer', '<input type=\\'text\\' id=\\'new_val\\' class=\\'w-full border p-2 rounded\\'>', 'dept_name', '${d[1]}')">✏️</button><button class="btn-action bg-red-100 text-red-600 p-2 rounded" onclick="deleteItem('/admin/departement/${d[1]}')">🗑️</button></td></tr>`).join('');
    renderSmartView('departments', 'Liste des Départements', ['ID', 'Nom', 'Action'], rows);
}
async function addDepartment() { const res = await fetchAPI('/admin/departement', 'POST', { name: document.getElementById('dept_name').value }); if(res && !res.error) { showNotify("Ajouté"); loadDepartments(); } }

// --- SEMESTRES ---
async function loadSemesters() {
    const data = await fetchAPI('/admin/semesters');
    let rows = "";
    if(data && data.length) rows = data.map(s => `<tr class="hover:bg-gray-50"><td class="px-6 py-4 font-bold">${s[1]}</td><td class="px-6 py-4">${new Date(s[2]).toLocaleDateString()} - ${new Date(s[3]).toLocaleDateString()}</td><td class="px-6 py-4 text-center"><button class="btn-action bg-amber-100 text-amber-600 p-2 rounded mr-2" onclick="openModal('Renommer', '<input type=\\'text\\' id=\\'new_val\\'>', 'sem_name', '${s[1]}')">✏️</button><button class="btn-action bg-red-100 text-red-600 p-2 rounded" onclick="deleteItem('/admin/semester/${s[0]}')">🗑️</button></td></tr>`).join('');
    renderSmartView('semesters', 'Liste des Semestres', ['Nom', 'Dates', 'Action'], rows);
}
async function addSemester() { const body = { name: document.getElementById('sem_name').value, start_date: document.getElementById('sem_start').value, end_date: document.getElementById('sem_end').value }; const res = await fetchAPI('/admin/semester', 'POST', body); if(res && !res.error) { showNotify("Ajouté"); loadSemesters(); } }

// --- SALLES ---
async function loadSalles() {
    const data = await fetchAPI('/admin/salles');
    let rows = "";
    if(data && data.length) rows = data.map(s => `<tr class="hover:bg-gray-50"><td class="px-6 py-4 font-bold">${s[1]}</td><td class="px-6 py-4"><span class="badge badge-success">${s[2]} places</span></td><td class="px-6 py-4">${s[3]}</td><td class="px-6 py-4 text-center"><button class="btn-action bg-amber-100 text-amber-600 p-2 rounded mr-2" onclick="openModal('Capacité', '<input type=\\'number\\' id=\\'new_val\\'>', 'salle_cap', '${s[1]}')">✏️</button><button class="btn-action bg-red-100 text-red-600 p-2 rounded" onclick="deleteItem('/admin/salle/${s[0]}')">🗑️</button></td></tr>`).join('');
    renderSmartView('salles', 'Liste des Salles', ['Code', 'Capacité', 'Bâtiment', 'Action'], rows);
}
async function addSalle() { const body = { code: document.getElementById('salle_code').value, capacity: document.getElementById('salle_cap').value, building: document.getElementById('salle_build').value }; const res = await fetchAPI('/admin/salle', 'POST', body); if(res && !res.error) { showNotify("Ajouté"); loadSalles(); } }

// --- AUDIT ---
async function loadAudit() { 
    const data = await fetchAPI('/admin/audit'); 
    let rows = "";
    if(data && data.length) rows = data.map(log => `<tr><td class="px-6 py-4">${log[0]}</td><td class="px-6 py-4 font-bold">${log[1]}</td><td class="px-6 py-4 text-gray-500">${log[2]}</td><td class="px-6 py-4 text-red-500">${log[3]}</td><td class="px-6 py-4 text-green-500">${log[4]}</td><td class="px-6 py-4">${new Date(log[5]).toLocaleString()}</td></tr>`).join('');
    const container = document.getElementById('audit-list');
    container.innerHTML = buildTableHTML('audit', 'Journal d\'Audit', ['ID', 'User', 'Cours', 'Avant', 'Après', 'Date'], rows);
}

// ==========================================
// 8. UTILS & LOGOUT (CORRIGÉ 5001)
// ==========================================
async function deleteItem(endpoint) { 
    if(!confirm("Confirmer la suppression ?")) return; 
    const res = await fetchAPI(endpoint, 'DELETE'); 
    if(res && !res.error) { 
        showNotify("Supprimé !"); 
        const activeId = document.querySelector('.section-view[style*="block"]')?.id || 'students';
        showSection(activeId); 
    } else { showNotify("Erreur", true); } 
}

function loadStats() {
    fetchAPI('/admin/stats').then(data => {
        if(data && !data.error) {
            document.getElementById('stat-students').innerText = data.students || 0;
            document.getElementById('stat-teachers').innerText = data.instructors || 0;
            document.getElementById('stat-courses').innerText = data.courses || 0;
            document.getElementById('stat-sections').innerText = data.sections || 0;
        }
    });
}

function logout() { 
    // Redirection correcte vers le port 5001
    window.location.href = "http://localhost:5001/"; 
}
// ==========================================
// 10. DÉTAILS PROFESSEUR
// ==========================================

async function viewTeacherDetails(teacherId) {
    const modal = document.getElementById('teacherDetailsModal');
    const tbody = document.getElementById('teacherSectionsBody');
    document.getElementById('studentListZone').classList.add('hidden'); // Cacher la sous-liste
    
    modal.style.display = 'flex';
    document.getElementById('tch_detail_name').textContent = "Chargement...";
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8"><div class="spinner"></div></td></tr>';

    const res = await fetchAPI(`/admin/teacher/${teacherId}/details`);

    if (res && res.info) {
        // [0:id, 1:code, 2:nom, 3:email, 4:dept]
        const t = res.info;
        document.getElementById('tch_detail_name').textContent = t[2];
        document.getElementById('tch_detail_email').textContent = t[3];
        document.getElementById('tch_detail_dept').textContent = t[4];

        tbody.innerHTML = "";
        if (res.sections && res.sections.length > 0) {
            res.sections.forEach(sec => {
                // sec: [0:id, 1:cours, 2:filiere, 3:semestre, 4:salle, 5:jour, 6:debut, 7:fin, 8:occupation]
                const sectionId = sec[0];
                const coursTitle = sec[1];
                
                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50 border-b border-gray-100">
                        <td class="px-4 py-3 font-bold text-gray-800">${sec[1]}</td>
                        <td class="px-4 py-3 text-sm">${sec[2]} <span class="text-xs bg-blue-100 text-blue-800 px-1 rounded">${sec[3]}</span></td>
                        <td class="px-4 py-3 text-sm">
                            <div class="font-medium">${sec[5]} ${sec[6]}-${sec[7]}</div>
                            <div class="text-xs text-gray-500">📍 ${sec[4]}</div>
                        </td>
                        <td class="px-4 py-3 text-sm text-center font-mono">${sec[8]}</td>
                        <td class="px-4 py-3 text-center">
                            <div class="flex justify-center gap-2">
                                <button onclick="showSectionStudents(${sectionId}, 'ACCEPTED', '${coursTitle}')" 
                                        class="px-2 py-1 bg-green-100 text-green-700 rounded text-xs hover:bg-green-200 transition flex items-center gap-1">
                                    ✅ Acceptés
                                </button>
                                <button onclick="showSectionStudents(${sectionId}, 'PENDING', '${coursTitle}')" 
                                        class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs hover:bg-yellow-200 transition flex items-center gap-1">
                                    ⏳ Attente
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-gray-500 italic">Aucune section assignée.</td></tr>`;
        }
    }
}

// Affiche la liste des étudiants (Acceptés ou En attente) pour une section donnée
async function showSectionStudents(sectionId, type, title) {
    const zone = document.getElementById('studentListZone');
    const tbody = document.getElementById('studentListBody');
    const header = document.getElementById('studentListTitle');
    
    zone.classList.remove('hidden');
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-2">Chargement...</td></tr>';
    
    if (type === 'ACCEPTED') {
        header.innerHTML = `✅ Étudiants inscrits - <span class="text-blue-600">${title}</span>`;
        header.className = "font-bold text-green-700 mb-2";
        zone.className = "mt-4 pt-4 border-t border-green-200 bg-green-50 p-4 rounded-lg animate-fade-in block";
    } else {
        header.innerHTML = `⏳ Demandes en attente - <span class="text-blue-600">${title}</span>`;
        header.className = "font-bold text-yellow-700 mb-2";
        zone.className = "mt-4 pt-4 border-t border-yellow-200 bg-yellow-50 p-4 rounded-lg animate-fade-in block";
    }

    // On réutilise l'API existante des inscriptions
    const regs = await fetchAPI(`/admin/section/${sectionId}/registrations`);
    
    tbody.innerHTML = "";
    if (regs && regs.length > 0) {
        // Filtrage côté client selon le bouton cliqué
        const filtered = regs.filter(r => {
            if (type === 'ACCEPTED') return r[4] === 'ACTIVE' || r[4] === 'VALIDE';
            if (type === 'PENDING') return r[4] === 'PENDING';
            return false;
        });

        if (filtered.length > 0) {
            filtered.forEach(r => {
                // r: [0:id, 1:prenom, 2:nom, 3:code, 4:status, 5:date]
                tbody.innerHTML += `
                    <tr class="border-b border-gray-200/50">
                        <td class="py-2 font-mono text-xs text-gray-500">${r[3]}</td>
                        <td class="py-2 font-bold text-gray-700">${r[1]} ${r[2]}</td>
                        <td class="py-2 text-xs text-gray-500">...</td> <td class="py-2 text-xs">${new Date(r[5]).toLocaleDateString()}</td>
                    </tr>
                `;
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-gray-500 italic">Aucun étudiant dans cette catégorie.</td></tr>`;
        }
    } else {
        tbody.innerHTML = `<tr><td colspan="4" class="text-center py-4 text-gray-500 italic">Aucune donnée.</td></tr>`;
    }
}

// Filtre JS pour la table des sections
function filterTeacherTable() {
    const input = document.getElementById('tch_search');
    const filter = input.value.toLowerCase();
    const table = document.getElementById('teacherSectionsBody');
    const tr = table.getElementsByTagName('tr');

    for (let i = 0; i < tr.length; i++) {
        const text = tr[i].textContent.toLowerCase();
        tr[i].style.display = text.indexOf(filter) > -1 ? "" : "none";
    }
}

function closeTeacherModal() {
    document.getElementById('teacherDetailsModal').style.display = 'none';
}
// ==========================================
// 11. DÉTAILS COURS (Suivi Heures)
// ==========================================

async function viewCourseDetails(courseCode) {
    const modal = document.getElementById('courseDetailsModal');
    const tbody = document.getElementById('courseSectionsBody');
    
    modal.style.display = 'flex';
    document.getElementById('crs_detail_title').textContent = "Chargement...";
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-8"><div class="spinner"></div></td></tr>';

    const res = await fetchAPI(`/admin/course/${courseCode}/details`);

    if (res && res.info) {
        // info: [0:code, 1:titre, 2:credits, 3:filiere, 4:semestre, 5:total_hours]
        const c = res.info;
        const stats = res.stats;

        // 1. Remplir Header
        document.getElementById('crs_detail_title').textContent = c[1];
        document.getElementById('crs_detail_fil').textContent = c[3];
        document.getElementById('crs_detail_sem').textContent = c[4];
        document.getElementById('crs_detail_credits').textContent = c[2];

        // 2. Barre de Progression Heures
        const percent = Math.min(100, Math.round((stats.total_planned / stats.total_budget) * 100));
        const bar = document.getElementById('crs_hours_bar');
        
        document.getElementById('crs_hours_text').textContent = `${stats.total_planned}h / ${stats.total_budget}h (${percent}%)`;
        bar.style.width = `${percent}%`;
        
        // Couleur dynamique
        if(percent < 50) bar.className = "bg-green-500 h-4 rounded-full transition-all duration-1000";
        else if(percent < 90) bar.className = "bg-orange-500 h-4 rounded-full transition-all duration-1000";
        else bar.className = "bg-red-500 h-4 rounded-full transition-all duration-1000";

        // 3. Liste des Sections
        tbody.innerHTML = "";
        if (res.sections && res.sections.length > 0) {
            res.sections.forEach(sec => {
                // sec: [0:id, 1:prof, 2:code_salle, 3:batiment, 4:jour, 5:debut, 6:fin, 7:duree, 8:curr, 9:max]
                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50 border-b border-gray-100 text-sm">
                        <td class="px-4 py-3 font-medium text-gray-800">👨‍🏫 ${sec[1]}</td>
                        <td class="px-4 py-3">${sec[4]} ${sec[5]}-${sec[6]}</td>
                        <td class="px-4 py-3"><span class="bg-gray-100 px-2 py-1 rounded text-xs font-mono">${sec[2]} (${sec[3]})</span></td>
                        <td class="px-4 py-3 font-bold text-blue-600">${parseFloat(sec[7]).toFixed(1)}h</td>
                        <td class="px-4 py-3 text-center text-xs">
                            ${sec[8]}/${sec[9]}
                        </td>
                    </tr>
                `;
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="5" class="text-center py-8 text-gray-500 italic">Aucune section planifiée.</td></tr>`;
        }
    }
}

function closeCourseModal() {
    document.getElementById('courseDetailsModal').style.display = 'none';
}
// ==========================================
// 12. DÉTAILS FILIÈRE (Programme)
// ==========================================
let currentFiliereId = null; // Pour stocker l'ID courant lors du changement de semestre

async function viewFiliereDetails(filId) {
    currentFiliereId = filId;
    const modal = document.getElementById('filiereDetailsModal');
    const select = document.getElementById('fil_det_sem_select');
    
    // 1. Remplir le select Semestre avec les données globales
    select.innerHTML = "";
    if(globalSemesters && globalSemesters.length > 0) {
        globalSemesters.forEach(s => {
            // s: [0:id, 1:nom, 2:debut, 3:fin]
            select.innerHTML += `<option value="${s[0]}">${s[1]}</option>`;
        });
        // Sélectionner le premier semestre par défaut (ex: S1)
        select.selectedIndex = 0;
    }

    modal.style.display = 'flex';
    document.getElementById('fil_detail_name').textContent = "Chargement...";
    
    // 2. Charger les données pour le semestre sélectionné
    refreshFiliereCourses();
}

async function refreshFiliereCourses() {
    if(!currentFiliereId) return;
    
    const semId = document.getElementById('fil_det_sem_select').value;
    const tbody = document.getElementById('filiereCoursesBody');
    
    tbody.innerHTML = '<tr><td colspan="4" class="text-center py-8"><div class="spinner"></div></td></tr>';

    // Appel API avec paramètre GET
    const res = await fetchAPI(`/admin/filiere/${currentFiliereId}/program?semester_id=${semId}`);

    if(res && res.info) {
        const f = res.info;
        document.getElementById('fil_detail_name').textContent = f[1];
        document.getElementById('fil_detail_dept').textContent = f[2];

        tbody.innerHTML = "";
        if(res.courses && res.courses.length > 0) {
            res.courses.forEach(c => {
                // c: [0:code, 1:titre, 2:credits, 3:hours, 4:active_sections]
                
                let sectionBadge = c[4] > 0 
                    ? `<span class="bg-green-100 text-green-700 px-2 py-1 rounded text-xs font-bold">${c[4]} Classes</span>`
                    : `<span class="bg-gray-100 text-gray-500 px-2 py-1 rounded text-xs">Aucune</span>`;

                tbody.innerHTML += `
                    <tr class="hover:bg-gray-50 border-b border-gray-100">
                        <td class="px-6 py-4 font-bold text-gray-800">${c[1]}</td>
                        <td class="px-6 py-4 font-mono text-blue-600">${c[2]} pts</td>
                        <td class="px-6 py-4 font-mono">${c[3]}h</td>
                        <td class="px-6 py-4 text-center">${sectionBadge}</td>
                    </tr>
                `;
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="4" class="text-center py-8 text-gray-500 italic">Aucun cours programmé pour ce semestre.</td></tr>`;
        }
    }
}

function closeFiliereModal() {
    document.getElementById('filiereDetailsModal').style.display = 'none';
}
// ==========================================
// 13. CHANGER DÉPARTEMENT (SIMPLE)
// ==========================================
let currentProfIdForDept = null;

async function openChangeDeptModal(profId) {
    currentProfIdForDept = profId;
    const modal = document.getElementById('changeDeptModal');
    
    // UI Reset
    document.getElementById('chg_dept_prof_name').textContent = "Chargement...";
    document.getElementById('chg_dept_current').textContent = "...";
    modal.style.display = 'flex';

    // 1. Récupérer l'info actuelle du prof (Via la nouvelle route)
    const profInfo = await fetchAPI(`/admin/teacher/${profId}/department`);
    
    // 2. Récupérer la liste de tous les départements (pour le select)
    const allDepts = await fetchAPI('/admin/departments');

    if (profInfo && !profInfo.error) {
        document.getElementById('chg_dept_prof_name').textContent = profInfo.name;
        document.getElementById('chg_dept_current').textContent = profInfo.dept_name;
        
        // Remplir le Select (en excluant le dept actuel pour éviter de le choisir 2 fois)
        const select = document.getElementById('chg_dept_select');
        select.innerHTML = '<option value="" disabled selected>Choisir un nouveau...</option>';
        
        if (allDepts && allDepts.length > 0) {
            allDepts.forEach(d => {
                // d: [0: id, 1: nom]
                // On affiche tous les départements sauf celui actuel
                if (d[0] !== profInfo.dept_id) {
                    select.innerHTML += `<option value="${d[0]}">${d[1]}</option>`;
                }
            });
        }
    }
}

async function submitDeptChange() {
    const newDeptId = document.getElementById('chg_dept_select').value;
    if (!newDeptId) {
        alert("Veuillez sélectionner un département.");
        return;
    }

    if(!confirm("Êtes-vous sûr de vouloir transférer ce professeur ?")) return;

    const res = await fetchAPI('/admin/teacher/department/update', 'PUT', {
        instructor_id: currentProfIdForDept,
        new_dept_id: newDeptId
    });

    if (res && !res.error) {
        showNotify("Département modifié avec succès !");
        document.getElementById('changeDeptModal').style.display = 'none';
        loadTeachers(); // Rafraîchir la liste
    } else {
        showNotify("Erreur lors du transfert.", true);
    }
}