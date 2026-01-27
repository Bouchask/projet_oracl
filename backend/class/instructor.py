import cx_Oracle 
from datetime import datetime
import time
import logging

from app_user import app_user

class instructor : 
    def __init__(self , cnn) : 
        self.cnn = cnn 
        self.app_user_manager = app_user(cnn)

    def select_instructor_By_codeApoge(self,code_apoge): 
        cur = self.cnn.cursor()
        try :
            cur.execute("select * from instructor where code_apoge = :1" ,(code_apoge,))
            rows = cur.fetchall()
            return rows 
        except Exception as e :
            logging.error(f"error in select instructor {code_apoge} : {e} ")
            return None
        finally : 
            cur.close()

    def select_Allinstructor(self):
        cur = self.cnn.cursor()
        try :
            cur.execute(f"select * from instructor ")
            rows = cur.fetchall()
            return rows
        except Exception as e :
            logging.error(f"error in select all instructor : {e}")
            return None
        finally : 
            cur.close()

    def insert_instructor(self , name : str, email : str , departement_id : int , password_hash ):
        timestamp = int(time.time())
        code_apoge = f"INS{timestamp}"
        cur = self.cnn.cursor()
        try : 
            self.app_user_manager.insert_app_user(code_apoge, password_hash, "TEACHER")
            cur.execute("insert into instructor(code_apoge ,name , email , departement_id ) values (:1, :2, :3, :4)" , (code_apoge ,name , email  , departement_id ))
            self.cnn.commit() 
            return True
        except Exception as e : 
            self.cnn.rollback()
            logging.error(f"error in insert instructor : {e}")
            return False
        finally : 
            cur.close()

    def update_departement_instructor(self , departement_id : str  , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("update instructor set departement_id = :1 where code_apoge = :2" , (departement_id , code_apoge))
            self.cnn.commit()
            return True 
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error in update academic level for instructor {code_apoge} : {e} ")
            return False
        finally : 
            cur.close()

    def update_email_instructor(self,email : str , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("update instructor set email = :1 where code_apoge = :2" , (email , code_apoge))
            self.cnn.commit()
            return True 
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error in update email for instructor {code_apoge} : {e}")
            return False 
        finally :
            cur.close()

    def update_password_instructor (self , password_hash : str ,  code_apoge : str):
        return self.app_user_manager.update_app_user_password(code_apoge, password_hash)

    def deleted_instructor(self , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("delete from instructor where code_apoge = :1" , (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error  in delet user {code_apoge} : {e}")
            return False
        finally : 
            cur.close()
    