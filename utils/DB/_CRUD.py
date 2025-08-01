import abc

class CRUDService(abc.ABC):
    def dump(self): raise NotImplementedError("미구현 되었습니다")
    def load(self): raise NotImplementedError("미구현 되었습니다")
    def get_all_datas(self): raise NotImplementedError("미구현 되었습니다")
    def update_item(self): raise NotImplementedError("미구현 되었습니다")
    def delete_item(self): raise NotImplementedError("미구현 되었습니다")
    def get_cursor(self): raise NotImplementedError("미구현 되었습니다")

class SqliteCRUD(CRUDService):
    def __init__(self, path):
        self.path = path
        