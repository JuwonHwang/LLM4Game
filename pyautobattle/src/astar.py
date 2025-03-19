import heapq
import time
import random
class Node:
    def __init__(self, position, parent=None, direction=None):
        self.position = position
        self.parent = parent
        self.direction = direction
        self.g = 0  # 시작 지점으로부터의 비용
        self.h = 0  # 휴리스틱(목표 지점까지의 예상 비용)
        self.f = 0  # 총 비용

    def __lt__(self, other):
        return self.f < other.f

def search(start, end, obstacles, wall=(7,6)):
    start = tuple(start)
    end = tuple(end)
    obstacles = [tuple(o) for o in obstacles]
    # 시작 및 종료 노드 초기화
    start_node = Node(start)
    end_node = Node(end)

    # 오픈 리스트와 클로즈드 리스트 초기화
    open_list = []
    closed_list = set()

    # 시작 노드를 오픈 리스트에 추가
    heapq.heappush(open_list, start_node)

    # 이동 가능한 방향 정의 (상, 하, 좌, 우)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while open_list:
        # print([n.position for n in open_list])
        # time.sleep(0.1)
        # 오픈 리스트에서 f 값이 가장 낮은 노드를 선택
        current_node = heapq.heappop(open_list)
        closed_list.add(tuple(current_node.position))

        # 목표 지점에 도달하면 경로를 생성하여 반환
        if current_node.position == end_node.position:
            path = []
            direction_list = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
                if current_node:
                    direction_list.append(current_node.direction)
            return path[::-1], direction_list[::-1][1:]  # 경로를 역순으로 반환
        # 현재 노드의 인접한 노드들을 탐색
        random.shuffle(directions)
        for direction in directions:
            neighbor_position = (current_node.position[0] + direction[0],
                                current_node.position[1] + direction[1])

            # 장애물이나 이미 방문한 노드는 무시
            if neighbor_position != end and (neighbor_position in obstacles or tuple(neighbor_position) in closed_list):
                continue
            if 0 > neighbor_position[0] or neighbor_position[0] > wall[0]:
                continue
            if 0 > neighbor_position[1] or neighbor_position[1] > wall[1]:
                continue
            # 새로운 인접 노드 생성
            neighbor_node = Node(neighbor_position, current_node, direction)
            neighbor_node.g = current_node.g + 1
            neighbor_node.h = abs(neighbor_node.position[0] - end_node.position[0]) + \
                                abs(neighbor_node.position[1] - end_node.position[1])
            neighbor_node.f = neighbor_node.g + neighbor_node.h

            # 오픈 리스트에 있는 노드 중 동일한 위치를 가진 노드 찾기
            existing_node = next((node for node in open_list if node.position == neighbor_node.position), None)

            # 기존 노드가 없거나 더 나은 경로를 찾은 경우에만 오픈 리스트에 추가
            if existing_node is None or neighbor_node.h < existing_node.h:
                heapq.heappush(open_list, neighbor_node)

    # 경로를 찾을 수 없는 경우
    return None, None
