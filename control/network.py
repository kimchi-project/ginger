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

from cfginterfaces import Cfginterfaces
from interfaces import Interfaces


NETWORK_REQUESTS = {
    'PUT': {'default': "GINNET0008L"},
    'POST': {
        'confirm_change': "GINNET0009L",
    },
}


@UrlSubNode('network', True)
class Network(Resource):

    def __init__(self, model):
        super(Network, self).__init__(model, None)
        self.admin_methods = ['PUT', 'POST']
        self.interfaces = Interfaces(model)
        self.cfginterfaces = Cfginterfaces(model)
        self.uri_fmt = '/network/%s'
        self.update_params = ['nameservers', 'gateway']
        self.confirm_change = self.generate_action_handler('confirm_change')
        self.log_map = NETWORK_REQUESTS

    @property
    def data(self):
        return self.info
