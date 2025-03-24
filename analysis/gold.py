import os
import json

# 읽어올 폴더 경로
folder_path = '../replay/direct_vs_ex_cot'

# 모든 JSON 데이터를 담을 리스트
json_list = []

# 폴더 내 파일들 순회
for filename in os.listdir(folder_path):
    if filename.endswith('.json'):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                json_list.append(data)
            except json.JSONDecodeError as e:
                print(f"파일 {filename}에서 JSON 에러 발생: {e}")

def average(a):
    return sum(a) / len(a)

# 결과 확인
avg_interest = {}
avg_streak_gold = {}
avg_action_len = {}
for replay in json_list:
    for player_id, history in replay.items():
        if player_id not in avg_interest.keys():
            avg_interest[player_id] = []
            avg_streak_gold[player_id] = []
            avg_action_len[player_id] = []
        avg_interest[player_id].append(average(history['interest']))
        avg_streak_gold[player_id].append(average(history['streak_gold']))
        avg_action_len[player_id].append(len(history['log'])/len(history['combat']))
        
for player_id, value in avg_interest.items():
    avg_interest[player_id] = average(value)
    
for player_id, value in avg_streak_gold.items():
    avg_streak_gold[player_id] = average(value)
    
for player_id, value in avg_action_len.items():
    avg_action_len[player_id] = average(value)

print("agent avg_interest")
for player_id, value in avg_interest.items():
    print(f"{player_id}, {value:.2f}")


print("agent avg_streak_gold")
for player_id, value in avg_streak_gold.items():
    print(f"{player_id}, {value:.2f}")
    
print("agent total_gold")
for player_id in avg_streak_gold.keys():
    value = avg_streak_gold[player_id] + avg_interest[player_id]
    print(f"{player_id}, {value:.2f}")
    
print("agent action_len")
for player_id in avg_action_len.keys():
    value = avg_action_len[player_id]
    print(f"{player_id}, {value:.2f}")