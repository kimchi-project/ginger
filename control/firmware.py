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

from wok.control.base import Resource
from wok.control.utils import UrlSubNode


FIRMWARE_REQUESTS = {
    'POST': {
        'upgrade': "GINFW0001L",
        'commit': "GINFW0002L",
        'reject': "GINFW0003L",
    },
}


@UrlSubNode('firmware', True)
class Firmware(Resource):
    def __init__(self, model, id=None):
        super(Firmware, self).__init__(model, id)
        self.admin_methods = ['GET', 'POST']
        self.uri_fmt = "/firmware/%s"
        self.commit = self.generate_action_handler('commit')
        self.reject = self.generate_action_handler('reject')
        upgrade_args = ['path', 'overwrite-perm']
        self.upgrade = self.generate_action_handler_task('upgrade',
                                                         upgrade_args)

        # set user log messages and make sure all parameters are present
        self.log_map = FIRMWARE_REQUESTS
        self.log_args.update({'path': ''})

    @property
    def data(self):
        return self.info
