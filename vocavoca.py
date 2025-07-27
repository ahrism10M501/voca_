from DB_utils import *

"""
'beginner':0,
'elementary':1,
'intermediate':2,
'advanced':3,
'native':4,
'<UNK>':5
"""
day = 3
voca_level = levelToIndex["elementary"]
voca_file_path = "voca.txt"

vocas = txtToList(voca_file_path)

with DBConnect("./VOCA.db", auto_commit=True) as db:
    db.addVocaToDB(vocas, voca_level, day)