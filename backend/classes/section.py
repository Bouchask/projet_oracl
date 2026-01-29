import cx_Oracle
import logging

class section:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_section(self, course_code, instructor_id, salle_id, capacity, day, start, end):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                INSERT INTO section (course_code, instructor_id, salle_id, max_capacity, day_of_week, start_time, end_time) 
                VALUES (:1, :2, :3, :4, :5, :6, :7)
            """, (course_code, instructor_id, salle_id, capacity, day, start, end))
            self.cnn.commit()
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self.cnn.rollback()
            logging.error(f"Erreur Insert Section: {error.message}")
            return False
        finally: cur.close()

    def get_all_section_details(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM v_section_details ORDER BY filiere_name, semester_name")
            return cur.fetchall()
        finally: cur.close()

    def delete_section(self, sid):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM section WHERE section_id = :1", (sid,))
            self.cnn.commit()
            return True
        except Exception as e:
            logging.error(f"Erreur Delete Section: {e}")
            return False
        finally: cur.close()
        
    # --- CORRECTION ICI ---
    def block_section_enrollment(self, section_id):
        cur = self.cnn.cursor()
        try:
            # 1. On compte d'abord le nombre d'inscrits réels (ACTIVE ou VALIDE)
            cur.execute("""
                SELECT COUNT(*) FROM registration 
                WHERE section_id = :1 AND status IN ('ACTIVE', 'VALIDE')
            """, (section_id,))
            
            count_result = cur.fetchone()
            current_enrolled = count_result[0] if count_result else 0
            
            # 2. On met à jour la capacité avec ce nombre
            cur.execute("""
                UPDATE section 
                SET max_capacity = :1 
                WHERE section_id = :2
            """, (current_enrolled, section_id))
            
            self.cnn.commit()
            return True
            
        except cx_Oracle.DatabaseError as e: 
            error, = e.args
            self.cnn.rollback()
            logging.error(f"Erreur Block Section SQL: {error.message}") # Affiche l'erreur réelle
            return False
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Erreur Block Section: {e}")
            return False
        finally: cur.close()
        
    def update_section_instructor(self, sid, pid):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE section SET instructor_id = :1 WHERE section_id = :2", (pid, sid))
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()

    def update_section_salle(self, sid, salid):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE section SET salle_id = :1 WHERE section_id = :2", (salid, sid))
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()