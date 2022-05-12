from typing import List


class Option(object):
    def __init__(self, option_str: str, param: List[str]):
        self.option_str = option_str
        self.param = param

    @abstractmethod
    def dump(self) -> str:
        raise NotImplementedError()


class PureOption(Option):
    def __init__(self, option_str, prefix=''):
        super().__init__(option_str, [])

    def dump(self):
        pass


class ParamOption(Option):
    def __init__(self, option_str, param, prefix):
        super().__init__(option_str, param)

    def dump(self):
        pass