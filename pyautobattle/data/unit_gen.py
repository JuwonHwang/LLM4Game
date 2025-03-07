import csv
import random
import numpy as np

# # Define the path to your CSV file
# file_path = 'synergy.csv'

# synergies = []

# # Open and read the CSV file
# with open(file_path, mode='r', newline='', encoding='utf-8') as file:
#     csv_reader = csv.reader(file)
    
#     # Retrieve the header
#     header = next(csv_reader)
    
#     # Process each row in the CSV
#     for row in csv_reader:
#         # Example: Print each row
#         synergies.append(row[0])




import unicodedata

def get_emojis_in_range(start, end):
    """주어진 유니코드 범위 내에서 이모지 리스트를 반환"""
    return [chr(codepoint) for codepoint in range(start, end) if chr(codepoint).isprintable()]

# 유니코드 블록별 범위 정의
emoji_blocks = {
    "Miscellaneous Symbols and Pictographs": (000000, 0x1F5FF),
}

skin_tone_modifiers = ["🏻", "🏼", "🏽", "🏾", "🏿"]

def remove_skin_modifiers(text):
    """이모지에서 피부색 수정자를 제거"""
    return "".join(char for char in text if char not in skin_tone_modifiers)

def is_valid_emoji(char):
    """윈도우와 맥에서 공통적으로 지원하는 이모지 필터링"""
    try:
        name = unicodedata.name(char)
        # 특정 플랫폼 전용 이모지 제외 (예: 특정 OS, 브랜드 전용)
        if "VARIATION SELECTOR" in name or "TAG" in name:
            return False
        return True
    except ValueError:
        return False  # 이름이 없는 경우 (이모지가 아님)

emoji_dict = {}
emoji_set = set()
emojis = get_emojis_in_range(0x1F600, 0x1FAFF)
for emoji_char in emojis:
    filtered_emoji = remove_skin_modifiers(emoji_char)
    try:
        char = filtered_emoji[0]
    except:
        continue
    if is_valid_emoji(char):
        try:
            name = unicodedata.name(char)
            if len(name) < 12:
                emoji_set.add((char,name))
        except ValueError:
            pass

emoji_list = list(emoji_set)

random.shuffle(emoji_list)

# Define the CSV headers
headers = [
    "name", "cost", "hp", "mp", "attack", "defense", "attackSpeed",
    "specialAttack", "specialDefense", "criticalRate", "criticalDamage",
    "attackRange",
]

roles = ['warrior', 'tanker', 'mage', 'archer', 'monk'] * 13
random.shuffle(roles)

def generate_random_unit(name: str, cost: int, role: str):
    hp_list = [0, 50, 150, 250, 400]
    attack_list = [0, 5, 10, 20, 30]
    defense_list = [0, 5, 10, 20, 30]

    template = {
        "name": name,
        "cost": cost,
        "hp": 450 + hp_list[cost - 1],
        "mp": 40,
        "attack": 40 + attack_list[cost - 1] + random.randint(0,10),
        "defense": 20 + defense_list[cost - 1]+ random.randint(0,10),
        "attackSpeed": round(0.6 + 0.1 * random.random(),2),
        "specialAttack": 0,
        "specialDefense": 20 + defense_list[cost - 1] + random.randint(0,10),
        "criticalRate": 15,
        "criticalDamage": 1.5,
        "attackRange": 1,
    }
    
    if role == 'warrrior':
        template["hp"] += 100
        template["attack"] += 10
        template["attackSpeed"] += 0.2
    if role == 'tanker':
        template["attack"] -= 5
        template["hp"] += 150
        template["defense"] += 20
        template["specialDefense"] += 20
        template["attackSpeed"] += 0.2
    if role == 'mage':
        template["attack"] -= 10
        template["attackRange"] += random.randint(2,4)
    if role == 'archer':
        template["attack"] += 5
        template["attackRange"] += random.randint(3,5)
        template["attackSpeed"] += 0.4 * random.random()
        template["attackSpeed"] = round(template["attackSpeed"],2)
    if role == 'monk':
        template["attack"] -= 10
        template["hp"] += 150
        template["defense"] += 20
        template["specialDefense"] += 20
        template["attackRange"] += 1

    return template

def generate_units_csv(filename, num_units):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        unit_count = 1
        for cost in range(1,6):
            for i in range(num_units[cost-1]):
                unit = generate_random_unit(f"{emoji_list[unit_count][1]}", cost, roles[unit_count])
                writer.writerow(unit)
                unit_count += 1
                
num_units = [
    14,
    13,
    13,
    12,
    8
]

generate_units_csv('unit.csv', num_units)
