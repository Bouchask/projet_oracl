import cx_Oracle
import logging

class grades_audit:
    def __init__(self, cnn):
        self.cnn = cnn

    def select_all_audits(self):
        """ Récupère tout l'historique des changements (du plus récent au plus ancien) """
        cur = self.cnn.cursor()
        try:
            cur.execute("SELECT * FROM grades_audit ORDER BY change_date DESC")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            # Pas de rollback nécessaire pour un select, mais on garde la structure
            logging.error(f"Error in selecting all audits: {e}")
            return None
        finally:
            cur.close()

    def select_audits_by_student(self, student_id: int):
        """ Voir l'historique des changements pour un étudiant spécifique """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT * FROM grades_audit 
                WHERE student_id = :1 
                ORDER BY change_date DESC
            """, (student_id,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error in selecting audits for student {student_id}: {e}")
            return None
        finally:
            cur.close()

    def select_audits_by_course(self, course_code: int):
        """ Voir l'historique des changements pour un cours spécifique """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT * FROM grades_audit 
                WHERE course_code = :1 
                ORDER BY change_date DESC
            """, (course_code,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error in selecting audits for course {course_code}: {e}")
            return None
        finally:
            cur.close()

    def select_audit_details(self):
        """ 
        Une version améliorée qui fait des JOINS pour afficher les Noms au lieu des IDs.
        Utile pour l'affichage Admin.
        """
        cur = self.cnn.cursor()
        try:
            cur.execute("""
                SELECT 
                    g.audit_id,
                    s.first_name || ' ' || s.last_name as student_name,
                    c.title as course_title,
                    g.old_grade,
                    g.new_grade,
                    g.change_date,
                    g.user_action
                FROM grades_audit g
                JOIN student s ON g.student_id = s.student_id
                JOIN course c ON g.course_code = c.course_code
                ORDER BY g.change_date DESC
            """)
            rows = cur.fetchall()
            return rows
        except Exception as e:
            logging.error(f"Error in selecting audit details: {e}")
            return None
        finally:
            cur.close()