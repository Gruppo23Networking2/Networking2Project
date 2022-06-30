# Networking2Project
Giuseppe Alessio Sciumè ([@Sciumegpp00](https://github.com/Sciumegpp00 "github.com"))

Marco Giacopuzzi ([@mgiacopu](https://github.com/mgiacopu "github.com"))

Federico Cucino ([@turbostar190](https://github.com/turbostar190 "github.com"))

## How to execute the project

- Clone this repository inside the root of [comnetsemu repo](https://git.comnets.net/public-repo/comnetsemu/ "git.comnets.net")
  - `comnetsemu$ git clone https://github.com/Gruppo23Networking2/Networking2Project project`, so the path to this directory will be `comnetsemu/project/`
- Execute `vagrant up` and `vagrant ssh` in `comnetsemu/`

### Execute flowvisor
- In `vagrant@comnetsemu:~/comnetsemu/project/flowvisor$`
  - Start flowvisor container: `./run_flowvisor_container.sh`
  - `cd ~/slicing_scripts`
  - `[root@comnetsemu slicing_scripts]#`:
    - Cleanup the flowvisor topology: `./cleanups/cleanup-project-topology.sh`
    - Start the flowvisor topology: `./projectFlowvisor.sh`, pressing `enter` at every password prompt

### Execute ryu controllers
- In `vagrant@comnetsemu:~/comnetsemu/project$` (One terminal for each script)
  
  - Run client slice: `ryu run --observe-links --ofp-tcp-listen-port 10003 --wsapi-port 8084 /usr/local/lib/python3.8/dist-packages/ryu/app/gui_topology/gui_topology.py ryu_client_slice.py`
  
  - Run server slice: `ryu run --observe-links --ofp-tcp-listen-port 10002 --wsapi-port 8083 /usr/local/lib/python3.8/dist-packages/ryu/app/gui_topology/gui_topology.py ryu_server_slice.py`

  - Run admin slice: `ryu run --observe-links --ofp-tcp-listen-port 10001 --wsapi-port 8082 /usr/local/lib/python3.8/dist-packages/ryu/app/gui_topology/gui_topology.py ryu_admin_slice.py`

### Execute topology
- In `vagrant@comnetsemu:~/comnetsemu/project$`
  - Clean mininet: `sudo mn -c`
  - Run topology: `sudo -E python3 topology.py`
  
### Test topology
- `mininet> xterm host-1 host-2 server-1 host-4`

- Isolation betweeen host-1, host-2, host-3
  - `host-1# ping 10.0.0.2` with no response
  - `host-2# python3 -m http.server 80`, `host-1# wget 10.0.0.2:80` should be pending
- Only HTTP (port 80) traffic allowed through client and server slice
  - `server-1# python3 -m http.server 80`, `host-1# wget 10.0.0.6:80` is successful
  - `server-1# python3 -m http.server 8080`, `host-1# wget 10.0.0.6:8080` should be pending
- UDP traffic is blocked from client to server
  - `server-1# iperf -s -p 999 -u`, `host-1# iperf -c 10.0.0.6 -p 999 -t 10 -i 1 -u` client host can't reach servers with udp traffic
- Any type of traffic is allowed between admin and server
  - `host-4# ping 10.0.0.6` is successful
  - `server-1# python3 -m http.server 80`, `host-4# wget 10.0.0.6:80` is successful
  - `server-1# python3 -m http.server 8080`, `host-4# wget 10.0.0.6:8080` is successful
  - `server-1# iperf -s -p 999 -u`, `host-4# iperf -c 10.0.0.6 -p 999 -t 10 -i 1 -u` is successful
- Only UDP port 9 from admin to client
  - `host-2# iperf -s -p 9 -u`, `host-4# iperf -c 10.0.0.2 -p 9 -t 10 -i 1 -u` is successful
