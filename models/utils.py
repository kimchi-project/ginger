#
# Project Ginger
#
# Copyright IBM, Corp. 2015
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

import dasd_utils
import os
import platform
import re
import subprocess

from parted import Device as PDevice
from parted import Disk as PDisk

from wok.exception import NotFoundError, OperationFailed
from wok.utils import run_command, wok_log
from wok.plugins.gingerbase.disks import _get_dev_major_min
from wok.plugins.gingerbase.disks import _get_dev_node_path

sg_dir = "/sys/class/scsi_generic/"


def _get_swapdev_list_parser(output):
    """
    This method parses the output of 'cat /proc/swaps' command
    :param output: output of 'cat /proc/swaps' command
    :return:list of swap devices
    """
    output = output.splitlines()
    output_list = []

    try:
        for swapdev in output[1:]:
            dev_name = swapdev.split()[0]
            output_list.append(dev_name)
    except Exception as e:
        wok_log.error("Error parsing /proc/swaps file.")
        raise OperationFailed("GINSP00010E", {'err', e.message})

    return output_list


def _create_file(size, file_loc):
    """
    Create a flat file to be used as a swap device
    :param file_loc: file location
    :param size: size of the file
    :return:
    """
    out, err, rc = run_command(
        ["dd", "if=/dev/zero", "of=" + file_loc, "bs=" + size, "count=1"])

    if rc != 0:
        wok_log.error("Error creating a flat file. %s", file_loc)
        raise OperationFailed("GINSP00011E", {'err': err})

    # So that only root can see the content of the swap
    os.chown(file_loc, 0, 0)
    os.chmod(file_loc, 0o600)

    return


def _make_swap(file_loc):
    """
    Format a device as a swap device
    :param file_loc: file location or a device path
    :return:
    """

    out, err, rc = run_command(["mkswap", file_loc])

    if rc != 0:
        wok_log.error("Unable to format swap device. %s", file_loc)
        raise OperationFailed("GINSP00012E", {'err': err})
    return


def _activate_swap(file_loc):
    """
    Activate a swap device
    :param file_loc: file location or a device path
    :return:
    """
    out, err, rc = run_command(["swapon", file_loc])
    if rc != 0:
        wok_log.error("Unable to activate swap device. %s", file_loc)
        raise OperationFailed("GINSP00013E", {'err': err})
    return


def _parse_swapon_output(output):
    """
    :param output: output of 'grep -w devname /proc/swaps' command
    :return:
    """
    try:
        output_dict = {}
        output_list = output.split()
        output_dict['filename'] = output_list[0]
        output_dict['type'] = output_list[1]
        output_dict['size'] = output_list[2]
        output_dict['used'] = output_list[3]
        output_dict['priority'] = output_list[4]
    except Exception as e:
        wok_log.error("Unable to parse 'swapon -s' output")
        raise OperationFailed("GINSP00014E", {'err': e.message})

    return output_dict


def _get_swap_output(device_name):
    """
    :param device_name: swap device path
    :return:
    """
    out, err, rc = run_command(["grep", "-w", device_name, "/proc/swaps"])

    if rc == 1:
        wok_log.error("Single swap device %s not found.", device_name)
        raise NotFoundError("GINSP00018E", {'swap': device_name})

    elif rc == 2:
        wok_log.error("Unable to get single swap device info: /proc/swaps "
                      "dir not found.")
        raise OperationFailed("GINSP00019E")

    elif rc != 0:
        wok_log.error("Unable to get single swap device info. %s", device_name)
        raise OperationFailed("GINSP00015E", {'err': err})

    return _parse_swapon_output(out)


def _swapoff_device(device_name):
    """
    Remove a swap device
    :param device_name: file or device path
    :return:
    """
    out, err, rc = run_command(["swapoff", device_name])

    if rc != 0:
        wok_log.error("Unable to deactivate swap device. %s", device_name)
        raise OperationFailed("GINSP00016E", {'err': err})

    return


def get_dm_name(devname):
    """
    Get the device mapper path of the device
    :param devname: device name
    :return:
    """
    out = get_disks_by_id_out()
    out = out.splitlines()
    for line in out[1:]:
        if devname not in line:
            continue
        else:
            idcol = line.split()[-3]
            dmdev = idcol.split('-')[-1]
            return dmdev


def change_part_type(part, type_hex):
    """
    Change the type of the given partition
    :param part: partition number on the device
    :param type_hex: partition type in hex
    :return:
    """
    devname = ''.join(i for i in part if not i.isdigit())
    majmin = _get_dev_major_min(devname)

    dev_path = _get_dev_node_path(majmin)
    partnum = ''.join(filter(lambda x: x.isdigit(), part))

    device = PDevice(dev_path)
    disk = PDisk(device)
    parts = disk.partitions

    if len(parts) == 1:
        typ_str = '\nt\n' + type_hex + '\n' + 'w\n'
    elif len(parts) > 1:
        typ_str = '\nt\n' + partnum + '\n' + type_hex + '\n' + 'w\n'
    else:
        wok_log.error("No partitions found for disk,  %s", disk)
        raise OperationFailed("GINSP00017E",
                              {'disk': "No partitions found for disk " + disk})

    t1_out = subprocess.Popen(["echo", "-e", "\'", typ_str, "\'"],
                              stdout=subprocess.PIPE)
    t2_out = subprocess.Popen(["fdisk",
                               dev_path], stdin=t1_out.stdout,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    t1_out.stdout.close()
    out, err = t2_out.communicate()

    if t2_out.returncode != 0:
        wok_log.error("Unable to change the partition type.")
        raise OperationFailed("change type failed", err)

    return part


def create_disk_part(dev, size):
    """
    This method creates a partition on the specified device
    :param dev: path of the device for which partition is to be created
    :param size: size of the partition (e.g 10M)
    :return:
    """
    p_str = _form_part_str(size)
    p1_out = subprocess.Popen(["echo", "-e", "\'", p_str, "\'"],
                              stdout=subprocess.PIPE)
    p2_out = subprocess.Popen(["fdisk", dev], stdin=p1_out.stdout,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p1_out.stdout.close()
    out, err = p2_out.communicate()
    if p2_out.returncode != 0:
        raise OperationFailed("GINPART00011E", err)
    part_path = get_dev_part(dev)
    return part_path.split('/')[2]


def _form_part_str(size):
    """
    Forms the string containing the size to be used in fdisk command
    :param size:size of the partition
    :return:
    """
    part_str = '\nn\np\n\n\n' + '+' + size + '\n' + 'w\n'
    return part_str


def get_dev_part(dev):
    """
    This method fetches the path of newly created partition
    :param dev: path of the device which is partitioned
    :return:
    """
    part_paths = []
    device = PDevice(dev)
    disk = PDisk(device)
    parts = disk.partitions
    for part in parts:
        part_paths.append(part.path)
    return part_paths[len(part_paths) - 1]


def _is_mntd(partition_name):
    """
    Checks if the partition is already mounted
    :param partition_name: name of the partition
    :return:
    """
    mtd_out, err, rc = run_command(["grep", "-w",
                                    "^/dev/" + partition_name +
                                    "\s", "/proc/mounts"])
    if rc != 0:
        return False
    else:
        return True


def _makefs(fstype, name):
    """
    Formats the partition with the specified file system type
    :param fstype: type of filesystem (e.g ext3, ext4)
    :param name: name of the partition to be formatted (e.g sdb1)
    :return:
    """
    majmin = _get_dev_major_min(name)
    path = _get_dev_node_path(majmin)
    force_flag = '-F'
    if fstype == 'xfs':
        force_flag = '-f'
    fs_out, err, rc = run_command(["mkfs", "-t", fstype, force_flag, path])
    if rc != 0:
        raise OperationFailed("GINPART00012E", {'err': err})
    return


def delete_part(partname):
    """
    Deletes the specified partition
    :param partname: name of the partition to be deleted
    :return:
    """
    devname = ''.join(i for i in partname if not i.isdigit())
    majmin = _get_dev_major_min(devname)
    dev_path = _get_dev_node_path(majmin)
    partnum = ''.join(filter(lambda x: x.isdigit(), partname))
    device = PDevice(dev_path)
    disk = PDisk(device)
    parts = disk.partitions
    if len(parts) == 1:
        typ_str = '\nd\nw\n'
    elif len(parts) > 1:
        typ_str = '\nd\n' + partnum + '\n' + 'w\n'
    else:
        raise OperationFailed("GINPART00013E")
    d1_out = subprocess.Popen(["echo", "-e", "\'", typ_str, "\'"],
                              stdout=subprocess.PIPE)
    d2_out = subprocess.Popen(["fdisk", dev_path], stdin=d1_out.stdout,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    d1_out.stdout.close()
    out, err = d2_out.communicate()
    if d2_out.returncode != 0:
        raise OperationFailed("GINPART00011E", err)


def _get_pv_devices():
    """
    This method fetches the list of PV names
    :return:
    """
    cmd = ["pvs", "-o", "pv_name"]
    pvout, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINPV00006E", {'err': err})
    return parse_pvlist_output(pvout)


def parse_pvlist_output(pvsout):
    """
    This method parses the output of 'pvs -o pv_name' command
    :param pvsout: output of 'pvs -o pv_name
    :return:
    """
    outlist = []
    parsed_list = pvsout.splitlines()
    for i in parsed_list[1:]:
        outlist.append(i.strip())

    return outlist


def _pvdisplay_out(name):
    """
    This method fetches the details of particular PV
    :param name: path of the PV
    :return:
    """
    out, err, rc = run_command(["pvdisplay", name])
    if rc != 0:
        raise OperationFailed("GINPV00007E", {'err': err})
    return parse_pvdisplay_output(out)


def parse_pvdisplay_output(pvout):
    """
    This method parses the output of pvdisplay
    :param pvout: output of pvdisplay
    :return:
    """
    output = {}
    p = re.compile("^\s*(\w(\s?\w+)*)\s*(.+)?")
    parsed_out = pvout.splitlines()
    for i in parsed_out[1:]:

        m = p.match(i)
        if not m:
            continue

        output[m.group(1)] = m.group(3)

    return output


def _create_pv(name):
    """
    This method creates the PV
    :param name: path of the partition to be used as PV
    :return:
    """
    out, err, rc = run_command(["pvcreate", "-f", name])
    if rc != 0:
        raise OperationFailed("GINPV00008E", {'err': err})
    return


def _remove_pv(name):
    """
    This method removes the PV
    :param name: path of the pv to be removed
    :return:
    """
    out, err, rc = run_command(["pvremove", "-f", name])
    if rc != 0:
        raise OperationFailed("GINPV00009E", {'err': err})
    return


def _get_vg_list():
    """
    This method gets a list of volume group names
    :return:
    """
    cmd = ["vgs", "-o", "vg_name"]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00007E")
    return parse_pvlist_output(out)


def _vgdisplay_out(name):
    """
    This method gets the details of particular volume group
    :param name: Name of the volume group
    :return:
    """
    cmd = ["vgs", "-o", "vg_name,vg_sysid,"
                        "vg_fmt,vg_mda_count,vg_seqno,vg_permissions,"
                        "vg_extendable,max_lv,lv_count,max_pv,pv_count,"
                        "vg_size,vg_extent_size,pv_pe_count,"
                        "pv_pe_alloc_count,pv_used,vg_free_count,pv_free,"
                        "vg_uuid,pv_name", "--separator", ":", name]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00008E")
    return parse_vgdisplay_output(out)


def parse_vgdisplay_output(vgout):
    """
    This method parses the output of vgs command
    :param vgout: output of vgs command
    :return:
    """
    output = {}
    p = vgout.splitlines()
    for i in p[1:]:
        output['VG Name'] = i.split(':')[0]
        output['System ID'] = i.split(':')[1]
        output['Format'] = i.split(':')[2]
        output['Metadata Areas'] = i.split(':')[3]
        output['Metadata Sequence No'] = i.split(':')[4]
        output['Permission'] = i.split(':')[5]
        output['VG Status'] = i.split(':')[6]
        output['Max LV'] = i.split(':')[7]
        output['Cur LV'] = i.split(':')[8]
        output['Max PV'] = i.split(':')[9]
        output['Cur PV'] = i.split(':')[10]
        output['VG Size'] = i.split(':')[11]
        output['PE Size'] = i.split(':')[12]
        output['Total PE'] = i.split(':')[13]
        output['Alloc PE'] = i.split(':')[14]
        output['Alloc PE Size'] = i.split(':')[15]
        output['Free PE'] = i.split(':')[16]
        output['Free PE Size'] = i.split(':')[17]
        output['VG UUID'] = i.split(':')[18]
        if 'PV Names' in output:
            output['PV Names'].append(i.split(':')[19])
        else:
            output['PV Names'] = [i.split(':')[19]]
    return output


def _create_vg(name, path):
    """
    This method creates a volume group
    :param name: Name of the volume group
    :param path: list of PVs
    :return:
    """
    cmd = ["vgcreate", name] + [path[i] for i in range(len(path))]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00009E", {'err': err})
    return


def _remove_vg(name):
    """
    This method removes the volume group
    :param name: Name of the volume group
    :return:
    """
    cmd = ["vgremove", name]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00010E")
    return


def _extend_vg(name, paths):
    """
    This method extends the volume group
    :param name: Name of the volume group
    :param paths: list of PVs to be added
    :return:
    """
    cmd = ["vgextend", name] + [paths[i] for i in range(len(paths))]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00011E")
    return


def _reduce_vg(name, paths):
    """
    This method reduces the volume group
    :param name: Name of the volume group
    :param paths: list of PVs to be removed
    :return:
    """
    cmd = ["vgreduce", name] + [paths[i] for i in range(len(paths))]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00012E")
    return


def _create_lv(vgname, size):
    """
    This method creates the logical volume
    :param vgname: Name of the volume group
    :param size: Size of the logival volume
    :return:
    """
    cmd = ["lvcreate", vgname, "-L", size]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINLV00007E")
    return


def _get_lv_list():
    """
    This method fetches the list of existing logical volumes
    :return:
    """
    cmd = ["lvs", "-o", "lv_path"]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINLV00008E")
    return parse_pvlist_output(out)


def _lvdisplay_out(path):
    """
    This method fetches the details of the logical volume
    :param path: Path of the particular logical volume
    :return:
    """
    cmd = ["lvdisplay", path]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINLV00009E")
    return parse_lvdisplay_output(out)


def parse_lvdisplay_output(lvout):
    """
    This method parses the output of lvdisplay
    :param lvout: output of lvdisplay command
    :return:
    """
    output = {}
    p = re.compile("^\s{0,2}((\w+|\S)(\s|\S)\w*(\s\w+)?(\S*\s\w+)?)\s*(.+)?$")
    parsed_out = lvout.splitlines()
    for i in parsed_out[1:]:

        m = p.match(i)
        if not m:
            q = re.match("^\s*(\w+\s.+)$", i)
            if not q:
                continue
            else:
                out1 = output['LV snapshot status']
                output['LV snapshot status'] = out1 + " " + q.group(1)
                continue

        output[m.group(1)] = m.group(6)

    return output


def _remove_lv(name):
    """
    This method removes the logical volume
    :param name: Path of the logical volume
    :return:
    """
    cmd = ["lvremove", "-f", name]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINLV00010E")
    return


def get_disks_by_id_out():
    """
    Execute 'ls -l /dev/disk/by-id'
    :return: Output of 'ls -l /dev/disk/by-id'
    """
    cmd = ['ls', '-l', '/dev/disk/by-id']
    out, err, rc = run_command(cmd)
    if rc != 0:
        wok_log.error("Error executing 'ls -l /dev/disk/by-id.")
        raise OperationFailed("GINSD00001E", {'err': err})
    return out


def get_lsblk_keypair_out(transport=True):
    """
    Get the output of lsblk'
    :param transport: True or False for getting transport information
    :return: output of 'lsblk -Po <columns>'

    """
    if transport:
        cmd = ['lsblk', '-Po', 'NAME,TYPE,SIZE,TRAN']
    else:
        # Some distributions don't ship 'lsblk' with transport
        # support.
        cmd = ['lsblk', '-Po', 'NAME,TYPE,SIZE']

    out, err, rc = run_command(cmd)
    if rc != 0:
        wok_log.error("Error executing 'lsblk -Po")
        raise OperationFailed("GINSD00002E", {'err': err})
    return out


def parse_ll_out(ll_out):
    """
    Parse the output of 'ls -l /dev/disk/by-id' command
    :param ll_out: output of 'ls -l /dev/disk/by-id'
    :return: tuple containing dictionaries. First dictionary
            contains devices as keys and the second dictionary
            contains device ids as keys
    """

    return_dict = {}
    return_id_dict = {}

    try:
        out = ll_out.splitlines()
        for line in out[1:]:
            ls_columns = line.split()
            disk_id = ls_columns[-3]

            if disk_id.startswith(
                    'ccw-') and not re.search('ccw-.+\w{4}\.\w{2}$', disk_id):
                continue

            if disk_id.startswith('wwn-'):
                continue

            if disk_id.startswith('dm-uuid-mpath'):
                continue

            disk_name = ls_columns[-1]
            name = disk_name.split("/")[-1]

            disk_id_split = disk_id.split('-')
            skip_list = ['ccw', 'usb', 'ata']
            disk_type = disk_id_split[0]

            if disk_type not in skip_list:
                disk_id = disk_id_split[-1]

            return_dict[name] = disk_id

            if disk_id in return_id_dict:
                return_id_dict[disk_id].append(name)
            else:
                return_id_dict[disk_id] = [name]
    except Exception as e:
        wok_log.error("Error parsing 'ls -l /dev/disk/by-id'")
        raise OperationFailed("GINSD00003E", {'err': e.message})

    return return_dict, return_id_dict


def parse_lsblk_out(lsblk_out):
    """
    Parse the output of 'lsblk -Po'
    :param lsblk_out: output of 'lsblk -Po'
    :return: Dictionary containing information about
            disks on the system
    """
    try:
        out_list = lsblk_out.splitlines()

        return_dict = {}

        for disk in out_list:
            disk_info = {}
            disk_attrs = disk.split()

            disk_type = disk_attrs[1]
            if not disk_type == 'TYPE="disk"':
                continue

            if len(disk_attrs) == 4:
                disk_info['transport'] = disk_attrs[3].split("=")[1][1:-1]
            else:
                disk_info['transport'] = "unknown"

            disk_info['size'] = disk_attrs[2].split("=")[1][1:-1]
            return_dict[disk_attrs[0].split("=")[1][1:-1]] = disk_info

    except Exception as e:
        wok_log.error("Error parsing 'lsblk -Po")
        raise OperationFailed("GINSD00004E", {'err': e.message})

    return return_dict


def get_unformatted_dasd_devs():
    """
    Get the list of unformatted DASD devices
    """
    unformatted = []
    if platform.machine() == "s390x":
        dasd_devices = dasd_utils._get_lsdasd_devs()
        for device in dasd_devices:
            if device['status'] == 'n/f':
                uf_dev = {}
                uf_dev['type'] = 'dasd'
                uf_dev['name'] = device['name']
                uf_dev['mpath_count'] = 'N/A'
                uf_dev['size'] = device['size']
                uf_dev['id'] = device['uid']
                uf_dev['bus_id'] = device['bus-id']
                unformatted.append(uf_dev)
    return unformatted


def get_final_list():
    """
    Comprehensive list of storage devices found on the system
    :return:List of dictionaries containing the information about
            individual disk
    """
    try:
        out = get_lsblk_keypair_out(True)
    except OperationFailed:
        out = get_lsblk_keypair_out(False)

    final_list = []

    try:
        unfomatted_dasds = get_unformatted_dasd_devs()
        if unfomatted_dasds:
            final_list = unfomatted_dasds

        blk_dict = parse_lsblk_out(out)

        out = get_disks_by_id_out()
        ll_dict, ll_id_dict = parse_ll_out(out)

        for blk in blk_dict:
            final_dict = {}
            final_dict['name'] = blk
            final_dict['size'] = blk_dict[blk]['size']
            final_dict['type'] = blk_dict[blk]['transport']
            if blk in ll_dict:
                final_dict['id'] = ll_dict[blk]
                if final_dict['id'].startswith('ccw-'):
                    final_dict['type'] = 'dasd'

                block_dev_list = ll_id_dict[final_dict['id']]
                max_slaves = 1
                for block_dev in block_dev_list:
                    slaves = os.listdir('/sys/block/' + block_dev + '/slaves/')
                    if max_slaves < len(slaves):
                        max_slaves = len(slaves)

                final_dict['mpath_count'] = max_slaves

            if final_dict['type'] == 'dasd':
                final_dict['bus_id'] = get_dasd_bus_id(blk)

            if final_dict['type'] == 'fc':
                final_dict['hba_id'], final_dict['wwpn'], final_dict[
                    'fcp_lun'] = get_fc_path_elements(blk)

            if 'id' in final_dict:
                if final_dict['id'] in ll_id_dict:
                    final_dict['name'] = ll_id_dict[final_dict['id']][0]
                final_list.append(final_dict)
    except Exception as e:
        wok_log.error("Error getting list of storage devices")
        raise OperationFailed("GINSD00005E", {'err': e.message})

    return final_list


def get_dasd_bus_id(blk):
    """
    Get the bus id for the given DASD device
    :param blk: DASD Block device
    :return: BUS ID
    """
    try:
        bus_id = os.readlink(
            '/sys/block/' + blk + "/device").split("/")[-1]
    except Exception as e:
        wok_log.error("Error getting bus id of DASD device, " + blk)
        raise OperationFailed("GINSD00006E", {'err': e.message})

    return bus_id


def get_fc_path_elements(blk):
    """
    Get the FC LUN ID, remote wwpn and local host adapter
    for the given block device based on FC LUN
    :param blk: Block device
    :return: tuple containing Host Adapter, WWPN, LUN ID
    """

    wwpn = ''
    fcp_lun = ''
    hba_id = ''

    for sg_dev in os.listdir(sg_dir):
        # skip devices whose transport is not FC
        sg_dev_path = sg_dir + "/" + sg_dev
        if os.path.exists(sg_dev_path + "/device/wwpn"):
            if os.path.exists(
                    sg_dev_path + "/device/block/" + blk):
                wwpn = open(
                    sg_dev_path +
                    "/device/wwpn").readline().rstrip()
                fcp_lun = open(
                    sg_dev_path +
                    "/device/fcp_lun").readline().rstrip()
                hba_id = open(
                    sg_dev_path +
                    "/device/hba_id").readline().rstrip()
                break

    if not wwpn or not fcp_lun or not hba_id:
        wok_log.error(
            "Unable to find FC elements for given fc block device: " + blk)
        raise OperationFailed("GINSD00007E", {'blk': blk})

    return hba_id, wwpn, fcp_lun
