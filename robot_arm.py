import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685

class Servo:
    SERVO_MIN_DUTY = 2.5    # % duty at 0°
    SERVO_MAX_DUTY = 12.5   # % duty at 180°

    def __init__(self, pwm, channel, angle_min=0, angle_max=180):
        self.pwm = pwm
        self.channel = channel
        self.ANGLE_MIN = angle_min
        self.ANGLE_MAX = angle_max

    def angle_to_pwm(self, angle):
        # Clamp to safe range
        angle = max(self.ANGLE_MIN, min(self.ANGLE_MAX, angle))

        duty_cycle = (float(angle) / 180.0) \
                     * (self.SERVO_MAX_DUTY - self.SERVO_MIN_DUTY) \
                     + self.SERVO_MIN_DUTY

        # Convert % duty cycle → 16-bit range
        pwm_value = int(65535 * duty_cycle / 100)
        return pwm_value

    def move(self, angle, delay=0.5):
        pwm_value = self.angle_to_pwm(angle)
        self.pwm.channels[self.channel].duty_cycle = pwm_value
        print(f"Servo {self.channel} → {angle}° (PWM={pwm_value})")
        time.sleep(delay)

class RobotArm:
    def __init__(self, pwm):
        # Define servos with their safe ranges
        self.servos = {
            0: Servo(pwm, 0, 140, 180),  # gripper
            1: Servo(pwm, 1, 0, 180),
            2: Servo(pwm, 2, 0, 180),
            # 3 is unused
            4: Servo(pwm, 4, 0, 180),
            5: Servo(pwm, 5, 0, 180),
        }

    def move_servo(self, index, angle, delay=0.5):
        if index in self.servos:
            self.servos[index].move(angle, delay)
        else:
            print(f"Servo {index} not available")

    def open_gripper(self):
        self.move_servo(0, 140)  # safe open

    def close_gripper(self):
        self.move_servo(0, 180)  # safe close

if __name__ == "__main__":
    i2c = busio.I2C(SCL, SDA)
    pwm = PCA9685(i2c)
    pwm.frequency = 50

    arm = RobotArm(pwm)

    # Test movements
    # Or initial state 
    arm.move_servo(5, 90)   # move servo 5
    arm.move_servo(4, 135)  # move servo 4
    arm.move_servo(2, 45)   # move servo 2
    arm.move_servo(1, 90)   # move servo 1 to mid

    arm.open_gripper()
    time.sleep(2)
    arm.close_gripper()
    time.sleep(2)

    # Routine number 1: Smooth rotation in particular degrees steps
    print("Routine: Pick up one object")

    arm.move_servo(0, 140)

    for angle in range(135, 171, 2):
        arm.move_servo(4, angle, delay=0.05)

    arm.move_servo(0, 176) #Close gripper to the range of 1cm between the 2 teeth

    for angle in range(170, 134, -5):
        arm.move_servo(4, angle, delay=0.1)
    
    for angle in range(90, 181, 1):
        arm.move_servo(5, angle, delay=0.1)
    
    for angle in range(135, 171, 5):
        arm.move_servo(4, angle, delay=0.1)

    arm.move_servo(0, 160) #Gripper half open 

    for angle in range(170, 134, -5):
        arm.move_servo(4, angle, delay=0.1)

    for angle in range(180, 89, -1):
        arm.move_servo(5, angle, delay=0.1)

    arm.move_servo(0, 180)

    print("The robot has completed the journey!")

    