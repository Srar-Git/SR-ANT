FROM docker.zhai.cm/ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    net-tools \
    iputils-ping \
    iproute2 \
    telnet telnetd \
    iperf \
    iperf3 \
    curl \
    sudo \
    gnupg \
    lsb-release \
    python3-pip \
    sysstat \
    traceroute \
    netcat-traditional \
    tcptraceroute \
    socat \
    iptables \
    libltdl7 \
    wget \
    axel \
    git \
    hping3 \
    mtr \
    rpm \
    gcc \
    flex \
    byacc


RUN wget https://www.tcpdump.org/release/libpcap-1.10.5.tar.xz && \
    tar -xvf libpcap-1.10.5.tar.xz && \
    wget https://www.tcpdump.org/release/tcpdump-4.99.5.tar.xz && \
    tar -xvf tcpdump-4.99.5.tar.xz && \
    cd libpcap-1.10.5 && \
    ./configure && \
    make -j 16&& \
    make install && \
    cd ../tcpdump-4.99.5 && \
   ./configure && \
    make -j 16&& \
    make install && \
    cd ../ && \
    rm -rf libpcap-1.10.5.tar.xz && \
    rm -rf tcpdump-4.99.5.tar.xz && \
    rm -rf libpcap-1.10.5 && \
    rm -rf tcpdump-4.99.5


RUN sudo update-alternatives --config nc

RUN pip3 install scapy

RUN sudo apt-get install apt-transport-https
RUN sudo apt update
RUN sudo apt install -y tcpdump vim
ADD nqa.py /root
ADD sendcustpkt.py /root/

COPY docker-ce_18.06.3_ce_3-0_debian_amd64.deb /root/
RUN dpkg -i /root/docker-ce_18.06.3_ce_3-0_debian_amd64.deb

CMD ["/usr/local/bin/bash"]
