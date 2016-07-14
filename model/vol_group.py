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

from wok.exception import InvalidOperation, MissingParameter, NotFoundError
from wok.exception import OperationFailed

from wok.model.tasks import TaskModel
from wok.utils import add_task


class VolumeGroupsModel(object):
    """
    Model class for listing and creating a VG
    """
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def create(self, params):

        if 'vg_name' not in params:
            raise MissingParameter("GINVG00013E")

        vgname = params['vg_name']

        if "pv_paths" not in params:
            raise MissingParameter("GINVG00014E")

        taskid = add_task(u'/vgs/vg_name/%s' % (vgname),
                          self._create_task, self.objstore, params)

        return self.task.lookup(taskid)

    def _create_task(self, cb, params):

        vgname = params['vg_name']

        pv_paths = params['pv_paths']

        cb('entering task to create vg')
        try:

            cb('create vg')
            utils._create_vg(vgname, pv_paths)

        except (OperationFailed), e:
            raise OperationFailed('GINVG00001E',
                                  {'name': vgname,
                                   'err': e.message})

        cb('OK', True)

    def get_list(self):

        try:
            vg_names = utils._get_vg_list()
        except OperationFailed as e:
            raise NotFoundError("GINVG00002E",
                                {'err': e.message})

        return vg_names


class VolumeGroupModel(object):
    """
    Model class for viewing, extending, reducing and deleting a VG
    """
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, name):
        try:
            return utils._vgdisplay_out(name)

        except OperationFailed:
            raise NotFoundError("GINVG00003E", {'name': name})

    def delete(self, name):
        try:

            vg_details = self.lookup(name)
            if vg_details['Cur LV'] > 0:
                raise InvalidOperation('GINVG00017E', {'name': name})

            utils._remove_vg(name)
        except OperationFailed:
            raise OperationFailed("GINVG00004E", {'name': name})

    def extend(self, name, paths):
        try:
            utils._extend_vg(name, paths)
        except OperationFailed:
            raise OperationFailed("GINVG00005E", {'name': name})

    def reduce(self, name, paths):
        try:
            utils._reduce_vg(name, paths)
        except OperationFailed:
            raise OperationFailed("GINVG00006E", {'name': name})
