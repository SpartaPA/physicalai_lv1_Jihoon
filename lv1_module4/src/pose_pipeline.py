"""문제 2 — camera 에서 base 로의 변환 파이프라인"""

from __future__ import annotations

import numpy as np

from .rotation import rot_x, rot_y, rot_z
from .transform import inv_T, make_T, transform_points, transform_point

__all__ = ["PosePipeline"]

_ROT = {"x": rot_x, "y": rot_y, "z": rot_z}


class PosePipeline:

    def __init__(self, T_base_link, T_link_camera, joint_axis: str = "z"):
        T_base_link = np.asarray(T_base_link, dtype=float)
        T_link_camera = np.asarray(T_link_camera, dtype=float)

        if T_base_link.shape != (4, 4):
            raise ValueError("T_base_link는 4x4 행렬이어야 합니다.")

        if T_link_camera.shape != (4, 4):
            raise ValueError("T_link_camera는 4x4 행렬이어야 합니다.")

        if joint_axis not in _ROT:
            raise ValueError("joint_axis는 x, y, z 중 하나여야 합니다.")

        self._T_base_link0 = T_base_link.copy()
        self._T_link_camera = T_link_camera.copy()

        self.joint_axis = joint_axis
        self.joint_angle = 0.0

    @property
    def T_base_link(self) -> np.ndarray:
        R = _ROT[self.joint_axis](self.joint_angle)
        T_joint = make_T(R, [0, 0, 0])

        return self._T_base_link0 @ T_joint

    @property
    def T_link_camera(self) -> np.ndarray:
        return self._T_link_camera

    @property
    def T_base_camera(self) -> np.ndarray:
        return self.T_base_link @ self.T_link_camera

    @property
    def T_camera_base(self) -> np.ndarray:
        return inv_T(self.T_base_camera)

    def set_joint_angle(self, theta: float) -> "PosePipeline":
        self.joint_angle = float(theta)
        return self

    def camera_to_base(self, P_cam) -> np.ndarray:
        P_cam = np.asarray(P_cam, dtype=float)

        if P_cam.ndim == 1:
            return transform_point(self.T_base_camera, P_cam)

        return transform_points(self.T_base_camera, P_cam)


    def base_to_camera(self, P_base) -> np.ndarray:
        P_base = np.asarray(P_base, dtype=float)

        if P_base.ndim == 1:
            return transform_point(self.T_camera_base, P_base)

        return transform_points(self.T_camera_base, P_base)

    def object_pose_in_base(self, T_camera_object) -> np.ndarray:
        T_camera_object = np.asarray(T_camera_object, dtype=float)

        if T_camera_object.shape != (4, 4):
            raise ValueError("T_camera_object는 4x4 행렬이어야 합니다.")

        return self.T_base_camera @ T_camera_object

    def __repr__(self) -> str:
        return "PosePipeline(joint_axis={!r}, joint_angle={:.4f} rad)".format(
            getattr(self, "joint_axis", "?"),
            getattr(self, "joint_angle", float("nan"))
        )