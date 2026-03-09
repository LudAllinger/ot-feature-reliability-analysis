from pymodbus.client import ModbusTcpClient
import time

PLC_IP = "127.0.0.1"

client = ModbusTcpClient(PLC_IP, port=502)
client.connect()

while True:
    temp = client.read_holding_registers(1024, 1, slave=1)
    counter = client.read_holding_registers(1025, 1, slave=1)
    motor = client.read_coils(0, 1, slave=1)

    print("temperature:", temp.registers[0])
    print("production_counter:", counter.registers[0])
    print("motor_state:", motor.bits[0])
    print("-----")

    time.sleep(0.02)