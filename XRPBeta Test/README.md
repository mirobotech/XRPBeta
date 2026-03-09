# XRPBeta Test

This repository contains a board module file and a test program for the [Sparkfun XRPBeta](https://www.sparkfun.com/experiential-robotics-platform-xrp-kit-beta.html) robot controller.

The board module file enables the XRPBeta controller to be programmed using regular MicroPython code and the helper functions included in the board module file. The XRPBeta board module is designed to be similar to the board modules developed for BEAPER Pico and BEAPER Nano, making it easy for students to transition between these three circuits.

The XRPBeta_test program tests all of the hardware features of the XRPBeta controller circuit.

To use this test program and board module, you will need to:

1. Install the latest MicroPython firmware on the XRPBeta
2. Copy the XRPBeta.py board module file into the memory of the Raspberry Pi Pico W mounted on the XRPBeta
3. Run the XRPBeta_test.py program in the XRPBeta

## Installing MicroPython on XRPBeta

1. Download the Sparkfun XRP Controller Beta MicroPython .UF2 firmware file from the [MicroPython downloads](https://micropython.org/download/SPARKFUN_XRP_CONTROLLER_BETA/) website.
2. With the XRPBeta switched off, press and hold the BOOTSEL button on the Raspberry Pi Pico module while connecting its USB cable to your computer.
3. An RPI-RP2 drive will be mounted on your computer. Copy the downloaded MicroPython .UF2 firware file to the RPI-RP2 drive to install it on the Raspberry Pi Pico W module in the XRPBeta controller.

After installing MicroPython on the Raspberry Pi Pico in the XRPBeta controller (we'll simply refer to as XRPBeta from here on), the RPI-RP2 drive will eject itself from your computer. 

## Copying the XRPBeta.py board module file into XRPBeta

1. Configure your Python IDE for use with a Raspberry Pi Pico microcontroller. For first time users, we suggest [Thonny](https://thonny.org) as an easy way to get started. (Find a good tutorial to lead you through it, but don't install MicroPython into the XRPBeta again -- we already did that in the above step!)
2. Connect the XRPBeta controller to your computer with a USB cable, and connect to it through the IDE. (Choose the Raspberry Pi Pico from the bottom right corner control of the Thonny window.)
2. Open the XRPBeta.py board module file in the IDE.
4. Save the XRPBeta.py file to into the memory of the XRPBeta controller (shown as Raspberry Pi Pico in Thonny).

## Running the XRPBeta_test.py program

1. Open the XRPBeta_test.py program in your IDE.
2. Connect the XRPBeta controller to your computer with a USB cable, and connect to its Raspberry Pi Pico through the IDE.
3. Ensure known good batteries are installed in the XRPBeta robot, and then switch the XRPBeta board on.
4. Run the XRPBeta_test program on the XRPBeta. The green LED on the Raspberry Pi Pico module of the XRPBeta will start flashing, and prompts will appear in the IDE's MicroPython console. Follow the prompts and press the USER pushbutton (beside the Sparkfun label) to advance to through tests for each of the XRPBeta's connected hardware devices.
