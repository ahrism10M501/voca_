import abc

class QueryService:
    @abc.abstractmethod
    def findWordById(self):
        pass
    @abc.abstractmethod
    def findMeaningById(self):
        pass
    @abc.abstractmethod
    def findWordByMeaning(self):
        pass
    @abc.abstractmethod
    def findMeaningByWord(self):
        pass
    @abc.abstractmethod
    def findWordByDay(self):
        pass
    @abc.abstractmethod
    def findWordByLevel(self):
        pass

class SqliteQueryService(QueryService):
    def __init__(self, cur):
        self.cur = cur