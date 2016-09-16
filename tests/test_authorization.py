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

import unittest
from functools import partial

from tests.utils import get_free_port, request, run_server

from wok.plugins.ginger.model import GingerModel


test_server = None
model = None
host = None
port = None
ssl_port = None


def setUpModule():
    global test_server, model, host, port, ssl_port

    model = GingerModel()
    host = '127.0.0.1'
    port = get_free_port('http')
    ssl_port = get_free_port('https')
    test_server = run_server(host, port, ssl_port, test_mode=True, model=model)


def tearDownModule():
    test_server.stop()


class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.request = partial(request, host, ssl_port)

    def test_nonauth(self):
        # Test APIs that DO NOT require authentication
        resp = self.request('/plugins/ginger/capabilities', '{}', 'GET')
        self.assertEquals(200, resp.status)

        # Test APIs that require authentication
        apis = ['/firmware', '/backup', '/backup/archives',
                '/ibm_sep', '/network', '/network/interfaces',
                '/network/cfginterfaces', '/powerprofiles',
                '/san_adapters', '/sensors', '/users', '/dasddevs',
                '/dasdpartitions', '/partitions', '/filesystems',
                '/lvs', '/pvs', '/stgdevs', '/swaps',
                '/sysmodules', '/vgs']

        for api in apis:
            resp = self.request('/plugins/ginger' + api, '{}', 'GET')
            self.assertEquals(401, resp.status)
