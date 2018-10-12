from influxdb import InfluxDBClient
import json
import argparse
import serial

host = 'trout.local'
database = 'lora'
measurement = 'dht'

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
    'measurement': measurement,
    'tags': tags,
    'fields': fields
  }]

  # print "Uploading: %s" % payload

  success = client.write_points(payload)
  if not success:
    print('Upload failed...')

while True:
  msg = ser.readline().strip()

  msg_json = json.loads(msg)

  id = msg_json[u'id']
  tags = {'id': id}
  fields = msg_json[u'data']

  send(measurement, tags, fields)
