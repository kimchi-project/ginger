#
# Project Ginger
#
# Copyright IBM Corp, 2015-2016
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


import mock
import unittest

from wok.exception import InvalidParameter, NotFoundError, OperationFailed

from plugins.ginger.model.users import create_group, create_user
from plugins.ginger.model.users import delete_group, delete_user
from plugins.ginger.model.users import get_user_profile
from plugins.ginger.model.users import UserModel, UsersModel


class CreateGroupUnitTests(unittest.TestCase):
    """
    Unit tests for create_group() method
    """
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_create_group_empty_name(self, mock_log):
        """
        unittest to validate create_group method with empty group name
        mock_log: mock of wok_log imported in model.users
        """
        self.assertRaises(InvalidParameter, create_group, '')
        mock_log.error.assert_called_once_with(
            'group name is not non-empty string. group name %s' % '')

    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_create_group_invalid_input(self, mock_log):
        """
        unittest to validate create_group method with invalid input
        for example integer value for group name instead of string
        mock_log: mock of wok_log imported in model.users
        """
        self.assertRaises(InvalidParameter, create_group, 12)
        mock_log.error.assert_called_once_with(
            'group name is not non-empty string. group name %s' % 12)

    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    def test_create_existing_group(self, mock_libuser, mock_log):
        """
        unittest to validate create_group method with invalid input
        for example integer value for group name instead of string
        mock_libuser: mock of libuser imported in model.users
        mock_log: mock of wok_log imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupGroupByName.return_value = 'dummy_group'
        self.assertRaises(OperationFailed, create_group, 'dummy_group')

    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    def test_create_grp_libuser_exception(self, mock_libuser, mock_log):
        """
        unittest to validate create_group when exception
        in adm.initGroup or adm.addGroup
        mock_libuser: mock of libuser imported in model.users
        mock_log: mock of wok_log imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupGroupByName.return_value = False
        mock_adm.addGroup.side_effect = Exception('fail')
        self.assertRaises(OperationFailed, create_group, 'dummy_group')
        mock_adm.initGroup.assert_called_once_with('dummy_group')

    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    def test_create_grp_success(self, mock_libuser, mock_log):
        """
        unittest to validate create_group success case
        mock_libuser: mock of libuser imported in model.users
        mock_log: mock of wok_log imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_libuser.GIDNUMBER.return_value = 1200
        mock_adm.lookupGroupByName.return_value = False
        create_group('dummy_group')
        mock_adm.initGroup.assert_called_once_with('dummy_group')
        self.assertTrue(mock_adm.addGroup.called,
                        msg='Expected call to mock_adm.addGroup(). '
                            'Not called')
        mock_log.info.assert_called_with(
            'successfully created group. group name: %s.' % 'dummy_group')


class DeleteGroupUnitTests(unittest.TestCase):
    """
    Unit tests for delete_group() method
    """
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_group_empty_name(self, mock_log):
        """
        unittest to validate delete_group method with empty group name
        mock_log: mock of wok_log imported in model.users
        """
        self.assertRaises(InvalidParameter, delete_group, '')
        mock_log.error.assert_called_once_with(
            'group name is not non-empty string. group name %s' % '')

    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_group_invalid_input(self, mock_log):
        """
        unittest to validate delete_group method with invalid input
        for example integer value for group name instead of string
        mock_log: mock of wok_log imported in model.users
        """
        self.assertRaises(InvalidParameter, delete_group, 12)
        mock_log.error.assert_called_once_with(
            'group name is not non-empty string. group name %s' % 12)

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.get_group_gid', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_system_group(self, mock_log, mock_libuser, mock_get_gid,
                                 mock_get_sudoers):
        """
        unittest to validate delete_group method for system group deletion
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_gid: mock of get_group_gid() method in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_get_gid.return_value = 10
        delete_group('dummy_group')
        mock_log.error('Ignoring deletion of system group "%s" with gid %s'
                       % ('dummy_group', 10))
        self.assertFalse(mock_get_sudoers.called, msg='Unexpected'
                         ' call to mock_get_sudoers')
        self.assertFalse(mock_adm.lookupGroupById.called, msg='Unexpected'
                         ' call to mock_adm.lookupGroupById')
        self.assertFalse(mock_adm.enumerateUsersByGroup.called,
                         msg='Unexpected call to '
                             'mock_adm.enumerateUsersByGroup')
        self.assertFalse(mock_adm.deleteGroup.called, msg='Unexpected'
                         ' call to mock_adm.deleteGroup')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.get_group_gid', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_nonempty_group(self, mock_log, mock_libuser, mock_get_gid,
                                   mock_get_sudoers):
        """
        unittest to validate delete_group method for a group with users
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_gid: mock of get_group_gid() method in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_get_gid.return_value = 1020
        mock_adm.lookupGroupById.return_value = 'dummy_info'
        mock_adm.enumerateUsersByGroup.return_value = ['dummy_users']
        delete_group('dummy_group')
        mock_adm.lookupGroupById.assert_called_once_with(1020)
        mock_adm.enumerateUsersByGroup.assert_called_once_with('dummy_group')
        self.assertFalse(mock_get_sudoers.called, msg='Unexpected'
                         ' call to mock_get_sudoers')
        self.assertFalse(mock_adm.deleteGroup.called, msg='Unexpected'
                         ' call to mock_adm.deleteGroup')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.get_group_gid', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_group_sudoer_group(self, mock_log, mock_libuser,
                                       mock_get_gid, mock_get_sudoers):
        """
        unittest to validate delete_group method for a
        group which is part of /etc/sudoers file
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_gid: mock of get_group_gid() method in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_get_gid.return_value = 1020
        mock_adm.lookupGroupById.return_value = 'dummy_info'
        mock_adm.enumerateUsersByGroup.return_value = []
        mock_get_sudoers.return_value = ['%dummy_group']
        self.assertRaises(OperationFailed, delete_group, 'dummy_group')
        mock_adm.lookupGroupById.assert_called_once_with(1020)
        mock_adm.enumerateUsersByGroup.assert_called_once_with('dummy_group')
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        self.assertFalse(mock_adm.deleteGroup.called, msg='Unexpected'
                         ' call to mock_adm.deleteGroup')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.get_group_gid', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_group_success(self, mock_log, mock_libuser, mock_get_gid,
                                  mock_get_sudoers):
        """
        unittest to validate delete_group method success case
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_gid: mock of get_group_gid() method in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_get_gid.return_value = 1020
        mock_adm.lookupGroupById.return_value = 'dummy_info'
        mock_adm.enumerateUsersByGroup.return_value = []
        mock_get_sudoers.return_value = []
        delete_group('dummy_group')
        mock_adm.lookupGroupById.assert_called_once_with(1020)
        mock_adm.enumerateUsersByGroup.assert_called_once_with('dummy_group')
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        mock_log.info.assert_called_with(
            'end of delete_group(). group name: %s' % 'dummy_group')
        mock_adm.deleteGroup.assert_called_once_with('dummy_info')


class CreateUserUnitTests(unittest.TestCase):
    """
    Unit tests for create_user() method
    """
    @mock.patch('plugins.ginger.model.users.crypt', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_create_existing_user(self, mock_log, mock_libuser, mock_crypt):
        """
        unittest to validate create_user method for existing user
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_crypt: mock of crypt imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = 'user_found'
        self.assertRaises(OperationFailed, create_user, 'dummy_user',
                          'password', 1020, no_login=False)
        self.assertFalse(mock_adm.lookupGroupById.called,
                         msg='Unexpected call to mock_adm.lookupGroupById')
        self.assertFalse(mock_adm.initUser.called,
                         msg='Unexpected call to mock_adm.initUser')
        self.assertFalse(mock_adm.addUser.called,
                         msg='Unexpected call to mock_adm.addUser')
        self.assertFalse(mock_adm.setpassUser.called,
                         msg='Unexpected call to mock_adm.setpassUser')

    @mock.patch('plugins.ginger.model.users.crypt', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_group_not_found(self, mock_log, mock_libuser, mock_crypt):
        """
        unittest to validate create_user method for non existing gid
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_crypt: mock of crypt imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = False
        mock_adm.lookupGroupById.return_value = False
        self.assertRaises(OperationFailed, create_user, 'dummy_user',
                          'password', 1020, no_login=False)
        mock_adm.lookupGroupById.assert_called_once_with(1020)
        self.assertFalse(mock_adm.initUser.called,
                         msg='Unexpected call to mock_adm.initUser')
        self.assertFalse(mock_adm.addUser.called,
                         msg='Unexpected call to mock_adm.addUser')
        self.assertFalse(mock_adm.setpassUser.called,
                         msg='Unexpected call to mock_adm.setpassUser')

    @mock.patch('plugins.ginger.model.users.crypt', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_create_exception(self, mock_log, mock_libuser, mock_crypt):
        """
        unittest to validate create_user method for libuser exception
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_crypt: mock of crypt imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = False
        mock_adm.lookupGroupById.return_value = True
        mock_adm.addUser.side_effect = Exception('fail')
        self.assertRaises(OperationFailed, create_user, 'dummy_user',
                          'password', 1020, no_login=False)
        mock_adm.lookupGroupById.assert_called_once_with(1020)
        mock_adm.initUser.assert_called_once_with('dummy_user')
        self.assertTrue(mock_adm.addUser.called,
                        msg='Expected call to mock_adm.addUser. Not called')
        self.assertFalse(mock_adm.setpassUser.called,
                         msg='Unexpected call to mock_adm.setpassUser')

    @mock.patch('plugins.ginger.model.users.crypt', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_create_user_success(self, mock_log, mock_libuser, mock_crypt):
        """
        unittest to validate create_user method for success scenario
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_crypt: mock of crypt imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = False
        mock_adm.lookupGroupById.return_value = True
        create_user('dummy_user', 'password', 1020, no_login=False)
        mock_adm.lookupGroupById.assert_called_once_with(1020)
        mock_adm.initUser.assert_called_once_with('dummy_user')
        self.assertTrue(mock_adm.addUser.called,
                        msg='Expected call to mock_adm.addUser. Not called')
        self.assertTrue(mock_adm.setpassUser.called,
                        msg='Expected call to mock_adm.setpassUser. '
                            'Not called')


class DeleteUserUnitTests(unittest.TestCase):
    """
    Unit tests for delete_user() method
    """
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_empty_name(self, mock_log):
        """
        unittest to validate delete_user method with empty user name
        mock_log: mock of wok_log imported in model.users
        """
        self.assertRaises(InvalidParameter, delete_user, '')
        mock_log.error.assert_called_once_with(
            'username is not non-empty string. name: %s' % '')

    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_invalid_input(self, mock_log):
        """
        unittest to validate delete_user method with invalid input
        for example integer value for user name instead of string
        mock_log: mock of wok_log imported in model.users
        """
        self.assertRaises(InvalidParameter, delete_user, 12)
        mock_log.error.assert_called_once_with(
            'username is not non-empty string. name: %s' % 12)

    @mock.patch('plugins.ginger.model.users.remove_user_from_group',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_sudoers(self, mock_log, mock_libuser, mock_os,
                                 mock_get_sudoers, mock_remove_from_group):
        """
        unittest to validate delete_user for user in /etc/sudoers file
        for example integer value for user name instead of string
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        mock_remove_from_group: mock of remove_user_from_group() method
                in model.users
        mock_os: mock of os imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_get_sudoers.return_value = ['dummy_user']
        self.assertRaises(OperationFailed, delete_user, 'dummy_user')
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        self.assertFalse(mock_adm.lookupUserByName.called,
                         msg='Unexpected call to mock_adm.lookupUserByName')
        self.assertFalse(mock_adm.deleteUser.called,
                         msg='Unexpected call to mock_adm.deleteUser')
        self.assertFalse(mock_remove_from_group.called,
                         msg='Unexpected call to mock_remove_from_group')
        self.assertFalse(mock_os.path.isfile.called,
                         msg='Unexpected call to mock_os.path.isfile')
        self.assertFalse(mock_os.unlink.called,
                         msg='Unexpected call to mock_os.unlink')

    @mock.patch('plugins.ginger.model.users.remove_user_from_group',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_not_found(self, mock_log, mock_libuser, mock_os,
                                   mock_get_sudoers, mock_remove_from_group):
        """
        unittest to validate delete_user for user doesn't exist
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        mock_remove_from_group: mock of remove_user_from_group() method
                in model.users
        mock_os: mock of os imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = False
        mock_get_sudoers.return_value = []
        self.assertRaises(OperationFailed, delete_user, 'dummy_user')
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        mock_adm.lookupUserByName.assert_called_once_with('dummy_user')
        self.assertFalse(mock_adm.deleteUser.called,
                         msg='Unexpected call to mock_adm.deleteUser')
        self.assertFalse(mock_remove_from_group.called,
                         msg='Unexpected call to mock_remove_from_group')
        self.assertFalse(mock_os.path.isfile.called,
                         msg='Unexpected call to mock_os.path.isfile')
        self.assertFalse(mock_os.unlink.called,
                         msg='Unexpected call to mock_os.unlink')

    @mock.patch('plugins.ginger.model.users.remove_user_from_group',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_unlink_exception(self, mock_log, mock_libuser,
                                          mock_os, mock_get_sudoers,
                                          mock_remove_from_group):
        """
        unittest to validate delete_user for exception in os.unlink
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        mock_remove_from_group: mock of remove_user_from_group() method
                in model.users
        mock_os: mock of os imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = 'dummy_info'
        mock_adm.enumerateGroupsByUser.return_value = ['dummy_group']
        mock_os.unlink.side_effect = Exception('fail')
        mock_get_sudoers.return_value = []
        self.assertRaises(OperationFailed, delete_user, 'dummy_user')
        f = '/etc/sudoers.d/dummy_user_conf'
        mock_log.error.assert_called_once_with(
            'Error removing file "%s": %s' % (f, 'fail'))
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        mock_adm.lookupUserByName.assert_called_once_with('dummy_user')
        self.assertFalse(mock_adm.deleteUser.called,
                         msg='Unexpected call to mock_adm.deleteUser')
        mock_remove_from_group.assert_called_once_with(
            'dummy_user', 'dummy_group')
        mock_os.path.isfile.assert_called_once_with(f)
        mock_os.unlink.assert_called_once_with(f)

    @mock.patch('plugins.ginger.model.users.remove_user_from_group',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_exception(self, mock_log, mock_libuser, mock_os,
                                   mock_get_sudoers, mock_remove_from_group):
        """
        unittest to validate delete_user for exception in deleteUser
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        mock_remove_from_group: mock of remove_user_from_group() method
                in model.users
        mock_os: mock of os imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = 'dummy_info'
        mock_adm.enumerateGroupsByUser.return_value = ['dummy_group']
        mock_adm.deleteUser.side_effect = Exception('fail')
        mock_get_sudoers.return_value = []
        self.assertRaises(OperationFailed, delete_user, 'dummy_user')
        f = '/etc/sudoers.d/dummy_user_conf'
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        mock_adm.lookupUserByName.assert_called_once_with('dummy_user')
        mock_adm.deleteUser.assert_called_once_with('dummy_info', True, True)
        mock_remove_from_group.assert_called_once_with(
            'dummy_user', 'dummy_group')
        mock_os.path.isfile.assert_called_once_with(f)
        mock_os.unlink.assert_called_once_with(f)

    @mock.patch('plugins.ginger.model.users.remove_user_from_group',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_user_success(self, mock_log, mock_libuser, mock_os,
                                 mock_get_sudoers, mock_remove_from_group):
        """
        unittest to validate delete_user for success scenario
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_sudoers: mock of get_sudoers() method in model.users
        mock_remove_from_group: mock of remove_user_from_group() method
                in model.users
        mock_os: mock of os imported in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.lookupUserByName.return_value = 'dummy_info'
        mock_adm.enumerateGroupsByUser.return_value = ['dummy_group']
        mock_get_sudoers.return_value = []
        delete_user('dummy_user')
        f = '/etc/sudoers.d/dummy_user_conf'
        mock_get_sudoers.assert_called_once_with(admin_check=False)
        mock_adm.lookupUserByName.assert_called_once_with('dummy_user')
        mock_adm.deleteUser.assert_called_once_with('dummy_info', True, True)
        mock_remove_from_group.assert_called_once_with(
            'dummy_user', 'dummy_group')
        mock_os.path.isfile.assert_called_once_with(f)
        mock_os.unlink.assert_called_once_with(f)


class UsersModelUnitTests(unittest.TestCase):
    """
    Unit tests for UsersModel()
    """
    @mock.patch('plugins.ginger.model.users.create_user', autospec=True)
    @mock.patch('plugins.ginger.model.users.create_group', autospec=True)
    @mock.patch('plugins.ginger.model.users.UsersModel', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.RollbackContext', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_create_default(self, mock_log, mock_rollback, mock_libuser,
                            mock_users_model, mock_create_group,
                            mock_create_user):
        """
        unittest to validate create method with only username and password
        mock_log: mock of wok_log imported in model.users
        mock_rollback: mock of RollbackContext imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_users_model: mock of UsersModel()  in model.users
        mock_create_group: mock of create_group()  in model.users
        mock_create_user: mock of create_user()  in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_users = mock_users_model()
        inpt = {'name': 'user1', 'password': 'password'}
        mock_users._validate_create_params.return_value = {
            'name': 'user1', 'password': 'password', 'group': None,
            'profile': 'regularuser', 'no_login': 'False'}
        mock_create_group.return_value = 1400
        users = UsersModel()
        users.create(inpt)
        self.assertFalse(mock_adm.lookupGroupByName.called,
                         msg='Unexpected call to mock_adm.lookupGroupByName')
        self.assertFalse(mock_adm.lookupGroupByName.called,
                         msg='Unexpected call to mock_adm.lookupGroupByName')
        self.assertFalse(mock_users._add_user_to_kvm_group.called,
                         msg='Unexpected call to '
                             'mock_users._add_user_to_kvm_group')
        self.assertFalse(mock_users._add_user_to_sudoers.called,
                         msg='Unexpected call to '
                             'mock_users._add_user_to_sudoers')
        mock_create_group.assert_called_once_with('user1')
        mock_create_user.assert_called_once_with('user1', 'password',
                                                 1400, no_login=False)

    @mock.patch('plugins.ginger.model.users.get_group_obj', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_addto_kvm_grp_fail(self, mock_log, mock_libuser,
                                mock_get_grp_obj):
        """
        unittest to validate _add_user_to_sudoers() method
        when modifyGroup() fails
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_grp_obj: mock of get_group_obj() method of model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.modifyGroup.return_value = 5
        users = UsersModel()
        self.assertRaises(OperationFailed,
                          users._add_user_to_kvm_group, 'user1')
        self.assertTrue(mock_adm.modifyGroup.called,
                        msg='Expected call to adm.modifyGroup(). Not Called.')
        mock_get_grp_obj.assert_called_once_with('kvm')

    @mock.patch('plugins.ginger.model.users.get_group_obj', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_addto_kvm_grp_success(self, mock_log, mock_libuser,
                                   mock_get_grp_obj):
        """
        unittest to validate _add_user_to_sudoers() method
        for success scenario
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_get_grp_obj: mock of get_group_obj() method of model.users
        """
        mock_adm = mock_libuser.admin()
        mock_adm.modifyGroup.return_value = 1
        users = UsersModel()
        users._add_user_to_kvm_group('user1')
        self.assertTrue(mock_adm.modifyGroup.called,
                        msg='Expected call to adm.modifyGroup(). Not Called.')
        mock_get_grp_obj.assert_called_once_with('kvm')

    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_addto_sudoers_fail(self, mock_log, mock_os):
        """
        unittest to validate _add_user_to_sudoers() method
        with exception in file creation
        mock_log: mock of wok_log imported in model.users
        mock_os: mock of os imported in model.users
        """
        mock_os.chmod.side_effect = Exception('fail')
        f = '/etc/sudoers.d/user1_conf'
        mock_os.path.isfile.return_value = True
        open_mock = mock.mock_open(read_data='1')
        with mock.patch('plugins.ginger.model.users.open',
                        open_mock, create=True):
            users = UsersModel()
            self.assertRaises(OperationFailed,
                              users._add_user_to_sudoers, 'user1')
            mock_os.path.isfile.assert_called_once_with(f)
            mock_os.unlink.assert_called_once_with(f)
            mock_os.chmod.assert_called_once_with(f, 0440)

    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_addto_sudoers_success(self, mock_log, mock_os):
        """
        unittest to validate _add_user_to_sudoers() method
        with exception in file creation
        mock_log: mock of wok_log imported in model.users
        mock_os: mock of os imported in model.users
        """
        f = '/etc/sudoers.d/user1_conf'
        open_mock = mock.mock_open(read_data='1')
        with mock.patch('plugins.ginger.model.users.open',
                        open_mock, create=True):
            users = UsersModel()
            users._add_user_to_sudoers('user1')
            mock_os.chmod.assert_called_once_with(f, 0440)


class UserModelUnitTests(unittest.TestCase):
    """
    Unit tests for UserModel()
    """
    @mock.patch('plugins.ginger.model.users.delete_group', autospec=True)
    @mock.patch('plugins.ginger.model.users.get_group_obj_by_gid',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_user_obj', autospec=True)
    @mock.patch('plugins.ginger.model.users.delete_user', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_not_found(self, mock_log, mock_delete_user,
                              mock_get_usr_obj, mock_get_grp_by_gid,
                              mock_delete_group):

        """
        unittest to validate delete() method when user is not found
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_delete_user: mock of delete_user() in model.users
        mock_get_usr_obj: mock of get_user_obj() in model.users
        mock_get_grp_by_gid: mock of get_group_obj_by_gid()  in model.users
        mock_delete_group: mock of delete_group() in model.users
        """
        mock_get_usr_obj.return_value = None
        user = UserModel()
        self.assertRaises(OperationFailed, user.delete, 'user1')
        mock_get_usr_obj.assert_called_once_with('user1')
        self.assertFalse(mock_delete_user.called,
                         msg='Unexpected call to mock_delete_user')
        self.assertFalse(mock_get_grp_by_gid.called,
                         msg='Unexpected call to mock_get_grp_by_gid')
        self.assertFalse(mock_delete_group.called,
                         msg='Unexpected call to mock_delete_group')

    @mock.patch('plugins.ginger.model.users.delete_group', autospec=True)
    @mock.patch('plugins.ginger.model.users.get_group_obj_by_gid',
                autospec=True)
    @mock.patch('plugins.ginger.model.users.get_user_obj', autospec=True)
    @mock.patch('plugins.ginger.model.users.delete_user', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_delete_success(self, mock_log, mock_delete_user,
                            mock_get_usr_obj, mock_get_grp_by_gid,
                            mock_delete_group):

        """
        unittest to validate delete() method success scenario
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_delete_user: mock of delete_user() in model.users
        mock_get_usr_obj: mock of get_user_obj() in model.users
        mock_get_grp_by_gid: mock of get_group_obj_by_gid()  in model.users
        mock_delete_group: mock of delete_group() in model.users
        """
        user = UserModel()
        user.delete('user1')
        mock_get_usr_obj.assert_called_once_with('user1')
        mock_delete_user.assert_called_once_with('user1')
        self.assertTrue(mock_get_grp_by_gid.called,
                        msg='Expected call to mock_get_grp_by_gid.Not Called')

    @mock.patch('plugins.ginger.model.users.get_users_info', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_lookup_not_found(self, mock_log, mock_get_users_info):

        """
        unittest to validate lookup() method for user not found
        mock_log: mock of wok_log imported in model.users
        mock_get_users_info: mock of get_users_info in model.users
        """
        user = UserModel()
        mock_get_users_info.return_value = []
        self.assertRaises(NotFoundError, user.lookup, 'user1')
        mock_get_users_info.assert_called_once_with(['user1'])

    @mock.patch('plugins.ginger.model.users.get_users_info', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_lookup_exception(self, mock_log, mock_get_users_info):

        """
        unittest to validate lookup() method when get_users_info()
        raises exception
        mock_log: mock of wok_log imported in model.users
        mock_get_users_info: mock of get_users_info in model.users
        """
        user = UserModel()
        mock_get_users_info.side_effect = Exception('fail')
        self.assertRaises(NotFoundError, user.lookup, 'user1')
        mock_get_users_info.assert_called_once_with(['user1'])


class GetUserProfileUnitTests(unittest.TestCase):
    """
    Unit tests for get_user_profile()
    """
    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_user_profile_inv_sudoers(self, mock_log, mock_libuser, mock_os,
                                      mock_get_sudoers):

        """
        unittest to validate get_user_profile() method with invalid i/p
        i.e, by passing sudoers as string instead of list
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        self.assertRaises(InvalidParameter, get_user_profile, 'user1',
                          'fake_sudoers')
        mock_log.error.assert_called_once_with(
            'Sudoers is not of type list. Sudoers: %s' % 'fake_sudoers')
        self.assertFalse(mock_adm.enumerateGroupsByUser.called,
                         msg='Unexpected call to '
                             'mock_adm.enumerateGroupsByUser')
        self.assertFalse(mock_os.path.isfile.called,
                         msg='Unexpected call to mock_os.path.isfile')
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_user_profile_inv_user(self, mock_log, mock_libuser, mock_os,
                                   mock_get_sudoers):

        """
        unittest to validate get_user_profile() method with
        invalid i/p for user i.e., passing empty string or integer
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        self.assertRaises(InvalidParameter, get_user_profile, 235)
        mock_log.error.assert_called_once_with(
            'username is not non-empty string. name: %s' % 235)
        self.assertFalse(mock_adm.enumerateGroupsByUser.called,
                         msg='Unexpected call to '
                             'mock_adm.enumerateGroupsByUser')
        self.assertFalse(mock_os.path.isfile.called,
                         msg='Unexpected call to mock_os.path.isfile')
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_user_profile_admin_byfile(self, mock_log, mock_libuser, mock_os,
                                       mock_get_sudoers):

        """
        unittest to validate get_user_profile() for user with conf file
        in /etc/sudoers.d/ directory
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_os.path.isfile.return_value = True
        f = '/etc/sudoers.d/user1_conf'
        profile = get_user_profile('user1')
        self.assertEqual('admin', profile)
        self.assertFalse(mock_adm.enumerateGroupsByUser.called,
                         msg='Unexpected call to '
                             'mock_adm.enumerateGroupsByUser')
        mock_os.path.isfile.assert_called_once_with(f)
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_user_profile_admin_wheel(self, mock_log, mock_libuser, mock_os,
                                      mock_get_sudoers):

        """
        unittest to validate get_user_profile() for user is wheel group
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_os.path.isfile.return_value = False
        mock_adm.enumerateGroupsByUser.return_value = ['user1', 'wheel']
        f = '/etc/sudoers.d/user1_conf'
        profile = get_user_profile('user1')
        self.assertEqual('admin', profile)
        mock_adm.enumerateGroupsByUser.assert_called_once_with('user1')
        mock_os.path.isfile.assert_called_once_with(f)
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_profile_user_in_sudoers_file(self, mock_log, mock_libuser,
                                          mock_os, mock_get_sudoers):

        """
        unittest to validate get_user_profile() for user in /etc/sudoers file
        Note: sudoers is not passed to get_user_profile() so it
              should call get_sudoers() method
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_os.path.isfile.return_value = False
        mock_adm.enumerateGroupsByUser.return_value = ['g1', 'g2']
        mock_get_sudoers.return_value = ['user1', 'user2']
        f = '/etc/sudoers.d/user1_conf'
        profile = get_user_profile('user1')
        self.assertEqual('admin', profile)
        mock_adm.enumerateGroupsByUser.assert_called_once_with('user1')
        mock_os.path.isfile.assert_called_once_with(f)
        mock_get_sudoers.assert_called_once_with()

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_profile_grp_in_sudoers_file(self, mock_log, mock_libuser,
                                         mock_os, mock_get_sudoers):

        """
        unittest to validate get_user_profile() for one of the
        user groups is in /etc/sudoers file.
        Note: sudoers list is passed to get_user_profile() so it shouldn't
              call get_sudoers() method
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_os.path.isfile.return_value = False
        mock_adm.enumerateGroupsByUser.return_value = ['g1', 'g2']
        f = '/etc/sudoers.d/user1_conf'
        profile = get_user_profile('user1', ['%g1'])
        self.assertEqual('admin', profile)
        mock_adm.enumerateGroupsByUser.assert_called_once_with('user1')
        mock_os.path.isfile.assert_called_once_with(f)
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_profile_kvm_grp(self, mock_log, mock_libuser,
                             mock_os, mock_get_sudoers):

        """
        unittest to validate get_user_profile() for user in kvm group
        Note: sudoers list is passed to get_user_profile() so it shouldn't
              call get_sudoers() method
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_os.path.isfile.return_value = False
        mock_adm.enumerateGroupsByUser.return_value = ['g1', 'kvm']
        f = '/etc/sudoers.d/user1_conf'
        profile = get_user_profile('user1', [])
        self.assertEqual('virtuser', profile)
        mock_adm.enumerateGroupsByUser.assert_called_once_with('user1')
        mock_os.path.isfile.assert_called_once_with(f)
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')

    @mock.patch('plugins.ginger.model.users.get_sudoers', autospec=True)
    @mock.patch('plugins.ginger.model.users.os', autospec=True)
    @mock.patch('plugins.ginger.model.users.libuser', autospec=True)
    @mock.patch('plugins.ginger.model.users.wok_log', autospec=True)
    def test_profile_regular_user(self, mock_log, mock_libuser,
                                  mock_os, mock_get_sudoers):

        """
        unittest to validate get_user_profile() for user in kvm group
        Note: sudoers list is passed to get_user_profile() so it shouldn't
              call get_sudoers() method
        mock_log: mock of wok_log imported in model.users
        mock_libuser: mock of libuser imported in model.users
        mock_os: mock of os imported in model.users
        mock_get_sudoers: mock of get_sudoers() in model.users
        """
        mock_adm = mock_libuser.admin()
        mock_os.path.isfile.return_value = False
        mock_adm.enumerateGroupsByUser.return_value = ['g1', 'g2']
        f = '/etc/sudoers.d/user1_conf'
        profile = get_user_profile('user1', [])
        self.assertEqual('regularuser', profile)
        mock_adm.enumerateGroupsByUser.assert_called_once_with('user1')
        mock_os.path.isfile.assert_called_once_with(f)
        self.assertFalse(mock_get_sudoers.called,
                         msg='Unexpected call to mock_get_sudoers')
