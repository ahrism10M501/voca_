import abc
import logging
import sqlite3

class IQuery(abc.ABC):
    @abc.abstractmethod
    def find(self, word_id=None, meaning_id=None, word=None, meaning=None, day=None, level=None) -> list:
        raise NotImplementedError

class SqliteQueryService(IQuery):
    def __init__(self, cur):
        self.cur: sqlite3.Cursor = cur
    
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