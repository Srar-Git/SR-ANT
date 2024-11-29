#include <core.p4>
#include <v1model.p4>

/************************************************************************
************************** Defines **************************************
*************************************************************************/

#define ETH_TYPE_IPV6 0x86dd
#define IP_PROTO_TCP 6
#define IP_PROTO_UDP 17
#define IP_PROTO_SRV6 43

typedef bit<48>  mac_addr_t;
typedef bit<128> ipv6_addr_t;
typedef bit<9>   port_t;

const port_t CPU_PORT = 255;

/************************************************************************
************************** Headers **************************************
*************************************************************************/

header ethernet_t {
    mac_addr_t dst_addr;
    mac_addr_t src_addr;
    bit<16> ether_type;
}

header ipv6_t {
    bit<4>  version;
    bit<8>  traffic_class;
    bit<20> flow_label;
    bit<16> payload_len;
    bit<8>  next_hdr;
    bit<8>  hop_limit;
    ipv6_addr_t src_addr;
    ipv6_addr_t dst_addr;
}

header srv6_header_t {
    bit<8> next_hdr;
    bit<8> hdr_ext_len;
    bit<8> routing_type;
    bit<8> segment_left;
    bit<8> last_entry;
    bit<8> flags;
    bit<16> tag;
}

header srv6_segment_list_t {
    ipv6_addr_t sid;
}

/************************************************************************
*********************** Custom Headers  *********************************
*************************************************************************/

struct headers_t {
    ethernet_t ethernet;
    ipv6_t ipv6;
    srv6_header_t srh;
    srv6_segment_list_t[3] segment_list; // 假设有 3 个 SID
}

struct local_metadata_t {
    bit<16>        l4_src_port;
    bit<16>        l4_dst_port;
    ipv6_addr_t next_sid;
    bit<8>         ip_proto;
}

/************************************************************************
**************************** Parser *************************************
*************************************************************************/

parser parser_impl(packet_in packet,
                  out headers_t hdr,
                  inout local_metadata_t local_metadata,
                  inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            ETH_TYPE_IPV6: parse_ipv6;
            default: accept;
        }
    }

    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        local_metadata.ip_proto = hdr.ipv6.next_hdr;
        transition select(hdr.ipv6.next_hdr) {
            IP_PROTO_SRV6: parse_srh;
            default: accept;
        }
    }

    state parse_srh {
        packet.extract(hdr.srh);
        transition parse_segment_list;
    }

    state parse_segment_list {
        packet.extract(hdr.segment_list.next);
        transition select(hdr.srh.segment_left == 0) {
            true: accept;
            false: parse_segment_list;
        }
    }
}

/************************************************************************
*********************** Ingress Pipeline*********************************
*************************************************************************/

control ingress(inout headers_t hdr,
                inout standard_metadata_t standard_metadata) {

    /********** Actions **********/

    action drop() {
        mark_to_drop(standard_metadata);
    }

    action insert_srh(ipv6_addr_t sid1, ipv6_addr_t sid2, ipv6_addr_t sid3) {
        hdr.srh.setValid();
        hdr.srh.next_hdr = hdr.ipv6.next_hdr;
        hdr.srh.hdr_ext_len = 4; // (number of 8-octet units, not including first 8 octets)
        hdr.srh.routing_type = 4;
        hdr.srh.segment_left = 2;
        hdr.srh.last_entry = 2;
        hdr.srh.flags = 0;
        hdr.srh.tag = 0;

        hdr.segment_list[0].setValid();
        hdr.segment_list[0].sid = sid3;
        hdr.segment_list[1].setValid();
        hdr.segment_list[1].sid = sid2;
        hdr.segment_list[2].setValid();
        hdr.segment_list[2].sid = sid1;

        hdr.ipv6.next_hdr = IP_PROTO_SRV6;
        hdr.ipv6.payload_len = hdr.ipv6.payload_len + 56; // SRH (8 bytes) + 3 SIDs (3 x 16 bytes)
        hdr.ipv6.dst_addr = sid1;
    }

    action dec_ttl() {
        hdr.ipv6.hop_limit = hdr.ipv6.hop_limit - 1;
    }

    action forward(port_t port, mac_addr_t dst_mac) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.src_addr = hdr.ethernet.dst_addr;
        hdr.ethernet.dst_addr = dst_mac;
    }

    action end() {
        hdr.srh.segment_left = hdr.srh.segment_left - 1;
        hdr.ipv6.dst_addr = hdr.segment_list[hdr.srh.last_entry - hdr.srh.segment_left].sid;
    }

    action srv6_pop() {
        hdr.ipv6.next_hdr = hdr.srh.next_hdr;
        bit<16> srh_size = (((bit<16>)hdr.srh.last_entry + 1) << 4) + 8;
        hdr.ipv6.payload_len = hdr.ipv6.payload_len - srh_size;
        hdr.srh.setInvalid();
        hdr.segment_list[0].setInvalid();
        hdr.segment_list[1].setInvalid();
        hdr.segment_list[2].setInvalid();
    }

    /********** Tables **********/

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
            hdr.ipv6.dst_addr: exact;
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
            hdr.ipv6.dst_addr: lpm;
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

            if (hdr.ipv6.hop_limit == 0) {
                drop();
            } else {
                ipv6_lpm_table.apply();
            }
        }
    }
}

/************************************************************************
*********************** Egress Pipeline**********************************
*************************************************************************/

control egress(inout headers_t hdr,
               inout standard_metadata_t standard_metadata) {
    apply { }
}

/************************************************************************
**************************** Deparser ***********************************
*************************************************************************/

control deparser(packet_out packet, in headers_t hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv6);
        if (hdr.srh.isValid()) {
            packet.emit(hdr.srh);
            packet.emit(hdr.segment_list);
        }
    }
}

/************************************************************************
*********************** Verify Checksum *********************************
*************************************************************************/

control verify_checksum_control(inout headers_t hdr,
                                inout standard_metadata_t standard_metadata) {
    apply {
        // Assume checksum is always correct.
    }
}
/************************************************************************
*********************** Compute Checksum ********************************
*************************************************************************/

control compute_checksum_control(inout headers_t hdr,
                                 inout standard_metadata_t standard_metadata) {
    apply {
        update_checksum(hdr.ipv4.isValid(),
            {
                hdr.ipv4.version,
                hdr.ipv4.ihl,
                hdr.ipv4.dscp,
                hdr.ipv4.ecn,
                hdr.ipv4.len,
                hdr.ipv4.identification,
                hdr.ipv4.flags,
                hdr.ipv4.frag_offset,
                hdr.ipv4.ttl,
                hdr.ipv4.protocol,
                hdr.ipv4.src_addr,
                hdr.ipv4.dst_addr
            },
            hdr.ipv4.hdr_checksum,
            HashAlgorithm.csum16
        );
    }
}
/************************************************************************
**************************** Switch *************************************
*************************************************************************/

V1Switch(parser_impl(),
         verify_checksum_control(),
         ingress(),
         egress(),
         compute_checksum_control(),
         deparser()) main;
