from influxdb import InfluxDBClient
import json
import argparse
import serial

host = 'alewife.local'
database = 'rpi'

parser = argparse.ArgumentParser(description='Read from serial and echo message')
parser.add_argument('-d', '--device', help='path to serial device', required=True)
parser.add_argument('-r', '--rate', help='rate of serial communication', type=int, required=True)

args = parser.parse_args()

DEVICE = args.device
RATE = args.rate

client = InfluxDBClient(host, 8086, 'root', 'root', database)

print 'Reading from %s at %d' % (DEVICE, RATE)

ser = serial.Serial(DEVICE, RATE)

def send(measurement, tags, fields):
  payload = [{
    "measurement": measurement,
    "tags": tags,
    "fields": fields
  }]

  print "Uploading: %s" % payload

  success = client.write_points(payload, retention_policy="one_hour")
  if not success:
    print('Upload failed...')

while True:
  msg = ser.readline().strip()
  
  msg_json = json.loads(msg)
  # print "msg_json = %s" % (msg_json)

  measurement = "lora"
  id = msg_json[u'id']
  millis = msg_json[u'millis']
  tags = {"id": id, "millis": millis}
  fields = msg_json[u'data']
  # print (measurement, tags, fields)
  send(measurement, tags, fields)
