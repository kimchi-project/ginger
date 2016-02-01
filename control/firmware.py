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

from wok.control.base import AsyncResource, Resource
from wok.control.utils import UrlSubNode


@UrlSubNode('firmware', True)
class Firmware(Resource):
    def __init__(self, model, id=None):
        super(Firmware, self).__init__(model, id)
        self.role_key = "administration"
        self.admin_methods = ['GET', 'POST']
        self.uri_fmt = "/firmware/%s"
        self.commit = self.generate_action_handler('commit')
        self.reject = self.generate_action_handler('reject')
        self.model_args = []
        upgrade_args = ['path', 'overwrite-perm']
        self.upgrade = self.generate_action_handler_task('upgrade',
                                                         upgrade_args)

    @property
    def data(self):
        return self.info


@UrlSubNode('fwprogress', True)
class FirmwareProgress(AsyncResource):
    def __init__(self, model, id=None):
        super(FirmwareProgress, self).__init__(model, id)
        self.role_key = 'administration'
        self.uri_fmt = "/fwprogress/%s"
        self.admin_methods = ['GET']

    @property
    def data(self):
        return self.info
