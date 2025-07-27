import re
import logging
import sqlite3

__all__ = ['levelToIndex', 'indexToLevel', 'txtToList', 'DBConnect', 'DataGetter']

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

def txtToList(path) -> list:
    voca = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            word, meaning = line.strip().split(':', 1)
            word = word.strip()
            meanings = re.split(r'[;,]', meaning.strip())
            for mean in meanings:
                mean = mean.strip()
                if mean:
                    voca.append((word, mean))
    return voca

class DBConnect():
    def __init__(self, path, auto_commit=True):
        
        self.path = path
        self.con = sqlite3.connect(path)
        logging.info(f"DB {path} is connected")
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA table_info(words);")
        # HACK : 하드코딩 된 부분 고쳐야 합니다.
        self.tables = {'words', 'meanings'}

        self.auto_commit = auto_commit
        self.words_columns = [row[1] for row in self.cur.fetchall()]
        
    def __del__(self):
        self.con.close()
        logging.info("DB is closed")

    def addVocaToDB(self, vocas:list, level:int, day:int) -> int:
        """
        list(tuple(str, str))로 받은 단어 정보를 저장합니다.
        level과 day는 별개로 지정해주세요.
        만약 해당 형식의 단어집이 있다면, txtToList를 이용해 단어 list를 받아오세요.
        """
        for voca in vocas:
            word, mean = voca
            
            self.cur.execute("INSERT OR IGNORE INTO words (word, level, day) VALUES (?, ?, ?)", (word, level, day))
            self.cur.execute("SELECT word_id FROM words WHERE word = ?", (word,))
            word_id = self.cur.fetchone()[0]
            self.cur.execute("INSERT OR IGNORE INTO meanings (word_id, meaning) VALUES (?, ?)", (word_id, mean))

        if self.auto_commit:
            self.con.commit()

        logging.info(f"the {len(vocas)} words are added on Database")
        return True

    def updateDataByWord(self, word, target, data) -> int:
        """
        단어를 토대로 words 테이블의 정보를 수정합니다.
        """
        if target not in self.words_columns:
            raise ValueError("Invalid Column name")
        
        

        query = f"SELECT word_id, {target} FROM words WHERE word = ?"
        self.cur.execute(query, (word,))
        diff = self.cur.fetchone()

        query = f"UPDATE words SET {target} = ? WHERE word = ?"
        self.cur.execute(query, (data, word))

        if self.auto_commit:
            self.con.commit()

        logging.info(f"{word}'s {target} updated from {diff[1]} to {data}: word_id={diff[0]}")

        return True

    def commit(self):
        self.con.commit()
        return True
    
    def close(self):
        self.con.close()
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

class DataGetter():
    def __init__(self, db: DBConnect, table:str, targets:str):
        self.con = db.con
        self.cur = db.cur
        self.words_columns = db.words_columns
        
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
        self.basic_query = f"SELECT {targets} FROM {table}"

        # 기본 PK 컬럼 지정 (words: word_id, meanings: meaning_id 등)
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

            query = self.basic_query + f" WHERE {self.pk_col} >= ? AND {self.pk_col} < ?"
            self.cur.execute(query, (start, stop))
            datas = self.cur.fetchall()[::step]
            return datas

        query = self.basic_query + f" WHERE {self.pk_col} = ?"
        self.cur.execute(query, (idx,))
        return self.cur.fetchone()

if __name__ == "__main__":
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y.%m.%d %H:%M:%S",
        filename="voca.log"
    )

    """
    'beginner':0,
    'elementary':1,
    'intermediate':2,
    'advanced':3,
    'native':4,
    '<UNK>':5
    """
    day = 2
    voca_level = levelToIndex['intermediate']
    voca_file_path = "voca.txt"

    print(txtToList(voca_file_path))
    db = DBConnect('./VOCA.db')
    data = DataGetter(db, 'words', 'word, level')
    print(data[3:10])