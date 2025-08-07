import re
import abc
import csv
import xml.etree.ElementTree as ET
import json

class _text_handler(abc.ABC):
    @abc.abstractmethod
    def load(self, path, encoding) -> list:
        pass

    @abc.abstractmethod
    def dump(self, path, data, encoding) -> bool:
        pass

class txtHandler(_text_handler):
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
    
class csvHandler(_text_handler):
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

class jsonHandler(_text_handler):
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

class xmlHandler(_text_handler):
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