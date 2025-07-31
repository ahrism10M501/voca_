from utils.DB_utils import *
from utils.FileProcessor import FileProcessor

"""
'beginner':0,
'elementary':1,
'intermediate':2,
'advanced':3,
'native':4,
'<UNK>':5
"""
day = 3
voca_level = levelToIndex["intermediate"]
voca_file_path = "vovovo.csv"
save_path = "vovovo.txt"

vocas = FileProcessor.load(voca_file_path)

with DBConnect("./VOCA.db", auto_commit=True) as db:
    words = db.load("words.word, meanings.meaning")

print(vocas)
# FileProcessor.dump(save_path, words)
