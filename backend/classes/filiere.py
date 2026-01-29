import cx_Oracle
import logging

class filiere:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_filiere(self, name, dept_id):
        cur = self.cnn.cursor()
        try:
            cur.execute("INSERT INTO filiere (name, departement_id) VALUES (:1, :2)", (name, dept_id))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error insert filiere: {e}")
            return False
        finally: cur.close()

    def select_all_filieres(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT f.filiere_id, f.name, d.name 
                FROM filiere f JOIN departement d ON f.departement_id = d.departement_id
                ORDER BY f.name
            """)
            return cur.fetchall()
        finally: cur.close()
    # Récupérer les cours d'une filière par semestre
    def get_courses_by_semester(self, filiere_id, semester_id):
        cur = self.cnn.cursor()
        try:
            ref_cursor = cur.callfunc("get_filiere_courses", cx_Oracle.CURSOR, [int(filiere_id), int(semester_id)])
            return ref_cursor.fetchall()
        except Exception as e:
            logging.error(f"Erreur Filiere Courses: {e}")
            return []
        finally:
            cur.close()