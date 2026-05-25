import numpy as np
import random as rm
import config as cn

#js에서 받은 값을 dick형태로 저장해야함, js에서 object형태로 저장하고 json으로 바꾼다음 json을 python의 dick으로 저장

def v2randomset(dict): #키와 시력에 따라 다른 리스트에 사람의 키를 저장하자, 그 값은 아래의 주석처리한 코드를 참조하여 해보자
    names = list(dict.keys())
    for i in range(len(names)):
        if dict.key[names[i]]:
            print(1)



def calculate_visibility(eye_pos, board_bounds, board_resolution, obstacles):
    """                  학생눈 위치 칠판의 좌표 범위, 칠판에 찍을 점의 개수, 장애물 리스트
    학생의 눈 위치, 칠판의 경계, 장애물 리스트를 입력받아 
    칠판의 1,000개 점에 대한 시야 차폐율을 계산하는 함수
    """
    # 1. 데이터 타입 최적화 및 배열 변환 (float32 적용으로 메모리 사용량 절반 감소)
    eye_pos = np.array(eye_pos, dtype=np.float32)
    obstacles = np.array(obstacles, dtype=np.float32)
    
    # 2. 장애물 필터링 (y축 기준: 학생 뒤에 있거나 칠판 너머에 있는 장애물 제거)
    if obstacles.size > 0:
        # obstacles: [x_min, y_min, z_min, x_max, y_max, z_max]
        valid_mask = (obstacles[:, 1] < eye_pos[1]) & (obstacles[:, 4] > 0)
        valid_obstacles = obstacles[valid_mask]
    else:
        valid_obstacles = np.empty((0, 6), dtype=np.float32)

    # 3. 칠판 점(Target) 1,000개 생성 (1000, 3)
    x_min, _, z_min = board_bounds[0]
    x_max, _, z_max = board_bounds[1]
    rows, cols = board_resolution
    
    x_coords = np.linspace(x_min, x_max, cols, dtype=np.float32)
    z_coords = np.linspace(z_min, z_max, rows, dtype=np.float32)
    
    xv, zv = np.meshgrid(x_coords, z_coords)
    yv = np.zeros_like(xv)
    targets = np.vstack([xv.ravel(), yv.ravel(), zv.ravel()]).T
    
    # 4. Ray 방향 벡터 D 계산 (Ray: P = O + t*D)
    rays_d = targets - eye_pos # 형태: (1000, 3)
    num_rays = rays_d.shape[0]
    num_obs = valid_obstacles.shape[0]
    
    if num_obs == 0:
        return 100.0, 0  # 유효한 장애물이 없으면 가시성 100%
        
    # 5. 브로드캐스팅을 위한 차원 확장 (M개의 장애물 x 1000개의 Ray)
    # rays_o_exp: (1, 1000, 3) / rays_d_exp: (1, 1000, 3)
    rays_o_exp = eye_pos[np.newaxis, np.newaxis, :]
    rays_d_exp = rays_d[np.newaxis, :, :]
    
    # obs_min, obs_max: (M, 1, 3)
    obs_min = valid_obstacles[:, :3][:, np.newaxis, :]
    obs_max = valid_obstacles[:, 3:][:, np.newaxis, :]
    
    # Zero Division 에러 방지를 위한 엡실론 추가 (Ray 방향 벡터의 축 값이 0일 경우 대비)
    epsilon = 1e-7
    rays_d_exp = np.where(np.abs(rays_d_exp) < epsilon, epsilon, rays_d_exp)
    
    # 6. Slab 알고리즘 교차 지점(t) 계산
    t1 = (obs_min - rays_o_exp) / rays_d_exp
    t2 = (obs_max - rays_o_exp) / rays_d_exp
    
    t_min = np.minimum(t1, t2)
    t_max = np.maximum(t1, t2)
    
    # 각 축(x, y, z)에 대해 t_near 중 가장 큰 값, t_far 중 가장 작은 값 도출
    t_near = np.max(t_min, axis=2) # 형태: (M, 1000)
    t_far = np.min(t_max, axis=2)  # 형태: (M, 1000)
    
    # 7. 충돌 판별 조건:
    # - t_near <= t_far: Ray가 박스를 관통함
    # - t_far >= 0: 장애물이 눈 앞쪽에 있음
    # - t_near <= 1: 교차점이 눈과 칠판 '사이'의 선분 위에 존재함
    hit_mask = (t_near <= t_far) & (t_far >= 0) & (t_near <= 1)
    
    # 8. 최종 결과 산출 (각 Ray별로 1개 이상의 장애물에 부딪혔는지 검사)
    ray_blocked = np.any(hit_mask, axis=0) # 형태: (1000,)
    blocked_count = np.sum(ray_blocked)
    
    visibility_ratio = ((num_rays - blocked_count) / num_rays) * 100.0
    
    return visibility_ratio, blocked_count