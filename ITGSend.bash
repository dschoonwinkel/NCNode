#! /bin/bash

#addr="10.0.0.2"
addr1=$1
addr2=$2
port2=$3

#/home/daniel/Development/ITGTrafficGen/bin/ITGSend -T UDP -a 10.0.0.2 -rp 10002 -C 100 -c 1000000 -t 20000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234

#/home/daniel/Development/ITGTrafficGen/bin/ITGSend -T UDP -a $addr -rp 10002 -C 100 -c 10 -t 20000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234
ITGSend -T UDP -a 127.0.0.1 -rp $port2 -C 500 -c 1200 -t 2000 -x ./logs/receiver_$addr1.log -l ./logs/sender_$addr1.log -Sda $addr2 -Sdp 11234 -p 2 -Fp ./data_files/random1M.txt
#/home/daniel/Development/ITGTrafficGen/bin/ITGSend -T UDP -a 127.0.0.1 -rp 10002 -C 100 -c 20 -t 20000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234
#/home/daniel/Development/ITGTrafficGen/bin/ITGSend -T UDP -a 127.0.0.1 -rp 10002 -C 200 -c 20 -z 200 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234





