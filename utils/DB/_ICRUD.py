import abc
from typing import Optional, cast
import sqlite3
import logging
from utils.DB._iconnection import *
from utils.FileProcessor import *

class ICRUD(abc.ABC):
    @abc.abstractmethod
    def dump(self, vocas:list|tuple, level:int, day:int): raise NotImplementedError("dump가 미구현 되었습니다")

    @abc.abstractmethod
    def load(self, order_by:str|None=None) -> list: raise NotImplementedError("load가 미구현 되었습니다")
        
    @abc.abstractmethod
    def find(self, target:dict) -> list: raise NotImplementedError("find가 미구현 되었습니다")

    @abc.abstractmethod
    def update(self, word_id:int, data:dict): raise NotImplementedError("update가 미구현 되었습니다")
    
    @abc.abstractmethod
    def delete(self, word_id:int): raise NotImplementedError("delete가 미구현 되었습니다")

class SqliteCRUD(ICRUD):
    def __init__(self, con:IConnection, auto_commit=False):
        self.con = con
        self.cur:sqlite3.Cursor|None = con.get_cursor()
        if self.cur is None:
            raise sqlite3.Error

        from utils.constants import sql_columns as sc
        self.words_column_list = sc["words_column_list"]
        self.meanings_column_list = sc["meanings_column_list"]

        self.auto_commit = auto_commit

    # HACK: dump하는 과정을 다르게 바꿔야할듯. 특히 인자값. pandas를 쓰면 다르게 받아올 거임. 
    # FIleProcessor 도 손봐야함. 지금은 (word, meaning) 쌍으로 저장 및 부르는데 DB 형식과 안 맞을뿐더러 그 떄문에 이상해짐.
    # 특히, 새로운 column이 생겼을떄 대처가 안 된다는 것도 문제. key값을 받아서 사용하는게 좋을 듯.
    def dump(self, vocas:list|tuple, level:int, day:int):
        if self.cur is None:
            raise sqlite3.Error
        vocas = FileProcessor._PreProcess(vocas)
        for word, mean in vocas:
            self.cur.execute("INSERT OR IGNORE INTO words (word, level, day) VALUES (?, ?, ?)", (word, level, day))
            self.cur.execute("SELECT word_id FROM words WHERE word = ?", (word,))
            word_id = self.cur.fetchone()[0]
            self.cur.execute("INSERT OR IGNORE INTO meanings (word_id, meaning) VALUES (?, ?)", (word_id, mean))

        if self.auto_commit:
            self.con.commit()

        logging.info(f"the {len(vocas)} words are added on Database")
        return True
    
    def load(self, order_by=None):
        if self.cur is None:
            raise sqlite3.Error
        query = f"SELECT * FROM words join meanings on words.word_id = meanings.word_id"
        
        if order_by:
            if order_by in self.words_column_list:
                query += " ORDER BY words.{}".format(order_by)
            elif order_by in self.meanings_column_list:
                query += " ORDER BY meanings.{}".format(order_by)
            else:
                raise ValueError("Invalid Column Name")

        self.cur.execute(query)
        return self.cur.fetchall()
    
    def find(self, target:dict) -> list:
        if self.cur is None:
            raise sqlite3.Error
        query = "SELECT * FROM words wo INNER JOIN meanings me ON wo.word_id=me.word_id WHERE 1=1 "
        params = []

        for k, v in target.items():
            if k in self.words_column_list:
                table = "wo"
            elif k in self.meanings_column_list:
                table = "me"
            else:
                raise ValueError(f"Invalid Column name {k}")
            
            if isinstance(v, (list, tuple)):
                qm = ",".join("?" * len(v))
                query += f" AND {table}.{k} IN ({qm})" # AND wo.word_id IN (?, ?, ?)
                params.extend(v)
            else:
                query += f" AND {table}.{k} = ?"
                params.append(v)
    
        self.cur.execute(query, tuple(params))
        return self.cur.fetchall()
    
    def update(self, word_id:int, data:dict):
        if self.cur is None:
            raise sqlite3.Error
        for key in data.keys():
            if key in self.words_column_list:
                query = f"UPDATE words SET {key} = ? FROM words WHERE word_id = {word_id}"
                self.cur.execute(query, tuple(data[key]))
            elif key in self.meanings_column_list:
                query = f"UPDATE words SET {key} = ? FROM meanings WHERE word_id = {word_id}"
                self.cur.execute(query, tuple(data[key]))
            else:
                logging.warning(f"Invalid Columns {key}: CONTINUE")
                continue

    def delete(self, word_id:int):
        if self.cur is None:
            raise sqlite3.Error
        # FIXME: If the meanings table doesn't have 'the ON DELETE CASCADE' property, it's workaround
        query = "DELETE FROM words WHERE word_id = ?"
        self.cur.execute(query, (word_id, ))