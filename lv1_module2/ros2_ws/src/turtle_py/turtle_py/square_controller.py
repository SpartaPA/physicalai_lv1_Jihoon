import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class SquareController(Node):

    def __init__(self):
        super().__init__('square_controller')

        self.publisher = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        # 현재 단계
        # 0: 전진, 1: 회전
        self.step = 0
        self.side_count = 0

        # 각 단계의 시작 시간
        self.step_start_time = self.get_clock().now()

        # 전진 속도 / 회전 속도
        self.linear_speed = 1.0
        self.angular_speed = 1.57   # 약 90도/초

        # 정사각형 한 변을 약 2초 전진
        self.forward_duration = 2.0

        # 90도 회전하는 데 약 1초
        self.turn_duration = 1.0

        # 10Hz로 명령 발행
        self.timer = self.create_timer(0.1, self.control_loop)

        self.get_logger().info('정사각형 주행 시작')

    def control_loop(self):
        now = self.get_clock().now()
        elapsed = (now - self.step_start_time).nanoseconds / 1e9

        msg = Twist()

        # 전진
        if self.step == 0:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0

            if elapsed >= self.forward_duration:
                self.step = 1
                self.step_start_time = now

        # 제자리 회전
        elif self.step == 1:
            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed

            if elapsed >= self.turn_duration:
                self.side_count += 1
                self.step_start_time = now

                # 네 변을 모두 돌았으면 종료
                if self.side_count >= 4:
                    self.stop()
                    self.get_logger().info('정사각형 한 바퀴 완료')
                    self.timer.cancel()
                    return

                self.step = 0

        self.publisher.publish(msg)

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = SquareController()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()