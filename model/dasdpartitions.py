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

import dasd_utils
import platform
import re

from wok.exception import InvalidParameter, MissingParameter
from wok.exception import NotFoundError, OperationFailed
from wok.plugins.gingerbase.disks import get_partitions_names
from wok.plugins.gingerbase.disks import get_partition_details
from wok.utils import wok_log


class DASDPartitionsModel(object):
    """
    Model class for listing DASD Partitions, creating and
    deleting a DASD Partition
    """
    def is_feature_available(self):
        ptfm = platform.machine()
        if ptfm != 's390x':
            return False
        else:
            return True

    def create(self, params):
        if not params.get('dev_name'):
            raise MissingParameter("GINDASDPAR0005E")
        dev_name = params['dev_name']

        if 'size' not in params:
            raise MissingParameter("GINDASDPAR0006E")

        if params['size']:
            if type(params['size']) != int:
                raise InvalidParameter("GINDASDPAR0013E")
        size = params['size']

        try:
            dasd_utils._create_dasd_part(dev_name, size)
        except OperationFailed as e:
            wok_log.error("Creation of partition failed")
            raise OperationFailed("GINDASDPAR0007E",
                                  {'dev_name': dev_name, 'err': e})
        return dev_name

    def get_list(self):
        dasd_part_list = []
        try:
            partitions_list = get_partitions_names()
            for part in partitions_list:
                if re.search("dasd.*", part):
                    dasd_part_list.append(part)
        except OperationFailed as e:
            wok_log.error("Fetching list of dasd partitions failed")
            raise OperationFailed("GINDASDPAR0008E",
                                  {'err': e})

        return dasd_part_list


class DASDPartitionModel(object):
    """
    Model for viewing and deleting a DASD partition
    """

    def lookup(self, name):
        try:
            return get_partition_details(name)
        except ValueError:
            wok_log.error("DASD Partition %s not found" % name)
            raise NotFoundError("GINDASDPAR0009E", {'name': 'name'})

    def delete(self, name):
        try:
            name_split = re.split('(\D+)', name, flags=re.IGNORECASE)
            dev_name = name_split[1]
            part_num = name_split[2]
            if dev_name != '' and part_num != '':
                dasd_utils._delete_dasd_part(dev_name, part_num)
            else:
                raise InvalidParameter("GINDASDPAR0011E", {'name': name})
        except InvalidParameter:
            wok_log.error("Invalid DASD partition: %s" % name)
            raise InvalidParameter("GINDASDPAR0011E", {'name': name})
        except OperationFailed as e:
            wok_log.error("Deletion of partition %s failed" % name)
            raise OperationFailed("GINDASDPAR0010E", {'err': e})
