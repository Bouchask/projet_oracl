import logging

class AdminService:
    def __init__(self, cnn, student_mgr, instructor_mgr, course_mgr, section_mgr, 
                 registration_mgr, departement_mgr, salle_mgr, semester_mgr, 
                 course_result_mgr, prerequisite_mgr, grades_audit_mgr, filiere_mgr):
        self.cnn = cnn
        self.student = student_mgr
        self.instructor = instructor_mgr
        self.course = course_mgr
        self.section = section_mgr
        self.registration = registration_mgr
        self.departement = departement_mgr
        self.salle = salle_mgr
        self.semester = semester_mgr
        self.course_result = course_result_mgr
        self.prerequisite = prerequisite_mgr
        self.grades_audit = grades_audit_mgr
        self.filiere = filiere_mgr # <--- IMPORTANT: Gestionnaire Filière ajouté

    # ==========================================
    # 1. STATISTIQUES (Pour Dashboard)
    # ==========================================
    def get_dashboard_stats(self):
        stats = {"students": 0, "instructors": 0, "courses": 0, "sections": 0}
        
        # On fait des try/except silencieux pour éviter que tout plante si une table est vide ou erreur SQL
        try: 
            cur = self.cnn.cursor()
            cur.execute("SELECT COUNT(*) FROM student")
            stats["students"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM instructor")
            stats["instructors"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM course")
            stats["courses"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM section")
            stats["sections"] = cur.fetchone()[0]
            cur.close()
        except Exception as e:
            logging.error(f"Erreur stats: {e}")
            
        return stats

    # ==========================================
    # 2. DROP FUNCTIONS (Suppression)
    # ==========================================
    def drop_student(self, code): return self.student.deleted_student(code)
    def drop_instructor(self, code): return self.instructor.deleted_instructor(code)
    def drop_course(self, title): return self.course.delete_course(title)
    
    def drop_departement(self, name): return self.departement.delete_departement(name)
    def drop_semester(self, name): return self.semester.delete_semester(name)
    def drop_salle(self, code): return self.salle.delete_salle(code)
    def drop_section(self, sid): return self.section.delete_section(sid)

    # ==========================================
    # 3. LISTS & ADDS
    # ==========================================
    # Filières
    def show_filieres(self): return self.filiere.select_all_filieres()
    def add_filiere(self, name, dept_id): return self.filiere.insert_filiere(name, dept_id)

    # Etudiants
    def show_all_students(self): return self.student.select_AllStudent()
    def add_student(self, f, l, e, fil_id, sem_id, p): 
        return self.student.insert_student(f, l, e, fil_id, sem_id, p)

    # Profs
    def show_all_instructors(self): return self.instructor.select_all_instructors()
    def add_instructor(self, n, e, d, p): return self.instructor.insert_instructor(n, e, d, p)

    # Cours
    def show_all_courses(self): return self.course.select_all_courses()
    def add_course(self, t, c, f_id, s_id, h): 
        return self.course.insert_course(t, c, f_id, s_id, h)

    # Structure
    def show_all_departments(self): return self.departement.select_all_departments()
    def add_departement(self, n): return self.departement.insert_departement(n)

    def show_all_semesters(self): return self.semester.select_all_semesters()
    def add_semester(self, n, s, e): return self.semester.insert_semester(n, s, e)

    def show_all_salles(self): return self.salle.select_all_salles()
    def add_salle(self, c, cap, b): return self.salle.insert_salle(c, cap, b)

    # Sections
    def show_sections(self): return self.section.get_all_section_details()
    def add_section(self, c, i, sa, cap, d, st, en): 
        # Note: semester_id est déduit ou non utilisé directement dans l'insert section simple
        return self.section.insert_section(c, i, sa, cap, d, st, en)

    # Inscriptions
    def show_section_registrations(self, sid): return self.registration.get_registrations_by_section(sid)
    def validate_reg(self, rid): return self.registration.validate_registration(rid)
    def cancel_reg(self, rid): return self.registration.cancel_registration(rid)
    def drop_reg(self, rid): return self.registration.drop_registration(rid)

    # Audit
    def show_audit_logs(self): return self.grades_audit.select_all_audits() if self.grades_audit else []

    # --- MODIFICATIONS ---
    def modify_teacher_password(self, code, pwd):
        return self.instructor.app_user_manager.update_app_user_password(code, pwd)
    
    def modify_student_password(self, code, pwd):
        return self.student.app_user_manager.update_app_user_password(code, pwd)

    def modify_course_credits(self, title, new_credits):
        return self.course.update_course_(title, new_credits)

    def modify_departement_name(self, old, new):
        return self.departement.update_departement_name(old, new)

    def modify_semester_name(self, old, new):
        return self.semester.update_semester_name(old, new)

    def modify_salle_capacity(self, code, cap):
        return self.salle.update_salle_capacity(code, cap)

    def modify_section_prof(self, sec_id, prof_id):
        return self.section.update_section_instructor(sec_id, prof_id)

    def modify_section_salle(self, sec_id, salle_id):
        return self.section.update_section_salle(sec_id, salle_id)

    def block_section(self, sec_id):
        return self.section.block_section_enrollment(sec_id)
    # Récupérer le dossier complet d'un étudiant (Infos + Notes)
    def get_student_details_full(self, student_id):
        # 1. Infos personnelles (On cherche dans la liste existante pour éviter une nouvelle requête complexe)
        all_students = self.student.select_AllStudent()
        # student_id est un string ou int, on compare en string pour être sûr
        std_info = next((s for s in all_students if str(s[0]) == str(student_id)), None)
        
        # 2. Historique des cours (Via la nouvelle fonction Oracle)
        transcript = self.student.get_course_history(student_id)
        
        return {
            "info": std_info,
            "transcript": transcript
        }
    # Récupérer dossier Professeur (Infos + Sections)
    def get_teacher_details_full(self, instructor_id):
        # 1. Chercher infos prof
        all_teachers = self.instructor.select_all_instructors()
        # [0:id, 1:code, 2:nom, 3:email, 4:dept]
        tch_info = next((t for t in all_teachers if str(t[0]) == str(instructor_id)), None)
        
        # 2. Récupérer ses sections
        sections = self.instructor.get_schedule_details(instructor_id)
        
        return {
            "info": tch_info,
            "sections": sections
        }
    # Récupérer dossier complet du Cours
    def get_course_details_full(self, course_code):
        # 1. Infos du cours (On cherche dans la liste globale)
        all_courses = self.course.select_all_courses()
        # [0:code, 1:titre, 2:credits, 3:filiere, 4:semestre, 5:total_hours]
        crs_info = next((c for c in all_courses if str(c[0]) == str(course_code)), None)
        
        # 2. Sections
        sections_raw = self.course.get_course_sections(course_code)
        
        # 3. Calcul des heures planifiées
        hours_planned = 0
        formatted_sections = []
        
        if sections_raw:
            for s in sections_raw:
                # s[7] est la durée calculée par SQL
                duration = float(s[7]) if s[7] else 0
                hours_planned += duration
                formatted_sections.append(s)

        return {
            "info": crs_info,
            "sections": formatted_sections,
            "stats": {
                "total_budget": crs_info[5] if crs_info else 0,
                "total_planned": round(hours_planned, 1)
            }
        }
    # Programme pédagogique (Filtre par semestre)
    def get_filiere_program(self, filiere_id, semester_id):
        # 1. Infos Filière
        all_fils = self.filiere.select_all_filieres()
        fil_info = next((f for f in all_fils if str(f[0]) == str(filiere_id)), None)
        
        # 2. Cours du semestre
        courses = self.filiere.get_courses_by_semester(filiere_id, semester_id)
        
        return {"info": fil_info, "courses": courses}
    def get_teacher_dept_info(self, instructor_id):
        # Récupère les infos du département actuel
        return self.instructor.get_current_dept(instructor_id)

    def modify_teacher_department(self, instructor_id, new_dept_id):
        # Appelle la procédure stockée pour changer le département
        return self.instructor.update_department(instructor_id, new_dept_id)