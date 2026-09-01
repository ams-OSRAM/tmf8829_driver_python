import serial.tools.list_ports
import threading
import time

# Import the official TMF8829 driver
# Make sure you've installed it from the ams-OSRAM GitHub repo
from tmf8829 import TMF8829

def list_tmf8829_ports():
    """
    Detect all COM ports that correspond to TMF8829_EVM-EB_SHIELD-01 boards.
    Adjust the filter string if your device description differs.
    """
    ports = serial.tools.list_ports.comports()
    tmf_ports = []
    for p in ports:
        if "TMF8829" in p.description or "USB Serial" in p.description:
            tmf_ports.append(p.device)
    return tmf_ports

def run_tmf8829(port):
    """
    Connect to a TMF8829 board, start measurements, and print distance data.
    Runs in its own thread for each board.
    """
    try:
        sensor = TMF8829(port)
        sensor.open()
        sensor.start_measurement()
        print(f"[{port}] Measurement started.")

        while True:
            frame = sensor.get_measurement()
            if frame:
                # distances_mm is a list of measured distances in millimeters
                distances = frame.distances_mm
                print(f"[{port}] Distances (mm): {distances}")
            time.sleep(0.05)  # Adjust for your measurement rate

    except Exception as e:
        print(f"[{port}] Error: {e}")
    finally:
        try:
            sensor.stop_measurement()
            sensor.close()
        except:
            pass
        print(f"[{port}] Closed.")

if __name__ == "__main__":
    ports = list_tmf8829_ports()
    if not ports:
        print("No TMF8829_EVM-EB_SHIELD-01 boards found.")
    else:
        print(f"Found boards: {ports}")
        threads = []
        for port in ports:
            t = threading.Thread(target=run_tmf8829, args=(port,), daemon=True)
            t.start()
            threads.append(t)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping all sensors...")