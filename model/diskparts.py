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

import re
import utils

from wok.asynctask import AsyncTask
from wok.exception import MissingParameter, NotFoundError, OperationFailed
from wok.model.tasks import TaskModel
from wok.plugins.gingerbase.disks import fetch_disks_partitions
from wok.plugins.gingerbase.disks import _get_vgname, get_partition_details
from wok.plugins.gingerbase.disks import pvs_with_vg_list


class PartitionsModel(object):

    def get_list(self, _name=None):

        try:
            result = fetch_disks_partitions()
        except OperationFailed as e:
            raise OperationFailed("GINPART00001E",
                                  {'err': e.message})
        result_names = []
        pv_vglist = pvs_with_vg_list()
        for i in result:
            part_path = i['path']
            pv_dict = \
                next((val for itr, val in enumerate(pv_vglist)
                      if part_path in val), None)
            if pv_dict:
                i['vgname'] = pv_dict[part_path]
            else:
                i['vgname'] = 'N/A'
            result_names.append(i['name'])
        if _name:
            name = list(set([_name]).intersection(set(result_names)))
            return filter(lambda x: re.match(name[0]+'[0-9]', x['name']),
                          result)
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
            raise OperationFailed("GINPART00002E",
                                  {'err': e.message})


class PartitionModel(object):
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, name, dev=None):

        try:
            part_details = get_partition_details(name)
            part_path = part_details['path']
            vg_name = _get_vgname(part_path)
            if vg_name:
                part_details['vgname'] = vg_name
            else:
                part_details['vgname'] = "N/A"
            return part_details

        except NotFoundError:
            raise NotFoundError("GINPART00014E", {'name': name})

        except OperationFailed as e:
            raise OperationFailed("GINPART00003E",
                                  {'name': name, 'err': e.message})

    def format(self, name, fstype):

        if utils._is_mntd(name):
            raise OperationFailed('GINPART00004E')

        task_params = {'name': name, 'fstype': fstype}
        taskid = AsyncTask(u'/partitions/%s/fstype%s' % (name, fstype),
                           self._format_task, task_params).id

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
            raise OperationFailed("GINPART00006E",
                                  {'err': e.message})
        return name

    def delete(self, name):
        try:
            utils.delete_part(name)
        except OperationFailed as e:
            raise OperationFailed("GINPART00007E",
                                  {'err': e.message})
