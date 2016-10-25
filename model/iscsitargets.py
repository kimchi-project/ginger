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

from wok.exception import InvalidParameter, NotFoundError
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
        discovered_qns = utils.get_discovered_iscsi_qns()
        iqn_exists = any(qn["iqn"] == name for qn in discovered_qns)
        if iqn_exists:
            return utils.get_iqn_info(name)
        else:
            raise NotFoundError("GINISCSI020E")

    def login(self, name):
        utils.iscsi_target_login(name)

    def logout(self, name):
        utils.iscsi_target_logout(name)

    def rescan(self, name):
        utils.iscsi_rescan_target(name)

    def delete(self, name):
        utils.iscsi_delete_iqn(name)

    def initiator_auth(self, name, auth_type, username, password):
        if auth_type == 'CHAP':
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.authmethod',
                db_key_value=auth_type)
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.username',
                db_key_value=username)
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.password',
                db_key_value=password)
        elif auth_type == 'None':
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.authmethod',
                db_key_value=auth_type)
        else:
            raise InvalidParameter('GINISCSI012E', {'auth_type': auth_type})

    def target_auth(self, name, auth_type, username, password):
        if auth_type == 'CHAP':
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.authmethod',
                db_key_value=auth_type)
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.username_in',
                db_key_value=username)
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.password_in',
                db_key_value=password)
        elif auth_type == 'None':
            utils.iscsiadm_update_db(
                iqn=name,
                db_key='node.session.auth.authmethod',
                db_key_value=auth_type)
        else:
            raise InvalidParameter('GINISCSI012E', {'auth_type': auth_type})


class ISCSIAuthModel(object):

    def lookup(self, name):
        return utils.get_iscsi_auth_info()

    def initiator_auth(self, name, auth_type, username, password):
        utils.modify_iscsid_initiator_auth(auth_type, username, password)

    def target_auth(self, name, auth_type, username, password):
        utils.modify_iscsid_target_auth(auth_type, username, password)

    def discovery_initiator_auth(self, name, auth_type, username, password):
        utils.modify_iscsid_discovery_initiator_auth(
            auth_type, username, password)

    def discovery_target_auth(self, name, auth_type, username, password):
        utils.modify_iscsid_discovery_target_auth(
            auth_type, username, password)
