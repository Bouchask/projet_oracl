import cx_Oracle
import logging

class course_result:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_result(self, student_id, course_code, grade):
        """ Insertion directe (Les triggers s'occupent de la validation) """
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO course_result (student_id, course_code, grade) VALUES (:1, :2, :3)", 
                        (student_id, course_code, grade))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert result: {e}")
            return False
        finally: cur.close()

    def get_student_results(self, student_id):
        """ Utilise la FONCTION PL/SQL PKG_GRADES """
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("PKG_GRADES.get_student_transcript", cx_Oracle.CURSOR, [student_id])
            columns = [col[0].lower() for col in ref_cursor.description]
            return [dict(zip(columns, row)) for row in ref_cursor]
        except Exception as e:
            logging.error(f"Error getting results: {e}")
            return []
        finally: cur.close()

    def update_result_grade(self, result_id, new_grade):
        """ Utilise la PROCEDURE PL/SQL PKG_GRADES """
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_GRADES.update_grade", [result_id, new_grade])
            return True
        except Exception as e:
            logging.error(f"Error updating grade: {e}")
            return False
        finally: cur.close()

    def delete_result(self, result_id):
        """ Utilise la PROCEDURE PL/SQL PKG_GRADES """
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_GRADES.delete_result", [result_id])
            return True
        except Exception as e:
            logging.error(f"Error deleting result: {e}")
            return False
        finally: cur.close()