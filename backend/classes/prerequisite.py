import cx_Oracle
import logging

class prerequisite:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_prerequisite(self, course_code, prereq_code, min_grade):
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO prerequisite (course_code, prereq_code, min_grade) VALUES (:1, :2, :3)",
                        (course_code, prereq_code, min_grade))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert prerequisite: {e}")
            return False
        finally: cur.close()

    def get_prerequisites(self, course_code):
        """ Utilise la FONCTION PL/SQL PKG_PREREQ """
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("PKG_PREREQ.get_course_prereqs", cx_Oracle.CURSOR, [course_code])
            columns = [col[0].lower() for col in ref_cursor.description]
            return [dict(zip(columns, row)) for row in ref_cursor]
        except Exception as e:
            logging.error(f"Error getting prereqs: {e}")
            return []
        finally: cur.close()

    def update_prerequisite(self, course_code, prereq_code, new_min_grade):
        """ Utilise la PROCEDURE PL/SQL PKG_PREREQ """
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_PREREQ.update_prereq", [course_code, prereq_code, new_min_grade])
            return True
        except Exception as e:
            logging.error(f"Error update prereq: {e}")
            return False
        finally: cur.close()

    def delete_prerequisite(self, course_code, prereq_code):
        """ Utilise la PROCEDURE PL/SQL PKG_PREREQ """
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_PREREQ.delete_prereq", [course_code, prereq_code])
            return True
        except Exception as e:
            logging.error(f"Error delete prereq: {e}")
            return False
        finally: cur.close()