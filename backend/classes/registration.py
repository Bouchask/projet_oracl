import cx_Oracle
import logging

class registration:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_registration(self, student_id: int, section_id: int):
        cur = self.cnn.cursor()
        try:
            # Trigger s'occupe de mettre status='PENDING' et vérifier filière
            cur.execute("INSERT INTO registration (student_id, section_id) VALUES (:1, :2)", (student_id, section_id))
            self.cnn.commit()
            return True
        except cx_Oracle.DatabaseError as e:
            error, = e.args
            self.cnn.rollback()
            if error.code == 20090: logging.error("Interdit: Hors Filière")
            elif error.code == 20200: logging.error("Bloqué: Etudiant Dropped")
            else: logging.error(f"DB Error: {e}")
            return False
        finally: cur.close()

    # --- WORKFLOW VIA PACKAGES ---
    def validate_registration(self, reg_id):
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_REGISTRATION.validate_reg", [reg_id])
            return True
        except Exception as e:
            logging.error(f"Error validate: {e}")
            return False
        finally: cur.close()

    def cancel_registration(self, reg_id):
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_REGISTRATION.cancel_reg", [reg_id])
            return True
        except: return False
        finally: cur.close()

    def drop_registration(self, reg_id):
        cur = self.cnn.cursor()
        try:
            cur.callproc("PKG_REGISTRATION.drop_reg", [reg_id])
            return True
        except: return False
        finally: cur.close()

    def get_registrations_by_section(self, section_id):
        """ Utilise la VUE v_registration_details """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT registration_id, first_name, last_name, code_apoge, status, registration_date
                FROM v_registration_details WHERE section_id = :1
            """, (section_id,))
            return cur.fetchall()
        finally: cur.close()