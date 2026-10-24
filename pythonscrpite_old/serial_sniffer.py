import serial
ser = serial.Serial('/dev/ttyUSB1', 9600, timeout=1)
def serial_sniffer():
    while True:
        data = ser.read(200)
        if data:
            print(data.hex())
