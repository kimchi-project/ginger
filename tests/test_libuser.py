#
# Project Ginger
#
# Copyright IBM, Corp. 2015
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

import crypt
import spwd
import unittest

import models.users as users

from wok.exception import OperationFailed
from wok.rollbackcontext import RollbackContext


class UserAdmTests(unittest.TestCase):

    def test_get_users_list(self):
        common_users = users.get_users()
        self.assertGreaterEqual(len(common_users), 0)

        all_users = users.get_users(exclude_system_users=False)
        self.assertGreaterEqual(len(all_users), 1)

        self.assertGreaterEqual(all_users, common_users)

    def test_create_user(self):
        user = 'unit_test_fake_user'
        passwd = 'fakepass'

        common_users = users.get_users()
        with RollbackContext() as rollback:
            users.create_user(user, passwd)
            rollback.prependDefer(users.delete_user, user)

            new_users = users.get_users()
            self.assertEqual(len(new_users), len(common_users) + 1)

            enc_passwd = spwd.getspnam(user)[1]
            invalid_passwd = [None, "NP", "!", "!!",  "", "LK", "*"]
            self.assertNotIn(enc_passwd, invalid_passwd)

            self.assertEqual(crypt.crypt(passwd, enc_passwd), enc_passwd)

    def test_create_existing_user_fails(self):
        user = 'unit_test_fake_user'
        passwd = 'fakepass'

        with RollbackContext() as rollback:
            users.create_user(user, passwd)
            rollback.prependDefer(users.delete_user, user)

            with self.assertRaises(OperationFailed):
                users.create_user(user, passwd)

    def test_list_existing_groups(self):
        groups = users.get_groups()
        self.assertGreaterEqual(len(groups), 1)

    def test_create_group(self):
        groupname = 'unit_test_fake_group'
        groups = users.get_groups()

        with RollbackContext() as rollback:
            users.create_group(groupname)
            rollback.prependDefer(users.delete_group, groupname)

            new_groups = users.get_groups()
            self.assertEqual(len(new_groups), len(groups) + 1)

    def test_add_user_to_primary_group(self):
        user = 'unit_test_fake_user'
        passwd = 'fakepass'
        group = 'unit_test_fake_group'

        with RollbackContext() as rollback:
            users.create_group(group)
            rollback.prependDefer(users.delete_group, group)

            users.create_user(user, passwd)
            rollback.prependDefer(users.delete_user, user)

            users.add_user_to_primary_group(user, group)

            users_group = users.get_users_from_group(group)
            self.assertEqual(len(users_group), 1)
            self.assertIn(user, users_group)
