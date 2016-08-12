import argparse
import serial

parser = argparse.ArgumentParser(description='Read from serial and echo message')
parser.add_argument('-d', '--device', help='path to serial device', required=True)
parser.add_argument('-r', '--rate', help='rate of serial communication', type=int, required=True)

args = parser.parse_args()

DEVICE = args.device
RATE = args.rate

print 'Reading from %s at %d' % (DEVICE, RATE)

ser = serial.Serial(DEVICE, RATE)

while 1:
  msg = ser.readline().strip()
  print msg

