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

from wok.exception import NotFoundError
import utils


class ISCSITargetsModel(object):
    """
    Model to represent the list of iSCSI targets
    """

    def get_list(self, model_args):
        iscsi_targets = utils.iscsi_discovery(model_args)
        if not iscsi_targets:
            raise NotFoundError("GINISCSI001E", {"ip_address": model_args})

        return iscsi_targets


class DiscoveredISCSIQNsModel(object):

    def get_list(self):
        return utils.get_discovered_iscsi_qns()


class DiscoveredISCSIQNModel(object):

    def lookup(self, name):
        return utils.get_iqn_info(name)

    def login(self, name):
        utils.iscsi_target_login(name)

    def logout(self, name):
        utils.iscsi_target_logout(name)

    def delete(self, name):
        utils.iscsi_delete_iqn(name)
