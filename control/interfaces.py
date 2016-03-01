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

from wok.control.base import Collection, Resource


INTERFACES_REQUESTS = {
    'POST': {'default': "Create network interface"},
}

INTERFACE_REQUESTS = {
    'DELETE': {'default': "Remove network interface '%(ident)s'"},
    'PUT': {'default': "Update network interface"},
    'POST': {
        'activate': "Activate network interface '%(ident)s'",
        'deactivate': "Deactivate network interface '%(ident)s'",
    },
}


class Interfaces(Collection):
    def __init__(self, model):
        super(Interfaces, self).__init__(model)
        self.resource = Interface
        self.log_map = INTERFACES_REQUESTS


class Interface(Resource):
    def __init__(self, model, ident):
        super(Interface, self).__init__(model, ident)
        self.uri_fmt = '/network/interfaces/%s'
        self.update_params = ['ipaddr', 'netmask', 'gateway']
        self.confirm_change = self.generate_action_handler('confirm_change')
        self.activate = self.generate_action_handler('activate')
        self.deactivate = self.generate_action_handler('deactivate')
        self.log_map = INTERFACE_REQUESTS

    @property
    def data(self):
        return {'device': self.ident,
                'type': self.info['type'],
                'ipaddr': self.info['ipaddr'],
                'netmask': self.info['netmask'],
                'status': self.info['status'],
                'macaddr': self.info['macaddr']}
