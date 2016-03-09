#
# Projact Ginger
#
# Copyright IBM Corp, 2014-2016
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA

import gettext


_ = gettext.gettext


messages = {
    "GINNET0001E": _("Failed to read /etc/resolv.conf because %(reason)s"),
    "GINNET0002E": _("Failed to write /etc/resolv.conf because %(reason)s"),
    "GINNET0003E": _("Invalid network parameters. Details: %(err)s"),
    "GINNET0004E": _("Unable to update interface configuration. "
                     "Details: %(err)s"),
    "GINNET0005E": _("Invalid parameter for DNS servers"),
    "GINNET0006E": _("Invalid parameter for interface ip address"),
    "GINNET0007E": _("Invalid parameter for interface netmask"),
    "GINNET0008E": _("Invalid parameter for network gateway"),
    "GINNET0009E": _("Unable to get default gateway: %(err)s"),
    "GINNET0010E": _("Unable to delete default gateway: %(err)s"),
    "GINNET0011E": _("Unable to set default gateway: %(err)s"),
    "GINNET0012E": _("Invalid ip/netmask inputs. Both fields must be valid "
                     "ip/netmask values or both must be blank (will erase "
                     "the current IP/netmask)."),
    "GINNET0013E": _("Interface %(name)s is not editable because it belongs "
                     "to a vlan or bridge"),
    "GINNET0014E": _("%(name)s is not valid network interface"),
    "GINNET0015E": _("Error getting information from ifcfg file: "
                     "'%(error)s'."),
    "GINNET0016E": _("Unable to activate the interface on '%(name)s', "
                     "'%(error)s'."),
    "GINNET0017E": _("Unable to deactivate the interface on '%(name)s', "
                     "'%(error)s'."),
    "GINNET0018E": _("Invalid ipv4 address '%(ip)s', "
                     "'%(error)s'."),
    "GINNET0019E": _("Invalid prefix '%(PREFIX)s', "
                     "'%(error)s'."),
    "GINNET0020E": _("IP address is missing."),
    "GINNET0021E": _("PREFIX missing."),
    "GINNET0022E": _("Invalid boot protocol '%(mode)s', "),
    "GINNET0023E": _("Boot protocol is missing for ipv4 settings."),
    "GINNET0024E": _("Basic information of interface is missing."),
    "GINNET0025E": _("Device name of interface is missing or invalid."),
    "GINNET0026E": _("Missing ipv4 initialization key."),
    "GINNET0027E": _("Missing ipv6 initialization key."),
    "GINNET0028E": _("Invalid ipv6 address '%(ip)s', "
                     "'%(error)s'."),
    "GINNET0029E": _("Missing ipv6 address information"),
    "GINNET0030E": _("Exception getting the route information"),
    "GINNET0032E": _("Bond info is missing"),
    "GINNET0033E": _("'yes' or 'no' is allowed value for the BONDING_MASTER"),
    "GINNET0034E": _("Bonding master is missing"),
    "GINNET0036E": _("Slave(s) is missing"),
    "GINNET0037E": _("Minimum one slave has to be given for the bond "
                     "interface"),
    "GINNET0038E": _("Type is missing"),
    "GINNET0040E": _("Invalid bonding option parameter"),
    "GINNET0041E": _("'yes' or 'no' is allowed value for the VLAN"),
    "GINNET0042E": _("Vlan info is missing"),
    "GINNET0043E": _("Vlan is missing"),
    "GINNET0044E": _("Vlan id is missing"),
    "GINNET0045E": _("Physical device name is missing"),
    "GINNET0046E": _("A VLAN slave cannot be configured on a bond with the "
                     "fail_over_mac=follow option"),
    "GINNET0047E": _("For vlan creation over bond, slaves has to be up"),
    "GINNET0048E": _("Module 802q is not loaded into kernel"),
    "GINNET0049E": _("Failed to delete ifcfg file, Error: '%(error)s'"),
    "GINNET0050E": _("VLAN id exceeds the ranges from '0' to '4095'"),
    "GINNET0051E": _("Parent interface of type 'Bond' is not active"),
    "GINNET0052E": _("Type is unknown"),
    "GINNET0053E": _("Persistent file for slave '%(slave)s' is missing"),
    "GINNET0055E": _("Interface '%(name)s' is neither Vlan nor "
                     "Bond to perform delete operation"),
    "GINNET0056E": _("Failed to identify the type of interface"),
    "GINNET0057E": _("Persistent file is not available for an interface, "
                     "'%(name)s'"),
    "GINNET0058E": _("Failed to a delete token from ifcfg file, Error: "
                     "'%(error)s'"),
    "GINNET0059E": _("Unable to bring up the interface '%(name)s', "
                     "'%(error)s'."),
    "GINNET0060E": _("Unable to bring down the interface '%(name)s', "
                     "'%(error)s'."),
    "GINNET0061E": _("Missing IPV4 addresses information"),
    "GINNET0062E": _("The prefix value %(PREFIX)s is not in range 1-32"),
    "GINNET0063E": _("Exception updating the interface settings"),
    "GINNET0064E": _("Boot protocol is missing for ipv6 settings."),
    "GINNET0065E": _("The prefix value %(PREFIX)s is not in range 1-128"),
    "GINNET0066E": _("Given vlan id is not an integer type, Error: '%("
                     "error)s'"),
    "GINNET0067E": _("Maximum length of device name is 15 characters only."),
    "GINNET0068E": _("Device name is invalid."),
    "GINNET0070E": _("Gateway information is missing."),
    "GINNET0071E": _("Invalid prefix '%(PREFIX)s'."),
    "GINNET0072E": _("Interface with the name '%(iface)s' already exists ."),

    "GINUSER0001E": _("Specify name, password, group and profile for the new "
                      "user."),
    "GINUSER0002E": _("User name is a required string."),
    "GINUSER0003E": _("User password is a required string."),
    "GINUSER0004E": _("User group is a required string."),
    "GINUSER0005E": _("User profile is required and should be one among "
                      "kimchiuser, virtuser or admin."),
    "GINUSER0006E": _("Could not add user '%(user)s' to kvm group."),
    "GINUSER0007E": _("Could not add user '%(user)s' to sudoers list."),
    "GINUSER0008E": _("The user name '%(user)s' is already in use'."),
    "GINUSER0009E": _("Could not create user '%(user)s'."),
    "GINUSER0010E": _("Could not delete user '%(user)s'."),
    "GINUSER0011E": _("User '%(user)s' does not exist."),
    "GINUSER0012E": _("Could not delete group '%(group)s'"),

    "GINFW0001E": _("Cannot update system firmware while running VMs."),
    "GINFW0002E": _("Firmware image unpack failed: rc = %(rc)s. "
                    "Details: %(err)s"),
    "GINFW0003E": _("FW update failed: "
                    "No image file found in the package file."),
    "GINFW0004E": _("Error flashing firmware. rc = %(rc)s. \
                     Please see /usr/sbin/update_flash for rc reasons."),
    "GINFW0005E": _("Error commiting firmware. rc = %(rc)s. \
                     Ensure you are booted to the temporary side."),
    "GINFW0006E": _("Error rejecting firmware. rc = %(rc)s. \
                     Ensure you are booted to the permanent side."),

    "GINHBK0001E": _('Failed to create tar archive "%(name)s", cmd: '
                     '"%(cmd)s". Inspect error log for more information.'),
    "GINHBK0002E": _('Failed to delete archive file "%(name)s".'),
    "GINHBK0003E": _('Failed to create archive dir "%(dir)s". '
                     'Inspect error log for more information.'),
    "GINHBK0004E": _('Description too long.'),
    "GINHBK0005E": _('Please check the uniqueness of the paths or patterns.'),
    "GINHBK0006E": _('Path or pattern is too long or too short.'),
    "GINHBK0007E": _('Invalid days_ago number.'),
    "GINHBK0008E": _('Invalid counts_ago number.'),
    "GINHBK0009E": _('Failed to create archive "%(identity)s". '
                     'Inspect error log for more information.'),
    "GINHBK0010E": _('Timeout while creating archive "%(identity)s", the '
                     'files might be too large for a configuration backup.'),

    "GINADAP0001E": _("SAN adapter '%(adapter)s' does not exist in the system."
                      ),

    "GINSEP0001E": _("Provide required parameters: hostname, port, community."
                     ),
    "GINSEP0002E": _("System hostname must be a valid string."),
    "GINSEP0003E": _("System port number must be an integer between 1 and \
                     65535."),
    "GINSEP0004E": _("SNMP community name must be a single word."),
    "GINSEP0005E": _("Error retrieving SEP subscribers data: '%(error)s'."),
    "GINSEP0006E": _("Hostname %(hostname)s not found."),
    "GINSEP0007E": _("Error loading SEP subscriptions data from server."),
    "GINSEP0008E": _("Error starting SEP service: '%(error)s'."),
    "GINSEP0009E": _("Error stopping SEP service: '%(error)s'."),
    "GINSEP0010E": _("Error subscribing SEP data to server: '%(error)s'."),
    "GINSEP0011E": _("Error deleting subscription: '%(error)s'."),

    "GINPOWER001E": _("Failed to retrieve power management profiles: \
                       Host OS does not support the tuned-adm package."),
    "GINPOWER002E": _("Failed to retrieve power management profiles: \
                       Daemon 'tuned-adm' is not active."),
    "GINPOWER003E": _("Failed to retrieve power management profiles: \
                       Package 'tuned-adm' is not installed."),
    "GINPOWER004E": _("Error activating power saving profile %(profile)s."),
    "GINFS00001E": _("Failed to retrieve details of the specified filesystem"),
    "GINFS00002E": _("Failed to unmount the filesystems"),
    "GINFS00003E": _("Parsing df output failed."),
    "GINFS00004E": _("error in filesystem get list util"),
    "GINFS00005E": _("error in filesystem info fetch util"),
    "GINFS00006E": _("Error in executing 'df -hT' command"),
    "GINFS00007E": _("Failed to mount the filesystem"),
    "GINFS00008E": _("error in unmount util"),
    "GINFS00009E": _("Require block dev to mount a filesystem"),
    "GINFS00010E": _("Require mount point to mount a filesystem"),

    "GINFS00011E": _("Unable to open fstab"),
    "GINFS00012E": _("Unable to write fstab"),
    "GINFS00013E": _("Failed to retrieve list of filesystems."),
    "GINFS00014E": _("required server ip addr"),
    "GINFS00015E": _("required remote share location"),
    "GINFS00016E": _("required type as local or nfs"),
    "GINFS00017E": _("Invalid type needs to be either local or nfs"),
    "GINFS00018E": _("NFS mount failed"),

    "GINSP00001E": _("File location required for creating a swap device."),
    "GINSP00002E": _("Type required for creating a swap device."),
    "GINSP00003E": _("Size is mandatory while creating file type swap device."),
    "GINSP00004E": _("Incorrect swap type, only 'device' and 'file' are allowed."),
    "GINSP00005E": _("Error creating a swap device. %(err)s "),
    "GINSP00006E": _("Error deleting a swap file."),
    "GINSP00007E": _("Error deleting a swap device. %(err)s"),
    "GINSP00008E": _("Swap device not found. %(name)s"),
    "GINSP00009E": _("Error deleting a swap file. %(err)s"),
    "GINSP00010E": _("Error parsing /proc/swaps file. %(err)s"),
    "GINSP00011E": _("Error creating a flat file. %(err)s"),
    "GINSP00012E": _("Unable to format swap device. %(err)s"),
    "GINSP00013E": _("Unable to activate swap device. %(err)s"),
    "GINSP00014E": _("Unable to parse 'swapon -s' output. %(err)s"),
    "GINSP00015E": _("Unable to get single swap device info. %(err)s"),
    "GINSP00016E": _("Unable to activate swap device. %(err)s"),
    "GINSP00017E": _("No partitions found for disk . %(disk)s"),
    "GINSP00018E": _("Single swap device %(swap)s not found."),
    "GINSP00019E": _("Unable to get single swap device info: directory /proc/swaps not found."),
    "GINSP00020E": _("File already in use."),

    "GINPART00001E": _("Fetching list of partitions failed"),
    "GINPART00002E": _("Create partition failed"),
    "GINPART00003E": _("Error retrieving information of partition %(name)s : %(err)s"),
    "GINPART00004E": _("Partition already mounted"),
    "GINPART00005E": _("Format partition failed"),
    "GINPART00006E": _("Change type for partition failed"),
    "GINPART00007E": _("Delete partition failed"),
    "GINPART00008E": _("Required parameter device name"),
    "GINPART00009E": _("Required parameter partition size"),
    "GINPART00011E": _("fdisk command failed"),
    "GINPART00012E": _("mkfs command failed"),
    "GINPART00013E": _("No partitions found"),
    "GINPART00014E": _("Partition %(name)s not found."),


    "GINPV00001E": _("Required pv_name parameter"),
    "GINPV00002E": _("Failed to create PV"),
    "GINPV00003E": _("Failed to fetch PV list"),
    "GINPV00004E": _("Failed to fetch PV details"),
    "GINPV00005E": _("Failed to delete PV"),
    "GINPV00006E": _("pvs command failed"),
    "GINPV00007E": _("Unable to get information of device %(dev)s, error: %(err)s"),
    "GINPV00008E": _("pvcreate command failed"),
    "GINPV00009E": _("Remove failed: error: %(err)s"),
    "GINPV00010E": _("Remove failed: device %(dev)s not found."),
    "GINPV00011E": _("Unable to find device %(dev)s ."),


    "GINVG00001E": _("Failed to create VG"),
    "GINVG00002E": _("Failed to list VGs"),
    "GINVG00003E": _("Failed to fetch VG details"),
    "GINVG00004E": _("Failed to delete VG"),
    "GINVG00005E": _("Failed to extend VG"),
    "GINVG00006E": _("Failed to reduce VG"),
    "GINVG00007E": _("vgs command failed"),
    "GINVG00008E": _("vgs command for given VG failed"),
    "GINVG00009E": _("vgcreate command failed"),
    "GINVG00010E": _("vgremove command failed"),
    "GINVG00011E": _("vgextend command failed"),
    "GINVG00012E": _("vgreduce command failed"),
    "GINVG00013E": _("Required vg_name parameter"),
    "GINVG00014E": _("Required pv_paths parameter"),

    "GINLV00001E": _("Required vg_name parameter"),
    "GINLV00002E": _("Required size parameter"),
    "GINLV00003E": _("Failed to create LV"),
    "GINLV00004E": _("Failed to list LVs"),
    "GINLV00005E": _("Failed to fetch LV details"),
    "GINLV00006E": _("Failed to delete LV"),
    "GINLV00007E": _("lvcreate command failed"),
    "GINLV00008E": _("lvs command failed"),
    "GINLV00009E": _("lvdisplay command failed"),
    "GINLV00010E": _("lvremove command failed"),

    "GINDASD0001E": _("Error in executing 'lsdasd -l' command"),
    "GINDASD0002E": _("Error in executing 'lsdasd -l bus_id' command"),
    "GINDASD0003E": _("Parsing lsdasd output failed"),
    "GINDASD0004E": _("Failed to format %(name)s. Either format currently going on or device not available for format. Please try after sometime."),
    "GINDASD0005E": _("Failed to retrieve list of DASD devices"),
    "GINDASD0006E": _("Failed to retrieve details of the specified DASD device"),
    "GINDASD0007E": _("Failed to find specified DASD device"),
    "GINDASD0008E": _("Failed to format %(name)s. Either format currently going on or device not available for format"),
    "GINDASD0009E": _("Require DASD device name to be formatted"),
    "GINDASD0010E": _("Require block size for formatting DASD device"),
    "GINDASD0011E": _("Invalid bus ID, %(bus_id)s"),
    "GINDASD0012E": _("Error in executing 'lscss -d' command : %(err)s"),
    "GINDASD0013E": _("Error in parsing 'lscss -d' command : %(err)s"),

    "GINDASDPAR0005E": _("Require name to create DASD device partition"),
    "GINDASDPAR0006E": _("Require partition size to create DASD device partition"),
    "GINDASDPAR0007E": _("Failed to create partition"),
    "GINDASDPAR0008E": _("Failed to retrieve list of DASD partitions"),
    "GINDASDPAR0009E": _("Failed to retrieve details of the specified DASD partition"),
    "GINDASDPAR0010E": _("Failed to delete partition"),

    "GINSYSMOD00001E": _("Error getting loaded module list: %(err)s"),
    "GINSYSMOD00002E": _("Module %(module)s not found."),
    "GINSYSMOD00003E": _("Error fetching info of module %(module)s, reason: %(err)s"),
    "GINSYSMOD00004E": _("Error loading module %(module)s, reason: %(err)s"),
    "GINSYSMOD00005E": _("Error unloading module %(module)s, reason: %(err)s"),

    "GINOVS00001E": _("Error executing OVS command. Please check if 'openvswitch' service is running."),
    "GINOVS00002E": _("Error executing OVS command: %(err)s"),
    "GINOVS00003E": _("Error creating OVS bridge %(name)s. OVS bridge already exists."),
    "GINOVS00004E": _("Error retrieving OVS bridge %(name)s. OVS bridge does not exist."),
    "GINOVS00005E": _("Error adding port %(port)s in bridge %(name)s. Port already exists."),
    "GINOVS00006E": _("Unable to create bond with less than two interfaces."),
    "GINOVS00007E": _("Bridge %(bridge)s does not have a bond named %(bond)s."),
    "GINOVS00008E": _("Interface %(iface)s not found in openvswitch database."),

    "GINSD00001E": _("Error executing 'ls -l /dev/disk/by-id, %(err)s"),
    "GINSD00002E": _("Error executing 'lsblk -Po, %(err)s"),
    "GINSD00003E": _("Error parsing 'ls -l /dev/disk/by-id', %(err)s"),
    "GINSD00004E": _("Error parsing 'lsblk -Po', %(err)s"),
    "GINSD00005E": _("Error getting list of storage devices, %(err)s"),
    "GINSD00006E": _("Error getting bus id of DASD device, %(err)s")
}
