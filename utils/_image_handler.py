import abc
from PIL import Image

class _image_handler(abc.ABC):
    def load(self, path, encoding='utf-8'):
        pass

    def dump(self, path, data, encoding='utf-8'):
        pass

class jpgHandler(_image_handler):
    def load(self, path, encoding='utf-8'):
        pass

    def dump(self, path, data, encoding='utf-8'):
        pass

class pngHandler(_image_handler):
    def load(self, path, encoding='utf-8'):
        pass

    def dump(self, path, data, encoding='utf-8'):
        pass