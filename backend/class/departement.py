import cx_Oracle
import logging

class departement  :
    def __init__(self , cnn ) : 
        self.cnn  =  cnn 
    def insert_departement(self  , name : str) : 
        cur = self.cnn.cursor()
        try :
            cur.execute("insert into departement (name) values (:1)" , (name,))
            self.cnn.commit()
            return True 
        except Exception as e : 
            self.cnn.rollback()
            logging.error(f"error in creation departement {name} : {e}")
            return False 
        finally : 
            cur.close()
    def select_departement_ByName(self, name : str) :
        cur = self.cnn.cursor()
        try  :
            cur.execute("select * from departement where name = :1" , (name,))
            rows = cur.fetchall()
            return rows 
        except Exception as  e :
            self.cnn.rollback()
            logging.error(f"error in select departement {name} : {e}")
            return None
        finally : 
            cur.close()
    def select_all_departement(self,) :
        cur = self.cnn.cursor()
        try  :
            cur.execute("select * from departement ")
            rows = cur.fetchall()
            return rows 
        except Exception as  e :
            self.cnn.rollback()
            logging.error(f"error in select departemensts : {e}")
            return None
        finally : 
            cur.close()   
    def delet_departement(self, name : str) :
        cur = self.cnn.cursor()
        try  :
            cur.execute("delete from departement where name = :1" , (name,))
            self.cnn.commit()
            return True
        except Exception as  e :
            self.cnn.rollback()
            logging.error(f"error in delet departement {name} : e")
            return False
        finally : 
            cur.close() 
    def update_departement(self, name : str , old_name : str) :
        cur = self.cnn.cursor()
        try  :
            cur.execute("update departement set name = :1 where name = :2" , (name , old_name))
            self.cnn.commit()
            return True
        except Exception as  e :
            self.cnn.rollback()
            logging.error(f"error in update departement {name} : e")
            return False
        finally : 
            cur.close() 
    