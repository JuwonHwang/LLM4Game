from abc import ABC, abstractmethod

EMPTY = " " * 18

class Base(ABC):
    def __init__(self):
        return
    
    @abstractmethod
    def observe(self):
        pass