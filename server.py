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
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 주소와 포트 번호를 소켓에 바인딩
server_socket.bind((HOST, PORT))

# 클라이언트의 연결 요청을 대기
server_socket.listen()

print(f"서버가 {HOST}:{PORT}에서 대기 중입니다...")

# 클라이언트의 연결 요청 수락
client_socket, client_address = server_socket.accept()
print(f"{client_address}가 연결되었습니다.")

# 클라이언트로부터 데이터 수신
data = client_socket.recv(1024).decode()
print(f"클라이언트로부터 받은 데이터: {data}")

# 클라이언트에게 데이터 전송
client_socket.sendall("서버에서 보내는 메시지입니다.".encode())

# 소켓 닫기
client_socket.close()
server_socket.close()
