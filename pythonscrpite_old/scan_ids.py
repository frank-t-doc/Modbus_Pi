from pymodbus.client.sync import ModbusSerialClient

client = ModbusSerialClient(
    method="rtu",
    port="/dev/ttyUSB0",
    baudrate=9600,
    timeout=1,
    parity="N",
    stopbits=1,
    bytesize=8
)

client.connect()

print("Starte Modbus-ID-Scan...")

for slave_id in range(1, 2):
    print(f"Teste ID {slave_id}...")
    result = client.read_holding_registers(0, 1, unit=slave_id)
    if not result.isError():
      print(f"✔ Gerät gefunden bei ID {slave_id}")
    print("Raw result:", result)
    print("Registers:", getattr(result, "registers", None))

client.close()
