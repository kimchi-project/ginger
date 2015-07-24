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

from models.users import UserModel, UsersModel

from kimchi.exception import OperationFailed
from kimchi.rollbackcontext import RollbackContext


class UserModelTests(unittest.TestCase):

    def test_get_users_list(self):
        model = UsersModel()
        users = model.get_list()
        self.assertGreaterEqual(len(users), 0)

    def test_create_user(self):
        users_model = UsersModel()
        user_model = UserModel()

        user = 'unit_test_fake_user'
        passwd = 'fakepass'
        group = 'unit_test_fake_group'
        profile = 'unit_test_fake_profile'

        common_users = users_model.get_list()
        params = {'name': user, 'password': passwd,
                  'group': group, 'profile': profile}
        with RollbackContext() as rollback:

            users_model.create(params)
            rollback.prependDefer(user_model.delete, user)

            new_users = users_model.get_list()
            self.assertEqual(len(new_users), len(common_users) + 1)

            enc_passwd = spwd.getspnam(user)[1]
            invalid_passwd = [None, "NP", "!", "!!",  "", "LK", "*"]
            self.assertNotIn(enc_passwd, invalid_passwd)

            self.assertEqual(crypt.crypt(passwd, enc_passwd), enc_passwd)

    def test_creating_existing_user_fails(self):
        users_model = UsersModel()
        user_model = UserModel()

        user = 'unit_test_fake_user'
        passwd = 'fakepass'
        group = 'unit_test_fake_group'
        profile = 'unit_test_fake_profile'

        params = {'name': user, 'password': passwd,
                  'group': group, 'profile': profile}

        with RollbackContext() as rollback:
            users_model.create(params)
            rollback.prependDefer(user_model.delete, user)

            with self.assertRaises(OperationFailed):
                users_model.create(params)
