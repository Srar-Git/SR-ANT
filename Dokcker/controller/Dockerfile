# 使用 Ubuntu 22.04 作为基础镜像
FROM cnet:latest

COPY . /root/
RUN ls /root/
RUN sed -i 's/privileged=False/privileged=True/' /containernet/mininet/node.py

RUN python3 -m pip install flask flask_restful marshmallow IPy scapy textfsm -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

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
    vim \
    tcpdump \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev


RUN sudo update-alternatives --config nc
RUN pip3 install scapy setuptools_rust cryptography==3.3.2 -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple


CMD ["python3", "/root/main.py", " > /var/log/controller.log 2>&1"]

