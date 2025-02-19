from abc import ABC, abstractmethod

EMPTY = " " * 20

class Base(ABC):
    def __init__(self):
        return
    
    @abstractmethod
    def observe(self):
        pass
    
    @abstractmethod
    def to_json(self):
        pass