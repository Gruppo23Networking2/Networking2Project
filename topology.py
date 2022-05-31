#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class Topology(Topo):
    def __init__(self):

        # Initialize topology
        Topo.__init__(self)

        # Create template host, server, switch, and link
        host_config = {"inNamespace": True}
        server_config = {"inNamespace": True}
        http_link_config = {"bw": 1}
        voip_link_config = {"bw": 5}
        video_link_config = {"bw": 10}
        host_link_config = {}
        server_link_config = {}

        # Create switch nodes
        for i in range(3):

            switch_config = {
                "dpid": "%016x" % (i + 1),  # TODO: Pythonize
            }

            self.addSwitch(
                f"switch-{i + 1}",
                protocols="OpenFlow10",
                **switch_config,
            )

        # Create host nodes
        for i in range(5):
            self.addHost(
                f"host-{i + 1}",
                **host_config,
            )

        # Create server nodes
        for i in range(2):
            self.addHost(
                f"server-{i + 1}",
                **server_config,
            )

        # Add switch links
        self.addLink("switch-1", "switch-3", 5, 1, **http_link_config)
        self.addLink("switch-1", "switch-2", 4, 2, **http_link_config)
        self.addLink("switch-2", "switch-3", 1, 2, **http_link_config)

        # Add host links
        self.addLink("host-1", "switch-1", 1, 1, **host_link_config)
        self.addLink("host-2", "switch-1", 1, 2, **host_link_config)
        self.addLink("host-3", "switch-1", 1, 3, **host_link_config)
        self.addLink("host-4", "switch-3", 1, 4, **host_link_config)
        self.addLink("host-5", "switch-3", 1, 3, **host_link_config)
        self.addLink("server-1", "switch-2", 1, 3, **server_link_config)
        self.addLink("server-2", "switch-2", 1, 4, **server_link_config)


topos = {"fvtopo": (lambda: Topology())}

if __name__ == "__main__":
    topo = Topology()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()
    CLI(net)
    net.stop()
