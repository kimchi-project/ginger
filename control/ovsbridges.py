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

from wok.control.base import Resource, Collection
from wok.control.utils import UrlSubNode


OVSBRIDGES_REQUESTS = {'POST': {'default': "GINOVS0001L"}}

OVSBRIDGE_REQUESTS = {
    'DELETE': {'default': "GINOVS0002L"},
    'POST': {
        'add_interface': "GINOVS0003L",
        'del_interface': "GINOVS0004L",
        'add_bond': "GINOVS0005L",
        'del_bond': "GINOVS0006L",
        'modify_bond': "GINOVS0007L",
    },
}


@UrlSubNode('ovsbridges', True)
class OVSBridges(Collection):
    def __init__(self, model):
        super(OVSBridges, self).__init__(model)
        self.admin_methods = ['GET', 'POST']
        self.resource = OVSBridge

        # set user log messages and make sure all parameters are present
        self.log_map = OVSBRIDGES_REQUESTS
        self.log_args.update({'name': ''})


class OVSBridge(Resource):
    def __init__(self, model, ident):
        super(OVSBridge, self).__init__(model, ident)
        self.ident = ident
        self.admin_methods = ['GET', 'DELETE']
        self.uri_fmt = "/ovsbridges/%s"

        # set user log messages and make sure all parameters are present
        self.log_map = OVSBRIDGE_REQUESTS
        self.log_args.update({
            'interface': '',
            'interface_add': '',
            'interface_del': '',
            'bond': '',
        })

        interface_args = ['interface']
        self.add_interface = \
            self.generate_action_handler('add_interface', interface_args)
        self.del_interface = \
            self.generate_action_handler('del_interface', interface_args)

        self.add_bond = self.generate_action_handler(
            'add_bond', ['bond', 'interfaces']
        )
        self.del_bond = self.generate_action_handler('del_bond', ['bond'])

        mod_bond_args = ['bond', 'interface_del', 'interface_add']
        self.modify_bond = \
            self.generate_action_handler('modify_bond', mod_bond_args)

    @property
    def data(self):
        return self.info
