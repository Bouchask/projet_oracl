import cx_Oracle
import logging

class departement:
    def __init__(self, cnn):
        self.cnn = cnn

    # KANET: select_all_departement (Ghalta)
    # REDDITHA: select_all_departements (S7i7a)
    def select_all_departements(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM departement ORDER BY name")
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Error select all departements: {e}")
            return []
        finally:
            cur.close()

    def insert_departement(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO departement (name) VALUES (:1)", (name,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert dept: {e}")
            return False
        finally:
            cur.close()

    def select_departement_ByName(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM departement WHERE name = :1", (name,))
            return cur.fetchall()
        except Exception as e:
            return None
        finally:
            cur.close()
            
    def delete_departement(self, name):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM departement WHERE name = :1", (name,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            return False
        finally:
            cur.close()