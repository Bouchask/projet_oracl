import cx_Oracle
class salle:
    def __init__(self, cnn): self.cnn = cnn
    def insert_salle(self, code, cap, build):
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO salle (code_salle, capacity, building) VALUES (:1, :2, :3)", (code, cap, build))
            self.cnn.commit(); return True
        except: self.cnn.rollback(); return False
        finally: cur.close()
    def select_all_salles(self):
        cur = self.cnn.cursor()
        try: cur.execute("SELECT * FROM salle"); return cur.fetchall()
        finally: cur.close()
    def delete_salle(self, code):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM salle WHERE code_salle = :1", (code,))
            self.cnn.commit(); return True
        except: return False
        finally: cur.close()
    def update_salle_capacity(self, code, cap):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE salle SET capacity = :1 WHERE code_salle = :2", (cap, code))
            self.cnn.commit(); return True
        except: return False
        finally: cur.close()