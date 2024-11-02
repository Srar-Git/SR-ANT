# 使用 Ubuntu 22.04 作为基础镜像
FROM m.daocloud.io/ubuntu:22.04

RUN apt-get update
RUN apt-get install -y \
    net-tools \
    cmake \
    curl \
    sudo \
    gnupg \
    lsb-release \
    python3-pip \
    sysstat \
    iptables \
    libltdl7 \
    wget \
    git
RUN apt-get install -y \
    bash

# 设置环境变量
ENV DISTRIB_RELEASE 22.04

# 添加 P4C 的源
RUN echo "deb http://download.opensuse.org/repositories/home:/p4lang/xUbuntu_${DISTRIB_RELEASE}/ /" > /etc/apt/sources.list.d/home:p4lang.list && \
    curl -fsSL https://download.opensuse.org/repositories/home:p4lang/xUbuntu_${DISTRIB_RELEASE}/Release.key | gpg --dearmor > /etc/apt/trusted.gpg.d/home_p4lang.gpg && \
    apt-get update && \
    apt-get install -y p4lang-p4c


#RUN git clone https://github.com/p4lang/p4c.git
#WORKDIR /root/p4c
#RUN git submodule update --init --recursive \
#    && mkdir build \
#    && cd build \
#    && cmake .. \
#    && make -j4 \
#    && make install

# 默认启动命令，进入 bash
CMD ["bash"]
