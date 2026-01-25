from flask import Flask, render_template, request, redirect, url_for, flash
import oracledb
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Replace with your actual Oracle Database connection details
# For example:
# dsn = oracledb.makedsn("your_hostname", "your_port", sid="your_sid")
# conn = oracledb.connect(user="your_username", password="your_password", dsn=dsn)
# For this example, I'll use a placeholder.
# In a real application, use a more secure way to handle credentials.
try:
    conn = oracledb.connect(user="system", password="yoyo", dsn="localhost:1521/XE")
    print("Database connection successful")
except oracledb.DatabaseError as e:
    print(f"Database connection failed: {e}")
    conn = None

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard', methods=['POST'])
def dashboard():
    role = request.form.get('role')
    if role == 'student':
        return redirect(url_for('student_dashboard'))
    elif role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        flash('Invalid role selected.')
        return redirect(url_for('login'))

@app.route('/student')
def student_dashboard():
    if not conn:
        flash('Database connection not available.')
        return render_template('student_dashboard.html', sections=[])
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT v.section_id, v.course_title, i.name, v.max_capacity, v.current_enrolled
            FROM v_section_capacity v
            JOIN section s ON v.section_id = s.section_id
            JOIN instructor i ON s.instructor_id = i.instructor_id
        """)
        sections = cursor.fetchall()
    except oracledb.DatabaseError as e:
        flash(f"Error fetching sections: {e}")
        sections = []
    cursor.close()
    return render_template('student_dashboard.html', sections=sections)

@app.route('/register', methods=['POST'])
def register():
    if not conn:
        flash('Database connection not available.')
        return redirect(url_for('student_dashboard'))

    student_id = request.form.get('student_id')
    section_id = request.form.get('section_id')
    cursor = conn.cursor()
    try:
        cursor.callproc('register_student', [student_id, section_id])
        conn.commit()
        flash('Successfully registered for the course.')
    except oracledb.DatabaseError as e:
        error_obj, = e.args
        flash(f"Error: {error_obj.message}")
    finally:
        cursor.close()
    return redirect(url_for('student_dashboard'))


@app.route('/teacher')
def teacher_dashboard():
    if not conn:
        flash('Database connection not available.')
        return render_template('teacher_dashboard.html', students=[])
    cursor = conn.cursor()
    try:
        # Assuming a teacher_id is hardcoded/mocked for this example
        teacher_id = 1 
        cursor.execute("""
            SELECT s.student_id, s.first_name, s.last_name, c.title, sec.section_id
            FROM student s
            JOIN registration r ON s.student_id = r.student_id
            JOIN section sec ON r.section_id = sec.section_id
            JOIN course c ON sec.course_code = c.course_code
            WHERE sec.instructor_id = :tid
        """, tid=teacher_id)
        students = cursor.fetchall()
    except oracledb.DatabaseError as e:
        flash(f"Error fetching students: {e}")
        students = []
    cursor.close()
    return render_template('teacher_dashboard.html', students=students)

@app.route('/update_grade', methods=['POST'])
def update_grade():
    if not conn:
        flash('Database connection not available.')
        return redirect(url_for('teacher_dashboard'))

    student_id = request.form.get('student_id')
    section_id = request.form.get('section_id')
    grade = request.form.get('grade')
    cursor = conn.cursor()
    try:
        # Get course_code from section_id
        cursor.execute("SELECT course_code FROM section WHERE section_id = :sec_id", sec_id=section_id)
        result = cursor.fetchone()
        if result is None:
            flash(f"Section {section_id} not found.")
            return redirect(url_for('teacher_dashboard'))
        course_code = result[0]

        cursor.execute("""
            MERGE INTO course_result cr
            USING (SELECT :sid AS student_id, :cc AS course_code FROM dual) data
            ON (cr.student_id = data.student_id AND cr.course_code = data.course_code)
            WHEN MATCHED THEN
                UPDATE SET cr.grade = :g
            WHEN NOT MATCHED THEN
                INSERT (student_id, course_code, grade, status)
                VALUES (:sid, :cc, :g, 'PASS')
        """, sid=student_id, cc=course_code, g=grade)
        conn.commit()
        flash('Grade updated successfully.')
    except oracledb.DatabaseError as e:
        flash(f"Error updating grade: {e}")
    finally:
        cursor.close()
    return redirect(url_for('teacher_dashboard'))

@app.route('/admin')
def admin_dashboard():
    if not conn:
        flash('Database connection not available.')
        return render_template('admin_dashboard.html', stats=[], students=[], courses=[])
    
    cursor = conn.cursor()
    try:
        # Global statistics
        cursor.execute("SELECT * FROM v_registration_details")
        stats = cursor.fetchall()

        # Fetch all students and courses for the forms
        cursor.execute("SELECT student_id, first_name, last_name, email FROM student")
        students = cursor.fetchall()
        cursor.execute("SELECT course_code, title, credits FROM course")
        courses = cursor.fetchall()
        
    except oracledb.DatabaseError as e:
        flash(f"Error fetching admin data: {e}")
        stats = []
        students = []
        courses = []
    finally:
        cursor.close()

    return render_template('admin_dashboard.html', stats=stats, students=students, courses=courses)


@app.route('/add_student', methods=['POST'])
def add_student():
    if not conn:
        flash('Database connection not available.')
        return redirect(url_for('admin_dashboard'))

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    academic_level = request.form.get('academic_level')
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO student (first_name, last_name, email, academic_level, enrollment_date)
            VALUES (:fn, :ln, :em, :al, SYSDATE)
        """, fn=first_name, ln=last_name, em=email, al=academic_level)
        conn.commit()
        flash('Student added successfully.')
    except oracledb.DatabaseError as e:
        flash(f"Error adding student: {e}")
    finally:
        cursor.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_course', methods=['POST'])
def add_course():
    if not conn:
        flash('Database connection not available.')
        return redirect(url_for('admin_dashboard'))

    course_name = request.form.get('course_name')
    credits = request.form.get('credits')
    
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO course (title, credits, departement_id)
            VALUES (:cn, :cr, 1)
        """, cn=course_name, cr=credits)
        conn.commit()
        flash('Course added successfully.')
    except oracledb.DatabaseError as e:
        flash(f"Error adding course: {e}")
    finally:
        cursor.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
