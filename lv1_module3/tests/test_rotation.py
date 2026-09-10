"""문제 3 — 회전 행렬의 수학적 성질 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 4가지를 각각 테스트 함수로 작성한다.

  1. 회전행렬의 열이 서로 직교하는 단위벡터인가   -> test_columns_are_orthonormal
  2. 행렬식이 1인가                               -> test_determinant_is_one
  3. 역행렬이 전치와 같은가                       -> test_inverse_equals_transpose
  4. 재직교화 결과가 직교행렬인가                 -> test_gram_schmidt_restores_orthogonality

작성 요령
--------
- @pytest.mark.parametrize 로 여러 축 x 여러 각도를 한 함수에서 검사하면
  테스트 하나가 여러 케이스를 담당한다.
- 비교는 반드시 np.isclose / np.allclose 로 한다.
- np.linalg 는 검산용으로만 사용한다.
"""

import numpy as np
import pytest

from src.rotation import (
    axis_angle_from_matrix,
    gram_schmidt,
    is_rotation,
    orthogonality_error,
    rodrigues,
    rot_x,
    rot_y,
    rot_z,
)

ANGLES = [
    0.0,
    np.deg2rad(22.5),
    np.pi / 6,
    np.pi / 4,
    np.pi / 2,
    2.0,
    np.pi,
    -1.234,
]

MAKERS = [rot_x, rot_y, rot_z]


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


# --- 1. 열이 서로 직교하는 단위벡터인가 -------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(maker, theta):
    R = maker(theta)

    # 각 열의 길이가 1인지 확인
    for i in range(3):
        assert np.isclose(
            np.linalg.norm(R[:, i]),
            1.0,
            atol=1e-6
        ), f"{maker.__name__}: {i}번째 열의 길이가 1이 아닙니다."

    # 서로 다른 두 열의 내적이 0인지 확인
    for i in range(3):
        for j in range(i + 1, 3):
            assert np.isclose(
                np.dot(R[:, i], R[:, j]),
                0.0,
                atol=1e-6
            ), f"{maker.__name__}: {i}, {j}번째 열이 직교하지 않습니다."


# --- 2. 행렬식이 1인가 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(maker, theta):
    R = maker(theta)

    # np.linalg.det는 검산용
    det_value = np.linalg.det(R)

    assert np.isclose(
        det_value,
        1.0,
        atol=1e-6
    ), f"{maker.__name__}: det(R) = {det_value}"


# --- 3. 역행렬 == 전치 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(maker, theta):
    R = maker(theta)

    # np.linalg.inv는 검산용
    R_inv = np.linalg.inv(R)

    assert np.allclose(
        R_inv,
        R.T,
        atol=1e-6
    ), f"{maker.__name__}: 역행렬과 전치행렬이 다릅니다."

    assert np.allclose(
        R.T @ R,
        np.eye(3),
        atol=1e-6
    ), f"{maker.__name__}: R.T @ R != I"


# --- 4. 재직교화 결과가 직교행렬인가 -----------------------------------------

def test_gram_schmidt_restores_orthogonality(rng):
    # 먼저 정상적인 회전행렬 생성
    R = rot_z(np.deg2rad(30.0))

    # 작은 난수를 추가해서 직교성을 일부러 깨뜨림
    noise = rng.normal(
        0.0,
        1e-4,
        size=(3, 3)
    )

    A = R + noise

    # 재직교화 전 오차
    before_error = orthogonality_error(A)

    # Gram-Schmidt 재직교화
    Q = gram_schmidt(A)

    # 재직교화 후 오차
    after_error = orthogonality_error(Q)

    # 재직교화 후 오차가 감소했는지 확인
    assert after_error < before_error, (
        f"재직교화 전 오차 {before_error}보다 "
        f"후 오차 {after_error}가 작지 않습니다."
    )

    # 직교성 오차가 충분히 작은지 확인
    assert after_error < 1e-12, (
        f"재직교화 후 직교성 오차가 너무 큽니다: {after_error}"
    )

    # 행렬식이 1인지 확인
    # np.linalg.det는 검산용
    det_value = np.linalg.det(Q)

    assert np.isclose(
        det_value,
        1.0,
        atol=1e-6
    ), f"재직교화 후 det(Q)가 1이 아닙니다: {det_value}"

    # 최종적으로 회전행렬인지 확인
    assert is_rotation(Q), (
        "재직교화 결과가 회전행렬이 아닙니다."
    )


# --- 여기부터는 추가 테스트 (권장) -------------------------------------------
#
# 예)
#
# def test_reflection_is_not_a_rotation():
#     """det = -1 인 반사 행렬은 직교여도 회전이 아니다."""
#
#     R = np.diag([1.0, 1.0, -1.0])
#
#     assert np.isclose(
#         orthogonality_error(R),
#         0.0,
#         atol=1e-6
#     )
#
#     assert not is_rotation(R)
#
#
# def test_rodrigues_matches_rot_z():
#     theta = np.pi / 4
#
#     R1 = rodrigues([0, 0, 1], theta)
#     R2 = rot_z(theta)
#
#     assert np.allclose(R1, R2, atol=1e-6)
#
#
# def test_axis_angle_roundtrip(rng):
#     axis = rng.normal(size=3)
#     axis = axis / np.linalg.norm(axis)
#     theta = 1.0
#
#     R = rodrigues(axis, theta)
#     axis2, theta2 = axis_angle_from_matrix(R)
#
#     assert np.allclose(axis2, axis, atol=1e-6)
#     assert np.isclose(theta2, theta, atol=1e-6)