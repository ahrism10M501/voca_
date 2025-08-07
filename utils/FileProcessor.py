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

import os
import re
import abc
from utils._text_handler import _text_handler, txtHandler, csvHandler, jsonHandler, xmlHandler
from utils._image_handler import _image_handler, jpgHandler, pngHandler

__all__ = ['FileProcessor']

class FileProcessor():
    _HANDELERS = {
        ".txt":txtHandler,
        ".csv":csvHandler,
        ".json":jsonHandler,
        ".xml":xmlHandler
    }

    @staticmethod
    def _get_handler(path:str) -> _text_handler:
        _, extension = os.path.splitext(path)
        try:
            return FileProcessor._HANDELERS[extension]()
        except:
            raise ValueError(f"지원하지 않는 파일 형식 입니다: {extension} ")
        
    @staticmethod
    def _PreProcess(data:list|tuple) -> list|tuple:
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
    def load(path, encoding='utf-8') -> list:
        handler = FileProcessor._get_handler(path)
        return handler.load(path, encoding)
    
    @staticmethod
    def dump(path:str, data:list|tuple, encoding='utf-8') -> bool:
        """
        Data 는 반드시 1개의 단어와 1개의 뜻으로 쌍을 이룬
        2차원 형식의 배열이어야 합니다.
        return [(word, meaning), (word, meaning), ...]
        """
        handler = FileProcessor._get_handler(path)
        data = FileProcessor._PreProcess(data)
        return handler.dump(path, data, encoding)