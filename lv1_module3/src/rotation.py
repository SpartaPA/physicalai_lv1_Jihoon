import numpy as np
from src.vectors import skew,norm,dot,det

def rot_x(theta: float):
    # x축 회전 행렬
    c,s = np.cos(theta), np.sin(theta)
    return np.array([
        [1,0,0],
        [0,c,-s],
        [0,s,c]]

    )

def rot_y(theta: float):
    # y축 회전 행렬
    c,s = np.cos(theta), np.sin(theta)
    a = np.array([
        [c,0,s],
        [0,1,0],
        [-s,0,c]]
    )
    return a

def rot_z(theta: float):
    # z축 회전 행렬
    c,s = np.cos(theta), np.sin(theta)
    a = np.array([
        [c,-s,0],
        [s,c,0],
        [0,0,1]]

    )
    return a


    

def rodrigues(axis, theta):
    """회전축과 회전각으로 Rodrigues 회전행렬을 계산한다."""

    axis = np.asarray(axis, dtype=float)

    axis_norm = norm(axis)

    if np.isclose(axis_norm, 0.0):
        raise ValueError("회전축은 영벡터가 될 수 없습니다.")

    # 회전축을 단위벡터로 만든다.
    k = axis / axis_norm

    # skew 행렬
    K = skew(k)

    I = np.eye(3)

    # Rodrigues 공식
    R = (
        I
        + np.sin(theta) * K
        + (1.0 - np.cos(theta)) * (K @ K)
    )

    return R

def rodrigues_matrix(axis: np.ndarray, theta: float):
    # 로드리게스 회전 공식에 따라 회전 행렬 생성
    v = np.asarray(axis, dtype=np.float64)
    axis_norm = norm(axis)

    if np.isclose(axis_norm, 0):
        raise ValueError("회전축은 영벡터가 될 수 없습니다.")

    k=axis/axis_norm
    K = skew(k)
    I = np.eye(3)
     # Rodrigues 공식
    R = (
        I
        + np.sin(theta) * K
        + (1.0 - np.cos(theta)) * (K @ K)
    )

    return R

def orthogonality_error(R: np.ndarray) -> float:
    """||R^T R - I||_F 를 직접 계산한다."""

    R = np.asarray(R, dtype=float)

    if R.ndim != 2 or R.shape[0] != R.shape[1]:
        raise ValueError("R은 정방행렬이어야 합니다.")

    I = np.eye(R.shape[0])
    error = R.T @ R - I

    # Frobenius norm 직접 계산
    return float(np.sqrt(np.sum(error * error)))


def is_rotation(R: np.ndarray, tol: float = 1e-6) -> bool:
    """직교성(R^T R = I)과 행렬식(det(R) = 1)을 모두 만족하는지 검증"""
    err = orthogonality_error(R)
    det_val = det(R)
    return err < tol and np.isclose(det_val, 1.0, atol=tol)


def gram_schmidt(A: np.ndarray) -> np.ndarray:
    """열벡터에 대해 Gram-Schmidt 직교정규화를 수행한다."""

    A = np.asarray(A, dtype=float).copy()

    Q = np.zeros_like(A, dtype=float)

    for i in range(A.shape[1]):

        v = A[:, i].copy()

        # 앞에서 만든 직교 벡터들의 성분을 제거
        for j in range(i):
            q = Q[:, j]
            v = v - dot(v, q) * q

        # 남은 벡터의 크기
        length = norm(v)

        if np.isclose(length, 0.0, atol=1e-12):
            raise ValueError(
                f"{i}번 열이 앞선 열들에 종속이라 직교화할 수 없습니다."
            )

        # 단위벡터로 저장
        Q[:, i] = v / length

    return Q

def axis_angle_from_matrix(R: np.ndarray):
    """회전 행렬 R에서 회전축과 회전각을 구한다."""

    R = np.asarray(R, dtype=float)

    if R.shape != (3, 3):
        raise ValueError("R은 3x3 행렬이어야 합니다.")

    # 회전각 계산
    cos_theta = (np.trace(R) - 1.0) / 2.0
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = np.arccos(cos_theta)

    # 회전각이 0이면 축을 [1, 0, 0]으로 둔다.
    if np.isclose(theta, 0.0):
        axis = np.array([1.0, 0.0, 0.0])
        return axis, 0.0

    # 일반적인 경우
    axis = np.array([
        R[2, 1] - R[1, 2],
        R[0, 2] - R[2, 0],
        R[1, 0] - R[0, 1]
    ])

    axis = axis / (2.0 * np.sin(theta))

    return axis, theta

def gauss_elimination(A: np.ndarray, b: np.ndarray) -> np.ndarray:
    """부분 피벗팅을 이용한 가우스 소거법 (Ax = b)"""
    A = np.asarray(A, dtype=float).copy()
    b = np.asarray(b, dtype=float).copy()
    n = len(b)

    for i in range(n):
        # 피벗팅 (수치적 안정성 확보)
        max_row = i + np.argmax(np.abs(A[i:, i]))
        if np.isclose(A[max_row, i], 0.0):
            raise ValueError("특이 행렬(Singular Matrix)이므로 해를 구할 수 없습니다.")
        
        if i != max_row:
            A[[i, max_row]] = A[[max_row, i]]
            b[[i, max_row]] = b[[max_row, i]]

        # 전진 소거
        for j in range(i + 1, n):
            factor = A[j, i] / A[i, i]
            A[j, i:] -= factor * A[i, i:]
            b[j] -= factor * b[i]

    # 후진 대입
    x = np.zeros(n, dtype=float)
    for i in range(n - 1, -1, -1):
        x[i] = (b[i] - np.dot(A[i, i + 1:], x[i + 1:])) / A[i, i]

    return x

def quaternion_from_axis_angle(axis, theta):
    """회전축과 회전각으로 단위 쿼터니언 (x, y, z, w) 를 만든다."""
    axis = np.asarray(axis, dtype=float)

    axis_norm = norm(axis)

    if np.isclose(axis_norm, 0.0):
        raise ValueError("회전축은 영벡터가 될 수 없습니다.")

    axis = axis / axis_norm

    half = theta / 2.0

    q = np.array([
        axis[0] * np.sin(half),
        axis[1] * np.sin(half),
        axis[2] * np.sin(half),
        np.cos(half)
    ])

    return q / norm(q)