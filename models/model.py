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
from kimchi.basemodel import BaseModel
from network import NetworkModel
from powermanagement import PowerProfilesModel, PowerProfileModel
from users import UsersModel, UserModel


class GingerModel(BaseModel):

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
