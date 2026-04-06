###
# This program connects to the PLC simulator and continuously reads data, logging it to a CSV file.
# Make sure to have the PLC simulator running before starting this.
# Press Ctrl+C to stop the capture when done.
###

from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import time
import threading
from datetime import datetime
import os
import atexit

# ----- Configuration -----
PLC_IP = "127.0.0.1"
LOG_FILE = "logs/plc/normal/plc_data_log.csv"
ERROR_LOG_FILE = "logs/plc/normal/error_log.txt"
MAX_LOG_SIZE = 50_000_000  # 50 MB
EXPERIMENT = "normal"

log_file = None

# ----- Error logging -----
def errorLog(message):
    timestamp = datetime.now().isoformat()
    print(f"ERROR: {message}")
    with open(ERROR_LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")

# ----- Clean up on exit -----
def close_log_file():
    global log_file
    if log_file:
        log_file.flush()
        log_file.close()
        print("Log file closed.")
atexit.register(close_log_file)

# ----- Main data reading loop -----
def read_plc_data():
    global log_file

    log_file = open(LOG_FILE, "a")
    counter = 0

    while True:
        start = time.monotonic()
        try:
            counter += 1

            # Read data from PLC
            registers = client.read_holding_registers(address=1024, count=2)
            coils = client.read_coils(address=0, count=5)

            # Validate data before logging
            if (not registers.isError() and 
                not coils.isError() and
                len(registers.registers) >= 2 and
                len(coils.bits) >= 5):

                timestamp = datetime.now().isoformat()

                # Extract values
                wl = registers.registers[0]
                wd = registers.registers[1]
                inlet = coils.bits[0]
                outlet = coils.bits[1]
                pump = coils.bits[2]
                levelArm = coils.bits[3]
                chemArm = coils.bits[4]

                # Log the data
                log_file.write(
                    f"{timestamp},{EXPERIMENT},{wl},{wd},{inlet},{outlet},{pump},{levelArm},{chemArm}\n"
                )

                # Flush every 10 lines to ensure data is written to disk
                if counter % 10 == 0:
                    log_file.flush()

            else:
                errorLog("Modbus read error")

            # Rotate log file if it exceeds max size
            if counter % 100 == 0:
                if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > MAX_LOG_SIZE:
                    log_file.flush()
                    log_file.close()

                    new_name = f"plc_data_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    os.rename(LOG_FILE, new_name)

                    log_file = open(LOG_FILE, "w")
                    log_file.write(
                        "timestamp,experiment,water_level,water_demand,inlet,outlet,pump,levelArm,chemArm\n"
                    )

            # Heartbeat
            if counter % 600 == 0:
                print(f"Heartbeat OK: {timestamp}")

        # Handle Modbus connection issues
        except ModbusIOException:
            errorLog("Trying to reconnect to PLC...")
            client.close()
            time.sleep(1)

            # Attempt reconnection with delay
            while not client.connect():
                errorLog("Reconnection failed. Retrying...")
                time.sleep(3)

        # Handle any other unexpected exceptions
        except Exception as e:
            errorLog(f"Unexpected error: {e}")

        # Deterministic timing
        elapsed = time.monotonic() - start
        time.sleep(max(0, 0.1 - elapsed))

# Initialize Modbus client
client = ModbusTcpClient(PLC_IP, port=502)

# Connect to PLC
if not client.connect():
    errorLog("Failed to connect to PLC. Exiting.")
    exit(1)
print("Connected to PLC")

# Initialize log file
with open(LOG_FILE, "w") as f:
    f.write("timestamp,experiment,water_level,water_demand,inlet,outlet,pump,levelArm,chemArm\n")

# Start data reading thread
threading.Thread(target=read_plc_data, daemon=True).start()

# Keep the main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Interrupted by user")
    client.close()