#
# Project Ginger
#
# Copyright IBM, Corp. 2014
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


SUDOERS_FILE = '/etc/sudoers.d/%s_conf'
SUDOERS_LINE = '%s\tALL=(ALL)\tALL\n'


class UsersModel():
    """
    The model class for basic management of users in the host system
    """

    def create(self, params):
        adm = libuser.admin()
        profile = params['profile']
        # Login/Group already in use ?
        user = adm.lookupUserByName(params['name'])
        group = adm.lookupGroupByName(params['group'])
        if user:
            msg = 'User/Login "%s" already in use' % params['name']
            kimchi_log.error(msg)
            raise OperationFailed('GINUSER0008E', {'user': params['name']})
        # Adding user/group
        try:
            new_user = adm.initUser(params['name'])
            # Handling user shell according to profile, else, use default shell
            if profile == "kimchiuser":
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
        except Exception as e:
            kimchi_log.error('Could not create user %s', params['name'], e)
            raise OperationFailed('GINUSER0009E', {'user': params['name']})

        # Handle profiles
        if profile in ["virtuser", "admin"]:
            self._add_user_to_kvm_group(adm, params['name'])
        if profile == "admin":
            self._add_user_to_sudoers(params['name'])

        return params['name']

    def _add_user_to_sudoers(self, user):
        try:
            # Creates the file in /etc/sudoers.d with proper user permission
            with open(SUDOERS_FILE % user, 'w') as f:
                f.write(SUDOERS_LINE % user)
            os.chmod(SUDOERS_FILE % user, 0440)
        except Exception as e:
            UserModel().delete(user)
            kimchi_log.error('Could not add user %s to sudoers: %s',
                             user, e.message)
            raise OperationFailed('GINUSER0007E', {'user': user})

    def _add_user_to_kvm_group(self, adm, user):
        # Add new user to KVM group
        kvmgrp = adm.lookupGroupByName('kvm')
        kvmgrp.add('gr_mem', user)
        ret = adm.modifyGroup(kvmgrp)
        if ret != 1:
            UserModel().delete(user)
            msg = ('Could not add user %s to kvm group. Operation failed.'
                   % user)
            kimchi_log.error(msg)
            raise OperationFailed('GINUSER0006E', {'user': user})

    def get_list(self):
        # Get list of users in the host excluding system users
        return [user.pw_name for user in pwd.getpwall() if user.pw_uid >= 1000]


class UserModel():
    def delete(self, user):
        adm = libuser.admin()
        user_obj = adm.lookupUserByName(user)
        # Check if user exist
        if user_obj is None:
            kimchi_log.error('User "%s" does not exist', user)
            raise OperationFailed('GINUSER0011E', {'user': user})
        group_obj = adm.lookupGroupById(int(user_obj.get('pw_gid')[0]))
        # Delete user with its home and mails too
        try:
            adm.deleteUser(user_obj, True, True)
        except Exception as e:
            kimchi_log.error('Could not delete user %s: %s', user, e)
            raise OperationFailed('GINUSER0010E', {'user': user})

        # Handle user according to its profile
        self._delete_profile_settings(user)

        # Delete group if no users are assigned to it
        # It is not possible to delete user/group at same time
        if group_obj is None:
            msg = 'Group for user "%s" does not exist for removal' % user
            kimchi_log.warn(msg)
            raise OperationFailed('GINUSER0013E', {'user': user})
        group = group_obj.get('gr_name')[0]
        if not adm.enumerateUsersByGroup(group):
            try:
                adm.deleteGroup(group_obj)
            except Exception as e:
                kimchi_log.error('Could not delete group "%s": %s', group, e)
                raise OperationFailed('GINUSER0012E', {'group': group})

    def lookup(self, user):
        user_info = pwd.getpwnam(user)
        return {"name": user,
                "uid": user_info.pw_uid,
                "gid": user_info.pw_gid,
                "group": grp.getgrgid(user_info.pw_gid).gr_name,
                "profile": self._get_user_profile(user)}

    def _get_user_profile(self, user):
        # ADMIN: Check /etc/sudoers.d
        if os.path.isfile(SUDOERS_FILE % user):
            return 'admin'
        # VIRTUSER: Check kvm group
        adm = libuser.admin()
        kvmgrp = adm.lookupGroupByName('kvm')
        if user in kvmgrp.get('gr_mem'):
            return 'virtuser'
        # KIMCHIUSER: If not any before
        return 'kimchiuser'

    def _delete_profile_settings(self, user):
        profile = self._get_user_profile(user)
        if profile == 'kimchiuser':
            return
        # Removing from sudoers
        elif profile == 'admin':
            f = SUDOERS_FILE % user
            try:
                os.unlink(f)
            except Exception as e:
                kimchi_log.error('Error removing file "%s": %s', f, e)

        # Finally remove from kvm group
        try:
            adm = libuser.admin()
            kvmgrp = adm.lookupGroupByName('kvm')
            # Remove all ocurrences
            members = set(kvmgrp.get('gr_mem')) - set([user])
            kvmgrp.set('gr_mem', list(members))
            adm.modifyGroup(kvmgrp)
        except Exception as e:
            kimchi_log.error('Error while removing user from kvm group: %s', e)
