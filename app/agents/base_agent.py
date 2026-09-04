from abc import ABC, abstractmethod


class BaseAgent(ABC):
    name: str
    role: str
    description: str

    @abstractmethod
    def analyse(self, *args, **kwargs): ...
