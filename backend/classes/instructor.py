import cx_Oracle 
import time
import logging
try: from classes.app_user import app_user
except ImportError: from .app_user import app_user

class instructor: 
    def __init__(self, cnn): 
        self.cnn = cnn 
        self.app_user_manager = app_user(cnn)

    def insert_instructor(self, name, email, dept_id, password_hash):
        timestamp = int(time.time())
        code_apoge = f"PRF{timestamp}"
        
        if not self.app_user_manager.insert_app_user(code_apoge, password_hash, "TEACHER"): return False
            
        cur = self.cnn.cursor()
        try: 
            cur.execute("INSERT INTO instructor (code_apoge, name, email, departement_id) VALUES (:1, :2, :3, :4)", 
                        (code_apoge, name, email, dept_id))
            self.cnn.commit() 
            return True
        except Exception as e: 
            self.cnn.rollback()
            self.app_user_manager.delete_app_user(code_apoge)
            return False
        finally: cur.close()

    def update_email_instructor(self, email, code_apoge):
        cur = self.cnn.cursor()
        try: 
            cur.callproc("PKG_SECURITY.update_teacher_email", [code_apoge, email])
            return True 
        except: return False
        finally: cur.close()

    def select_all_instructors(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT i.instructor_id, i.code_apoge, i.name, i.email, d.name 
                FROM instructor i JOIN departement d ON i.departement_id = d.departement_id
                ORDER BY i.name
            """)
            return cur.fetchall()
        finally: cur.close()

    # --- PL/SQL INTELLIGENT ---
    def get_teacher_smart_dashboard(self, code_apoge):
        """ Appelle FUNCTION PL/SQL qui retourne un CURSOR """
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("PKG_ACADEMIC.get_teacher_dashboard", cx_Oracle.CURSOR, [code_apoge])
            columns = [col[0].lower() for col in ref_cursor.description]
            return [dict(zip(columns, row)) for row in ref_cursor]
        except Exception as e:
            logging.error(f"Error teacher dashboard: {e}")
            return []
        finally: cur.close()

    def get_my_section_students(self, section_id):
        """ Appelle FUNCTION PL/SQL pour la liste de classe """
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("PKG_ACADEMIC.get_section_students", cx_Oracle.CURSOR, [section_id])
            columns = [col[0].lower() for col in ref_cursor.description]
            return [dict(zip(columns, row)) for row in ref_cursor]
        except Exception as e:
            logging.error(f"Error section students: {e}")
            return []
        finally: cur.close()
        
    def deleted_instructor(self, code_apoge):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM instructor WHERE code_apoge = :1", (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()
    # Récupérer l'emploi du temps détaillé
    def get_schedule_details(self, instructor_id):
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("get_teacher_schedule_details", cx_Oracle.CURSOR, [int(instructor_id)])
            return ref_cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur Schedule Prof: {e}")
            return []
        finally:
            cur.close()
    # Récupérer le département actuel (Via Fonction)
    def get_current_dept(self, instructor_id):
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("get_instructor_dept_info", cx_Oracle.CURSOR, [int(instructor_id)])
            return ref_cursor.fetchone() # On attend une seule ligne (1 prof = 1 dept)
        except Exception as e:
            return None
        finally:
            cur.close()

    # Changer le département (Update simple)
   # Changer le département (Via Procédure Oracle)
    def update_department(self, instructor_id, new_dept_id):
        cur = self.cnn.cursor()
        try:
            # Appel de la procédure stockée 'update_instructor_dept'
            cur.callproc("update_instructor_dept", [int(instructor_id), int(new_dept_id)])
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            logging.error(f"Erreur Oracle Update Dept: {error.message}")
            return False
        except Exception as e:
            logging.error(f"Erreur Update Dept: {e}")
            return False
        finally:
            cur.close()