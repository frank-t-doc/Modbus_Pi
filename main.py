import threading
from reader.reader_wr import reader_wr
from reader.reader_smartmeter import reader_smartmeter
#from reader.modbus_reader import read_modbus_frame
from pythonscrpite_old.serial_sniffer import serial_sniffer

def main():
    print("Growatt Parser gestartet...")

    # WR / ShineBus / BMS / CAN
    #t1 = threading.Thread(target=reader_wr, daemon=True)

    # Smartmeter (FC=04 / FC=06)
    #t2 = threading.Thread(target=reader_smartmeter, daemon=True)

    t3 = threading.Thread(target=serial_sniffer, daemon=True)

    #t1.start()
    #t2.start()
    t3.start()

    # Hauptthread läuft weiter
    while True:
        pass

if __name__ == "__main__":
    main()
