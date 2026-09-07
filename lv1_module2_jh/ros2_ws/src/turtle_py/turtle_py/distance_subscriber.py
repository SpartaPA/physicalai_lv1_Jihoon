import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult


class DistanceSubscriber(Node):

    def __init__(self):
        super().__init__('turtle_distance_subscriber')

        # 경고 임계값 파라미터
        self.declare_parameter('warn_distance', 2.5)

        # 파라미터 초기값 읽기
        self.warn_distance = self.get_parameter(
            'warn_distance'
        ).value

        # /turtle_distance 구독
        self.subscription = self.create_subscription(
            Float32,
            '/turtle_distance',
            self.distance_callback,
            10
        )

        # 실행 중 파라미터 변경 허용
        self.add_on_set_parameters_callback(
            self.parameter_callback
        )

        self.get_logger().info(
            f'거리 구독 시작 '
            f'(임계값: {self.warn_distance:.2f} m)'
        )

    def distance_callback(self, msg):
        distance = msg.data

        # 임계값을 넘으면 경고
        if distance > self.warn_distance:
            self.get_logger().warn(
                f'경고: 원점 거리 {distance:.2f} m > '
                f'임계값 {self.warn_distance:.2f} m'
            )

    def parameter_callback(self, params):

        for param in params:

            if param.name == 'warn_distance':

                if param.value < 0.0:
                    return SetParametersResult(
                        successful=False,
                        reason='임계값은 0 이상이어야 합니다.'
                    )

                self.warn_distance = param.value

                self.get_logger().info(
                    f'임계값이 {self.warn_distance:.2f} m로 '
                    f'변경되었습니다.'
                )

        return SetParametersResult(
            successful=True
        )


def main(args=None):

    # 1. ROS 2 초기화
    rclpy.init(args=args)

    # 2. 노드 생성
    node = DistanceSubscriber()

    try:
        # 3. 노드 실행
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        # 4. 노드 제거
        node.destroy_node()

        # 5. ROS 2 종료
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()