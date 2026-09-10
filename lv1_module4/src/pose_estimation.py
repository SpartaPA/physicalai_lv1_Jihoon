"""문제 5 — 점군 자세 추정: PCA · Kabsch · 최소제곱 평면 피팅. (학생 작성용 템플릿)

- `pca_axes`        : 공분산 고유분해로 물체의 주축 3개를 뽑는다
- `kabsch`          : 대응이 알려진 두 점군 사이의 최적 회전·병진을 SVD 로 구한다
- `fit_plane_lstsq` : 최소제곱으로 평면을 피팅하고 점별 잔차를 돌려준다
- `remove_outliers` : 잔차가 큰 점을 걸러낸다

`rotation_angle_deg` 는 제공 코드다 (두 회전행렬 사이 각도).
"""

from __future__ import annotations

import numpy as np

__all__ = ["pca_axes", "kabsch", "fit_plane_lstsq", "remove_outliers", "rotation_angle_deg"]


def rotation_angle_deg(R_a, R_b) -> float:
    """두 회전행렬 사이의 각도 [deg] — R_a^T R_b 의 회전각. (제공 코드)"""
    R_rel = np.asarray(R_a, dtype=float).T @ np.asarray(R_b, dtype=float)
    cos_theta = np.clip((np.trace(R_rel) - 1.0) / 2.0, -1.0, 1.0)
    return float(np.rad2deg(np.arccos(cos_theta)))


def pca_axes(P):
    """점군 (N,3) 의 주축을 고유분해로 뽑는다.

    1. centroid = P 의 평균, X = P - centroid
    2. C = X^T X / (N - 1)   (3x3 공분산)
    3. C 를 고유분해 (`np.linalg.eigh` — 대칭행렬 전용, 실수 고유값)
    4. 고유값 **내림차순**으로 정렬해 axes 의 열 0,1,2 가 각각 긴 축 -> 짧은 축이 되게 한다
    5. det(axes) = +1 이 되도록 (오른손 좌표계) 필요하면 마지막 열의 부호를 뒤집는다

    Returns
    -------
    axes : (3,3) 열이 주축 (단위벡터, 서로 직교, det = +1) — 회전행렬로 그대로 쓸 수 있다
    eigvals : (3,) 내림차순 고유값 (각 축 방향 분산)
    centroid : (3,) 점군 중심
    """
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("P는 (N, 3) 형태이어야 합니다.")
    if P.shape[0] < 2:
        raise ValueError("PCA에는 2개 이상의 점이 필요합니다.")

    centroid = P.mean(axis=0)
    X = P - centroid
    C = X.T @ X / (P.shape[0] - 1)
    eigvals_asc, eigvecs_asc = np.linalg.eigh(C)
    order = np.argsort(eigvals_asc)[::-1]
    eigvals = eigvals_asc[order]
    axes = eigvecs_asc[:, order]
    if np.linalg.det(axes) < 0:
        axes[:, -1] = -axes[:, -1]
    return axes, eigvals, centroid


def kabsch(P, Q):
    """대응이 알려진 두 점군 P, Q (N,3) 에 대해 Q ~ P @ R.T + t 를 만족하는 (R, t) 를 구한다.

    1. 두 점군의 중심 cP, cQ 를 빼서 X = P - cP, Y = Q - cQ
    2. H = X^T Y  (3x3 교차 공분산)
    3. U, S, Vt = svd(H)
    4. d = sign(det(V U^T)) — 반사가 나오면 (-1) 보정: D = diag(1, 1, d)
    5. R = V D U^T,  t = cQ - R cP

    Returns
    -------
    R : (3,3) 회전행렬 (det = +1)
    t : (3,) 병진
    """
    P = np.asarray(P, dtype=float)
    Q = np.asarray(Q, dtype=float)
    if P.ndim != 2 or P.shape[1] != 3 or Q.ndim != 2 or Q.shape[1] != 3:
        raise ValueError("P, Q는 (N, 3) 형태이어야 합니다.")
    if P.shape[0] != Q.shape[0] or P.shape[0] < 3:
        raise ValueError("P, Q는 같은 개수(N>=3)의 대응점이 필요합니다.")

    cP = P.mean(axis=0)
    cQ = Q.mean(axis=0)
    X = P - cP
    Y = Q - cQ
    H = X.T @ Y
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    if np.isclose(d, 0.0):
        d = 1.0
    Dmat = np.diag([1.0, 1.0, d])
    R = Vt.T @ Dmat @ U.T
    t = cQ - R @ cP
    return R, t


def fit_plane_lstsq(P):
    """점군 (N,3) 에 평면 n . p + d = 0 을 최소제곱으로 피팅한다.

    권장 방법 (정규방정식): z = a x + b y + c 로 두고
        A = [x, y, 1],  b = z,   (A^T A) [a, b, c]^T = A^T b
    를 풀면 평면 a x + b y - z + c = 0 이므로 법선 n = (a, b, -1) 을 정규화한다.
    (평면이 z축과 나란하면 이 모델은 못 쓴다 — 그런 경우 SVD 로 최소 분산 방향을 쓴다.)

    Returns
    -------
    normal : (3,) 단위 법선
    d : float — 평면 상수 (n . p + d = 0)
    residuals : (N,) 각 점의 부호 있는 평면까지의 거리 n . p + d
    """
    P = np.asarray(P, dtype=float)
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("P는 (N, 3) 형태이어야 합니다.")
    if P.shape[0] < 3:
        raise ValueError("평면 피팅에는 3개 이상의 점이 필요합니다.")

    A = np.column_stack([P[:, 0], P[:, 1], np.ones(P.shape[0])])
    b = P[:, 2]
    try:
        sol, _, rank, _ = np.linalg.lstsq(A, b, rcond=None)
        if rank < 3:
            raise np.linalg.LinAlgError("rank 부족")
        a, bb, c = sol
        n_unnorm = np.array([a, bb, -1.0])
        nn = np.linalg.norm(n_unnorm)
        normal = n_unnorm / nn
        d = c / nn
    except np.linalg.LinAlgError:
        # 수직 평면 등: 최소 분산 방향을 법선으로 (SVD)
        centroid = P.mean(axis=0)
        _, _, Vt = np.linalg.svd(P - centroid, full_matrices=False)
        normal = Vt[-1] / np.linalg.norm(Vt[-1])
        d = float(-normal @ centroid)

    residuals = P @ normal + d
    return normal, float(d), residuals


def remove_outliers(P, residuals, k: float = 3.0):
    """잔차가 큰 점을 제거한다.

    기준: |residual| < k * sigma. sigma 는 이상치에 강한 추정치를 권장한다
        sigma = 1.4826 * median(|residual - median(residual)|)      (MAD)
    (단순 std 를 쓰면 이상치가 sigma 자체를 키워 걸러지지 않을 수 있다.)

    Returns
    -------
    P_clean : (M,3) 남은 점
    mask : (N,) bool — True 가 남긴 점. P 와 대응 점군에 같은 mask 를 적용해야 Kabsch 대응이 유지된다
    """
    P = np.asarray(P, dtype=float)
    residuals = np.asarray(residuals, dtype=float)
    if P.ndim != 2 or P.shape[1] != 3:
        raise ValueError("P는 (N, 3) 형태이어야 합니다.")
    if residuals.shape != (P.shape[0],):
        raise ValueError("residuals는 (N,) 형태이어야 합니다.")

    med = np.median(residuals)
    sigma = 1.4826 * np.median(np.abs(residuals - med))
    if np.isclose(sigma, 0.0):
        # 모든 잔차가 동일하면 중앙값과 같은 점만 유지
        mask = np.isclose(residuals, med)
    else:
        mask = np.abs(residuals) < k * sigma
    return P[mask], mask
