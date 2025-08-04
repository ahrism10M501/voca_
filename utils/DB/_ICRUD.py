import abc
import sqlite3
import logging
from utils.DB._iconnection import *
from utils.FileProcessor import *

class ICRUD(abc.ABC):
    @abc.abstractmethod
    def dump(self, vocas:list|tuple, level:int, day:int) -> bool: pass

    @abc.abstractmethod
    def load(self, order_by:str|None=None) -> list: pass
        
    @abc.abstractmethod
    def find(self, condition:dict|None=None, columns:list|None=None) -> list: pass

    @abc.abstractmethod
    def update(self, condition:dict, data:dict) -> bool: pass
    
    @abc.abstractmethod
    def delete(self, condition:dict) -> bool: pass

class SqliteCRUD(ICRUD):
    def __init__(self, con:IConnection):
        self.con = con
        self.cur:sqlite3.Cursor|None = con.get_cursor()
        if self.cur is None:
            raise sqlite3.Error

        from utils.constants import sql_columns as sc
        self.words_column_list = sc["words_column_list"]
        self.meanings_column_list = sc["meanings_column_list"]

    def _condition(self, condition:dict|None) -> tuple[str, tuple]:
        query = " WHERE 1=1"
        if condition is None:
            return query, tuple()
        
        params = []
        for k, v in condition.items():
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

        return query, tuple(params)
    
    # HACK: dump하는 과정을 다르게 바꿔야할듯. 특히 인자값. pandas를 쓰면 다르게 받아올 거임. 
    # FIleProcessor 도 손봐야함. 지금은 (word, meaning) 쌍으로 저장 및 부르는데 DB 형식과 안 맞을뿐더러 그 떄문에 이상해짐.
    # 특히, 새로운 column이 생겼을떄 대처가 안 된다는 것도 문제. key값을 받아서 사용하는게 좋을 듯.
    def dump(self, vocas:list|tuple, level:int, day:int) -> bool:
        if self.cur is None:
            raise sqlite3.Error
        vocas = FileProcessor._PreProcess(vocas) # [(word, meaning), (..., ...)]
       
        words = [(word, level, day) for word, _ in vocas]
        self.cur.executemany(f"INSERT OR IGNORE INTO words (word, level, day) VALUES (?, ?, ?)", words)

        qm = ",".join("?"*len(vocas))
        self.cur.execute(f"SELECT word_id, word FROM words WHERE word IN ({qm})", words)
        
        id_map = {word:word_id for word_id, word in self.cur.fetchall()}
        meanings = [(id_map[word], mean) for word, mean in vocas if word in id_map]

        self.cur.executemany(f"INSERT OR IGNORE INTO meanings (word_id, meaning) VALUES (?, ?)", meanings)

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
    
    def find(self, condition=None, columns=None) -> list:
        if self.cur is None:
            raise sqlite3.Error
        if condition is None:
            condition = {}
        if columns is None:
            columns = ["*"]
        query = f"SELECT {','.join(columns)} FROM words wo INNER JOIN meanings me ON wo.word_id = me.word_id"
        q, params = self._condition(condition)
        query += q

        self.cur.execute(query, params)
        return self.cur.fetchall()
    
    def update(self, condition:dict, data:dict) -> bool:
        if self.cur is None:
            raise sqlite3.Error
        
        condi, params = self._condition(condition)

        for key, val in data.items():
            if key in self.words_column_list:
                query = f"UPDATE words SET {key} = ?" + condi
                self.cur.execute(query, (val, *params))
                
            elif key in self.meanings_column_list:
                query = f"UPDATE meanings SET {key} = ?" + condi
                self.cur.execute(query, (val, *params))
            
            else:
                logging.warning(f"Invalid Columns {key}: CONTINUE")
                continue
            
            for k, v in condition.items():
                logging.info(f"DB Update: {k} = {v} | {key} -> {data[key]}")
        
        return True
                
    def delete(self, condition:dict) -> bool:
        if self.cur is None:
            raise sqlite3.Error
        
        sub_query = "SELECT wo.word_id FROM words wo INNER JOIN meanings me ON wo.word_id = me.word_id"
        q, params = self._condition(condition)
        sub_query += q
        word_ids = [wid[0] for wid in self.cur.execute(sub_query, params)]
        if not word_ids:
            return False
        
        물음표 = ",".join("?"* len(word_ids))
        self.cur.execute(f"DELETE FROM meanings WHERE word_id IN ({물음표})", word_ids)
        self.cur.execute(f"DELETE FROM words WHERE word_id IN ({물음표})", word_ids)

        logging.info(f"DB Delete: word_ids = {word_ids} | conditon -> {condition}")
        return True