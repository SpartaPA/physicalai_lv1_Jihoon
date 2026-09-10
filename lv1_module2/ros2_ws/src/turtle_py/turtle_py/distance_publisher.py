import math

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult


class TurtleDistancePublisher(Node):

    def __init__(self):
        super().__init__('turtle_distance_publisher')

        # 최신 자세
        self.x = 0.0
        self.y = 0.0

        # 파라미터 선언
        self.declare_parameter('publish_rate', 10.0)

        self.publish_rate = self.get_parameter(
            'publish_rate'
        ).value

        # /turtle1/pose 구독
        self.pose_subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

        # /turtle_distance 발행
        self.distance_publisher = self.create_publisher(
            Float32,
            '/turtle_distance',
            10
        )

        # Timer
        self.timer = self.create_timer(
            1.0 / self.publish_rate,
            self.timer_callback
        )

        # 파라미터 변경 콜백
        self.add_on_set_parameters_callback(
            self.parameter_callback
        )

    def pose_callback(self, msg):
        self.x = msg.x
        self.y = msg.y

    def timer_callback(self):
        distance = math.sqrt(self.x ** 2 + self.y ** 2)

        msg = Float32()
        msg.data = distance

        self.distance_publisher.publish(msg)

    def parameter_callback(self, params):

        for param in params:

            if param.name == 'publish_rate':

                if param.value <= 0:
                    return SetParametersResult(
                        successful=False,
                        reason='publish_rate must be greater than 0'
                    )

                self.publish_rate = param.value

                # 기존 Timer 제거 후 새로운 주기로 생성
                self.timer.cancel()

                self.timer = self.create_timer(
                    1.0 / self.publish_rate,
                    self.timer_callback
                )

                self.get_logger().info(
                    f'publish_rate changed to '
                    f'{self.publish_rate} Hz'
                )

        return SetParametersResult(successful=True)


def main(args=None):

    # 1. ROS 2 초기화
    rclpy.init(args=args)

    # 2. 노드 생성
    node = TurtleDistancePublisher()

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