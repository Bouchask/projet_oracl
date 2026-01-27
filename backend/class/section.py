import cx_Oracle
from datetime import datetime
import logging

class section:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_section(self, course_code: int, semester_id: int, instructor_id: int, salle_id: int, max_capacity: int, day_of_week: str, start_time: datetime, end_time: datetime):
        cur = self.cnn.cursor()
        try:
            cur.execute("insert into section (course_code, semester_id, instructor_id, salle_id, max_capacity, day_of_week, start_time, end_time) values (:1, :2, :3, :4, :5, :6, :7, :8)",
                        (course_code, semester_id, instructor_id, salle_id, max_capacity, day_of_week, start_time, end_time))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating section: {e}")
            return False
        finally:
            cur.close()

    def select_section_by_id(self, section_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from section where section_id = :1", (section_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting section {section_id}: {e}")
            return None
        finally:
            cur.close()

    def select_all_sections(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from section")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all sections: {e}")
            return None
        finally:
            cur.close()

    def update_section(self, section_id: int, new_instructor_id: int, new_salle_id: int, new_max_capacity: int, new_day_of_week: str, new_start_time: datetime, new_end_time: datetime):
        cur = self.cnn.cursor()
        try:
            cur.execute("update section set instructor_id = :1, salle_id = :2, max_capacity = :3, day_of_week = :4, start_time = :5, end_time = :6 where section_id = :7",
                        (new_instructor_id, new_salle_id, new_max_capacity, new_day_of_week, new_start_time, new_end_time, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating section {section_id}: {e}")
            return False
        finally:
            cur.close()
    def update_section_salle(self, section_id: int, new_salle_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("update section set salle_id = :1 where section_id = :2",
                        (new_salle_id, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating section salle {section_id}: {e}")
            return False
        finally:
            cur.close()
    def update_section_instructor(self, section_id: int, new_instructor_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("update section set instructor_id = :1 where section_id = :2",
                        (new_instructor_id, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating section instructor {section_id}: {e}")
            return False
        finally:
            cur.close()
    def update_section_time(self, section_id: int, new_start_time: datetime, new_end_time: datetime):
        cur = self.cnn.cursor()
        try:
            cur.execute("update section set start_time = :1, end_time = :2 where section_id = :3",
                        (new_start_time, new_end_time, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating section time {section_id}: {e}")
            return False
        finally:
            cur.close()
    def update_section_day(self, section_id: int, new_day_of_week: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("update section set day_of_week = :1 where section_id = :2",
                        (new_day_of_week, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating section day {section_id}: {e}")
            return False
        finally:
            cur.close()
    def update_section_max_capacity(self, section_id: int, new_max_capacity: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("update section set max_capacity = :1 where section_id = :2",
                        (new_max_capacity, section_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating section max capacity {section_id}: {e}")
            return False
        finally:
            cur.close()
    def get_all_section_details(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT course_title, semester_name, instructor_name, salle_code, 
                       day_of_week, start_time, end_time, max_capacity 
                FROM v_section_details
            """)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in getting all section details: {e}")
            return None
        finally:
            cur.close()

    def get_section_details(self, section_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT course_title, semester_name, instructor_name, salle_code, 
                       day_of_week, start_time, end_time, max_capacity 
                FROM v_section_details 
                WHERE section_id = :1
            """, (section_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in getting section details {section_id}: {e}")
            return None
        finally:
            cur.close() 
    def delete_section(self, section_id: int):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from section where section_id = :1", (section_id,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting section {section_id}: {e}")
            return False
        finally:
            cur.close()
