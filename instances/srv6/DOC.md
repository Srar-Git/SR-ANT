# topo
## graph
````
   h1--------s1----------s2-----------s3-----------s4---------h2
   eth0  eth0 eth1   eth0 eth1    eth0 eth1     eth0 eth1    eth0
````
## ip
- h1 `1::1/128`
- h2 `2::2/128`
## links
- h1-s1 | intfNames: h1-eth0-s1-eth0 | addrs: 10:00:00:00:00:01-00:00:00:00:01:01
- s1-s2 | intfNames: s1-eth1-s2-eth0 | addrs: 00:00:00:00:01:02-00:00:00:00:02:01
- s2-s3 | intfNames: s2-eth1-s3-eth0 | addrs: 00:00:00:00:02:02-00:00:00:00:03:01
- s3-s4 | intfNames: s2-eth1-s4-eth0 | addrs: 00:00:00:00:02:02-00:00:00:00:04:01
- s4-h2 | intfNames: s4-eth1-h2-eth0 | addrs: 00:00:00:00:04:02-20:00:00:00:00:01

# sid list
- s1: `A1:11::11/128` as the source node
- s2: not support srv6
- s3: `A3:33::33/128` as the transit node
- s4: `A4:44::44/128` as the end node

# run time
warn: this run time only for h1 -> h2, not h2 -> h1
## s1
````
# check if the mac is local host ingress interface mac
local_mac_table NoAction 00:00:00:00:01:01 => 
# if s1 as the end node, do end
local_sid_table end A1:11::11/128 => 
# if s1 as the source node, do insert sids
transit_table insert_segment_list_3 2::2/128 => A2:22::22 A3:33::33 2::2
# transit action s1 -> s2, s1 port 0 egress, dst mac is s2 eth0
routing_v6_table set_next_hop A2:22::22/128 => 00:00:00:00:02:01 1
````
## s2
```
local_mac_table NoAction 00:00:00:00:02:01 => 
routing_v6_table set_next_hop A3:33::33/128 => 00:00:00:00:03:01 1
routing_v6_table set_next_hop 1::1/128 => 10:00:00:00:00:01 0
````
## s3
````
local_mac_table NoAction 00:00:00:00:03:01 => 
local_sid_table end A3:33::33/128 => 
routing_v6_table set_next_hop A2:22::22/128 => 20:00:00:00:00:01 1
````
# send packet
`python3 pkt_manager.py eth0 1::1 2::2 "qqq"`
`python3 sniff.py h2-eth0`
