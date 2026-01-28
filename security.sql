/* =======================================================
   SCRIPT DE SECURITE (ROLES & USERS)
   CORRIGE: Schema Prefix + No Inline Comments
   ======================================================= */

/* 1. CLEANUP */
BEGIN
   EXECUTE IMMEDIATE 'DROP USER user_student CASCADE';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP USER user_teacher CASCADE';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP USER user_admin CASCADE';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP ROLE role_student';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP ROLE role_teacher';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/
BEGIN
   EXECUTE IMMEDIATE 'DROP ROLE role_admin';
EXCEPTION WHEN OTHERS THEN NULL;
END;
/

/* 2. CREATION DES ROLES */
CREATE ROLE role_admin;
CREATE ROLE role_teacher;
CREATE ROLE role_student;

/* 3. CONFIGURATION: ROLE ADMIN */
GRANT ALL PRIVILEGES ON yahya_admin.app_user TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.student TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.instructor TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.departement TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.course TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.semester TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.section TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.salle TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.prerequisite TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.registration TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.course_result TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.grades_audit TO role_admin;

GRANT SELECT ON yahya_admin.v_users_login TO role_admin;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_admin;
GRANT SELECT ON yahya_admin.v_registration_details TO role_admin;
GRANT SELECT ON yahya_admin.v_section_details TO role_admin;
GRANT SELECT ON yahya_admin.v_student_transcript TO role_admin;
GRANT SELECT ON yahya_admin.v_student_results_grouped TO role_admin;
GRANT SELECT ON yahya_admin.v_student_enrollment_extended TO role_admin;

/* 4. CONFIGURATION: ROLE TEACHER */
GRANT SELECT ON yahya_admin.app_user TO role_teacher;
GRANT UPDATE (password_hash) ON yahya_admin.app_user TO role_teacher;
GRANT SELECT ON yahya_admin.instructor TO role_teacher;
GRANT UPDATE (email, name) ON yahya_admin.instructor TO role_teacher;

GRANT SELECT ON yahya_admin.departement TO role_teacher;
GRANT SELECT ON yahya_admin.course TO role_teacher;
GRANT SELECT ON yahya_admin.semester TO role_teacher;
GRANT SELECT ON yahya_admin.salle TO role_teacher;
GRANT SELECT ON yahya_admin.prerequisite TO role_teacher;
GRANT SELECT ON yahya_admin.student TO role_teacher;
GRANT SELECT ON yahya_admin.section TO role_teacher;
GRANT SELECT ON yahya_admin.v_section_details TO role_teacher;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_teacher;

GRANT SELECT ON yahya_admin.course_result TO role_teacher;
GRANT INSERT ON yahya_admin.course_result TO role_teacher;
GRANT UPDATE (grade) ON yahya_admin.course_result TO role_teacher;
GRANT SELECT ON yahya_admin.v_student_transcript TO role_teacher;
GRANT SELECT ON yahya_admin.v_student_results_grouped TO role_teacher;

GRANT SELECT ON yahya_admin.registration TO role_teacher;
GRANT SELECT ON yahya_admin.v_registration_details TO role_teacher;
GRANT UPDATE (status) ON yahya_admin.registration TO role_teacher;

/* 5. CONFIGURATION: ROLE STUDENT */
GRANT SELECT ON yahya_admin.app_user TO role_student;
GRANT UPDATE (password_hash) ON yahya_admin.app_user TO role_student;
GRANT SELECT ON yahya_admin.student TO role_student;
GRANT UPDATE (email) ON yahya_admin.student TO role_student;

GRANT SELECT ON yahya_admin.departement TO role_student;
GRANT SELECT ON yahya_admin.course TO role_student;
GRANT SELECT ON yahya_admin.semester TO role_student;
GRANT SELECT ON yahya_admin.salle TO role_student;
GRANT SELECT ON yahya_admin.prerequisite TO role_student;
GRANT SELECT ON yahya_admin.instructor TO role_student;
GRANT SELECT ON yahya_admin.section TO role_student;
GRANT SELECT ON yahya_admin.v_section_details TO role_student;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_student;
GRANT SELECT ON yahya_admin.v_student_enrollment_extended TO role_student;

GRANT SELECT ON yahya_admin.registration TO role_student;
GRANT SELECT ON yahya_admin.v_registration_details TO role_student;
GRANT INSERT ON yahya_admin.registration TO role_student;
GRANT UPDATE (status) ON yahya_admin.registration TO role_student;

GRANT SELECT ON yahya_admin.course_result TO role_student;
GRANT SELECT ON yahya_admin.v_student_transcript TO role_student;
GRANT SELECT ON yahya_admin.v_student_results_grouped TO role_student;

/* 6. USERS */
CREATE USER user_admin IDENTIFIED BY "AdminPass123" DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
GRANT CREATE SESSION TO user_admin;
GRANT role_admin TO user_admin;

CREATE USER user_teacher IDENTIFIED BY "TeacherPass123" DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
GRANT CREATE SESSION TO user_teacher;
GRANT role_teacher TO user_teacher;

CREATE USER user_student IDENTIFIED BY "StudentPass123" DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
GRANT CREATE SESSION TO user_student;
GRANT role_student TO user_student;

COMMIT;