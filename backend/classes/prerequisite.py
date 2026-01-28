import cx_Oracle
import logging

class prerequisite:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_prerequisite(self, course_code: int, prereq_code: int, min_grade: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("insert into prerequisite (course_code, prereq_code, min_grade) values (:1, :2, :3)",
                        (course_code, prereq_code, min_grade))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating prerequisite: {e}")
            return False
        finally:
            cur.close()

    def select_prerequisites_for_course(self, course_code: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from prerequisite where course_code = :1", (course_code,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting prerequisites for course {course_code}: {e}")
            return None
        finally:
            cur.close()

    def select_all_prerequisites(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from prerequisite")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all prerequisites: {e}")
            return None
        finally:
            cur.close()

    def update_prerequisite_min_grade(self, course_code: int, prereq_code: int, new_min_grade: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("update prerequisite set min_grade = :1 where course_code = :2 and prereq_code = :3",
                        (new_min_grade, course_code, prereq_code))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating prerequisite: {e}")
            return False
        finally:
            cur.close()

    def delete_prerequisite(self, course_code: int, prereq_code: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from prerequisite where course_code = :1 and prereq_code = :2",
                        (course_code, prereq_code))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting prerequisite: {e}")
            return False
        finally:
            cur.close()
