from flask import Flask, request, jsonify, g
from flask_cors import CORS
import cx_Oracle
import logging
import platform
import os
from datetime import datetime  # <--- IMPORTANTE

# ==========================================
# 1. FIX WINDOWS (Instant Client)
# ==========================================
try:
    if platform.system() == "Windows":
        # Check path dyalk
        cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_0")
except Exception as e:
    print("Info: Oracle Client déjà initialisé ou erreur non bloquante:", e)
    pass

# ==========================================
# 2. IMPORTS DES CLASSES (DAOs)
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

try:
    from classes.grades_audit import grades_audit
except ImportError:
    grades_audit = None

# ==========================================
# 3. IMPORTS DES SERVICES
# ==========================================
from services.admin import AdminService
from services.student import StudentService
from services.teacher import TeacherService

# ==========================================
# 4. IMPORT CONNECTION
# ==========================================
from connection.db import db

app = Flask(__name__)
CORS(app) 

logging.basicConfig(level=logging.INFO)

# ==========================================
# 5. CONFIGURATION ORACLE
# ==========================================
ORACLE_CONFIG = {
    'ADMIN': {
        'user': 'yahya_admin', 
        'password': '123', 
        'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')
    },
    'TEACHER': {
        'user': 'user_teacher', 
        'password': 'TeacherPass123', 
        'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')
    },
    'STUDENT': {
        'user': 'user_student', 
        'password': 'StudentPass123', 
        'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')
    }
}

# ==========================================
# 6. FACTORY
# ==========================================
def get_service_for_role(role_name):
    config = ORACLE_CONFIG.get(role_name.upper())
    if not config: return None, None

    db_obj = db(config['user'], config['password'], config['dsn'])
    cnn = db_obj.get_connection()
    
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
        'grades_audit': grades_audit(cnn) if grades_audit else None
    }

    if role_name.upper() == 'ADMIN':
        service = AdminService(cnn, mgrs['student'], mgrs['instructor'], mgrs['course'], 
                               mgrs['section'], mgrs['registration'], mgrs['departement'], 
                               mgrs['salle'], mgrs['semester'], mgrs['course_result'], 
                               mgrs['prerequisite'], mgrs['grades_audit'])
    elif role_name.upper() == 'STUDENT':
        service = StudentService(cnn, mgrs['student'], mgrs['section'], mgrs['registration'], 
                                 mgrs['instructor'], mgrs['departement'], mgrs['salle'], 
                                 mgrs['course_result'], mgrs['app_user'])
    elif role_name.upper() == 'TEACHER':
        service = TeacherService(cnn, mgrs['instructor'], mgrs['section'], mgrs['student'], 
                                 mgrs['course'], mgrs['prerequisite'], mgrs['registration'], 
                                 mgrs['course_result'], mgrs['app_user'], mgrs['departement'], 
                                 mgrs['salle'], mgrs['semester'])
    else:
        return None, None

    return service, cnn

def format_response(data):
    if not data: return []
    return data

# ==========================================
# 7. LOGIN
# ==========================================
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    role = data.get('role') 
    code_apoge = data.get('code_apoge')
    password = data.get('password')

    if not all([role, password]): 
        return jsonify({"error": "Données incomplètes"}), 400

    try:
        service, cnn = get_service_for_role(role)
        if not service: return jsonify({"error": "Role invalide"}), 400

        user_mgr = app_user(cnn)
        user_data = user_mgr.select_app_user_by_code_apoge(code_apoge)
        cnn.close()

        if role == 'ADMIN':
            if user_data:
                if user_data[0][2] == password:
                     return jsonify({"message": "Success", "role": "ADMIN", "user": "admin"})
            elif password == "AdminPass123" or password == "123":
                 return jsonify({"message": "Success (Direct)", "role": "ADMIN", "user": "admin"})
            return jsonify({"error": "Mot de passe incorrect"}), 401

        if not user_data: return jsonify({"error": "Utilisateur introuvable"}), 404

        stored_password = user_data[0][2]
        stored_role = user_data[0][3]

        if stored_password != password: return jsonify({"error": "Mot de passe incorrect"}), 401
        if stored_role != role: return jsonify({"error": f"Ce compte n'est pas {role}"}), 403

        return jsonify({"message": "Login Success", "role": role, "code_apoge": code_apoge})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# ROUTES ADMIN
# ==========================================

# --- ETUDIANTS ---
@app.route('/api/admin/students', methods=['GET'])
def admin_get_students():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_students()))
    finally: cnn.close()

@app.route('/api/admin/student', methods=['POST'])
def admin_add_student():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_student(d['first_name'], d['last_name'], d['email'], d['level'], d['password']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- PROFESSEURS ---
@app.route('/api/admin/teachers', methods=['GET'])
def admin_get_teachers():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_instructors()))
    finally: cnn.close()

@app.route('/api/admin/teacher', methods=['POST'])
def admin_add_teacher():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_instructor(d['name'], d['email'], d['dept_id'], d['password']):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- COURS ---
@app.route('/api/admin/courses', methods=['GET'])
def admin_get_courses():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_courses()))
    finally: cnn.close()

@app.route('/api/admin/course', methods=['POST'])
def admin_add_course():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_course(d['title'], d['credits']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- DEPARTEMENTS ---
@app.route('/api/admin/departments', methods=['GET'])
def admin_get_departments():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_departments()))
    finally: cnn.close()

@app.route('/api/admin/departement', methods=['POST'])
def admin_add_dept():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_departement(d['name']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- SEMESTRES ---
@app.route('/api/admin/semesters', methods=['GET'])
def admin_get_semesters():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_semesters()))
    finally: cnn.close()

@app.route('/api/admin/semester', methods=['POST'])
def admin_add_semester():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_semester(d['name'], d['start_date'], d['end_date']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# --- SALLES ---
@app.route('/api/admin/salles', methods=['GET'])
def admin_get_salles():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_salles()))
    finally: cnn.close()

@app.route('/api/admin/salle', methods=['POST'])
def admin_add_salle():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.add_salle(d['code'], d['capacity'], d['building']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

# ==========================================
# 8. ROUTES SECTIONS (CORRIGÉES)
# ==========================================

@app.route('/api/admin/sections', methods=['GET'])
def admin_get_sections():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        # FIX: "show_sections" (Nom correct dans admin.py)
        data = svc.show_sections() 
        return jsonify(format_response(data))
    finally: cnn.close()

@app.route('/api/admin/section', methods=['POST'])
def admin_add_section():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        
        # FIX: CONVERSION DATE STRING -> DATETIME OBJECT
        # Hada howa l-7ll d ORA-01861
        start_dt = datetime.strptime(d['start'], '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(d['end'], '%Y-%m-%d %H:%M:%S')

        if svc.add_section(d['course_code'], d['semester_id'], d['instructor_id'], 
                           d['salle_id'], d['capacity'], d['day'], start_dt, end_dt):
            return jsonify({"message": "Section créée"})
        return jsonify({"error": "Erreur création"}), 400
    except Exception as e:
        print("Erreur Date/System:", e)
        return jsonify({"error": str(e)}), 400
    finally:
        cnn.close()

@app.route('/api/admin/section/<section_id>', methods=['DELETE'])
def admin_delete_section(section_id):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        # FIX: "drop_section" (Nom correct dans admin.py)
        if svc.drop_section(section_id):
            return jsonify({"message": "Section supprimée"})
        return jsonify({"error": "Erreur suppression"}), 400
    finally: cnn.close()

# ==========================================
# 9. ROUTES INSCRIPTIONS
# ==========================================

@app.route('/api/admin/section/<section_id>/registrations', methods=['GET'])
def admin_get_section_registrations(section_id):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        # FIX: admin.py ma fihch had l-fonction, donc kansta3mlo MANAGER direct
        data = svc.registration.get_registrations_by_section(section_id)
        return jsonify(format_response(data))
    finally: cnn.close()

@app.route('/api/admin/registration/status', methods=['PUT'])
def admin_update_reg_status():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        # FIX: admin.py ma fihch generic update, kansta3mlo MANAGER direct
        if svc.registration.update_registration_status(d['registration_id'], d['status']):
            return jsonify({"message": "Statut mis à jour"})
        return jsonify({"error": "Erreur mise à jour"}), 400
    finally: cnn.close()

# --- AUDIT ---
@app.route('/api/admin/audit', methods=['GET'])
def admin_audit():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_audit_logs()))
    finally: cnn.close()

# ==========================================
# ROUTES STUDENT / TEACHER
# ==========================================
# (Keep student/teacher routes same as before - omitted for brevity but include them if needed)
# ...

if __name__ == '__main__':
    app.run(debug=True, port=5000)