import pickle
import numpy as np
import sys
# import matplotlib.pyplot as plot

filename = sys.argv[1]
print(filename)

f = open(filename, 'rb')

times = pickle.load(f)

times_order = ["Streamreader received",
"Encapsulator processed0",
"Encapsulator processed1",
"Encapsulator processed2",
"Enqueuer processed",
"AddPacketToOutputQueue processed",
"checkDispatch processed",
"Packet dispatcher send",
"Encoder processed",
"AddACKs processed1",
"AddACKs processed2",
"AddACKs processed3",
"AddACKs processed4",
"AddACKs processed",
"Transmitter send"]


recv_times = np.array(times['Streamreader received'])
# print(recv_times)
transmitter_send_times = np.array(times["Transmitter send"])

for i in range(1,len(times_order)):
    if len(times[times_order[i]]) == len(times[times_order[i-1]]):
        times_step = np.array(times[times_order[i]]) - np.array(times[times_order[i-1]])
        print("%s - %s:" % (times_order[i], times_order[i-1]))
        # print("%s" % (times_step*1000))
        print(np.mean(times_step)*1000)

# durations = transmitter_send_times - recv_times
# print("Total durations", durations * 1000)
# print(np.mean(durations) * 1000)

# plot.figure()
# plot.grid('on', 'both')
# plot.hist(durations*1000, range(100))
# plot.xlabel('Inter receive time [ms]')
# plot.savefig('exec_times_10.0.0.1_plot.pdf')
# plot.show()


