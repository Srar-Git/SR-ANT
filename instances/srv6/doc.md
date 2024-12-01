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
table_add sr_source_table insert_srh 0 => A3:33::33 A4:44::44 2::2
# the ipv6 forward
table_add ipv6_lpm_table forward A3:33::33/128 => 1 00:00:00:00:01:02
````
## s2
```
table_add ipv6_lpm_table forward A3:33::33/128 => 1 00:00:00:00:02:02
````
## s3
````
table_add sr_end_table end A3:33::33 =>
table_add ipv6_lpm_table forward A4:44::44/128 => 1 00:00:00:00:03:02
````
## s4
````
table_add sr_end_table srv6_pop A4:44::44 =>
table_add ipv6_lpm_table forward 2::2/128 => 1 00:00:00:00:04:02
````
# send packet
`python3 pkt_manager.py eth0 1::1 2::2 "qqq"`

# sniff packet
`python3 sniff.py h2-eth0`
