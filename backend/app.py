from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import oracledb
from database import get_db_connection
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# This should be a secret key and stored securely
app.config['SECRET_KEY'] = 'your-secret-key'

def get_user_role(username):
    # This is a simplified example. In a real application, you would query
    # the database to get the user's role.
    if 'admin' in username:
        return 'admin'
    elif 'teacher' in username:
        return 'teacher'
    else:
        return 'student'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    connection = get_db_connection(username, password)

    if connection:
        connection.close()
        role = get_user_role(username)
        # WARNING: Storing password in JWT is a security risk.
        # This is done here only for demonstration purposes as per the project requirements.
        token = jwt.encode({'user': username, 'password': password, 'role': role}, app.config['SECRET_KEY'], algorithm='HS256')
        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data
        except:
            return jsonify({'message': 'Token is invalid'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/courses', methods=['GET', 'POST', 'DELETE', 'PUT'])
@token_required
def courses(current_user):
    if request.method == 'POST':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can add courses'}), 403

        data = request.get_json()
        course_code = data.get('course_code')
        title = data.get('title')
        credits = data.get('credits')
        departement_id = data.get('departement_id')

        if not all([course_code, title, credits, departement_id]):
            return jsonify({'message': 'course_code, title, credits, and departement_id are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO course (course_code, title, credits, departement_id) VALUES (:1, :2, :3, :4)", [course_code, title, credits, departement_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Course added successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'DELETE':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can delete courses'}), 403

        data = request.get_json()
        course_code = data.get('course_code')

        if not course_code:
            return jsonify({'message': 'course_code is required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM course WHERE course_code = :1", [course_code])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Course deleted successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'PUT':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can update courses'}), 403

        data = request.get_json()
        course_code = data.get('course_code')
        title = data.get('title')
        credits = data.get('credits')
        departement_id = data.get('departement_id')

        if not all([course_code, title, credits, departement_id]):
            return jsonify({'message': 'course_code, title, credits, and departement_id are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE course SET title = :1, credits = :2, departement_id = :3 WHERE course_code = :4", [title, credits, departement_id, course_code])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Course updated successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    else: # GET request
        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT course_code, title, credits, departement_id FROM course")
            courses = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify([{'course_code': c[0], 'title': c[1], 'credits': c[2], 'departement_id': c[3]} for c in courses])
        except oracledb.Error as err:
            error_obj, = err.args
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500


@app.route('/sections', methods=['GET', 'POST', 'DELETE', 'PUT'])
@token_required
def sections(current_user):
    if request.method == 'POST':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can add sections'}), 403

        data = request.get_json()
        section_id = data.get('section_id')
        course_code = data.get('course_code')
        semester_id = data.get('semester_id')
        instructor_id = data.get('instructor_id')
        max_capacity = data.get('max_capacity')
        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        room_location = data.get('room_location')


        if not all([section_id, course_code, semester_id, instructor_id, max_capacity, day_of_week, start_time, end_time, room_location]):
            return jsonify({'message': 'All fields are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO section (section_id, course_code, semester_id, instructor_id, max_capacity, current_enrolled, day_of_week, start_time, end_time, room_location) VALUES (:1, :2, :3, :4, :5, 0, :6, TO_DATE(:7, 'HH24:MI'), TO_DATE(:8, 'HH24:MI'), :9)",
                           [section_id, course_code, semester_id, instructor_id, max_capacity, day_of_week, start_time, end_time, room_location])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Section added successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'DELETE':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can delete sections'}), 403

        data = request.get_json()
        section_id = data.get('section_id')

        if not section_id:
            return jsonify({'message': 'section_id is required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM section WHERE section_id = :1", [section_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Section deleted successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'PUT':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can update sections'}), 403

        data = request.get_json()
        section_id = data.get('section_id')
        course_code = data.get('course_code')
        semester_id = data.get('semester_id')
        instructor_id = data.get('instructor_id')
        max_capacity = data.get('max_capacity')
        day_of_week = data.get('day_of_week')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        room_location = data.get('room_location')

        if not all([section_id, course_code, semester_id, instructor_id, max_capacity, day_of_week, start_time, end_time, room_location]):
            return jsonify({'message': 'All fields are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE section SET course_code = :1, semester_id = :2, instructor_id = :3, max_capacity = :4, day_of_week = :5, start_time = TO_DATE(:6, 'HH24:MI'), end_time = TO_DATE(:7, 'HH24:MI'), room_location = :8 WHERE section_id = :9",
                           [course_code, semester_id, instructor_id, max_capacity, day_of_week, start_time, end_time, room_location, section_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Section updated successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    else: # GET request
        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT section_id, course_code, semester_id, instructor_id, max_capacity, current_enrolled, day_of_week, TO_CHAR(start_time, 'HH24:MI'), TO_CHAR(end_time, 'HH24:MI'), room_location FROM section")
            sections = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify([{'section_id': s[0], 'course_code': s[1], 'semester_id': s[2], 'instructor_id': s[3], 'max_capacity': s[4], 'current_enrolled': s[5], 'day_of_week': s[6], 'start_time': s[7], 'end_time': s[8], 'room_location': s[9]} for s in sections])
        except oracledb.Error as err:
            error_obj, = err.args
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500


@app.route('/registration', methods=['POST'])
@token_required
def registration(current_user):
    if current_user['role'] != 'student':
        return jsonify({'message': 'Only students can register'}), 403

    data = request.get_json()
    section_id = data.get('section_id')
    student_id = data.get('student_id') # In a real app, you might get this from the user's profile

    if not section_id or not student_id:
        return jsonify({'message': 'section_id and student_id are required'}), 400

    conn = get_db_connection(current_user['user'], current_user['password'])
    if not conn:
        return jsonify({'message': 'Invalid credentials'}), 401

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO registration (student_id, section_id, registration_date, status) VALUES (:1, :2, SYSDATE, 'Registered')", [student_id, section_id])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Registration successful'})
    except oracledb.Error as err:
        error_obj, = err.args
        conn.rollback()
        return jsonify({'message': f'Database error: {error_obj.message}'}), 500

@app.route('/grades', methods=['GET', 'POST'])
@token_required
def grades(current_user):
    if request.method == 'POST':
        if current_user['role'] != 'teacher':
            return jsonify({'message': 'Only teachers can post grades'}), 403

        data = request.get_json()
        student_id = data.get('student_id')
        course_code = data.get('course_code')
        grade = data.get('grade')
        status = data.get('status')

        if not all([student_id, course_code, grade, status]):
            return jsonify({'message': 'student_id, course_code, grade, and status are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO course_result (student_id, course_code, grade, status) VALUES (:1, :2, :3, :4)", [student_id, course_code, grade, status])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Grade added successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    else: # GET request
        if current_user['role'] != 'student':
            return jsonify({'message': 'Only students can view grades'}), 403
        
        student_id = current_user['user']
        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT course_code, grade, status FROM course_result WHERE student_id = :1", [student_id])
            grades = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify([{'course_code': g[0], 'grade': g[1], 'status': g[2]} for g in grades])
        except oracledb.Error as err:
            error_obj, = err.args
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500


@app.route('/views/section-capacity', methods=['GET'])
@token_required
def get_section_capacity(current_user):
    conn = get_db_connection(current_user['user'], current_user['password'])
    if not conn:
        return jsonify({'message': 'Invalid credentials'}), 401
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM v_section_capacity")
        capacity_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([{'section_id': c[0], 'course_title': c[1], 'max_capacity': c[2], 'current_enrolled': c[3], 'available_seats': c[4]} for c in capacity_data])
    except oracledb.Error as err:
        error_obj, = err.args
        return jsonify({'message': f'Database error: {error_obj.message}'}), 500


@app.route('/views/registration-details', methods=['GET'])
@token_required
def get_registration_details(current_user):
    conn = get_db_connection(current_user['user'], current_user['password'])
    if not conn:
        return jsonify({'message': 'Invalid credentials'}), 401
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM v_registration_details")
        registration_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify([{'registration_id': r[0], 'student_id': r[1], 'first_name': r[2], 'last_name': r[3], 'course_title': r[4], 'semester': r[5], 'registration_date': r[6], 'status': r[7]} for r in registration_data])
    except oracledb.Error as err:
        error_obj, = err.args
        return jsonify({'message': f'Database error: {error_obj.message}'}), 500


@app.route('/students', methods=['GET', 'POST', 'DELETE', 'PUT'])
@token_required
def students(current_user):
    if request.method == 'POST':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can add students'}), 403

        data = request.get_json()
        student_id = data.get('student_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')

        if not all([student_id, first_name, last_name, email, phone_number]):
            return jsonify({'message': 'student_id, first_name, last_name, email, and phone_number are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO student (student_id, first_name, last_name, email, phone_number) VALUES (:1, :2, :3, :4, :5)", [student_id, first_name, last_name, email, phone_number])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Student added successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'DELETE':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can delete students'}), 403

        data = request.get_json()
        student_id = data.get('student_id')

        if not student_id:
            return jsonify({'message': 'student_id is required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM student WHERE student_id = :1", [student_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Student deleted successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'PUT':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can update students'}), 403

        data = request.get_json()
        student_id = data.get('student_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')

        if not all([student_id, first_name, last_name, email, phone_number]):
            return jsonify({'message': 'student_id, first_name, last_name, email, and phone_number are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE student SET first_name = :1, last_name = :2, email = :3, phone_number = :4 WHERE student_id = :5", [first_name, last_name, email, phone_number, student_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Student updated successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    else: # GET request
        if current_user['role'] not in ['teacher', 'admin']:
            return jsonify({'message': 'Only teachers and admins can view students'}), 403

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT student_id, first_name, last_name, email, phone_number FROM student")
            students = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify([{'student_id': s[0], 'first_name': s[1], 'last_name': s[2], 'email': s[3], 'phone_number': s[4]} for s in students])
        except oracledb.Error as err:
            error_obj, = err.args
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500


@app.route('/teachers', methods=['GET', 'POST', 'DELETE', 'PUT'])
@token_required
def teachers(current_user):
    if request.method == 'POST':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can add teachers'}), 403

        data = request.get_json()
        instructor_id = data.get('instructor_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')

        if not all([instructor_id, first_name, last_name, email]):
            return jsonify({'message': 'instructor_id, first_name, last_name, and email are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO instructor (instructor_id, first_name, last_name, email) VALUES (:1, :2, :3, :4)", [instructor_id, first_name, last_name, email])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Teacher added successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'DELETE':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can delete teachers'}), 403

        data = request.get_json()
        instructor_id = data.get('instructor_id')

        if not instructor_id:
            return jsonify({'message': 'instructor_id is required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM instructor WHERE instructor_id = :1", [instructor_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Teacher deleted successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    elif request.method == 'PUT':
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can update teachers'}), 403

        data = request.get_json()
        instructor_id = data.get('instructor_id')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')

        if not all([instructor_id, first_name, last_name, email]):
            return jsonify({'message': 'instructor_id, first_name, last_name, and email are required'}), 400

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401

        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE instructor SET first_name = :1, last_name = :2, email = :3 WHERE instructor_id = :4", [first_name, last_name, email, instructor_id])
            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'message': 'Teacher updated successfully'})
        except oracledb.Error as err:
            error_obj, = err.args
            conn.rollback()
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500
    else: # GET request
        if current_user['role'] != 'admin':
            return jsonify({'message': 'Only admins can view teachers'}), 403

        conn = get_db_connection(current_user['user'], current_user['password'])
        if not conn:
            return jsonify({'message': 'Invalid credentials'}), 401
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT instructor_id, first_name, last_name, email FROM instructor")
            teachers = cursor.fetchall()
            cursor.close()
            conn.close()
            return jsonify([{'instructor_id': t[0], 'first_name': t[1], 'last_name': t[2], 'email': t[3]} for t in teachers])
        except oracledb.Error as err:
            error_obj, = err.args
            return jsonify({'message': f'Database error: {error_obj.message}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5001)