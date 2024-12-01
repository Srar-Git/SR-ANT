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

# INT config
Enabling INT source for an ingress port
------

INT source functionality is enabled per a switch port. Without this command, it is not possible to perform INT monitoring for the incoming traffic flow even 
it will be added to the INT watchlist. In general it should be done for each switch port where incoming traffic is entering our network. 

```
table_add tb_activate_source activate_source {ingress-port} =>
```
where:
* `ingress-port` - ingress port for which INT source functionality is enabled

Here is example of this command:
```
table_add tb_activate_source activate_source 1 =>
```
This command must be repeated for each ingress port of the switch.

Adding 4-tuple flow to the INT watchlist
------
In order to activate INT monitoring of the traffic flow a INT watch table must contain entry for a given flow. 
The following commands allows us to configure an entry in this table:

```
table_add tb_int_source configure_source {source-ip}&&&(source-ip-bitmask) {destination-ip}&&&(destination-ip-bitmask) 
                                         {source-port}&&&(source-port-bitmask) {destination-port}&&&(destination-port-bitmask) 
                                         => {int-max-hops} {int-hop-metadata-len} {int-hop-instruction-cnt} {int-instruction-bitmap} {table-entry-priority}
```
where:
* `source-ip`, `source-port`, `destination-ip`, `destination-port` defines 4-tuple flow which will be monitored using INT functionality
* `int-max-hops` - how many INT nodes can add their INT node metadata to packets of this flow
* `int-hop-metadata-len` - INT metadata words are added by a single INT node
* `int-hop-instruction-cnt` - how many INT headers must be added by a single INT node
* `int-instruction-bitmap` - instruction_mask defining which information (INT headers types) must added to the packet
* `table-entry-priority` - general priority of entry in match table (not related to INT)

`int-instruction-bitmap` example values:
* 0xFF - all defined INT metadata headers should be added to a flow frame
* 0xCC - INT node must add node id, ingress and egress L1 port ids, ingress and egress timestamps
* 0x0C - INT node must add node id, ingress and egress L1 port ids

Example of command activating INT monitoring for a traffic flow 10.0.1.1:4607 --> 10.0.2.2:8959
```
table_add tb_int_source configure_source 10.0.1.1&&&0xFFFFFFFF 10.0.2.2&&&0xFFFFFFFF 0x11FF&&&0x0000 0x22FF&&&0x0000 => 4 10 8 0xFF 0
```

Enabling INT transit functionality within a switch
------
In order to allow P4 node to perform role of INT transit, INT switch identifier and MTU size must be provided.
The following command enables INT transit functionality for a switch:
```
table_add tb_int_transit configure_transit => {int-node-identifier} {allowed-mtu}
```
where:
* `int-node-identifier` - switch id which is used within INT node metadata
* `allowed-mtu` - layer 3 packet MTU size which must be not exceeded when adding INT metadata to a frame

INT transit functionality must be also configured for switches performing role of INT source and/or INT sink for some their ports. 
To be precise, INT transit functionality is responsible for addition of INT node metadata to a monitored frame.

Here is example of this command:
```
table_add tb_int_transit configure_transit => 1 1500
```

Enabling INT sink for an egress port
------
INT sink functionality is enabled per a switch port. Without this command, it is not possible to perform INT metadata extraction 
and INT reporting for the monitored traffic flow. In general it should be done for each switch port where network traffic is exiting our network. 
```
table_add tb_int_sink configure_sink {egress-port} => {int-reporting-port}
```
where:
* `egress-port` - egress port for which INT sink functionality is enabled
* `int-reporting-port` - switch port number where INT reports should be send out from a switch

Here is example of this command enabling INT sink functionality for egress port 4.
```
table_add tb_int_sink configure_sink 1 => 4
```

Additionally, in order to allow proper working of INT reporting a proper traffic mirroring must be configured:

```
mirroring_add 1 {int-reporting-port}
```
where:
* `int-reporting-port` - switch port number where INT reports should be send out from a switch

Here is example of this command allowing INT reporting using switch port 4.
```
mirroring_add 1 4
```

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
