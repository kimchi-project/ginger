#
# Project Ginger
#
# Copyright IBM Corp, 2016-2017
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

from dasd_utils import get_dasd_devs
from utils import get_disks_by_id_out, get_fc_path_elements
from utils import get_lsblk_keypair_out, parse_ll_out, parse_lsblk_out
from wok.exception import OperationFailed


class StorageDevsModel(object):
    """
    Model to represent the list of storage devices
    """

    def get_list(self):

        return get_final_list()


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
        dasds = get_dasd_devs()
        if dasds:
            final_list = dasds

        blk_dict = parse_lsblk_out(out)

        out = get_disks_by_id_out()
        ll_dict, ll_id_dict = parse_ll_out(out)

        fc_blk_dict = get_fc_path_elements()

        for blk in blk_dict:
            final_dict = {}
            if blk in ll_dict:
                final_dict['id'] = ll_dict[blk]
                if final_dict['id'].startswith('ccw-'):
                    continue

                block_dev_list = ll_id_dict[final_dict['id']]
                max_slaves = 1
                for block_dev in block_dev_list:
                    slaves = os.listdir('/sys/block/' + block_dev + '/slaves/')
                    if max_slaves < len(slaves):
                        max_slaves = len(slaves)

                final_dict['mpath_count'] = max_slaves

            final_dict['name'] = blk
            final_dict['size'] = blk_dict[blk]['size']
            final_dict['type'] = blk_dict[blk]['transport']

            if final_dict['type'] == 'fc':
                final_dict['hba_id'] = fc_blk_dict[blk].get('hba_id', '')
                final_dict['wwpn'] = fc_blk_dict[blk].get('wwpn', '')
                final_dict['fcp_lun'] = fc_blk_dict[blk].get('fcp_lun', '')
                final_dict['vport'] = fc_blk_dict[blk].get('vport', '')
                final_dict['status'] = ''

            if 'id' in final_dict:
                if final_dict['id'] in ll_id_dict:
                    final_dict['name'] = ll_id_dict[final_dict['id']][0]
                if 'hba_id' in final_dict.keys():
                    if final_dict['hba_id']:
                        final_list.append(final_dict)
                else:
                    final_list.append(final_dict)
    except Exception as e:
        raise OperationFailed("GINSD00005E", {'err': e.message})

    return final_list
