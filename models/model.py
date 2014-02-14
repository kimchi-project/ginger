#
# Project Kimchi
#
# Copyright IBM, Corp. 2014
#
# Authors:
#  Mark Wu <wudxw@linux.vnet.ibm.com>
#  Rodrigo Trujillo <rodrigo.trujillo@linux.vnet.ibm.com>
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

from interfaces import InterfacesModel, InterfaceModel
from network import NetworkModel
from powermanagement import PowerProfilesModel, PowerProfileModel
from users import UsersModel, UserModel


# RootModel is taken from Zhengsheng's patch for kimchi upstream.
# We could remove it from here when it's merged there.


class RootModel(object):
    '''
    This model squashes all sub-model's public callable methods to itself.

    Model methods are not limited to get_list, create, lookup, update, delete.
    Controller can call generate_action_handler to generate new actions, which
    call the related model methods. So all public callable methods of a
    sub-model should be mapped to this model.
    '''
    def __init__(self, model_instances):
        for model_instance in model_instances:
            cls_name = model_instance.__class__.__name__
            if cls_name.endswith('Model'):
                method_prefix = cls_name[:-len('Model')].lower()
            else:
                method_prefix = cls_name.lower()

            callables = [m for m in dir(model_instance)
                         if not m.startswith('_') and
                         callable(getattr(model_instance, m))]

            for member_name in callables:
                m = getattr(model_instance, member_name, None)
                setattr(self, '%s_%s' % (method_prefix, member_name), m)


class GingerModel(RootModel):

    def __init__(self):
        sub_models = []
        powerprofiles = PowerProfilesModel()
        powerprofile = PowerProfileModel()
        users = UsersModel()
        user = UserModel()
        interfaces = InterfacesModel()
        interface = InterfaceModel()
        network = NetworkModel()
        sub_models = [interfaces, interface,
                      network,
                      powerprofiles, powerprofile,
                      users, user]
        super(GingerModel, self).__init__(sub_models)
