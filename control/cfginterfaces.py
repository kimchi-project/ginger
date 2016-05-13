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


CFGINTERFACES_REQUESTS = {
    'POST': {'default': "GINNET0001L"},
}

CFGINTERFACE_REQUESTS = {
    'DELETE': {
        'default': "GINNET0002L",
    },
    'PUT': {
        'default': "GINNET0003L",
    },
}


class Cfginterfaces(Collection):
    def __init__(self, model):
        super(Cfginterfaces, self).__init__(model)
        self.resource = Cfginterface
        self.log_map = CFGINTERFACES_REQUESTS


class Cfginterface(Resource):
    def __init__(self, model, ident):
        super(Cfginterface, self).__init__(model, ident)
        self.uri_fmt = '/network/cfginterfaces/%s'
        self.log_map = CFGINTERFACE_REQUESTS

    @property
    def data(self):
        return self.info
