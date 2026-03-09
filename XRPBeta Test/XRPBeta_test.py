"""
XRPBeta_test.py
March 9, 2026

Hardware test program for the XRPBeta robot circuit.

This program tests each piece of XRPBeta hardware in sequence.
Press the USER button to advance through each test stage.

Test sequence:
  Startup       - print welcome message and battery voltage, blink LED
                  while waiting for the user to begin
  Stage 1       - Left/right drive motors: turn, forward, reverse
  Stage 2       - Auxiliary motors 3 and 4: forward and reverse
  Stage 3       - Servos: sweep SERVO1 and SERVO2 through their range
  Stage 4       - Line sensors: print values until button press
  Stage 5       - SONAR: print distance readings until button press
  Stage 6       - IMU: print accelerometer and gyroscope values until button press
  (then repeats from Stage 1)
"""

from XRPBeta import *   # Import all XRPBeta board functions and objects
import time

# ---------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------

def wait_for_button():
    # Wait until the USER button is pressed and then released.
    # A short debounce delay prevents a single press being read twice.
    print("  Press USER button to continue...")
    while not button_pressed():     # Wait for button press
        pass
    time.sleep_ms(50)               # Debounce delay
    while button_pressed():         # Wait for button release
        pass
    time.sleep_ms(50)               # Debounce delay


def wait_for_button_blinking():
    # Blink the on-board LED while waiting for the USER button.
    # Returns once the button has been pressed and released.
    print("  Press USER button to continue...")
    while not button_pressed():
        pico_led_toggle()
        time.sleep_ms(200)
    pico_led_off()                  # Make sure LED is off when done
    time.sleep_ms(50)               # Debounce delay
    while button_pressed():         # Wait for button release
        pass
    time.sleep_ms(50)               # Debounce delay


def print_divider():
    # Print a divider line to separate test stages in the output.
    print("\n" + "-" * 40)


# ---------------------------------------------------------------------
# Test stage functions
# ---------------------------------------------------------------------

def test_startup():
    # Startup: Print a welcome message, show battery voltage, and blink
    # the on-board LED while waiting for the user to begin the tests.
    print_divider()
    print("XRPBeta Hardware Test")
    print_divider()
    voltage = battery_voltage()
    print(f"  Battery voltage: {voltage:.2f} V")
    if voltage < 4.4:
        # 4.4V threshold for NiMH batteries - set for your battery type
        print("  WARNING: Battery voltage is low - consider recharging!")
    else:
        print("  Battery voltage OK.")
    print("\n  LED is blinking to confirm the program is running.")
    wait_for_button_blinking()


def test_drive_motors():
    # Stage 1: Test the left and right drive motors and read encoders.
    # Motors run for MOTOR_RUN_MS milliseconds at each step.
    MOTOR_RUN_MS = 750

    print_divider()
    print("Stage 1: Left and Right Drive Motors")
    print("  Make sure the robot has room to move!")
    wait_for_button()

    reset_encoders()

    print("  Turning left...")
    left_motor(-60)
    right_motor(60)
    time.sleep_ms(MOTOR_RUN_MS)
    motors_stop()
    time.sleep_ms(300)

    print("  Turning right...")
    left_motor(60)
    right_motor(-60)
    time.sleep_ms(MOTOR_RUN_MS)
    motors_stop()
    time.sleep_ms(300)

    print("  Driving forward...")
    left_motor(60)
    right_motor(60)
    time.sleep_ms(MOTOR_RUN_MS)
    motors_stop()
    time.sleep_ms(300)

    print("  Driving reverse...")
    left_motor(-60)
    right_motor(-60)
    time.sleep_ms(MOTOR_RUN_MS)
    motors_stop()

    # Print encoder counts - non-zero values confirm encoders are working
    print(f"  Encoder counts - Left: {left_encoder()}, Right: {right_encoder()}")
    if left_encoder() == 0 and right_encoder() == 0:
        print("  NOTE: Both encoder counts are 0 - encoders may not be installed.")
    else:
        print("  Encoders OK.")
    print("  Drive motor test complete.")


def test_aux_motors():
    # Stage 2: Test auxiliary motors 3 and 4.
    MOTOR_RUN_MS = 750

    print_divider()
    print("Stage 2: Auxiliary Motors 3 and 4")
    print("  NOTE: Skip this stage if no auxiliary motors are connected.")
    wait_for_button()

    print("  Running motor 3 forward...")
    motor3(60)
    time.sleep_ms(MOTOR_RUN_MS)
    motor3(0)
    time.sleep_ms(300)

    print("  Running motor 3 reverse...")
    motor3(-60)
    time.sleep_ms(MOTOR_RUN_MS)
    motor3(0)
    time.sleep_ms(300)

    print("  Running motor 4 forward...")
    motor4(60)
    time.sleep_ms(MOTOR_RUN_MS)
    motor4(0)
    time.sleep_ms(300)

    print("  Running motor 4 reverse...")
    motor4(-60)
    time.sleep_ms(MOTOR_RUN_MS)
    motor4(0)

    print(f"  Encoder counts - Motor 3: {encoder3()}, Motor 4: {encoder4()}")
    print("  Auxiliary motor test complete.")


def test_servos():
    # Stage 3: Sweep SERVO1 and SERVO2 through centre, 0, 90, and back to centre.
    SERVO_STEP_MS = 600  # Time to hold each position (ms)

    print_divider()
    print("Stage 3: Servos")
    print("  NOTE: Skip this stage if no servos are connected.")
    wait_for_button()

    positions = [90, 0, 180, 90]    # Centre (90°), min, max, back to centre
    labels    = ["centre (90°)", "0°", "180°", "centre (90°)"]

    for angle, label in zip(positions, labels):
        print(f"  Moving servos to {label}...")
        set_servo(SERVO1, angle)
        set_servo(SERVO2, angle)
        time.sleep_ms(SERVO_STEP_MS)

    print("  Servo test complete.")


def test_sensors():
    # Stage 4: Read and print line sensor values until the button is pressed.
    # Values range from 0 (dark/no reflection) to 65535 (bright/full reflection).
    PRINT_INTERVAL_MS = 200

    print_divider()
    print("Stage 4: Line Sensors")
    print("  Try placing the robot over light and dark surfaces.")
    print("  Format: Left | Right  (0 = dark, 65535 = bright)")
    print("  Press USER button to stop and continue.")

    last_print = time.ticks_ms()
    while not button_pressed():
        if time.ticks_diff(time.ticks_ms(), last_print) >= PRINT_INTERVAL_MS:
            print(f"  Left: {line_left():5d}  |  Right: {line_right():5d}")
            last_print = time.ticks_ms()

    # Wait for button release before continuing
    time.sleep_ms(50)
    while button_pressed():
        pass
    time.sleep_ms(50)
    print("  Line sensor test complete.")


def test_sonar():
    # Stage 5: Print SONAR distance readings until the button is pressed.
    # Distance is returned in cm. See sonar_range() in XRPBeta.py for
    # an explanation of the negative error codes.
    PRINT_INTERVAL_MS = 100  # 100ms gives a readable update rate for a moving target

    print_divider()
    print("Stage 5: SONAR Distance Sensor")
    print("  NOTE: Skip this stage if no SONAR module is connected.")
    print("  Try moving an object toward and away from the sensor.")
    print("  Press USER button to stop and continue.")

    last_print = time.ticks_ms()
    while not button_pressed():
        if time.ticks_diff(time.ticks_ms(), last_print) >= PRINT_INTERVAL_MS:
            distance = sonar_range()
            if distance > 0:
                print(f"  Distance: {distance:6.1f} cm")
            elif distance == 0:
                print("  Distance: out of range")
            else:
                print(f"  Distance: error ({distance})")
            last_print = time.ticks_ms()

    # Wait for button release before continuing
    time.sleep_ms(50)
    while button_pressed():
        pass
    time.sleep_ms(50)
    print("  SONAR test complete.")


def test_imu():
    # Stage 6: Print IMU accelerometer and gyroscope values until the button is pressed.
    # Accelerometer values are in g (1g ≈ 9.8 m/s²) - at rest, Z should be near 1.0g.
    # Gyroscope values are in degrees per second - at rest, all axes should be near 0.
    PRINT_INTERVAL_MS = 200

    print_divider()
    print("Stage 6: IMU (Accelerometer and Gyroscope)")
    print("  Try tilting and rotating the robot.")
    print("  Accel in g (1g ≈ 9.8 m/s²), Gyro in degrees/second")
    print("  Press USER button to stop and continue.")

    last_print = time.ticks_ms()
    while not button_pressed():
        if time.ticks_diff(time.ticks_ms(), last_print) >= PRINT_INTERVAL_MS:
            ax, ay, az = imu_acceleration()
            gx, gy, gz = imu_gyroscope()
            print(f"  Accel: X={ax:6.3f}g  Y={ay:6.3f}g  Z={az:6.3f}g  |"
                  f"  Gyro: X={gx:7.2f}  Y={gy:7.2f}  Z={gz:7.2f} dps")
            last_print = time.ticks_ms()

    # Wait for button release before continuing
    time.sleep_ms(50)
    while button_pressed():
        pass
    time.sleep_ms(50)
    print("  IMU test complete.")


# ---------------------------------------------------------------------
# Main test loop
# ---------------------------------------------------------------------

test_startup()  # Run the startup check once at power-on

while True:
    # Run each test stage in sequence, repeating indefinitely.
    # Each stage waits for a button press before beginning.

    test_drive_motors()

    print("\n  Press USER button to begin Stage 2 (auxiliary motors).")
    wait_for_button()
    test_aux_motors()

    print("\n  Press USER button to begin Stage 3 (servos).")
    wait_for_button()
    test_servos()

    print("\n  Press USER button to begin Stage 4 (line sensors).")
    wait_for_button()
    test_sensors()

    print("\n  Press USER button to begin Stage 5 (SONAR).")
    wait_for_button()
    test_sonar()

    print("\n  Press USER button to begin Stage 6 (IMU).")
    wait_for_button()
    test_imu()

    print_divider()
    print("All tests complete!")
    print("  LED will blink while waiting to repeat the test sequence.")
    wait_for_button_blinking()