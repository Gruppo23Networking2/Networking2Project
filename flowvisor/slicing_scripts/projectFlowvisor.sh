#!/bin/bash

# Start FlowVisor service
echo "Starting FlowVisor service..."
sudo /etc/init.d/flowvisor start

echo "Waiting for service to start..."
sleep 10
echo "Done."

# Get FlowVisor current config
echo "FlowVisor initial config:"
fvctl -f /etc/flowvisor/flowvisor.passwd get-config

# Get FlowVisor current defined slices
echo "FlowVisor initially defined slices:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-slices

# Get FlowVisor current defined flowspaces
echo "FlowVisor initially defined flowspaces:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-flowspace

# Get FlowVisor connected switches
echo "FlowVisor connected switches:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-datapaths

# Get FlowVisor connected switches links up
echo "FlowVisor connected switches links:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-links

# Define the FlowVisor slices
echo "Definition of FlowVisor slices..."
# fvctl add-slice [options] <slicename> <controller-url> <admin-email>
fvctl -f /etc/flowvisor/flowvisor.passwd add-slice admin tcp:localhost:10001 admin@slice
fvctl -f /etc/flowvisor/flowvisor.passwd add-slice server tcp:localhost:10002 server@slice
fvctl -f /etc/flowvisor/flowvisor.passwd add-slice client tcp:localhost:10003 client@slice

# Check defined slices
echo "Check slices just defined:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-slices

# Define flowspaces
echo "Definition of flowspaces..."
# fvctl add-flowspace [options] <flowspace-name> <dpid> <priority> <match> <slice-perm>

fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port1 1 100 in_port=1 client=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port2 1 100 in_port=2 client=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port3 1 100 in_port=3 client=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port4 1 100 in_port=4,dl_type=0x0800,nw_proto=6 client=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port5 1 100 in_port=5,dl_type=0x0800,nw_proto=11 client=7

fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid2-port1 2 100 in_port=1 server=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid2-port2 2 100 in_port=2,dl_type=0x0800,nw_proto=6 server=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid2-port3 2 100 in_port=3 server=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid2-port4 2 100 in_port=4 server=7

fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid3 3 100 any admin=7

# Check all the flowspaces added
echo "Check all flowspaces just defined:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-flowspace
