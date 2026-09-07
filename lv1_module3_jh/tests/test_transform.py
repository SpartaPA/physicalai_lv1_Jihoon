"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
    inverse_gauss_jordan
    
)
from src.vectors import gauss_eliminate


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    T_inv = inv_T(T)
    I = np.eye(4)

    assert np.allclose(
        T_inv @ T,
        I,
        atol=1e-6
    )

    assert np.allclose(
        T @ T_inv,
        I,
        atol=1e-6
    )


def test_inv_T_matches_generic_inverse(T):
    T_inv = inv_T(T)

    # np.linalg.inv는 검산용
    expected = np.linalg.inv(T)

    assert np.allclose(
        T_inv,
        expected,
        atol=1e-6
    )


def test_point_and_direction_differ(T):
    v = np.array([1.0, 2.0, 3.0])

    point = transform_point(T, v)
    direction = transform_direction(T, v)

    # 점과 방향은 병진 때문에 결과가 다름
    assert not np.allclose(point, direction)

    # 두 결과의 차이는 이동 벡터
    translation = T[:3, 3]

    assert np.allclose(
        point - direction,
        translation,
        atol=1e-6
    )

    # 회전은 방향 벡터의 길이를 보존
    assert np.isclose(
        np.linalg.norm(direction),
        np.linalg.norm(v),
        atol=1e-6
    )


def test_transform_points_is_vectorized(T):
    points = np.array([
        [1.0, 2.0, 3.0],
        [2.0, 1.0, 0.0],
        [-1.0, 0.5, 2.0],
        [3.0, -2.0, 1.0],
    ])

    result = transform_points(T, points)

    expected = np.array([
        transform_point(T, p)
        for p in points
    ])

    assert np.allclose(
        result,
        expected,
        atol=1e-6
    )


def test_roundtrip_through_inverse(T):
    points = np.array([
        [1.0, 2.0, 3.0],
        [-1.0, 0.5, 2.0],
        [3.0, -2.0, 1.0],
    ])

    transformed = transform_points(T, points)
    restored = transform_points(inv_T(T), transformed)

    assert np.allclose(
        restored,
        points,
        atol=1e-6
    )


def test_least_squares_matches_lstsq():
    rng = np.random.default_rng(42)

    A = rng.normal(size=(8, 3))
    x_true = np.array([1.5, -2.0, 0.7])

    noise = rng.normal(0.0, 0.05, size=8)
    b = A @ x_true + noise

    x = least_squares_normal_equation(A, b)

    # np.linalg.lstsq는 검산용
    x_expected, _, _, _ = np.linalg.lstsq(A, b, rcond=None)

    assert np.allclose(
        x,
        x_expected,
        atol=1e-6
    )

    # 잔차는 A의 열공간에 수직이어야 함
    r = b - A @ x

    assert np.allclose(
        A.T @ r,
        np.zeros(A.shape[1]),
        atol=1e-6
    )