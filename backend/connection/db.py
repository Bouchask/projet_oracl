import cx_Oracle 
import logging
class db : 
    def __init__(self,user : str , password : str , dsn : str):
        self.user  = user 
        self.password = password 
        self.dsn = dsn 
    def get_connection(self):
        self.connection = cx_Oracle.connect(user = self.user  , password = self.password , dsn = self.dsn)
        return self.connection
    def close_connection(self):
        if self.connection:
            try:
                self.connection.close()
            except cx_Oracle.DatabaseError as e:
                logging.error(f"Erreur lors de la fermeture de la connexion: {e}")
 