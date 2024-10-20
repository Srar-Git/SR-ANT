# 使用 Ubuntu 22.04 作为基础镜像
FROM m.daocloud.io/ubuntu:22.04

# 设置环境变量，避免在安装时交互
ENV DEBIAN_FRONTEND=noninteractive

# 更新包列表并安装必要依赖项
RUN apt-get update && apt-get install -y \
    git \
    cmake \
    build-essential \
    automake \
    libtool \
    libgmp-dev \
    libpcap-dev \
    libboost-dev \
    libboost-program-options-dev \
    libboost-system-dev \
    libboost-filesystem-dev \
    libevent-dev \
    flex \
    bison \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    python-is-python3 \
    libfl-dev \
    llvm \
    clang \
    libgc-dev \
    wget \
    curl \
    iproute2 \
    iputils-ping \
    net-tools \
    sudo \
    vim \
    && apt-get clean

# 安装 protobuf
RUN apt-get install -y autoconf automake libtool curl make g++ unzip
RUN git clone https://github.com/protocolbuffers/protobuf.git /root/protobuf
WORKDIR /root/protobuf
RUN git submodule update --init --recursive
RUN ./autogen.sh
RUN ./configure
RUN make -j4
RUN make check
RUN sudo make install
RUN sudo ldconfig

# 安装 gRPC
WORKDIR /root
RUN git clone --recurse-submodules -b v1.41.1 https://github.com/grpc/grpc
WORKDIR /root/grpc
RUN git submodule update --init
RUN mkdir -p cmake/build
WORKDIR /root/grpc/cmake/build
RUN cmake ../..
RUN make -j4
RUN sudo make install
RUN sudo ldconfig

# 设置工作目录
WORKDIR /root

# 克隆并安装 behavioral-model（bmv2）
RUN git clone https://github.com/p4lang/behavioral-model.git
WORKDIR /root/behavioral-model
RUN git submodule update --init --recursive \
    && ./install_deps.sh \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && ldconfig

# 安装 simple_switch_grpc
WORKDIR /root/behavioral-model/targets/simple_switch_grpc
RUN ./install_grpc_deps.sh \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install

# 返回根目录
WORKDIR /root

# 克隆并安装 P4C（P4 编译器）
RUN git clone https://github.com/p4lang/p4c.git
WORKDIR /root/p4c
RUN git submodule update --init --recursive \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make -j4 \
    && make install

# 克隆并安装 PI (Protocol Independent Switch Architecture)
WORKDIR /root
RUN git clone https://github.com/p4lang/PI.git
WORKDIR /root/PI
RUN git submodule update --init --recursive \
    && ./autogen.sh \
    && ./configure \
    && make \
    && make install \
    && ldconfig

# 安装 thrift
RUN apt-get install -y thrift-compiler

# 清理无用文件
RUN apt-get autoremove -y && apt-get clean

# 设置默认工作目录
WORKDIR /root

# 默认启动命令，进入 bash
CMD ["bash"]
