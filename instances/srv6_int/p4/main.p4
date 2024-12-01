#include <core.p4>
#include <v1model.p4>

/************************************************************************
************************** Defines **************************************
*************************************************************************/

#define ETH_TYPE_IPV4 0x0800
#define ETH_TYPE_IPV6 0x86dd
#define l4_proto_TCP 8w6
#define l4_proto_UDP 8w17
#define l4_proto_SRV6 8w43
#define IP_VERSION_4 4w4
#define SRV6_MAX_HOPS 6

#define PKT_INSTANCE_TYPE_NORMAL 0
#define PKT_INSTANCE_TYPE_INGRESS_CLONE 1
#define PKT_INSTANCE_TYPE_EGRESS_CLONE 2
#define PKT_INSTANCE_TYPE_COALESCED 3
#define PKT_INSTANCE_TYPE_INGRESS_RECIRC 4
#define PKT_INSTANCE_TYPE_REPLICATION 5
#define PKT_INSTANCE_TYPE_RESUBMIT 6

typedef bit<48>  mac_addr_t;
typedef bit<32>  ipv4_addr_t;
typedef bit<128> ipv6_addr_t;
typedef bit<9>   port_t;

const port_t CPU_PORT = 255;



/************************************************************************
************************** Headers **************************************
*************************************************************************/

@controller_header("packet_in")
header packet_in_header_t {
    bit<9> ingress_port;
    bit<7> _padding;
}

@controller_header("packet_out")
header packet_out_header_t {
    bit<9> egress_port;
    bit<7> _padding;
}

header ethernet_t {
    bit<48> dst_addr;
    bit<48> src_addr;
    bit<16> ether_type;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<6>  dscp;
    bit<2>  ecn;
    bit<16> len;
    bit<16> identification;
    bit<3>  flags;
    bit<13> frag_offset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdr_checksum;
    bit<32> src_addr;
    bit<32> dst_addr;
}

header ipv6_t {
    bit<4> version;
    bit<8> traffic_class;
    bit<20> flow_label;
    bit<16> payload_len;
    bit<8> next_hdr;
    bit<8> hop_limit;
    bit<128> src_addr;
    bit<128> dst_addr;
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

header srv6_segment_list_t{
    bit<128> sid;
}

header tcp_t {
    bit<16> src_port;
    bit<16> dst_port;
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4>  data_offset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

header udp_t {
    bit<16> src_port;
    bit<16> dst_port;
    bit<16> length_;
    bit<16> checksum;
}

const bit<6> IPv4_DSCP_INT = 0x20;   // indicates an INT header in the packet
const bit<16> INT_SHIM_HEADER_LEN_BYTES = 4;
const bit<8> INT_TYPE_HOP_BY_HOP = 1;

header intl4_shim_t {
    bit<8> int_type;
    bit<8> rsvd1;
    bit<8> len;    // the length of all INT headers in 4-byte words
    bit<6> dscp;  // copy DSCP here
    bit<2> rsvd3;
}
const bit<16> INT_HEADER_LEN_BYTES = 8;
const bit<4> INT_VERSION = 1;

header int_header_t {
    bit<4>  ver;
    bit<2>  rep;
    bit<1>  c;
    bit<1>  e;
    bit<1>  m;
    bit<7>  rsvd1;
    bit<3>  rsvd2;
    bit<5>  hop_metadata_len;   // the length of the metadata added by a single INT node (4-byte words)
    bit<8>  remaining_hop_cnt;  // how many switches can still add INT metadata
    bit<16> instruction_mask;
    bit<16> seq;  // rsvd3 - custom implementation of a sequence number
}

const bit<16> INT_ALL_HEADER_LEN_BYTES = INT_SHIM_HEADER_LEN_BYTES + INT_HEADER_LEN_BYTES;

header int_switch_id_t {
    bit<32> switch_id;
}

header int_port_ids_t {
    bit<16> ingress_port_id;
    bit<16> egress_port_id;
}

header int_hop_latency_t {
    bit<32> hop_latency;
}

header int_q_occupancy_t {
    bit<8>  q_id;
    bit<24> q_occupancy;
}

header int_ingress_tstamp_t {
    bit<64> ingress_tstamp;
}

header int_egress_tstamp_t {
    bit<64> egress_tstamp;
}

header int_level2_port_ids_t {
    bit<16> ingress_port_id;
    bit<16> egress_port_id;
}

header int_egress_port_tx_util_t {
    bit<32> egress_port_tx_util;
}


const bit<4> INT_REPORT_HEADER_LEN_WORDS = 4;
const bit<4> INT_REPORT_VERSION = 1;

header int_report_fixed_header_t {
    bit<4> ver;
    bit<4> len;
    bit<3> nprot;
    bit<5> rep_md_bits_high; // Split rep_md_bits to align to word boundaries
    bit<1> rep_md_bits_low;
    bit<6> reserved;
    bit<1> d;
    bit<1> q;
    bit<1> f;
    bit<6> hw_id;
    bit<32> switch_id;
    bit<32> seq_num;
    bit<32> ingress_tstamp;
}

struct int_metadata_t {
    bit<1>  source;    // is INT source functionality enabled
    bit<1>  sink;        // is INT sink functionality enabled
    bit<32> switch_id;  // INT switch id is configured by network controller
    bit<16> insert_byte_cnt;  // counter of inserted INT bytes
    bit<8>  int_hdr_word_len;  // counter of inserted INT words
    bit<1>  remove_int;           // indicator that all INT headers and data must be removed at egress for the processed packet
    bit<16> sink_reporting_port;    // on which port INT reports must be send to INT collector
    bit<64> ingress_tstamp;   // pass ingress timestamp from Ingress pipeline to Egress pipeline
    bit<16> ingress_port;  // pass ingress port from Ingress pipeline to Egress pipeline
}

struct layer34_metadata_t {
    bit<128> ip_src;
    bit<128> ip_dst;
    bit<8>  ip_ver;
    bit<16> l4_src;
    bit<16> l4_dst;
    bit<8>  l4_proto;
    bit<16> l3_mtu;
    bit<6>  dscp;
}



header int_data_t {
    // Enough room for previous 4 nodes worth of data
    varbit<1600> data;
}
/************************************************************************
*********************** Custom Headers  *********************************
*************************************************************************/

struct headers_t {
    packet_out_header_t packet_out;
    packet_in_header_t packet_in;

    // normal headers
    ethernet_t ethernet;
    ipv4_t ipv4;
    ipv6_t ipv6;
    srv6_header_t srh;
    srv6_segment_list_t[SRV6_MAX_HOPS] segment_list;
    tcp_t tcp;
    udp_t udp;

    // INT report headers
    ethernet_t                report_ethernet;
    ipv4_t                    report_ipv4;
    udp_t                     report_udp;
    int_report_fixed_header_t report_fixed_header;

    // INT headers
    intl4_shim_t              int_shim;
    int_header_t              int_header;

    // local INT node metadata
    int_egress_port_tx_util_t int_egress_port_tx_util;
    int_egress_tstamp_t       int_egress_tstamp;
    int_hop_latency_t         int_hop_latency;
    int_ingress_tstamp_t      int_ingress_tstamp;
    int_port_ids_t            int_port_ids;
    int_level2_port_ids_t     int_level2_port_ids;
    int_q_occupancy_t         int_q_occupancy;
    int_switch_id_t           int_switch_id;

    // INT metadata of previous nodes
    int_data_t                int_data;
}

struct metadata {
    int_metadata_t       int_metadata;
    intl4_shim_t         int_shim;
    layer34_metadata_t   layer34_metadata;
    ipv6_addr_t next_sid;
}

/************************************************************************
**************************** Parser *************************************
*************************************************************************/

parser parser_impl(packet_in packet,
                  out headers_t hdr,
                  inout metadata local_metadata,
                  inout standard_metadata_t standard_metadata) {

    state start {
        transition select(standard_metadata.ingress_port) {
            CPU_PORT: parse_packet_out;
            default: parse_ethernet;
        }
    }

    state parse_packet_out {
        packet.extract(hdr.packet_out);
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            ETH_TYPE_IPV4: parse_ipv4;
            ETH_TYPE_IPV6: parse_ipv6;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            l4_proto_TCP: parse_tcp;
            l4_proto_UDP: parse_udp;
            default: accept;
        }
    }

    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        local_metadata.layer34_metadata.ip_ver = hdr.ipv6.next_hdr;
        local_metadata.layer34_metadata.ip_src = hdr.ipv6.src_addr;
        local_metadata.layer34_metadata.ip_dst = hdr.ipv6.dst_addr;
        local_metadata.layer34_metadata.ip_ver = 8w6;
        local_metadata.layer34_metadata.dscp = hdr.ipv6.traffic_class[7:2];
        transition select(hdr.ipv6.next_hdr) {
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
        local_metadata.layer34_metadata.l4_src = hdr.tcp.src_port;
        local_metadata.layer34_metadata.l4_dst = hdr.tcp.dst_port;
        transition accept;
    }

    state parse_udp {
        packet.extract(hdr.udp);
        local_metadata.layer34_metadata.l4_src = hdr.udp.src_port;
        local_metadata.layer34_metadata.l4_dst = hdr.udp.dst_port;
        local_metadata.layer34_metadata.l4_proto = 8w0x11;
        transition select(meta.layer34_metadata.dscp, hdr.udp.dstPort) {
            (6w0x20 &&& 6w0x3f, 16w0x0 &&& 16w0x0): parse_int;
            default: accept;
        }
    }

    state parse_int {
        packet.extract(hdr.int_shim);
        packet.extract(hdr.int_header);
        transition accept;
    }
}


/************************************************************************
*********************** Verify Checksum *********************************
*************************************************************************/

control verify_checksum_control(inout headers_t hdr,
                                inout metadata local_metadata) {
    apply {
        // Assume checksum is always correct.
    }
}


/************************************************************************
*********************** Ingress Pipeline*********************************
*************************************************************************/

control ingress(inout headers_t hdr,
                inout metadata local_metadata,
                inout standard_metadata_t standard_metadata) {

/********** Actions **********/
    action drop(){
    	mark_to_drop(standard_metadata);
    }

    action insert_srh_num(bit<8> num_segments){
        hdr.srh.setValid();
        hdr.srh.next_hdr = hdr.ipv6.next_hdr;
        hdr.srh.hdr_ext_len = num_segments * 2;
        hdr.srh.routing_type = 4;
        hdr.srh.segment_left = num_segments - 1;
        hdr.srh.last_entry = num_segments - 1;
        hdr.srh.flags = 0;
        hdr.srh.tag = 0;
        hdr.ipv6.next_hdr = l4_proto_SRV6;
    }

    action insert_srh(ipv6_addr_t s1, ipv6_addr_t s2, ipv6_addr_t s3){
        hdr.ipv6.dst_addr = s1;
        hdr.ipv6.payload_len = hdr.ipv6.payload_len + 56;
        insert_srh_num(3);
        hdr.segment_list[0].setValid();
        hdr.segment_list[0].sid = s3;
        hdr.segment_list[1].setValid();
        hdr.segment_list[1].sid = s2;
        hdr.segment_list[2].setValid();
        hdr.segment_list[2].sid = s1;
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
        hdr.ipv6.dst_addr = local_metadata.next_sid;
        //hdr.ipv6.dst_addr = hdr.segment_list[hdr.srh.last_entry - hdr.srh.segment_left].sid;
    }

    action srv6_pop() {
        end();
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
               inout metadata local_metadata,
               inout standard_metadata_t standard_metadata) {

    apply {
        if (standard_metadata.egress_port == CPU_PORT) {
        	// Handle packet-in packet, if egress_port is cpu port, which means this packet is sent to controller
            // Add the packet-in header

            hdr.packet_in.setValid();
            hdr.packet_in.ingress_port = standard_metadata.ingress_port;

        }    
    }
}



/************************************************************************
*********************** Compute Checksum ********************************
*************************************************************************/

control compute_checksum_control(inout headers_t hdr,
                                 inout metadata local_metadata) {
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
**************************** Deparser ***********************************
*************************************************************************/

control deparser(packet_out packet, in headers_t hdr) {
    apply {


        // raport headers
        packet.emit(hdr.report_ethernet);
        packet.emit(hdr.report_ipv6);
        packet.emit(hdr.report_udp);
        packet.emit(hdr.report_fixed_header);

        // original headers
        packet.emit(hdr.packet_in);
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


/************************************************************************
**************************** Switch *************************************
*************************************************************************/

V1Switch(parser_impl(),
         verify_checksum_control(),
         ingress(),
         egress(),
         compute_checksum_control(),
         deparser()) main;

