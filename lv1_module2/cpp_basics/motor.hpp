#ifndef MOTOR_HPP
#define MOTOR_HPP

class Motor {
public:
    Motor();
    ~Motor();

    void start();
    void stop();
    void setSpeed(int target_rpm);
    int getSpeed() const;
    bool getStatus() const;

private:
    bool is_running;
    int rpm;
};

#endif
