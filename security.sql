/* =========================
   ROLES
========================= */

CREATE ROLE role_admin;
CREATE ROLE role_teacher;
CREATE ROLE role_student;

/* =========================
   ROLE_ADMIN PRIVILEGES
========================= */

GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.student TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.course TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.section TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.semester TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.prerequisite TO role_admin;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_admin;
GRANT SELECT ON yahya_admin.v_registration_details TO role_admin;

/* =========================
   ROLE_TEACHER PRIVILEGES
========================= */

GRANT SELECT ON yahya_admin.student TO role_teacher;
GRANT SELECT ON yahya_admin.section TO role_teacher;
GRANT INSERT, UPDATE ON yahya_admin.course_result TO role_teacher;
GRANT SELECT ON yahya_admin.v_student_performance TO role_teacher;

/* =========================
   ROLE_STUDENT PRIVILEGES
========================= */

GRANT SELECT ON yahya_admin.course TO role_student;
GRANT SELECT ON yahya_admin.section TO role_student;
GRANT INSERT ON yahya_admin.registration TO role_student;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_student;
GRANT SELECT ON yahya_admin.v_registration_details TO role_student;

/* =========================
   USERS
========================= */

CREATE USER admin_user IDENTIFIED BY admin123;
CREATE USER teacher_user IDENTIFIED BY teacher123;
CREATE USER student_user IDENTIFIED BY student123;

/* =========================
   LOGIN PERMISSION
========================= */

GRANT CREATE SESSION TO admin_user;
GRANT CREATE SESSION TO teacher_user;
GRANT CREATE SESSION TO student_user;

/* =========================
   ASSIGN ROLES
========================= */

GRANT role_admin TO admin_user;
GRANT role_teacher TO teacher_user;
GRANT role_student TO student_user;
