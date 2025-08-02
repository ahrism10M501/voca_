import abc
from typing import Optional, cast
import sqlite3
import logging
from _IConnection import IConnection
from utils.FileProcessor import *

class ICRUD(abc.ABC):
    @abc.abstractmethod
    def dump(self, vocas:list|tuple, level:int, day:int): raise NotImplementedError("미구현 되었습니다")

    @abc.abstractmethod
    def load(self, order_by:str|None=None) -> list: raise NotImplementedError("미구현 되었습니다")
        
    @abc.abstractmethod
    def find(self, word_id=None, meaning_id=None, word=None, meaning=None, day=None, level=None) -> list: raise NotImplementedError("미구현 되었습니다")
    
    @abc.abstractmethod
    def update(self, word_id:int, data:dict): raise NotImplementedError("미구현 되었습니다")
    
    @abc.abstractmethod
    def delete(self, word_id:int): raise NotImplementedError("미구현 되었습니다")


class SqliteCRUD(ICRUD):
    def __init__(self, con:IConnection, auto_commit=False):
        self.con = con
        self.curs = con.get_cursor()
        if self.cur is None:
            raise sqlite3.Error
        self.cur = cast(sqlite3.Cursor, self.curs)

        self.words_column_list = ("word_id", "word", "day", "level")
        self.meanings_column_list = ("meaning_id", "meaning")

        self.auto_commit = auto_commit

    def dump(self, vocas:list|tuple, level:int, day:int):
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
    
    def load(self, order_by:str|None=None):
        
        query = "SELECT * FROM words join meanings on words.word_id = meanings.word_id"

        if order_by:
            if order_by in self.words_column_list:
                query += " ORDER BY words.{}".format(order_by)
            elif order_by in self.meanings_column_list:
                query += " ORDER BY meanings.{}".format(order_by)
            else:
                raise ValueError("Invalid Column Name")

        self.cur.execute(query)
        return self.cur.fetchall()
    
    def find(self, word_id=None, meaning_id=None, word=None, meaning=None, day=None, level=None) -> list:
        query = "SELECT * FROM words wo, meaning me WHERE 1=1"
        params = []

        if word_id:
            query += " AND wo.word_id = ?"
            params.append(word_id)
        if meaning_id:
            query += " AND me.meaning_id = ?"
            params.append(meaning_id)
        if word:
            query += " AND wo.word = ?"
            params.append(word)
        if meaning:
            query += " AND me.meaning = ?"
            params.append(meaning)
        if day:
            query += " AND wo.day = ?"
            params.append(day)
        if level:
            query += " AND wo.level = ?"
            params.append(level)
        
        self.cur.execute(query, tuple(params))
        return self.cur.fetchall()
    
    def update(self, word_id:int, data:dict):
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
        # FIXME: If the meanings table doesn't have 'the ON DELETE CASCADE' property, it's workaround
        query = "DELETE FROM words WHERE word_id = ?"
        self.cur.execute(query, (word_id, ))