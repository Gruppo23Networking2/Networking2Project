#!/bin/bash

echo "Starting FlowVisor service..."
sudo /etc/init.d/flowvisor start

echo "Waiting for service to start..."
sleep 10
echo "Done."

echo "Cleaning FlowVisor from slices previously defined..."
fvctl -f /etc/flowvisor/flowvisor.passwd remove-slice client
fvctl -f /etc/flowvisor/flowvisor.passwd remove-slice admin
fvctl -f /etc/flowvisor/flowvisor.passwd remove-slice server

echo "Check cleanup just performed:"
fvctl -f /etc/flowvisor/flowvisor.passwd list-slices
fvctl -f /etc/flowvisor/flowvisor.passwd list-flowspace
