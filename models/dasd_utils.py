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

import os
import platform
import re
import subprocess

from wok.exception import InvalidParameter, OperationFailed
from wok.utils import run_command, wok_log

from wok.plugins.ginger.models.utils import get_storagedevice, get_directories
from wok.plugins.ginger.models.utils import syspath_eckd, get_dirname


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


def get_dasd_devs():
    """
    Get the list of unformatted DASD devices
    """
    devs = []
    if platform.machine() == "s390x":
        dasd_devices = _get_lsdasd_devs()
        for device in dasd_devices:
            uf_dev = {}
            uf_dev['type'] = 'dasd'
            uf_dev['name'] = device['name']
            uf_dev['mpath_count'] = 'N/A'
            uf_dev['size'] = device['size']
            uf_dev['id'] = device['uid']
            uf_dev['bus_id'] = device['bus-id']
            uf_dev['mpath_count'] = len(
                get_storagedevice(
                    uf_dev['bus_id'])['enabled_chipids'])
            devs.append(uf_dev)
    return devs


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


def _is_dasdeckd_device(device):
    """
    Return True if the device is of type dasd-eckd otherwise False
    :param device: device id
    """
    dasdeckd_devices = _get_dasdeckd_devices()
    if device in dasdeckd_devices:
        return True
    return False


def _get_dasdeckd_devices():
    """
    Return list of dasd-eckd devices
    """
    device_paths = get_directories(syspath_eckd)
    dasdeckd_devices = []
    for path in device_paths:
        device = get_dirname(path)
        if device:
            dasdeckd_devices.append(device)
    return dasdeckd_devices
