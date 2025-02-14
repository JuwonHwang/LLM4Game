class Color:
    RESET = '\033[0m'
    def __init__(self, r,g,b):
        self.r = r
        self.g = g
        self.b = b
        
    def __str__(self):
        return f'\033[38;2;{self.r};{self.g};{self.b}m'

    def __add__(self, other):
        return str(self) + other

class Gold():
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return Color(255,228,0) + f"${self.value}" + Color.RESET
    
def red(content: str):
    return Color(241,95,95) + str(content) + Color.RESET

def blue(content: str):
    return Color(0,0,255) + str(content) + Color.RESET

def green(content: str):
    return Color(65,175,57) + str(content) + Color.RESET

def magenta(content: str):
    return Color(171,18,155) + str(content) + Color.RESET

def cyan(content: str):
    return Color(0,255,255) + str(content) + Color.RESET

def yellow(content: str):
    return Color(255,255,0) + str(content) + Color.RESET

def grey(content: str):
    return Color(166,166,166) + str(content) + Color.RESET

def gold(content: str):
    return Color(225,210,72) + str(content) + Color.RESET

def silver(content: str):
    return Color(234,234,234) + str(content) + Color.RESET

def bronze(content: str):
    return Color(171,130,18) + str(content) + Color.RESET

def platinum(content: str):
    return Color(178,235,244) + str(content) + Color.RESET

def star_color(level: int):
    star = "*" * level
    star = f"<{star}>"
    star = f"{star:^5}"
    if level == 1:
        return bronze(star)
    elif level == 2:
        return silver(star)
    elif level == 3:
        return gold(star)
    elif level == 4:
        return platinum(star)
    else:
        return star

def auto_color(content: str, num: int):
    if num == 2:
        return green(content)
    elif num == 3:
        return blue(content)
    elif num == 4:
        return magenta(content)
    elif num == 5:
        return yellow(content)
    else:
        return str(content)