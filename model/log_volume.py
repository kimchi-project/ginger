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

from wok.asynctask import AsyncTask
from wok.exception import MissingParameter, \
    NotFoundError, OperationFailed
from wok.model.tasks import TaskModel


class LogicalVolumesModel(object):
    """
    Model class for listing and creating a LV
    """
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def create(self, params):

        if 'vg_name' not in params:
            raise MissingParameter('GINLV00001E')

        vgname = params['vg_name']

        if 'size' not in params:
            raise MissingParameter('GINLV00002E')

        taskid = AsyncTask(u'/lvs/vg_name/%s' % (vgname),
                           self._create_linear_task, params).id
        return self.task.lookup(taskid)

    def _create_linear_task(self, cb, params):

        vgname = params['vg_name']
        size = params['size']

        cb('entering task to create lv')
        try:

            cb('create lv')
            utils._create_lv(vgname, size)

        except (OperationFailed), e:
            raise OperationFailed('GINLV00003E',
                                  {'err': e.message})

        cb('OK', True)

    def get_list(self):
        try:
            lv_names = utils._get_lv_list()
        except OperationFailed as e:
            raise OperationFailed("GINLV00004E",
                                  {'err': e.message})

        return lv_names


class LogicalVolumeModel(object):
    """
    Model class for viewing and deleting a LV
    """
    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, name):
        try:
            out_dict = utils._lvdisplay_out(name)
            return out_dict

        except OperationFailed:
            raise NotFoundError("GINLV00005E", {'name': name})

    def delete(self, name):
        try:
            utils._remove_lv(name)
        except OperationFailed as e:
            raise OperationFailed("GINLV00006E",
                                  {'err': e.message})
