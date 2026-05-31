import hashlib
from pydantic._internal import _model_construction
from fastapi import datastructures
import numpy as np
import random as rm
import classroom_121212.config as cn

#js에서 받은 값을 dick형태로 저장해야함, js에서 object형태로 저장하고 json으로 바꾼다음 json을 python의 dick으로 저장




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



def sort_by_height(student_dict):
    """
    학생 딕셔너리를 키(value) 순으로 정렬하는 함수
    - reverse=False: 키가 작은 순서대로 (오름차순)
    - reverse=True: 키가 큰 순서대로 (내림차순)
    """
    # student_dict.items()로 (이름, 키) 쌍을 꺼내고, 
    # x[1](즉, 키)을 기준으로 정렬합니다.
    sorted_result = sorted(student_dict.items(), key=lambda x: x[1], reverse=False)
    
    return sorted_result











import random

def random_stndt(lst):
    # 1. 각 그룹(Short / High)의 배정해야 할 총원(자리수) 계산
    a = len(cn.desk_lst_shortbad) + len(cn.desk_lst_shortgood)
    b = len(cn.desk_lst_highbad) + len(cn.desk_lst_highgood)
    

    cn.desk_lst_short_name = lst[:a]
    cn.desk_lst_high_name = lst[a:a+b]

    # 결과 리스트 초기화 (매번 새로 분류하기 위함)
    cn.desk_lst_shortbad_name = []
    cn.desk_lst_shortgood_name = []
    cn.desk_lst_highbad_name = []
    cn.desk_lst_highgood_name = []

    # ==========================================
    # 2. 키가 작은 학생(Short) 처리 영역
    # ==========================================
    # (1) 시력에 따라 1차 분류 (item[0]은 이름/ID, item[1]은 키)
    for item in cn.desk_lst_short_name:
        student_id = item if isinstance(item, str) else item[0]
        if cn.stdnteye_dict.get(student_id) == 0:
            cn.desk_lst_shortbad_name.append(student_id)
        else:
            cn.desk_lst_shortgood_name.append(student_id)

    # (2) while문 + 랜덤 pop으로 부족한 인원 채우기
    target_shortbad = len(cn.desk_lst_shortbad)
    while len(cn.desk_lst_shortbad_name) < target_shortbad:
        if not cn.desk_lst_shortgood_name:  # 시력 좋은 학생이 더 없으면 탈출
            break
        random_idx = random.randrange(len(cn.desk_lst_shortgood_name))
        chosen_student = cn.desk_lst_shortgood_name.pop(random_idx)
        cn.desk_lst_shortbad_name.append(chosen_student)

    # ==========================================
    # 3. 키가 큰 학생(High) 처리 영역
    # ==========================================
    # (1) 시력에 따라 1차 분류
    for item in cn.desk_lst_high_name:
        student_id = item if isinstance(item, str) else item[0]
        if cn.stdnteye_dict.get(student_id) == 0:
            cn.desk_lst_highbad_name.append(student_id)
        else:
            cn.desk_lst_highgood_name.append(student_id)

    # (2) while문 + 랜덤 pop으로 부족한 인원 채우기
    target_highbad = len(cn.desk_lst_highbad)
    while len(cn.desk_lst_highbad_name) < target_highbad:
        if not cn.desk_lst_highgood_name:  # 시력 좋은 학생이 더 없으면 탈출
            break
        random_idx = random.randrange(len(cn.desk_lst_highgood_name))
        chosen_student = cn.desk_lst_highgood_name.pop(random_idx)
        cn.desk_lst_highbad_name.append(chosen_student)
    
    return ()