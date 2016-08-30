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
from wok.control.utils import UrlSubNode

from sel import Sels
from servers_sensors import ServerSensors

SERVERS_REQUESTS = {
    'POST': {'default': "GINSE0001L"}
}

SERVER_REQUESTS = {
    'DELETE': {'default': "GINSE0002L"},
    'POST': {
        'poweron': "GINSE0003L",
        'poweroff': "GINSE0004L,"
    },
}


@UrlSubNode('servers', True)
class Servers(Collection):
    def __init__(self, model):
        super(Servers, self).__init__(model)
        self.role_key = "administration"
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = Server
        self.log_map = SERVERS_REQUESTS
        self.log_args.update({'name': ''})


class Server(Resource):
    def __init__(self, model, ident):
        super(Server, self).__init__(model, ident)
        self.uri_fmt = '/servers/%s'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.poweron = self.generate_action_handler('poweron')
        self.poweroff = self.generate_action_handler('poweroff')
        self.sels = Sels(self.model, ident)
        self.sensors = ServerSensors(self.model, ident)
        self.log_map = SERVER_REQUESTS

    @property
    def data(self):
        return {
            'name': self.info['name'],
            'ipaddr': self.info['ipaddr'],
            'status': self.info['status'],
        }
