# 과제 1. 배달 로봇의 연산 분담과 실시간성 설계

## 연산분담 배치표
### 배달 로봇에 다음이 실려 있다고 가정합니다 — 2D 라이다(10Hz), RGB 카메라(30fps·1080p), IMU(200Hz), 바퀴 엔코더(1kHz), 모터 드라이버, LTE 모듈.
### 1. 이 로봇이 하는 작업 여섯 가지(모터 속도 제어, 장애물 감지, 보행자 인식, 지도 기반 경로 계획, 배달 완료 사진 업로드, 운행 로그 집계)를 임베디드 / Edge AI / 클라우드 중 어디서 처리할지 표로 배치하고, 지연 예산과 데이터 전송량을 근거로 각각 이유를 쓰세요(1강).

| 작업 | 위치 | 지연예산| 데이터량 | 근거 |
| :---: | :---: | :---: | :---: | :---: |
| 모터속도 제어 | 임베디드 | 1khz(1ms) | 16kb/s | 4륜 x 4B 카운터<br> 실시간 제어가 필수, 지연없이 저전력/고속 연이 필요
| 장애물 감지| Edge AI | 10Hz(100 ms)  | 약 28 kB/s | 360 x 8 Bytes x 10/s = 28,800 Byte/s<br> 2d 라이다데이터 즉시 처리 속도 확보 필요
| 보행자 인식 | Edge AI | 30fps(33ms) | 1.49 Gbps | 1920 x 1080 x 3 Bytes = 6,220,800,  6.22Mb x30 fps x 8 bits = 1.49 Gbps <br> 고용량 rgb 카메라 인지 결과만 판단 계층으로 전달
| 지도 기반 경로 계획 | 클라우드 | 1s ~ 5s | 최대 50 Mbps | cat4 (위치 및 환경에따라 다름)
|배달 완료 사진 업로드| 클라우드 | - | 수 mb | 비동기 전송, 서버로 안전하게 저장되면 됨 |
|운행 로그 집계 |클라우드 | _ | 수 kb | 모니터링 및 분석용 |

### 2. 카메라 원시 영상을 클라우드로 계속 보내면 초당 몇 MB 인지 계산하고, LTE 대역폭과 비교해 그 설계가 왜 성립하지 않는지 수치로 보이세요.
####  원시영상 초당 데이터 전송량 : 1920 x 1080 x 3 Bytes = 6,220,800,  6.22Mb x30 fps x 8 bits = 1.49 Gbp
#### 해당 크기는 LTE 대역폭을 초과하므로 불가능

### 3. 같은 작업들을 인지 → 판단 → 제어 계층에 매핑하고, 계층별 갱신 주기를 적어 멀티레이트 데이터 흐름을 그림이나 표로 정리하세요(2강).
| 계층 | 작업항목 | 갱신주기 |
| :---: | :---: | :---:|
|인지| 보행자 인식, 장애물 감지 | 30fps ~ / 10Hz|
| 판단 | 지도기반 경로 계획, 운행로그, 배달완료 사진 업로드  | 02,~1Hz|
| 제어 | 모터속도 제어 | 1kHz|
- Hard 초과 시 : 급정지 또는 급발진 발생




### 4.여섯 작업을 Hard / Firm / Soft 실시간으로 분류하고, Hard 로 분류한 작업이 마감을 놓치면 어떤 물리적 결과가 생기는지 한 줄씩 쓰세요.
| Hard | Firm | soft |
| :---: | :---: | :---:|
|모터속도제어| 보행자 인식, 장애물 감지 | 배달 완료 사진 업로드, 지도 기반 경로 계획, 운행 로그 집계|
- Hard 초과 시 : 급정지 또는 급발진 발생


### 5. 주기 지연 지터 구분
- 주기 : 바퀴의 회전 측정 간격, 라이다가 전방 장애물 인지위한 스캔 간격
- 지연 : 장애물 인식 후 정지 하는 시간
- 지터 : 빛반사, 신호 불량으로 스캔결과 불량 또는 늦게 도착

<br>
<br>

  
# 과제 2. 원격 접속(SSH)과 센서 장치 경로 고정
#### 1. 고른 접속 대상 : localhost // pa22@localhost
#### 2. 서버에 등록되는 것은 **공개키(id_ed25519.pub)**이고, 개인키(id_ed25519)는 클라이언트에만 보관한다. 공개키로는 인증에 필요한 비밀정보를 직접 복원할 수 없기 때문에 개인키를 공개하지 않는 한 안전하게 분리할 수 있습니다
#### 3. who 출력값
   
```bash
     pa22     pts/4        2026-08-27 12:05 (127.0.0.1)
     pa22@pa22-Legion-Pro-5-16IAX10:~$ echo $SSH_CONNECTION
     127.0.0.1 49580 127.0.0.1 22 
  ```

#### 4. 원격 단일 명령 실행과 scp 전송 출력
 
 ```
 pa22@pa22-Legion-Pro-5-16IAX10:~$ ssh pa22@localhost 'uname -a'

Linux pa22-Legion-Pro-5-16IAX10 6.8.0-138-generic #138~22.04.1-Ubuntu SMP PREEMPT_DYNAMIC Fri Aug  7 13:43:15 UTC  x86_64 x86_64 x86_64 GNU/Linux

pa22@pa22-Legion-Pro-5-16IAX10:~$ echo "ssH test"> ssH_test.txt 

pa22@pa22-Legion-Pro-5-16IAX10:~$ scp ssH_test.txt pa22@localhost:/tmp/

ssH_test.txt                                                        100%    9    14.0KB/s   00:00    

pa22@pa22-Legion-Pro-5-16IAX10:~$ ssh pa22@localhost 'cat /tmp/ssH_test.txt'

ssH test
 ```

### 4. 두장치를 구분한 속성 : 
##### 라이다
	/sys/block/loopN/loop/backing_file → /home/pa22/fake_sensors/lidar.img
#### IMU
	/sys/block/loopN/loop/backing_file → /home/pa22/fake_sensors/imu.img

### 5. 작성한 규칙<br>
SUBSYSTEM=="block", KERNEL=="loop5", SYMLINK+="robot_lidar", MODE="0660", GROUP="disk"

SUBSYSTEM=="block", KERNEL=="loop18", SYMLINK+="robot_imu", MODE="0660", GROUP="disk"<br>
subsytem 검사           커널 검사           심볼릭 링크 생성          장치파일 권한 설정   장치파일 소유 그룹

#### 6. 순서를 바꿔 재연결 한뒤
#### 이전
```
pa22@pa22-Legion-Pro-5-16IAX10:~/fake_sensors$ ls -l /dev/robot_*
lrwxrwxrwx 1 root root 6 Aug 27 16:18 /dev/robot_imu -> loop18
lrwxrwxrwx 1 root root 5 Aug 27 16:18 /dev/robot_lidar -> loop5
```

#### 결과

```pa22@pa22-Legion-Pro-5-16IAX10:~/fake_sensors$ ls -l /dev/robot*
lrwxrwxrwx 1 root root 6 Aug 27 16:48 /dev/robot_imu -> loop19
lrwxrwxrwx 1 root root 6 Aug 27 16:48 /dev/robot_lidar -> loop20
pa22@pa22-Legion-Pro-5-16IAX10:~/fake_sensors$ 
```

#### 7. 실제 USB 센서용 규칙 초안과 구분 근거
**idVendor**는 두센서 모두 **0403**으로 동일하므로 단독으로 사용할수없다. **idProduct**가 **LiDAR6001**, **IMU**가 **6015**로 서로 다르므로 함께 매칭하여 센서를 구분한다
> 실제 장치에서 두값까지 동일한 경우에는 USB serial number등의 추가적인 식별 속성을 사용해야한다.<br>
>  udev의 USB식별과정에서도 시리얼, product ID 등 이러한 정보가 장치 식별에 사용될수있다.
<br>

|센서|	idVendor|	idProduct|
|:---|:---|:---|
|LiDAR|	0403	|6001|
|IMU|	0403	|6015|


따라서 USB 시리얼 장치가 tty 서브시스템을 사용하는 경우 다음과 같이 규칙을 작성할 수 있다.

# USB Serial LiDAR
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", SYMLINK+="robot_lidar", MODE="0660", GROUP="dialout"

# USB Serial IMU
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6015", SYMLINK+="robot_imu", MODE="0660", GROUP="dialout"


# 과제 3. 팀 저장소 협업 -브랜치/충돌 해결 / PR리뷰

1. 저장소 URL : https://github.com/polarnight1212/physical-ai-project.git
2. 