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

import os

from wok.exception import OperationFailed
from wok.utils import run_command, wok_log


def _parse_df_output(output):
    """
    This method parses the output of 'df -hT' command.
    :param output: Parsed output of the 'df -hT' command
    :return:list containing filesystems information
    """

    try:
        output = output.splitlines()
        out_list = []
        for fs in output[1:]:
            fs_dict = {}
            fs_list = fs.split()
            fs_dict['filesystem'] = fs_list[0]
            fs_dict['type'] = fs_list[1]
            fs_dict['size'] = int(fs_list[2])
            fs_dict['used'] = fs_list[3]
            fs_dict['avail'] = int(fs_list[4])
            fs_dict['use%'] = fs_list[5]
            fs_dict['mounted_on'] = fs_list[6]

            out_list.append(fs_dict)
    except:
        wok_log.error("Parsing df output failed")
        raise OperationFailed("GINFS00003E")

    return out_list


def _get_fs_names():
    """
    Fetches list of filesystems
    :return: list of filesystem names
    """
    fs_name_list = []
    try:
        outlist = _get_df_output()
        fs_name_list = [d['mounted_on'] for d in outlist]
        return fs_name_list
    except:
        wok_log.error("Fetching list of filesystems failed")
        raise OperationFailed("GINFS00004E")


def _get_fs_info(mnt_pt):
    """
    Fetches information about the given filesystem
    :param mnt_pt: mount point of the filesystem
    :return: dictionary containing filesystem info
    """
    fs_info = {}
    try:
        mnt_pt = mnt_pt.strip() if mnt_pt.strip() == '/' \
            else mnt_pt.strip().rstrip('/')
        # 'df -kT' command doesn't have extra '/' at end for mount
        # point, so remove '/' at end for given mount point
        fs_search_list = _get_df_output()
        for i in fs_search_list:
            if mnt_pt == i['mounted_on']:
                fs_info['filesystem'] = i['filesystem']
                fs_info['type'] = i['type']
                fs_info['size'] = i['size']
                fs_info['used'] = i['used']
                fs_info['avail'] = i['avail']
                fs_info['use%'] = i['use%']
                fs_info['mounted_on'] = i['mounted_on']
    except:
        wok_log.error("Fetching fs %s info failed", mnt_pt)
        raise OperationFailed("GINFS00005E", {'device': mnt_pt})
    return fs_info


def _get_df_output():
    """
    Executes 'df -kT' command and returns
    :return: output of 'df -kT' command
    """
    command = ['df', '-kT']
    dfout, err, rc = run_command(command)
    if rc:
        wok_log.error("df -kT failed")
        raise OperationFailed("GINFS00006E", {'err': err})
    return _parse_df_output(dfout)


def _mount_a_blk_device(blk_dev, mount_point, mnt_opts):
    """
    Mounts the given block device on the given mount point
    :param blk_dev: path of the block device
    :param mount_point: mount point
    :param mnt_opts: mount options
    :return:
    """
    if mnt_opts:
        mnt_cmd = ['/bin/mount', blk_dev, mount_point, "-o", mnt_opts]
    else:
        mnt_cmd = ['/bin/mount', blk_dev, mount_point]
    mount_out, err, rc = run_command(mnt_cmd)
    if rc:
        wok_log.error("Mounting block device failed. Error: %s" % err)
        raise OperationFailed("GINFS00007E", {'err': err})
    return


def _umount_partition(mnt_pt):
    """
    Unmounts the given mount point (filesystem)
    :param mnt_pt: mount point
    :return:
    """
    umnt_cmd = ['/bin/umount', mnt_pt]
    mount_out, err, rc = run_command(umnt_cmd)
    if rc:
        wok_log.error("Unmounting block device failed")
        raise OperationFailed("GINFS00008E", {'err': err})
    return


def _fstab_dev_exists(dev):
    """
    This method checks if the device already exists in fstab
    :param dev: device to be checked
    :return:
    """

    dev_exist = False
    fo = open("/etc/fstab", "r")
    lines = fo.readlines()
    for i in lines:
        if not i.startswith("/"):
            continue

        columns = i.split()

        device = columns[0]
        if dev == device:
            dev_exist = True
            break

    return dev_exist


def persist_swap_dev(dev):
    """
    This method persists the swap device by making an entry in fstab
    :param dev: path of the device
    :return:
    """
    if _fstab_dev_exists(dev):
        wok_log.error("entry in fstab already exists")
        raise OperationFailed("GINSP00020E")
    else:
        try:
            fo = open("/etc/fstab", "a+")
            fo.write(dev + "    none    swap    sw      0   0\n")
            fo.close()
        except:
            wok_log.error("Unable to open fstab")
            raise OperationFailed("GINFS00012E")


def unpersist_swap_dev(dev):
    """
    This method removes the fstab entry for swap device
    :param dev: device
    :return:
    """
    try:
        fo = open("/etc/fstab", "r")
        lines = fo.readlines()
        output = []
        fo.close()
    except:
        raise OperationFailed("GINFS00011E")

    try:
        fo = open("/etc/fstab", "w")
        for line in lines:
            if dev in line:
                continue
            else:
                output.append(line)
        fo.writelines(output)
        fo.close()
    except:
        raise OperationFailed("GINFS00012E")


def _mnt_exists(mount):
    """
    This method checks if the mount point already exists in fstab
    :param mount: mount point to be checked
    :return:
    """

    is_mnt_exist = False
    fo = open("/etc/fstab", "r")
    lines = fo.readlines()
    for i in lines:
        if not i.startswith("/"):
            continue

        columns = i.split()

        mount_pt = columns[1]
        if mount == mount_pt:
            is_mnt_exist = True
            break

    return is_mnt_exist


def make_persist(dev, mntpt, mnt_opts):
    """
    This method persists the mounted filesystem by making an entry in fstab
    :param dev: path of the device to be mounted
    :param mntpt: mount point
    :param mnt_opts: mount options
    :return:
    """
    try:
        if _mnt_exists(mntpt):
            raise OperationFailed("GINFS00019E", {'name': mntpt})
        else:
            fs_info = _get_fs_info(mntpt)
            if not fs_info.get('type') and not fs_info.get('mounted_on'):
                raise Exception('Failed to fetch filesystem details')
            fo = open("/etc/fstab", "a+")
            if mnt_opts:
                fo.write(dev + " " + fs_info['mounted_on'] + " " +
                         fs_info['type'] + " " + mnt_opts + " " + "0 0\n")
            else:
                fo.write(dev + " " + fs_info['mounted_on'] + " " +
                         fs_info['type'] + " " + "defaults 1 2\n")
            fo.close()
    except OperationFailed:
        raise
    except Exception as e:
        raise OperationFailed("GINFS00011E", {'err': e.__str__()})


def remove_persist(mntpt):
    """
    This method removes the fstab entry
    :param mntpt: mount point
    :return:
    """
    try:
        fo = open("/etc/fstab", "r")
        lines = fo.readlines()
        output = []
        fo.close()
    except:
        raise OperationFailed("GINFS00011E")

    try:
        fo = open("/etc/fstab", "w")
        for line in lines:
            if mntpt in line:
                continue
            else:
                output.append(line)
        fo.writelines(output)
        fo.close()
    except:
        raise OperationFailed("GINFS00012E")


def nfsmount(server, share, mount_point, mnt_opts):
    """
    This method mounts the remote nfs share on local system
    :param server: ip address of the nfs server
    :param share: remote share location
    :param mount_point: mount point on local system
    :return:
    """
    if not os.path.exists(mount_point):
        d_cmd = ['mkdir', mount_point]
        d_out, err, rc = run_command(d_cmd)
        if rc:
            wok_log.error("mkdir failed")
    if mnt_opts:
        nfs_cmd = ['mount', server + ':' + share, mount_point, "-o", mnt_opts]
    else:
        nfs_cmd = ['mount', server + ':' + share, mount_point]
    nfs_out, err, rc = run_command(nfs_cmd)
    if rc:
        raise OperationFailed("GINFS00018E", {'err': err})
