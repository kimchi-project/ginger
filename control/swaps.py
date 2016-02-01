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

from wok.control.base import AsyncCollection, Resource
from wok.control.utils import UrlSubNode


@UrlSubNode('swaps', True)
class Swaps(AsyncCollection):
    def __init__(self, model):
        super(Swaps, self).__init__(model)
        self.role_key = 'storage'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = Swap


class Swap(Resource):
    def __init__(self, model, ident):
        super(Swap, self).__init__(model, ident)
        self.role_key = 'storage'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/swaps/%s"

    @property
    def data(self):
        return {'filename': self.info['filename'],
                'type': self.info['type'],
                'size': self.info['size'],
                'used': self.info['used'],
                'priority': self.info['priority']}
