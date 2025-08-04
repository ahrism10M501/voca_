from utils.DB.DB_utils import *

db_path = "VOCA.DB"
sqlrepo = SqliteDB(db_path)

with DBOpen(sqlrepo) as db:
    data = db.load(order_by="word")
    fin1 = db.find(condition={"word":"check"})
    fin2 = db.find(condition={"word_id":[10, 40, 30, 20]})

def printline(data:list):
    for line in data:
        print(line)
    print()

# printline(data[:30])
# printline(fin1)
printline(sorted(fin2, key=lambda x: x[6]))