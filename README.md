1. controller run:
`docker run --name controller -dit --privileged --pid='host' --network=host -v /data00/home/pengyufan/PycharmProjects/SR-ANT:/root/ -v /var/run/docker.sock:/var/run/docker.sock controller:latest`

docker run --privileged --net=host --rm -it --name bmv2 -d docker.zhai.cm/p4lang/behavioral-model:latest simple_switch_grpc --log-file switch.log --device-id 1 -i 1@v1 -i 2@v2 -i 4@v3 -i 3@v4 -i 5@v5 --thrift-port 9090 -Ldebug --no-p4 -- --cpu-port 255 --grpc-server-add 0.0.0.0:50001