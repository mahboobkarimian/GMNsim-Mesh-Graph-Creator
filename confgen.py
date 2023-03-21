#!/bin/python3

def configure(num_nodes, edges, dir, cleanup, add_tun, tunip, log_nano, log_radio, be_logged_nodes, options):
    config = dict()

    config['BASH'] = "#!/bin/bash"
    if cleanup:
        config['CLEANUP'] = "rm -rf /tmp/wsbrd/\nrm -f /tmp/sim_socket /tmp/*_pae_*\nrm -f /tmp/n{1,2,3,4,5,6,7,8,9,10}*\nmkdir -p /tmp/wsbrd/"

    # Run tun
    if add_tun:
        # enable core generation
        if tunip == None:
            tunip = "fd12:3456::2e99:8528:350:bbb7/64"
        config['TUN_ADD'] = "sudo ip tuntap add mode tun tun0"
        config['TUN_IP'] = f"sudo ip addr add {tunip} dev tun0"
        config['TUN_UP'] = "sudo ip link set tun0 up"

    # process edges, create TPG
    tpg = ""
    for e in edges:
        n1 = e[0]
        n2 = e[1]
        tpg += f"-g {n1},{n2} "

    # run server
    config['RUN_SVR'] = f"gnome-terminal --tab -- {dir}/wssimserver {tpg} /tmp/sim_socket --dump"
    config['SLEEP'] = "sleep 0.5"

    # run phy/mac
    for i in range(num_nodes):
        if (log_radio and str(i) in be_logged_nodes) or (log_radio and be_logged_nodes == []):
            config[f'RUN_MAC_{i}'] = f"gnome-terminal --tab --title \"MAC_N {i}\" --  bash -c \" {dir}/wshwsim -m 01:02:03:04:05:06:00:{i:02x} \"/tmp/uart{i}\" /tmp/sim_socket\""
        else:
            config[f'RUN_MAC_{i}'] = f"gnome-terminal --tab --title \"MAC_N {i}\" --  bash -c \" {dir}/wshwsim -m 01:02:03:04:05:06:00:{i:02x} \"/tmp/uart{i}\" /tmp/sim_socket > /dev/null 2> /dev/null\""

    # Run Router nodes
    for i in range(1, num_nodes):
        if (log_nano and str(i) in be_logged_nodes) or (log_nano and be_logged_nodes == []):
            config[f'RUN_R_{i}'] = f"gnome-terminal --tab --title \"R_N {i}\" -- {dir}/wsnode -F {dir}/examples/wsnode.conf -u $(readlink \"/tmp/uart{i}\") -o storage_prefix=/tmp/n{i}_"
        else:
            config[f'RUN_R_{i}'] = f"{dir}/wsnode -F {dir}/examples/wsnode.conf -u $(readlink \"/tmp/uart{i}\") -o storage_prefix=/tmp/n{i}_ > /dev/null 2> /dev/null &"

    # Run BR
    config['RUN_BR'] = f"gnome-terminal --window --title \"BR N0\" -- {dir}/wsbrd -F {dir}/examples/wsbrd.conf -u $(readlink /tmp/uart0)"

    complete_config = ""
    for key, value in config.items():
        complete_config += f"{value}\n"

    print(complete_config)
    return complete_config

# Example
#edg = [[1, 2, 9, 10], [2, 3, 9, 10], [1, 3, 9, 10]]
#conf = configure(3, edg, "/home/mahboob/test/mse-tm-mbed-simulator", True, True, None, None)