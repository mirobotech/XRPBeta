# XRPBeta Test

This repository contains a board module file and a test program for the [Sparkfun XRPBeta](https://www.sparkfun.com/experiential-robotics-platform-xrp-kit-beta.html) robot controller.

The board module file enables the XRPBeta controller to be programmed using regular MicroPython code and the helper functions included in the board module file. The XRPBeta board module is designed to be similar to the board modules developed for BEAPER Pico and BEAPER Nano, making it easy for students to transition between these three circuits.

To use this test program and board module, you will need to:

1. Install the latest MicroPython firmware on the XRPBeta
2. Copy the XRPBeta.py board module file into the memory of the Raspberry Pi Pico W
3. Run the XRPBeta_test.py program

## Installing MicroPython on XRPBeta

1. Download the Sparkfun XRP Controller Beta MicroPython .UF2 firmware file from the [MicroPython downloads](https://micropython.org/download/SPARKFUN_XRP_CONTROLLER_BETA/) website.
2. With the XRPBeta switched off, press and hold the BOOTSEL button on the Raspberry Pi Pico module while connecting its USB cable to your computer.
3. An RPI-RP2 drive will be mounted on your computer. Copy the downloaded MicroPython .UF2 firware file to the RPI-RP2 drive to install it on the Raspberry Pi Pico W module in the XRPBeta.

After installing MicroPython on the controller, the RPI-RP2 drive will eject itself from your computer. 

## Copying the XRPBeta.py board module file into the Raspberry Pi Pico W

1. Configure your Python IDE for use with Raspberry Pi Pico. For first time users, we suggest [Thonny](https://thonny.org) as an easy way to get started.
2. Connect the XRPBeta controller to your computer and connect to its Raspberry Pi Pico through the IDE.
2. Open the XRPBeta.py board module file in the IDE.
4. Save the XRPBeta.py file to into the memory of the connected Raspberry Pi Pico in your XRPBeta controller.

## Running the XRPBeta_test.py program

1. Open the XRPBeta_test.py program in your IDE.
2. Connect the XRPBeta controller to your computer and connect to its Raspberry Pi Pico through the IDE.
3. Ensure known good batteries are installed in the XRPBeta robot and switch the XRPBeta board on.
4. Run the program on the connected Raspberry Pi Pico in your XRPBeta controller. The green LED on the Raspberry Pi Pico module will start flashing, and prompts will appear in the IDE's MicroPython console. Follow the prompts to test each of the XRPBeta's connected hardware devices.
