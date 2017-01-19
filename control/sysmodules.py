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

from wok.control.base import Collection, Resource
from wok.control.utils import UrlSubNode


SYSMODULES_REQUESTS = {
    'POST': {'default': "GINSYSMOD0001L"},
}

SYSMODULE_REQUESTS = {
    'DELETE': {'default': "GINSYSMOD0002L"},
}


@UrlSubNode('sysmodules', True)
class SysModules(Collection):
    def __init__(self, model):
        super(SysModules, self).__init__(model)
        self.admin_methods = ['GET', 'POST']
        self.resource = SysModule

        # set user log messages and make sure all parameters are present
        self.log_map = SYSMODULES_REQUESTS
        self.log_args.update({'name': ''})


class SysModule(Resource):
    def __init__(self, model, ident):
        super(SysModule, self).__init__(model, ident)
        self.admin_methods = ['GET', 'DELETE']
        self.uri_fmt = "/sysmodules/%s"
        self.log_map = SYSMODULE_REQUESTS

    @property
    def data(self):
        return self.info
