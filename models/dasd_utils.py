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

import os.path
import re
import subprocess

from parted import Device as PDevice
from parted import Disk as PDisk
from wok.exception import InvalidParameter, OperationFailed
from wok.utils import run_command, wok_log


def _get_lsdasd_devs():
    """
    Executes 'lsdasd -l' command and returns
    :return: output of 'lsdasd -l' command
    """
    command = ['lsdasd', '-l']
    dasdout, err, rc = run_command(command)
    if rc:
        wok_log.error("lsdasd -l failed")
        raise OperationFailed("GINDASD0001E", {'err': err})
    return _parse_lsdasd_output(dasdout)


def _get_dasd_dev_details(bus_id):
    """
    Executes 'lsdasd -l bus_id' command and returns
    :return: details of device with given bus_id
    """
    command = ['lsdasd', '-l', bus_id]
    dasdout, err, rc = run_command(command)
    if rc:
        wok_log.error("Fetching details of DASD device %s failed" % bus_id)
        raise OperationFailed("GINDASD0002E", {'err': err})
    return _parse_lsdasd_output(dasdout)


def _parse_lsdasd_output(output):
    """
    This method parses the output of 'lsdasd' command.
    :param output: Output of the 'lsdasd' command
    :return: list containing DASD devices information
    """
    try:
        split_out = output.split("\n\n")
        out_list = []
        len_dasd = len(split_out)-1
        for i in split_out[:len_dasd]:
            fs_dict = {}
            p = re.compile(r'^\s+(\w+)\:\s+(.+)$')
            parsed_out = i.splitlines()
            first_spl = i.splitlines()[0].split("/")
            fs_dict['bus-id'] = first_spl[0]
            fs_dict['name'] = first_spl[1]
            fs_dict['device'] = first_spl[2]
            for fs in parsed_out[1:]:
                m = p.search(fs)
                if not m:
                    continue
                fs_dict[m.group(1)] = m.group(2)
                if fs_dict['status'] == 'n/f':
                    fs_dict['blksz'] = 'None'
                    fs_dict['blocks'] = 'None'
            if fs_dict['size'] == '\t':
                fs_dict['size'] = 'Unknown'
            out_list.append(fs_dict)
    except:
        wok_log.error("Parsing lsdasd output failed")
        raise OperationFailed("GINDASD0003E")

    return out_list


def _format_dasd(blk_size, dev):
    """
    This method formats a DASD device dev with block size blk_size
    :param blk_size: block size for formatting of DASD device
    :param dev: name of DASD device to be formatted
    :return:
    """
    dev_name = '/dev/' + dev
    command = ['dasdfmt', '-b', blk_size, '-y', dev_name, '-p']
    fmtout, err, rc = run_command(command)
    if rc:
        wok_log.error("Formatting of DASD device %s failed", dev_name)
        raise OperationFailed("GINDASD0004E", {'err': err})
    return


def _get_dasd_names(check=False):
    """
    Fetches list of names of all DASD devices
    :return: list of names of all DASD devices
    """
    names = set()
    for dev in _get_lsdasd_devs():
        name = dev['name'].split()[0]
        names.add(name)

    return list(names)


def _get_lsblk_devs(keys, devs=[]):
    """
    Executes 'lsblk -Pbo' command and returns
    :return: output of 'lsblk -Pbo' command
    """
    lsblk = subprocess.Popen(
        ["lsblk", "-Pbo"] + [','.join(keys)] + devs,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = lsblk.communicate()
    if lsblk.returncode != 0:
        wok_log.error("lsblk -Pbo failed")
        raise OperationFailed("GINDASDPAR0001E", {'err': err})
    return _parse_lsblk_output(out, keys)


def _get_dev_node_path(maj_min):
    """ Returns device node path given the device number 'major:min' """

    dm_name = "/sys/dev/block/%s/dm/name" % maj_min
    if os.path.exists(dm_name):
        with open(dm_name) as dm_f:
            content = dm_f.read().rstrip('\n')
        return "/dev/mapper/" + content

    uevent = "/sys/dev/block/%s/uevent" % maj_min
    with open(uevent) as ueventf:
        content = ueventf.read()
    data = dict(re.findall(r'(\S+)=(".*?"|\S+)', content.replace("\n", " ")))

    return "/dev/%s" % data["DEVNAME"]


def _is_dev_leaf(devNodePath):
    try:
        # By default, lsblk prints a device information followed by children
        # device information
        childrenCount = len(
            _get_lsblk_devs(["NAME"], [devNodePath])) - 1
    except OperationFailed as e:
        # lsblk is known to fail on multipath devices
        # Assume these devices contain children
        wok_log.error(
            "Error getting device info for %s: %s", devNodePath, e)
        return False

    return childrenCount == 0


def _is_dev_extended_partition(devType, devNodePath):
    if devType != 'part':
        return False
    diskPath = devNodePath.rstrip('0123456789')
    device = PDevice(diskPath)
    try:
        extended_part = PDisk(device).getExtendedPartition()
    except NotImplementedError as e:
        wok_log.warning(
            "Error getting extended partition info for dev %s type %s: %s",
            devNodePath, devType, e.message)
        # Treate disk with unsupported partiton table as if it does not
        # contain extended partitions.
        return False
    if extended_part and extended_part.path == devNodePath:
        return True
    return False


def _parse_lsblk_output(output, keys):
    """
    This method parses the output of 'lsblk -Pbo' command.
    :param output: Output of the 'lsblk -Pbo' command
    :return: list containing block devices information
    """
    # output is on format key="value",
    # where key can be NAME, TYPE, FSTYPE, SIZE, MOUNTPOINT, etc
    lines = output.rstrip("\n").split("\n")
    r = []
    for line in lines:
        d = {}
        for key in keys:
            expression = r"%s=\".*?\"" % key
            match = re.search(expression, line)
            field = match.group()
            k, v = field.split('=', 1)
            d[k.lower()] = v[1:-1]
        r.append(d)
    return r


def _get_vgname(devNodePath):
    """ Return volume group name of a physical volume. If the device node path
     is not a physical volume, return empty string. """
    pvs = subprocess.Popen(["pvs", "--unbuffered", "--nameprefixes",
                            "--noheadings", "-o", "vg_name", devNodePath],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = pvs.communicate()
    if pvs.returncode != 0:
        return ""

    return re.findall(r"LVM2_VG_NAME='([^\']*)'", out)[0]


def _is_available(name, devtype, fstype, mountpoint, majmin):
    devNodePath = _get_dev_node_path(majmin)
    # Only list unmounted and unformated and leaf and (partition or disk)
    # leaf means a partition, a disk has no partition, or a disk not held
    # by any multipath device. Physical volume belongs to no volume group
    # is also listed. Extended partitions should not be listed.
    if (devtype in ['part', 'disk', 'mpath'] and
            fstype in ['', 'LVM2_member'] and
            mountpoint == "" and
            _get_vgname(devNodePath) == "" and
            _is_dev_leaf(devNodePath) and
            not _is_dev_extended_partition(devtype, devNodePath)):
        return True
    return False


def _get_partitions_names(check=False):
    """
    This method will give names of all block devices and their partitions
    :return: returns the list of names of all block devices and partitions
    """
    names = set()
    keys = ["NAME", "TYPE", "FSTYPE", "MOUNTPOINT", "MAJ:MIN"]
    # output is on format key="value",
    # where key can be NAME, TYPE, FSTYPE, MOUNTPOINT
    for dev in _get_lsblk_devs(keys):
        # split()[0] to avoid the second part of the name, after the
        # whiteline
        name = dev['name'].split()[0]
        names.add(name)

    return list(names)


def _get_dev_major_min(name):
    maj_min = None

    keys = ["NAME", "MAJ:MIN"]
    dev_list = _get_lsblk_devs(keys)

    for dev in dev_list:
        if dev['name'].split()[0] == name:
            maj_min = dev['maj:min']
            break
    else:
        raise OperationFailed("GINDASDPAR0002E", {'device': name})

    return maj_min


def _get_partition_details(name):
    """
    This method will give details of a partition on a block device
    :param name: name of block device
    :return: returns the details of a partition on a block device
    """
    majmin = _get_dev_major_min(name)
    dev_path = _get_dev_node_path(majmin)
    keys = ["TYPE", "FSTYPE", "SIZE", "MOUNTPOINT"]
    try:
        dev = _get_lsblk_devs(keys, [dev_path])[0]
    except OperationFailed as e:
        wok_log.error(
            "Error getting partition info for %s: %s", name, e)
        return {}
    dev['available'] = _is_available(name, dev['type'], dev['fstype'],
                                     dev['mountpoint'], majmin)

    if dev['mountpoint']:
        # Sometimes the mountpoint comes with [SWAP] or other
        # info which is not an actual mount point. Filtering it
        regexp = re.compile(r"\[.*\]")
        if regexp.search(dev['mountpoint']) is not None:
            dev['mountpoint'] = ''
    dev['path'] = dev_path
    dev['name'] = name
    return dev


def _create_dasd_part(dev, size):
    """
    This method creates a DASD partition
    :param dev: name of DASD device for creation of partition
    :param size: block size
    :return:
    """
    p_str = _form_part_str(size)
    devname = '/dev/' + dev
    p1_out = subprocess.Popen(["echo", "-e", "\'", p_str, "\'"],
                              stdout=subprocess.PIPE)
    p2_out = subprocess.Popen(["fdasd", devname], stdin=p1_out.stdout,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p1_out.stdout.close()
    out, err = p2_out.communicate()
    if p2_out.returncode != 0:
        wok_log.error("Creation of partition on DASD device %s failed",
                      devname)
        raise OperationFailed("GINDASD0003E", {'err': err})
    return


def _form_part_str(size):
    part_str = '\nn\n \n' + '+' + size + 'M' + '\n' + 'w\n'
    return part_str


def _delete_dasd_part(dev, part_id):
    """
    This method deletes a DASD partition
    :param dev: name of DASD device
    :param part_id: ID of partition to be deleted
    :return:
    """
    p_str = _del_part_str(part_id)
    devname = '/dev/' + dev
    p1_out = subprocess.Popen(["echo", "-e", "\'", p_str, "\'"],
                              stdout=subprocess.PIPE)
    p2_out = subprocess.Popen(["fdasd", devname], stdin=p1_out.stdout,
                              stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p1_out.stdout.close()
    out, err = p2_out.communicate()
    if p2_out.returncode != 0:
        wok_log.error("Deletion of partition on DASD device %s failed",
                      devname)
        raise OperationFailed("GINDASD0004E", {'err': err})
    return


def _del_part_str(part_id):
    part_str = '\nd\n' + part_id + '\n' + 'w\n'
    return part_str


def validate_bus_id(bus_id):
    """
    Validate bus ID
    :param bus_id: bus ID
    """
    pattern = re.compile(r'\d\.\d\.\w{4}')
    valid = pattern.match(bus_id)

    if not valid:
        wok_log.error("Unable to validate bus ID, %s", bus_id)
        raise InvalidParameter("GINDASD0011E", {'bus_id': bus_id})

    # No need to worry about IndexError exception below becuase
    # the regex above would have made sure we go through the
    # split operation on the string smoothly
    ch_len = bus_id.split(".")[-1]
    if len(ch_len) > 4:
        wok_log.error("Unable to validate bus ID, %s", bus_id)
        raise InvalidParameter("GINDASD0011E", {'bus_id': bus_id})
