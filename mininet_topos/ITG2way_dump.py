#!/usr/bin/python

import re
import sys
import imp
import os

from mininet.cli import CLI
from mininet.log import setLogLevel, info, error
from mininet.net import Mininet
from mininet.topolib import TreeTopo
from mininet.node import Controller, RemoteController
import time

def main():

    setLogLevel("info")
    info( '*** Creating network\n' )
    net = Mininet( topo=TreeTopo( depth=1, fanout=2 ), controller=RemoteController )
    h1 = net.hosts[0]
    h2 = net.hosts[1]
    net.start()

    f = open("network_layout.net", 'w')
    # f.write("[IP]\n")
    f.write("%s %s\n" % (h1.IP(), h1.MAC()))
    f.write("%s %s\n" % (h2.IP(), h2.MAC()))
    # f.write("[Links]")
    # for link in net.links:
    #     f.write("%s\n" % link)
    f.close()

    # h1.cmd("sudo python ../nc_runner2.py &")
    # h2.cmd("sudo python ../nc_runner2.py &")
    h1.cmd("tcpdump -i lo -s 65535 -w dump_sender.pcap &")
    h1.cmd("tcpdump -i h1-eth0 -s 65535 -w dump_sender_netw.pcap &")
    h2.cmd("tcpdump -i lo -s 65535 -w dump_receiver.pcap &")


    h1.cmd("xterm -fg black -bg cyan -geometry 80x24+450+0 -e \"python3 -m cProfile -o h1_profile.txt nc_runner2.py; bash \" &")
    # h1.cmd("xterm -fg black -bg cyan -geometry 80x24+450+0 -e \"python nc_runner2_profile.py; bash \" &")
    h2.cmd("xterm -fg black -bg yellow -geometry 80x24+450+400 -e \"python3 -m cProfile -o h2_profile.txt nc_runner2.py; bash \" &")
    # h2.cmd("xterm -fg black -bg yellow -geometry 80x24+450+400 -e \"python nc_runner2_profile.py; bash \" &")
    h2.cmd("xterm -fg black -bg yellow -geometry 80x12+950+400 -e \"bash ITGRecv_dump.bash; bash\" &")
    h1.cmd("xterm -fg black -bg cyan -geometry 80x12+950+250 -e \"bash ITGRecv_dump.bash; bash\" &")

    time.sleep(3)

    h1.cmd("xterm -fg black -bg cyan -geometry 80x12+950+0 -e \"bash ITGSend.bash 10.0.0.1 10.0.0.2 10002; bash\" &")
    h2.cmd("xterm -fg black -bg yellow -geometry 80x12+950+550 -e \"bash ITGSend.bash 10.0.0.2 10.0.0.1 10001; bash\" &")
    # h2.cmd("xterm -fg black -bg yellow -geometry 80x24+0+400 &")

    time.sleep(4)
    h1.cmd("killall -signal SIGINT ITGRecvDump")
    h1.cmd("killall -signal SIGINT python3")
    h1.cmd("killall tcpdump")

    CLI( net )
    net.stop()

    # os.system("killall tcpdump")
    # os.system("killall -signal SIGINT ITGRecvDump")
    # os.system("killall -signal SIGINT python3")
    time.sleep(0.1)
    os.system("killall -signal SIGINT xterm")
    os.system("echo \"cmp 10.0.0.1\"")
    os.system("cmp -n 300000 data_files/random1M.txt data_files/receiverdump_10.0.0.1.bin")
    os.system("echo \"cmp 10.0.0.2\"")
    os.system("cmp -n 300000 data_files/random1M.txt data_files/receiverdump_10.0.0.2.bin")
    os.system("ls -l data_files/")
    os.system("python3 parse_exec_times.py exec_times_10.0.0.1.log")
    os.system("ITGDec logs/sender_10.0.0.1.log | tail -n 16")
    os.system("ITGDec logs/receiver_10.0.0.1.log | tail -n 16")

if __name__ == '__main__':
    main()
