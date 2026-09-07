cmake_minimum_required(VERSION 3.8)
project(turtle_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(turtlesim REQUIRED)

# C++ executable
add_executable(distance_publisher
  src/distance_publisher.cpp
)

# ROS 2 dependencies
ament_target_dependencies(distance_publisher
  rclcpp
  std_msgs
  turtlesim
)

# C++ executable
add_executable(distance_subscriber
  src/distance_subscriber.cpp
)

ament_target_dependencies(distance_subscriber
  rclcpp
  std_msgs
  turtlesim
)

# Install executable
install(
  TARGETS distance_publisher distance_subscriber
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()