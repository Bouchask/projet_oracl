import cx_Oracle 
from datetime import datetime
import time
import logging
from app_user import app_user

class student: 
    def __init__(self, cnn): 
        self.cnn = cnn
        self.app_user_manager = app_user(cnn)

    # =========================================================
    # 0. HELPER: Get ID by Code
    # =========================================================
    def _get_student_id(self, code_apoge):
        """ Private helper to get ID from Code Apoge """
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT student_id FROM student WHERE code_apoge = :1", (code_apoge,))
            res = cur.fetchone()
            return res[0] if res else None
        finally:
            cur.close()

    # =========================================================
    # 1. GESTION PROFIL (Base)
    # =========================================================
    def select_student_By_codeApoge(self, code_apoge): 
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM student WHERE code_apoge = :1", (code_apoge,))
            rows = cur.fetchall()
            return rows 
        except Exception as e:
            logging.error(f"Error selecting student {code_apoge}: {e}")
            return None
        finally: 
            cur.close()

    def modify_email(self, code_apoge, new_email):
        cur = self.cnn.cursor()
        try: 
            cur.execute("UPDATE student SET email = :1 WHERE code_apoge = :2", (new_email, code_apoge))
            self.cnn.commit()
            return True 
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error updating email for {code_apoge}: {e}")
            return False 
        finally:
            cur.close()

    def modify_password(self, code_apoge, new_password):
        # Delegate to app_user manager
        return self.app_user_manager.update_app_user_password(code_apoge, new_password)

    # =========================================================
    # 2. GESTION INSCRIPTION (Registration)
    # =========================================================
    def get_available_sections(self):
        """ Show List Section (Pour s'inscrire) """
        cur = self.cnn.cursor()
        try:
            # On utilise v_section_capacity pour voir les places dispo
            cur.execute("""
                SELECT section_id, title, code_salle, max_capacity, current_enrolled, available_seats 
                FROM v_section_capacity 
                WHERE available_seats > 0
                ORDER BY title
            """)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting available sections: {e}")
            return None
        finally:
            cur.close()

    def add_registration(self, code_apoge, section_id):
        """ Ajouter Registration """
        sid = self._get_student_id(code_apoge)
        if not sid: return False

        cur = self.cnn.cursor()
        try:
            # Status par défaut ACTIVE
            cur.execute("INSERT INTO registration (student_id, section_id, status) VALUES (:1, :2, 'ACTIVE')",
                        (sid, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            # On log l'erreur (Trigger prerequisites va lever une erreur ici si pas validé)
            logging.error(f"Error registering {code_apoge} to {section_id}: {e}")
            return False
        finally:
            cur.close()

    def cancel_registration(self, code_apoge, registration_id):
        """ Cancelled Registration (Soft delete via Status) """
        sid = self._get_student_id(code_apoge)
        cur = self.cnn.cursor()
        try:
            # Vérifie que la registration appartient bien à l'étudiant
            cur.execute("""
                UPDATE registration 
                SET status = 'CANCELLED' 
                WHERE registration_id = :1 AND student_id = :2
            """, (registration_id, sid))
            
            if cur.rowcount > 0:
                self.cnn.commit()
                return True
            return False
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error cancelling registration {registration_id}: {e}")
            return False
        finally:
            cur.close()

    def get_my_registrations(self, code_apoge):
        """ Show List Registration by Student """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT vr.registration_id, vr.course_title, vr.status, vr.registration_date
                FROM v_registration_details vr
                JOIN student s ON vr.student_id = s.student_id
                WHERE s.code_apoge = :1
                ORDER BY vr.registration_date DESC
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting registrations for {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    # =========================================================
    # 3. AFFICHAGE DETAILS (Section, Teacher, Dept, Salle)
    # =========================================================
    def get_my_sections(self, code_apoge):
        """ Show Section by Student (Emploi du temps) """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT course_title, day_of_week, start_time, end_time, code_salle, salle_building
                FROM v_student_enrollment_extended
                WHERE code_apoge = :1 AND registration_status = 'ACTIVE'
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting sections for {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    def get_my_teachers_info(self, code_apoge):
        """ Show Profil Teacher Section by Student """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT course_title, instructor_name, instructor_email
                FROM v_student_enrollment_extended
                WHERE code_apoge = :1 AND registration_status = 'ACTIVE'
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting teachers for {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    def get_my_departments(self, code_apoge):
        """ Show Departement by Section by Student """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT course_title, departement_name
                FROM v_student_enrollment_extended
                WHERE code_apoge = :1 AND registration_status = 'ACTIVE'
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting departments for {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    def get_my_salles(self, code_apoge):
        """ Show Salle by Section by Student """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT DISTINCT course_title, code_salle, salle_building
                FROM v_student_enrollment_extended
                WHERE code_apoge = :1 AND registration_status = 'ACTIVE'
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting salles for {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    # =========================================================
    # 4. RESULTATS
    # =========================================================
    def get_student_transcript(self, code_apoge):
        """ Show Cours Result (Relevé de notes) """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT course_title, credits, grade, status 
                FROM v_student_transcript 
                WHERE code_apoge = :1
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting transcript for {code_apoge}: {e}")
            return None
        finally:
            cur.close()
    def update_academic_level(self, code_apoge, new_level):
        """ Met à jour le niveau académique (ex: MASTER, LICENCE) """
        cur = self.cnn.cursor()
        try:
            # Oracle va vérifier la contrainte CHECK (LICENCE, MASTER, etc.)
            cur.execute("UPDATE student SET academic_level = :1 WHERE code_apoge = :2", 
                        (new_level, code_apoge))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error updating academic level for {code_apoge}: {e}")
            return False
        finally:
            cur.close()