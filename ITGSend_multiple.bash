#! /bin/bash

#ITGSend -T UDP -a 127.0.0.1 -rp 10002 -C 100 -c 10 -t 20000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234
#ITGSend -T UDP -a 127.0.0.1 -rp 10002 -C 100 -c 20 -t 20000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234
#ITGSend -T UDP -a 127.0.0.1 -rp 10002 -C 200 -c 20 -z 200 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234

addr="10.0.0.2"
packet_sizes=(1000 10000 1000000)
packet_rates=(10 1000 100000)

for packet_size in ${packet_sizes[@]}
do

    for packet_rate in ${packet_rates[@]}
    do

        for ((i=0; i < 3; i++))
        do
            echo "Run "$i" packet size "$packet_size" packet rate "$packet_rate >> ITGRecv_results.txt
            /home/daniel/Development/ITGTrafficGen/bin/ITGSend -T UDP -a $addr -rp 10002 -C $packet_rate -c $packet_size -t 20000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234
            ITGDec receiver.log | grep "Average bitrate" | head -n 1 >> ITGRecv_results.txt
            ITGDec receiver.log | grep "Average packet rate" | head -n 1 >> ITGRecv_results.txt

        done
       echo "\n" >> ITGRecv_results.txt
    done
    echo "\n" >> ITGRecv_results.txt
done