import cx_Oracle
import logging
from classes.course import course
from classes.course_result import course_result

class registration:
    def __init__(self, cnn):
        self.cnn = cnn
        self.course_manager = course(cnn)
        self.course_result_manager = course_result(cnn)

    def insert_registration(self, student_id: int, section_id: int):
        cur = self.cnn.cursor()
        try:
            status = 'ACTIVE' 
            
            cur.execute("insert into registration (student_id, section_id, status) values (:1, :2, :3)",
                        (student_id, section_id, status))
            self.cnn.commit()
            return True
            
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self.cnn.rollback()
            
            if error.code == 20040:
                logging.warning(f"Registration failed: Prerequisites not met for student {student_id}")
            else:
                logging.error(f"Database error: {e}")
            return False
            
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"General error: {e}")
            return False
        finally:
            cur.close()

    def select_registration_by_id(self, registration_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from registration where registration_id = :1", (registration_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting registration {registration_id}: {e}")
            return None
        finally:
            cur.close()

    def select_registrations_by_student(self, student_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from registration where student_id = :1", (student_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting registrations for student {student_id}: {e}")
            return None
        finally:
            cur.close()

    def select_all_registrations(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from registration")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all registrations: {e}")
            return None
        finally:
            cur.close()

    def update_registration_status(self, registration_id: int, new_status: str):
        cur = self.cnn.cursor()
        try:
            if new_status not in ['ACTIVE', 'DROPPED', 'CANCELLED']:
                raise ValueError("Invalid status. Allowed values are 'ACTIVE', 'DROPPED', 'CANCELLED'.")
            
            cur.execute("update registration set status = :1 where registration_id = :2",
                        (new_status, registration_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating registration {registration_id}: {e}")
            return False
        finally:
            cur.close()

    def get_all_registration_details(self):
        cur = self.cnn.cursor()
        try:
           
            cur.execute("""
                SELECT first_name, last_name, course_title, status 
                FROM v_registration_details
            """)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in getting all registration details: {e}")
            return None
        finally:
            cur.close()

    def get_registration_details(self, registration_id: int):
        cur = self.cnn.cursor()
        try:
            
            cur.execute("""
                SELECT first_name, last_name, course_title, status 
                FROM v_registration_details 
                WHERE registration_id = :1
            """, (registration_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in getting registration details {registration_id}: {e}")
            return None
        finally:
            cur.close()

    def delete_registration(self, registration_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from registration where registration_id = :1", (registration_id,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting registration {registration_id}: {e}")
            return False
        finally:
            cur.close()
