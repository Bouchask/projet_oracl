import logging

class StudentService:
    def __init__(self, cnn, student_mgr, registration_mgr, course_result_mgr):
        self.cnn = cnn
        self.student = student_mgr
        self.registration = registration_mgr
        self.course_result = course_result_mgr

    # =========================================================
    # 1. INSCRIPTION INTELLIGENTE
    # =========================================================
    def get_available_courses(self, code_apoge):
        """ 
        Affiche UNIQUEMENT les cours valides pour la filière/semestre de l'étudiant.
        Utilise la vue 'v_student_eligible_sections'.
        """
        return self.student.get_available_sections(code_apoge)

    def register_course(self, code_apoge, section_id):
        """ S'inscrire (Status sera PENDING par défaut via Trigger) """
        # Récupérer l'ID interne via PL/SQL
        std_id = self.student._get_student_id(code_apoge)
        if not std_id: return False
        
        return self.registration.insert_registration(std_id, section_id)

    def cancel_request(self, reg_id):
        """ Annuler sa propre demande """
        # L'étudiant peut utiliser la procédure cancel_reg du package
        return self.registration.cancel_registration(reg_id)

    # =========================================================
    # 2. RESULTATS (Transcript)
    # =========================================================
    def view_grades(self, code_apoge):
        """ 
        Voir ses notes et résultats.
        Utilise PKG_GRADES.get_student_transcript
        """
        std_id = self.student._get_student_id(code_apoge)
        if not std_id: return []
        return self.course_result.get_student_results(std_id)

    # =========================================================
    # 3. PROFIL
    # =========================================================
    def update_email(self, code_apoge, new_email):
        return self.student.update_email_student(new_email, code_apoge)

    def update_password(self, code_apoge, new_pwd):
        return self.student.app_user_manager.update_app_user_password(code_apoge, new_pwd)