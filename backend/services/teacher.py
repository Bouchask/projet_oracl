import logging

class TeacherService:
    def __init__(self, cnn, instructor_mgr, section_mgr, student_mgr, course_mgr, 
                 prerequisite_mgr, registration_mgr, course_result_mgr, app_user_mgr,
                 departement_mgr, salle_mgr, semester_mgr):
        """
        Service dédié aux opérations de l'enseignant (Teacher).
        Centralise l'accès aux données pour un prof spécifique via son Code Apogée.
        """
        self.cnn = cnn
        self.instructor = instructor_mgr
        self.section = section_mgr
        self.student = student_mgr
        self.course = course_mgr
        self.prerequisite = prerequisite_mgr
        self.registration = registration_mgr
        self.course_result = course_result_mgr
        self.app_user = app_user_mgr
        self.departement = departement_mgr
        self.salle = salle_mgr
        self.semester = semester_mgr

    # =========================================================
    # 1. GESTION PROFIL (Password & Email)
    # =========================================================
    def modify_password(self, code_apoge, new_password):
        return self.app_user.update_app_user_password(code_apoge, new_password)

    def modify_email(self, code_apoge, new_email):
        return self.instructor.update_email_instructor(new_email, code_apoge)

    def show_my_profile(self, code_apoge):
        return self.instructor.select_instructor_By_codeApoge(code_apoge)

    # =========================================================
    # 2. GESTION SECTIONS, SALLES & DEPARTEMENTS
    # =========================================================
    def show_my_sections(self, code_apoge):
        """ Affiche les sections enseignées par ce prof (Cours, Salle, Horaire...) """
        # Utilise la méthode optimisée dans instructor.py
        return self.instructor.get_my_teaching_sections(code_apoge)

    def show_my_department_info(self, code_apoge):
        """ Affiche les infos du département du prof """
        prof_data = self.instructor.select_instructor_By_codeApoge(code_apoge)
        if prof_data:
            # prof_data[0] est le row, colonnes: id, code, name, email, dept_id
            dept_id = prof_data[0][4] 
            # On doit récupérer le nom du département via son ID (Besoin d'une méthode select_by_id dans departement.py ou via Query directe)
            cur = self.cnn.cursor()
            try:
                cur.execute("SELECT * FROM departement WHERE departement_id = :1", (dept_id,))
                return cur.fetchall()
            finally:
                cur.close()
        return None

    def show_section_salle_details(self, code_apoge):
        """ Affiche les détails des salles où le prof enseigne """
        # On récupère les codes salles depuis les sections
        sections = self.instructor.get_my_teaching_sections(code_apoge)
        salles_details = []
        if sections:
            for sec in sections:
                code_salle = sec[3] # Index 3 est salle_code dans la requête get_my_teaching_sections
                details = self.salle.select_salle_by_code(code_salle)
                if details:
                    salles_details.append(details[0])
        # On dédoublonne la liste
        return list(set(salles_details))

    def show_section_semester_details(self, code_apoge):
        """ Affiche les détails des semestres des sections du prof """
        sections = self.instructor.get_my_teaching_sections(code_apoge)
        semesters = []
        if sections:
            for sec in sections:
                sem_name = sec[2] # Index 2 est semester_name
                details = self.semester.select_semester_by_name(sem_name)
                if details:
                    semesters.append(details[0])
        return list(set(semesters))

    # =========================================================
    # 3. COURS & PREREQUIS
    # =========================================================
    def show_my_courses_and_prereqs(self, code_apoge):
        """ Affiche les cours enseignés et leurs pré-requis """
        sections = self.instructor.get_my_teaching_sections(code_apoge)
        courses_info = {}
        
        if sections:
            for sec in sections:
                course_title = sec[1] # Index 1 est course_title
                if course_title not in courses_info:
                    # Récupérer l'objet cours pour avoir l'ID
                    crs = self.course.select_course_by_title(course_title)
                    if crs:
                        course_id = crs[0][0]
                        credits = crs[0][2]
                        # Récupérer pré-requis
                        prereqs = self.prerequisite.select_prerequisites_for_course(course_id)
                        courses_info[course_title] = {
                            "credits": credits,
                            "prerequisites": prereqs # Liste des pré-requis
                        }
        return courses_info

    # =========================================================
    # 4. GESTION ETUDIANTS & INSCRIPTIONS
    # =========================================================
    def show_my_students_list(self, code_apoge):
        """ Affiche la liste des étudiants inscrits dans les sections du prof """
        # Utilise la méthode de instructor.py qui fait déjà les JOINS nécessaires
        return self.instructor.get_students_in_my_sections(code_apoge)

    def show_student_profile(self, student_code_apoge):
        """ Voir le profil complet d'un étudiant spécifique """
        return self.student.select_student_By_codeApoge(student_code_apoge)

    def accept_student_registration(self, registration_id):
        """ Accepter une demande d'inscription (Status -> ACTIVE) """
        return self.registration.update_registration_status(registration_id, 'ACTIVE')

    def cancel_student_registration(self, registration_id):
        """ Refuser/Annuler une inscription (Status -> CANCELLED) """
        return self.registration.update_registration_status(registration_id, 'CANCELLED')

    # =========================================================
    # 5. GESTION DES RESULTATS (NOTES)
    # =========================================================
    def add_student_result(self, student_id, course_code, grade):
        """ Ajouter une note pour un étudiant """
        # course_result.py gère déjà l'insertion. 
        # Le trigger Oracle s'occupera du statut (PASS/NV).
        return self.course_result.insert_course_result(student_id, course_code, grade)

    def modify_student_result(self, result_id, new_grade):
        """ Modifier une note existante """
        return self.course_result.update_course_result_grade(result_id, new_grade)