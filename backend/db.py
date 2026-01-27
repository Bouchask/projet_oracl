import cx_Oracle 
class db : 
    def __init__(self,user : str , password : str , dsn : str):
        self.user  = user 
        self.password = password 
        self.dsn = dsn 
    def get_connection(self):
        return cx_Oracle.connect(user = self.user  , password = self.password , dsn = self.dsn)

 