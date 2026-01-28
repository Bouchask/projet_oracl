from flask import Flask, request, jsonify
from flask_cors import CORS
import cx_Oracle
import logging
import platform
from datetime import datetime

# INIT
try:
    if platform.system() == "Windows":
        cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_23_0")
except: pass

# IMPORTS
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
try: from classes.grades_audit import grades_audit
except: grades_audit = None

from services.admin import AdminService
from services.student import StudentService
from services.teacher import TeacherService
from connection.db import db

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

ORACLE_CONFIG = {
    'ADMIN': {'user': 'yahya_admin', 'password': '123', 'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')},
    'TEACHER': {'user': 'user_teacher', 'password': 'TeacherPass123', 'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')},
    'STUDENT': {'user': 'user_student', 'password': 'StudentPass123', 'dsn': cx_Oracle.makedsn('localhost', 1521, service_name='ORCLCDB')}
}

def get_service_for_role(role_name):
    config = ORACLE_CONFIG.get(role_name.upper())
    if not config: return None, None
    try:
        db_obj = db(config['user'], config['password'], config['dsn'])
        cnn = db_obj.get_connection()
    except Exception as e:
        print(f"DB Error: {e}")
        return None, None
    
    mgrs = {
        'student': student(cnn), 'instructor': instructor(cnn), 'course': course(cnn),
        'section': section(cnn), 'registration': registration(cnn), 'departement': departement(cnn),
        'salle': salle(cnn), 'semester': semester(cnn), 'course_result': course_result(cnn),
        'prerequisite': prerequisite(cnn), 'app_user': app_user(cnn),
        'grades_audit': grades_audit(cnn) if grades_audit else None
    }

    if role_name.upper() == 'ADMIN':
        service = AdminService(cnn, mgrs['student'], mgrs['instructor'], mgrs['course'], mgrs['section'], mgrs['registration'], mgrs['departement'], mgrs['salle'], mgrs['semester'], mgrs['course_result'], mgrs['prerequisite'], mgrs['grades_audit'])
    elif role_name.upper() == 'STUDENT':
        service = StudentService(cnn, mgrs['student'], mgrs['section'], mgrs['registration'], mgrs['instructor'], mgrs['departement'], mgrs['salle'], mgrs['course_result'], mgrs['app_user'])
    elif role_name.upper() == 'TEACHER':
        service = TeacherService(cnn, mgrs['instructor'], mgrs['section'], mgrs['student'], mgrs['course'], mgrs['prerequisite'], mgrs['registration'], mgrs['course_result'], mgrs['app_user'], mgrs['departement'], mgrs['salle'], mgrs['semester'])
    else: return None, None
    return service, cnn

def format_response(data): return data if data else []

@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    try:
        svc, cnn = get_service_for_role(d.get('role'))
        if not svc: return jsonify({"error": "Connexion DB échouée"}), 500
        u = app_user(cnn).select_app_user_by_code_apoge(d.get('code_apoge'))
        cnn.close()
        
        if d.get('role') == 'ADMIN' and (d.get('password') in ['123', 'AdminPass123']):
             return jsonify({"message": "OK", "role": "ADMIN"})
        if u and u[0][2] == d.get('password') and u[0][3] == d.get('role'):
            return jsonify({"message": "OK", "role": d.get('role'), "code_apoge": d.get('code_apoge')})
        return jsonify({"error": "Login failed"}), 401
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- ADMIN STATS ---
@app.route('/api/admin/stats', methods=['GET'])
def admin_stats():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(svc.get_dashboard_stats())
    finally: cnn.close()

# --- ROUTES GET & POST ---
@app.route('/api/admin/students', methods=['GET'])
def get_stds():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_students()))
    finally: cnn.close()
@app.route('/api/admin/student', methods=['POST'])
def add_std():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_student(request.json['first_name'], request.json['last_name'], request.json['email'], request.json['level'], request.json['password']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/teachers', methods=['GET'])
def get_tch():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_instructors()))
    finally: cnn.close()
@app.route('/api/admin/teacher', methods=['POST'])
def add_tch():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_instructor(request.json['name'], request.json['email'], request.json['dept_id'], request.json['password']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/courses', methods=['GET'])
def get_crs():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_courses()))
    finally: cnn.close()
@app.route('/api/admin/course', methods=['POST'])
def add_crs():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_course(request.json['title'], request.json['credits']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

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

@app.route('/api/admin/semesters', methods=['GET'])
def get_sem():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_semesters()))
    finally: cnn.close()
@app.route('/api/admin/semester', methods=['POST'])
def add_sem():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_semester(request.json['name'], request.json['start_date'], request.json['end_date']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/salles', methods=['GET'])
def get_sal():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_all_salles()))
    finally: cnn.close()
@app.route('/api/admin/salle', methods=['POST'])
def add_sal():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.add_salle(request.json['code'], request.json['capacity'], request.json['building']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

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
        if svc.add_section(d['course_code'], d['semester_id'], d['instructor_id'], d['salle_id'], d['capacity'], d['day'], s_dt, e_dt):
            return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: cnn.close()

@app.route('/api/admin/section/<section_id>/registrations', methods=['GET'])
def get_regs(section_id):
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_section_registrations(section_id)))
    finally: cnn.close()
@app.route('/api/admin/registration/status', methods=['PUT'])
def upd_reg():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.change_registration_status(request.json['registration_id'], request.json['status']): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/audit', methods=['GET'])
def get_aud():
    svc, cnn = get_service_for_role('ADMIN')
    try: return jsonify(format_response(svc.show_audit_logs()))
    finally: cnn.close()

# --- ROUTES DELETE ---
@app.route('/api/admin/student/<code_apoge>', methods=['DELETE'])
def del_std(code_apoge):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_student(code_apoge): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/teacher/<code_apoge>', methods=['DELETE'])
def del_tch(code_apoge):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_instructor(code_apoge): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/course/<path:title>', methods=['DELETE'])
def del_crs(title):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_course(title): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/departement/<name>', methods=['DELETE'])
def del_dpt(name):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_departement(name): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/semester/<name>', methods=['DELETE'])
def del_sem(name):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_semester(name): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/salle/<code>', methods=['DELETE'])
def del_sal(code):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_salle(code): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()

@app.route('/api/admin/section/<sid>', methods=['DELETE'])
def del_sec(sid):
    svc, cnn = get_service_for_role('ADMIN')
    try:
        if svc.drop_section(sid): return jsonify({"message": "OK"})
        return jsonify({"error": "Erreur"}), 400
    finally: cnn.close()
# ==========================================
# ROUTES MODIFICATIONS (UPDATES)
# ==========================================

# 1. Password Student
@app.route('/api/admin/student/password', methods=['PUT'])
def update_student_pass():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.modify_student_password(d['code_apoge'], d['new_password']):
            return jsonify({"message": "Mot de passe étudiant modifié"})
        return jsonify({"error": "Erreur modification"}), 400
    finally: cnn.close()

# 2. Password Teacher
@app.route('/api/admin/teacher/password', methods=['PUT'])
def update_teacher_pass():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.modify_teacher_password(d['code_apoge'], d['new_password']):
            return jsonify({"message": "Mot de passe professeur modifié"})
        return jsonify({"error": "Erreur modification"}), 400
    finally: cnn.close()

# 3. Course Credits
@app.route('/api/admin/course/credits', methods=['PUT'])
def update_course_credits():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.modify_course_credits(d['title'], d['credits']):
            return jsonify({"message": "Crédits modifiés"})
        return jsonify({"error": "Erreur modification"}), 400
    finally: cnn.close()

# 4. Departement Name
@app.route('/api/admin/departement/name', methods=['PUT'])
def update_dept_name():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.modify_departement_name(d['old_name'], d['new_name']):
            return jsonify({"message": "Nom département modifié"})
        return jsonify({"error": "Erreur modification"}), 400
    finally: cnn.close()

# 5. Semester Name
@app.route('/api/admin/semester/name', methods=['PUT'])
def update_sem_name():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.modify_semester_name(d['old_name'], d['new_name']):
            return jsonify({"message": "Nom semestre modifié"})
        return jsonify({"error": "Erreur modification"}), 400
    finally: cnn.close()

# 6. Salle Capacity
@app.route('/api/admin/salle/capacity', methods=['PUT'])
def update_salle_cap():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        if svc.modify_salle_capacity(d['code'], d['capacity']):
            return jsonify({"message": "Capacité salle modifiée"})
        return jsonify({"error": "Erreur modification"}), 400
    finally: cnn.close()

# 7. Section Updates (Prof, Salle, Block)
@app.route('/api/admin/section/update', methods=['PUT'])
def update_section_details():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        sec_id = d.get('section_id')
        
        # Modification Professeur
        if 'instructor_id' in d:
            if not svc.modify_section_prof(sec_id, d['instructor_id']):
                return jsonify({"error": "Erreur update prof"}), 400
        
        # Modification Salle
        if 'salle_id' in d:
            if not svc.modify_section_salle(sec_id, d['salle_id']):
                return jsonify({"error": "Erreur update salle"}), 400

        return jsonify({"message": "Section mise à jour"})
    finally: cnn.close()

@app.route('/api/admin/section/block', methods=['PUT'])
def block_section_route():
    svc, cnn = get_service_for_role('ADMIN')
    try:
        d = request.json
        # Appelle la logique pour égaliser max_capacity = current_enrolled
        if svc.block_section(d['section_id']):
            return jsonify({"message": "Section bloquée (Complet)"})
        return jsonify({"error": "Erreur blocage"}), 400
    finally: cnn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)