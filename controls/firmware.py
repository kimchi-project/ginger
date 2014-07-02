#
# Project Ginger
#
# Copyright IBM, Corp. 2014
#
# Authors:
#   Christy Perez <christy@linux.vnet.ibm.com>
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

from kimchi.control.base import Resource


class Firmware(Resource):
    def __init__(self, model, id=None):
        super(Firmware, self).__init__(model, id)
        self.uri_fmt = "/firmware/%s"
        self.update_params = ['path', 'overwrite-perm-ok']
        self.commit = self.generate_action_handler('commit')
        self.reject = self.generate_action_handler('reject')

    @property
    def data(self):
        return self.info
