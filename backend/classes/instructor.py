import cx_Oracle 
import time
import logging

try:
    from classes.app_user import app_user
except ImportError:
    from .app_user import app_user

class instructor: 
    def __init__(self, cnn): 
        self.cnn = cnn 
        self.app_user_manager = app_user(cnn)

    # =========================================================
    # 1. GESTION BASIQUE (CRUD)
    # =========================================================
    def select_all_instructors(self):
        cur = self.cnn.cursor()
        try:
            # Indices: 0=ID, 1=Code, 2=Name, 3=Email, 4=DeptName
            sql = """
                SELECT i.instructor_id, i.code_apoge, i.name, i.email, d.name 
                FROM instructor i
                JOIN departement d ON i.departement_id = d.departement_id
                ORDER BY i.name
            """
            cur.execute(sql)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error select all instructors: {e}")
            return []
        finally: 
            cur.close()

    def select_instructor_By_codeApoge(self, code_apoge): 
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM instructor WHERE code_apoge = :1", (code_apoge,))
            return cur.fetchall()
        finally: 
            cur.close()

    def insert_instructor(self, name, email, dept_id, password_hash):
        timestamp = int(time.time())
        code_apoge = f"PRF{timestamp}"
        
        # 1. Create User
        if not self.app_user_manager.insert_app_user(code_apoge, password_hash, "TEACHER"):
            return False
            
        cur = self.cnn.cursor()
        try: 
            # 2. Create Profile
            cur.execute("""
                INSERT INTO instructor (code_apoge, name, email, departement_id) 
                VALUES (:1, :2, :3, :4)
            """, (code_apoge, name, email, dept_id))
            self.cnn.commit() 
            return True
        except Exception as e: 
            self.cnn.rollback()
            self.app_user_manager.delete_app_user(code_apoge)
            logging.error(f"Error insert instructor: {e}")
            return False
        finally: 
            cur.close()

    def deleted_instructor(self, code_apoge):
        cur = self.cnn.cursor()
        try: 
            cur.execute("DELETE FROM instructor WHERE code_apoge = :1", (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error delete instructor {code_apoge}: {e}")
            return False
        finally: 
            cur.close()

    def update_email_instructor(self, email, code_apoge):
        cur = self.cnn.cursor()
        try: 
            cur.execute("UPDATE instructor SET email = :1 WHERE code_apoge = :2", (email, code_apoge))
            self.cnn.commit()
            return True 
        except Exception as e:
            self.cnn.rollback()
            return False
        finally:
            cur.close()

    def update_departement_instructor(self, dept_id, code_apoge):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE instructor SET departement_id = :1 WHERE code_apoge = :2", (dept_id, code_apoge))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            return False
        finally:
            cur.close()

    # =========================================================
    # 2. METHODES AVANCEES (UTILISATION DES VIEWS)
    # =========================================================
    
    def get_my_teaching_sections(self, code_apoge):
        """ 
        Récupère les sections du prof en utilisant la vue 'v_section_details'.
        Cela simplifie la récupération des noms de cours, salles, et horaires.
        """
        cur = self.cnn.cursor()
        try:
            # On joint la VUE avec les tables SECTION et INSTRUCTOR pour filtrer par code_apoge
            sql = """
                SELECT vs.section_id, vs.course_title, vs.semester_name, vs.salle_code, 
                       vs.day_of_week, vs.start_time, vs.end_time, 
                       vs.current_enrolled, vs.max_capacity
                FROM v_section_details vs
                JOIN section s ON vs.section_id = s.section_id
                JOIN instructor i ON s.instructor_id = i.instructor_id
                WHERE i.code_apoge = :1
                ORDER BY vs.day_of_week, vs.start_time
            """
            cur.execute(sql, (code_apoge,))
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Error get teaching sections: {e}")
            return []
        finally:
            cur.close()

    def get_students_in_my_sections(self, code_apoge):
        """ 
        Récupère la liste des étudiants inscrits chez le prof en utilisant 'v_registration_details'.
        Inclut aussi la note (grade) si elle existe via course_result.
        """
        cur = self.cnn.cursor()
        try:
            sql = """
                SELECT vr.registration_id, vr.first_name, vr.last_name, vr.course_title, vr.status, cr.grade
                FROM v_registration_details vr
                JOIN registration r ON vr.registration_id = r.registration_id
                JOIN section s ON r.section_id = s.section_id
                JOIN instructor i ON s.instructor_id = i.instructor_id
                LEFT JOIN course_result cr ON r.student_id = cr.student_id AND s.course_code = cr.course_code
                WHERE i.code_apoge = :1
                ORDER BY vr.course_title, vr.last_name
            """
            cur.execute(sql, (code_apoge,))
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Error get students for teacher: {e}")
            return []
        finally:
            cur.close()
    def count_instructors(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM instructor")
            res = cur.fetchone()
            return res[0] if res else 0
        except: return 0
        finally: cur.close()
    def update_password_instructor(self, new_password, code_apoge):
        
        return self.app_user_manager.update_app_user_password(code_apoge, new_password)