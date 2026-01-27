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
        
        user_created = False
        
        try : 
            if not self.app_user_manager.insert_app_user(code_apoge, password_hash, "TEACHER"):
                return False
            user_created = True

            cur.execute("insert into instructor(code_apoge ,name , email , departement_id ) values (:1, :2, :3, :4)" , (code_apoge ,name , email  , departement_id ))
            self.cnn.commit() 
            return True
            
        except Exception as e : 
            self.cnn.rollback()
            logging.error(f"error in insert instructor : {e}")
            
            if user_created:
                self.app_user_manager.delete_app_user(code_apoge)
                logging.info(f"Rolled back app_user {code_apoge} due to instructor insertion failure.")
                
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

    def delete_instructor(self , code_apoge : str):
        cur = self.cnn.cursor()
        try : 
            cur.execute("delete from instructor where code_apoge = :1" , (code_apoge,))
            self.app_user_manager.delete_app_user(code_apoge)
            self.cnn.commit()
            return True
        except Exception as e :
            self.cnn.rollback()
            logging.error(f"error in delete user {code_apoge} : {e}")
            return False
        finally : 
            cur.close()

    # --- NEW METHODS ---

    def get_my_teaching_sections(self, code_apoge: str):
        """ Retrieves details of sections taught by THIS instructor. """
        cur = self.cnn.cursor()
        try:
            # Join v_section_details with section -> instructor table to filter by code_apoge
            cur.execute("""
                SELECT vs.section_id, vs.course_title, vs.semester_name, vs.salle_code, 
                       vs.day_of_week, vs.start_time, vs.end_time, vs.current_enrolled, vs.max_capacity
                FROM v_section_details vs
                JOIN section s ON vs.section_id = s.section_id
                JOIN instructor i ON s.instructor_id = i.instructor_id
                WHERE i.code_apoge = :1
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting teaching sections for instructor {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    def get_students_in_my_sections(self, code_apoge: str):
        """ Retrieves registration details for students enrolled in THIS instructor's sections. """
        cur = self.cnn.cursor()
        try:
            # Join views/tables to link Registration -> Section -> Instructor
            cur.execute("""
                SELECT vr.registration_id, vr.first_name, vr.last_name, vr.course_title, vr.status
                FROM v_registration_details vr
                JOIN registration r ON vr.registration_id = r.registration_id
                JOIN section s ON r.section_id = s.section_id
                JOIN instructor i ON s.instructor_id = i.instructor_id
                WHERE i.code_apoge = :1
            """, (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error getting student registrations for instructor {code_apoge}: {e}")
            return None
        finally:
            cur.close()