"""문제 6 — 좌표 변환 체인 모듈. (학생 작성용 템플릿)

base -> link -> camera 로 이어지는 동차변환 체인을 구성하고,
카메라 기준 좌표를 로봇 base 기준으로 바꾼다.
모듈 4(픽앤플레이스 미니 프로젝트)에서 그대로 import 해 쓰게 되므로,
공개 함수 이름과 반환 형식을 이 템플릿 그대로 유지한다.
"""

from __future__ import annotations

import numpy as np

from .rotation import axis_angle_from_matrix, rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_points

__all__ = ["CoordinateChain", "default_chain", "camera_point_to_base", "base_point_to_camera"]


class CoordinateChain:
    """부모 -> 자식 동차변환을 이름으로 등록하고, 임의의 두 프레임 사이 변환을 만든다.

    TF2 의 축소판이라고 보면 된다.

    Examples
    --------
    >>> chain = CoordinateChain("base")
    >>> chain.add("base", "link", T_base_link)
    >>> chain.add("link", "camera", T_link_camera)
    >>> T = chain.T("base", "camera")     # camera 좌표 -> base 좌표
    """

    def __init__(self, root: str = "base"):
        self.root = root
        self._parent: dict[str, str] = {}                 # child -> parent
        self._T: dict[tuple[str, str], np.ndarray] = {}   # (parent, child) -> T

    def add(self, parent: str, child: str, T) -> "CoordinateChain":
        """parent 기준으로 표현된 child 프레임의 자세 T(parent<-child) 를 등록한다.

        체이닝이 되도록 self 를 돌려준다. 4x4 가 아니면 ValueError.
        """
        T = np.asarray(T, dtype=float)
        if T.shape != (4, 4):
            raise ValueError(f"4x4 동차변환이 필요합니다. 받은 shape={T.shape}")
        self._parent[child] = parent
        self._T[(parent, child)] = T
        return self

    def get(self, parent: str, child: str) -> np.ndarray:
        """등록해 둔 T(parent <- child) 를 그대로 돌려준다."""
        return self._T[(parent, child)]

    def frames(self) -> list[str]:
        """등록된 프레임 이름 목록 (root 포함)."""
        return [self.root] + list(self._parent.keys())

    # ------------------------------------------------------ 여기부터 구현

    def _path_to_root(self, frame: str) -> list[str]:
        """frame 에서 root 까지의 경로 [frame, ..., root] 를 만든다.

        root 에 연결되어 있지 않으면 KeyError.
        """
        # TODO: 문제 6-1
        path = [frame]
        while frame != self.root:
            if frame not in self._parent:
                raise KeyError(f"root에 연결되지않은 프레임 : {frame}")

            frame = self._parent[frame]
            path.append(frame)
        return path
    

    def T_from_root(self, frame: str) -> np.ndarray:
        """root 기준 frame 의 자세 T(root <- frame).

        경로를 따라가며 등록된 변환을 곱한다. 곱하는 **순서**에 주의할 것:
        윗첨자/아랫첨자가 이웃끼리 상쇄되도록 놓으면 틀리지 않는다.
            T(base<-camera) = T(base<-link) @ T(link<-camera)
        """
        # TODO: 문제 6-1
        path = self._path_to_root(frame)

        T = np.eye(4)

        for i in range(len(path)-1,0,-1):
            parent = path[i]
            child  = path[i -1]

            T = T @ self._T[(parent,child)]
        return T

    def T(self, target: str, source: str) -> np.ndarray:
        T_root_target = self.T_from_root(target)
        T_root_source = self.T_from_root(source)

        return inv_T(T_root_target) @ T_root_source

    

    def transform(self, target: str, source: str, P, w: float = 1.0) -> np.ndarray:
        T = self.T(target, source)
        
        P_arr = np.asarray(P, dtype=float)
        is_1d = (P_arr.ndim == 1)
        
        # 1. (N, 3) 형태로 차원 정렬
        if is_1d:
            P_arr = P_arr.reshape(1, -1)
            
        N = P_arr.shape[0]
        
        # 2. (N, 4) 동차 좌표 생성 (w 값 추가)
        P_h = np.hstack([P_arr, np.full((N, 1), w)])
        
        # 3. 행렬 곱 수행: (N, 4) @ (4, 4).T = (N, 4)
        P_trans_h = P_h @ T.T
        
        # 4. 상단 (N, 3) 3D 좌표만 추출
        result = P_trans_h[:, :3]
        
        # 5. 입력이 단일 점(1D)이었으면 다시 1D로 복원하여 반환
        if is_1d:
            return result[0]
        
        return result  # Shape: (N, 3) 정확히 유지

    def axis_angle(self, target: str, source: str):
        T = self.T(target, source)
        R = T[:3, :3]

        return axis_angle_from_matrix(R)


def default_chain() -> CoordinateChain:
    T_base_link = make_T(
        rot_z(np.deg2rad(22.5)),
        [0.35, 0.05, 0.45]
    )

    T_link_camera = make_T(
        rot_y(np.deg2rad(-22.5)) @ rot_x(np.deg2rad(67.5)),
        [0.12, 0.04, 0.18]
    )

    return (
        CoordinateChain("base")
        .add("base", "link", T_base_link)
        .add("link", "camera", T_link_camera)
    )


def camera_point_to_base(p_cam, chain=None):
    if chain is None:
        chain = default_chain()

    return chain.transform("base", "camera", p_cam)


def base_point_to_camera(p_base, chain=None):
    if chain is None:
        chain = default_chain()

    return chain.transform("camera", "base", p_base)