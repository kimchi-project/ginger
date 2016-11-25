# -*- coding: utf-8 -*-
#
# Project Ginger
#
# Copyright IBM Corp, 2016
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

import binascii
import fileinput
import glob
import os
import re
import subprocess
import sys

from distutils.version import LooseVersion
from parted import Device as PDevice
from parted import Disk as PDisk
from wok.exception import InvalidParameter, NotFoundError, OperationFailed
from wok.utils import run_command, wok_log
from wok.plugins.gingerbase.disks import _get_dev_major_min
from wok.plugins.gingerbase.disks import _get_dev_node_path

LVM_THR_VERSION = "2.02.116"

FC_PATHS = "/dev/disk/by-path/*fc*"
PATTERN_CCW = "ccw-(?P<hba_id>[\da-fA-F.]+)-zfcp-(?P<wwpn>[\w]+):" \
              "(?P<fcp_lun>[\w]+)$"
PATTERN_PCI = "pci-(?P<hba_id>[\da-fA-F.:]+)(-vport-(?P<vport>[\w]+))?-fc-" \
              "(?P<wwpn>[\w]+)-lun-(?P<fcp_lun>[\d]+)$"

DEV_TYPES = ["dasd-eckd", "zfcp"]
syspath_eckd = "/sys/bus/ccw/drivers/dasd-eckd/0.*/"
syspath_zfcp = "/sys/bus/ccw/drivers/zfcp/0.*/"
lscss = "lscss"
chccwdev = 'chccwdev'
LSCSS_DEV = "Device"
LSCSS_SUBCH = "Subchan"
LSCSS_DEVTYPE = "DevType"
LSCSS_CUTYPE = "CU Type"
LSCSS_USE = "Use"
LSCSS_PIM = "PIM"
LSCSS_PAM = "PAM"
LSCSS_POM = "POM"
LSCSS_CHPID = "CHPIDs"
HEADER_PATTERN = r'(' + re.escape(LSCSS_DEV) + r')\s+' \
                 r'(' + re.escape(LSCSS_SUBCH) + r')\.\s+' \
                 r'(' + re.escape(LSCSS_DEVTYPE) + r')\s+' \
                 r'(' + re.escape(LSCSS_CUTYPE) + r')\s+' \
                 r'(' + re.escape(LSCSS_USE) + r')\s+' \
                 r'(' + re.escape(LSCSS_PIM) + r')\s+' \
                 r'(' + re.escape(LSCSS_PAM) + r')\s+' \
                 r'(' + re.escape(LSCSS_POM) + r')\s+' \
                 r'(' + re.escape(LSCSS_CHPID) + r')$'
DASD_CONF = '/etc/dasd.conf'
ZFCP_CONF = '/etc/zfcp.conf'


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
        if "Text file busy" in err:
            raise InvalidParameter("GINSP00020E", {'file': file_loc})
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
        output_dict['size'] = int(output_list[2])
        output_dict['used'] = int(output_list[3])
        output_dict['priority'] = output_list[4]
    except Exception as e:
        raise OperationFailed("GINSP00014E", {'err': e.message})

    return output_dict


def _get_swap_output(device_name):
    """
    :param device_name: swap device path
    :return:
    """
    out, err, rc = run_command(["grep", "-w", device_name, "/proc/swaps"])

    if rc == 1:
        raise NotFoundError("GINSP00018E", {'swap': device_name})

    elif rc == 2:
        raise OperationFailed("GINSP00019E")

    elif rc != 0:
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
        raise OperationFailed("GINSP00016E", {'err': err})


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
        raise OperationFailed("GINSP00017E", {'disk': disk})

    t1_out = subprocess.Popen(["echo", "-e", "\'", typ_str, "\'"],
                              stdout=subprocess.PIPE)
    t2_out = subprocess.Popen(["fdisk",
                               dev_path], stdin=t1_out.stdout,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    t1_out.stdout.close()
    out, err = t2_out.communicate()

    if t2_out.returncode != 0:
        raise OperationFailed("GINSP00021E", {'err': err})

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
    :param size:size of the partition in Megabytes
    :return:
    """
    part_str = '\nn\np\n\n\n' + '+' + str(size) + 'M' + '\n' + 'w\n'
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
    pv_version = get_lvm_version()
    # Disabled unsupported options to vgs command below
    # a threshold version
    if LooseVersion(pv_version) < LooseVersion(LVM_THR_VERSION):
        below_threshold_version = True
        cmd = ['pvs', '-o', 'pv_name,vg_name,'
               'pv_size,'
               'pv_pe_count,pv_pe_alloc_count,'
               'pv_uuid,vg_extent_size,'
               'vg_free_count', "--separator", ":", name,
               "--units", "K"]
    else:
        below_threshold_version = False
        cmd = ['pvs', '-o', 'pv_name,vg_name,'
               'pv_size,pv_allocatable,'
               'pv_pe_count,pv_pe_alloc_count,'
               'pv_uuid,vg_extent_size,'
               'vg_free_count', "--separator", ":", name,
               "--units", "K"]
    out, err, rc = run_command(cmd)

    if rc == 5 and 'Failed to find device' in err:
        raise NotFoundError("GINPV00011E", {'dev': name})

    elif rc != 0:
        raise OperationFailed("GINPV00007E",
                              {'dev': name, 'err': err})

    return parse_pvdisplay_output(out, below_threshold_version)


def parse_pvdisplay_output(pvout, below_threshold_version):
    """
    This method parses the output of pvs command
    :param pvout: output of pvs command
    :param below_threshold_version: boolean denoting if we are below
    LVM_THR_VERSION
    :return:
    """
    output = {}
    p = pvout.splitlines()
    for i in p[1:]:
        output['PV Name'] = i.split(':')[0].strip()
        output['VG Name'] = i.split(':')[1].strip()
        output['PV Size'] = float(i.split(':')[2].strip()[:-1])
        if below_threshold_version:
            output['Allocatable'] = 'N/A'
            output['Total PE'] = int(i.split(':')[3].strip())
            output['Allocated PE'] = float(i.split(':')[4].strip())
            output['PV UUID'] = i.split(':')[5].strip()
            output['PE Size'] = float(i.split(':')[6].strip()[:-1])
            output['Free PE'] = int(i.split(':')[7].strip())
        else:
            output['Allocatable'] = i.split(':')[3].strip()
            output['Total PE'] = int(i.split(':')[4].strip())
            output['Allocated PE'] = float(i.split(':')[5].strip())
            output['PV UUID'] = i.split(':')[6].strip()
            output['PE Size'] = float(i.split(':')[7].strip()[:-1])
            output['Free PE'] = int(i.split(':')[8].strip())

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

    if rc == 5 and 'Device %s not found' % name in err:
        raise NotFoundError("GINPV00010E", {'dev': name})

    elif rc != 0:
        if 'PV %s belongs to Volume Group' % name in err:
            err = 'PV %s belongs to a Volume Group,\
                   please use vgreduce first' % name
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
    vg_version = get_lvm_version()
    # Disabled unsupported options to vgs command below
    # a threshold version
    if LooseVersion(vg_version) < LooseVersion(LVM_THR_VERSION):
        below_threshold_version = True
        cmd = ["vgs", "-o", "vg_name,vg_sysid,"
               "vg_fmt,vg_mda_count,vg_seqno,"
               "max_lv,lv_count,max_pv,pv_count,"
               "vg_size,vg_extent_size,pv_pe_count,"
               "pv_pe_alloc_count,pv_used,vg_free_count,pv_free,"
               "vg_uuid,pv_name", "--separator", ":", name,
               "--units", "B"]
    else:
        below_threshold_version = False
        cmd = ["vgs", "-o", "vg_name,vg_sysid,"
               "vg_fmt,vg_mda_count,vg_seqno,vg_permissions,"
               "vg_extendable,max_lv,lv_count,max_pv,pv_count,"
               "vg_size,vg_extent_size,pv_pe_count,"
               "pv_pe_alloc_count,pv_used,vg_free_count,pv_free,"
               "vg_uuid,pv_name", "--separator", ":", name,
               "--units", "B"]
    out, err, rc = run_command(cmd)
    if rc != 0:
        raise OperationFailed("GINVG00008E")
    return parse_vgdisplay_output(out, below_threshold_version)


def parse_vgdisplay_output(vgout, below_threshold_version):
    """
    This method parses the output of vgs command
    :param vgout: output of vgs command
    :param below_threshold_version: boolean denoting if we are below
    LVM_THR_VERSION
    :return:
    """
    output = {}
    p = vgout.splitlines()

    if len(p) < 2:
        return output

    vg_info = p[1].split(':')

    output['VG Name'] = vg_info[0]
    output['System ID'] = vg_info[1]
    output['Format'] = vg_info[2]
    output['Metadata Areas'] = vg_info[3]
    output['Metadata Sequence No'] = vg_info[4]

    if below_threshold_version:
        output['Permission'] = 'N/A'
        output['VG Status'] = 'N/A'
        output['Max LV'] = vg_info[5]
        output['Cur LV'] = int(vg_info[6])
        output['Max PV'] = vg_info[7]
        output['Cur PV'] = vg_info[8]
        output['VG Size'] = float(vg_info[9][:-1])
        output['PE Size'] = float(vg_info[10][:-1])
        output['Free PE'] = vg_info[14]
        output['VG UUID'] = vg_info[16]
    else:
        output['Permission'] = vg_info[5]
        output['VG Status'] = vg_info[6]
        output['Max LV'] = vg_info[7]
        output['Cur LV'] = int(vg_info[8])
        output['Max PV'] = vg_info[9]
        output['Cur PV'] = vg_info[10]
        output['VG Size'] = float(vg_info[11][:-1])
        output['PE Size'] = float(vg_info[12][:-1])
        output['Free PE'] = vg_info[16]
        output['VG UUID'] = vg_info[18]

    for i in p[1:]:
        if below_threshold_version:
            output['Free PE Size'] = \
                output.get('Free PE Size', 0) + float(i.split(':')[15][:-1])
            output['Alloc PE'] = \
                output.get('Alloc PE', 0) + int(i.split(':')[12])
            output['Total PE'] = \
                output.get('Total PE', 0) + int(i.split(':')[11])
            output['Alloc PE Size'] = \
                output.get('Alloc PE Size', 0) + float(i.split(':')[13][:-1])

        else:
            output['Free PE Size'] = \
                output.get('Free PE Size', 0) + float(i.split(':')[17][:-1])
            output['Alloc PE'] = \
                output.get('Alloc PE', 0) + int(i.split(':')[14])
            output['Total PE'] = \
                output.get('Total PE', 0) + int(i.split(':')[13])
            output['Alloc PE Size'] = \
                output.get('Alloc PE Size', 0) + float(i.split(':')[15][:-1])

        if 'PV Names' in output:
            if below_threshold_version:
                output['PV Names'].append(i.split(':')[17])
            else:
                output['PV Names'].append(i.split(':')[19])
        else:
            if below_threshold_version:
                output['PV Names'] = [i.split(':')[17]]
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
    if rc == 5:
        raise InvalidParameter("GINVG00015E", {'err': err})
    elif rc != 0:
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
    if rc == 5:
        raise InvalidParameter("GINVG00016E", {'err': err})
    elif rc != 0:
        raise OperationFailed("GINVG00012E", {'err': err})

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
        raise OperationFailed("GINSD00001E", {'err': err})
    return out


def get_lsblk_keypair_out(transport=True):
    """
    Get the output of lsblk'
    :param transport: True or False for getting transport information
    :return: output of 'lsblk -Po <columns>'

    """
    if transport:
        cmd = ['lsblk', '-Pbo', 'NAME,TYPE,SIZE,TRAN']
    else:
        # Some distributions don't ship 'lsblk' with transport
        # support.
        cmd = ['lsblk', '-Pbo', 'NAME,TYPE,SIZE']

    out, err, rc = run_command(cmd)
    if rc != 0:
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

            if disk_id.startswith('dm-name'):
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
        raise OperationFailed("GINSD00003E", {'err': e.message})

    return return_dict, return_id_dict


def parse_lsblk_out(lsblk_out):
    """
    Parse the output of 'lsblk -Pbo'
    :param lsblk_out: output of 'lsblk -Pbo'
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

            disk_info['size'] = int(disk_attrs[2].split("=")[1][1:-1])
            disk_info['size'] = disk_info['size'] / (1024 * 1024)
            return_dict[disk_attrs[0].split("=")[1][1:-1]] = disk_info

    except Exception as e:
        raise OperationFailed("GINSD00004E", {'err': e.message})

    return return_dict


def get_fc_path_elements():
    """
    Get the FC LUN ID, remote wwpn and local host adapter
    for all the 'fc' type block devices.
    :return: dictionary containing key as block device and value as
    dictionary of Host Adapter, WWPN, LUN ID
    e.g. for s390x:
         {'sda': {'wwpn': '0x5001738030bb0171',
                 'fcp_lun': '0x00df000000000000',
                 'hba_id': '0.0.7100'},
          'sdb': {'wwpn': '0x5001738030bb0171',
                  'fcp_lun': '0x41cf000000000000',
                  'hba_id': '0.0.7100'},}
    """
    fc_blk_dict = {}

    fc_devs = glob.glob(FC_PATHS)
    for path in fc_devs:
        blkdev = os.path.basename(os.path.realpath(path))

        try:
            pattern = re.compile(PATTERN_PCI)
            blk_info_dict = pattern.search(path).groupdict()
        except:
            try:
                pattern = re.compile(PATTERN_CCW)
                blk_info_dict = pattern.search(path).groupdict()
            except:
                # no pattern match, probably a partition (...-partN), ignore it
                continue

        fc_blk_dict[blkdev] = blk_info_dict

    return fc_blk_dict


def _get_deviceinfo(lscss_out, device):
    """
    :param lscss_out: out of lscss command
    :param device: device id for which we need info to be returned
    :return: device info dict for the device from lscss output
    """
    device_pattern = r'(' + re.escape(device) + r')\s+' \
        r'(\d\.\d\.[0-9a-fA-F]{4})\s+' \
        r'(\w+\/\w+)\s+' \
        r'(\w+\/\w+)\s' \
        r'(\s{3}|yes)\s+' \
        r'([0-9a-fA-F]{2})\s+' \
        r'([0-9a-fA-F]{2})\s+' \
        r'([0-9a-fA-F]{2})\s+' \
        r'(\w+\s\w+)'
    if device:
        device = get_row_data(lscss_out, HEADER_PATTERN, device_pattern)
        msg = 'The device is %s' % device
        wok_log.debug(msg)
        try:
            device_info = _format_lscss(device)
            return device_info
        except KeyError as e:
            wok_log.error('lscss column key not found')
            raise e
    else:
        return device


def _format_lscss(device):
    """
    method to reform dictionary with new keys for lscss device
    :param device: device dictionary with keys "
            Device", "Subchan", "DevType",
            "CU Type", "Use", "PIM", "PAM",
            "POM", "CHPIDs"
    :return: dictionary with new keys mapped as follows
             "Device" - "device", "Subchan" - "sub_channel",
             "DevType" - "device_type"
             "CU Type" - "cu_type", "PIM, PAM, POM, CHPIDs" -
             "enabled_chipids" and "installed_chipids"
             "Use" is mapped as "status" and its value is
             mapped as "online" or "offline"
    """
    if device:
        try:
            status = 'offline'
            if device[LSCSS_USE] == 'yes':
                status = 'online'
            device['status'] = status
            del device[LSCSS_USE]
            device['device'] = device.pop(LSCSS_DEV)
            device['sub_channel'] = device.pop(LSCSS_SUBCH)
            device['device_type'] = device.pop(LSCSS_DEVTYPE)
            device['cu_type'] = device.pop(LSCSS_CUTYPE)
            pim = device.pop(LSCSS_PIM)
            pam = device.pop(LSCSS_PAM)
            del device[LSCSS_POM]
            chipid = device.pop(LSCSS_CHPID)
            if pim == pam:
                binaryval_pam = _hex_to_binary(pam)
                device['enabled_chipids'] = _get_paths(binaryval_pam, chipid)
                device['installed_chipids'] = device['enabled_chipids']
            else:
                binaryval_pam = _hex_to_binary(pam)
                device['enabled_chipids'] = _get_paths(binaryval_pam, chipid)
                binaryval_pim = _hex_to_binary(pim)
                device['installed_chipids'] = _get_paths(binaryval_pim, chipid)
        except KeyError as e:
            wok_log.error('Issue while formating lscss dictionary output')
            raise e
    return device


def _byte_to_binary(n):
    """
    Converts each byte into binary value i.e. sets of 0 and 1
    """
    return ''.join(str((n & (1 << i)) and 1) for i in reversed(range(8)))


def _hex_to_binary(h):
    """
    Return the actual bytes of data represented by the
    hexadecimal string specified as the parameter.
    """
    return ''.join(_byte_to_binary(ord(b)) for b in binascii.unhexlify(h))


def _get_paths(mask, chipid):
    """
    method to return the enabled or installed paths of chipid.
    :param mask: the binary value for the pam or pim.
    :return: list of available or installed paths of the chipid value.
    """
    chipids = [chipid[i:i + 2] for i in range(0, len(chipid), 2)]
    chipid_paths = []
    for index, j in enumerate(mask):
        if j == '1':
            chipid_paths.append(chipids[index])
    return chipid_paths


def _get_zfcp_devices():
    """
    Return list of zfcp devices
    """
    device_paths = get_directories(syspath_zfcp)
    zfcp_devices = []
    for path in device_paths:
        device = get_dirname(path)
        if device:
            zfcp_devices.append(device)
    return zfcp_devices


def get_row_data(command_output, header_pattern, value_pattern):
    """
    return a dictionary for particular row, in which row is
    mapped as values to the header keys
    dictionary is prepared based on first matched row
    header pattern and value pattern should be unique to
    retrieve header and particular row in command output

    :param command_output: Command output is provided as input to this api
    :param header_pattern:This pattern is needed to parse the header
        of the command output to define the keys
    :param value_pattern: This pattern is needed to search particular row,
                        the values of the row are assigned to
                        corresponding header key
    :return: dictionary

    eg.
    command_output is as below"
    Device   Subchan.  DevType CU Type Use  PIM PAM POM  CHPIDs
    ----------------------------------------------------------------------
    0.0.0200 0.0.0000  3390/0a 3990/e9 yes  e0  e0  ff   b0b10d00 00000000
    0.0.0201 0.0.0001  3390/0a 3990/e9 yes  e0  e0  ff   b0b10d00 00000000
    0.0.0202 0.0.0002  3390/0c 3990/e9      e0  e0  ff   b0b10d00 00000000

    This will return:
    {"Device":"0.0.0200", "Subchan": "0.0.0000",
                "DevType": "3390/0a", "CU Type":"3990/e9",
                "Use": "yes", "PIM": e0, "PAM": "e0",
                "POM": "ff", "CHPIDs": "b0b10d00 00000000"
    }, the first match to the value_pattern
    """
    header = re.search(header_pattern, command_output, re.M | re.I)
    value = re.search(value_pattern, command_output, re.M | re.I)
    row_data = {}
    if header is None or not header.group():
        raise OperationFailed("GINDASD0015E")
    elif value:
        if (header.group() != value.group()) and \
                (len(header.groups()) == len(value.groups())):
            for cnt in range(1, len(header.groups()) + 1):
                row_data[header.group(cnt)] = value.group(cnt)
    return row_data


def get_dirname(path):
    """
    This method extracts last directory name in given path
    :param path: example /usr/lib/
    :return: directory name for valid path separated
            by "/" or None if path is None
            for above example it returns "lib"
    """
    if path:
        split_index = -1
        if path.endswith("/"):
            split_index = -2
        dirname = path.split("/")[split_index]
        return dirname
    else:
        return None


def get_directories(path_pattern):
    """
    this is a method to get list of directories in given directory path
    path_pattern: This is pattern for the path for
          which it will get the directories.
          e.g. if path = "/sys/bus/ccw/drivers/dasd-eckd/*/"
          it return list of all the directories under
          "/sys/bus/ccw/drivers/dasd-eckd/"
          And if path = "/sys/bus/ccw/drivers/dasd-eckd/"
          then it will return just ["dasd-eckd"]
    Returns list of all the directories for given path pattern.
    """
    paths = glob.glob(path_pattern)
    return paths


def _parse_lvm_version(lvm_version_out):
    """
    Parse the output of to get LVM version
    :param lvm_version_out: first line of the 'lvm version' command output
    :return: version string
    """
    p = re.compile("\s+(\d+.\d+.\d+)")
    m = p.match(lvm_version_out)
    try:
        lvm_version = m.group(1)
    except Exception as e:
        raise OperationFailed("GINLVM0001E", {'err': e.message})

    return lvm_version


def get_lvm_version():
    """
    Get the version of the installed LVM
    :return: version string
    """
    out, err, rc = run_command(
        ["lvm", "version"])

    if rc != 0:
        raise OperationFailed("GINLVM0002E", {'err': err})

    try:
        out = out.splitlines()[0].split(":")[1]
    except Exception as e:
        raise OperationFailed("GINLVM0003E", {'err': e.message})

    return _parse_lvm_version(out)


def iscsi_discovery(target_ipaddress):
    """
    This function returns the list of discovered iSCSI targets
    Args:
        target_ipaddress: IP Address of the target host

    Returns: Parsed output of the iSCSI target discovery

    """
    out, err, rc = run_command(
        ["iscsiadm", "-m", "discovery",
            "-t", "sendtargets", "-p", target_ipaddress,
            "-o", "delete", "-o", "new"])

    if rc == 4:
        raise OperationFailed("GINISCSI004E", {'host': target_ipaddress})
    if rc != 0:
        raise OperationFailed("GINISCSI002E", {'err': err})

    try:
        out = parse_iscsi_discovery(out)
        return out
    except Exception as e:
        raise OperationFailed("GINISCSI003E", {'err': e.message})


def parse_iscsi_discovery(iscsiadm_output):
    """
    Parse the output of iSCSI discovery command
    Args:
        iscsiadm output: Output of iSCSI discovery command

    Returns: List of Dictionaries of parsed output

    """

    p = re.compile("(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}):(\d+),\d+\s+(\S+)")
    parsed_out = iscsiadm_output.splitlines()
    iqn_list = []

    try:
        for line in parsed_out:
            m = p.match(line)
            if m:
                target_ipaddress = m.group(1)
                target_port = m.group(2)
                iqn = m.group(3)
                iqn_list.append({"target_ipaddress": target_ipaddress,
                                 "target_port": target_port, "iqn": iqn})
    except Exception as e:
        raise OperationFailed(
            "GINISCSI010E", {
                'err': e.message, 'output': iscsiadm_output})

    return iqn_list


def get_discovered_iscsi_qns():
    """
    List the already discovered iSCSI targets on the system
    Returns: Dictionary of discovered IQNs

    """
    discovered_iqns = {}
    iqn_list = []

    try:
        iscsiadm_db_path = '/etc/iscsi/nodes'
        if not os.path.exists(iscsiadm_db_path):
            iscsiadm_db_path = '/var/lib/iscsi/nodes'

        discovered_iqns_list = os.listdir(iscsiadm_db_path) \
            if os.path.isdir(iscsiadm_db_path) else []

        for discovered_iqn in discovered_iqns_list:
            discovered_iqns[discovered_iqn] = False

        current_sessions = os.listdir('/sys/class/iscsi_session') if \
            os.path.isdir('/sys/class/iscsi_session') else []

        # Iterate over all sessions once for efficiency instead of
        # calling is_target_logged_in function below for every iqn
        for session in current_sessions:
            target_name = open(
                '/sys/class/iscsi_session/' +
                session +
                '/targetname').readline().rstrip()
            discovered_iqns[target_name] = True

        for iqn, status in discovered_iqns.iteritems():
            iqn_list.append({'iqn': iqn, 'status': status,
                             'targets': get_iscsi_iqn_auth_info(iqn)})

    except Exception as e:
        raise OperationFailed("GINISCSI005E", {'err': e.__str__()})

    return iqn_list


def get_iqn_info(iqn):
    """
    Basic information about iqn
    Args:
        iqn: IQN

    Returns: Dictionary containing basic info about given IQN

    """
    return {'iqn': iqn, 'status': is_target_logged_in(
        iqn), 'targets': get_iscsi_iqn_auth_info(iqn)}


def is_target_logged_in(iqn):
    """
    Returns True if iqn is logged in, otherwise returns False
    Args:
        iqn: IQN

    Returns: True or False for logged in status of iqn

    """
    logged_in_status = False

    try:
        if get_iscsi_session_id(iqn):
            logged_in_status = True

    except Exception as e:
        raise OperationFailed("GINISCSI006E", {'err': e.message, 'iqn': iqn})

    return logged_in_status


def iscsi_target_login(iqn):
    """

    Log into an iSCSI target using the given IQN
    :param iqn: IQN
    :return:
    """
    out, err, rc = run_command(
        ["iscsiadm", "-m", "node",
            "-T", iqn, "--login"])

    if rc != 0:
        raise OperationFailed("GINISCSI007E", {'err': err, 'iqn': iqn})


def iscsi_target_logout(iqn):
    """
    Log out of an iSCSI target using the given IQN
    :param iqn: IQN
    :return:
    """
    out, err, rc = run_command(
        ["iscsiadm", "-m", "node",
            "-T", iqn, "--logout"])

    if rc != 0:
        raise OperationFailed("GINISCSI008E", {'err': err, 'iqn': iqn})


def iscsi_delete_iqn(iqn):
    """
    Delete the IQN from iscsiadm database
    :param iqn:
    :return:
    """
    out, err, rc = run_command(
        ["iscsiadm", "-m", "node",
            "-o", "delete", "-T", iqn])

    if rc != 0:
        raise OperationFailed("GINISCSI009E", {'err': err, 'iqn': iqn})


def iscsiadm_update_db(iqn, db_key, db_key_value):
    """
    Method to update the iscsiadm db
    Args:
        iqn: iSCSI Qualified Name
        db_key: DB Key
        db_key_value: New Value for the DB Key

    Returns: None

    """
    out, err, rc = run_command(
        ["iscsiadm", "--m", "node", "--targetname",
         iqn, "--op=update", "--name",
         db_key, "--value=" + db_key_value])

    if rc != 0:
        raise OperationFailed(
            "GINISCSI011E", {
                'err': err, 'iqn': iqn, 'db_key': db_key})


def _parse_session_dir_name(session):
    """
    Parse the directory name of the iSCSI session
    to extract the session ID
    :param session: Directory name of the session
    :return: session ID
    """
    session_id = None
    try:
        session_id = session.split("session")[-1]
    except Exception as e:
        raise OperationFailed(
            "GINISCSI013E", {
                'err': e.message, 'session': session})
    return session_id


def get_iscsi_session_id(iqn):
    """
    Get the session ID of the given logged in target
    :param iqn: iSCSI Qualified Name
    :return: Session ID of the target
    """
    iscsi_session_id = None
    try:
        current_sessions = os.listdir('/sys/class/iscsi_session')

        for session in current_sessions:
            target_name = open(
                '/sys/class/iscsi_session/' +
                session +
                "/targetname").readline().rstrip()
            if iqn == target_name:
                iscsi_session_id = _parse_session_dir_name(session)
                break
    except Exception as e:
        raise OperationFailed("GINISCSI014E", {'err': e.message, 'iqn': iqn})

    return iscsi_session_id


def iscsi_rescan_target(iqn):
    """
    Rescan the given target IQN
    :param iqn: iSCSI Qualified Name
    :return:
    """
    session_id = get_iscsi_session_id(iqn)

    if not session_id:
        raise InvalidParameter("GINISCSI016E", {'iqn': iqn})

    out, err, rc = run_command(
        ["iscsiadm", "-m", "session",
            "-r", session_id, "--rescan"])

    if rc != 0:
        raise OperationFailed("GINISCSI015E", {'err': err, 'iqn': iqn})


def modify_iscsid_initiator_auth(auth_type, username, password):
    """
    Modify iSCSI initiator auth globally
    :param enable:
    :return:
    """
    iscsi_auth_info = get_iscsi_auth_info()
    if auth_type == 'CHAP':
        if iscsi_auth_info['node.session.auth.authmethod'] != 'CHAP':
            modify_iscsid_conf('node.session.auth.authmethod', auth_type)
        modify_iscsid_conf('node.session.auth.username', username)
        modify_iscsid_conf('node.session.auth.password', password)
    elif auth_type == 'None':
        if iscsi_auth_info['node.session.auth.username_in'] == 'None':
            modify_iscsid_conf('node.session.auth.authmethod', auth_type)
        modify_iscsid_conf('node.session.auth.username', username)
        modify_iscsid_conf('node.session.auth.password', password)
    else:
        raise InvalidParameter('GINISCSI012E')


def modify_iscsid_target_auth(auth_type, username, password):
    """
    Modify iSCSI target auth globally
    :param enable:
    :return:
    """
    iscsi_auth_info = get_iscsi_auth_info()
    if auth_type == 'CHAP':
        if iscsi_auth_info['node.session.auth.authmethod'] != 'CHAP':
            modify_iscsid_conf('node.session.auth.authmethod', auth_type)
        modify_iscsid_conf('node.session.auth.username_in', username)
        modify_iscsid_conf('node.session.auth.password_in', password)
    elif auth_type == 'None':
        if iscsi_auth_info['node.session.auth.username'] == 'None':
            modify_iscsid_conf('node.session.auth.authmethod', auth_type)
        modify_iscsid_conf('node.session.auth.username_in', username)
        modify_iscsid_conf('node.session.auth.password_in', password)
    else:
        raise InvalidParameter('GINISCSI012E')


def modify_iscsid_discovery_initiator_auth(auth_type, username, password):
    """
    Modify iSCSI discovery initiator auth globally
    :param enable:
    :return:
    """
    iscsi_auth_info = get_iscsi_auth_info()
    if auth_type == 'CHAP':
        if iscsi_auth_info['discovery.sendtargets.auth.authmethod'] != 'CHAP':
            modify_iscsid_conf(
                'discovery.sendtargets.auth.authmethod', auth_type)
        modify_iscsid_conf('discovery.sendtargets.auth.username', username)
        modify_iscsid_conf('discovery.sendtargets.auth.password', password)
    elif auth_type == 'None':
        if iscsi_auth_info['discovery.sendtargets.auth.username_in'] == 'None':
            modify_iscsid_conf(
                'discovery.sendtargets.auth.authmethod', auth_type)
        modify_iscsid_conf('discovery.sendtargets.auth.username', username)
        modify_iscsid_conf('discovery.sendtargets.auth.password', password)
    else:
        raise InvalidParameter('GINISCSI012E')


def modify_iscsid_discovery_target_auth(auth_type, username, password):
    """
    Modify iSCSI discovery target auth globally
    :param enable:
    :return:
    """
    iscsi_auth_info = get_iscsi_auth_info()
    if auth_type == 'CHAP':
        if iscsi_auth_info['discovery.sendtargets.auth.authmethod'] != 'CHAP':
            modify_iscsid_conf(
                'discovery.sendtargets.auth.authmethod', auth_type)
        modify_iscsid_conf('discovery.sendtargets.auth.username_in', username)
        modify_iscsid_conf('discovery.sendtargets.auth.password_in', password)
    elif auth_type == 'None':
        if iscsi_auth_info['discovery.sendtargets.auth.username'] == 'None':
            modify_iscsid_conf(
                'discovery.sendtargets.auth.authmethod', auth_type)
        modify_iscsid_conf('discovery.sendtargets.auth.username_in', username)
        modify_iscsid_conf('discovery.sendtargets.auth.password_in', password)
    else:
        raise InvalidParameter('GINISCSI012E')


def modify_iscsid_conf(parameter, value):
    """
    Modify iSCSI global configuration file /etc/iscsi/iscsid.conf
    :param parameter: parameter to be modified
    :param value: modified value of the parameter
    :return:
    """

    try:
        with open('/etc/iscsi/iscsid.conf', 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            for line in lines:
                if re.match('^#?\s*' +
                            (parameter[1:] if
                             parameter.startswith("#") else parameter) +
                            '\s', line) is not None:
                    if not value or value == 'None':
                        line = '#' + parameter + ' = ' + 'None' + '\n'
                    else:
                        line = parameter + ' = ' + value + '\n'
                f.write(line)
    except Exception as e:
        raise OperationFailed(
            "GINISCSI017E", {
                'err': e.message, 'parameter': parameter, 'value': value})


def get_iscsi_auth_info():
    """
    Get Global iSCSI auth info from /etc/iscsi/iscsid.conf
    :return: Dictionary containing global iSCSI auth info
    """
    info_map = {}
    try:
        f = open('/etc/iscsi/iscsid.conf', 'r')
        lines = f.readlines()
        for line in lines:
            if re.match(
                    '^#?' + "node.session.auth",
                    line) is not None or re.match(
                    '^#?' + "discovery.sendtargets.auth",
                    line) is not None:
                info_key, info_value = line.split("=")
                if line.startswith("#"):
                    info_key = info_key[1:].strip()
                    info_value = 'None'
                    info_map[info_key] = info_value
                    continue
                info_map[info_key.strip()] = info_value.strip()
    except Exception as e:
        raise OperationFailed("GINISCSI018E", {'err': e.message})

    return info_map


def get_iscsi_iqn_auth_info(iqn):
    """
    Get IQN specific auth info
    :param iqn: iSCSI Qualified Name
    :return: List containing target auth info
    """
    info_list = []
    iscsiadm_db_path = '/etc/iscsi/nodes/'
    if not os.path.exists(iscsiadm_db_path):
        iscsiadm_db_path = '/var/lib/iscsi/nodes/'

    iqn_db_path = iscsiadm_db_path + iqn + '/'
    try:
        iqn_dir = os.listdir(iqn_db_path)
        for iqn_target in iqn_dir:
            info_map = {}
            f = open(iqn_db_path + iqn_target + '/default')
            lines = f.readlines()
            auth_info = {}
            for line in lines:
                if re.match(
                        'node.session.auth',
                        line) is not None or re.match(
                        'discovery.sendtargets.auth',
                        line) is not None:
                    info_key, info_value = line.split("=")
                    auth_info[info_key.strip()] = info_value.strip()

                if re.match('node.discovery_address', line) is not None:
                    ip_address = line.split("=")[1].strip()
                    info_map['target_address'] = ip_address

                if re.match('node.discovery_port', line) is not None:
                    port = line.split("=")[1].strip()
                    info_map['target_port'] = port

            security_params = [
                'discovery.sendtargets.auth.authmethod',
                'discovery.sendtargets.auth.username',
                'discovery.sendtargets.auth.username_in',
                'discovery.sendtargets.auth.password',
                'discovery.sendtargets.auth.password_in',
                'node.session.auth.authmethod',
                'node.session.auth.username',
                'node.session.auth.username_in',
                'node.session.auth.password',
                'node.session.auth.password_in']

            for sec_param in security_params:
                if sec_param not in auth_info:
                    auth_info[sec_param] = 'None'

            info_map['auth'] = auth_info
            info_list.append(info_map)
    except Exception as e:
        raise OperationFailed("GINISCSI019E", {'err': e.message, 'iqn': iqn})

    return info_list


def del_lines_of_attribute(key_string, conf):
    try:
        for line in fileinput.input(conf, inplace=True):
            my_regex = \
                "(#)+(" + re.escape(key_string) + ")+\s*\W+\s*(\W+\w+)*"
            if not re.match(my_regex, line):
                sys.stdout.write(line)

        for line in fileinput.input(conf, inplace=True):
            my_regex = "(" + re.escape(key_string) + ")+\s*\W+\s*(\W+\w+)*"
            if not re.match(my_regex, line):
                sys.stdout.write(line)
    except Exception:
        raise OperationFailed("GINAUDISP0002E", {"name": conf})


def write_to_conf(key, value, conf):
    try:
        with open(conf, 'a+') as conf_file:
            conf_file.write(key + " = " + value + "\n")
            conf_file.close()
    except Exception:
        raise OperationFailed("GINAUDISP0003E", {"name": conf})
