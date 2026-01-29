from flask import Flask, request, jsonify
from flask_cors import CORS
import cx_Oracle
import logging
import platform
from datetime import datetime

# ==========================================
# 1. INITIALISATION & CONFIG
# ==========================================
try:
    if platform.system() == "Windows":
        # Adapte le chemin si nécessaire
        cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_0")
except: pass

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

ORACLE_CONFIG = {
    'ADMIN': {'user': 'yahya_admin', 'password': '123', 'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')},
    'TEACHER': {'user': 'user_teacher', 'password': 'TeacherPass123', 'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')},
    'STUDENT': {'user': 'user_student', 'password': 'StudentPass123', 'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')}
}

# ==========================================
# 2. IMPORTS DES CLASSES (DAO)
# ==========================================
from classes.student import student
from classes.instructor import instructor
from classes.course import course
from classes.section import section
from classes.registration import registration
from classes.departement import departement
from classes.salle import salle
from classes.semester import semester
from classes.course_result import course_result
from classes.prerequisite import prerequisite
from classes.app_user import app_user
from classes.filiere import filiere # <--- IMPORTANT
try: from classes.grades_audit import grades_audit
except: grades_audit = None

from services.admin import AdminService
from services.student import StudentService
from services.teacher import TeacherService
from connection.db import db

# ==========================================
# 3. FACTORY SERVICE
# ==========================================
def get_service_for_role(role_name):
    # Sélection de la config user selon le rôle
    config = ORACLE_CONFIG.get(role_name.upper())
    if not config: return None, None
    
    try:
        db_obj = db(config['user'], config['password'], config['dsn'])
        cnn = db_obj.get_connection()
    except Exception as e:
        print(f"DB Connection Error: {e}")
        return None, None
    
    # Instanciation de TOUS les managers
    mgrs = {
        'student': student(cnn), 
        'instructor': instructor(cnn), 
        'course': course(cnn),
        'section': section(cnn), 
        'registration': registration(cnn), 
        'departement': departement(cnn),
        'salle': salle(cnn), 
        'semester': semester(cnn), 
        'course_result': course_result(cnn),
        'prerequisite': prerequisite(cnn), 
        'app_user': app_user(cnn),
        'filiere': filiere(cnn), # <--- Ajouté
        'grades_audit': grades_audit(cnn) if grades_audit else None
    }

    # Injection dans les Services
    if role_name.upper() == 'ADMIN':
        service = AdminService(
            cnn, mgrs['student'], mgrs['instructor'], mgrs['course'], mgrs['section'], 
            mgrs['registration'], mgrs['departement'], mgrs['salle'], mgrs['semester'], 
            mgrs['course_result'], mgrs['prerequisite'], mgrs['grades_audit'], 
            mgrs['filiere'] # <--- Passé au service
        )
    elif role_name.upper() == 'STUDENT':
        service = StudentService(cnn, mgrs['student'], mgrs['registration'], mgrs['course_result'])
    elif role_name.upper() == 'TEACHER':
        service = TeacherService(cnn, mgrs['instructor'], mgrs['course_result'], mgrs['registration'])
    else: 
        return None, None
        
    return service, cnn

def format_response(data): return data if data else []

# ==========================================
# 4. ROUTES API
# ==========================================

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    # Pour le login, on utilise une connexion générique ou admin pour vérifier
    # Ici on simplifie: si ADMIN on check '123'
    if d.get('role') == 'ADMIN' and d.get('password') in ['123', 'AdminPass123']:
         return jsonify({"message": "OK", "role": "ADMIN"})
         
    # Pour les autres, on tente de se connecter avec leurs credentials Oracle via le service
    try:
        svc, cnn = get_service_for_role(d.get('role'))
        if not svc: return jsonify({"error": "Login failed"}), 401
        
        # Si la connexion DB réussit, on vérifie si l'utilisateur existe dans app_user
        # Note: Dans une vraie app, on vérifierait le hash. Ici la connexion DB fait foi.
        u = app_user(cnn).select_app_user_by_code_apoge(d.get('code_apoge'))
        cnn.close()
        
        if u: return jsonify({"message": "OK", "role": d.get('role'), "code_apoge": d.get('code_apoge')})
        return jsonify({"error": "User not found"}), 401
    except:
        return jsonify({"error": "Login failed"}), 401

# --- ADMIN DASHBOARD ---
@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(svc.get_dashboard_stats())
    finally: cnn.close()

# --- FILIERES ---
@app.route('/api/admin/filieres', methods=['GET'])
def get_fils():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_filieres()))
    finally: cnn.close()

@app.route('/api/admin/filiere', methods=['POST'])
def add_fil():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_filiere(request.json['name'], request.json['dept_id']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- ETUDIANTS ---
@app.route('/api/admin/students', methods=['GET'])
def get_stds():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_students()))
    finally: cnn.close()

@app.route('/api/admin/student', methods=['POST'])
def add_std():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        # Gestion des valeurs par défaut si le front n'envoie pas tout
        fil_id = d.get('filiere_id', 1)
        sem_id = d.get('semester_id', 1)
        if svc.add_student(d['first_name'], d['last_name'], d['email'], fil_id, sem_id, d['password']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/student/<code_apoge>', methods=['DELETE'])
def del_std(code_apoge):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_student(code_apoge): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/student/password', methods=['PUT'])
def upd_std_pass():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.modify_student_password(request.json['code_apoge'], request.json['new_password']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- PROFESSEURS ---
@app.route('/api/admin/teachers', methods=['GET'])
def get_tch():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_instructors()))
    finally: cnn.close()

@app.route('/api/admin/teacher', methods=['POST'])
def add_tch():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_instructor(d['name'], d['email'], d['dept_id'], d['password']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/teacher/<code_apoge>', methods=['DELETE'])
def del_tch(code_apoge):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_instructor(code_apoge): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/teacher/password', methods=['PUT'])
def upd_tch_pass():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.modify_teacher_password(request.json['code_apoge'], request.json['new_password']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- COURS ---
@app.route('/api/admin/courses', methods=['GET'])
def get_crs():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_courses()))
    finally: cnn.close()

@app.route('/api/admin/course', methods=['POST'])
def add_crs():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        # Valeurs par défaut
        hours = d.get('total_hours', 40)
        fil_id = d.get('filiere_id', 1)
        sem_id = d.get('semester_id', 1)
        
        if svc.add_course(d['title'], d['credits'], fil_id, sem_id, hours):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/course/<path:title>', methods=['DELETE'])
def del_crs(title):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_course(title): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/course/credits', methods=['PUT'])
def upd_crs_cred():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.modify_course_credits(request.json['title'], request.json['credits']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- DEPARTEMENTS ---
@app.route('/api/admin/departments', methods=['GET'])
def get_dpt():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_departments()))
    finally: cnn.close()

@app.route('/api/admin/departement', methods=['POST'])
def add_dpt():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_departement(request.json['name']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/departement/<name>', methods=['DELETE'])
def del_dpt(name):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_departement(name): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/departement/name', methods=['PUT'])
def upd_dpt_name():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.modify_departement_name(request.json['old_name'], request.json['new_name']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- SEMESTRES ---
@app.route('/api/admin/semesters', methods=['GET'])
def get_sem():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_semesters()))
    finally: cnn.close()

@app.route('/api/admin/semester', methods=['POST'])
def add_sem():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_semester(d['name'], d['start_date'], d['end_date']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/semester/<name>', methods=['DELETE'])
def del_sem(name):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_semester(name): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/semester/name', methods=['PUT'])
def upd_sem_name():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.modify_semester_name(request.json['old_name'], request.json['new_name']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- SALLES ---
@app.route('/api/admin/salles', methods=['GET'])
def get_sal():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_salles()))
    finally: cnn.close()

@app.route('/api/admin/salle', methods=['POST'])
def add_sal():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_salle(d['code'], d['capacity'], d['building']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/salle/<code>', methods=['DELETE'])
def del_sal(code):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_salle(code): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/salle/capacity', methods=['PUT'])
def upd_sal_cap():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.modify_salle_capacity(request.json['code'], request.json['capacity']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- SECTIONS ---
@app.route('/api/admin/sections', methods=['GET'])
def get_secs():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_sections()))
    finally: cnn.close()

@app.route('/api/admin/section', methods=['POST'])
def add_sec():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        s_dt = datetime.strptime(d['start'], '%Y-%m-%d %H:%M:%S')
        e_dt = datetime.strptime(d['end'], '%Y-%m-%d %H:%M:%S')
        
        if svc.add_section(d['course_code'], d['instructor_id'], d['salle_id'], d['capacity'], d['day'], s_dt, e_dt):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: cnn.close()

@app.route('/api/admin/section/<sid>', methods=['DELETE'])
def del_sec(sid):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_section(sid): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/section/update', methods=['PUT'])
def upd_sec_det():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        sec_id = d.get('section_id')
        if 'instructor_id' in d: svc.modify_section_prof(sec_id, d['instructor_id'])
        if 'salle_id' in d: svc.modify_section_salle(sec_id, d['salle_id'])
        return jsonify({"message": "OK"})
    finally: cnn.close()

@app.route('/api/admin/section/block', methods=['PUT'])
def block_sec():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.block_section(request.json['section_id']): return jsonify({"message": "Section Bloquée"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- INSCRIPTIONS & AUDIT ---
@app.route('/api/admin/section/<section_id>/registrations', methods=['GET'])
def get_regs(section_id):
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_section_registrations(section_id)))
    finally: cnn.close()

@app.route('/api/admin/registration/status', methods=['PUT'])
def upd_reg_status():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        status = d['status']
        rid = d['registration_id']
        ok = False
        if status == 'ACTIVE' or status == 'VALIDE': ok = svc.validate_reg(rid)
        elif status == 'CANCELLED': ok = svc.cancel_reg(rid)
        elif status == 'DROPPED': ok = svc.drop_reg(rid)
        
        if ok: return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur Workflow"}), 400
    finally: cnn.close()

@app.route('/api/admin/audit', methods=['GET'])
def get_aud():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_audit_logs()))
    finally: cnn.close()
@app.route('/api/admin/student/<id>/transcript', methods=['GET'])
def get_std_transcript(id):
    svc, cnn = get_service_for_role('ADMIN')
    if not svc: return jsonify({"error": "Unauthorized"}), 401
    
    try:
        # Appel du service qui combine infos + historique
        data = svc.get_student_details_full(id)
        return jsonify(data)
    except Exception as e:
        logging.error(f"API Error Transcript: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cnn.close()
@app.route('/api/admin/teacher/<id>/details', methods=['GET'])
def get_tch_details(id):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        data = svc.get_teacher_details_full(id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cnn.close()
@app.route('/api/admin/course/<code_apoge>/details', methods=['GET'])
def get_crs_details(code_apoge):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        data = svc.get_course_details_full(code_apoge)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cnn.close()
@app.route('/api/admin/filiere/<id>/program', methods=['GET'])
def get_fil_prog(id):
    svc, cnn = get_service_for_role('ADMIN')
    sem_id = request.args.get('semester_id') # On récupère le paramètre ?semester_id=...
    try:
        data = svc.get_filiere_program(id, sem_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cnn.close()
# --- GESTION DEPARTEMENT PROF (SIMPLE) ---

@app.route('/api/admin/teacher/<id>/department', methods=['GET'])
def get_tch_dept_info(id):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        # data = [id, nom, dept_id, dept_name]
        data = svc.instructor.get_current_dept(id)
        if data:
            return jsonify({
                "instructor_id": data[0],
                "name": data[1],
                "dept_id": data[2],
                "dept_name": data[3]
            })
        return jsonify({"error": "Not found"}), 404
    finally: cnn.close()

# Fichier app.py - Route Update Dept
@app.route('/api/admin/teacher/department/update', methods=['PUT'])
def update_tch_dept():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        # Daba kan-3yyto l Service (Admin) machi Manager direct
        if svc.modify_teacher_department(d['instructor_id'], d['new_dept_id']):
            return jsonify({"message": "Département modifié avec succès"})
        return jsonify({"error": "Erreur Update"}), 400
    finally: cnn.close()
if __name__ == '__main__':
    print("🚀 Serveur démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)