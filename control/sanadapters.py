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


@UrlSubNode('san_adapters', True)
class SanAdapters(Collection):
    def __init__(self, model):
        super(SanAdapters, self).__init__(model)
        self.admin_methods = ['GET']
        self.resource = SanAdapter


class SanAdapter(Resource):
    def __init__(self, model, ident):
        super(SanAdapter, self).__init__(model, ident)
        self.uri_fmt = '/san_adapters/%s'

    @property
    def data(self):
        self.info.update({'name': self.ident})
        return self.info
