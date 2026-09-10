"""문제 6 — 좌표 변환 체인 모듈."""

from __future__ import annotations

import numpy as np

from .rotation import axis_angle_from_matrix, rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_point, transform_points

__all__ = [
    "CoordinateChain",
    "default_chain",
    "camera_point_to_base",
    "base_point_to_camera"
]


class CoordinateChain:

    def __init__(self, root: str = "base"):
        self.root = root
        self._parent = {}
        self._T = {}

    def add(self, parent: str, child: str, T) -> "CoordinateChain":
        T = np.asarray(T, dtype=float)

        if T.shape != (4, 4):
            raise ValueError(f"4x4 동차변환이 필요합니다. 받은 shape={T.shape}")

        self._parent[child] = parent
        self._T[(parent, child)] = T

        return self

    def get(self, parent: str, child: str) -> np.ndarray:
        return self._T[(parent, child)]

    def frames(self) -> list[str]:
        return [self.root] + list(self._parent.keys())

    def _path_to_root(self, frame: str) -> list[str]:
        path = [frame]

        while frame != self.root:
            if frame not in self._parent:
                raise KeyError(f"root에 연결되지않은 프레임 : {frame}")

            frame = self._parent[frame]
            path.append(frame)

        return path

    def T_from_root(self, frame: str) -> np.ndarray:
        path = self._path_to_root(frame)

        T = np.eye(4)

        for i in range(len(path) - 1, 0, -1):
            parent = path[i]
            child = path[i - 1]

            T = T @ self._T[(parent, child)]

        return T

    def T(self, target: str, source: str) -> np.ndarray:
        T_root_target = self.T_from_root(target)
        T_root_source = self.T_from_root(source)

        return inv_T(T_root_target) @ T_root_source

    def transform(
        self,
        target: str,
        source: str,
        P,
        w: float = 1.0
    ) -> np.ndarray:

        T = self.T(target, source)
        P = np.asarray(P, dtype=float)

        if P.ndim == 1:
            return transform_point(T, P)

        return transform_points(T, P)

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