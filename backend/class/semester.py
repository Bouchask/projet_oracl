import cx_Oracle
from datetime import datetime
import logging

class semester:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_semester(self, name: str, start_date: datetime, end_date: datetime):
        cur = self.cnn.cursor()
        try:
            cur.execute("insert into semester (name, start_date, end_date) values (:1, :2, :3)",
                        (name, start_date, end_date))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating semester {name}: {e}")
            return False
        finally:
            cur.close()

    def select_semester_by_name(self, name: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from semester where name = :1", (name,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting semester {name}: {e}")
            return None
        finally:
            cur.close()

    def select_all_semesters(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from semester")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all semesters: {e}")
            return None
        finally:
            cur.close()

    def update_semester(self, name: str, new_start_date: datetime, new_end_date: datetime):
        cur = self.cnn.cursor()
        try:
            cur.execute("update semester set start_date = :1, end_date = :2 where name = :3",
                        (new_start_date, new_end_date, name))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating semester {name}: {e}")
            return False
        finally:
            cur.close()

    def delete_semester(self, name: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from semester where name = :1", (name,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting semester {name}: {e}")
            return False
        finally:
            cur.close()
