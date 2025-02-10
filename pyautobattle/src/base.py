from abc import ABC, abstractmethod

class Base(ABC):
    def __init__(self):
        return
    
    @abstractmethod
    def observe(self):
        pass