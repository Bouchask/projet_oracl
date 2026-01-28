import cx_Oracle
import logging

class salle:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_salle(self, code_salle: str, capacity: int, building: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("insert into salle (code_salle, capacity, building) values (:1, :2, :3)",
                        (code_salle, capacity, building))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating salle {code_salle}: {e}")
            return False
        finally:
            cur.close()

    def select_salle_by_code(self, code_salle: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from salle where code_salle = :1", (code_salle,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting salle {code_salle}: {e}")
            return None
        finally:
            cur.close()

    def select_all_salles(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from salle")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all salles: {e}")
            return None
        finally:
            cur.close()

    def update_salle(self, code_salle: str, new_capacity: int, new_building: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("update salle set capacity = :1, building = :2 where code_salle = :3",
                        (new_capacity, new_building, code_salle))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating salle {code_salle}: {e}")
            return False
        finally:
            cur.close()

    def delete_salle(self, code_salle: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("delete from salle where code_salle = :1", (code_salle,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting salle {code_salle}: {e}")
            return False
        finally:
            cur.close()
