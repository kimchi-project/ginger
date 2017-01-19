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
from wok.control.utils import model_fn, UrlSubNode


USERS_REQUESTS = {
    'POST': {'default': "GINUSER0001L"},
}

USER_REQUESTS = {
    'DELETE': {'default': "GINUSER0002L"},
    'POST': {
        'chpasswd': "GINUSER0003L"
    }
}


@UrlSubNode('users', True)
class Users(Collection):
    def __init__(self, model):
        super(Users, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = User

        # set user log messages and make sure all parameters are present
        self.log_map = USERS_REQUESTS
        self.log_args.update({'name': ''})

    def _get_resources(self, flag_filter):
        """
        Overriding this method to avoid lookup call for each user,
        here get_list should return list of dict
        which will be set to the resource, this way we avoid calling lookup
        and hence avoiding augeas parsing for each user.
        :param flag_filter:
        :return: list of resources.
        """
        try:
            get_list = getattr(self.model, model_fn(self, 'get_list'))
            idents = get_list(*self.model_args, **flag_filter)
            res_list = []
            for ident in idents:
                args = self.resource_args + [ident]
                res = self.resource(self.model, *args)
                res.info = ident
                res_list.append(res)
            return res_list
        except AttributeError:
            return []


class User(Resource):
    def __init__(self, model, ident):
        super(User, self).__init__(model, ident)
        self.log_map = USER_REQUESTS
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/users/%s"
        self.chpasswd = self.generate_action_handler('chpasswd', ['password'])

    @property
    def data(self):
        return self.info
