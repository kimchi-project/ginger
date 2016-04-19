# -*- coding: utf-8 -*-
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

import augeas
import crypt
import os
import pwd
import random
import string

import libuser

from wok.exception import InvalidParameter, NotFoundError, OperationFailed
from wok.rollbackcontext import RollbackContext
from wok.utils import wok_log


SUDOERS_FILE = '/etc/sudoers.d/%s_conf'
SUDOERS_LINE = '%s\tALL=(ALL)\tALL\n'
SUDOERS_CHECK = 'etc/sudoers/spec/user'


def get_groups():
    adm = libuser.admin()
    return adm.enumerateGroups()


def get_group_obj(groupname):
    adm = libuser.admin()
    return adm.lookupGroupByName(groupname)


def get_group_obj_by_gid(gid):
    adm = libuser.admin()
    return adm.lookupGroupById(gid)


def get_group_gid(groupname):
    adm = libuser.admin()
    if isinstance(groupname, unicode):
        groupname = groupname.encode('utf-8')
    group = adm.lookupGroupByName(groupname)
    if group is None:
        return None
    return group.get('pw_gid')[0]


def create_group(groupname):
    """
    method to create user group
    :param groupname: non-empty string
    :return: group id(gid)
    """
    wok_log.info('in create_group() method. group name: %s' % groupname)
    if not isinstance(groupname, str) or not groupname.strip():
        wok_log.error('group name is not non-empty string. '
                      'group name %s' % groupname)
        raise InvalidParameter('GINUSER0014E',
                               {'group': groupname,
                                'err': 'see log for details'})
    adm = libuser.admin()
    if adm.lookupGroupByName(groupname):
        raise OperationFailed('GINUSER0018E', {'group': groupname})
    try:
        new_group = adm.initGroup(groupname)
        if new_group[libuser.GIDNUMBER][0] < 1000:
            new_group.set(libuser.GIDNUMBER, adm.getFirstUnusedGid(1000))
        adm.addGroup(new_group)
        wok_log.info('successfully created group. group name: %s.' % groupname)
        return new_group[libuser.GIDNUMBER][0]

    except Exception as e:
        raise OperationFailed('GINUSER0014E', {'group': groupname, 'err': e})


def delete_group(groupname):
    wok_log.info('in delete_group(). group name: %s' % groupname)
    if not isinstance(groupname, str) or not groupname.strip():
        wok_log.error('group name is not non-empty string. '
                      'group name %s' % groupname)
        raise InvalidParameter('GINUSER0012E',
                               {'group': groupname,
                                'err': 'see log for details'})
    adm = libuser.admin()
    group_id = int(get_group_gid(groupname))

    if group_id <= 1000:
        wok_log.error('Ignoring deletion of system group "%s" with gid %s'
                      % (groupname, group_id))
        return

    group_obj = adm.lookupGroupById(group_id)

    if not group_obj:
        wok_log.error('Could not locate group "%s" with gid %s'
                      % (groupname, group_id))
        return

    if not adm.enumerateUsersByGroup(groupname):
        # groups prepend with '%'
        if '%' + groupname in get_sudoers(admin_check=False):
            raise OperationFailed('GINUSER0017E', {'group': groupname})
        try:
            adm.deleteGroup(group_obj)
        except Exception as e:
            raise OperationFailed('GINUSER0012E',
                                  {'group': groupname, 'err': e.__str__()})

    wok_log.info('end of delete_group(). group name: %s' % groupname)


def get_users_from_group(groupname):
    adm = libuser.admin()
    if isinstance(groupname, unicode):
        groupname = groupname.encode('utf-8')
    group_obj = adm.lookupGroupById(
        int(get_group_gid(groupname))
    )
    if group_obj is not None:
        return adm.enumerateUsersByGroup(groupname)
    return None


def get_users(exclude_system_users=True):
    if exclude_system_users:
        return [user.pw_name for user in pwd.getpwall()
                if user.pw_uid >= 1000]

    admin = libuser.admin()
    return admin.enumerateUsers()


def get_user_obj(username):
    adm = libuser.admin()
    if isinstance(username, unicode):
        username = username.encode('utf-8')
    return adm.lookupUserByName(username)


def gen_salt():
    # Generate strongest encryption to user passwords:
    # $6$ - SHA512, plus 16 bytes random SALT
    chars = string.letters + string.digits + './'
    return "$6$" + "".join([random.choice(chars) for x in range(16)])


def create_user(name, plain_passwd, gid, no_login=False):
    """
    method to create user
    :param name: user name
    :param plain_passwd: password for user
    :param gid: primary group id for user
    :param no_login: True/False for log in shell
    """
    wok_log.info('in create_user() method')
    if not isinstance(name, str) or not name.strip():
        wok_log.error('user name is not non-empty string. name: %s' % name)
        raise InvalidParameter(
            'GINUSER0009E', {'user': name, 'err': 'see log for details'})
    if not type(gid) in [int, long]:
        wok_log.error('group id is not of integer type. gid: %s' % gid)
        raise InvalidParameter('GINUSER0009E', {'user': name,
                                                'err': 'see log for details'})
    if not isinstance(no_login, bool):
        wok_log.error('no_login id is not of boolean type.'
                      ' no_login: %s' % no_login)
        raise InvalidParameter('GINUSER0009E',
                               {'user': name,
                                'err': 'see log for details'})
    adm = libuser.admin()
    if adm.lookupUserByName(name):
        raise OperationFailed('GINUSER0008E', {'user': name})

    if not adm.lookupGroupById(gid):
        raise OperationFailed(
            'GINUSER0009E', {'user': name,
                             'err': "group with id %s doesn't exist" % gid})

    try:
        new_user = adm.initUser(name)
        # Ensure user is normal and not system user
        if new_user[libuser.UIDNUMBER][0] < 1000:
            new_user.set(libuser.UIDNUMBER, adm.getFirstUnusedUid(1000))

        new_user.set(libuser.GIDNUMBER, gid)

        if no_login:
            new_user[libuser.LOGINSHELL] = '/sbin/nologin'
        adm.addUser(new_user)

        # Setting user password. Crypt in Python 3.3 and some 2.7 backports
        # bring mksalt function, so, use it or use our self salt generator
        # Creates strongest encryption (SHA512 + 16 bytes SALT)
        if hasattr(crypt, "mksalt"):
            salt = crypt.mksalt(crypt.METHOD_SHA512)
        else:
            salt = gen_salt()
        enc_pwd = crypt.crypt(plain_passwd, salt)

        adm.setpassUser(new_user, enc_pwd, True)

    except UnicodeEncodeError as ue:
        err_msg = ue.message if ue.message else 'Username / password \
            has NON - ASCII charater'
        raise OperationFailed('GINUSER0009E', {'user': name, 'err': err_msg})

    except Exception as e:
        err_msg = e.message if e.message else e
        raise OperationFailed('GINUSER0009E', {'user': name, 'err': err_msg})
    wok_log.info('end of create_user() method')


def delete_user(username):
    """
    method to delete user
    :param username: user name
    """
    wok_log.info('in delete_user() method')
    if not isinstance(username, str) or not username.strip():
        wok_log.error('username is not non-empty string. name: %s' % username)
        raise InvalidParameter('GINUSER0010E', {'user': username,
                                                'err': 'see log for details'})
    if username in get_sudoers(admin_check=False):
        raise OperationFailed('GINUSER0016E', {'user': username})

    adm = libuser.admin()
    user_obj = adm.lookupUserByName(username)

    if not user_obj:
        raise OperationFailed('GINUSER0011E', {'user': username})

    groups = adm.enumerateGroupsByUser(username)
    for group in groups:
        # remove user from all groups
        remove_user_from_group(username, group)

    f = SUDOERS_FILE % username
    if os.path.isfile(f):
        try:
            os.unlink(f)
        except Exception as e:
            wok_log.error('Error removing file "%s": %s' % (f, e))
            raise OperationFailed('GINUSER0013E', {'user': username})
    try:
        adm.deleteUser(user_obj, True, True)
    except Exception as e:
        raise OperationFailed('GINUSER0010E',
                              {'user': username, 'err': e.__str__()})
    wok_log.info('end of delete_user() method')


def remove_user_from_group(user, group):
    """
    method to remove user from group
    :param user: user name
    :param group: group name
    """
    wok_log.info('in remove_user_from_group() method')
    if not isinstance(user, str) or not user.strip():
        wok_log.error('user name is not non-empty string. name: %s' % user)
        raise InvalidParameter('GINUSER0010E',
                               {'user': user, 'err': 'see log for details'})
    if not isinstance(group, str) or not group.strip():
        wok_log.error('group name is not non-empty string. '
                      'group name %s' % group)
        raise InvalidParameter('GINUSER0010E',
                               {'user': user, 'err': 'see log for details'})
    try:
        adm = libuser.admin()
        grpobj = adm.lookupGroupByName(group)
        # Remove all ocurrences
        members = set(grpobj.get('gr_mem'))
        if user in members:
            members = set(grpobj.get('gr_mem')) - set([user])
            grpobj.set('gr_mem', list(members))
            adm.modifyGroup(grpobj)
    except Exception as e:
        raise OperationFailed('GINUSER0021E', {'user': user, 'group': group,
                                               'err': e.__str__()})
    wok_log.info('end of remove_user_from_group() method')


def get_sudoers(admin_check=True):
    """
    method to get user and groups mentioned in /etc/sudoers file
    if admin_check is True - return users and groups with admin privilege
    if False, return users and groups is mentioned in /etc/sudoers file
    :param admin_check: True/False (to check admin/just part of sudoers file)
    :return: list of users and groups
    """
    wok_log.info('in get_sudoers() method')
    sudoers = []
    try:
        parser = augeas.Augeas()
        parser.load()
        users = parser.match(SUDOERS_CHECK)
        # sample ouput with augeas:
        # parser.match('etc/sudoers/spec/user')
        # [u'/files/etc/sudoers/spec[1]/user',
        #  u'/files/etc/sudoers/spec[2]/user',
        #  u'/files/etc/sudoers/spec[3]/user']
        # indicates /etc/sudoers file has 3 users/groups
        for user in users:
            name = parser.get(user)
            if isinstance(name, unicode):
                # augeas returns in unicode format
                name = name.encode('utf-8')
            if admin_check:
                user = user.rstrip('user') + 'host_group'
                # to check for commands and host
                # parser.get('etc/sudoers/spec[1]/host_group/host')
                # u'ALL'
                # parser.get('etc/sudoers/spec[1]/host_group/command')
                # Out[35]: u'ALL'
                if 'ALL' == parser.get(user + '/command') and\
                   'ALL' == parser.get(user + '/host'):
                    sudoers.append(name)
            else:
                sudoers.append(name)
    except Exception as e:
        raise OperationFailed('GINUSER0019E', {'error': e.__str__()})
    wok_log.info('end of get_sudoers() method, sudoers: %s' % sudoers)
    return sudoers


def get_users_info(users):
    """
    method to get users details - uid, group name, group id, profile
    :param users: list of users
    :return: list of dictionary with user details
    """
    wok_log.info('in get_users_info(). Users: %s' % users)
    if not isinstance(users, list):
        wok_log.error('Users is not of type list. Users: %s' % users)
        raise InvalidParameter('GINUSER0022E')
    users_info = []
    sudoers = get_sudoers(admin_check=True)
    for user in users:
        try:
            user_info = pwd.getpwnam(user)
        except Exception as e:
            wok_log.error('pwd.getpwnam(%s) exception. Error: %s' % (user, e))
            raise NotFoundError('GINUSER0011E', {'user': user})
        if not user_info:
            raise NotFoundError('GINUSER0011E', {'user': user})
        if user_info.pw_uid < 1000:
            raise OperationFailed('GINUSER0020E')

        adm = libuser.admin()
        group_obj = adm.lookupGroupById(user_info.pw_gid)
        if group_obj:
            group_name = group_obj.get('gr_name')
        else:
            group_name = 'undefined'

        users_info.append(
            {"name": user,
             "uid": user_info.pw_uid,
             "gid": user_info.pw_gid,
             "group": group_name,
             "profile": get_user_profile(user, sudoers)})
    wok_log.info('end of get_users_info(). Users details: %s' % users_info)
    return users_info


def get_user_profile(user, sudoers=None):
    """
    method to check user profile
    :param user: username
    :param sudoers: list of sudoers from /etc/sudoers file
    :return: admin, virtuser or regularuser
    """
    if not isinstance(user, str) or not user.strip():
        wok_log.error('username is not non-empty string. name: %s' % user)
        raise InvalidParameter('GINUSER0002E')
    if sudoers and not isinstance(sudoers, list):
        wok_log.error('Sudoers is not of type list. Sudoers: %s' % sudoers)
        raise InvalidParameter('GINUSER0023E')
    if os.path.isfile(SUDOERS_FILE % user):
        return 'admin'
    adm = libuser.admin()
    groups = adm.enumerateGroupsByUser(user)
    # check for admin groups
    if 'wheel' in groups or 'sudo' in groups:
        return 'admin'
    # check user and groups in /etc/sudoers file
    if sudoers is None:
        # checking None, to avoid get_sudoers() call, in case of empty list
        sudoers = get_sudoers()
    if user in sudoers:
        return 'admin'
    for group in groups:
        # groups prepend with '%'
        if '%' + group in sudoers:
            return 'admin'

    # VIRTUSER: Check kvm group
    if 'kvm' in groups:
        return 'virtuser'

    # REGULARUSER: If not any before
    return 'regularuser'


class UsersModel(object):
    """
    The model class for basic management of users in the host system
    """

    def create(self, params):
        params = self._validate_create_params(params)
        username = params['name']
        passwd = params['password']
        profile = params['profile']
        groupname = params['group']
        no_login = params['no_login']

        with RollbackContext() as rollback:
            adm = libuser.admin()
            if groupname:
                group_obj = adm.lookupGroupByName(groupname)
                if group_obj:
                    group_id = group_obj.get('pw_gid')[0]
                else:
                    group_id = create_group(groupname)
                    rollback.prependDefer(delete_group, groupname)
            else:
                group_id = create_group(username)
                rollback.prependDefer(delete_group, username)
            create_user(username, passwd, group_id, no_login=no_login)
            rollback.prependDefer(delete_user, username)
            if profile == 'virtuser':
                self._add_user_to_kvm_group(username)
            if profile == 'admin':
                self._add_user_to_sudoers(username)
            rollback.commitAll()
        return username

    def _validate_create_params(self, params):
        """
        method to validate create parameters
        :return: params dictionary with keys: name, password,
                 profile, group and no_login
        """
        wok_log.info('in _validate_create_params(). params: %s' % params)
        if not isinstance(params, dict):
            wok_log.error(
                'Params is not of type dictionary. Params: %s' % params)
            raise InvalidParameter('GINUSER0001E')
        keys = params.keys()
        if isinstance(params['name'], unicode):
            params['name'] = params['name'].encode('utf-8')
        if not params['name'].strip():
            raise InvalidParameter('GINUSER0002E')
        if isinstance(params['password'], unicode):
            params['password'] = params['password'].encode('utf-8')
        if not params['password'].strip():
            raise InvalidParameter('GINUSER0003E')
        if 'group' in keys:
            if isinstance(params['group'], unicode):
                params['group'] = params['group'].encode('utf-8')
            if not params['group'].strip():
                # if group is empty string or only spaces then
                # set group to None to create new group with username
                params['group'] = None
        else:
            # if group is not in params, set group to None to
            # create new group with username
            params['group'] = None
        if 'profile' in keys:
            if isinstance(params['profile'], unicode):
                params['profile'] = params['profile'].encode('utf-8')
            if not params['profile'] in ['regularuser', 'virtuser', 'admin']:
                raise InvalidParameter('GINUSER0005E')
            if params['profile'] == 'regularuser':
                if 'no_login' in keys:
                    if not isinstance(params['no_login'], bool):
                        raise InvalidParameter('GINUSER0015E')
                else:
                    params['no_login'] = False
            else:
                # for other users use log in shell
                params['no_login'] = False
        else:
            # if profile is not passed, assume regular user with log in shell
            params['profile'] = 'regularuser'
            params['no_login'] = False

        wok_log.info(
            'End of _validate_create_params(). Return params: %s' % params)
        return params

    def _add_user_to_kvm_group(self, user):
        # Add new user to KVM group
        if not isinstance(user, str) or not user.strip():
            wok_log.error('username is not non-empty string. name: %s' % user)
            raise InvalidParameter('GINUSER0009E',
                                   {'user': user,
                                    'err': 'see log for details'})
        adm = libuser.admin()
        kvmgrp = get_group_obj('kvm')
        if isinstance(user, unicode):
            user = user.encode('utf-8')
        kvmgrp.add('gr_mem', user)
        ret = adm.modifyGroup(kvmgrp)
        if ret != 1:
            raise OperationFailed('GINUSER0006E', {'user': user})

    def _add_user_to_sudoers(self, user):
        if not isinstance(user, str) or not user.strip():
            wok_log.error('username is not non-empty string. name: %s' % user)
            raise InvalidParameter('GINUSER0009E',
                                   {'user': user,
                                    'err': 'see log for details'})
        try:
            # Creates the file in /etc/sudoers.d with proper user permission
            with open(SUDOERS_FILE % user, 'w') as f:
                f.write(SUDOERS_LINE % user)
            os.chmod(SUDOERS_FILE % user, 0440)
        except Exception as e:
            if os.path.isfile(SUDOERS_FILE % user):
                os.unlink(SUDOERS_FILE % user)
            raise OperationFailed('GINUSER0007E', {'user': user,
                                                   'err': e})

    def get_list(self):
        users = get_users()
        return get_users_info(users)


class UserModel(object):
    def delete(self, user):
        if isinstance(user, unicode):
            user = user.encode('utf-8')
        if not isinstance(user, str) or not user.strip():
            raise InvalidParameter('GINUSER0002E')
        user_obj = get_user_obj(user)
        if user_obj:
            group_id = int(user_obj.get('pw_gid')[0])
            group_obj = get_group_obj_by_gid(group_id)
        else:
            raise OperationFailed('GINUSER0011E', {'user': user})

        delete_user(user)
        if group_id > 1000 and group_obj:
            groupname = group_obj.get('gr_name')[0]
            delete_group(groupname)

    def lookup(self, user):
        if isinstance(user, unicode):
            user = user.encode('utf-8')
        if not isinstance(user, str) or not user.strip():
            raise InvalidParameter('GINUSER0002E')
        try:
            user_info = get_users_info([user])
        except Exception:
            raise NotFoundError('GINUSER0011E', {'user': user})
        if not user_info:
            raise NotFoundError('GINUSER0011E', {'user': user})
        return user_info[0]
