import cx_Oracle 
from datetime import datetime
import time
import logging

# Gestion des imports (Compatible dossier 'classes' ou racine)
try:
    from classes.app_user import app_user
except ImportError:
    from .app_user import app_user

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
    # 1. ADMIN FEATURES (CRUD)
    # =========================================================
    def select_AllStudent(self):
        """ Récupérer tous les étudiants (Pour Admin Dashboard) """
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM student")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error selecting all students: {e}")
            return []
        finally: 
            cur.close()

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

    def insert_student(self, first_name: str, last_name: str, email: str, academic_lvl: str, password_hash: str):
        """ Créer un nouvel étudiant + Son compte User """
        timestamp = int(time.time())
        code_apoge = f"STD{timestamp}"
        
        # 1. Créer User Login (app_user)
        if not self.app_user_manager.insert_app_user(code_apoge, password_hash, "STUDENT"):
            return False
            
        cur = self.cnn.cursor()
        try: 
            # 2. Créer Student Profile
            cur.execute("""
                INSERT INTO student (code_apoge, first_name, last_name, email, academic_level) 
                VALUES (:1, :2, :3, :4, :5)
            """, (code_apoge, first_name, last_name, email, academic_lvl))
            self.cnn.commit()
            return True 
        except Exception as e:
            self.cnn.rollback()
            # Si échec, on supprime le login créé juste avant
            self.app_user_manager.delete_app_user(code_apoge)
            logging.error(f"Error inserting student {first_name}: {e}")
            return False 
        finally:
            cur.close()

    def deleted_student(self, code_apoge: str):
        """ Supprimer un étudiant et son compte """
        cur = self.cnn.cursor()
        try: 
            cur.execute("DELETE FROM student WHERE code_apoge = :1", (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True 
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error deleting student {code_apoge}: {e}")
            return False 
        finally:
            cur.close()

    # --- Updates (Noms alignés avec AdminService) ---
    def update_email_student(self, new_email, code_apoge):
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

    def update_password_student(self, new_password, code_apoge):
        # Delegate to app_user manager
        return self.app_user_manager.update_app_user_password(code_apoge, new_password)

    def update_academic_level_student(self, new_level, code_apoge):
        """ Met à jour le niveau académique (ex: MASTER, LICENCE) """
        cur = self.cnn.cursor()
        try:
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
            
    # Alias pour compatibilité si besoin
    def modify_password(self, code_apoge, new_pass): return self.update_password_student(new_pass, code_apoge)

    # =========================================================
    # 2. GESTION INSCRIPTION (Student Features)
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
            return []
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
            # Trigger 'trg_check_prerequisites' ou 'capacity' peut lever une erreur ici
            logging.error(f"Error registering {code_apoge} to {section_id}: {e}")
            return False
        finally:
            cur.close()

    def register_to_section(self, code_apoge, section_id):
        # Alias pour compatibilité avec le Service Student
        return self.add_registration(code_apoge, section_id)

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
            return []
        finally:
            cur.close()

    # =========================================================
    # 3. AFFICHAGE DETAILS (Schedule, Info)
    # =========================================================
    def get_my_sections(self, code_apoge):
        """ Show Section by Student (Emploi du temps - v_student_enrollment_extended) """
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
            return []
        finally:
            cur.close()
            
    # Alias pour le Service Student
    def get_my_schedule(self, code_apoge):
        return self.get_my_sections(code_apoge)

    # =========================================================
    # 4. RESULTATS & TRANSCRIPT
    # =========================================================
    def get_student_transcript(self, code_apoge):
        """ Relevé de notes simple """
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
            return []
        finally:
            cur.close()

    def get_transcript_grouped(self, code_apoge):
        """ Relevé de notes groupé par Semestre (Utilisé par le Frontend) """
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM v_student_results_grouped WHERE code_apoge = :1", (code_apoge,))
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Error grouped transcript: {e}")
            return []
        finally:
            cur.close()
    def count_students(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM student")
            res = cur.fetchone()
            return res[0] if res else 0
        except: return 0
        finally: cur.close()