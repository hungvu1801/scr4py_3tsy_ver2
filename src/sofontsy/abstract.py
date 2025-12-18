from abc import ABC, abstractmethod
from typing import Optional
from .elems import SofontsyItems
from selenium import webdriver


class Upload:
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def set_current_item(self, item: Optional[SofontsyItems]):
        self.current_item = item

    def next_step(self, upload_state: "UploadState"):
        self._upload_state = upload_state
        self._upload_state.upload = self


class UploadState(ABC):
    @property
    def upload(self) -> Upload:
        return self._upload

    @upload.setter
    def upload(self, upload: Upload):
        self._upload = upload

    @abstractmethod
    def handle(self) -> int: ...
