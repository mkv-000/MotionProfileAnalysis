import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import struct

class ProcessedData:
    def __init__(self):
        self.timestamp = []
        self.data = []

class Node:
    def __init__(self):
        self.actualTorque = ProcessedData()
        self.controlEffort = ProcessedData()
        self.desiredPosition = ProcessedData()
        self.actualPosition = ProcessedData()
        self.desiredSpeed = ProcessedData()
        self.actualSpeed = ProcessedData()

nodeList = [Node() for _ in range(4)]

def parse_channel(bytesIn, fmt):
    byte_length = struct.calcsize(fmt)
    return struct.unpack(fmt, bytes.fromhex(''.join(bytesIn[:byte_length * 2])))

def get_channel_and_node(pdoId):
    channel_map = {
        '18': 1,
        '28': 2,
        '38': 3,
        '48': 4
    }
    return channel_map.get(pdoId[:2], 0), int(pdoId[2:]) if pdoId[2:].isdigit() else 0

with open('logs/unloaded.log', 'r', encoding='utf-8-sig') as file:
    lines = file.readlines()

for line in lines:
    logItems = line.split()
    ts = datetime.strptime(logItems[1].rstrip(")"), "%H:%M:%S.%f")
    channel, node = get_channel_and_node(logItems[3])

    byteData = logItems[5:13]
    if channel == 1:
        actualTorque = parse_channel(byteData[2:4], '<h')[0]
        controlEffort = parse_channel(byteData[4:8], '<i')[0]
        nodeList[node - 1].actualTorque.timestamp.append(ts)
        nodeList[node - 1].controlEffort.timestamp.append(ts)
        nodeList[node - 1].actualTorque.data.append(actualTorque * 1000)
        nodeList[node - 1].controlEffort.data.append(controlEffort)
    elif channel == 2:
        desiredPosition = parse_channel(byteData[:4], '<i')[0]
        actualPosition = parse_channel(byteData[4:8], '<i')[0]
        nodeList[node - 1].desiredPosition.timestamp.append(ts)
        nodeList[node - 1].actualPosition.timestamp.append(ts)
        nodeList[node - 1].desiredPosition.data.append(desiredPosition)
        nodeList[node - 1].actualPosition.data.append(actualPosition)
    elif channel == 3:
        desiredSpeed = parse_channel(byteData[:4], '<i')[0]
        actualSpeed = parse_channel(byteData[4:8], '<i')[0]
        nodeList[node - 1].desiredSpeed.timestamp.append(ts)
        nodeList[node - 1].actualSpeed.timestamp.append(ts)
        nodeList[node - 1].desiredSpeed.data.append(desiredSpeed)
        nodeList[node - 1].actualSpeed.data.append(actualSpeed)


drive1 = nodeList[0]
drive2 = nodeList[1]
drive3 = nodeList[2]
drive4 = nodeList[3]

# Calculate the delta (difference) between desired and actual positions for each drive
drive1_delta_position = np.array(drive1.desiredPosition.data) - np.array(drive1.actualPosition.data)
drive2_delta_position = np.array(drive2.desiredPosition.data) - np.array(drive2.actualPosition.data)
drive3_delta_position = np.array(drive3.desiredPosition.data) - np.array(drive3.actualPosition.data)
drive4_delta_position = np.array(drive4.desiredPosition.data) - np.array(drive4.actualPosition.data)

# Calculate total torque
min_length_torque = min(len(drive1.actualTorque.data), len(drive2.actualTorque.data), len(drive3.actualTorque.data), len(drive4.actualTorque.data))
drive1.actualTorque.data = drive1.actualTorque.data[:min_length_torque]
drive2.actualTorque.data = drive2.actualTorque.data[:min_length_torque]
drive3.actualTorque.data = drive3.actualTorque.data[:min_length_torque]
drive4.actualTorque.data = drive4.actualTorque.data[:min_length_torque]
totalTorque = np.add(drive1.actualTorque.data, drive2.actualTorque.data)
totalTorque = np.add(totalTorque, drive3.actualTorque.data)
totalTorque = np.add(totalTorque, drive4.actualTorque.data)

tTT = drive2.actualTorque.timestamp[:min_length_torque]

plt.style.use('ggplot')
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Plotting data for Drive 1
ax1 = axes[0]
ax1.plot(mdates.date2num(drive1.desiredPosition.timestamp), drive1_delta_position, linestyle='-', label="Drive 1 Delta Position")
ax1.set_xlabel("Time (H:M:S)", fontsize=12)
ax1.set_ylabel("Delta Position (mm)", fontsize=12)
ax1.set_title("Delta Position and Total Torque Analysis for Drive 1", fontsize=16)
ax1.set_ylim([-50000, 250000])

ax1_twin = ax1.twinx()
ax1_twin.plot(mdates.date2num(tTT), totalTorque, linestyle='-', color='gray', label="Total Torque")
ax1_twin.set_ylabel("Total Torque", fontsize=12)
ax1_twin.legend(loc='upper right')

# Plotting data for Drive 2
ax2 = axes[1]
ax2.plot(mdates.date2num(drive2.desiredPosition.timestamp), drive2_delta_position, linestyle='-', label="Drive 2 Delta Position")
ax2.set_xlabel("Time (H:M:S)", fontsize=12)
ax2.set_ylabel("Delta Position(mm)", fontsize=12)
ax2.set_title("Delta Position and Total Torque Analysis for Drive 2", fontsize=16)
ax2.set_ylim([-50000, 250000])

ax2_twin = ax2.twinx()
ax2_twin.plot(mdates.date2num(tTT), totalTorque, linestyle='-', color='gray', label="Total Torque")
ax2_twin.set_ylabel("Total Torque", fontsize=12)
ax2_twin.legend(loc='upper right')

# Plotting data for Drive 3
ax3 = axes[2]
ax3.plot(mdates.date2num(drive3.desiredPosition.timestamp), drive3_delta_position, linestyle='-', color='orange', label="Drive 3 Delta Position")
ax3.set_xlabel("Time (H:M:S)", fontsize=12)
ax3.set_ylabel("Delta Position(mm)", fontsize=12)
ax3.set_title("Delta Position and Total Torque Analysis for Drive 3", fontsize=16)
ax3.set_ylim([-50000, 250000])

ax3_twin = ax3.twinx()
ax3_twin.plot(mdates.date2num(tTT), totalTorque, linestyle='-',  color='gray', label="Total Torque")
ax3_twin.set_ylabel("Total Torque", fontsize=12)
ax3_twin.legend(loc='upper right')


# Customize the date format on the X-axis
for ax in [ax1, ax2, ax3]:
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    ax.grid(True)

plt.tight_layout()
plt.show()
