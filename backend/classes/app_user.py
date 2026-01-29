import cx_Oracle
import logging

class app_user:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_app_user(self, code_apoge: str, password_hash: str, role: str):
        cur = self.cnn.cursor()
        try:
            # Vérifier existence
            cur.execute("SELECT 1 FROM app_user WHERE code_apoge = :1", (code_apoge,))
            if cur.fetchone(): return True 
            
            cur.execute("INSERT INTO app_user (code_apoge, password_hash, role) VALUES (:1, :2, :3)",
                        (code_apoge, password_hash, role))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert user {code_apoge}: {e}")
            return False
        finally: cur.close()

    def select_app_user_by_code_apoge(self, code_apoge: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM app_user WHERE code_apoge = :1", (code_apoge,))
            return cur.fetchall()
        finally: cur.close()

    def update_app_user_password(self, code_apoge: str, new_password_hash: str):
        """ Utilise la PROCEDURE PL/SQL pour changer le mot de passe """
        cur = self.cnn.cursor()
        try:
            # APPEL PACKAGE PKG_SECURITY
            cur.callproc("PKG_SECURITY.update_password", [code_apoge, new_password_hash])
            return True
        except Exception as e:
            logging.error(f"Error calling PKG_SECURITY.update_password: {e}")
            return False
        finally: cur.close()

    def delete_app_user(self, code_apoge: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("DELETE FROM app_user WHERE code_apoge = :1", (code_apoge,))
            self.cnn.commit()
            return True
        except: return False
        finally: cur.close()