import serial
ser=serial.Serial('/dev/ttyS0', 115200, timeout=1)
ser.write('setpt 120,120\r\n')
while True:
  print(ser.readline())
