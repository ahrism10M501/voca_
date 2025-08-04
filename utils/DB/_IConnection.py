import abc
import logging
from typing import Optional, Any
import sqlite3

class IConnection(abc.ABC):
    @abc.abstractmethod
    def connect(self) -> bool: pass
    @abc.abstractmethod
    def close(self) -> bool: pass
    @abc.abstractmethod
    def commit(self) -> bool: pass
    @abc.abstractmethod
    def rollback(self) -> bool: pass
    @abc.abstractmethod
    def get_cursor(self) -> Optional[sqlite3.Cursor]: pass

class SqliteConnection(IConnection):
    def __init__(self, path:str):
        self.path = path
        self.con = None
        self.cur = None

    def connect(self) -> bool:
        self.con = sqlite3.connect(self.path)
        self.cur:Optional[sqlite3.Cursor] = self.con.cursor()
        return True

    def close(self) -> bool:
        if self.con:
            self.con.close()
            return True
        return False
    
    def commit(self) -> bool:
        if self.con:
            self.con.commit()
            return True
        return False
        
    def rollback(self) -> bool:
        if self.con:
            self.con.rollback()
            return True
        return False

    def get_cursor(self) -> Optional[sqlite3.Cursor]:
        if self.cur:
            return self.cur
        return None