import logging
from datetime import datetime

class AdminService:
    def __init__(self, cnn, student_mgr, instructor_mgr, course_mgr, section_mgr, 
                 registration_mgr, departement_mgr, salle_mgr, semester_mgr, 
                 course_result_mgr, prerequisite_mgr, grades_audit_mgr):
        """
        L'AdminService centralise tous les managers pour effectuer les tâches administratives.
        """
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

    # =========================================================
    # 1. GESTION DES ETUDIANTS
    # =========================================================
    def add_student(self, first_name, last_name, email, level, password):
        return self.student.insert_student(first_name, last_name, email, level, password)

    def drop_student(self, code_apoge):
        # Note: Assurez-vous que la méthode s'appelle 'deleted_student' ou 'delete_student' dans votre manager
        return self.student.deleted_student(code_apoge)

    def modify_student_password(self, code_apoge, new_password):
        return self.student.update_password_student(new_password, code_apoge)

    def modify_student_academic_level(self, code_apoge, new_level):
        """ Change le niveau (ex: LICENCE -> MASTER) """
        return self.student.update_academic_level_student(new_level, code_apoge)

    def show_all_students(self):
        return self.student.select_AllStudent()

    # =========================================================
    # 2. GESTION DES PROFESSEURS (Instructors)
    # =========================================================
    def add_instructor(self, name, email, dept_id, password):
        return self.instructor.insert_instructor(name, email, dept_id, password)

    def drop_instructor(self, code_apoge):
        # Vérifiez le nom de la méthode dans instructor.py (deleted_instructor ou delete_instructor)
        return self.instructor.deleted_instructor(code_apoge)

    def modify_instructor_dept(self, code_apoge, new_dept_id):
        return self.instructor.update_departement_instructor(new_dept_id, code_apoge)

    # =========================================================
    # 3. GESTION DES SECTIONS (Emploi du temps)
    # =========================================================
    def show_sections(self):
        return self.section.get_all_section_details()

    def add_section(self, course_code, semester_id, instructor_id, salle_id, capacity, day, start, end):
        return self.section.insert_section(course_code, semester_id, instructor_id, salle_id, capacity, day, start, end)

    def drop_section(self, section_id):
        return self.section.delete_section(section_id)

    # Mise à jour granulaire (Une seule info à la fois)
    def update_section_instructor(self, section_id, new_instructor_id):
        return self.section.update_section_instructor(section_id, new_instructor_id)

    def update_section_salle(self, section_id, new_salle_id):
        return self.section.update_section_salle(section_id, new_salle_id)

    def update_section_time(self, section_id, new_start, new_end):
        return self.section.update_section_time(section_id, new_start, new_end)

    # =========================================================
    # 4. GESTION DES INSCRIPTIONS (Registration)
    # =========================================================
    def show_registrations(self):
        return self.registration.get_all_registration_details()

    def accept_registration(self, registration_id):
        return self.registration.update_registration_status(registration_id, 'ACTIVE')

    def cancel_registration(self, registration_id):
        return self.registration.update_registration_status(registration_id, 'CANCELLED')

    # =========================================================
    # 5. GESTION COURS & PREREQUIS
    # =========================================================
    def add_course(self, title, credits):
        return self.course.insert_course(title, credits)

    def drop_course(self, title):
        return self.course.delete_course(title)

    def add_prerequisite(self, course_code, prereq_code, min_grade):
        return self.prerequisite.insert_prerequisite(course_code, prereq_code, min_grade)

    # =========================================================
    # 6. GESTION SALLES & DEPARTEMENTS & SEMESTRES
    # =========================================================
    def add_salle(self, code, capacity, building):
        return self.salle.insert_salle(code, capacity, building)

    def add_departement(self, name):
        return self.departement.insert_departement(name)
        
    def add_semester(self, name, start, end):
        return self.semester.insert_semester(name, start, end)

    # =========================================================
    # 7. GESTION RESULTATS & AUDIT
    # =========================================================
    def show_audit_logs(self):
        """ Affiche l'historique des modifications de notes """
        # Assurez-vous d'avoir ajouté select_audit_details dans grades_audit.py
        if hasattr(self.grades_audit, 'select_audit_details'):
            return self.grades_audit.select_audit_details()
        else:
            return self.grades_audit.select_all_audits()

    def modify_student_grade(self, result_id, new_grade):
        return self.course_result.update_course_result_grade(result_id, new_grade)