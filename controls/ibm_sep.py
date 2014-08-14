#
# Project Ginger
#
# Copyright IBM, Corp. 2014
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


class Sep(Resource):
    def __init__(self, model, id=None):
        super(Sep, self).__init__(model, id)
        self.update_params = ['hostname', 'port', 'community']
        self.role_key = "administration"
        self.admin_methods = ['GET', 'POST', 'PUT']
        self.uri_fmt = '/ibm_sep/%s'
        self.start = self.generate_action_handler('start')
        self.stop = self.generate_action_handler('stop')

    @property
    def data(self):
        return self.info
