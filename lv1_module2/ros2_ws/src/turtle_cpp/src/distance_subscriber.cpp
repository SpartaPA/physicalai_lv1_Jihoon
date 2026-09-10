#include <functional>
#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"
#include<iostream>
#include <string>


class Distance_scribe : public rclcpp::Node
{
public:
    Distance_scribe() : Node("Distance_scribe")
    {
        subscription_ = this->create_subscription<std_msgs::msg::Float32>(
            "/turtle_distance",
            10,
            std::bind(
                &Distance_scribe::topic_callback,
                this,
                std::placeholders::_1
            )
        );
    }

private:
    void topic_callback(
        const std_msgs::msg::Float32::SharedPtr msg) const
    {
        RCLCPP_INFO(
            this->get_logger(),
            "Distance: %.2f",
            msg->data
        );
    }

    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_;
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);

    rclcpp::spin(std::make_shared<Distance_scribe>());

    rclcpp::shutdown();

    return 0;
}