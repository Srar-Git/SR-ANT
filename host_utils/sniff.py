from scapy.all import *

def packet_callback(packet):
    print(packet.summary())

# 开始嗅探
def begin_sniff(name):
    sniff(iface=name, prn=packet_callback)

def main():
    if len(sys.argv) < 1:
        print('pass 1 arguments: <interface>')
        exit(1)
    interface_name = sys.argv[1]
    begin_sniff(interface_name)

if __name__ == '__main__':
    main()
