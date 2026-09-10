import numpy as np
from src.vectors import skew, norm, dot, det

from src.vectors import inverse_gauss_jordan, gauss_eliminate
from src.rotation import gauss_elimination

def make_T(R,Y):
    """회전행렬 R과 이동벡터 Y를 이용하여 동차변환행렬 T를 생성"""
    T = np.eye(4)
    T[:3,:3] = R
    T[:3,3] = Y
    return T

def inv_T(T):
    """동차변환행렬 T의 역행렬을 계산"""
    R = T[:3,:3]
    Y = T[:3,3]
    T_inv = np.eye(4)
    T_inv[:3,:3] = R.T
    T_inv[:3,3] = -R.T @ Y
    return T_inv

def inv_T_batch(T_batch):
    """동차변환행렬 T_batch의 역행렬을 계산 (배치 처리)"""
    T_batch = np.asarray(T_batch, dtype=float)

    if T_batch.ndim != 3 or T_batch.shape[1:] != (4, 4):
        raise ValueError("T_batch는 (N, 4, 4) 형태여야 합니다.")

    R = T_batch[:, :3, :3]
    Y = T_batch[:, :3, 3]

    R_inv = np.transpose(R, (0, 2, 1))

    T_inv = np.tile(np.eye(4), (T_batch.shape[0], 1, 1))

    T_inv[:, :3, :3] = R_inv
    T_inv[:, :3, 3] = -np.einsum(
        "bij,bj->bi",
        R_inv,
        Y
    )

    return T_inv


def least_squares_normal_equation(A, b):
    """최소제곱법을 이용하여 Ax = b의 해를 구함"""
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)

    if A.ndim != 2 or b.ndim != 1:
        raise ValueError("A는 2차원 배열, b는 1차원 배열이어야 합니다.")

    # 정규방정식: (A^T A) x = A^T b
    AtA = A.T @ A
    Atb = A.T @ b

    # 역행렬을 이용하여 해를 계산
    try:
        x = gauss_elimination(AtA, Atb)

    except ValueError:

        raise ValueError("정규방정식의 계수 행렬이 가역적이지 않습니다.")

    residual =  b - A @ x

    return x, residual


def rmse(residual):
    """잔차의 평균제곱근오차(RMSE)를 계산"""
    residual = np.asarray(residual, dtype=float)

    return np.sqrt(np.mean(residual ** 2))

def to_homogeneous(v, w):
    """3차원 벡터를 동차좌표로 변환"""

    v = np.asarray(v, dtype=float)

    if v.shape != (3,):
        raise ValueError("v는 (3,) 형태여야 합니다.")

    return np.array([v[0], v[1], v[2], w], dtype=float)

def transform_direction(T: np.ndarray, v: np.ndarray) -> np.ndarray:
    """T를 이용하여 방향 벡터 v를 변환 (동차좌표 w=0.0 적용)"""
    T = np.asarray(T, dtype=float)
    v = np.asarray(v, dtype=float)

    if T.shape != (4, 4):
        raise ValueError("T는 (4, 4) 형태의 동차변환행렬이어야 합니다.")
    if v.ndim != 1 or v.shape[0] != 3:
        raise ValueError("v는 (3,) 형태의 방향 벡터이어야 합니다.")

    # 올바른 1차원 동차좌표 벡터 생성 [vx, vy, vz, 0.0]
    v_h = np.append(v, 0.0)
    t_v_h = T @ v_h

    return t_v_h[:3]

def transform_point(T: np.ndarray, p: np.ndarray) -> np.ndarray:
    """T를 이용하여 점 p를 변환 (동차좌표 w=1.0 적용)"""
    T = np.asarray(T, dtype=float)
    p = np.asarray(p, dtype=float)

    if T.shape != (4, 4):
        raise ValueError("T는 (4, 4) 형태의 동차변환행렬이어야 합니다.")
    if p.ndim != 1 or p.shape[0] != 3:
        raise ValueError("p는 (3,) 형태의 점 벡터이어야 합니다.")

    # 올바른 1차원 동차좌표 벡터 생성 [x, y, z, 1.0]
    p_h = np.append(p, 1.0)
    t_p_h = T @ p_h

    return t_p_h[:3]

def transform_points(T, points):
    """동차변환행렬 T를 이용하여 여러 점들을 변환"""
    T = np.asarray(T, dtype=float)
    points = np.asarray(points, dtype=float)

    if T.shape != (4, 4):
        raise ValueError("T는 (4, 4) 형태의 동차변환행렬이어야 합니다.")
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points는 (N, 3) 형태의 2차원 배열이어야 합니다.")

    # 점들을 동차좌표로 변환 (w=1)
    ones = np.ones((points.shape[0], 1))

    points_homogeneous = np.hstack((points, ones))

    t_p_h = (T @ points_homogeneous.T).T

    transformed_points = t_p_h[:, :3]

    return transformed_points


