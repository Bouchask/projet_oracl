/* =======================================================
   SCRIPT DE SECURITE (ROLES & USERS)
   Compatible avec db.sql
   ======================================================= */

/* -------------------------------------------------------
   1. NETTOYAGE (CLEANUP) - Bach nbda mn Zero
   ------------------------------------------------------- */
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

/* -------------------------------------------------------
   2. CREATION DES ROLES
   ------------------------------------------------------- */
CREATE ROLE role_admin;
CREATE ROLE role_teacher;
CREATE ROLE role_student;

/* -------------------------------------------------------
   3. CONFIGURATION: ROLE ADMIN (Moul Chi)
   ------------------------------------------------------- */
-- Admin 3ndo Full Access (Select, Insert, Update, Delete) 3la kolchi
-- Tables
GRANT ALL PRIVILEGES ON app_user TO role_admin;
GRANT ALL PRIVILEGES ON student TO role_admin;
GRANT ALL PRIVILEGES ON instructor TO role_admin;
GRANT ALL PRIVILEGES ON departement TO role_admin;
GRANT ALL PRIVILEGES ON course TO role_admin;
GRANT ALL PRIVILEGES ON semester TO role_admin;
GRANT ALL PRIVILEGES ON section TO role_admin;
GRANT ALL PRIVILEGES ON salle TO role_admin;
GRANT ALL PRIVILEGES ON prerequisite TO role_admin;
GRANT ALL PRIVILEGES ON registration TO role_admin;
GRANT ALL PRIVILEGES ON course_result TO role_admin;
GRANT ALL PRIVILEGES ON grades_audit TO role_admin; -- Admin bohdou li ychouf l'audit

-- Views
GRANT SELECT ON v_users_login TO role_admin;
GRANT SELECT ON v_section_capacity TO role_admin;
GRANT SELECT ON v_registration_details TO role_admin;
GRANT SELECT ON v_section_details TO role_admin;
GRANT SELECT ON v_student_transcript TO role_admin;


GRANT SELECT ON yahya_admin.v_student_results_grouped TO role_student;
GRANT SELECT ON yahya_admin.v_student_results_grouped TO role_teacher;
GRANT SELECT ON yahya_admin.v_student_results_grouped TO role_admin;
GRANT SELECT ON v_student_enrollment_extended TO role_student;
GRANT SELECT ON v_student_enrollment_extended TO role_admin;
/* -------------------------------------------------------
   4. CONFIGURATION: ROLE TEACHER (Prof)
   ------------------------------------------------------- */
-- A. Données Personnelles (Profile)
GRANT SELECT ON app_user TO role_teacher;
GRANT UPDATE (password_hash) ON app_user TO role_teacher; -- Ybdl Mdp
GRANT SELECT ON instructor TO role_teacher;
GRANT UPDATE (email, name) ON instructor TO role_teacher; -- Ybdl Email/Name

-- B. Affichage (Read Only)
GRANT SELECT ON departement TO role_teacher;
GRANT SELECT ON course TO role_teacher;
GRANT SELECT ON semester TO role_teacher;
GRANT SELECT ON salle TO role_teacher;
GRANT SELECT ON prerequisite TO role_teacher;
GRANT SELECT ON student TO role_teacher; -- Ychouf smiyat tlamd
GRANT SELECT ON section TO role_teacher;
GRANT SELECT ON v_section_details TO role_teacher;
GRANT SELECT ON v_section_capacity TO role_teacher;

-- C. Gestion des Notes (Le Cœur du métier)
GRANT SELECT ON course_result TO role_teacher;
GRANT INSERT ON course_result TO role_teacher; -- Yzid note
GRANT UPDATE (grade) ON course_result TO role_teacher; -- Ybdl note
-- Note: Trigger 'trg_auto_status' ghadi y-géré Status, donc prof may9issouch direct
GRANT SELECT ON v_student_transcript TO role_teacher;

-- D. Gestion Inscription (Juste Status)
GRANT SELECT ON registration TO role_teacher;
GRANT SELECT ON v_registration_details TO role_teacher;
GRANT UPDATE (status) ON registration TO role_teacher; -- Drop/Cancel student

/* -------------------------------------------------------
   5. CONFIGURATION: ROLE STUDENT (Etudiant)
   ------------------------------------------------------- */
-- A. Données Personnelles
GRANT SELECT ON app_user TO role_student;
GRANT UPDATE (password_hash) ON app_user TO role_student; -- Ybdl Mdp
GRANT SELECT ON student TO role_student;
GRANT UPDATE (email) ON student TO role_student; -- Ybdl Email

-- B. Affichage (Offre Pédagogique)
GRANT SELECT ON departement TO role_student;
GRANT SELECT ON course TO role_student;
GRANT SELECT ON semester TO role_student;
GRANT SELECT ON salle TO role_student;
GRANT SELECT ON prerequisite TO role_student;
GRANT SELECT ON instructor TO role_student; -- Ychouf profs
GRANT SELECT ON section TO role_student;
GRANT SELECT ON v_section_details TO role_student;
GRANT SELECT ON v_section_capacity TO role_student;

-- C. Inscription (S'inscrire + Annuler)
GRANT SELECT ON registration TO role_student;
GRANT SELECT ON v_registration_details TO role_student;
GRANT INSERT ON registration TO role_student; -- Ydf3 inscription
GRANT UPDATE (status) ON registration TO role_student; -- Y-annuler raso (Cancel)

-- D. Résultats (Read Only)
GRANT SELECT ON course_result TO role_student;
GRANT SELECT ON v_student_transcript TO role_student;

/* -------------------------------------------------------
   6. CREATION DES USERS (Connectors pour Python)
   ------------------------------------------------------- */

-- 1. Admin User
CREATE USER user_admin IDENTIFIED BY "AdminPass123" 
DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
GRANT CREATE SESSION TO user_admin;
GRANT role_admin TO user_admin;

-- 2. Teacher User (Compte générique pour les profs)
CREATE USER user_teacher IDENTIFIED BY "TeacherPass123" 
DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
GRANT CREATE SESSION TO user_teacher;
GRANT role_teacher TO user_teacher;

-- 3. Student User (Compte générique pour les étudiants)
CREATE USER user_student IDENTIFIED BY "StudentPass123" 
DEFAULT TABLESPACE users QUOTA UNLIMITED ON users;
GRANT CREATE SESSION TO user_student;
GRANT role_student TO user_student;

COMMIT;