/* SECURITE (ROLES & PRIVILEGES) - VERSION CORRIGEE */
BEGIN EXECUTE IMMEDIATE 'DROP USER user_student CASCADE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP USER user_teacher CASCADE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP USER user_admin CASCADE'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP ROLE role_student'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP ROLE role_teacher'; EXCEPTION WHEN OTHERS THEN NULL; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP ROLE role_admin'; EXCEPTION WHEN OTHERS THEN NULL; END;
/

CREATE ROLE role_admin;
CREATE ROLE role_teacher;
CREATE ROLE role_student;

-- ADMIN
GRANT ALL PRIVILEGES ON yahya_admin.app_user TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.student TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.instructor TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.departement TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.filiere TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.course TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.semester TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.section TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.salle TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.prerequisite TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.registration TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.course_result TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.student_semester_result TO role_admin;
GRANT ALL PRIVILEGES ON yahya_admin.grades_audit TO role_admin;
GRANT SELECT ON yahya_admin.v_course_hours_tracking TO role_admin;
GRANT SELECT ON yahya_admin.v_section_details TO role_admin;
GRANT EXECUTE ON yahya_admin.PKG_SECURITY TO role_admin;
GRANT EXECUTE ON yahya_admin.PKG_ACADEMIC TO role_admin;
GRANT EXECUTE ON yahya_admin.PKG_REGISTRATION TO role_admin;
GRANT EXECUTE ON yahya_admin.PKG_GRADES TO role_admin;
GRANT EXECUTE ON yahya_admin.PKG_PREREQ TO role_admin;

-- TEACHER
GRANT SELECT ON yahya_admin.app_user TO role_teacher;
GRANT SELECT ON yahya_admin.instructor TO role_teacher;
GRANT UPDATE (email, name) ON yahya_admin.instructor TO role_teacher;
GRANT SELECT ON yahya_admin.departement TO role_teacher;
GRANT SELECT ON yahya_admin.course TO role_teacher;
GRANT SELECT ON yahya_admin.section TO role_teacher;
GRANT SELECT ON yahya_admin.student TO role_teacher;
GRANT SELECT ON yahya_admin.v_section_details TO role_teacher;
GRANT SELECT ON yahya_admin.v_course_hours_tracking TO role_teacher;
GRANT SELECT ON yahya_admin.v_section_student_list TO role_teacher;
GRANT EXECUTE ON yahya_admin.PKG_ACADEMIC TO role_teacher;
GRANT EXECUTE ON yahya_admin.PKG_REGISTRATION TO role_teacher;
GRANT EXECUTE ON yahya_admin.PKG_SECURITY TO role_teacher;
GRANT EXECUTE ON yahya_admin.PKG_GRADES TO role_teacher;
GRANT EXECUTE ON yahya_admin.PKG_PREREQ TO role_teacher;

-- STUDENT
GRANT SELECT ON yahya_admin.app_user TO role_student;
GRANT SELECT ON yahya_admin.student TO role_student;
GRANT UPDATE (email) ON yahya_admin.student TO role_student;
GRANT SELECT ON yahya_admin.course TO role_student;
GRANT SELECT ON yahya_admin.section TO role_student;
GRANT SELECT ON yahya_admin.v_student_eligible_sections TO role_student;
GRANT INSERT ON yahya_admin.registration TO role_student;
GRANT UPDATE (status) ON yahya_admin.registration TO role_student;
GRANT SELECT ON yahya_admin.course_result TO role_student;
GRANT SELECT ON yahya_admin.v_student_transcript TO role_student;
GRANT EXECUTE ON yahya_admin.PKG_ACADEMIC TO role_student;
GRANT EXECUTE ON yahya_admin.PKG_REGISTRATION TO role_student;
GRANT EXECUTE ON yahya_admin.PKG_SECURITY TO role_student;
GRANT EXECUTE ON yahya_admin.PKG_GRADES TO role_student;

-- USERS
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