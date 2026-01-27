import logging

class StudentService:
    def __init__(self, cnn, student_mgr, section_mgr, registration_mgr, 
                 instructor_mgr, departement_mgr, salle_mgr, course_result_mgr, app_user_mgr):
        """
        Service dédié aux opérations de l'étudiant.
        Il utilise principalement les méthodes 'intelligentes' (JOINs/Views) de student.py
        """
        self.cnn = cnn
        self.student = student_mgr
        self.section = section_mgr
        self.registration = registration_mgr
        self.instructor = instructor_mgr
        self.departement = departement_mgr
        self.salle = salle_mgr
        self.course_result = course_result_mgr
        self.app_user = app_user_mgr

    # =========================================================
    # 1. MON PROFIL
    # =========================================================
    def show_profile(self, code_apoge):
        return self.student.select_student_By_codeApoge(code_apoge)

    def modify_email(self, code_apoge, new_email):
        return self.student.update_email_student(new_email, code_apoge)

    def modify_password(self, code_apoge, new_password):
        return self.app_user.update_app_user_password(code_apoge, new_password)


    # =========================================================
    # 2. INSCRIPTION (S'inscrire aux cours)
    # =========================================================
    def show_available_sections(self):
        """ Affiche la liste des sections disponibles avec places restantes """
        return self.student.get_available_sections()

    def register_to_section(self, code_apoge, section_id):
        """ Tenter de s'inscrire à une section """
        return self.student.add_registration(code_apoge, section_id)

    def cancel_my_registration(self, code_apoge, registration_id):
        """ Annuler une inscription (Status -> CANCELLED) """
        return self.student.cancel_registration(code_apoge, registration_id)

    def show_my_registration_history(self, code_apoge):
        """ Voir l'historique de mes demandes """
        return self.student.get_my_registrations(code_apoge)

    # =========================================================
    # 3. MON EMPLOI DU TEMPS & INFOS COURS
    # =========================================================
    def show_my_schedule(self, code_apoge):
        """ Affiche mes sections actives (Emploi du temps) """
        return self.student.get_my_sections(code_apoge)

    def show_my_teachers(self, code_apoge):
        """ Affiche les profs de mes cours """
        return self.student.get_my_teachers_info(code_apoge)

    def show_my_departments(self, code_apoge):
        """ Affiche les départements liés à mes cours """
        return self.student.get_my_departments(code_apoge)

    def show_my_salles(self, code_apoge):
        """ Affiche les salles où j'ai cours """
        return self.student.get_my_salles(code_apoge)

    # =========================================================
    # 4. MES RESULTATS
    # =========================================================
    def show_transcript(self, code_apoge):
        """ Affiche le relevé de notes simple """
        return self.student.get_student_transcript(code_apoge)
    
    def show_transcript_grouped(self, code_apoge):
        """ Affiche le relevé de notes groupé par semestre (Mieux) """
        # Assurez-vous d'avoir ajouté get_transcript_grouped dans student.py
        if hasattr(self.student, 'get_transcript_grouped'):
            return self.student.get_transcript_grouped(code_apoge)
        else:
            return self.student.get_student_transcript(code_apoge)