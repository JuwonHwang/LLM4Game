import socketio
from aiohttp import web
from pyautobattle.src import AutoBattlerGame
import time
import os

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

connected_user = set()
game : AutoBattlerGame = None
player_dict = dict()

def call_api(sid, raw_data: str):
    global game
    data = raw_data.split()
    print(data)
    if data[0] == 'game':
        game = AutoBattlerGame()
        player_dict[sid] = game.get_player_by_index(len(player_dict.keys()))

# 'command' 이벤트를 처리하는 핸들러 정의
@sio.event
async def command(sid, data):
    print(f"Received command from client {sid}: {data}")
    try:
        call_api(sid, data)
    except Exception as e:
        print(e)
    response = f"Command '{data}' executed successfully."
    await sio.emit('response', response, to=sid)

@sio.event
async def view(sid, data):
    global game
    await sio.emit('display', game, to=sid)

# 연결 이벤트 핸들러
@sio.event
async def connect(sid, environ):
    connected_user.add(sid)
    print(f"Client {sid} connected.")

# 연결 해제 이벤트 핸들러
@sio.event
async def disconnect(sid):
    if sid in player_dict.keys():
        player_dict.pop(sid)
    connected_user.discard(sid)
    print(f"Client {sid} disconnected.")


async def send_game_state():
    global game
    """주기적으로 클라이언트에 메시지를 보내는 백그라운드 작업"""
    count = 0
    while True:
        await sio.sleep(1)  # 5초 대기
        # os.system('clear')
        count += 1
        for user, player in player_dict.items():
            try:
                print(user)
                print(player)
                await sio.emit('server_response', {'game': game.observe(), 'player': player.observe()}, to=user)
            except Exception as e:
                print(e)
        print(f'send game state to', player_dict.keys())

async def init_app():
    """애플리케이션 초기화 및 백그라운드 작업 시작"""
    sio.start_background_task(send_game_state)
    return app

if __name__ == '__main__':
    web.run_app(init_app(), host='localhost', port=5000)
    print("server terminated")
