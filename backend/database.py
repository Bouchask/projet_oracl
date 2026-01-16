import oracledb
from db_config import DB_USER, DB_PASSWORD, DB_DSN

def get_db_connection(user, password):
    try:
        connection = oracledb.connect(user=user, password=password, dsn=DB_DSN)
        return connection
    except oracledb.Error as err:
        error_obj, = err.args
        print("Oracle-Error-Code:", error_obj.code)
        print("Oracle-Error-Message:", error_obj.message)
        return None
