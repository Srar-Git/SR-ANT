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

error
{
	INTShimLenTooShort,
	INTVersionNotSupported
}


parser ParserImpl(packet_in packet,
                  out headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    state start {
       transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            ETH_TYPE_IPV4: parse_ipv4;
            ETH_TYPE_IPV6: parse_ipv6;
            // 16w0x800: parse_ipv4;
            default: accept;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        meta.layer34_metadata.ip_src = hdr.ipv4.srcAddr;
        meta.layer34_metadata.ip_dst = hdr.ipv4.dstAddr;
        meta.layer34_metadata.ip_ver = 8w4;
        meta.layer34_metadata.dscp = hdr.ipv4.dscp;
        transition select(hdr.ipv4.protocol) {
            8w0x11: parse_udp;
            8w0x6: parse_tcp;
            default: accept;
        }
    }
    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        meta.layer34_metadata.ip_ver = hdr.ipv6.nextHdr;
        meta.layer34_metadata.ip_src = hdr.ipv6.srcAddr;
        meta.layer34_metadata.ip_dst = hdr.ipv6.dstAddr;
        meta.layer34_metadata.ip_ver = 8w6;
        meta.layer34_metadata.dscp = hdr.ipv6.trafficClass[7:2];
        transition select(hdr.ipv6.nextHdr) {
            l4_proto_TCP: parse_tcp;
            l4_proto_UDP: parse_udp;
            l4_proto_SRV6: parse_srv6;
            default: accept;
        }
    }

    state parse_srv6 {
        packet.extract(hdr.srh);
        transition parse_segment_list;
    }

    state parse_segment_list {
        packet.extract(hdr.segment_list.next);
        bool next_sid = (bit<32>)hdr.srh.segment_left - 1 == (bit<32>)hdr.segment_list.lastIndex;
        transition select(next_sid){
            true: mark_next_sid;
            default: check_last_sid;
        }
    }

    state mark_next_sid{
        local_metadata.next_sid = hdr.segment_list.last.sid;
        transition check_last_sid;
    }

    state check_last_sid {
        bool last_sid = (bit<32>)hdr.srh.last_entry == (bit<32>)hdr.segment_list.lastIndex;
        transition select(last_sid){
            true: parse_srv6_next_hdr;
            false: parse_segment_list;
        }
    }

    state parse_srv6_next_hdr{
        transition select(hdr.srh.next_hdr){
            l4_proto_TCP: parse_tcp;
            l4_proto_UDP: parse_udp;
            default: accept;
        }
    }

    state parse_tcp {
        packet.extract(hdr.tcp);
        meta.layer34_metadata.l4_src = hdr.tcp.srcPort;
        meta.layer34_metadata.l4_dst = hdr.tcp.dstPort;
        meta.layer34_metadata.l4_proto = 8w0x6;
        transition select(meta.layer34_metadata.dscp) {
            IPv4_DSCP_INT: parse_int;
            default: accept;
        }
    }
    state parse_udp {
        packet.extract(hdr.udp);
        meta.layer34_metadata.l4_src = hdr.udp.srcPort;
        meta.layer34_metadata.l4_dst = hdr.udp.dstPort;
        meta.layer34_metadata.l4_proto = 8w0x11;
        transition select(meta.layer34_metadata.dscp, hdr.udp.dstPort) {
            (6w0x20 &&& 6w0x3f, 16w0x0 &&& 16w0x0): parse_int;
            default: accept;
        }
    }
    state parse_int {
        packet.extract(hdr.int_shim);
        /*verify(hdr.int_shim.len >= 3, error.INTShimLenTooShort);*/
        packet.extract(hdr.int_header);
        // DAMU: warning (from TOFINO): Parser "verify" is currently unsupported
        /*verify(hdr.int_header.ver == INT_VERSION, error.INTVersionNotSupported);*/
        transition accept;
    }
}


control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        // raport headers
        packet.emit(hdr.report_ethernet);
        packet.emit(hdr.report_ipv4);
        packet.emit(hdr.report_udp);
        packet.emit(hdr.report_fixed_header);

        // original headers
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv6);
        packet.emit(hdr.udp);
        packet.emit(hdr.tcp);
        packet.emit(hdr.srh);
        packet.emit(hdr.segment_list);

        // INT headers
        packet.emit(hdr.int_shim);
        packet.emit(hdr.int_header);

        // local INT node metadata
        packet.emit(hdr.int_switch_id);     //bit 1
        packet.emit(hdr.int_port_ids);       //bit 2
        packet.emit(hdr.int_hop_latency);   //bit 3
        packet.emit(hdr.int_q_occupancy);  // bit 4
        packet.emit(hdr.int_ingress_tstamp);  // bit 5
        packet.emit(hdr.int_egress_tstamp);   // bit 6
        packet.emit(hdr.int_level2_port_ids);   // bit 7
        packet.emit(hdr.int_egress_port_tx_util);  // bit 8
    }
}

control verifyChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

control computeChecksum(inout headers hdr, inout metadata meta) {
    apply {
        update_checksum(
            hdr.ipv4.isValid(),
            {
                hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.dscp,
                hdr.ipv4.ecn,
                hdr.ipv4.totalLen,
                hdr.ipv4.id,
                hdr.ipv4.flags,
                hdr.ipv4.fragOffset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr
            },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16
        );

        update_checksum(
            hdr.report_ipv4.isValid(),
            {
                hdr.report_ipv4.version,
                hdr.report_ipv4.ihl,
                hdr.report_ipv4.dscp,
                hdr.report_ipv4.ecn,
                hdr.report_ipv4.totalLen,
                hdr.report_ipv4.id,
                hdr.report_ipv4.flags,
                hdr.report_ipv4.fragOffset,
                hdr.report_ipv4.ttl,
                hdr.report_ipv4.protocol,
                hdr.report_ipv4.srcAddr,
                hdr.report_ipv4.dstAddr
            },
            hdr.report_ipv4.hdrChecksum,
            HashAlgorithm.csum16
        );

        update_checksum_with_payload(
            hdr.udp.isValid(),
            {  hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                8w0,
                hdr.ipv4.protocol,
                hdr.udp.len,
                hdr.udp.srcPort,
                hdr.udp.dstPort,
                hdr.udp.len
            },
            hdr.udp.csum,
            HashAlgorithm.csum16
        );

        update_checksum_with_payload(
            hdr.udp.isValid() && hdr.int_header.isValid() ,
            {  hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                8w0,
                hdr.ipv4.protocol,
                hdr.udp.len,
                hdr.udp.srcPort,
                hdr.udp.dstPort,
                hdr.udp.len,
                hdr.int_shim,
                hdr.int_header,
                hdr.int_switch_id,
                hdr.int_port_ids,
                hdr.int_q_occupancy,
                hdr.int_level2_port_ids,
                hdr.int_ingress_tstamp,
                hdr.int_egress_tstamp,
                hdr.int_egress_port_tx_util,
                hdr.int_hop_latency
            },
            hdr.udp.csum,
            HashAlgorithm.csum16
        );
    }
}