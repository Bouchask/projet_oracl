/* =========================
   ROLES
========================= */
CREATE ROLE role_admin;
CREATE ROLE role_backend;

-- GRANTS FOR ROLE_ADMIN
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.app_user TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.student TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.instructor TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.course TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.section TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.semester TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.prerequisite TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.registration TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.course_result TO role_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON yahya_admin.salle TO role_admin;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_admin;
GRANT SELECT ON yahya_admin.v_users_login TO role_admin;

-- GRANTS FOR ROLE_BACKEND
-- AUTH
GRANT SELECT ON yahya_admin.app_user TO role_backend;

-- READ
GRANT SELECT ON yahya_admin.student TO role_backend;
GRANT SELECT ON yahya_admin.instructor TO role_backend;
GRANT SELECT ON yahya_admin.course TO role_backend;
GRANT SELECT ON yahya_admin.section TO role_backend;
GRANT SELECT ON yahya_admin.semester TO role_backend;
GRANT SELECT ON yahya_admin.salle TO role_backend;
GRANT SELECT ON yahya_admin.v_section_capacity TO role_backend;

-- WRITE (Controlled Logic)
GRANT INSERT, UPDATE ON yahya_admin.registration TO role_backend;
GRANT INSERT, UPDATE ON yahya_admin.course_result TO role_backend;

/* =========================
   USERS
========================= */
CREATE USER app_backend IDENTIFIED BY "Str0ng_Backend_P@ss"
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

GRANT CREATE SESSION TO app_backend;
GRANT role_backend TO app_backend;

-- Note: user 'app_user' table is created in db.sql

CREATE USER app_admin IDENTIFIED BY "Str0ng_Admin_P@ss"
DEFAULT TABLESPACE users
TEMPORARY TABLESPACE temp
QUOTA UNLIMITED ON users;

GRANT CREATE SESSION TO app_admin;
GRANT role_admin TO app_admin;