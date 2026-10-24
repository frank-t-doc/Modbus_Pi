import threading
from reader.reader_wr import reader_wr
from reader.reader_smartmeter import reader_smartmeter

def main():
    print("Growatt Parser gestartet...")

    # WR / ShineBus / BMS / CAN
    #t1 = threading.Thread(target=reader_wr, daemon=True)

    # Smartmeter (FC=04 / FC=06)
    t2 = threading.Thread(target=reader_smartmeter, daemon=True)

    
    #t1.start()
    t2.start()

    # Hauptthread läuft weiter
    while True:
        pass

if __name__ == "__main__":
    main()
