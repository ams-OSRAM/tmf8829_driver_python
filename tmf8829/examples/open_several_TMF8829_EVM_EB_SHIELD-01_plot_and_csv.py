import threading
import time
import csv
import serial.tools.list_ports
from datetime import datetime
# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

from tmf8829_conv import TMF8829

from __init__ import HEX_FILE
from tmf8829_conv import *
from tmf8829_application import Tmf8829Application
from tmf8829_application_defines import tmf8829RefSpadFrame
from utilities.tmf8829_visualisation import Tmf8829PlotPixelMap
from utilities.tmf8829_visualisation import Tmf8829PlotPixelDistMap

# Import the official TMF8829 driver
from tmf8829_conv import TMF8829

# Shared data structure for plotting
sensor_data = {}
lock = threading.Lock()

def list_tmf8829_ports():
    """Find all COM ports that look like TMF8829 boards."""
    ports = serial.tools.list_ports.comports()
    tmf_ports = []
    for p in ports:
        if "TMF8829" in p.description or "USB Serial" in p.description:
            tmf_ports.append(p.device)
    return tmf_ports

def read_tmf8829(port):
    """Connect to TMF8829, log to CSV, and update shared data."""
    csv_filename = f"tmf8829_{port.replace(':','_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    try:
        print(f"[{port}] Connecting...")
        sensor = TMF882X(port)
        sensor.open()
        sensor.start_measurement()

        with open(csv_filename, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["timestamp", "distances_mm"])

            while True:
                frame = sensor.get_measurement()
                if frame:
                    distances = frame.distances_mm
                    timestamp = datetime.now().isoformat()
                    writer.writerow([timestamp, distances])

                    with lock:
                        sensor_data[port] = distances

                time.sleep(0.05)

    except Exception as e:
        print(f"[{port}] Error: {e}")
    finally:
        try:
            sensor.stop_measurement()
            sensor.close()
        except:
            pass

def animate(i):
    """Update the live plot."""
    plt.cla()
    with lock:
        for port, distances in sensor_data.items():
            plt.plot(distances, label=port)
    plt.xlabel("Pixel Index")
    plt.ylabel("Distance (mm)")
    plt.title("TMF8829 Multi-Board Live Distances")
    plt.legend(loc="upper right")
    plt.grid(True)

if __name__ == "__main__":
    ports = list_tmf8829_ports()
    if not ports:
        print("No TMF8829 boards found.")
    else:
        print(f"Found boards: {ports}")
        threads = []
        for port in ports:
            t = threading.Thread(target=read_tmf8829, args=(port,), daemon=True)
            t.start()
            threads.append(t)

        # Start live plot
        fig = plt.figure()
        ani = animation.FuncAnimation(fig, animate, interval=200)
        try:
            plt.show()
        except KeyboardInterrupt:
            print("Stopping...")