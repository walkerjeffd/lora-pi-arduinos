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
7. Add `lora-gateway` to supervisor
8. Configure Grafana to plot data from InfluxDB

## InfluxDB

Download and install InfluxDB (v1.6) according to [instructions](https://docs.influxdata.com/influxdb/v1.6/introduction/installation/).

Create new database called `lora`.

```
influx -precision rfc3339
> CREATE DATABASE lora
> USE lora
> SHOW DATABASES
```

### Retention Policies and Continuous Queries

[Downsampling and Retention](https://docs.influxdata.com/influxdb/v1.6/guides/downsampling_and_retention/)

A retention policy (RP) determines how long data are kept within InfluxDB. A continuous query (CQ) automatically downsamples a time series to a lower frequency, and can be used with different RPs. The two constructs can be mixed and matched to store data at varying frequencies for varying durations.

Three CQs are then created and stored in varying retention policies:

- 5 min stored for 30 days
- 15 minutes stored for 1 year
- 1 hour stored forever

```
CREATE RETENTION POLICY "1_day" ON "lora" DURATION 1d REPLICATION 1 DEFAULT
CREATE RETENTION POLICY "30_days" ON "lora" DURATION 30d REPLICATION 1
CREATE RETENTION POLICY "1_year" ON "lora" DURATION 52w REPLICATION 1

CREATE CONTINUOUS QUERY "cq_1m" ON "lora" BEGIN SELECT mean("f") AS "f_mean", mean("h") AS "h_mean", mean("hi") AS "hi_mean" INTO "30_days"."dht_1m" FROM "dht" GROUP BY time(1m) END
CREATE CONTINUOUS QUERY "cq_15m" ON "lora" BEGIN SELECT mean("f") AS "f_mean", min("f") AS "f_min", max("f") AS "f_max", mean("h") AS "h_mean", min("h") AS "h_min", max("h") AS "h_max", mean("hi") AS "hi_mean", min("hi") AS "hi_min", max("hi") AS "hi_max" INTO "1_year"."dht_15m" FROM "dht" GROUP BY time(15m) END
CREATE CONTINUOUS QUERY "cq_1h" ON "lora" BEGIN SELECT mean("f") AS "f_mean", min("f") AS "f_min", max("f") AS "f_max", mean("h") AS "h_mean", min("h") AS "h_min", max("h") AS "h_max", mean("hi") AS "hi_mean", min("hi") AS "hi_min", max("hi") AS "hi_max" INTO "dht_1h" FROM "dht" GROUP BY time(1h) END
```

Inspect database

```
SHOW RETENTION POLICIES
SHOW CONTINUOUS QUERIES
SHOW MEASUREMENTS
SHOW SERIES
```

Query data. Note that measurements (`dht`, `dht_1m`, `dht_15m`, `dht_1h` need to prefixed with retention policy if not default).

```
use lora
select * from "1_day".dht
select * from "30_days".dht_1m
select * from "1_year".dht_15m
select * from dht_1h
```

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

```txt
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

Output on raspberry pi should now show (from `read-serial.py`):

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
> select * from dht;
# name: dht
# time                f     h    hi     id
# ----                -     -    --     --
# 1539289787555996127 71.96 51.8 76.821 0
# 1539289790292909668 71.96 51.8 76.821 0
# 1539289792895148684 71.96 51.8 76.821 0
# 1539289795741793109 71.78 51.8 76.804 0
# 1539289798295975899 71.96 51.8 76.821 0
# 1539289801092241760 71.78 51.8 76.804 0
# 1539289803729000326 71.96 51.8 76.821 0
# 1539289806493233282 71.78 51.8 76.804 0
# 1539289809092750704 71.96 51.8 76.821 0
# 1539289811890869965 71.96 51.8 76.821 0
# 1539289814489342027 71.96 51.7 76.827 0
# 1539289817451912271 71.96 51.7 76.827 0
# 1539289819887961413 71.96 51.7 76.827 0
# 1539289822487912570 71.96 51.7 76.827 0
# 1539289825289112963 71.96 51.7 76.827 0
```

## Supervisor Process Manager

The `lora-gateway.py` script can be automatically (re)started on the Raspberry Pi using the `supervisord` daemon.

### Configuration File

A template configuration file is provided in `py/supervisor/lora-gateway.template.conf`.

Create a new supervisor configuration file and copy the contents from the template.

```txt
sudo nano /etc/supervisor/conf.d/lora-gateway.conf
<paste contents of py/supervisor/lora-gateway.template.conf>
<edit 'directory' and other fields as needed>
```

After creating the configuration file, update `supervisor` to add the `lora-gateway` program.

```
sudo supervisor update
```

### Log Files

Only stderr logging is enabled, and will be stored in `/var/log/supervisor/lora-gateway-stderr.log`.

The stdout stream can also be logged by modifying the configuration file.

### Manage Process

```
sudo supervisorctl update
sudo supervisorctl status lora-gateway
sudo supervisorctl stop lora-gateway
sudo supervisorctl start lora-gateway
```

## Grafana

Add InfluxDB data source and build dashboard.

## References

- [Reading messages sent from Arduino to RPi over USB](https://oscarliang.com/connect-raspberry-pi-and-arduino-usb-cable/)
- [ArduinoJSON library for converting sensor readings to JSON, which can be sent over LoRa](https://github.com/bblanchon/ArduinoJson)
- [Connecting Adafruit LoRa breakout board to an Arduino](https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/overview)
