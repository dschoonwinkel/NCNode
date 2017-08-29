#!/usr/bin/python

"""
This example shows how to create an empty Mininet object
(without a topology object) and add nodes to it manually.
"""

from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os, time

def clean_up_aux_files():
    os.system("rm data_files/receiverdump_*.bin")
    os.system("rm coding1_profile.txt")
    os.system("rm profiling/h*_profile.txt")
    os.system("rm exec_times_*.log")
    os.system("rm logs/sender_*.log")
    os.system("rm logs/receiver_*.log")
    os.system("rm pcap_files/*_dump.pcap")
    os.system("rm logs/config.log")

def codingNet():

    "Create an empty network and add nodes to it."
    net = Mininet( controller=RemoteController, autoSetMacs=True )

    info( '*** Adding controller\n' )
    net.addController( 'c0' )

    info( '*** Adding hosts\n' )
    h1 = net.addHost( 'h1', ip='10.0.0.1' )
    h2 = net.addHost( 'h2', ip='10.0.0.2' )
    coding1 = net.addHost('coding1', ip='10.0.1.1', mac='00:00:ff:00:00:01')

    info( '*** Adding switch\n' )
    s1 = net.addSwitch( 's1' )

    info( '*** Creating links\n' )
    net.addLink( h1, s1 )
    net.addLink( h2, s1 )
    net.addLink( coding1, s1 )

    info( '*** Starting network\n')
    net.start()


    # TODO: This steps sets up nexthops: By specifying the coding1 MAC here, all ACKs will be done by coding1.
    # TODO: This should really be done better, figure out a way to describe topologies better
    f = open("network_layout.net", 'w')
    # f.write("[IP]\n")
    f.write("%s %s\n" % (h1.IP(), coding1.MAC()))
    f.write("%s %s\n" % (h2.IP(), coding1.MAC()))
    f.write("%s %s\n" % (coding1.IP(), coding1.MAC()))
    # f.write("[Links]")
    # for link in net.links:
    #     f.write("%s\n" % link)
    f.close()

    # h1.cmd("tcpdump -i lo -s 65535 -w dump_sender.pcap &")
    # h2.cmd("tcpdump -i lo -s 65535 -w dump_receiver.pcap &")
    h1.cmd("tcpdump -i h1-eth0 -s 65535 -w pcap_files/h1_dump.pcap &")
    h2.cmd("tcpdump -i h2-eth0 -s 65535 -w pcap_files/h2_dump.pcap &")
    coding1.cmd("tcpdump -i coding1-eth0 -s 65535 -w pcap_files/coding1_dump.pcap &")

    h1.cmd(
        "xterm -fg black -bg cyan -geometry 80x24+450+0 -e \"python3 -m cProfile -o profiling/h1_profile.txt nc_runner2.py; bash \" &")
    h2.cmd(
        "xterm -fg black -bg yellow -geometry 80x24+450+400 -e \"python3 -m cProfile -o profiling/h2_profile.txt nc_runner2.py; bash \" &")

    coding1.cmd(
        "xterm -fg black -bg red -geometry 80x24+450+600 -e \"python3 -m cProfile -o profiling/coding1_profile.txt nc_codinghost.py; bash \" &")

    h2.cmd("xterm -fg black -bg yellow -geometry 80x12+950+400 -e \"bash ITGRecv_dump.bash; bash\" &")
    h1.cmd("xterm -fg black -bg cyan -geometry 80x12+950+250 -e \"bash ITGRecv_dump.bash; bash\" &")

    time.sleep(2)

    h1.cmd("xterm -fg black -bg cyan -geometry 80x12+950+0 -e \"bash ITGSend.bash 10.0.0.1 10.0.0.2 10002 ; bash\" &")
    h2.cmd(
        "xterm -fg black -bg yellow -geometry 80x12+950+550 -e \"bash ITGSend.bash 10.0.0.2 10.0.0.1 10001 ; bash\" &")


    time.sleep(4)
    # h1.cmd("killall -signal SIGINT ITGRecvDump")
    # h1.cmd("killall -signal SIGINT python3")
    h1.cmd("killall tcpdump")

    info( '*** Running CLI\n' )
    CLI( net )

    info( '*** Stopping network' )
    net.stop()

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
    setLogLevel( 'info' )
    clean_up_aux_files()
    codingNet()
