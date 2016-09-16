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
from wok.control.utils import model_fn, UrlSubNode


ISCSIIQN_REQUESTS = {
    'DELETE': {'default': "GINISCSI0001L"},
    'POST': {
        'login': "GINISCSI0002L",
        'logout': "GINISCSI0003L",
        'rescan': "GINISCSI0004L",
        'initiator_auth': "GINISCSI0005L",
        'target_auth': "GINISCSI0006L",
    },
}

ISCSIAUTH_REQUESTS = {
    'POST': {
        'initiator_auth': "GINISCSIATH001L",
        'target_auth': "GINISCSIATH002L",
        'discovery_initiator_auth': "GINISCSIATH003L",
        'discovery_target_auth': "GINISCSIATH004L",
    },
}


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
        self.rescan = self.generate_action_handler('rescan')
        # modify auth settings per IQN
        self.initiator_auth = self.generate_action_handler(
            'initiator_auth', ['auth_type', 'username', 'password'])
        self.target_auth = self.generate_action_handler(
            'target_auth', ['auth_type', 'username', 'password'])

    @property
    def data(self):
        return self.info


@UrlSubNode('iscsi_auth', True)
class ISCSIAuth(Resource):
    """
    Resource for the global iSCSI Auth info from /etc/iscsi/iscsid.conf
    """

    def __init__(self, model):
        super(ISCSIAuth, self).__init__(model, None)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/iscsi_auth/%s"
        # modify auth settings globally for all IQNs
        self.initiator_auth = self.generate_action_handler(
            'initiator_auth', ['auth_type', 'username', 'password'])
        self.target_auth = self.generate_action_handler(
            'target_auth', ['auth_type', 'username', 'password'])
        self.discovery_initiator_auth = self.generate_action_handler(
            'discovery_initiator_auth', ['auth_type', 'username', 'password'])
        self.discovery_target_auth = self.generate_action_handler(
            'discovery_target_auth', ['auth_type', 'username', 'password'])

        # set user log messages and make sure all parameters are present
        self.log_map = ISCSIAUTH_REQUESTS

    @property
    def data(self):
        return self.info
