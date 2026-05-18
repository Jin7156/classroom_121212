import numpy as np

def calculate_infringement_rates(eyes, board, board_y, body_size, head_margin=0.1, other_obs=[]):
    """
    여러 명의 눈 좌표에서 칠판을 바라볼 때, 다른 사람 및 장애물에 의한 시야 침해율을 계산합니다.
    """
    S = len(eyes) # 학생(관찰자) 수
    R = 1000      # 칠판에 찍을 점의 개수
    
    eyes_array = np.array(eyes, dtype=float)
    
    # 1. 사람을 장애물로 변환 (눈 좌표 기준 좌우/앞뒤 확장, 발(Z=0)부터 머리 꼭대기까지)
    w, d = body_size # w: 좌우 너비(X), d: 앞뒤 두께(Y)
    
    student_obs = []
    for ex, ey, ez in eyes_array:
        # [x_min, y_min, z_min, x_max, y_max, z_max]
        # z_min은 바닥(0), z_max는 눈 높이(ez) + 머리 꼭대기 여백(head_margin)
        obs = [ex - w/2, ey - d/2, 0, 
               ex + w/2, ey + d/2, ez + head_margin]
        student_obs.append(obs)
        
    # 모든 장애물 병합 (학생 몸 + 기타 장애물)
    all_obs = np.array(student_obs + other_obs, dtype=float)
    O = len(all_obs) # 전체 장애물 개수
    
    # 2. 칠판(Board)의 1000개 점 생성
    # [q, w, e, r] = [x_min, x_max, z_min, z_max]
    q, w_board, e, r = board 
    
    x_points = np.linspace(q, w_board, 40)
    z_points = np.linspace(e, r, 25)
    X, Z = np.meshgrid(x_points, z_points)
    
    # 3. 차원 확장 및 브로드캐스팅 준비
    # 시점(Eyes): (S, 1, 1, 3)
    E_tensor = eyes_array.reshape(S, 1, 1, 3)
    
    # 목표점(Board Points): (1, R, 1, 3)
    P_tensor = np.c_[X.ravel(), np.full(R, board_y), Z.ravel()].reshape(1, R, 1, 3)
    
    # 방향 벡터 D = 목표점 - 시점 : (S, R, 1, 3)
    D = P_tensor - E_tensor
    D = np.where(D == 0, 1e-8, D) # 0으로 나누기 방지
    
    # 장애물 범위: (1, 1, O, 3)
    box_min = all_obs[:, :3].reshape(1, 1, O, 3)
    box_max = all_obs[:, 3:].reshape(1, 1, O, 3)
    
    # 4. 슬랩 알고리즘 적용
    t1 = (box_min - E_tensor) / D
    t2 = (box_max - E_tensor) / D
    
    t_enter = np.max(np.minimum(t1, t2), axis=3) # 형태: (S, R, O)
    t_exit  = np.min(np.maximum(t1, t2), axis=3) # 형태: (S, R, O)
    
    # 교차 판별 조건
    intersect = (t_enter <= t_exit) & (t_enter <= 1.0) & (t_exit >= 0.0)
    
    # 5. 자기 자신에 의한 가려짐 예외 처리 (Self-Occlusion 방지)
    # i번째 학생의 시야가 i번째 학생의 몸(장애물 인덱스 i)에 가려지는 것은 무시합니다.
    self_mask = np.ones((S, 1, O), dtype=bool)
    for i in range(S):
        self_mask[i, 0, i] = False
    
    # 실제 유효한 충돌만 남김
    valid_intersect = intersect & self_mask
    
    # 6. 침해율 계산
    # 각 학생(S)별로 1000개의 선분(R) 중 하나라도 충돌한(any O) 선분의 수
    blocked_rays = np.any(valid_intersect, axis=2) # 형태: (S, R)
    blocked_count = np.sum(blocked_rays, axis=1)   # 형태: (S,)
    
    # 침해율(%) = (가려진 선분 / 1000) * 100
    infringement_rates = (blocked_count / R) * 100
    
    return infringement_rates

# ==========================================
# 실행 테스트 (교실 자리배치 예시)
# ==========================================

# 학생 20명의 눈 좌표 랜덤 생성 (교실 좌석 배치 형태 모사)
# X(좌우): -4 ~ 4, Y(앞뒤): -8 ~ -2, Z(키): 1.0 ~ 1.5 (앉은 키 가설)
np.random.seed(42)
num_students = 20
student_eyes = np.column_stack([
    np.random.uniform(-4, 4, num_students),
    np.random.uniform(-8, -2, num_students),
    np.random.uniform(1.0, 1.5, num_students)
])

# 칠판 정보 [x_min, x_max, z_min, z_max], 칠판은 Y=0에 위치
board_info = [-5, 5, 1.0, 2.5] 
board_y_pos = 0

# 사람 몸 크기 설정 (너비 0.6m, 앞뒤 두께 0.4m)
body_dimensions = (0.6, 0.4)

# 실행
rates = calculate_infringement_rates(
    eyes=student_eyes, 
    board=board_info, 
    board_y=board_y_pos, 
    body_size=body_dimensions
)

# 결과 출력
print("=== 각 학생별 칠판 시야 침해율(%) ===")
for idx, rate in enumerate(rates):
    print(f"학생 {idx+1:2d}: {rate:5.1f}% 가려짐 (좌표: X={student_eyes[idx][0]:.1f}, Y={student_eyes[idx][1]:.1f}, Z={student_eyes[idx][2]:.1f})")