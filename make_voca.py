import sqlite3
import re

con = sqlite3.connect("./VOCA.db")
cur = con.cursor()

level = {'beginner':0, 'elementary':1, 'intermediate':2, 'advanced':3, 'native':4, '':5}










day = 1
voca_level = level['intermediate']
voca_file_path = "voca.txt"













voca = []
with open('voca.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        word_part, meaning_part = line.strip().split(':', 1)
        word = word_part.strip()
        meanings = re.split(r'[;,]', meaning_part.strip())  # 쉼표/세미콜론 기준 분리. 리스트 반환

        # 1. 단어 삽입 or 무시
        cur.execute("INSERT OR IGNORE INTO words (word, level, day) VALUES (?, ?, ?)", (word, voca_level, day))
        
        # 2. word_id 가져오기
        cur.execute("SELECT word_id FROM words WHERE word = ?", (word,))
        word_id = cur.fetchone()[0]

        # 3. 의미 삽입
        for mean in meanings:
            mean = mean.strip()
            if mean:
                cur.execute("INSERT OR IGNORE INTO meanings (word_id, meaning) VALUES (?, ?)", (word_id, mean))

con.commit()
con.close()