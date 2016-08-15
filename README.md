LoRa + Raspberry Pi + Arduinos
==============================

Jeffrey D. Walker, PhD  
[Walker Environmental Research, LLC](http://walkerenvres.com)

This repo contains source code for creating a wireless sensor network using a Raspberry Pi and one or more Arduinos connected via LoRa.

The Raspberry Pi serves as the central receiver by connecting an Arduino Feather M0 with embedded LoRa chip via USB. In this configuration, the feather acts as a relay, passing LoRa messages received from other nodes to the RPi over Serial.

## Python Scripts

The `py/` folder contains python scripts that are run on the Raspberry Pi.

### read-serial.py

The `py/read-serial.py` script simply reads data from the USB serial port.

```
cd py
python read-serial.py -d /dev/ttyACM0 -r 9600
```

where `-d` defines the device socket to listen on (corresponds to the Arduino connected via USB), and `-r` is the serial baud rate.

### lora-gateway.py

The `py/lora-gateway.py` script reads messages from the USB serial port, and automatically pushes those messages to a remote influxdb server. This script takes the same arguments as `read-serial.py`

```
python lora-gateway.py -d /dev/ttyACM0 -r 9600
```

## Arduino Sketches

The `ino/` folder contains a number of Arduino sketches. These will be described soon...

## References

- Reading messages sent from Arduino to RPi over USB: https://oscarliang.com/connect-raspberry-pi-and-arduino-usb-cable/
- ArduinoJSON library for converting sensor readings to JSON, which can be sent over LoRa: https://github.com/bblanchon/ArduinoJson
- Connecting Adafruit LoRa breakout board to an Arduino: https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/overview


