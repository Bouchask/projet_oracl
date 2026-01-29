import cx_Oracle
class departement:
    def __init__(self, cnn): self.cnn = cnn
    def insert_departement(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO departement (name) VALUES (:1)", (name,))
            self.cnn.commit(); return True
        except: self.cnn.rollback(); return False
        finally: cur.close()
    def select_all_departments(self):
        cur = self.cnn.cursor()
        try: cur.execute("SELECT * FROM departement"); return cur.fetchall()
        finally: cur.close()
    def delete_departement(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM departement WHERE name = :1", (name,))
            self.cnn.commit(); return True
        except: return False
        finally: cur.close()
    def update_departement_name(self, old, new):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE departement SET name = :1 WHERE name = :2", (new, old))
            self.cnn.commit(); return True
        except: return False
        finally: cur.close()