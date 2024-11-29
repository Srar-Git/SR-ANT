import argparse
import sys
import socket
import random
import struct

from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IPv6, UDP


def get_if(name):
    iface = None  # "h1-eth0"
    for i in get_if_list():
        if name in i:
            iface = i
            break
    if not iface:
        print(f"Cannot find interface {name}")
        exit(1)
    return iface


def main():
    if len(sys.argv) < 3:
        print
        'pass 4 arguments: <interface> <source ip> <destination ip> "<message>"'
        exit(1)
    interface_name = sys.argv[1]
    saddr = sys.argv[2]
    addr = sys.argv[3]
    iface = get_if(interface_name)

    print("sending on interface %s to %s" % (iface, str(addr)))
    # 注意，这里的目的地址是转发给s1的目的mac地址
    pkt = Ether(src=get_if_hwaddr(iface), dst='00:00:00:00:01:01') / IPv6(src=saddr, dst=addr) / UDP(dport=4321, sport=1234) / sys.argv[4]
    pkt.show2()
    sendp(pkt, iface=iface, verbose=False)


if __name__ == '__main__':
    main()