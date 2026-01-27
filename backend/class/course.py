import cx_Oracle
import logging
from prerequisite import prerequisite
class course:
    def __init__(self, cnn):
        self.cnn = cnn
        self.prerequisite = prerequisite(cnn)

    def insert_course(self, title: str, credits: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("insert into course (title, credits) values (:1, :2)",
                        (title, credits))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating course {title}: {e}")
            return False
        finally:
            cur.close()

    def select_course_by_title(self, title: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from course where title = :1", (title,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting course {title}: {e}")
            return None
        finally:
            cur.close()

    def select_all_courses(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from course")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all courses: {e}")
            return None
        finally:
            cur.close()

    def update_course_(self, title: str, new_credits: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("update course set credits = :1 where title = :2",
                        (new_credits, title))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating course {title}: {e}")
            return False
        finally:
            cur.close()

    def delete_course(self, title: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from course where title = :1", (title,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting course {title}: {e}")
            return False
        finally:
            cur.close()
    def update_prerequisite_grade_Cour(self , id_cours : int , id_prerequisite : str , new_grade : str):
        rs = self.prerequisite.update_prerequisite_min_grade(id_cours , id_prerequisite , new_grade)
        if rs : 
            return True 
        else : 
            return False 
    def delete_prerequisite_cours(self,id_cours  : str, id_prerequisite : str):
        rs  = self.prerequisite.delete_prerequisite(id_cours , id_prerequisite)
        if rs : 
            return True
        else : 
            return False 
    def update_prerequisite_cours(self , id_old_prerequisite : int ,id_cours : int , id_cours_prerequisite : int , grade : str) : 
        rs   = self.prerequisite.delete_prerequisite(id_cours , id_old_prerequisite)
        if rs : 
            rsi = self.prerequisite.insert_prerequisite(id_cours , id_cours_prerequisite , grade)
            if rsi : 
                return True 
            else : 
                return False
        else : 
            return False
