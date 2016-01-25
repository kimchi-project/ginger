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

import dasd_utils
import platform
import threading

from wok.exception import MissingParameter, NotFoundError, OperationFailed
from wok.model.tasks import TaskModel
from wok.utils import add_task, run_command, wok_log


class DASDdevsModel(object):
    """
    Model class for listing DASD devices (lsdasd -l)
    """
    def is_feature_available(self):
        _, _, returncode = run_command(['lsdasd', '-l'])
        ptfm = platform.machine()
        if ptfm != 's390x' or returncode != 0:
            return False
        else:
            return True

    def get_list(self):
        try:
            dasd_devs = dasd_utils._get_lsdasd_devs()
        except OperationFailed as e:
            wok_log.error("Fetching list of dasd devices failed")
            raise OperationFailed("GINDASD0005E",
                                  {'err': e})

        return dasd_devs


class DASDdevModel(object):
    """
    Model for viewing and formatting a DASD device
    """

    def __init__(self, **kargs):
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)
        self.dev_details = {}

    def lookup(self, bus_id):
        dasd_utils.validate_bus_id(bus_id)
        try:
            dasddevices = dasd_utils._get_dasd_dev_details(bus_id)
            self.dev_details = dasddevices[0]
        except IndexError as e:
            wok_log.error("DASD device %s not found." % bus_id)
            raise NotFoundError("GINDASD0006E", {'err': e})

        return self.dev_details

    def format(self, bus_id, blk_size):
        dasd_utils.validate_bus_id(bus_id)
        woklock = threading.Lock()
        name = self.dev_details['name']
        dasd_name_list = dasd_utils._get_dasd_names()
        if name not in dasd_name_list:
            raise NotFoundError('GINDASD0007E')
        task_params = {'blk_size': blk_size, 'name': name}
        try:
            woklock.acquire()
            taskid = add_task(u'/dasddevs/%s/blksize/%s' % (name, blk_size),
                              self._format_task, self.objstore, task_params)
        except OperationFailed:
            woklock.release()
            wok_log.error("Formatting of DASD device %s failed" % bus_id)
            raise OperationFailed("GINDASD0008E", {'name': name})
        finally:
            woklock.release()

        return self.task.lookup(taskid)

    def _format_task(self, cb, params):
        if 'name' not in params:
            raise MissingParameter("GINDASD0009E")
        name = params['name']

        if 'blk_size' not in params:
            raise MissingParameter("GINDASD0010E")
        blk_size = params['blk_size']

        try:
            dasd_utils._format_dasd(blk_size, name)
        except OperationFailed:
            wok_log.error("Formatting of DASD device %s failed" % name)
            raise OperationFailed('GINDASD0008E', {'name': name})

        cb('OK', True)
