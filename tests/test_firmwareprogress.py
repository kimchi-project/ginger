#
# Project Ginger
#
# Copyright IBM Corp, 2015-2016
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

import unittest

from wok import config
from wok.model.tasks import TaskModel
from wok.objectstore import ObjectStore
from wok.plugins.ginger.model.firmware import FirmwareProgressModel


class FirmwareProgressTests(unittest.TestCase):
    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        self.task = TaskModel(objstore=self._objstore)

    def test_fwprogress_without_update_flash(self):
        fwprogress = FirmwareProgressModel(objstore=self._objstore)
        task_info = fwprogress.lookup()
        self.task.wait(task_info['id'])
        task_info = self.task.lookup(task_info['id'])

        self.assertEquals('finished', task_info['status'])
        self.assertIn('Error', task_info['message'])
        self.assertEquals('/plugins/ginger/fwprogress',
                          task_info['target_uri'])
