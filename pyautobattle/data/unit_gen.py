import csv
import random
import numpy as np

# Define the path to your CSV file
file_path = 'synergy.csv'

synergies = []

# Open and read the CSV file
with open(file_path, mode='r', newline='', encoding='utf-8') as file:
    csv_reader = csv.reader(file)
    
    # Retrieve the header
    header = next(csv_reader)
    
    # Process each row in the CSV
    for row in csv_reader:
        # Example: Print each row
        synergies.append(row[0])


# Define the CSV headers
headers = [
    "name", "cost", "hp", "mp", "attack", "defense", "attackSpeed",
    "specialAttack", "specialDefense", "criticalRate", "criticalDamage",
    "attackRange",
]

def generate_random_unit(name: str, cost: int):
    hp_list = [0, 50, 150, 250, 400]
    attack_list = [0, 5, 10, 20, 30]
    return {
        "name": name,
        "cost": cost,
        "hp": 150 + hp_list[cost - 1] + 10 * random.randint(5, 10),
        "mp": 40 + 10 * random.randint(0, 8),
        "attack": 40 + attack_list[cost - 1] + random.randint(0, 10),
        "defense": random.randint(10, 40),
        "attackSpeed": round(random.uniform(0.8, 1.0), 2),
        "specialAttack": random.randint(20, 60),
        "specialDefense": random.randint(10, 40),
        "criticalRate": 15,
        "criticalDamage": 1.5,
        "attackRange": random.randint(1, 5),
    }

def generate_units_csv(filename, num_units):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        unit_count = 1
        for cost in range(1,6):
            for i in range(num_units[cost-1]):
                unit = generate_random_unit(f"unit_{cost}_{i+1:02}", cost)
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
