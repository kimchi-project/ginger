#
# Project Kimchi
#
# Copyright IBM, Corp. 2014
#
# Authors:
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


import grp
import os
import pwd

import libuser

from kimchi.exception import OperationFailed
from kimchi.utils import kimchi_log


class UsersModel():
    """
    The model class for basic management of users in the host system
    """

    def create(self, params):
        adm = libuser.admin()
        # Login/Group already in use ?
        user = adm.lookupUserByName(params['name'])
        group = adm.lookupGroupByName(params['group'])
        if user:
            msg = 'User/Login "%s" already in use' % params['name']
            kimchi_log.error(msg)
            raise OperationFailed(msg)
        # Adding user/group
        try:
            new_user = adm.initUser(params['name'])
            new_user[libuser.LOGINSHELL] = '/sbin/nologin'
            # Creating group or adding user to existing group
            if group is None:
                new_group = adm.initGroup(params['group'])
                gid = new_group[libuser.GIDNUMBER]
                adm.addGroup(new_group)
            else:
                gid = adm.lookupGroupByName(params['group']).get('pw_gid')[0]
            new_user[libuser.GIDNUMBER] = gid
            adm.addUser(new_user)
            # Password should come encrypted
            adm.setpassUser(new_user, params['password'], True)
        except:
            kimchi_log.error('Could not add user %s', params['name'])
            raise OperationFailed('Could not add user %s' % params['name'])
        return params['name']

    def get_list(self):
        # Get list of users in the host excluding system users
        return [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]


class UserModel():
    def delete(self, user):
        adm = libuser.admin()
        user_obj = adm.lookupUserByName(user)
        group_obj = adm.lookupGroupById(int(user_obj.get('pw_gid')[0]))
        if user_obj:
            # Delete home and mails too
            try:
                adm.deleteUser(user_obj, True, True)
            except:
                kimchi_log.error('Could not delete user %s', user)
                raise OperationFailed('Could not delete user %s' % user)
        else:
            kimchi_log.error('User "%s" does not exist', user)
            raise OperationFailed('User "%s" does not exist' % user)
        # Delete group if no user are assigned to it
        # It is not possible to delete user/group at same time
        if group_obj:
            group = group_obj.get('gr_name')[0]
            if not adm.enumerateUsersByGroup(group):
                try:
                    adm.deleteGroup(group_obj)
                except:
                    kimchi_log.error('Could not delete group "%s"', group)
                    raise OperationFailed('Could not delete group "%s"'
                                          % group)
        else:
            msg = 'Group for user "%s" does not exist for removal' % user
            kimchi_log.warn(msg)
            raise OperationFailed(msg)

    def lookup(self, user):
        user_info = pwd.getpwnam(user)
        return {"name": user,
                "uid": user_info.pw_uid,
                "gid": user_info.pw_gid,
                "group": grp.getgrgid(user_info.pw_gid).gr_name}
