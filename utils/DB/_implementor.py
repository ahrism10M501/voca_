import abc
from _iconnection import *
from _icrud import *

class DBImplementor:
    @abc.abstractmethod
    def __enter__(self) -> 'ICRUD': pass
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, exc_tb) -> bool|None: pass

class SqliteRepo(DBImplementor):
    def __init__(self, path):
        self.path = path
        self.connection_handler:IConnection = SqliteConnection(path)
        self.cur:Optional[sqlite3.Cursor] = None

    def __enter__(self) -> 'ICRUD':
        self.connection_handler.connect()
        self.cur = self.connection_handler.get_cursor()
        self.crud = SqliteCRUD(self.connection_handler)
        return self.crud
    
    def __exit__(self, exc_type, exc_value, exc_tb) -> Optional[bool]:
        try:
            if exc_type is None:
                self.connection_handler.commit()
            else:
                self.connection_handler.rollback()
            self.connection_handler.close()
        except Exception as e:
            print(f"Exit handling error: {e}")
            return False
        finally:
            return exc_type is None