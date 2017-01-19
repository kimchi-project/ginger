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
from wok.control.utils import model_fn


class Frus(Collection):
    def __init__(self, model, server):
        super(Frus, self).__init__(model)
        print "Frus __init"
        self.server = server
        self.resource_args = [self.server, ]
        self.model_args = [self.server, ]
        self.admin_methods = ['GET']
        self.resource = Fru

    def _get_resources(self, flag_filter):
        """
        Overriden this method, here get_list should return list dict
        which will be set to the resource, this way we avoid calling lookup
        again for each device.
        :param flag_filter:
        :return: list of resources.
        """
        try:
            get_list = getattr(self.model, model_fn(self, 'get_list'))
            idents = get_list(*self.model_args, **flag_filter)
            res_list = []
            for ident in idents:
                # internal text, get_list changes ident to unicode for sorted
                print self.resource_args
                args = self.resource_args + [ident]
                print args
                res = self.resource(self.model, *args)
                res.info = ident
                res_list.append(res)
            return res_list
        except AttributeError:
            return []


class Fru(Resource):
    def __init__(self, model, server, ident):
        super(Fru, self).__init__(model, ident)
        self.server = server
        self.uri_fmt = '/servers/%s/frus/%s'
        self.model_args = [self.server, self.ident]
        self.admin_methods = ['GET']

    @property
    def data(self):
        return self.info
