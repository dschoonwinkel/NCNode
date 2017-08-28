

f = open("ITGRecv_results.txt", 'r')

contents = f.readlines()

bitrates = list()
packetrates = list()
max_bitrate = 0
max_packet_rate = 0

for line in contents:
    if line.find("Average bitrate") != -1:
        splits = line.split(" ")
        # print("Avg bitrate value: ", splits[-2])
        bitrates.append(float(splits[-2]))

    if line.find("Average packet rate") != -1:
        splits = line.split(" ")
        # print("Avg bitrate value: ", splits[-2])
        packetrates.append(float(splits[-2]))

bitrates.sort()
packetrates.sort()

print("Avg bitrates: ", bitrates)
print("Avg packetrates: ", packetrates)

f.close()