#! /bin/bash

#/home/daniel/Development/ITGTrafficGen/bin/ITGRecv -Sp 11234
ipaddr=$(ip addr show | grep eth | grep inet | awk -F ' ' '{print $2}' | sed 's/\(.*\)../\1/')
echo $ipaddr
