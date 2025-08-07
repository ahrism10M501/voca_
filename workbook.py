# 자동으로 문제지를 만드는 프로그램을 만들어 봅시다

import abc
import random
from typing import Dict, Tuple
from PIL import Image

from utils.FileProcessor import *

# 가져야만 하는 인자를 정의해둘 수는 없나?
class VocaTemplate(abc.ABC):
    def __init__(self, type, num):
        self.type = type
        self.num_word = num
        self.ratio = 0.5
        self.blank = "___"

    def set_ratio(self, ratio):
        self.ratio = ratio
        return self
    
    def set_blank(self, blank):
        self.blank = blank
        return self
    
    def seed(self, seed):
        random.seed(seed)
        return True

class TextTemplate(VocaTemplate):
    def __init__(self, type, num):
        super().__init__(type, num)
        self.indent = 1

    def set_indent(self, indent):
        self.indent = indent
        return self

class ImageTemplate(VocaTemplate):
    pass

class Workbook(abc.ABC):
    def __init__(self, temp:VocaTemplate, data:list|tuple):
        self.template = temp
        self.processor = self._get_processor(temp)
        self.data = self.blanker(self._preprocess(data))

    @staticmethod
    def _get_processor(temp):
        if isinstance(temp, TextTemplate):
            return TextFileProcessor
        elif isinstance(temp, ImageTemplate):
            raise NotImplementedError
        else:
            raise ValueError(f"Invalid Template {temp}")

    @staticmethod
    def _preprocess(data):
        data = [(word, meaning) for word_id, word, day, level, meaning_id, word_id2, meaning in data]
        voca = {}
        temp = []
        for word, mean in data:
            if word in voca.keys():
                voca[word].append(mean)
            else:
                voca[word] = [mean]
        for k, v in voca.items():
            temp.append((k, ", ".join(v)))
        return temp
    
    def blanker(self, data):
        temp = []
        if self.template.type == 'ko':
            for word, mean in data:
                temp.append((mean, self.template.blank))
        elif self.template.type == 'en':
            for word, mean in data:
                temp.append((word, self.template.blank))
        elif self.template.type == 'both':
            # FIXME : 임시 조치로 비율을 대충 산정함. ratio가 더 덩당하게 적용되도록 만들어야한다.
            for row in data:
                choice = round(random.random()+self.template.ratio/2)
                temp.append((row[choice], self.template.blank))
        else:
            raise ValueError("Invalid Form Type")
        return temp
    
    def load(self, path): pass
    
    
    def save(self, path:str):
        return self.processor.dump(path, self.data)


"""
목표 클라이언트 코드

from utils.DB.DB_utils import *

sqlite = SqliteDB("VOCA.DB")
with DBOpen(sqlite) as db:
    data = db.load()

templ = TextTemplate("both")
workbook = workbook(templ, data)
workbook.save("workbook_ex.csv")
"""


if __name__ == "__main__":
    from utils.DB.DB_utils import *

    sqlite = SqliteDB("VOCA.DB")
    with DBOpen(sqlite) as db:
        data = db.load()

    templ = TextTemplate("both", 30)
    workbook = Workbook(templ, data)
    workbook.save("workbook_ex.csv")
    