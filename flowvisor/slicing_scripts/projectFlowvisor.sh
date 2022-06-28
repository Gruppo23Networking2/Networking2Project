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

#Connecting client and server slices
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port1-http-to-server-src 1 100 any server=7

fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-port4-http-to-server-dst 1 100 any client=7


#Connecting server and admin slices
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid3-port2-admin-to-server-src 3 100 any server=7

fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid3-port1-admin-to-client-src 3 100 any client=7

# server to admin
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid2-port1-server-to-admin-src 2 100 any admin=7



# internal switches


fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid1-client 1 100 any client=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid2-server 2 100 any server=7
fvctl -f /etc/flowvisor/flowvisor.passwd add-flowspace dpid3-admin 3 100 any admin=7


# Check all the flowspaces added
echo "Check all flowspaces just defined:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-flowspace
