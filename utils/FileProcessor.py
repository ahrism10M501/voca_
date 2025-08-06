# ToListFactory
# 어떤 파일을 받느냐에 따라서 다르게 동작해야만 한다.
# 이를 구현하기 위해, 팩토리 메서드 패턴이나 추상 팩토리 패턴을 활용해서 만들어보자.

# txt, csv, json... -> list

"""
파일 입출력을 일정한 양식에 맞추어서 가능케 하는 프로세서 클래스.
원하는 포맷인 [(), (), ...] 으로 값을 받아오고,
그 포맷으로 데이터를 변환하거나,
파일로 출력하는 클래스.
"""

import re
import abc
import csv
import xml.etree.ElementTree as ET
import json

__all__ = ['TextFileProcessor']

class StringToList(abc.ABC):
    @abc.abstractmethod
    def load(self, path, encoding) -> list:
        pass

    @abc.abstractmethod
    def dump(self, path, data, encoding) -> bool:
        pass

class txtHandler(StringToList):
    def load(self, path, encoding) -> list:
        voca = []
        with open(path, 'r', encoding=encoding) as f:
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
    
    def dump(self, path, data, encoding) -> bool:
        with open(path, 'w', encoding=encoding) as f:
            for word, meaning in data:
                if isinstance(meaning, list|tuple):
                    meaning = ','.join(meaning)
                f.write(f"{word}:{meaning}\n")
        return True
    
class csvHandler(StringToList):
    def load(self, path, encoding) -> list:
        voca = []
        with open(path, 'r', encoding=encoding) as f:
            rdr = csv.reader(f)
            for line in rdr:
                if not line:
                    continue
                word = line[0]
                meaning = line[1]
                meanings = re.split(r'[;,]', meaning.strip())
                for mean in meanings:
                    mean = mean.strip()
                    if mean:
                        voca.append((word, mean))
        return voca
    
    def dump(self, path, data, encoding) -> bool:
        with open(path, 'w', encoding=encoding) as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['word', 'meaning'])
            for word, meaning in data:
                writer.writerow([word, meaning])
        return True

class jsonHandler(StringToList):
    def load(self, path, encoding) -> list:
        voca = []
        with open(path, 'r', encoding=encoding) as f:
            data = json.load(f)
            for item in data:  # 예: [{ "word": "apple", "meaning": "과일" }, ...]
                word = item.get("word", "").strip()
                meanings = re.split(r'[;,]', item.get("meaning", "").strip())
                for mean in meanings:
                    mean = mean.strip()
                    if mean:
                        voca.append((word, mean))
        return voca
    
    def dump(self, path, data, encoding) -> bool:
        with open(path, 'w', encoding=encoding) as f:
            temp = []
            for word, meaning in data:
                if isinstance(meaning, list|tuple):
                    meaning = ','.join(meaning)
                temp.append({'word':word, 'meaning':meaning})
            json.dump(temp, f, ensure_ascii=False, indent=2)
        return True

class xmlHandler(StringToList):
    def load(self, path, encoding) -> list:
        tree = ET.parse(path)
        root = tree.getroot()
        rows = root.findall("row")
        voca = []
        for row in rows:
            word = row.get('word')
            meaning = row.get('meaning')
            voca.append((word, meaning))
        return voca
    
    def dump(self, path, data, encoding) -> bool:
        root = ET.Element('data')
        for word, meaning in data:
            row = ET.SubElement(root, 'row')
            row.set("word", word)
            row.set("meaning", meaning if isinstance(meaning, str) else ','.join(meaning))

        tree = ET.ElementTree(root)
        tree.write(path, encoding=encoding, xml_declaration=True)
        return True

class TextFileProcessor:
    @staticmethod
    def _get_handler(path:str) -> StringToList:
        if path.endswith(".txt"):
            return txtHandler()
        elif path.endswith(".csv"):
            return csvHandler()
        elif path.endswith(".json"):
            return jsonHandler()
        elif path.endswith(".xml"):
            return xmlHandler()
        else:
            raise ValueError("지원하지 않는 파일 형식 입니다.")
        
    @staticmethod
    def load(path, encoding='utf-8') -> list:
        handler = TextFileProcessor._get_handler(path)
        return handler.load(path, encoding)
    
    @staticmethod
    def _PreProcess(data) -> list|tuple:
        """
        서브 클래스에 일관된 데이터를 전송해줍니다. 이를 통해 코드를 좀 더 쉽게 유지보수 할 수 있습니다!
        만약, 다양한 형식을 추가하고 싶다면 새로운 유틸 클래스를 만드는 것을 추천합니다.
        return [(word, meaning), (word, meaning), ...]
        """
        if isinstance(data, (list, tuple)):
            for item in data:
                if not (isinstance(item, (list, tuple)) and len(item) == 2):
                    raise TypeError("각 항목은 (단어, 뜻) pair여야합니다.")
            return data
        
        elif isinstance(data, dict):
            temp = []
            for item in data:
                word = item["word"]
                meaning = item["meaning"]
                item.append((word, meaning))
            return temp
        
        else:
            raise TypeError("Data의 형식이 수상합니다")
    
    @staticmethod
    def dump(path, data, encoding='utf-8') -> bool:
        """
        Data 는 반드시 1개의 단어와 1개의 뜻으로 쌍을 이룬
        2차원 형식의 배열이어야 합니다.
        return [(word, meaning), (word, meaning), ...]
        """
        handler = TextFileProcessor._get_handler(path)
        data = TextFileProcessor._PreProcess(data)
        return handler.dump(path, data, encoding)