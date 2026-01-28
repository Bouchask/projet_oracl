import logging

class AdminService:
    def __init__(self, cnn, student_mgr, instructor_mgr, course_mgr, section_mgr, 
                 registration_mgr, departement_mgr, salle_mgr, semester_mgr, 
                 course_result_mgr, prerequisite_mgr, grades_audit_mgr):
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

    # ==========================================
    # 1. STATISTIQUES (Pour Dashboard)
    # ==========================================
    def get_dashboard_stats(self):
        # On utilise try/except au cas où une classe n'a pas encore la fonction count
        stats = {"students": 0, "instructors": 0, "courses": 0, "sections": 0}
        try: stats["students"] = self.student.count_students()
        except: pass
        try: stats["instructors"] = self.instructor.count_instructors()
        except: pass
        try: stats["courses"] = self.course.count_courses()
        except: pass
        try: stats["sections"] = self.section.count_sections()
        except: pass
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
    def show_all_students(self): return self.student.select_AllStudent()
    def add_student(self, f, l, e, lvl, p): return self.student.insert_student(f, l, e, lvl, p)

    def show_all_instructors(self): return self.instructor.select_all_instructors()
    def add_instructor(self, n, e, d, p): return self.instructor.insert_instructor(n, e, d, p)

    def show_all_courses(self): return self.course.select_all_courses()
    def add_course(self, t, c): return self.course.insert_course(t, c)

    def show_all_departments(self): return self.departement.select_all_departements()
    def add_departement(self, n): return self.departement.insert_departement(n)

    def show_all_semesters(self): return self.semester.select_all_semesters()
    def add_semester(self, n, s, e): return self.semester.insert_semester(n, s, e)

    def show_all_salles(self): return self.salle.select_all_salles()
    def add_salle(self, c, cap, b): return self.salle.insert_salle(c, cap, b)

    # Sections
    def show_sections(self): return self.section.get_all_section_details()
    def add_section(self, c, s, i, sa, cap, d, st, en): return self.section.insert_section(c, s, i, sa, cap, d, st, en)

    # Inscriptions
    def show_section_registrations(self, sid): return self.registration.get_registrations_by_section(sid)
    def change_registration_status(self, rid, st): return self.registration.update_registration_status(rid, st)

    # Audit
    def show_audit_logs(self): return self.grades_audit.select_all_audits() if self.grades_audit else []

    # --- MODIFICATIONS UTILISATEURS ---
    def modify_teacher_password(self, code_apoge, new_password):
        return self.instructor.update_password_instructor(new_password, code_apoge)

    # --- MODIFICATIONS COURS & STRUCTURE ---
    def modify_course_credits(self, title, new_credits):
        return self.course.update_course_(title, new_credits) # Note: typo update_course_ dans votre course.py

    def modify_departement_name(self, old_name, new_name):
        return self.departement.update_departement_name(old_name, new_name)

    def modify_semester_name(self, old_name, new_name):
        return self.semester.update_semester_name(old_name, new_name)

    def modify_salle_capacity(self, code, new_cap):
        return self.salle.update_salle_capacity(code, new_cap)

    # --- MODIFICATIONS SECTION & BLOQUAGE ---
    def modify_section_prof(self, sec_id, prof_id):
        return self.section.update_section_instructor(sec_id, prof_id)

    def modify_section_salle(self, sec_id, salle_id):
        return self.section.update_section_salle(sec_id, salle_id)

    def block_section(self, sec_id):
        return self.section.block_section_enrollment(sec_id)