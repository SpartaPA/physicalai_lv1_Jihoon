#include <iostream>
#include "motor.hpp"
#include "sensors/sensor.hpp"
#include <memory>
#include <vector>
#include <unordered_map>
#include <algorithm>


template<typename T>
T clamp(T value, T min, T max){
    if(value<min) return min;
    if(value>max) return max;
    return value;
}

void memory_test()
{
    for (int i = 0; i < 1000; ++i)
    {
        auto data = std::make_unique<int[]>(100); 
        data[0] = i; 
        // 일부러 delete[] 하지 않음
    }
}

int main() {

     double speed = 1005.2;
    speed = clamp(speed, 0.0, 800.0);
    std::cout << "제한전 double: "
              << speed
              << std::endl;


    std::cout<<"더블 인트 clamp 적용"<<std::endl;
    std::cout << "제한된 double: "
           << speed
           << std::endl;

   int pixel = 300;

   pixel = clamp(pixel, 0, 255);

   std::cout << "제한된 int값: "
             << pixel
             << std::endl;


    memory_test();


//     std::unordered_map<std::string, double> last_measurement;

//     last_measurement["Lidar"] = 0.42;
//     last_measurement["Imu"] = 9.81;

    
//     std::cout << "=== 최근 측정값 ===" << std::endl;

//     std::cout << "Lidar: "
//               << last_measurement["Lidar"]
//               << std::endl;


//     std::cout << "Imu: "
//                 << last_measurement["Imu"]
//                 << std::endl;          
  

// std::vector<double> measurements = {0.42, 9.81, 1.23, 4.56,0.32,0.35,0.36,0.34};

//     std::cout << "\n=== 측정값 출력 ===" << std::endl;
//     for (const auto& measurement : measurements) {
//         std::cout << "측정값: " << measurement << std::endl;
//     }


// int count = std::count_if(measurements.begin(), measurements.end(),
//  [](double value) {
//         return value <= 0.35;
//  }); 


//     std::cout << "\n=== 측정값 개수 ===" << std::endl;
//     std::cout << "0.35 이내 측정값 개수: " << count << std::endl;




//std::cout << "=== 모터 제어 테스트 시작 ===" << std::endl;
    
//    Motor myMotor;
    
//    myMotor.start();
//     myMotor.setSpeed(1500);
    
//    std::cout << "\n현재 모터 속도: " << myMotor.getSpeed() << " RPM" << std::endl;
    
//     myMotor.stop();
    
//    std::cout << "\n=== 모터 제어 테스트 종료 ===\n" << std::endl;
    

//     std::vector<std::unique_ptr<sensor>> sensor;

//     sensor.push_back(std::make_unique<Lidar>());
//     sensor.push_back(std::make_unique<Imu>());

//     std::cout<<"\n------센서 루프 실행-----"<<std::endl;
//     for(const auto& s : sensor) {
//         s->read();
//     }

//     std::cout<<"\n------센서 루프 종료-----"<<std::endl;


//     std::cout<<"------테스트 시작-----"<<std::endl;
// {
//     std::cout<<"\n지역변수 생성"<<std::endl;
//     Lidar lidar;

//     std::cout<<"\n지역변수 생성완료"<<std::endl;
// }

// {
//     std::cout<<"\n make_unique 변수 생성"<<std::endl;
//     auto lidar = std::make_unique<Lidar>();

//     std::cout<<"\nmak_unique 생성완료"<<std::endl;
// }


    return 0;

}