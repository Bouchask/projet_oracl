import cx_Oracle
import logging

class departement:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_departement(self, name: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("insert into departement (name) values (:1)", (name,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert departement: {e}")
            return False
        finally: cur.close()

    def select_all_departements(self): # <--- Renommé avec 's' à la fin
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from departement ORDER BY name")
            return cur.fetchall()
        except Exception as e:
            logging.error(f"Error select departements: {e}")
            return []
        finally: cur.close()

    def select_departement_ByName(self, name: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from departement where name = :1", (name,))
            return cur.fetchall()
        finally: cur.close()

    def delete_departement(self, name: str): # <--- Corrigé (delet -> delete)
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from departement where name = :1", (name,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error delete departement {name}: {e}")
            return False
        finally: cur.close()

    def count_departements(self): # <--- Zidna had fonction d STATS
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM departement")
            res = cur.fetchone()
            return res[0] if res else 0
        except: return 0
        finally: cur.close()
    def update_departement_name(self, old_name, new_name):
        cur = self.cnn.cursor()
        try:
            cur.execute("UPDATE departement SET name = :1 WHERE name = :2", (new_name, old_name))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            return False
        finally: cur.close()