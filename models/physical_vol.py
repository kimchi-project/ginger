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

import utils

from diskparts import PartitionModel
from wok.exception import MissingParameter,\
    NotFoundError, OperationFailed
from wok.model.tasks import TaskModel
from wok.utils import add_task, wok_log


class PhysicalVolumesModel(object):
    """
    Model class for listing and creating a PV
    """
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def create(self, params):

        if 'pv_name' not in params:
            raise MissingParameter("GINPV00001E")

        pvname = params['pv_name']

        taskid = add_task(u'/pvs/pv_name/%s' % (pvname),
                          self._create_task, self.objstore, params)

        return self.task.lookup(taskid)

    def _create_task(self, cb, params):

        pvname = params['pv_name']

        cb('entering task to create pv')
        try:

            cb('create pv')
            part = PartitionModel(objstore=self.objstore)
            part_name = pvname.split('/')[2]
            type = '8e'   # hex value for type Linux LVM
            part.change_type(part_name, type)
            utils._create_pv(pvname)

        except OperationFailed:
            wok_log.error("PV create failed")
            raise OperationFailed("GINPV00002E",
                                  {'pvname': pvname})

        cb('OK', True)

    def get_list(self):

        try:
            pv_names = utils._get_pv_devices()
        except OperationFailed as e:
            wok_log.error("Unable to fetch list of PVs")
            raise NotFoundError("GINPV00003E",
                                {'err': e.message})

        return pv_names


class PhysicalVolumeModel(object):
    """
    Model for viewing and deleting a PV
    """
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, name):
        try:
            return utils._pvdisplay_out(name)

        except OperationFailed:
            wok_log.error("Unable to fetch details of PV")
            raise NotFoundError("GINPV00004E", {'name': name})

    def delete(self, name):
        try:
            utils._remove_pv(name)
        except OperationFailed:
            wok_log.error("delete PV failed")
            raise OperationFailed("GINPV00005E", {'name': name})
