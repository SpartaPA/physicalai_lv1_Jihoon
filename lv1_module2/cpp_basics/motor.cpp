#include "motor.hpp"
#include <iostream>

// 생성자: 초기 상태는 정지, RPM은 0
Motor::Motor() : is_running(false), rpm(0) {
    std::cout << "[Motor] 객체가 생성되었습니다." << std::endl;
}

Motor::~Motor() {
    stop();
    std::cout << "[Motor] 객체가 소멸되었습니다." << std::endl;
}

void Motor::start() {
    if (!is_running) {
        is_running = true;
        std::cout << "[Motor] 모터가 가동을 시작합니다." << std::endl;
    }
}

void Motor::stop() {
    if (is_running) {
        is_running = false;
        rpm = 0;
        std::cout << "[Motor] 모터가 정지했습니다." << std::endl;
    }
}

void Motor::setSpeed(int target_rpm) {
    if (is_running) {
        rpm = target_rpm;
        std::cout << "[Motor] 속도가 " << rpm << " RPM으로 설정되었습니다." << std::endl;
    } else {
        std::cout << "[Motor] 경고: 모터가 정지 상태입니다. 먼저 start()를 호출하세요." << std::endl;
    }
}

int Motor::getSpeed() const {
    return rpm;
}

bool Motor::getStatus() const {
    return is_running;
}

// 문제 4번 수정 빌드되는 어떤 파일만 재검파일되는지 확인용
int test(){
    std::cout<<"test // 집에가고싶다"<<std::endl;
    return 0;
}

