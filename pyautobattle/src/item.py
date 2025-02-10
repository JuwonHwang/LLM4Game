from .active import Active
from .status import Status

class Item(Active, Status):
    def __init__(self):
        super().__init__()
        return
    
    def observe(self):
        pass