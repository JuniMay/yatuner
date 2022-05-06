from typing import List

class Option(object):

    def __init__(self, option_str: str, param: List[str]):
        self.option_str = option_str
        self.param = param

    @abstractmethod
    def dump(self):
        raise NotImplementedError()
