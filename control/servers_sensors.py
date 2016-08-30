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

from wok import template
from wok.control.base import Collection
from wok.control.utils import model_fn, get_class_name


class ServerSensors(Collection):
    def __init__(self, model, server):
        super(ServerSensors, self).__init__(model)
        self.server = server
        self.resource_args = [self.server, ]
        self.model_args = [self.server, ]
        self.role_key = "administration"
        self.admin_methods = ['GET']

    def get(self, filter_params):
        res_list = []
        get_list = getattr(self.model, model_fn(self, 'get_list'))
        res_list = get_list(*self.model_args, **filter_params)
        return template.render(get_class_name(self), res_list)
