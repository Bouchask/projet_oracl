import cx_Oracle
import logging

class semester:
    def __init__(self, cnn):
        self.cnn = cnn

    def select_all_semesters(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM semester ORDER BY start_date DESC")
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Error select semesters: {e}")
            return []
        finally:
            cur.close()

    def insert_semester(self, name, start_date, end_date):
        cur = self.cnn.cursor()
        try:
            # FIX: Zdna TO_DATE bach Oracle yfhm string 'YYYY-MM-DD'
            sql = "INSERT INTO semester (name, start_date, end_date) VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), TO_DATE(:3, 'YYYY-MM-DD'))"
            cur.execute(sql, (name, start_date, end_date))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert semester: {e}")
            return False
        finally:
            cur.close()

    def select_semester_by_name(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM semester WHERE name = :1", (name,))
            return cur.fetchall()
        finally:
            cur.close()
            
    def delete_semester(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM semester WHERE name = :1", (name,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            return False
        finally:
            cur.close()
    def update_semester_name(self, old_name, new_name):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE semester SET name = :1 WHERE name = :2", (new_name, old_name))
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()