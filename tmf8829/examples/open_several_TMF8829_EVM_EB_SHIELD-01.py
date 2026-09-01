import serial
import serial.tools.list_ports
import threading
import time

# Replace with your TMF8829 driver import
# from tmf8829_driver import TMF8829

def list_tmf8829_ports():
    """Find all COM ports that look like TMF8829 boards."""
    ports = serial.tools.list_ports.comports()
    tmf_ports = []
    for p in ports:
        if "TMF8829" in p.description or "USB Serial" in p.description:
            tmf_ports.append(p.device)
    return tmf_ports

def read_from_board(port):
    """Example: read raw UART data from TMF8829."""
    try:
        with serial.Serial(port, baudrate=115200, timeout=1) as ser:
            print(f"[{port}] Connected.")
            while True:
                line = ser.readline().decode(errors="ignore").strip()
                if line:
                    print(f"[{port}] {line}")
    except serial.SerialException as e:
        print(f"[{port}] Error: {e}")

if __name__ == "__main__":
    ports = list_tmf8829_ports()
    if not ports:
        print("No TMF8829 boards found.")
    else:
        print(f"Found boards: {ports}")
        threads = []
        for port in ports:
            t = threading.Thread(target=read_from_board, args=(port,), daemon=True)
            t.start()
            threads.append(t)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping...")