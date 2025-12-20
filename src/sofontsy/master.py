from abc import abstractmethod

class Master:
    _pipeline: tuple = ()

    def __init__(self, upload):
        self.upload = upload
        
    @property
    def pipeline(self) -> tuple:
        return self._pipeline

    @pipeline.setter
    def pipeline(self, value: tuple) -> None:
        self._pipeline = value

    @abstractmethod
    def next_state(self): ...


