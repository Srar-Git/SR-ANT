/*
 * Copyright 2020-2021 PSNC, FBK
 *
 * Author: Damian Parniewicz, Damu Ding
 *
 * Created in the GN4-3 project.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "include/headers.p4"

control Srv6Impl(inout headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    action drop(){
    	mark_to_drop(standard_metadata);
    }

    action insert_srh_num(bit<8> num_segments){
        hdr.srh.setValid();
        hdr.srh.nextHdr = hdr.ipv6.nextHdr;
        hdr.srh.hdrExtLen = num_segments * 2;
        hdr.srh.routingType = 4;
        hdr.srh.segmentLeft = num_segments - 1;
        hdr.srh.lastEntry = num_segments - 1;
        hdr.srh.flags = 0;
        hdr.srh.tag = 0;
        hdr.ipv6.nextHdr = l4_proto_SRV6;
    }

    action insert_srh(ipv6_addr_t s1, ipv6_addr_t s2, ipv6_addr_t s3){
        hdr.ipv6.dstAddr = s1;
        hdr.ipv6.payloadLen = hdr.ipv6.payloadLen + 56;
        insert_srh_num(3);
        hdr.segment_list[0].setValid();
        hdr.segment_list[0].sid = s3;
        hdr.segment_list[1].setValid();
        hdr.segment_list[1].sid = s2;
        hdr.segment_list[2].setValid();
        hdr.segment_list[2].sid = s1;
    }
    action dec_ttl() {
        hdr.ipv6.hopLimit = hdr.ipv6.hopLimit - 1;
    }

    action forward(port_t port, mac_addr_t dst_mac) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dst_mac;
    }

    action end() {
        hdr.srh.segmentLeft = hdr.srh.segmentLeft - 1;
        hdr.ipv6.dstAddr = local_metadata.next_sid;
        //hdr.ipv6.dst_addr = hdr.segment_list[hdr.srh.last_entry - hdr.srh.segment_left].sid;
    }

    action srv6_pop() {
        end();
        hdr.ipv6.nextHdr = hdr.srh.nextHdr;
        bit<16> srh_size = (((bit<16>)hdr.srh.lastEntry + 1) << 4) + 8;
        hdr.ipv6.payloadLen = hdr.ipv6.payloadLen - srh_size;
        hdr.srh.setInvalid();
        hdr.segment_list[0].setInvalid();
        hdr.segment_list[1].setInvalid();
        hdr.segment_list[2].setInvalid();
    }

    table sr_source_table {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            insert_srh;
            NoAction;
        }
        size = 256;
    }

    table sr_end_table {
        key = {
            hdr.ipv6.dstAddr: exact;
        }
        actions = {
            end;
            srv6_pop;
            NoAction;
        }
        size = 256;
    }

    table ipv6_lpm_table {
        key = {
            hdr.ipv6.dstAddr: lpm;
        }
        actions = {
            forward;
            drop;
        }
        size = 1024;
    }

    apply {
        sr_source_table.apply();

        if (hdr.ipv6.isValid()) {
            dec_ttl();
            sr_end_table.apply();
            if (hdr.ipv6.hopLimit == 0) {
                drop();
            } else {
                ipv6_lpm_table.apply();
            }
        }
    }


}