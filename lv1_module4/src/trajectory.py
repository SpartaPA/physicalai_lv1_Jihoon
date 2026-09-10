"""문제 4 — 궤적 보간. (학생 작성용 템플릿)

경유점(waypoint)을 지나는 궤적을 선형 보간 / 큐빅 스플라인으로 만들고,
시작·끝에서 속도와 가속도가 0 이 되는 5차 다항식 프로파일을 구현한다.

입력 규약
--------
- t_wp : (M,) 경유점 시각, 오름차순
- q_wp : (M,) 스칼라 궤적 또는 (M, D) 다차원 궤적 (예: 3차원 위치는 D = 3)
- t    : (N,) 평가할 시각 (t_wp[0] <= t <= t_wp[-1])
- 반환 : q_wp 가 (M,) 이면 (N,), (M, D) 이면 (N, D)

큐빅 스플라인은 `scipy.interpolate.CubicSpline` 을 써도 된다 (axis=0).
"""

from __future__ import annotations

import numpy as np

__all__ = ["linear_interp", "cubic_spline_interp", "quintic_profile", "finite_diff"]


def linear_interp(t_wp, q_wp, t) -> np.ndarray:
    """경유점 사이를 직선으로 잇는 보간. 각 차원마다 `np.interp` 를 쓰면 된다.

    위치는 이어지지만 경유점에서 속도가 불연속(꺾임)이다.
    """
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)

    if t_wp.ndim != 1:
        raise ValueError("t_wp는 (M,) 형태이어야 합니다.")
    if q_wp.shape[0] != t_wp.shape[0]:
        raise ValueError("q_wp의 첫 축 길이가 t_wp와 같아야 합니다.")

    if q_wp.ndim == 1:
        return np.interp(t, t_wp, q_wp)
    if q_wp.ndim == 2:
        out = np.empty((t.shape[0], q_wp.shape[1]), dtype=float)
        for d in range(q_wp.shape[1]):
            out[:, d] = np.interp(t, t_wp, q_wp[:, d])
        return out
    raise ValueError("q_wp는 (M,) 또는 (M, D) 형태이어야 합니다.")


def cubic_spline_interp(t_wp, q_wp, t, bc_type: str = "natural") -> np.ndarray:
    """경유점을 지나는 큐빅 스플라인 보간 (위치·속도·가속도가 모두 연속, C2).

    bc_type : 양끝 경계 조건. "natural" (양끝 가속도 0) 또는 "clamped" (양끝 속도 0).
    """
    t_wp = np.asarray(t_wp, dtype=float)
    q_in = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)

    if t_wp.ndim != 1:
        raise ValueError("t_wp는 (M,) 형태이어야 합니다.")
    if bc_type not in ("natural", "clamped"):
        raise ValueError("bc_type은 'natural' 또는 'clamped'이어야 합니다.")
    n = t_wp.shape[0]
    if n < 2:
        raise ValueError("경유점이 2개 이상 필요합니다.")
    if q_in.shape[0] != n:
        raise ValueError("q_wp의 첫 축 길이가 t_wp와 같아야 합니다.")
    if np.any(np.diff(t_wp) <= 0):
        raise ValueError("t_wp는 오름차순이어야 합니다.")

    is_1d = (q_in.ndim == 1)
    if q_in.ndim == 1:
        Y = q_in.reshape(n, 1)
    elif q_in.ndim == 2:
        Y = q_in
    else:
        raise ValueError("q_wp는 (M,) 또는 (M, D) 형태이어야 합니다.")

    h = np.diff(t_wp)  # (n-1,)
    if np.any(h <= 0):
        raise ValueError("t_wp는 오름차순이어야 합니다.")

    # 2계 도함수 M (n, D) — 삼중대각 시스템 (Thomas 알고리즘)
    D = Y.shape[1]
    M = np.zeros((n, D), dtype=float)

    if n == 2:
        # 점 2개면 직선 (natural/clamped 모두 동일)
        pass
    else:
        # n x n 삼중대각 조립 (a[0], c[-1] 미사용)
        a_full = np.zeros(n)
        b_full = np.zeros(n)
        c_full = np.zeros(n)
        rhs_full = np.zeros((n, D))

        if bc_type == "natural":
            # M0 = M_{n-1} = 0
            b_full[0] = 1.0
            rhs_full[0] = 0.0
            b_full[-1] = 1.0
            rhs_full[-1] = 0.0
            for i in range(1, n - 1):
                a_full[i] = h[i - 1]
                b_full[i] = 2.0 * (h[i - 1] + h[i])
                c_full[i] = h[i]
                rhs_full[i] = 6.0 * ((Y[i + 1] - Y[i]) / h[i]
                                     - (Y[i] - Y[i - 1]) / h[i - 1])
        else:  # clamped, 양끝 속도 0
            # 첫 행: 2*h0*M0 + h0*M1 = 6*((y1-y0)/h0 - 0)
            # 끝 행: h_{n-2}*M_{n-2} + 2*h_{n-2}*M_{n-1} = 6*(0 - (y_{n-1}-y_{n-2})/h_{n-2})
            b_full[0] = 2.0 * h[0]
            c_full[0] = h[0]
            rhs_full[0] = 6.0 * ((Y[1] - Y[0]) / h[0])
            for i in range(1, n - 1):
                a_full[i] = h[i - 1]
                b_full[i] = 2.0 * (h[i - 1] + h[i])
                c_full[i] = h[i]
                rhs_full[i] = 6.0 * ((Y[i + 1] - Y[i]) / h[i]
                                     - (Y[i] - Y[i - 1]) / h[i - 1])
            a_full[-1] = h[-1]
            b_full[-1] = 2.0 * h[-1]
            rhs_full[-1] = 6.0 * (-(Y[-1] - Y[-2]) / h[-1])
        M = _solve_tridiag_full(a_full, b_full, c_full, rhs_full)

    out = np.empty((t.shape[0], D), dtype=float)
    # 구간 탐색 (벡터화)
    idx = np.searchsorted(t_wp, t, side="right") - 1
    idx = np.clip(idx, 0, n - 2)
    for k in range(t.shape[0]):
        i = idx[k]
        hi = h[i]
        ti, tip1 = t_wp[i], t_wp[i + 1]
        tk = t[k]
        A = (tip1 - tk) / hi
        B = (tk - ti) / hi
        out[k] = (M[i] * (tip1 - tk) ** 3 / (6.0 * hi)
                  + M[i + 1] * (tk - ti) ** 3 / (6.0 * hi)
                  + (Y[i] - M[i] * hi ** 2 / 6.0) * A
                  + (Y[i + 1] - M[i + 1] * hi ** 2 / 6.0) * B)

    if is_1d:
        return out[:, 0]
    return out


def _solve_tridiag_full(a, b, c, rhs):
    """n x n 삼중대각 풀이 (a[0], c[-1] 미사용)."""
    n = b.shape[0]
    cp = np.zeros(n)
    dp = np.zeros_like(rhs)
    cp[0] = c[0] / b[0]
    dp[0] = rhs[0] / b[0]
    for i in range(1, n):
        denom = b[i] - a[i] * cp[i - 1]
        if i < n - 1:
            cp[i] = c[i] / denom
        dp[i] = (rhs[i] - a[i] * dp[i - 1]) / denom
    x = np.zeros_like(rhs)
    x[-1] = dp[-1]
    for i in range(n - 2, -1, -1):
        x[i] = dp[i] - cp[i] * x[i + 1]
    return x


def quintic_profile(t, t0: float, tf: float, q0, qf,
                    v0=0.0, vf=0.0, a0=0.0, af=0.0):
    """5차 다항식 궤적 q(t) 와 그 도함수 (q, qd, qdd) 를 돌려준다.

    경계 조건 6개 — q(t0)=q0, q(tf)=qf, qd(t0)=v0, qd(tf)=vf, qdd(t0)=a0, qdd(tf)=af —
    로 계수 6개 (c0 ~ c5) 를 정한다. 경계 속도·가속도가 모두 0 인 기본형은

        tau = (t - t0) / (tf - t0)
        s(tau) = 10 tau^3 - 15 tau^4 + 6 tau^5
        q(t) = q0 + (qf - q0) s(tau)

    로 닫힌 꼴이 있고, 일반형은 6x6 선형계를 풀면 된다. 어느 쪽으로 구현해도 된다.
    q0, qf 가 스칼라이면 (N,), (D,) 이면 (N, D) 를 돌려준다.

    Returns
    -------
    q, qd, qdd : 위치, 속도, 가속도 (해석적 미분. 유한차분이 아니다)
    """
    t = np.asarray(t, dtype=float)
    if tf <= t0:
        raise ValueError("tf는 t0보다 커야 합니다.")

    q0a = np.asarray(q0, dtype=float)
    qfa = np.asarray(qf, dtype=float)
    v0a = np.asarray(v0, dtype=float)
    vfa = np.asarray(vf, dtype=float)
    a0a = np.asarray(a0, dtype=float)
    afa = np.asarray(af, dtype=float)

    scalar = (q0a.ndim == 0 and qfa.ndim == 0)
    # 브로드캐스트 차원 결정
    try:
        D = np.broadcast_shapes(q0a.shape, qfa.shape, v0a.shape,
                                vfa.shape, a0a.shape, afa.shape)
    except ValueError:
        raise ValueError("q0, qf, v0, vf, a0, af의 shape이 맞지 않습니다.")
    q0b = np.broadcast_to(q0a, D)
    qfb = np.broadcast_to(qfa, D)
    v0b = np.broadcast_to(v0a, D)
    vfb = np.broadcast_to(vfa, D)
    a0b = np.broadcast_to(a0a, D)
    afb = np.broadcast_to(afa, D)

    T = float(tf - t0)
    # 6x6 계수행렬 (s = t - t0 기준): [1 s s^2 ... s^5] 와 도함수
    Mmat = np.array([
        [1, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0],
        [0, 0, 2, 0, 0, 0],
        [1, T, T**2, T**3, T**4, T**5],
        [0, 1, 2*T, 3*T**2, 4*T**3, 5*T**4],
        [0, 0, 2, 6*T, 12*T**2, 20*T**3],
    ], dtype=float)
    B = np.stack([q0b, v0b, a0b, qfb, vfb, afb], axis=0)  # (6, *D)
    Bf = B.reshape(6, -1)  # (6, K)
    C = np.linalg.solve(Mmat, Bf)  # (6, K)

    s = (t - t0)  # (N,)
    S = np.stack([np.ones_like(s), s, s**2, s**3, s**4, s**5], axis=0)  # (6, N)
    Sd = np.stack([np.zeros_like(s), np.ones_like(s), 2*s,
                   3*s**2, 4*s**3, 5*s**4], axis=0)
    Sdd = np.stack([np.zeros_like(s), np.zeros_like(s), 2*np.ones_like(s),
                    6*s, 12*s**2, 20*s**3], axis=0)
    Q = (C.T @ S)    # (K, N)
    Qd = (C.T @ Sd)
    Qdd = (C.T @ Sdd)

    if scalar:
        return Q[0], Qd[0], Qdd[0]
    # (N, *D)
    shape_out = (t.shape[0],) + D
    return (Q.T.reshape(shape_out), Qd.T.reshape(shape_out),
            Qdd.T.reshape(shape_out))


def finite_diff(y, t) -> np.ndarray:
    """시간축(axis 0)에 대한 수치 미분. `np.gradient(y, t, axis=0)` 를 쓰면 된다.

    y : (N,) 또는 (N, D),  t : (N,)
    속도 = finite_diff(q, t),  가속도 = finite_diff(속도, t)
    """
    y = np.asarray(y, dtype=float)
    t = np.asarray(t, dtype=float)
    if t.ndim != 1:
        raise ValueError("t는 (N,) 형태이어야 합니다.")
    if y.shape[0] != t.shape[0]:
        raise ValueError("y의 첫 축 길이가 t와 같아야 합니다.")
    return np.gradient(y, t, axis=0)
