import asyncio
import socketio
import json
import os
from pyautobattle.src.render import client_render


# 비동기 클라이언트 인스턴스 생성
sio = socketio.AsyncClient()

# 서버로부터의 응답을 처리하는 핸들러 정의
@sio.event
async def response(data):
    print(f"서버로부터의 응답: {data}")

@sio.event
async def server_response(data):
    os.system('clear')
    # print(data['game'], data['player'])
    try:
        client_render(data['game'], data['player'])
    except Exception as e:
        print(e)

async def send_command():
    """사용자 명령을 서버로 전송하는 비동기 함수"""
    while True:
        command = await asyncio.get_event_loop().run_in_executor(None, input, "Your command: ")
        if command.lower() == 'exit':
            print("서버와의 연결을 종료합니다.")
            await sio.disconnect()
            break
        await sio.emit('command', command)

async def main():
    await sio.connect('http://localhost:5000')
    print("서버에 연결되었습니다.")

    # 사용자 명령 전송을 별도의 태스크로 실행
    send_task = asyncio.create_task(send_command())

    # 서버로부터의 메시지를 수신하면서 사용자 명령을 처리
    await send_task

if __name__ == '__main__':
    asyncio.run(main())
