import numpy as np


def dot(a, b):
    """두 벡터의 내적"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    return np.sum(a*b)



def norm(v):
    """벡터의 크기"""
    v = np.asarray(v, dtype=float)
    return np.sqrt(np.sum(v*v))



def normalize(v):
    """벡터 정규화"""
    v = np.asarray(v, dtype=float)

    length = norm(v)

    if np.isclose(length, 0.0):
        raise ValueError("영벡터는 정규화할 수 없습니다.")

    return v / length


def angle_between(a, b):
    """두 벡터 사이각을 degree 단위로 반환"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    na = norm(a)
    nb = norm(b)

    if np.isclose(na, 0.0) or np.isclose(nb, 0.0):
        raise ValueError("영벡터와의 사이각은 정의할 수 없습니다.")

    cos_theta = dot(a, b) / (na * nb)

    # 부동소수점 오차 방지
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    return np.degrees(np.arccos(cos_theta))


def cross(a, b):
    """두 3차원 벡터의 외적"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    return np.array([
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ])

def project(a, b):
    """a를 b 방향으로 정사영"""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)

    denominator = dot(b, b)

    if np.isclose(denominator, 0.0):
        raise ValueError("영벡터 방향으로는 투영할 수 없습니다.")

    return (dot(a, b) / denominator) * b


def reject(a, b):
    """a에서 b 방향 성분을 제거한 수직 성분"""
    return np.asarray(a, dtype=float) - project(a, b)


def skew(a):
    """3차원 벡터의 반대칭행렬"""
    a = np.asarray(a, dtype=float)

    if a.shape != (3,):
        raise ValueError("skew는 3차원 벡터만 지원합니다.")

    x, y, z = a

    return np.array([
        [0, -z, y],
        [z, 0, -x],
        [-y, x, 0]
    ])


def plane_normal(P1, P2, P3):
    """세 점이 만드는 평면의 단위 법선 벡터"""
    P1 = np.asarray(P1, dtype=float)
    P2 = np.asarray(P2, dtype=float)
    P3 = np.asarray(P3, dtype=float)

    u = P2 - P1
    v = P3 - P1

    n = cross(u, v)
    length = norm(n)

    if np.isclose(length, 0.0):
        raise ValueError("세 점이 일직선이므로 법선을 정의할 수 없습니다.")

    return n / length


def det(A):
    """행렬식"""
    A = np.asarray(A, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("행렬식은 정방행렬에 대해서만 계산할 수 있습니다.")

    n = A.shape[0]

    # 1x1 행렬
    if n == 1:
        return A[0, 0]

    # 2x2 행렬
    if n == 2:
        return (
            A[0, 0] * A[1, 1]
            - A[0, 1] * A[1, 0]
        )

    # 첫 번째 행을 기준으로 여인수 전개
    result = 0.0

    for col in range(n):
        minor = np.delete(
            np.delete(A, 0, axis=0),
            col,
            axis=1
        )

        sign = 1.0 if col % 2 == 0 else -1.0

        result += sign * A[0, col] * det(minor)

    return result


def rank(A):
    """행렬의 rank를 가우스 소거를 이용해 직접 계산한다."""
    A = np.asarray(A, dtype=float).copy()

    if A.ndim != 2:
        raise ValueError("2차원 행렬을 입력해야 합니다.")

    rows, cols = A.shape
    pivot_row = 0

    for col in range(cols):
        if pivot_row >= rows:
            break

        # 현재 열에서 가장 큰 값의 위치를 찾는다.
        pivot = pivot_row + np.argmax(np.abs(A[pivot_row:, col]))

        # 유효한 피벗이 없으면 다음 열로 넘어간다.
        if np.isclose(A[pivot, col], 0.0):
            continue

        # 필요한 경우 행을 교환한다.
        if pivot != pivot_row:
            A[[pivot_row, pivot]] = A[[pivot, pivot_row]]

        # 피벗 아래의 값들을 0으로 만든다.
        for row in range(pivot_row + 1, rows):
            factor = A[row, col] / A[pivot_row, col]
            # 수정: A[pivot_row, col] -> A[pivot_row, col:] (행 전체 슬라이싱)
            A[row, col:] -= factor * A[pivot_row, col:]

            # 부동소수점 미세 잔차 정리
            A[row, np.isclose(A[row], 0.0)] = 0.0

        # 피벗 하나를 찾았으므로 rank 증가
        pivot_row += 1

    return pivot_row


def gauss_eliminate(A, b, pivoting=True, verbose=False):

    A = np.asarray(A, dtype=float).copy()   
    b=np.asarray(b, dtype=float).copy()

    if A.ndim != 2:
        raise ValueError("A는 2차원 행렬이어야 합니다.")

    rows, cols = A.shape

    if rows != cols:
        raise ValueError("현재 구현은 정방행렬만 지원합니다.")

    if b.shape != (rows,):
        raise ValueError("b의 크기가 A의 행 수와 같아야 합니다.")

    n = len(b)
    # 첨가행렬 [A | b] 생성
    Ab = np.hstack([A,b.reshape(-1,1)])

    
    steps = [Ab.copy()]
    
    # --- 1. 전방 소거 (Forward Elimination) ---
    for i in range(n):
        if pivoting:
            # i번째 열에서 절댓값이 가장 큰 피벗 행 찾기
            pivot = i + np.argmax(np.abs(Ab[i:, i]))
            if pivot != i:
                Ab[[i, pivot]] = Ab[[pivot, i]]
                if verbose:
                    print(f"행 교환: R{i+1} <-> R{pivot+1}")
        
        if np.isclose(Ab[i, i], 0.0):
           raise ValueError("피벗이 0이므로 유일해를 구할 수 없습니다.")
            
        # i번째 행 아래의 성분들을 0으로 소거
        for j in range(i + 1, n):
            factor = Ab[j, i] / Ab[i, i]
            Ab[j, i:] -= factor * Ab[i, i:]
            
        steps.append(Ab.copy())
        
    # --- 2. 후진 대입 (Back Substitution) ---
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (Ab[i, -1] - dot(Ab[i, i + 1:n], x[i + 1:n])) / Ab[i, i]
        
    return x, steps

def inverse_gauss_jordan(A):
    """가우스-조던 소거법으로 역행렬을 계산한다."""

    A = np.asarray(A, dtype=float)

    if A.ndim != 2 or A.shape[0] != A.shape[1]:
        raise ValueError("정방행렬만 사용할 수 있습니다.")

    n = A.shape[0]

    # [A | I]
    M = np.hstack((A.copy(), np.eye(n)))

    for col in range(n):

        # 부분 피벗팅
        pivot = col + np.argmax(np.abs(M[col:, col]))

        if np.isclose(M[pivot, col], 0.0):
            raise ValueError("역행렬이 존재하지 않습니다.")

        # 필요한 경우 행 교환
        if pivot != col:
            M[[col, pivot]] = M[[pivot, col]]

        # 피벗을 1로 만든다.
        M[col] = M[col] / M[col, col]

        # 다른 모든 행의 현재 열을 0으로 만든다.
        for row in range(n):
            if row == col:
                continue

            factor = M[row, col]
            M[row] -= factor * M[col]

    # 오른쪽 부분이 A의 역행렬
    return M[:, n:]

def row_echelon(A):
    """행렬을 행 사다리꼴 형태로 변환한다."""

    A = np.asarray(A, dtype=float).copy()

    if A.ndim != 2:
        raise ValueError("2차원 행렬을 입력해야 합니다.")

    rows, cols = A.shape
    pivot_row = 0
    pivots = []
    swaps = 0

    for col in range(cols):

        if pivot_row >= rows:
            break

        # 현재 열에서 가장 큰 피벗 선택
        pivot = pivot_row + np.argmax(
            np.abs(A[pivot_row:, col])
        )

        # 유효한 피벗이 없으면 다음 열
        if np.isclose(A[pivot, col], 0.0):
            continue

        # 행 교환
        if pivot != pivot_row:
            A[[pivot_row, pivot]] = A[[pivot, pivot_row]]
            swaps += 1

        # 피벗을 1로 만든다.
        A[pivot_row] /= A[pivot_row, col]

        # 피벗 아래를 0으로 만든다.
        for row in range(pivot_row + 1, rows):
            factor = A[row, col]
            A[row] -= factor * A[pivot_row]

        pivots.append(col)
        pivot_row += 1

    return A, pivots, swaps
 