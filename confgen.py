#!/bin/python3

def configure(num_nodes, edges, dir, cleanup, add_tun, tunip, log_nano, log_radio, be_logged_nodes, options):
    config = ""

    config += "#!/bin/bash\n"
    if cleanup:
        config += "rm -rf /tmp/wsbrd/\nrm -f /tmp/sim_socket /tmp/*_pae_*\nrm -f /tmp/n{1,2,3,4,5,6,7,8,9,10}*\nmkdir -p /tmp/wsbrd/\n"

    config += f"cd {dir}\n"
    # Run tun
    if add_tun:
        # enable core generation
        if tunip == None:
            tunip = "fd12:3456::2e99:8528:350:bbb7/64"
        config += "sudo ip tuntap add mode tun tun0 user $(whoami)\n"
        config += f"sudo ip addr add {tunip} dev tun0\n"
        config += "sudo ip link set tun0 up\n"

    # Creating D-Bus rule file for wsbrd which is necessary when it is executed as root
    content="""
WSBRD_DBUS_CONF_FILE=/etc/dbus-1/system.d/com.silabs.Wisun.BorderRouter.conf

WSBRD_DBUS_CONF_FILE_CONTENT=$(cat <<EOF
<!DOCTYPE busconfig PUBLIC "-//freedesktop//DTD D-Bus Bus Configuration 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
  <policy context="default">
    <allow own="com.silabs.Wisun.BorderRouter"/>
    <allow send_destination="com.silabs.Wisun.BorderRouter"/>
    <allow receive_sender="com.silabs.Wisun.BorderRouter"/>
    <allow send_interface="com.silabs.Wisun.BorderRouter"/>
    <allow receive_interface="com.silabs.Wisun.BorderRouter"/>
    <allow send_interface="org.freedesktop.DBus.Introspectable"/>
    <allow send_interface="org.freedesktop.DBus.Properties"/>
    <allow receive_interface="org.freedesktop.DBus.Introspectable"/>
    <allow receive_interface="org.freedesktop.DBus.Properties"/>
  </policy>
</busconfig>
EOF
)

if [ ! -f "$WSBRD_DBUS_CONF_FILE" ]; then
	echo "Writing WSBRD D-Bus configuration file"
	echo $WSBRD_DBUS_CONF_FILE_CONTENT | sudo tee -a $WSBRD_DBUS_CONF_FILE
fi
"""
    config += content

    # process edges, create TPG
    tpg = ""
    for e in edges:
        n1 = e[0]
        n2 = e[1]
        tpg += f"-g {n1},{n2} "

    # run server
    config += f"gnome-terminal --tab -- {dir}/wssimserver {tpg} /tmp/sim_socket --dump -f\n"
    config += "sleep 0.5\n"

    # run phy/mac
    for i in range(num_nodes):
        hex_i = f"{i:04x}"
        print(hex_i)
        if (log_radio and str(i) in be_logged_nodes) or (log_radio and be_logged_nodes == []):
            config += f"gnome-terminal --tab --title \"MAC_N {i}\" --  bash -c \" {dir}/wshwsim -m 01:02:03:04:05:06:{hex_i[0:2]}:{hex_i[2:4]} /tmp/uart{i} /tmp/sim_socket\"\n"
        else:
            config += f"gnome-terminal --tab -- sh -c \"{dir}/wshwsim -m 01:02:03:04:05:06:{hex_i[0:2]}:{hex_i[2:4]} /tmp/uart{i} /tmp/sim_socket > /dev/null 2> /dev/null\"\n"

    # Run Router nodes
    for i in range(1, num_nodes):
        if (log_nano and str(i) in be_logged_nodes) or (log_nano and be_logged_nodes == []):
            config += f"gnome-terminal --window --title \"R_N {i}\" -- {dir}/wsnode -F {dir}/examples/wsnode.conf -u $(readlink \"/tmp/uart{i}\") -o storage_prefix=/tmp/n{i}_\n"
        else:
            config += f"sh -c \"{dir}/wsnode -F {dir}/examples/wsnode.conf -u $(readlink \"/tmp/uart{i}\") -o storage_prefix=/tmp/n{i}_ > /dev/null 2> /dev/null &\"\n"

    # Run BR
    config += f"gnome-terminal --window --title \"BR N0\" -- sudo {dir}/wsbrd -F {dir}/examples/wsbrd.conf -u $(readlink /tmp/uart0)\n"

    return config

# Example
#edg = [[1, 2, 9, 10], [2, 3, 9, 10], [1, 3, 9, 10]]
#conf = configure(3, edg, "/home/mahboob/test/mse-tm-mbed-simulator", True, True, None, None)