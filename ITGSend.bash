#! /bin/bash

ITGSend -T UDP -a 127.0.0.1 -rp 10002 -C 20 -c 20 -t 1000 -x receiver.log -l sender.log -Sda 10.0.0.2 -Sdp 11234