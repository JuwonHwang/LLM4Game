import socket

def parse_config(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            # 줄 양끝의 공백 제거 및 주석(#) 처리
            line = line.strip().split('#', 1)[0]
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config

# 사용 예시
config = parse_config('.server')
print(config)

HOST = config["HOST"]
PORT = int(config["PORT"])

# 소켓 객체 생성
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 서버에 연결 요청
client_socket.connect((HOST, PORT))

# 서버로 데이터 전송
client_socket.sendall("클라이언트에서 보내는 메시지입니다.".encode())

# 서버로부터 데이터 수신
data = client_socket.recv(1024).decode()
print(f"서버로부터 받은 데이터: {data}")

# 소켓 닫기
client_socket.close()
