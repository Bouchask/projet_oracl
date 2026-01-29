import cx_Oracle
import logging

class course:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_course(self, title, credits, filiere_id, semester_id, total_hours=40):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                INSERT INTO course (title, credits, filiere_id, semester_id, total_hours) 
                VALUES (:1, :2, :3, :4, :5)
            """, (title, credits, filiere_id, semester_id, total_hours))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert course: {e}")
            return False
        finally: cur.close()

    def select_all_courses(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT c.course_code, c.title, c.credits, f.name, s.name, c.total_hours
                FROM course c
                JOIN filiere f ON c.filiere_id = f.filiere_id
                JOIN semester s ON c.semester_id = s.semester_id
                ORDER BY f.name, s.name
            """)
            return cur.fetchall()
        finally: cur.close()

    def delete_course(self, title):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM course WHERE title = :1", (title,))
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()
        
    def update_course_(self, title, new_credits):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE course SET credits = :1 WHERE title = :2", (new_credits, title))
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()
    # Récupérer les détails et sections d'un cours
    def get_course_sections(self, course_code):
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("get_course_sections_details", cx_Oracle.CURSOR, [int(course_code)])
            return ref_cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur Course Sections: {e}")
            return []
        finally:
            cur.close()