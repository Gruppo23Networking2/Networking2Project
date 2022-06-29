# Networking2Project
Giuseppe Alessio Sciumè ([@Sciumegpp00](https://github.com/Sciumegpp00 "github.com"))

Marco Giacopuzzi ([@mgiacopu](https://github.com/mgiacopu "github.com"))

Federico Cucino ([@turbostar190](https://github.com/turbostar190 "github.com"))

## How to execute the program
### Execute flowvisor
- In `vagrant@comnetsemu:~/comnetsemu/project/flowvisor$`
  - `./run_flowvisor_container.sh`
  - `cd ~/slicing_scripts`
  - `[root@comnetsemu slicing_scripts]#`:
    - `./projectFlowvisor.sh`, pressing `enter` at every password prompt

### Execute ryu controllers
- In `vagrant@comnetsemu:~/comnetsemu/project$` (One terminal for each script)
  
  - `ryu run --observe-links --ofp-tcp-listen-port 10003 --wsapi-port 8084 /usr/local/lib/python3.8/dist-packages/ryu/app/gui_topology/gui_topology.py ryu_client_slice.py`
  
  - `ryu run --observe-links --ofp-tcp-listen-port 10002 --wsapi-port 8083 /usr/local/lib/python3.8/dist-packages/ryu/app/gui_topology/gui_topology.py ryu_server_slice.py`

  - `ryu run --observe-links --ofp-tcp-listen-port 10001 --wsapi-port 8082 /usr/local/lib/python3.8/dist-packages/ryu/app/gui_topology/gui_topology.py ryu_admin_slice.py`

### Execute topology
- In `vagrant@comnetsemu:~/comnetsemu/project$`
  - Clean mininet: `sudo mn -c`
  - `sudo -E python3 topology.py`
  
### Test topology
TODO SAMPLE TEST
