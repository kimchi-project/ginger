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

import utils

from wok.exception import MissingParameter, NotFoundError, OperationFailed
from wok.model.tasks import TaskModel
from wok.plugins.gingerbase.disks import get_partitions_names,\
    get_partition_details
from wok.utils import wok_log, add_task


class PartitionsModel(object):

    def get_list(self):

        try:
            result = get_partitions_names()
        except OperationFailed as e:
            wok_log.error("Fetching list of partitions failed")
            raise OperationFailed("GINPART00001E",
                                  {'err': e})
        result = set(result)  # removes duplicates in case of multipath
        return result

    def create(self, params):

        if 'devname' not in params:
            raise MissingParameter("GINPART00008E")

        dev_name = params['devname']

        if 'partsize' not in params:
            raise MissingParameter("GINPART00009E")

        part_size = params['partsize']
        try:
            return utils.create_disk_part(dev_name, part_size)
        except OperationFailed as e:
            wok_log.error("Create partition failed")
            raise OperationFailed("GINPART00002E",
                                  {'err': e})


class PartitionModel(object):
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, name, dev=None):

        try:
            return get_partition_details(name)

        except NotFoundError:
            wok_log.error("partition %s not found" % name)
            raise NotFoundError("GINPART00014E", {'name': name})

        except OperationFailed as e:
            wok_log.error("lookup method of partition failed")
            raise OperationFailed("GINPART00003E", {'name': name, 'err': e})

    def format(self, name, fstype):

        if utils._is_mntd(name):
            raise OperationFailed('GINPART00004E')

        task_params = {'name': name, 'fstype': fstype}
        taskid = add_task(u'/partitions/%s/fstype%s' % (name, fstype),
                          self._format_task, self.objstore, task_params)

        return self.task.lookup(taskid)

    def _format_task(self, cb, params):
        name = params['name']
        fstype = params['fstype']
        try:
            utils._makefs(fstype, name)
        except (OperationFailed):
            raise OperationFailed('GINPART00005E')
        cb('OK', True)

    def change_type(self, name, type):
        try:
            utils.change_part_type(name, type)
        except OperationFailed as e:
            wok_log.error("change type for partition failed")
            raise OperationFailed("GINPART00006E",
                                  {'err': e})
        return name

    def delete(self, name):
        try:
            utils.delete_part(name)
        except OperationFailed as e:
            wok_log.error("delete partition failed")
            raise OperationFailed("GINPART00007E",
                                  {'err': e})
