"""문제 3 — 쿼터니언 변환과 SLERP. (학생 작성용 템플릿)

규약
----
- 쿼터니언은 길이 4 배열 **(x, y, z, w)** 다. 모듈 ③ 의 `quaternion_from_axis_angle` 과
  SciPy `Rotation.as_quat()` 와 같은 순서다. w 가 스칼라(실수부)다.
- q 와 -q 는 같은 회전이다 (이중 덮개). 비교할 때는 부호를 무시하거나 |q . q_ref| 를 본다.
- 보간은 항상 **짧은 호**를 택한다: q0 . q1 < 0 이면 q1 의 부호를 뒤집고 시작한다.

SciPy 는 검산(비교) 용도로만 쓴다. 이 파일 안에서는 numpy 만 사용한다.
"""

from __future__ import annotations

import numpy as np

__all__ = ["matrix_to_quaternion", "quaternion_to_matrix", "slerp", "lerp_quat", "quat_angle"]

def matrix_to_quaternion(R) -> np.ndarray:
    R = np.asarray(R, dtype=float)

    if R.shape != (3, 3):
        raise ValueError("R은 (3, 3) 회전행렬이어야 합니다.")

    t = np.trace(R)

    if t > 0:
        s = 2.0 * np.sqrt(1.0 + t)

        w = 0.25 * s
        x = (R[2, 1] - R[1, 2]) / s
        y = (R[0, 2] - R[2, 0]) / s
        z = (R[1, 0] - R[0, 1]) / s

    elif R[0, 0] >= R[1, 1] and R[0, 0] >= R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2])

        x = 0.25 * s
        y = (R[0, 1] + R[1, 0]) / s
        z = (R[0, 2] + R[2, 0]) / s
        w = (R[2, 1] - R[1, 2]) / s

    elif R[1, 1] >= R[2, 2]:
        s = 2.0 * np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2])

        x = (R[0, 1] + R[1, 0]) / s
        y = 0.25 * s
        z = (R[1, 2] + R[2, 1]) / s
        w = (R[0, 2] - R[2, 0]) / s

    else:
        s = 2.0 * np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1])

        x = (R[0, 2] + R[2, 0]) / s
        y = (R[1, 2] + R[2, 1]) / s
        z = 0.25 * s
        w = (R[1, 0] - R[0, 1]) / s

    q = np.array([x, y, z, w])

    q = q / np.linalg.norm(q)

    if q[3] < 0:
        q = -q

    return q


def quaternion_to_matrix(q) -> np.ndarray:
    """쿼터니언 (x, y, z, w) 을 3x3 회전행렬로 변환한다."""
    q = np.asarray(q, dtype=float)

    if q.shape != (4,):
        raise ValueError("q는 (4,) 형태의 쿼터니언이어야 합니다.")

    n = np.linalg.norm(q)
    if np.isclose(n, 0.0):
        raise ValueError("영 쿼터니언은 회전행렬로 변환할 수 없습니다.")
    x, y, z, w = q / n

    return np.array([
        [1.0 - 2.0 * (y * y + z * z), 2.0 * (x * y - z * w), 2.0 * (x * z + y * w)],
        [2.0 * (x * y + z * w), 1.0 - 2.0 * (x * x + z * z), 2.0 * (y * z - x * w)],
        [2.0 * (x * z - y * w), 2.0 * (y * z + x * w), 1.0 - 2.0 * (x * x + y * y)],
    ])


def slerp(q0, q1, t: float) -> np.ndarray:
    """두 단위 쿼터니언 사이 구면 선형 보간 (짧은 호).

    q0 . q1 < 0 이면 q1 의 부호를 뒤집고 시작한다.
    두 자세가 거의 같으면 (dot > 0.9995) 선형 보간 후 정규화한다.
    """
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    if q0.shape != (4,) or q1.shape != (4,):
        raise ValueError("q0, q1은 (4,) 형태이어야 합니다.")

    n0 = np.linalg.norm(q0)
    n1 = np.linalg.norm(q1)
    if np.isclose(n0, 0.0) or np.isclose(n1, 0.0):
        raise ValueError("영 쿼터니언으로는 보간할 수 없습니다.")
    q0 = q0 / n0
    q1 = q1 / n1

    dot = float(np.dot(q0, q1))
    # 짧은 호 선택
    if dot < 0.0:
        q1 = -q1
        dot = -dot
    dot = np.clip(dot, -1.0, 1.0)

    # 거의 같은 자세면 수치 안정성을 위해 LERP + 정규화
    if dot > 0.9995:
        q = (1.0 - t) * q0 + t * q1
        return q / np.linalg.norm(q)

    theta = np.arccos(dot)
    sin_theta = np.sin(theta)
    s0 = np.sin((1.0 - t) * theta) / sin_theta
    s1 = np.sin(t * theta) / sin_theta
    return s0 * q0 + s1 * q1


def lerp_quat(q0, q1, t: float, normalize: bool = False) -> np.ndarray:
    """성분별 단순 선형 보간.

    기본값(normalize=False)에서는 정규화하지 않은 원시값을 돌려준다
    (중간값의 노름이 1에서 벗어남을 보이기 위한 대비용).
    normalize=True 이면 정규화한 단위 쿼터니언을 돌려준다.
    짧은 호 선택(내적<0 이면 q1 부호 반전)은 항상 적용한다.
    """
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    if q0.shape != (4,) or q1.shape != (4,):
        raise ValueError("q0, q1은 (4,) 형태이어야 합니다.")

    if float(np.dot(q0, q1)) < 0.0:
        q1 = -q1
    q = (1.0 - t) * q0 + t * q1
    if normalize:
        n = np.linalg.norm(q)
        if np.isclose(n, 0.0):
            raise ValueError("보간 결과가 영벡터이므로 정규화할 수 없습니다.")
        q = q / n
    return q


def quat_angle(q0, q1) -> float:
    """두 쿼터니언 사이 회전각 [rad] — 2*arccos(|q0 . q1|)."""
    q0 = np.asarray(q0, dtype=float)
    q1 = np.asarray(q1, dtype=float)

    if q0.shape != (4,) or q1.shape != (4,):
        raise ValueError("q0, q1은 (4,) 형태이어야 합니다.")

    n0 = np.linalg.norm(q0)
    n1 = np.linalg.norm(q1)
    if np.isclose(n0, 0.0) or np.isclose(n1, 0.0):
        raise ValueError("영 쿼터니언의 각도는 정의할 수 없습니다.")

    dot = abs(float(np.dot(q0 / n0, q1 / n1)))
    dot = np.clip(dot, -1.0, 1.0)
    return float(2.0 * np.arccos(dot))