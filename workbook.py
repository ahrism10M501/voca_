# 자동으로 문제지를 만드는 프로그램을 만들어 봅시다

"""
Client 동작

1. 원하는 DB 설정하기
2. DB에서 단어 load하기
3. 원하는 문제 형식과 day, level, 단어 개수 등으로 voca_form 객체 초기화 하기
=> 문제 형식: 한국어 빈칸, 영어 빈칸, 혼용
4. DB에서 load한 데이터를 넣어주고 make하기
5. 원하는 형식으로 화면에 띄우거나 파일로 저장하기
=> 간단한 파일, txt, json, csv, xml 부터 pdf, jpg, png까지. 된다면 tts를 이용해서 mp3나 wav까지
"""

"""
Client 동작 예시

database = SqliteDB("VOCA.DB")
with DBOpen(database) as db:
    data = db.load() # List[Tuple]

template = VocaTemplate(type="kr", day=[3], level=[0:5], num=30)
template.seed(2025)
workbook = template.make(data)

path = 'C:/Users/user1/Desktop'
workbook.save(PDFWriter(f"{path}/workbook1.pdf"))
workbook.save(JPGWriter(f"{path}/workbook2.jpg")) # 만약 여러 장의 문제지가 만들어질시 해당 이름의 파일을 만들고 뒤에 (0), (1) 처럼 붙여서 jpg로 저장
"""

"""
구조 설계

class
VocaTemplate, 문제지를 어떤 형태로 만들 것인지에 대한 전체적인 설계도 보유. 미리 등록된 특정 사진을 지정하면 그걸 토대로 처리함. -> 따로 템플릿 파일 형식을 만들어야 할듯
template.make는 또 다른 객체(workbook)를 반한함.
이를 따로 저장할 수 있음.

template를 저장해서 나중에 load하는 방식으로 사용할 수도 있고,
workbook 형식을 저장했다가 여러 번 꺼내 쓸 수도 있게 만들거임. -> 이것도 파일 형식을 새로 만들어야할듯

따라서

class VocaTemplate 은 일반 객체

class workbook은 팩토리 메서드로 구현.
파일 명을 받고 그 파일명에 알맞는 handler를 이용해서 데이터 처리.
오히려 전략 메서드 어떰

"""

"""
클래스 설계

class VocaTemplate(abc.ABC):
    def __init__(self, type, day, level, num)
    def seed(self, num)
    @abc. ...
    def make(self, data)
    @staticmethod
    def _preprocess(data) -> List[Tuple]
        # 데이터를 type에 따라 blur 처리
        # 데이터의 level, day 등에 따라 처리
        # 모든 입력 데이터 형식은 같고, 출력값도 같으므로 staticmethod로 상속

class ImageTemplate(VocaTemplate):
    def __init__(self, path, type, day, level, num):
    super().__init__(type, day, level, num)
    def make(self, data) :
        data = _preprocess(data)
        data = {"image":self.path, "form":[(사진 별 위치)], "data":data}
        return Workbook(data)
    
class TextTemplate(VocaTemplate):
    def __init__(self, type, day, level, num)
    def make(self, data):
        return Workbook
    
class Workbook:
    def __init__(self, data):
        self.data = data # Dict[str, Tuple]
    def load(self, reader:FileReader)
    def save(self, writer:FileWriter):
        writer.write(self.data)

class FileWriter(abc.ABC):
    @abc.abstractmethod
    def save(self, path:str) -> bool        

class JPGWriter():
    def __init__(self, data:Dict); self.data = data
    def save(self, path):
        # JPG save logic
        return True

class PDFWriter():
    def __init__(self, data:Dict); self.data = data
    def save(self, path):
        # PDF save logic
        return True
"""

"""
구현 전 설계 리뷰

원하는 템플릿을 선택하므로 구분이 뚜렷하다.
만약 VocaTemplate로만 지정하고 filepath에 따라 바뀌었으면 디버깅 떄 찾기 힘들 듯. 이러면 어디서 어떻게 바뀌고 있는지 클래스 명으로 추적하면 되니까 편하다.
만약 다른 템플릿을 추가할때는 그대로 추가만 하면 됨!

workbook은 FileWriter를 의존성 주입 받아서 사용한다. 따라서 workbook은 FileWriter를 몰라도 된다. 결합이 약해요.
이에 따라 복잡한 로직 필요없다.

--> textWorkbook과 imageworkbook으로 변경해야할까?
    지금은 일반 Filewriter를 제공 받는데, 여기서 이미 파일이 나뉜다. 이때 Image인데 text를 사용하면 이상해진다. encoding에러 마냥, 딕셔너리를에서 get하는 부분에서 에러날것.

FileWriter는 계속 추가가능하다!
전략 패턴을 사용해서 편의성이 높아졌다.

고민해볼점.

TextTemplate과 ImageTemplate을 나눈 이유가 있을까?
-> 데이터 자체를 다르게 저장해서 넘기기 떄문에 이유가 있다.
특히 다른 Template 추가 시 지금 구조가 더 합리적이다.

workbook을 나눌까?
-> 그냥 주석으로 달아주자. 사용하는 사람이 알아서 조정하도록. 이정도는 괜찮잖아. 안정성을 생각하면 나누는게 맞지만 클래스가 너무 복잡해진다.
물론, 나중에 너무 많아지면 나누는걸 고려해야한다. 파일을 분리해서 각 세션마다 관리하는 것이 좋겠다.

writer?
새로운 기능 추가 할 떄 writer 건들지 않아도 된다.
예를 들어 workbook에 load, write 말고 share라는 식으로 다른 앱으로 연결 및 공유하는 기능이 들어간다고 해보자. 이때, 다른 부분은 건들필요 없이

workbook에는 share를 추가하고 관련된 전략 클래스들을 생성해주면 된다. AppSharer 와 같은 식으로 혹은 다른 방식으로 해결해줘도 된다. 팩토리 식으로 들어간다든지... 이것저것

특히 TextWriter 종류는 FileProcessor를 사용하고 싶으니, 나는 미리미리 수정을 해야하겠다.
"""

# 애초에 데이터를 정제해서 넘겨받으면 되는거 아니냐?
# 애초에 원하는 day, level의 데이터를 클라이언트가 준다면 전체적으로 쉬워짐


"""
사용 예시
path = "VOCA.DB"
sqiltedb = sqilteDB(path)

with DBOpen(sqlitedb) as db:
    data = db.load()
    data = db.filter(data, condition:dict)

template = ImageTemplate("ko", 30)
workbook = template.make(data)
# 같은 데이터도 여러 템플릿으로 만들 수 있는 유연성 제공

# workbook의 내용을 저장해놓고 나중에 다시 불러오기 가능
workbook.dump(save_path) # Workbook객체를 저장하는 법?
workbook.save(JPGWriter(save_path))
"""

import abc
import random
from typing import Dict, Tuple
from PIL import Image

class VocaTemplate(abc.ABC):
    def __init__(self, type):
        self.type = type
        self.ratio = 0.5 # ratio가 1에 가까울 수록 영어를 블러처리( both에 대한 해결책)

    def seed(self, seed):
        random.seed(seed)
        return True
    
    @abc.abstractmethod
    def make(self, voca) -> 'Workbook': pass

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
    
    def blanker(self, data, blank_type="_____"):
        temp = []
        if self.type == 'ko':
            for word, mean in data:
                temp.append((mean, blank_type))
        elif self.type == 'en':
            for word, mean in data:
                temp.append((word, blank_type))
        elif self.type == 'both':
            # FIXME : 임시 조치로 비율을 대충 산정함. ratio가 더 덩당하게 적용되도록 만들어야한다.
            choice = round(random.random()+self.ratio/2)
            for row in data:
                temp.append((row[choice], blank_type))
        else:
            raise ValueError("Invalid Form Type")
        return temp

class TextTemplate(VocaTemplate):
    def __init__(self, type):
        super().__init__(type)

    def make(self, voca):
        data = VocaTemplate._preprocess(voca)
        data = self.blanker(data)
        return Workbook(data)

class ImageTemplate(VocaTemplate):
    def __init__(self, path, type):
        super().__init__(type)
        self.path = path

    def make(self, voca):
        data = VocaTemplate._preprocess(voca)
        data = self.blanker(data)
        writer_data = {}
        writer_data["path"] = self.path
        # 이미지 마다 어떤 위치에 어떤 식으로 글자를 쓸 것인지 미리 지정해주어야 한다.
        # 이를 어떻게 저장하고 있을 것이며, 어떻게 처리할 것인가?
        writer_data["image"] = Image.open(self.path) # 미구현
        writer_data["pos"] = open(self.path).read()
        writer_data["voca"] = data
        return Workbook(writer_data)

from utils.FileProcessor import TextFileProcessor

class FileWriter(abc.ABC):
    @abc.abstractmethod
    def write(self, data): pass
    
class ImageWriter(FileWriter):
    def __init__(self, save_path):
        self._save_path = save_path

    def write(self, data):
        pass

class TextWriter(FileWriter):
    def __init__(self, save_path):
        self._save_path = save_path
    def write(self, data):
        TextFileProcessor.dump(self._save_path, data)

class Workbook:
    def __init__(self, data):
        self.data = data

    def load(self):
        pass

    def save(self, writer:FileWriter):
        return writer.write(self.data)
    
# 패턴 수준... 복잡시러워!!! 
# 구조 다시 짜야 할 듯. 특히 Image, Text 나누는 것부터 잘못됨.

if __name__ == "__main__":
    from utils.DB.DB_utils import *
    
    sqlite = SqliteDB("VOCA.DB")
    with DBOpen(sqlite) as db:
        data = db.load()

    templ = TextTemplate("ko")
    workbook = templ.make(data[:20])

    workbook.save(TextWriter("workbook_ex.csv"))
    