

import numpy as np
import pytest

from src.coordinate_chain import default_chain
from src.pose_pipeline import PosePipeline
from src.transform import make_T, transform_points
from src.rotation import rot_x, rot_y, rot_z


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


@pytest.fixture
def pipeline():
    """모듈 ③ default_chain 과 같은 값으로 만든 파이프라인."""
    chain = default_chain()
    return PosePipeline(chain.get("base", "link"), chain.get("link", "camera"))



def test_camera_to_base_matches_chain(pipeline, rng):
    P = rng.normal(size=(10, 3))
    via_pipe = pipeline.camera_to_base(P)
    via_chain = default_chain().transform("base", "camera", P)
    via_mat = transform_points(pipeline.T_base_camera, P)
    assert np.allclose(via_pipe, via_chain)
    assert np.allclose(via_pipe, via_mat)



def test_roundtrip_restores_points(pipeline, rng):
    p_single = rng.normal(size=3)
    assert np.allclose(pipeline.base_to_camera(
        pipeline.camera_to_base(p_single)), p_single)
    P = rng.normal(size=(10, 3))
    assert np.allclose(pipeline.base_to_camera(
        pipeline.camera_to_base(P)), P)


# --- 여기부터는 추가 테스트 (권장) -------------------------------------------
#
# 예) def test_joint_angle_zero_is_nominal(pipeline):
#         """set_joint_angle(0) 이면 T_base_link 가 생성자에 준 값 그대로."""
#
# 예) def test_joint_angle_changes_result(pipeline, rng):
#         """관절 각도를 바꾸면 같은 관측이 base 에서 다른 위치로 간다."""
#
# 예) def test_distance_is_preserved(pipeline, rng):
#         """강체 변환은 두 점 사이 거리를 보존한다."""
#
# 예) def test_rejects_wrong_shape():
#         """(3,3) 을 넣으면 ValueError."""
