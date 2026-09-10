cmake_minimum_required(VERSION 3.22)
project(cpp_basics CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# motor.cpp와 main.cpp를 합쳐 main 실행 파일 생성
add_executable(main main.cpp motor.cpp)
