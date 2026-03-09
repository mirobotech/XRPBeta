"""
XRPBeta.py
March 9, 2026

Board support module for the XRP (Experiential Robotics Platform) Beta.

This module configures Raspberry Pi Pico W's GPIO pins for XRPBeta's
on-board circuits and provides simple helper functions to enable
beginners to focus on learning programming concepts first.

Before getting started with it you should know:
- nothing here is hidden, or * magic *, or requires special libraries
- the functions are just normal Python code to help you start learning
- you're encouraged to modify the code to make it work better for you!

XRPBeta hardware notes:
- The USER button uses an internal pull-up resistor (so pressed == 0)
- Motors use phase/enable control:
    - Phase pin sets direction (1 = forward, 0 = reverse)
    - Enable pin sets speed using PWM (0-65535, where 65535 = full speed)
- Motor encoders count shaft rotations for precise distance/speed control
- The IMU (inertial measurement unit) is on I2C address 0x6B
"""

import machine
from machine import Pin, ADC, PWM, I2C
import time

# ---------------------------------------------------------------------
# Raspberry Pi Pico W Module LED
# ---------------------------------------------------------------------

PICO_LED = Pin("LED", Pin.OUT)

def pico_led_on():
    # Turn the Raspberry Pi Pico W on-board LED on.
    PICO_LED.value(1)

def pico_led_off():
    # Turn the Raspberry Pi Pico W on-board LED off.
    PICO_LED.value(0)

def pico_led_toggle():
    # Toggle the Raspberry Pi Pico W on-board LED.
    PICO_LED.value(not PICO_LED.value())


# ---------------------------------------------------------------------
# XRPBeta Pushbutton Switch
# ---------------------------------------------------------------------

# User pushbutton uses an internal pull-up resistor (active LOW)

USER_BTN_PIN = const(22)  # USER button
# Note: const() stores fixed values in ROM to save RAM

USER_BTN = Pin(USER_BTN_PIN, Pin.IN, Pin.PULL_UP)

def button_pressed():
    # Returns True if the user button is currently pressed.
    return USER_BTN.value() == 0


# ---------------------------------------------------------------------
# XRPBeta Motor Controller
# ---------------------------------------------------------------------

# XRPBeta uses DRV8835 motor driver ICs with phase/enable control.
#   - Phase pin: sets direction (1 = forward, 0 = reverse)
#   - Enable pin: sets speed via PWM duty cycle (0 = stop, 65535 = full speed)
#
# Two primary drive motors (left and right) plus two auxiliary motors
# (motor 3 and motor 4) are supported.

# Left motor
MOT_L_PH_PIN = const(6)   # Left motor phase (direction)
MOT_L_EN_PIN = const(7)   # Left motor enable (speed, PWM)

# Right motor
MOT_R_PH_PIN = const(14)  # Right motor phase (direction)
MOT_R_EN_PIN = const(15)  # Right motor enable (speed, PWM)

# Auxiliary motor 3
MOT_3_PH_PIN = const(2)   # Motor 3 phase (direction)
MOT_3_EN_PIN = const(3)   # Motor 3 enable (speed, PWM)

# Auxiliary motor 4
MOT_4_PH_PIN = const(10)  # Motor 4 phase (direction)
MOT_4_EN_PIN = const(11)  # Motor 4 enable (speed, PWM)

MOT_L_PH = Pin(MOT_L_PH_PIN, Pin.OUT)
MOT_L_EN = PWM(Pin(MOT_L_EN_PIN))

MOT_R_PH = Pin(MOT_R_PH_PIN, Pin.OUT)
MOT_R_EN = PWM(Pin(MOT_R_EN_PIN))

MOT_3_PH = Pin(MOT_3_PH_PIN, Pin.OUT)
MOT_3_EN = PWM(Pin(MOT_3_EN_PIN))

MOT_4_PH = Pin(MOT_4_PH_PIN, Pin.OUT)
MOT_4_EN = PWM(Pin(MOT_4_EN_PIN))


def set_motor(phase_pin, enable_pwm, speed):
    # Set a motor's direction and speed.
    # speed: -100 to +100 (negative = reverse, 0 = stop, positive = forward)
    # Pass motor phase pin and enable PWM object as the first two arguments:
    #   set_motor(MOT_L_PH, MOT_L_EN, 75)   # left motor forward at 75%
    #   set_motor(MOT_R_PH, MOT_R_EN, -50)  # right motor reverse at 50%
    speed = max(-100, min(100, speed))  # Clamp to -100..+100
    if speed >= 0:
        phase_pin.value(1)              # Forward
    else:
        phase_pin.value(0)              # Reverse
        speed = -speed                  # Make positive for duty calculation
    enable_pwm.duty_u16(int(speed / 100 * 65535))


def left_motor(speed):
    # Set left motor speed: -100 (full reverse) to +100 (full forward), 0 = stop.
    set_motor(MOT_L_PH, MOT_L_EN, speed)

def right_motor(speed):
    # Set right motor speed: -100 (full reverse) to +100 (full forward), 0 = stop.
    set_motor(MOT_R_PH, MOT_R_EN, -speed)

def motor3(speed):
    # Set auxiliary motor 3 speed: -100 to +100, 0 = stop.
    set_motor(MOT_3_PH, MOT_3_EN, speed)

def motor4(speed):
    # Set auxiliary motor 4 speed: -100 to +100, 0 = stop.
    set_motor(MOT_4_PH, MOT_4_EN, speed)

def drive(speed, turn=0):
    # Drive both motors together with optional turning.
    # speed: -100 to +100 (negative = reverse)
    # turn:  -100 to +100 (negative = turn left, positive = turn right)
    # Examples:
    #   drive(50)        # Forward at 50% speed, straight
    #   drive(50, 25)    # Forward at 50%, turning right
    #   drive(-50)       # Reverse at 50% speed
    left_speed  = max(-100, min(100, speed - turn))
    right_speed = max(-100, min(100, speed + turn))
    left_motor(left_speed)
    right_motor(right_speed)

def motors_stop():
    # Stops all four motors (left, right, motor3, motor4).
    left_motor(0)
    right_motor(0)
    motor3(0)
    motor4(0)


# ---------------------------------------------------------------------
# XRPBeta Motor Encoders
# ---------------------------------------------------------------------

# Each drive motor has a quadrature encoder with A and B signal pins.
# Encoders count shaft pulses to measure distance and speed.
# Use the encoder count to drive precise distances or at controlled speeds.
#
# NOTE: This is a basic software encoder counter. For higher-speed
# applications consider using Pico's PIO state machines instead.

ENC_L_A_PIN = const(4)   # Left encoder channel A
ENC_L_B_PIN = const(5)   # Left encoder channel B
ENC_R_A_PIN = const(12)  # Right encoder channel A
ENC_R_B_PIN = const(13)  # Right encoder channel B
ENC_3_A_PIN = const(0)   # Motor 3 encoder channel A
ENC_3_B_PIN = const(1)   # Motor 3 encoder channel B
ENC_4_A_PIN = const(8)   # Motor 4 encoder channel A
ENC_4_B_PIN = const(9)   # Motor 4 encoder channel B

ENC_L_A = Pin(ENC_L_A_PIN, Pin.IN)
ENC_L_B = Pin(ENC_L_B_PIN, Pin.IN)
ENC_R_A = Pin(ENC_R_A_PIN, Pin.IN)
ENC_R_B = Pin(ENC_R_B_PIN, Pin.IN)
ENC_3_A = Pin(ENC_3_A_PIN, Pin.IN)
ENC_3_B = Pin(ENC_3_B_PIN, Pin.IN)
ENC_4_A = Pin(ENC_4_A_PIN, Pin.IN)
ENC_4_B = Pin(ENC_4_B_PIN, Pin.IN)

# Encoder counts (updated by interrupts)
_enc_counts = [0, 0, 0, 0]  # [left, right, motor3, motor4]

def _make_enc_handler(index, b_pin):
    # Returns an interrupt handler that increments or decrements the
    # encoder count for motor [index] based on the B channel state.
    def handler(pin):
        if pin.value() == b_pin.value():
            _enc_counts[index] -= 1
        else:
            _enc_counts[index] += 1
    return handler

# Attach rising-edge interrupts on each encoder's A channel
ENC_L_A.irq(trigger=Pin.IRQ_RISING, handler=_make_enc_handler(0, ENC_L_B))
ENC_R_A.irq(trigger=Pin.IRQ_RISING, handler=_make_enc_handler(1, ENC_R_B))
ENC_3_A.irq(trigger=Pin.IRQ_RISING, handler=_make_enc_handler(2, ENC_3_B))
ENC_4_A.irq(trigger=Pin.IRQ_RISING, handler=_make_enc_handler(3, ENC_4_B))

def left_encoder():
    # Return the current left motor encoder count.
    return _enc_counts[0]

def right_encoder():
    # Return the current right motor encoder count.
    return _enc_counts[1]

def encoder3():
    # Return the current motor 3 encoder count.
    return _enc_counts[2]

def encoder4():
    # Return the current motor 4 encoder count.
    return _enc_counts[3]

def reset_encoders():
    # Reset all encoder counts to zero.
    for i in range(4):
        _enc_counts[i] = 0


# ---------------------------------------------------------------------
# XRPBeta Servos
# ---------------------------------------------------------------------

# Servo pulse width constants (microseconds). Adjust for your servo.
# Standard 90-degree servo: 1000us to 2000us (centre at 45 degrees)
# XRPBeta 180-degree servo: 500us to 2500us (centre at 90 degrees)
SERVO_MIN_US = const(500)   # Pulse width at 0 degrees
SERVO_MAX_US = const(2500)  # Pulse width at maximum angle
SERVO_RANGE  = const(180)   # Maximum servo angle (degrees)

# Servos are initialized to centre position (duty_u16=4915 ≈ 1.5ms).
# Modify the duty_u16 value if the centre position is not safe for
# your application before connecting servos to the circuit.
S1_PIN = const(16)
S2_PIN = const(17)

SERVO1 = PWM(Pin(S1_PIN), freq=50, duty_u16=4915)
SERVO2 = PWM(Pin(S2_PIN), freq=50, duty_u16=4915)

SERVOS = (SERVO1, SERVO2)  # Tuple of all servo PWM outputs

def set_servo(servo, angle):
    # Set a servo to angle (0 to SERVO_RANGE degrees).
    # Pass the servo object as the first argument: set_servo(SERVO1, 45)
    angle = max(0, min(SERVO_RANGE, angle))
    pulse_us = SERVO_MIN_US + int(angle / SERVO_RANGE * (SERVO_MAX_US - SERVO_MIN_US))
    servo.duty_ns(pulse_us * 1000)
    return angle


# ---------------------------------------------------------------------
# XRPBeta Analog Inputs
# ---------------------------------------------------------------------

LINE_L_PIN  = const(26)  # Left line sensor phototransistor
LINE_R_PIN  = const(27)  # Right line sensor phototransistor
VIN_MEAS_PIN = const(28) # Battery monitor voltage divider

LINE_L  = ADC(Pin(LINE_L_PIN))
LINE_R  = ADC(Pin(LINE_R_PIN))
VIN_ADC = ADC(Pin(VIN_MEAS_PIN))

def line_left():
    # Read left line sensor. Higher values indicate a lighter (more reflective) surface.
    return 65535 - LINE_L.read_u16()

def line_right():
    # Read right line sensor. Higher values indicate a lighter (more reflective) surface.
    return 65535 - LINE_R.read_u16()

def battery_voltage():
    # Read battery voltage in volts.
    # VIN_MEAS uses a resistor divider on the XRPBeta. To calibrate
    # the voltage, measure Vin with a multimeter and adjust the final
    # multiplier until battery_voltage() matches the measured value.
    return VIN_ADC.read_u16() * 3.3 / 65535 * 4  # 4x multiplier

# RP2xxxx die temperature sensor
MCU_TEMP = ADC(ADC.CORE_TEMP)

def mcu_temperature():
    # Read MCU die temperature in degrees C. From the Raspberry Pi Pico datasheet:
    # The temperature sensor measures the Vbe voltage of a biased bipolar
    # diode, connected to the fifth ADC channel. Typically, Vbe = 0.706V
    # at 27 degrees C, with a slope of -1.721mV (0.001721) per degree.
    mcu_temp_volts = MCU_TEMP.read_u16() * 3.3 / 65535
    return 27 - (mcu_temp_volts - 0.706) / 0.001721


# ---------------------------------------------------------------------
# XRPBeta SONAR Distance Sensor
# ---------------------------------------------------------------------

RANGE_TRIG_PIN = const(20)  # SONAR trigger output
RANGE_ECHO_PIN = const(21)  # SONAR echo input

SONAR_TRIG = Pin(RANGE_TRIG_PIN, Pin.OUT, value=0)
SONAR_ECHO = Pin(RANGE_ECHO_PIN, Pin.IN)

def sonar_range(max=300):
    # Returns either:
    #  distance (cm) - target detected within max range
    #  0             - no target within max range
    #  -1            - time-out waiting for ECHO to end
    #  -2            - time-out waiting for ECHO to start
    #  -3            - previous ECHO still in progress

    if SONAR_ECHO.value() == 1:
        # Check if previous ECHO is in progress, return error if so
        return -3   # (wait 10ms after ECHO ends before re-triggering)

    # Create a TRIG pulse
    SONAR_TRIG.value(1)
    time.sleep_us(10)
    SONAR_TRIG.value(0)

    # Wait 2500us for ECHO pulse to start. Note: HC-SR04P (3.3V-capable
    # modules also labelled as RCWL-9610A 2022) delay for approximately
    # 2300us after the TRIG pulse ends and the ECHO pulse starts.
    duration = machine.time_pulse_us(SONAR_ECHO, 0, 2500)

    if duration < 0:
        # ECHO didn't start - return time_pulse_us() error (-2, -1)
        return duration

    # Time ECHO pulse. Set time-out value to max range.
    duration = machine.time_pulse_us(SONAR_ECHO, 1, (max + 1) * 58)
    if duration < 0:
        return 0    # Distance > max range

    # Calculate target distance in cm
    return duration / 58


# ---------------------------------------------------------------------
# QWIIC/I2C Connector (supports 3.3V I2C devices)
# ---------------------------------------------------------------------

I2C_ID = 1
SDA = Pin(18)
SCL = Pin(19)
QWIIC = I2C(id=I2C_ID, sda=SDA, scl=SCL)


# ---------------------------------------------------------------------
# XRPBeta IMU - LSM6DSO 6-DoF Inertial Measurement Unit
# ---------------------------------------------------------------------

# The LSM6DSO provides 3-axis accelerometer and 3-axis gyroscope data.
# It is connected to the I2C bus at address 0x6B.

IMU_ADDR = const(0x6B)  # LSM6DSO I2C address

# LSM6DSO register addresses (from datasheet)
_WHO_AM_I  = const(0x0F)  # Device ID register - should return 0x6C
_CTRL1_XL  = const(0x10)  # Accelerometer control register
_CTRL2_G   = const(0x11)  # Gyroscope control register
_CTRL3_C   = const(0x12)  # Control register 3 (IF_INC and reboot)
_STATUS    = const(0x1E)  # Status register
_OUTX_L_G  = const(0x22)  # Gyroscope X output low byte (first of 6 bytes)
_OUTX_L_XL = const(0x28)  # Accelerometer X output low byte (first of 6 bytes)


def _imu_write(reg, value):
    # Write a single byte to an IMU register.
    QWIIC.writeto_mem(IMU_ADDR, reg, bytes([value]))

def _imu_read(reg, length):
    # Read length bytes starting from an IMU register.
    return QWIIC.readfrom_mem(IMU_ADDR, reg, length)

def _imu_signed16(high, low):
    # Combine two bytes into a signed 16-bit integer.
    value = (high << 8) | low
    if value >= 32768:
        value -= 65536
    return value


def imu_whoami():
    # Read and return the device ID register.
    # LSM6DSO should return 0x6C. Useful for verifying the IMU is
    # connected and responding correctly.
    return hex(_imu_read(_WHO_AM_I, 1)[0])


def imu_init():
    # Initialize the LSM6DSO IMU.
    #
    # CTRL3_C = 0x04: Set IF_INC bit to enable automatic register address
    # incrementing during multi-byte reads. Required for the 6-byte burst
    # reads used in imu_acceleration() and imu_gyroscope().
    _imu_write(_CTRL3_C, 0x04)
    #
    # CTRL1_XL = 0x40: Accelerometer on at 104Hz, ±2g range.
    # Bits 7:4 = 0100 = 104Hz output data rate
    # Bits 3:2 = 00   = ±2g full-scale range
    # Bits 1:0 = 00   = default anti-aliasing filter
    _imu_write(_CTRL1_XL, 0x40)
    #
    # CTRL2_G = 0x40: Gyroscope on at 104Hz, ±250 dps range.
    # Bits 7:4 = 0100 = 104Hz output data rate
    # Bits 3:1 = 000  = ±250 dps full-scale range
    _imu_write(_CTRL2_G, 0x40)


def imu_acceleration():
    # Read accelerometer and return (x, y, z) in units of g.
    # LSM6DSO at ±2g range: sensitivity = 0.000061 g/LSB
    # At rest, the axis pointing up should read approximately +1.0g.
    data = _imu_read(_OUTX_L_XL, 6)
    x = _imu_signed16(data[1], data[0]) * 0.000061
    y = _imu_signed16(data[3], data[2]) * 0.000061
    z = _imu_signed16(data[5], data[4]) * 0.000061
    return (x, y, z)


def imu_gyroscope():
    # Read gyroscope and return (x, y, z) rotation rates in degrees per second.
    # LSM6DSO at ±250 dps range: sensitivity = 0.00875 dps/LSB
    # At rest all axes should read approximately 0 dps.
    data = _imu_read(_OUTX_L_G, 6)
    x = _imu_signed16(data[1], data[0]) * 0.00875
    y = _imu_signed16(data[3], data[2]) * 0.00875
    z = _imu_signed16(data[5], data[4]) * 0.00875
    return (x, y, z)


def imu_ready():
    # Returns True if new IMU data is available to read.
    # Bit 0 of STATUS = accelerometer data ready
    # Bit 1 of STATUS = gyroscope data ready
    status = _imu_read(_STATUS, 1)[0]
    return bool(status & 0x03)


# Initialize the IMU (QWIIC bus must be set up before calling this)
imu_init()
