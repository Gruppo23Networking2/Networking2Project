#!/usr/bin/env python3
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.packet import packet, ethernet, ether_types, udp, tcp, icmp


class ClientSlice(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ClientSlice, self).__init__(*args, **kwargs)

        # Support function for easy blacklisting of host to host connections
        def _cannot_go(src, dst):
            # blacklist[src_mac]["blocked_dst_mac"]
            blacklist = {
                "00:00:00:00:00:01": ["00:00:00:00:00:02", "00:00:00:00:00:03"],
                "00:00:00:00:00:02": ["00:00:00:00:00:01", "00:00:00:00:00:03"],
                "00:00:00:00:00:03": ["00:00:00:00:00:01", "00:00:00:00:00:02"],
            }

            if blacklist.get(src):
                return dst in blacklist[src]

            return False

        # can_go = self.blacklist(src_mac, dst_mac)
        self.blacklist = _cannot_go

        # outport = self.mac_to_port[dpid][mac_address]
        self.mac_to_port = {
            1: {
                "00:00:00:00:00:01": 1,
                "00:00:00:00:00:02": 2,
                "00:00:00:00:00:03": 3,
                "00:00:00:00:00:04": 0,
                "00:00:00:00:00:05": 0,
                "00:00:00:00:00:06": 4,
                "00:00:00:00:00:07": 4,
            }
        }

        self.end_switches = [1]
        self.HTTP_PORT = 80

        # Just for test purposes
        self.WOL_PORT = 9
        self.admins = ["00:00:00:00:00:04", "00:00:00:00:00:05"]
        self.admin_port = 5

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        mod = parser.OFPFlowMod(
            datapath=datapath,
            match=match,
            cookie=0,
            command=ofproto.OFPFC_ADD,
            idle_timeout=20,
            hard_timeout=0,
            priority=priority,
            flags=ofproto.OFPFF_SEND_FLOW_REM,
            actions=actions,
        )

        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        data = None
        ofproto = datapath.ofproto

        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )

        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        in_port = msg.in_port
        dpid = datapath.id

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        # ignore lldp packet
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        dst = eth.dst
        src = eth.src

        # Check if the source should be able to contact the destination
        if self.blacklist(src, dst):
            self.logger.info(
                f"INFO blocked packet in switch-{dpid} (eth_src={src}, eth_dst={dst}) w/ Blacklist rule",
            )
            return

        self.logger.info(
            f"INFO packet arrived in switch-{dpid} (in_port={in_port}, eth_src={src}, eth_dst={dst})"
        )

        # Check if destination is in the routing table
        if (dpid in self.mac_to_port) and (dst in self.mac_to_port[dpid]):

            # Just for test purposes if traffic on UDP port 9 then it's ok
            if pkt.get_protocol(udp.udp) and (pkt.get_protocol(udp.udp).dst_port == self.WOL_PORT or pkt.get_protocol(udp.udp).src_port == self.WOL_PORT):
                out_port = self.mac_to_port[dpid][dst]

                self.logger.info(
                    f"INFO sending packet from switch-{dpid} (out_port={out_port}) w/ WOL rule"
                )

                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                match = datapath.ofproto_parser.OFPMatch(
                    in_port=in_port,
                    dl_dst=dst,
                    dl_src=src,
                    dl_type=ether_types.ETH_TYPE_IP,
                    nw_proto=0x11,  # udp
                )

                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)
            
            # UDP
            elif pkt.get_protocol(udp.udp) :
                self.logger.info(
                    f"INFO blocked packet from switch-{dpid} w/ UDP rule"
                )

            # If the packet is TCP and sent on port HTTP_PORT then it can pass
            elif pkt.get_protocol(tcp.tcp) and (
                pkt.get_protocol(tcp.tcp).dst_port == self.HTTP_PORT
                or pkt.get_protocol(tcp.tcp).src_port == self.HTTP_PORT
            ):
                out_port = self.mac_to_port[dpid][dst]

                self.logger.info(
                    f"INFO sending packet from switch-{dpid} (out_port={out_port}) w/ TCP {self.HTTP_PORT} rule"
                )

                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                match = datapath.ofproto_parser.OFPMatch(
                    in_port=in_port,
                    dl_dst=dst,
                    dl_type=ether_types.ETH_TYPE_IP,
                    nw_proto=0x06,  # tcp
                    tp_dst=self.HTTP_PORT,
                )

                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)

            # TCP packets sent on ports other than HTTP_PORT are not allowed
            elif pkt.get_protocol(tcp.tcp):
                self.logger.info(
                    f"INFO blocked from switch-{dpid} (in_port={in_port}) w/ TCP rule"
                )

            # Behaviour if the packet is ICMP
            elif pkt.get_protocol(icmp.icmp):
                out_port = self.mac_to_port[dpid][dst]

                self.logger.info(
                    f"INFO blocked from switch-{dpid} (out_port={out_port}) w/ ICMP rule"
                )

                actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
                match = datapath.ofproto_parser.OFPMatch(
                    in_port=in_port,
                    dl_dst=dst,
                    dl_src=src,
                    dl_type=ether_types.ETH_TYPE_IP,
                    nw_proto=0x01,  # icmp
                )

                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)

        # If destination is unknown flood all switch ports
        elif dpid not in self.end_switches:
            out_port = ofproto.OFPP_FLOOD

            self.logger.info(
                f"INFO sending packet from switch-{dpid} (out_port={out_port}) w/ flooding rule"
            )

            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)

            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)