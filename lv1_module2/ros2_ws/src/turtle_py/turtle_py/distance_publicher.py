import math

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
from std_msgs.msg import Float32


class TurtleDistancePublisher(Node):

    def __init__(self):
        super().__init__('turtle_distance_publisher')

        # 최신 자세를 저장할 변수
        self.x = 0.0
        self.y = 0.0

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

        # 10Hz = 0.1초마다 타이머 실행
        self.timer = self.create_timer(
            0.1,
            self.timer_callback
        )

    # 구독 콜백: 최신 자세를 저장만 함
    def pose_callback(self, msg):
        self.x = msg.x
        self.y = msg.y

    # 타이머 콜백: 거리 계산 후 발행
    def timer_callback(self):
        distance = math.sqrt(self.x ** 2 + self.y ** 2)

        msg = Float32()
        msg.data = distance

        self.distance_publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = TurtleDistancePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()