levelToIndex = {'beginner':0,
                'elementary':1,
                'intermediate':2,
                'advanced':3,
                'native':4,
                '<UNK>':5
                }

indexToLevel = {v: k for k, v in levelToIndex.items()}

sql_table = ('words', 'meanings')
sql_columns = {
                "words_column_list":("word_id", "word", "day", "level"),
                "meanings_column_list":("meaning_id", "meaning")
                }