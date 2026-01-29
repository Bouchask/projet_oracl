import cx_Oracle
class semester:
    def __init__(self, cnn): self.cnn = cnn
    def insert_semester(self, name, start, end):
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO semester (name, start_date, end_date) VALUES (:1, :2, :3)", (name, start, end))
            self.cnn.commit(); return True
        except: self.cnn.rollback(); return False
        finally: cur.close()
    def select_all_semesters(self):
        cur = self.cnn.cursor()
        try: cur.execute("SELECT * FROM semester"); return cur.fetchall()
        finally: cur.close()
    def delete_semester(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM semester WHERE name = :1", (name,))
            self.cnn.commit(); return True
        except: return False
        finally: cur.close()
    def update_semester_name(self, old, new):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE semester SET name = :1 WHERE name = :2", (new, old))
            self.cnn.commit(); return True
        except: return False
        finally: cur.close()