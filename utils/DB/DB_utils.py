"""
디자인 패턴 연습용 프로젝트 이므로 오버엔지니어링은 어쩔 수 없다! 그래도 연습했잖아~ 한잔해~

어떤 형상으로 만들까?
1. 여러 DB를 사용할 수 있다고 가정
 - 만약 sqlite3가 아니라 mysql, oracle, Mongo를 사용할때, 전의 코드는 로직을 다 바꿔야했다.
 => DBConnect는 DBRepo를 받는다. DBRepo는 추상 클래스, 자식으로 Sqlite3Repo, MySQLRepo, MongoRepo... 등을 가진다. 

2. 책임 분리
 - load, dump, get, set, update, delete에 대한 책임을 분산하자.
 => 마찬가지로 DBConnect 클래스로 다양한 서비스를 호출하고, 그들은 각자의 추상 클래스로 개발된다. 정격 아웃풋이 있으므로, 하위 메서드는 이를 구현하면 될 뿐.
  궁금증은, 각 repo가 구현되었다면, 이것들을 구현하는것도 repo에게 맡겨야 할까?

  예를 들어

  DBConnect는 repo를 가진다. commit과 같은 인스턴스 호출 시 의존성 주입으로 새겨진 repo에 접근해서 이를 처리한다.
  repo는 dump, load 등의 추상 클래스를 가진다. 이들은 팩토리 메서드를 이용해 분리된다?
  근데 여기서 굳이 해야 할 까 라는 의문. dump와 load는 이미 repo를 통해 나뉜 상태임. 여기서 repo의 책임을 낮추기 위해서 하위 인스턴스를 패턴화해서 사용할 필요가 있을까?

  어차피 각 db마다 dump나 load의 형식이 다른텐데, repo마다 하나씩이니까 상관없는거 아닌가?


    DBRepository, ConnectionHandler, QueryService 로 기능 구분
    CRUD , Connection, Query
    DB repository는 DBIMplementor를 사용
    DBimplementor를 상속 받는 각 db의 구현체 ex) sqliteImplementor
    --> DBConnect를 DBrepository 위치에 넣어야 할 듯

    db = sqliteImlementor()
    with DBConnect(db) as db:
        db.load


    DBRepository에다가 Implementor를 주입해서 그걸 사용하는거지.
    올바른 crud 객체를 받아와서 그 안의 메서드를 사용하는거임
    이때 crud 객체는 implementor가 반환해줌

    이제 직접적인 구현은 DBRepo가 하믄 됨.
    즉, 쓰잘데기 없는건 다른 애들이 해주고, 명령은 DBRepo가 내린다!

    왕과 귀족과 하인 들로 이루어진 우아한 권력 계층 ㄷㄷ

    bridge -> strategy

    브릿지를 쓰는 이유는 DBOpen 녀석이 지혼자 이상한 기능을 만들 수도 있기 떄문이다! 
    코드 유연성 확보!!! CRUD를 기본 바탕으로 고급 구현을 하는거지.
    예를 들어, 난이도 별로 뽑아오기
    뭐 이런거

"""

import logging
import abc
import sqlite3
from typing import Optional
from utils.DB._IConnection import *
from utils.DB._ICRUD import *
from utils.FileProcessor import *

class DBOpen:
    def __init__(self, implementor: 'DBImplementor'):
        self.impl = implementor
        self.crud: ICRUD|None = None

    def load(self, order_by=None):
        if not self.crud:
            raise ConnectionError
        return self.crud.load(order_by)

    def filter(self, data, condition:dict):
        # data must be data earning by 'load' method
        # 만약 util이 더 많아지면 따로 빼기. 다른 데이터를 불러오는 함수는 정격화된 출력을 return해야하므로 db에 넣음
        # FIXME : Hardcoding
        condition_enum = {
            "word_id":0,
            "word":1,
            "day":2,
            "level":3,
            "meaning_id":4,
            "word_id":5,
            "meaning":6
        }
        filtered_data = []
        for k, v in condition.items():
           filtered_data.append(filter(lambda x: x[condition_enum[k]]> v, data))
        return filtered_data

    def dump(self, vocas, day, level):
        """
        vocas = [(word, meaning), (..., ...)]
        """
        if not self.crud:
            raise ConnectionError
        return self.crud.dump(vocas, day, level)

    def dump_to_file(self, path):
        if not self.crud:
            raise ConnectionError
        data = self.crud.find(columns=["word", "meaning"])
        fp = FileProcessor()
        return fp.dump(path, data)

    def find(self, condition:dict|None=None, columns:list|None=None):
        """
        condition은 {column1:value1, column2:value2} 의 딕셔너리 형태
        columns는 [column1, column2] 의 리스트 형태
        return은 [(values), (...)] 의 list(tuple(values)) 형태
        """
        if not self.crud:
            raise ConnectionError
        return self.crud.find(condition, columns)
    
    def update(self, condition:dict, data:dict):
        if not self.crud:
            raise ConnectionError
        return self.crud.update(condition, data)

    def delete(self, condition:dict):
        if not self.crud:
            raise ConnectionError
        return self.crud.delete(condition)

    def __enter__(self):
        self.crud = self.impl.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        return self.impl.__exit__(exc_type, exc_value, exc_tb)
    
class DBImplementor:
    @abc.abstractmethod
    def filter(self, data, condition) -> list: pass
    @abc.abstractmethod
    def __enter__(self) -> 'ICRUD': pass
    @abc.abstractmethod
    def __exit__(self, exc_type, exc_value, exc_tb) -> bool|None: pass

class SqliteDB(DBImplementor):
    def __init__(self, path):
        self.path = path
        self.connection_handler:IConnection = SqliteConnection(path)
        self.cur:Optional[sqlite3.Cursor] = None

    def __enter__(self) -> 'ICRUD':
        self.connection_handler.connect()
        self.cur = self.connection_handler.get_cursor()
        self.crud = SqliteCRUD(self.connection_handler)
        return self.crud
    
    def __exit__(self, exc_type, exc_value, exc_tb) -> Optional[bool]:
        try:
            if exc_type is None:
                self.connection_handler.commit()
            else:
                self.connection_handler.rollback()
            self.connection_handler.close()
        except Exception as e:
            print(f"Exit handling error: {e}")
            return False
        finally:
            return exc_type is None