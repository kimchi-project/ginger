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

from wok.control.base import Collection, Resource, SimpleCollection
from wok.control.utils import model_fn, UrlSubNode


@UrlSubNode('iscsitargets', True)
class ISCSITargets(SimpleCollection):

    def __init__(self, model, server):
        super(ISCSITargets, self).__init__(model)
        self.admin_methods = ['GET']
        self.role_key = 'host'
        self.server = server
        self.resource_args = [self.server, ]
        self.model_args = [self.server, ]


@UrlSubNode('iscsi_qns', True)
class DiscoveredISCSIQNs(Collection):

    def __init__(self, model):
        super(DiscoveredISCSIQNs, self).__init__(model)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = DiscoveredISCSIQN

    def _get_resources(self, flag_filter):
        """
        Overriden this method, here get_list should return list dict
        which will be set to the resource, this way we avoid calling lookup
        every single resource.
        :param flag_filter:
        :return: list of resources.
        """
        try:
            get_list = getattr(self.model, model_fn(self, 'get_list'))
            idents = get_list(*self.model_args, **flag_filter)
            res_list = []
            for ident in idents:
                # internal text, get_list changes ident to unicode for sorted
                args = self.resource_args + [ident]
                res = self.resource(self.model, *args)
                res.info = ident
                res_list.append(res)
            return res_list
        except AttributeError:
            return []


class DiscoveredISCSIQN(Resource):

    def __init__(self, model, ident):
        super(DiscoveredISCSIQN, self).__init__(model, ident)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/iscsi_qns/%s"
        self.login = self.generate_action_handler('login')
        self.logout = self.generate_action_handler('logout')

    @property
    def data(self):
        return self.info
