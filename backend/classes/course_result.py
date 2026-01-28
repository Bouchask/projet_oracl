import cx_Oracle
import logging

class course_result:
    def __init__(self, cnn):
        self.cnn = cnn

   
    def insert_course_result(self, student_id: int, course_code: int, grade: str):
        cur = self.cnn.cursor()
        try:
            # Oracle Trigger will set status (PASS/NV) based on grade
            cur.execute("insert into course_result (student_id, course_code, grade) values (:1, :2, :3)",
                        (student_id, course_code, grade))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating course result: {e}")
            return False
        finally:
            cur.close()

    def select_course_result_by_id(self, result_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from course_result where result_id = :1", (result_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting course result {result_id}: {e}")
            return None
        finally:
            cur.close()

    def select_course_results_by_student(self, student_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from course_result where student_id = :1", (student_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting course results for student {student_id}: {e}")
            return None
        finally:
            cur.close()

    def select_all_course_results(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from course_result")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all course results: {e}")
            return None
        finally:
            cur.close()

    
    def update_course_result_grade(self, result_id: int, new_grade: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("update course_result set grade = :1 where result_id = :2",
                        (new_grade, result_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating course result {result_id}: {e}")
            return False
        finally:
            cur.close()

    def delete_course_result(self, result_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from course_result where result_id = :1", (result_id,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting course result {result_id}: {e}")
            return False
        finally:
            cur.close()