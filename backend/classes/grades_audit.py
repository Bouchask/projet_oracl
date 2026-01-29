import cx_Oracle
class grades_audit:
    def __init__(self, cnn): self.cnn = cnn
    def select_all_audits(self):
        cur = self.cnn.cursor()
        try: cur.execute("SELECT * FROM grades_audit ORDER BY change_date DESC"); return cur.fetchall()
        finally: cur.close()