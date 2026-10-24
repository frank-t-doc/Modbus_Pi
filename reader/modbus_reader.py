import serial

def read_modbus_frame(port="/dev/ttyUSB0", baud=9600):
    """
    Liest rohe Modbus-RTU Frames vom RS485-Bus.
    Gibt einen Hex-String zurück oder None bei Timeout.
    """

    try:
        ser = serial.Serial(port, baudrate=baud, timeout=1)
    except Exception as e:
        return None

    raw = ser.read(40)  # typische Growatt-Frames sind < 40 Bytes

    if len(raw) == 0:
        return None

    return raw.hex()
