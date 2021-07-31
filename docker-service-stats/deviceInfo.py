import socket
import sys
import platform
import psutil
import subprocess
import json
import os
from time import sleep


def get_info():
    monitor_data = {}
    # Get data from script
    cmd = "sh ./tool/info.sh"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    data = str(output)[2:-1].replace("\\n", "")
    data = data.split("|||")
    # Input data
    monitor_data["hostname"] = socket.gethostname()
    monitor_data["memory"] = psutil.virtual_memory().percent
    monitor_data["swap"] = psutil.swap_memory().percent
    monitor_data["cpu"] = psutil.cpu_percent()
    monitor_data["system-platform"] = sys.platform
    monitor_data["machine"] = platform.machine()
    monitor_data["release"] = platform.release()
    monitor_data["cpu-num"] = str(psutil.cpu_count())

    # Get IP Address
    cmd = "hostname -I | awk '{print $1}'"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    monitor_data["IP"] = str(output).split("\\n")[0][2:]

    # Get Disk Data
    cmd = "sh ./tool/disk.sh"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()
    data = str(output)[2:-1]
    data = data.split("|||")[1:]
    DiskData = {}
    for row in data:
        try:
            col = row.split("||")
            DiskData[col[0].replace(" ", "")] = {"Used": int(
                col[1]), "Available": int(col[2]), "percent": col[3].replace(" ", "")}
        except:
            continue
    monitor_data["Disk"] = DiskData
    sleep(2)
    with open('./monitor_data.json', 'w') as data:
        json.dump(monitor_data, data)

    return monitor_data

if __name__ == '__main__':
    get_info()
