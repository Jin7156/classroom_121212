    import numpy as np

def count_visible_lines(eye, obstacles, board, board_y):
    """
    눈에서 칠판의 점들로 향하는 선분 중 장애물에 가려지지 않은 선분의 개수를 구합니다.
    """
    
    # 1. 시점(Eye) 좌표 (1, 1, 3) 형태로 변환
    O = np.array(eye, dtype=float).reshape(1, 1, 3)
    
    # 2. 장애물 배열 처리 (N x 6)
    obs_array = np.array(obstacles, dtype=float)
    if len(obs_array) == 0:
        return 1000 # 장애물이 없으면 1000개 모두 보임
        
    # 장애물의 최소/최대 좌표를 (1, N, 3) 형태로 차원 확장
    box_min = obs_array[:, :3].reshape(1, -1, 3)
    box_max = obs_array[:, 3:].reshape(1, -1, 3)
    
    # 3. 칠판(Board)에 1000개의 점 생성
    # [q, w, e, r] = [x_min, x_max, z_min, z_max] 로 가정
    q, w, e, r = board 
    
    # x축 40개, z축 25개의 일정한 간격의 점 생성 (40 * 25 = 1000)
    x_points = np.linspace(q, w, 40)
    z_points = np.linspace(e, r, 25)
    X, Z = np.meshgrid(x_points, z_points)
    
    # 칠판의 1000개 점 좌표 배열 (1000, 1, 3)
    E = np.c_[X.ravel(), np.full(1000, board_y), Z.ravel()].reshape(1000, 1, 3)
    
    # 4. 방향 벡터 계산 (D = E - O)
    D = E - O
    
    # 0으로 나누는 오류 방지 (아주 작은 값으로 대체)
    D = np.where(D == 0, 1e-8, D)
    
    # 5. 슬랩 알고리즘 (Slab Method)을 이용한 교차 판별
    # 각 축(x, y, z)별로 광선이 장애물 경계면에 닿는 비율(t) 계산
    t1 = (box_min - O) / D
    t2 = (box_max - O) / D
    
    # 각 축별 진입점(t_min)과 진출점(t_max)
    t_min_axis = np.minimum(t1, t2)
    t_max_axis = np.maximum(t1, t2)
    
    # 박스에 완전히 진입하는 시간(t_enter)과 빠져나가는 시간(t_exit)
    t_enter = np.max(t_min_axis, axis=2) # (1000, N)
    t_exit = np.min(t_max_axis, axis=2)  # (1000, N)
    
    # [교차 조건]
    # 1. t_enter <= t_exit : 광선이 직육면체와 교차함
    # 2. t_exit >= 0 : 장애물이 눈(시점) 뒤에 있지 않음
    # 3. t_enter <= 1 : 장애물이 칠판(목표점) 너머에 있지 않음 (선분 내에 존재)
    intersect = (t_enter <= t_exit) & (t_enter <= 1.0) & (t_exit >= 0.0)
    
    # 6. 최종 판별
    # 각 선분(1000개)에 대해 하나(any)의 장애물이라도 교차했다면 가려진 것(True)
    blocked_rays = np.any(intersect, axis=1) # 결과 형태: (1000,)
    
    # 가려지지 않은(~blocked_rays) 선분의 총 개수 합산
    visible_count = np.sum(~blocked_rays)
    
    return visible_count

# ==========================================
# 실행 테스트 (예시 데이터)
# ==========================================

# 눈 좌표 [x, y, z]
eye_pos = [0, 0, -10]

# 장애물 리스트 [x_min, y_min, z_min, x_max, y_max, z_max]
obs_list = [
    [-2, -2, -5, 2, 2, -3], # 시야 정중앙을 가리는 큰 장애물
    [8, 8, 0, 10, 10, 2]    # 시야 바깥에 있는 장애물
]

# 칠판 평면 정보 [x_min, x_max, z_min, z_max]
board_info = [-10, 10, -10, 10]
board_y_pos = 10 # 칠판의 고정된 Y 좌표

result = count_visible_lines(eye_pos, obs_list, board_info, board_y_pos)
print(f"장애물에 가려지지 않고 온전히 보이는 선분의 개수: {result} / 1000")