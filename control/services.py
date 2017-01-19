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


SERVICE_REQUESTS = {
    'POST': {
        'enable': "GINSERV0001L",
        'disable': "GINSERV0002L",
        'start': "GINSERV0003L",
        'stop': "GINSERV0004L",
        'restart': "GINSERV0005L",
    },
}


@UrlSubNode('services', True)
class Services(Collection):
    def __init__(self, model):
        super(Services, self).__init__(model)
        self.admin_methods = ['GET']
        self.resource = Service


class Service(Resource):
    def __init__(self, model, ident):
        super(Service, self).__init__(model, ident)
        self.ident = ident
        self.admin_methods = ['GET']
        self.uri_fmt = "/services/%s"
        self.log_map = SERVICE_REQUESTS

        self.enable = self.generate_action_handler('enable')
        self.disable = self.generate_action_handler('disable')
        self.start = self.generate_action_handler('start')
        self.stop = self.generate_action_handler('stop')
        self.restart = self.generate_action_handler('restart')

    @property
    def data(self):
        return self.info
