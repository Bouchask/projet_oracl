import cx_Oracle 
from datetime import datetime
import time
import logging
from app_user import app_user

class student : 
    def __init__(self , cnn) : 
        self.cnn = cnn
        self.app_user_manager = app_user(cnn)

    def select_student_By_codeApoge(self,code_apoge): 
        cur = self.cnn.cursor()
        try :
            cur.execute("select * from student where code_apoge = :1" ,(code_apoge,))
            rows = cur.fetchall()
            return rows 
        except Exception as e :
            logging.error(f"error in select student {code_apoge} : {e} ")
            return None
        finally : 
            cur.close()

    def select_AllStudent(self):
        cur = self.cnn.cursor()
        try :
            cur.execute(f"select * from student ")
            rows = cur.fetchall()
            return rows
        except Exception as e :
            logging.error(f"error in select all student : {e}")
            return None
        finally : 
            cur.close()

    def insert_student(self, first_name: str, last_name: str, email: str, academic_lvl: str, password_hash: str):
        timestamp = int(time.time())
        code_apoge = f"STD{timestamp}"
        enrollment_date = datetime.now()
        cur = self.cnn.cursor()
        user_created = False 
        
        try:
            if not self.app_user_manager.insert_app_user(code_apoge, password_hash, "STUDENT"):
                return False
            user_created = True

            cur.execute("insert into student(code_apoge, first_name, last_name, email, academic_level, enrollment_date) values (:1, :2, :3, :4, :5, :6)", 
                        (code_apoge, first_name, last_name, email, academic_lvl, enrollment_date))
            self.cnn.commit()
            return True
            
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"error in insert student : {e}")
            if user_created:
                self.app_user_manager.delete_app_user(code_apoge)
                logging.info(f"Rolled back app_user {code_apoge} due to student insertion failure.")
                
            return False
        finally:
            cur.close()

    def update_academic_level_student(self , academic_level : str  , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("update student set academic_level = :1 where code_apoge = :2" , (academic_level , code_apoge))
            self.cnn.commit()
            return True 
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error in update academic level for student {code_apoge} : {e} ")
            return False
        finally : 
            cur.close()

    def update_email_student(self,email : str , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("update student set email = :1 where code_apoge = :2" , (email , code_apoge))
            self.cnn.commit()
            return True 
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error in update email for student {code_apoge} : {e}")
            return False 
        finally :
            cur.close()

    def update_password_student (self , password_hash : str ,  code_apoge : str):
        return self.app_user_manager.update_app_user_password(code_apoge, password_hash)

    def deleted_student(self , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("delete from student where code_apoge = :1" , (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error  in delet user {code_apoge} : {e}")
            return False
        finally : 
            cur.close()
    def get_student_transcript(self, code_apoge: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT course_title, credits, grade, status 
                FROM v_student_transcript 
                WHERE code_apoge = :1
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error fetching transcript: {e}")
            return None
        finally:
            cur.close()