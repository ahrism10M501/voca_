import re
import logging
import sqlite3
from typing import Optional

from utils.FileProcessor import FileProcessor

"""
SQL형식의 DB에 업로드하거나, 업데이트 하거나, 불러오기 위한 클래스

지금은 너무 패턴이 어렵다!!!
DBConnect 클래스의 책임이 너무 크다. CRUD를 분리해서 관리하고, DBConnect는 with문을 통해 이들을 통제하는 팩토리가 되면 좋겠다.
"""


__all__ = ['levelToIndex', 'indexToLevel', 'DBConnect', 'DataGetter']

levelToIndex = {'beginner':0,
                'elementary':1,
                'intermediate':2,
                'advanced':3,
                'native':4,
                '<UNK>':5
                }

indexToLevel = {0:'beginner',
                1:'elementary',
                2:'intermediate',
                3:'advanced',
                4:'native',
                5:'<UNK>'
                }

class DBConnect():
    def __init__(self, path, auto_commit=False):
        
        self.path = path
        # HACK : 하드코딩 된 부분 고쳐야 합니다.
        self.tables = ('words', 'meanings')

        self.con = sqlite3.connect(path)
        logging.info(f"DB {path} is connected")
        self.cur = self.con.cursor()
        
        self.cur.execute(f"PRAGMA table_info({self.tables[0]})")
        self.words_columns = [row[1] for row in self.cur.fetchall()]

        self.cur.execute(f"PRAGMA table_info({self.tables[1]})")
        self.meanings_columns = [row[1] for row in self.cur.fetchall()]

        self.auto_commit = auto_commit

    def __del__(self):
        self.con.close()

    def dump(self, vocas:list|tuple, level:int, day:int) -> bool:
        """
        list(tuple(str, str))로 받은 단어 정보를 저장합니다.
        level과 day는 별개로 지정해주세요.
        """
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

    def load(self, target):
        """
        target은 반드시 앞에 테이블명.타겟명
        """
        if ';' in target:
            logging.warning("SQL Injection Detected!")
            raise ValueError("Semicolons are not allowed in table or targets.")
        
        query = f"SELECT {target} FROM words left join meanings on words.word_id = meanings.word_id ORDER BY words.word_id"
        self.cur.execute(query)
        return self.cur.fetchall()

    def updateDataByWord(self, word, target, data, num:Optional[int] = None) -> bool:
        """
        단어를 토대로 words 테이블의 정보를 수정합니다.
        뜻이 여러 개일 경우, num으로 수정 대상을 선택하세요.
        """
        if target in self.meanings_columns:
            return self._updateMeaningsByWord(word, target, data, num)
        elif target in self.words_columns:
            return self._updateWordsByWord(word, target, data)
        else:
            raise ValueError("Invalid Column name")

    def _updateWordsByWord(self, word, target, data):
        query = f"SELECT word_id, {target} FROM words WHERE word = ?"
        self.cur.execute(query, (word,))
        diff = self.cur.fetchone()
        if not diff:
            raise ValueError("Word not found")
        
        query = f"UPDATE words SET {target} = ? WHERE word = ?"
        self.cur.execute(query, (data, word))

        if self.auto_commit:
            self.con.commit()

        logging.info(f"{word}'s {target} updated from {diff[1]} to {data}: word_id={diff[0]}")

        return True

    def _updateMeaningsByWord(self, word, target, data, num:Optional[int] = None):
        self.cur.execute("SELECT word_id FROM words WHERE word = ?", (word,))
        word_id = self.cur.fetchone()
        if not word_id:
            raise ValueError("Word not found")
        word_id = word_id[0]

        self.cur.execute("SELECT meaning_id, meaning FROM meanings WHERE word_id = ?", (word_id,))
        means = self.cur.fetchall()
        if not means:
            raise ValueError("Meanings not found")

        if len(means) > 1:
            if num is None or not (0 <= num < len(means)):
                raise ValueError(f"Invalid Num. Must be 0 ~ {len(means)-1}")
            mean_id = means[num][0]
            old_mean = means[num][1]
        else:
            mean_id = means[0][0]
            old_mean = means[0][1]

        query = f"UPDATE meanings SET {target} = ? WHERE meaning_id = {mean_id}"
        self.cur.execute(query, (data,))

        if self.auto_commit:
            self.con.commit()

        logging.info(f"{word}'s {target} updated from {old_mean} to {data}: meaning_id={mean_id}")

        return True

    def commit(self):
        self.con.commit()
        logging.info("DB commited")
        return True
    
    def close(self):
        self.con.close()
        logging.info("DB closed")
        return True
    
    def reconnect(self, retry=5):
        import time
        for num in range(retry):
            if not self.con:
                try:
                    logging.info(f"DB connecting... attempt {num+1}")
                    self.con = sqlite3.connect(self.path)
                    self.cur = self.con.cursor()
                    return True
                except sqlite3.Error as e:
                    logging.error(f"Connection ERROR: {e}")
                    time.sleep(1)
            else:
                print("DB is already connected")
                return True
        return False

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logging.error(f"Exception: {exc_type}, {exc_val}")
            return False
        
        self.commit() if self.auto_commit else None
        self.close()
        return True

class DataGetter():
    def __init__(self, db: DBConnect, table:str, targets:str, batch_size=128):
        self.batch_size = batch_size
        self.con = db.con
        self.cur = db.cur
        self.words_columns = db.words_columns
        self.commit = db.commit if db.auto_commit else None

        if ";" in table or ";" in targets:
            logging.warning("SQL Injection Detected!")
            raise ValueError("Semicolons are not allowed in table or targets.")
        
        if table not in db.tables:
            raise ValueError("Invalid table name")

        for col in targets.split(','):
            if col.strip() not in self.words_columns:
                raise ValueError(f"Invalid column name: {col.strip()}")

        self.table = table
        self.targets = targets

        self.pk_col = "word_id" if table == "words" else "meaning_id"

    def findMeanByWord(self, word:str) -> list[str]:
            """
            find means by one word from DB, and return list type object
            """
            query = """
            SELECT meaning FROM words wo, meanings me 
            WHERE wo.word= ? AND wo.word_id = me.word_id
            """
            self.cur.execute(query, (word,))
            means = self.cur.fetchall()

            return [m[0] for m in means]

    def __len__(self):
        self.cur.execute(f"SELECT COUNT(*) FROM {self.table}")
        return self.cur.fetchone()[0]

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start = 0 if idx.start is None else idx.start
            stop = 1<<30 if idx.stop is None else idx.stop
            step = 1 if idx.step is None else idx.step

            query = f"SELECT {self.targets} FROM {self.table} LIMIT ? OFFSET ? ORDER BY {self.pk_col}"
            self.cur.execute(query, (stop-start, start))
            return self.cur.fetchall()[::step]

        query = f"SELECT {self.targets} FROM {self.table} LIMIT 1 OFFSET ? ORDER BY {self.pk_col}"
        self.cur.execute(query, (idx,))
        return self.cur.fetchone()
    
    def __iter__(self):
        query = f"SELECT {self.targets} FROM {self.table} ORDER BY {self.pk_col}"
        self.cur.execute(query)
        while True:
            rows = self.cur.fetchmany(self.batch_size)
            if not rows:
                break
            for row in rows:
                yield row

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        filename="voca.log"
    )