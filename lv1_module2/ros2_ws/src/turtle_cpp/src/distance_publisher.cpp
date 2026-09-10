#include <cmath>
#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include "turtlesim/msg/pose.hpp"

class DistancePublisher : public rclcpp::Node
{
public:
    DistancePublisher()
    : Node("turtle_distance_publisher"),
      x_(0.0),
      y_(0.0)
    {
        // /turtle1/pose 구독
        pose_subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose",
            10,
            std::bind(
                &DistancePublisher::pose_callback,
                this,
                std::placeholders::_1
            )
        );

        // /turtle_distance 발행
        distance_publisher_ =
            this->create_publisher<std_msgs::msg::Float32>(
                "/turtle_distance",
                10
            );

        // 10Hz = 0.1초
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100),
            std::bind(
                &DistancePublisher::timer_callback,
                this
            )
        );

        RCLCPP_INFO(
            this->get_logger(),
            "거리 발행자 시작 (10 Hz)"
        );
    }

private:
    // /turtle1/pose를 받음
    void pose_callback(
        const turtlesim::msg::Pose::SharedPtr msg)
    {
        x_ = msg->x;
        y_ = msg->y;
    }

    // 10Hz마다 거리 계산 후 발행
    void timer_callback()
    {
        double distance = std::sqrt(
            x_ * x_ + y_ * y_
        );

        std_msgs::msg::Float32 msg;
        msg.data = static_cast<float>(distance);

        distance_publisher_->publish(msg);
    }

    double x_;
    double y_;

    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr
        pose_subscription_;

    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr
        distance_publisher_;

    rclcpp::TimerBase::SharedPtr timer_;
};


int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    auto node = std::make_shared<DistancePublisher>();

    rclcpp::spin(node);

    rclcpp::shutdown();

    return 0;
}