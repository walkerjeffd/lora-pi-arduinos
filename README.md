LoRa + Raspberry Pi + Arduinos
==============================

Jeffrey D. Walker, PhD  
[Walker Environmental Research, LLC](https://walkerenvres.com)

This repo contains source code for creating a wireless sensor network using a Raspberry Pi and one or more Arduinos connected via LoRa radio transmitters.

The Raspberry Pi serves as the central receiver by connecting an Arduino Feather M0 with embedded LoRa chip via USB. In this configuration, the feather acts as a relay, passing LoRa messages received from other nodes to the RPi over Serial.

Any number of sensor nodes can be set up using Arduino Uno with a LoRa chip.

## Quick Start

1. Load `ino/arduino-feather-m0-rx/arduino-feather-m0-rx.ino` onto Arduino Feather M0
2. Load `ino/arduino-uno-tx/arduino-uno-tx.ino` onto Arduino Uno
3. Connect Arduino Feather M0 to Raspberry Pi
4. Run `py/read-serial.py` on Raspberry Pi to test transmission
5. Run `py/lora-gateway.py` on Raspberry Pi to test InfluxDB storage
6. Set up `supervisord` by copying content of `py/supervisor/lora-gateway.template.conf` to `/etc/supervisor/conf.d/lora-gateway.conf` and setting `directory` value
7. Update supervisor (`sudo supervisorctl update`) and then check status (`sudo supervisorctl status`) and stderr logs in `/var/log/supervisor/lora-gateway-stderr.log`
8. Configure Grafana to plot data from InfluxDB

## Set Up Raspberry Pi

### Operating System

Install [Raspbian Stretch with Desktop](https://www.raspberrypi.org/downloads/raspbian/), follow usual linux set up guides.

### Supervisor

Install [supervisord](http://supervisord.org) python process manager

```
sudo apt update
sudo apt install supervisor
```

Configuration files can be stored in `/etc/supervisor/conf.d`.

Control using `sudo supervisorctl <update|status|help|...>`.

### InfluxDB Client

Install `influxdb` python package as root

```
sudo pip install influxdb
```

### Clone Project Repo

```
mkdir ~/repo
git clone git@github.com:walkerjeffd/lora-pi-arduinos.git ~/repo/lora-pi-arduinos
```

## Set Up Arduinos

### Receiver Arduino (`arduino-feather-m0-rx`)

Connect Feather M0 to local USB.

Open Arduino App (v1.8.7)

Add Feather M0 board

```
Arduino > Preferences > Additional Boards Manager URLs: + "https://adafruit.github.io/arduino-board-index/package_adafruit_index.json"
```

Update boards manager (if necessary), then select board: `Tools > Board: Adafruit SAMD > Adafruit Feather M0`

Open `ino/arduino-feather-m0-rx/arduino-feather-m0-rx.ino`

Upload to arduino and check Serial output.

Disconnect from local, and connect to Raspberry Pi.

### Transmitter Arduino

Connect Arduino Uno to local USB.

Open Arduino App (v1.8.7)

Select board: `Tools > Board: Arduino/Genuino Uno`

#### Test LoRa Chip (rf95)

Upload `ino/arduino-uno-tx-test/arduino-uno-tx-test.ino`

Open arduino serial log, and expect output:

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

Check receiver on Raspberry Pi using `py/read-serial.py`

```
Hello World #29

Hello World #30

Hello World #31
```

#### DHT Sensor

Upload `ino/arduino-uno-tx/arduino-uno-tx.ino` to Arduino Uno.

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

Output on raspberry pi should now show (from `sudo cat /dev/ttyACM0`):

```json
{"id":2,"millis":80999,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":83682,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":86365,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":89048,"data":{"h":52.0,"f":71.60,"hi":76.779}}
{"id":2,"millis":91731,"data":{"h":52.0,"f":71.60,"hi":76.779}}
```

## Python Scripts

### `read-serial.py`

The `py/read-serial.py` script simply reads data from the USB serial port and prints to the console.

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

### `lora-gateway.py`

The `py/lora-gateway.py` script reads messages from the USB serial port, and automatically pushes those messages to a remote influxdb server. This script takes the same arguments as `read-serial.py`. Must be run as `root`.

The script may need to be modified by specifying the `host` and `database` variables (**TODO**: set up python configuration file).

```
sudo python lora-gateway.py -d /dev/ttyACM0 -r 9600
```

Check that data are uploaded on InfluxDB server.

```
$ influx
> USE lora
> select * from lora;
> select * from lora;
# name: lora
# time                f     h    hi     id millis
# ----                -     -    --     -- ------
# 1539289787555996127 71.96 51.8 76.821 0  655478
# 1539289790292909668 71.96 51.8 76.821 0  658163
# 1539289792895148684 71.96 51.8 76.821 0  660848
# 1539289795741793109 71.78 51.8 76.804 0  663531
# 1539289798295975899 71.96 51.8 76.821 0  666216
# 1539289801092241760 71.78 51.8 76.804 0  668901
# 1539289803729000326 71.96 51.8 76.821 0  671586
# 1539289806493233282 71.78 51.8 76.804 0  674269
# 1539289809092750704 71.96 51.8 76.821 0  676954
# 1539289811890869965 71.96 51.8 76.821 0  679639
# 1539289814489342027 71.96 51.7 76.827 0  682323
# 1539289817451912271 71.96 51.7 76.827 0  685006
# 1539289819887961413 71.96 51.7 76.827 0  687691
# 1539289822487912570 71.96 51.7 76.827 0  690376
# 1539289825289112963 71.96 51.7 76.827 0  693061
```

## Grafana

Add InfluxDB data source and build dashboard.

## References

- [Reading messages sent from Arduino to RPi over USB](https://oscarliang.com/connect-raspberry-pi-and-arduino-usb-cable/)
- [ArduinoJSON library for converting sensor readings to JSON, which can be sent over LoRa](https://github.com/bblanchon/ArduinoJson)
- [Connecting Adafruit LoRa breakout board to an Arduino](https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/overview)
