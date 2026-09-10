#ifndef SENSOR_HPP
#define SENSOR_HPP

#include <iostream>

class sensor {
private:
    bool is_active;
    int value;

public:
    sensor() = default;                    // 생성자 (초기화)

    virtual ~sensor() {
        std::cout << "\n[Sensor] 기반 클래스 소멸자 호출" << std::endl;
    }

    void activate();             // 센서 활성화 함수
    void deactivate();           // 센서 비활성화 함수
    void setValue(int v);        // 센서 값 설정 함수
    int getValue() const;        // 센서 값 가져오기 함수
    bool getStatus() const;      // 센서 상태 가져오기 함수
    virtual void read() const = 0;    

};

class Lidar : public sensor {

    public:
    ~Lidar() {
        std::cout << "\n[Lidar] 객체가 소멸되었습니다." << std::endl;
    }
    void read() const override {
        std::cout << "\n[Lidar] 거리 측정 중..." << std::endl;
    }

};



class Imu : public sensor {
    public:
    ~Imu() {
        std::cout << "\n[Imu] 객체가 소멸되었습니다." << std::endl;
    }

    void read() const override{
        std::cout<<"\n[Imu] 데이터 읽는중"<<std::endl;

    }
};

#endif
