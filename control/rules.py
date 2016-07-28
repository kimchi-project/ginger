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


class Rules(Collection):
    def __init__(self, model):
        super(Rules, self).__init__(model)
        self.resource = Rule


class Rule(Resource):
    def __init__(self, model, ident):
        super(Rule, self).__init__(model, ident)
        self.uri_fmt = '/audit/rules/%s'
        self.persist = self.generate_action_handler('persist')
        self.load = self.generate_action_handler('load')

    @property
    def data(self):
        return self.info
