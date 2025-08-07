# 자동으로 문제지를 만드는 프로그램을 만들어 봅시다

import abc
import random
from utils.FileProcessor import *

class VocaTemplate(abc.ABC):
    def __init__(self, type:str, num:int):
        self.type = type
        self.num_word = num
        self.ratio = 0.5
        self.blank = "___"

    def set_ratio(self, ratio): self.ratio = ratio; return self
    def set_blank(self, blank): self.blank = blank; return self
    def set_seed(self, seed): random.seed(seed); return True

class TextTemplate(VocaTemplate):
    def __init__(self, type, num):
        super().__init__(type, num)
        self.indent = 1

    def set_indent(self, indent): self.indent = indent; return self

class ImageTemplate(VocaTemplate):
    def __init__(self, type,num):
        super().__init__(type, num)
        self.size = (2480, 3508) # DPI 300, A4
        self.DPI = 300
        self.space_between_word = 15
        # 만약 사진 파일 path가 들어오면 이미지 경로, 차후 파싱을 통해 해결
        # pillow lib 을 사용할 예정(한국어 처리 용이)
        self.background = "#white"
        self.font = ''
        self.font_color = '#black'
        self.font_size = 20

    def set_size(self, width, height): self.size = (width, height); return self
    def set_dpi(self, dpi): self.DPI = dpi; return self
    def set_space(self, space): self.space_between_word = space; return self
    def set_background(self, backgorund): self.background = backgorund; return self
    def set_font(self, font_path): self.font = font_path; return self
    def set_color(self, color): self.font_color = color; return self
    def set_font_size(self, size): self.font_size = size; return self

class Workbook:
    def __init__(self, temp:VocaTemplate, data:list|tuple):
        self.template = temp
        self.data = self._blanker(self._preprocess(data))

    def _preprocess(self, data):
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
        return random.sample(temp, self.template.num_word)
    
    def _blanker(self, data):
        temp = []
        if self.template.type == 'ko':
            for word, mean in data:
                temp.append((mean, self.template.blank))
        elif self.template.type == 'en':
            for word, mean in data:
                temp.append((word, self.template.blank))
        elif self.template.type == 'both':
            for row in data:
                if random.random() < self.template.ratio:
                    temp.append((row[0], self.template.blank))
                else:
                    temp.append((row[1], self.template.blank))
        else:
            raise ValueError("Invalid Form Type")
        return temp
    
    def load(self, path, encoding='utf-8'):
        return FileProcessor.load(path, encoding)
    
    def save(self, path:str, encoding='utf-8'):
        return FileProcessor.dump(path, self.data, encoding)

"""
목표 클라이언트 코드

from utils.DB.DB_utils import *

sqlite = SqliteDB("VOCA.DB")
with DBOpen(sqlite) as db:
    data = db.load()

templ = TextTemplate("both")
workbook = workbook(templ, data)
workbook.save("workbook_ex.csv")

img_templ = ImageTemplate("ko") # 한국어가 보이고, 영어가 가려짐
workboo.save("img_workbook_ex.jpg") #jpg, png, webp, raw, jpeg... endwith로 검사?

"""


if __name__ == "__main__":
    from utils.DB.DB_utils import *

    sqlite = SqliteDB("VOCA.DB")
    with DBOpen(sqlite) as db:
        data = db.load()

    templ = (TextTemplate("both", 30)
             .set_ratio(0.4)
             .set_blank("[   ]"))
    workbook = Workbook(templ, data)
    workbook.save("workbook_ex.csv")
    