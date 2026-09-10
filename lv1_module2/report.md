# lv2 module2

## 1. C++빌드 체계 세우기
### 1.  수동 2단계 빌드 명령 (터미널 입력)
```bash 
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ ls
CMakdelist.txt  main.cpp  motor.cpp  motor.o        stop_distance.cpp
CMakelist.txt   main.o    motor.hpp  stop_distance
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ g++ -Wall -std=c++17 -c motor.cpp -o motor.o
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ g++ -wall -std=c++17 -c main.cpp -o main.o
g++: error: unrecognized command-line option ‘-wall’; did you mean ‘-Wall’?
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ g++ -Wall -std=c++17 -c main.cpp -o main.o
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ g++ motor.o main.o -o main
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ ./main
=== 모터 제어 테스트 시작 ===
[Motor] 객체가 생성되었습니다.
[Motor] 모터가 가동을 시작합니다.
[Motor] 속도가 1500 RPM으로 설정되었습니다.
현재 모터 속도: 1500 RPM
[Motor] 모터가 정지했습니다.
=== 모터 제어 테스트 종료 ===
[Motor] 객체가 소멸되었습니다.
```

### 2. underfined reference 에러 재현
```bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics$ g++ main.o -o main
/usr/bin/ld: main.o: in function `main':
main.cpp:(.text+0x4f): undefined reference to `Motor::Motor()'
/usr/bin/ld: main.cpp:(.text+0x5b): undefined reference to `Motor::start()'
/usr/bin/ld: main.cpp:(.text+0x6c): undefined reference to `Motor::setSpeed(int)'
/usr/bin/ld: main.cpp:(.text+0x94): undefined reference to `Motor::getSpeed() const'
/usr/bin/ld: main.cpp:(.text+0xd1): undefined reference to `Motor::stop()'
/usr/bin/ld: main.cpp:(.text+0x10d): undefined reference to `Motor::~Motor()'
/usr/bin/ld: main.cpp:(.text+0x133): undefined reference to `Motor::~Motor()'
collect2: error: ld returned 1 exit status```

컴파일 에러 : C++규격위반, 구문 오류, 미선언 변수/타입사용 시 발생
링크 에러 : 헤더선언은 존재하여 형태는 알지만 실제 기계어 구현체(.o)가 누락됨 
```
### 3. cmake 빌드
```bash 
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ make
[ 33%] Building CXX object CMakeFiles/main.dir/main.cpp.o
[ 66%] Building CXX object CMakeFiles/main.dir/motor.cpp.o
[100%] Linking CXX executable main
[100%] Built target main
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ./main
=== 모터 제어 테스트 시작 ===
[Motor] 객체가 생성되었습니다.
[Motor] 모터가 가동을 시작합니다.
[Motor] 속도가 1500 RPM으로 설정되었습니다.
현재 모터 속도: 1500 RPM
[Motor] 모터가 정지했습니다.
=== 모터 제어 테스트 종료 ===
[Motor] 객체가 소멸되었습니다.
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ 
```

### 4. 증분 빌드
```bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ make
Consolidate compiler generated dependencies of target main
[ 33%] Building CXX object CMakeFiles/main.dir/motor.cpp.o
[ 66%] Linking CXX executable main
[100%] Built target main
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ 
```
증분 빌드 시 재컴파일된 파일: **motor.cpp**

**main.o**는 재컴파일되지 않고, 변경된 motor.cpp.o만 재컴파일된 후 최종 실행 파일 main으로 빌드됨

증분빌드란? - 소스 코드 전체를 다시 빌드하는것이 아닌 마지막 빌드 후 변경점이있는 파일과 그에 의존하는 타깃만 선택적 재컴파일/링크

따라서 motor.cpp가 수정되어 타임스탬프가 motor.cpp.o보다 최신상태가 되었으므로 해당 파일이 변경된것으로 판단 선택적 재컴파일
## 2. 현대 c++센서 계층 구혀

### 1. 다형성 루프
   ```bash
    22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ./main
=== 모터 제어 테스트 시작 ===
[Motor] 객체가 생성되었습니다.
[Motor] 모터가 가동을 시작합니다.
[Motor] 속도가 1500 RPM으로 설정되었습니다.

현재 모터 속도: 1500 RPM
[Motor] 모터가 정지했습니다.

=== 모터 제어 테스트 종료 ===


------센서 루프 실행-----
[Lidar] 거리 측정 중...
[Imu] 데이터 읽는중

------센서 루프 종료-----
[Lidar] 객체가 소멸되었습니다.
[Sensor] 기반 클래스 소멸자 호출
[Imu] 객체가 소멸되었습니다.
[Sensor] 기반 클래스 소멸자 호출
[Motor] 객체가 소멸되었습니다.
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$
 ```

### 2. 스택 객체와 힙 객체의 소멸 시점 — 관찰 로그와 설명
   - main() 함수 종료 시, sensors 벡터 내부의 힙(Heap) 객체들(Lidar, Imu)이 먼저 소멸한 뒤, 스택(Stack) 객체인 myMotor가 가장 마지막에 소멸합니다.
### 그냥 가상소멸자 제거
``` bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ./main

------센서 루프 실행-----
[Lidar] 거리 측정 중...
[Imu] 데이터 읽는중

------센서 루프 종료-----```

자식클래스(Lidar,Imu) 소멸자가 호출되지않음, 부모 클래스 소멸자만 호출됨
이 경우 자원 누수 또는 정의되지않은 동작 발생가능
```


### 3. 가상 소멸자를 제거_make_unique
```bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ./main
------테스트 시작-----

지역변수 생성

지역변수 생성완료

[Lidar] 객체가 소멸되었습니다.

[Sensor] 기반 클래스 소멸자 호출

 make_unique 변수 생성

mak_unique 생성완료

[Lidar] 객체가 소멸되었습니다.

[Sensor] 기반 클래스 소멸자 호출
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ 
```

지역변수 (스택객체)
- 변수가 선언된 스코프를 벗어난 시점에 컴파일러 스택 메모리를 회수하면서 소멸자 자동 호출 자식 -> 부모 순

make_unique (힙객체)
- Lidar는 힙영역에 할당되지만 이를 가리키는 unique 변수자체는 스택 영역에 존재 , 스코프 벗어날시 소멸자 내부에서 힙메모리에대한 delete를 수행하여 힙 객체를 안전하게 소멸

### 4. count_if 결과 
```bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ./main
=== 최근 측정값 ===
Lidar: 0.42
Imu: 9.81

=== 측정값 출력 ===
측정값: 0.42
측정값: 9.81
측정값: 1.23
측정값: 4.56
측정값: 0.32
측정값: 0.35
측정값: 0.36
측정값: 0.34

=== 측정값 개수 ===
0.35 이내 측정값 개수: 3
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ 

0.35 이내 기록 3개
```

### 5. 누수 검출결과

```bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ASAN_OPTIONS=detect_leaks=1 ./main
제한전 double: 800
더블 인트 clamp 적용
제한된 double: 800
제한된 int값: 255
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ cmake .. -DCMAKE_CXX_FLAGS="-fsanitize=address -g"
make
-- Configuring done
-- Generating done
-- Build files have been written to: /home/pa22/lv1_module2_jh/cpp_basics/build
Consolidate compiler generated dependencies of target main
[ 33%] Building CXX object CMakeFiles/main.dir/main.cpp.o
[ 66%] Building CXX object CMakeFiles/main.dir/motor.cpp.o
[100%] Linking CXX executable main
[100%] Built target main
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ASAN_OPTIONS=detect_leaks=1 ./main
제한전 double: 800
더블 인트 clamp 적용
제한된 double: 800
제한된 int값: 255

=================================================================
==31662==ERROR: LeakSanitizer: detected memory leaks

Direct leak of 400000 byte(s) in 1000 object(s) allocated from:
    #0 0x75c83b0b6357 in operator new[](unsigned long) ../../../../src/libsanitizer/asan/asan_new_delete.cpp:102
    #1 0x642be57bd367 in memory_leak_test() /home/pa22/lv1_module2_jh/cpp_basics/main.cpp:21
    #2 0x642be57bd503 in main /home/pa22/lv1_module2_jh/cpp_basics/main.cpp:52
    #3 0x75c83a829d8f in __libc_start_call_main ../sysdeps/nptl/libc_start_call_main.h:58

SUMMARY: AddressSanitizer: 400000 byte(s) leaked in 1000 allocation(s).
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ 
```

#### 수정 후 결과
```bash
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ cmake .. -DCMAKE_CXX_FLAGS="-fsanitize=address -g"
-- Configuring done
-- Generating done
-- Build files have been written to: /home/pa22/lv1_module2_jh/cpp_basics/build
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ make
Consolidate compiler generated dependencies of target main
[ 33%] Building CXX object CMakeFiles/main.dir/main.cpp.o
[ 66%] Linking CXX executable main
[100%] Built target main
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ ASAN_OPTIONS=detect_leaks=1 ./main
제한전 double: 800
더블 인트 clamp 적용
제한된 double: 800
제한된 int값: 255
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/cpp_basics/build$ 
```


# 문제.3 rclpy 노드 작성 — 거북이 상태 발행자와 구독자
### 1. /turtle1/pose 필드 구성: ___
1. /turtle1/pose 필드 구성: ___[turtle1] at x=[5.544445], y=[5.544445], theta=[0.000000]
![alt text](<스크린샷, 2026-09-04 16-47-16.png>)

#### 2.  ros2 topic hz /turtle_distance 출력: 평균 10 Hz

![alt text](distance_publishing.gif)

```
/turtle_py$ ros2 topic hz /turtle_distance
average rate: 9.999
	min: 0.100s max: 0.100s std dev: 0.00008s window: 11
average rate: 9.999
	min: 0.100s max: 0.100s std dev: 0.00009s window: 21
average rate: 10.000
	min: 0.100s max: 0.100s 
   ````

### 3. 구독자 경고 로그
```[WARN] [1788511858.178248845] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.278412433] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.378781946] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.478240669] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.578394507] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.678051730] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.778226364] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.878328923] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788511858.978229924] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값
```
### 4. 구독자 2개 동시 수신 확인 
![alt text](subscribe.gif)

### 5. 정사각형 주행캡쳐
1. 거북이 움직임
![ ](fucking_turtle.gif) 

### 6. Ctrl+C 정상 종료 화면 (출력)

1. publisher
```
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws/src/turtle_py$ ros2 run turtle_py distance_publisher
^Cpa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws/src/turtle_py$ 
```

2. subscriber

```
경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788747222.547248468] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788747222.646298175] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788747222.746457925] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788747222.850239224] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
[WARN] [1788747222.946635486] [turtle_distance_subscriber]: 경고: 원점 거리 7.84 m > 임계값 2.50 m
^Cpa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws/src/turtle_py$ 

```
3. image
![alt text](컨트롤.png)

### 4.  rclcpp 노드 작성 — C++ 발행자와 구독자

#### 1. colcon build 성공 출력
```
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws$ source /opt/ros/humble/setup.bash
colcon build --packages-select turtle_cpp
Starting >>> turtle_cpp
Finished <<< turtle_cpp [0.17s]

Summary: 1 package finished [0.55s]
```

#### 2. rclpy 발행에서 rclcpp 구독으로 이어진 로그

Python `rclpy` 발행자에서 `/turtle_distance` 토픽을 발행하고,
C++ `rclcpp` 구독자에서 동일한 토픽의 `Float32` 메시지를 수신하였다.

Python 발행자 실행:

```bash
ros2 run turtle_py distance_publisher
```
```
ros2 run turtle_cpp distance_subscriber
```


### 2. rclpy와 rclcpp 대응 관계

![alt text](rosgraph-1.png)


| 항목    | rclpy (Python)                                                                    | rclcpp (C++)                                                                                        |
| ----- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| 노드 생성 | `class DistancePublisher(Node)` / `super().__init__('turtle_distance_publisher')` | `class DistanceSubscriber : public rclcpp::Node` / `DistanceSubscriber() : Node("Distance_scribe")` |
| 타이머   | `self.create_timer(0.1, self.timer_callback)`                                     | `create_wall_timer()`                                                                               |
| 콜백    | `def pose_callback(self, msg)`, `def timer_callback(self)`                        | `void topic_callback(const std_msgs::msg::Float32::SharedPtr msg)`                                  |
| 종료    | `rclpy.spin(node)` → `node.destroy_node()` → `rclpy.shutdown()`                   | `rclcpp::spin(...)` → `rclcpp::shutdown()`                                                          |

Python의 `rclpy`와 C++의 `rclcpp`는 문법과 함수 이름은 다르지만, 노드를 생성하고 콜백을 실행한 뒤 `spin()`으로 노드를 동작시키고 종료 시 ROS 2를 정리하는 기본 구조는 동일하다.


### 10. 시각화·기록·테스트로 검증하기

#### 1. rqt_graph 캡처 — 데이터 미수신 진단 절차 (단계별)

![alt text](../../../lv1_module2_jh/ros2_ws/src/turtle_py/finished_turtlesim.png)

진단절차
1. ros2 node list
2. ros2 topic list
3.
```
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws/src/turtle_py$ ros2 node list
/Distance_scribe
/rqt_gui_py_node_34159
/turtle_distance_publisher
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws/src/turtle_py$ ros2 topic list
/parameter_events
/rosout
/turtle1/pose
/turtle_distance
pa22@pa22-Legion-Pro-5-16IAX10:~/lv1_module2_jh/ros2_ws/src/turtle_py$ ros2 topic echo /turtle_distance
data: 7.841028690338135
---
data: 7.841028690338135
---
data: 7.841028690338135
---
data: 7.841028690338135
---
data: 7.841028690338135
---
data: 7.841028690338135
---
```

결과 
```
rc/turtle_pyros2 topic hz /turtle_distancece
average rate: 10.001
	min: 0.100s max: 0.100s std dev: 0.00004s window: 12
average rate: 10.000
	min: 0.100s max: 0.100s std dev: 0.00006s window: 22
average rate: 10.000
	min: 0.100s max: 0.100s std dev: 0.00006s window: 33

```

![alt text](rosgraph.png)

**결론** : turtlesim 종료되어도 기존 발행되었돈 위치는 distance_publisher가 계속 발행


/// 이후로 진행불가 막힘
