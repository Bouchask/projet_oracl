import logging

class TeacherService:
    def __init__(self, cnn, instructor_mgr, course_result_mgr, registration_mgr):
        """
        Service Professeur allégé et puissant grâce aux Packages.
        """
        self.cnn = cnn
        self.instructor = instructor_mgr
        self.course_result = course_result_mgr
        self.registration = registration_mgr

    # =========================================================
    # 1. TABLEAU DE BORD INTELLIGENT (PL/SQL)
    # =========================================================
    def get_dashboard(self, code_apoge):
        """ 
        Retourne la liste des cours avec suivi des heures (Planifié vs Budget).
        Appelle PKG_ACADEMIC.get_teacher_dashboard via instructor.py
        """
        return self.instructor.get_teacher_smart_dashboard(code_apoge)

    def get_my_students(self, section_id):
        """
        Retourne la liste des étudiants d'une section spécifique.
        Appelle PKG_ACADEMIC.get_section_students via instructor.py
        """
        return self.instructor.get_my_section_students(section_id)

    # =========================================================
    # 2. GESTION DES INSCRIPTIONS (Workflow)
    # =========================================================
    def accept_student(self, reg_id):
        return self.registration.validate_registration(reg_id)

    def reject_student(self, reg_id):
        return self.registration.cancel_registration(reg_id)

    def drop_student(self, reg_id):
        """ Bloquer un étudiant (Status DROPPED) """
        return self.registration.drop_registration(reg_id)

    # =========================================================
    # 3. GESTION DES NOTES (PKG_GRADES)
    # =========================================================
    def add_grade(self, student_id, course_code, grade):
        """ 
        Ajoute une note. 
        Le Trigger Oracle calculera auto le status (PASS/FAIL) 
        et validera le semestre si c'est la dernière note.
        """
        return self.course_result.insert_result(student_id, course_code, grade)

    def modify_grade(self, result_id, new_grade):
        return self.course_result.update_result_grade(result_id, new_grade)

    # =========================================================
    # 4. PROFIL
    # =========================================================
    def update_my_email(self, code_apoge, email):
        return self.instructor.update_email_instructor(email, code_apoge)
    
    def update_password(self, code_apoge, pwd):
        return self.instructor.app_user_manager.update_app_user_password(code_apoge, pwd)