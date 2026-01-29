import cx_Oracle 
import time
import logging
try: from classes.app_user import app_user
except ImportError: from .app_user import app_user

class student: 
    def __init__(self, cnn): 
        self.cnn = cnn
        self.app_user_manager = app_user(cnn)

    def _get_student_id(self, code_apoge):
        """ Utilise la FONCTION PL/SQL du package ACADEMIC """
        cur = self.cnn.cursor()
        try:
            return cur.callfunc("PKG_ACADEMIC.get_student_id", cx_Oracle.NUMBER, [code_apoge])
        except: return None
        finally: cur.close()

    def insert_student(self, first_name, last_name, email, filiere_id, semester_id, password_hash):
        timestamp = int(time.time())
        code_apoge = f"STD{timestamp}"
        
        if not self.app_user_manager.insert_app_user(code_apoge, password_hash, "STUDENT"): return False
            
        cur = self.cnn.cursor()
        try: 
            cur.execute("""
                INSERT INTO student (code_apoge, first_name, last_name, email, filiere_id, current_semester_id) 
                VALUES (:1, :2, :3, :4, :5, :6)
            """, (code_apoge, first_name, last_name, email, filiere_id, semester_id))
            self.cnn.commit()
            return True 
        except Exception as e:
            self.cnn.rollback()
            self.app_user_manager.delete_app_user(code_apoge)
            logging.error(f"Error insert student: {e}")
            return False 
        finally: cur.close()

    def update_email_student(self, new_email, code_apoge):
        """ Appel PROCEDURE PL/SQL PKG_SECURITY """
        cur = self.cnn.cursor()
        try: 
            cur.callproc("PKG_SECURITY.update_student_email", [code_apoge, new_email])
            return True 
        except Exception as e:
            logging.error(f"Error PKG update email: {e}")
            return False 
        finally: cur.close()

    def select_AllStudent(self):
        cur = self.cnn.cursor()
        try:
            # Jointure pour afficher les noms de filière et semestre
            cur.execute("""
                SELECT s.student_id, s.code_apoge, s.first_name, s.last_name, s.email, f.name, sem.name
                FROM student s
                JOIN filiere f ON s.filiere_id = f.filiere_id
                JOIN semester sem ON s.current_semester_id = sem.semester_id
            """)
            return cur.fetchall()
        finally: cur.close()

    def get_available_sections(self, code_apoge):
        """ Utilise la VUE INTELLIGENTE qui filtre selon la filière de l'étudiant """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT section_id, course_title, credits, instructor_name, code_salle, 
                       day_of_week, start_time, end_time, available_seats
                FROM v_student_eligible_sections
                WHERE code_apoge = :1
                ORDER BY course_title
            """, (code_apoge,))
            return cur.fetchall()
        finally: cur.close()

    def deleted_student(self, code_apoge):
        cur = self.cnn.cursor()
        try: 
            cur.execute("DELETE FROM student WHERE code_apoge = :1", (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True 
        except: 
            self.cnn.rollback()
            return False 
        finally: cur.close()
    # Récupérer l'historique académique via la fonction Oracle
    def get_course_history(self, student_id):
        cur = self.cnn.cursor()
        try:
            # Appel de la fonction stockée Oracle
            ref_cursor = cur.callfunc("get_student_transcript", cx_Oracle.CURSOR, [int(student_id)])
            
            # On récupère toutes les lignes du curseur
            return ref_cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur Transcript (Oracle): {e}")
            return []
        finally:
            cur.close()