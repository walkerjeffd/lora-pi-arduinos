LoRa + Raspberry Pi + Arduinos
==============================

Jeffrey D. Walker, PhD  
[Walker Environmental Research, LLC](http://walkerenvres.com)

This repo contains source code for creating a wireless sensor network using a Raspberry Pi and one or more Arduinos connected via LoRa.

The Raspberry Pi serves as the central receiver by connecting an Arduino Feather M0 with embedded LoRa chip via USB. In this configuration, the feather acts as a relay, passing LoRa messages received from other nodes to the RPi over Serial.

## Set Up Raspberry Pi

Install NOOBS, follow usual linux set up guides


## Set Up Arduinos

There are two arduinos with LoRa boards

```
Arduino:TX = Arduino Uno + DHT Sensor
Arduino:RX = Feather MO < Raspberry Pi
```

### Receiver Arduino (`arduino-feather-m0-rx`)

Connect Feather M0 to local USB.

Open Arduino App (v1.8.7)

Add Feather M0 board

```
Arduino > Preferences > Additional Boards Manager URLs: + "https://adafruit.github.io/arduino-board-index/package_adafruit_index.json"
```

Update boards manager (if necessary)

```txt
Tools > Board: Adafruit SAMD > Adafruit Feather M0
```

Open `ino/arduino-feather-m0-rx/arduino-feather-m0-rx.ino`

Upload to arduino

Disconnect from local to `minnow`.

#### Test Receiver

List available devices on raspberry pi

```
ls /dev
```

Arduino will probably be `/dev/ttyACM0`.

Print output

```
sudo cat /dev/ttyACM0
```

Should show boot up text and stream from there...

### Transmitter Arduino

Connect Uno to local USB.

Open Arduino App (v1.8.7)

Set `Tools > Board: Arduino/Genuino Uno`

#### Test

Upload `ino/arduino-uno-tx-test/arduino-uno-tx-test.ino`

Open arduino serial log

```
Sending to rf95_server
Sending Hello World #29
Sending...
Waiting for packet to complete...
Sending to rf95_server
Sending Hello World #30
Sending...
Waiting for packet to complete...
Sending to rf95_server
Sending Hello World #31
Sending...
```

Check raspberry pi log

```
Hello World #29

Hello World #30

Hello World #31
```

#### Add DHT Sensor

Upload `ino/arduino-uno-tx/arduino-uno-tx.ino`

Open arduino serial log.
Should send `{id, millis, data: {h,f,hi}}` in JSON

```
Waiting for packet to complete...
Humidity: 51.90 % Temperature: 71.60 *F Heat index: 76.78 *F
Sending {"id":2,"millis":8547,"data":{"h":51.9,"f":71.60,"hi":76.785}}
Waiting for packet to complete...
Humidity: 51.90 % Temperature: 71.60 *F Heat index: 76.78 *F
Sending {"id":2,"millis":11230,"data":{"h":52.0,"f":71.78,"hi":76.793}}
Waiting for packet to complete...
Humidity: 52.00 % Temperature: 71.78 *F Heat index: 76.79 *F
Sending {"id":2,"millis":13914,"data":{"h":51.9,"f":71.60,"hi":76.785}}
Waiting for packet to complete...
```

### Check Receiver

Output on raspberry pi should now show (from `cat /dev/ttyACM0`):

```json
{"id":2,"millis":80999,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":83682,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":86365,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":89048,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":91731,"data":{"h":52.0,"f":71.60,"hi":76.779}}
```

## Python Scripts

The `py/` folder contains python scripts that are run on the Raspberry Pi.

Clone the repo

```
cd ~/repo

```

### read-serial.py

The `py/read-serial.py` script simply reads data from the USB serial port.

```
cd py
sudo python read-serial.py -d /dev/ttyACM0 -r 9600
```

where `-d` defines the device socket to listen on (corresponds to the Arduino connected via USB), and `-r` is the serial baud rate.

Output should look like:

```
{"id":2,"millis":1264966,"data":{"h":52.5,"f":71.78,"hi":76.762}}
{"id":2,"millis":1270338,"data":{"h":52.4,"f":71.78,"hi":76.768}}
{"id":2,"millis":1275710,"data":{"h":52.3,"f":71.78,"hi":76.774}}
```

### lora-gateway.py

Install dependencies under `root`

```
sudo su root
pip install influxdb
```

The `py/lora-gateway.py` script reads messages from the USB serial port, and automatically pushes those messages to a remote influxdb server. This script takes the same arguments as `read-serial.py`

```
python lora-gateway.py -d /dev/ttyACM0 -r 9600
```




## References

- Reading messages sent from Arduino to RPi over USB: https://oscarliang.com/connect-raspberry-pi-and-arduino-usb-cable/
- ArduinoJSON library for converting sensor readings to JSON, which can be sent over LoRa: https://github.com/bblanchon/ArduinoJson
- Connecting Adafruit LoRa breakout board to an Arduino: https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/overview


