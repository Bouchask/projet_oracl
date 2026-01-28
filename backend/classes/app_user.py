import cx_Oracle
import logging

class app_user:
    def __init__(self, cnn):
        self.cnn = cnn

    def insert_app_user(self, code_apoge: str, password_hash: str, role: str):
        cur = self.cnn.cursor()
        try:
            # Check if user already exists
            existing_user = self.select_app_user_by_code_apoge(code_apoge)
            if existing_user:
                return True
            
            # If not, insert the new user
            cur.execute("insert into app_user (code_apoge, password_hash, role) values (:1, :2, :3)",
                        (code_apoge, password_hash, role))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in creating app user {code_apoge}: {e}")
            return False
        finally:
            cur.close()

    def select_app_user_by_code_apoge(self, code_apoge: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from app_user where code_apoge = :1", (code_apoge,))
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting app user {code_apoge}: {e}")
            return None
        finally:
            cur.close()

    def select_all_app_users(self):
        cur = self.cnn.cursor()
        try:
            cur.execute("select * from app_user")
            rows = cur.fetchall()
            return rows
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in selecting all app users: {e}")
            return None
        finally:
            cur.close()

    def update_app_user_password(self, code_apoge: str, new_password_hash: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("update app_user set password_hash = :1 where code_apoge = :2",
                        (new_password_hash, code_apoge))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating app user password for {code_apoge}: {e}")
            return False
        finally:
            cur.close()

    def update_app_user_role(self, code_apoge: str, new_role: str):
        cur = self.cnn.cursor()
        try:
            cur.execute("update app_user set role = :1 where code_apoge = :2",
                        (new_role, code_apoge))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in updating app user role for {code_apoge}: {e}")
            return False
        finally:
            cur.close()

    def delete_app_user(self, code_apoge: str):
        cur = self.cnn.cursor()
        try:
            # Be cautious with this method, as it can orphan records in student/instructor tables
            # or fail if there are related records.
            cur.execute("delete from app_user where code_apoge = :1", (code_apoge,))
            self.cnn.commit()
            return True
        except Exception as e:
            self.cnn.rollback()
            logging.error(f"Error in deleting app user {code_apoge}: {e}")
            return False
        finally:
            cur.close()
