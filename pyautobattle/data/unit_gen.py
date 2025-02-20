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


# Define the CSV headers
headers = [
    "name", "cost", "hp", "mp", "attack", "defense", "attackSpeed",
    "specialAttack", "specialDefense", "criticalRate", "criticalDamage",
    "attackRange",
]

def generate_random_unit(name: str, cost: int):
    hp_list = [0, 50, 150, 250, 400]
    attack_list = [0, 5, 10, 20, 30]
    defense = 20 + 5 * (random.randint(0, 4) + cost - 1)
    return {
        "name": name,
        "cost": cost,
        "hp": 450 + hp_list[cost - 1] + 50 * random.randint(0, 4),
        "mp": 40 + 10 * random.randint(0, 8),
        "attack": 40 + attack_list[cost - 1] + random.randint(0, 10),
        "defense": defense,
        "attackSpeed": round(random.uniform(0.6, 1.0), 2),
        "specialAttack": 0,
        "specialDefense": defense,
        "criticalRate": 15,
        "criticalDamage": 1.5,
        "attackRange": random.randint(1, 5),
    }

import emoji
import unicodedata

def get_emojis_in_range(start, end):
    """주어진 유니코드 범위 내에서 이모지 리스트를 반환"""
    return [chr(codepoint) for codepoint in range(start, end) if chr(codepoint).isprintable()]

# 유니코드 블록별 범위 정의
emoji_blocks = {
    "Miscellaneous Symbols and Pictographs": (0x1F300, 0x1F5FF),
    "Emoticons": (0x1F600, 0x1F64F),
    "Transport and Map Symbols": (0x1F680, 0x1F6FF),
    "Miscellaneous Symbols": (0x2600, 0x26FF),
    "Dingbats": (0x2700, 0x27BF),
    "Supplemental Symbols and Pictographs": (0x1F900, 0x1F9FF),
    "Symbols and Pictographs Extended-A": (0x1FA70, 0x1FAFF),
    "Symbols for Legacy Computing": (0x1FB00, 0x1FBFF),
    "Ornamental Dingbats": (0x1F650, 0x1F67F),
    "Alchemical Symbols": (0x1F700, 0x1F77F),
    "Geometric Shapes Extended": (0x1F780, 0x1F7FF),
}

skin_tone_modifiers = ["🏻", "🏼", "🏽", "🏾", "🏿"]

def remove_skin_modifiers(text):
    """이모지에서 피부색 수정자를 제거"""
    return "".join(char for char in text if char not in skin_tone_modifiers)

emoji_dict = {}
emoji_set = set()
for name, block in emoji_blocks.items():
    emojis = get_emojis_in_range(block[0], block[1])
    for emoji_char in emojis:
        filtered_emoji = remove_skin_modifiers(emoji_char)  # ✅ 피부색만 제거
        try:
            char = filtered_emoji[0]
        except:
            continue
        try:
            name = unicodedata.name(char)
            if len(name) < 12:
                emoji_set.add((char,name))
        except ValueError:
            pass

emoji_list = list(emoji_set)
random.shuffle(emoji_list)
print(emoji_list)

def generate_units_csv(filename, num_units):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        unit_count = 1
        for cost in range(1,6):
            for i in range(num_units[cost-1]):
                unit = generate_random_unit(f"{emoji_list[unit_count][1]}", cost)
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
