from abc import ABC, abstractmethod

class BaseCommand(ABC):
    name = ""

    @abstractmethod
    def execute(self, args: str) -> str:
        pass