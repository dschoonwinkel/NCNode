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
    h2.cmd("xterm -fg black -bg yellow -geometry 80x24+950+400 -e \"bash ITGRecv.bash; bash\" &")

    time.sleep(3)

    h1.cmd("xterm -fg black -bg cyan -geometry 80x24+950+0 -e \"bash ITGSend12.bash; bash\" &")
    h2.cmd("xterm -fg black -bg yellow -geometry 80x24+0+400 &")



    CLI( net )
    net.stop()

    os.system("killall xterm")
    os.system("killall tcpdump")

if __name__ == '__main__':
    main()
