#
# Project Ginger
#
# Copyright IBM Corp, 2016-2017
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

import tests.utils as utils

from wok.exception import NotFoundError
from wok.plugins.ginger.model.audisp_plugins import PluginsModel, write_to_conf
from wok.plugins.ginger.model.audisp_plugins import PluginModel


class Audisp_PluginsTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.audisp_plugins.'
                'PluginsModel.get_list')
    def test_get_list_success(self, mock_get):
        """
        Unittest to get list of plugins.
        :param self:
        :return:
        """
        plugin = 'dummy1'
        audisp_plugins = PluginsModel()
        mock_get.return_value = plugin
        out = audisp_plugins.get_list()
        self.assertIn(plugin, out)

    @unittest.skipUnless(utils.running_as_root(), 'Must be run as root')
    def test_get_list_invalid_plugin(self):
        """
         Unittest to test invalid plugin in list of plugins.
        :param self:
        :return:
        """
        plugin = 'abcd'
        audisp_plugins = PluginsModel()
        out = audisp_plugins.get_list()
        self.assertNotIn(plugin, out)

    @mock.patch('wok.plugins.ginger.model.audisp_plugins.'
                'PluginModel.get_plugin_info')
    def test_get_plugin_info(self, mock_info):
        """
        Unittest to get a plugin info.
        :return:
        """
        exp_out = {'details': {'direction': 'out',
                               'format': 'string',
                               'args': '0640 /var/run/audispd_events',
                               'active': 'no',
                               'path': 'builtin_af_unix',
                               'type': 'builtin'},
                   'name': u'dummy1'}
        name = "dummy1"
        open_mock = mock.mock_open()
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            audisp_plugin = PluginModel()
            mock_info.return_value = exp_out
            out = audisp_plugin.get_plugin_info(name)
            self.assertEquals(name, out['name'])

    @mock.patch('os.path.isfile')
    def test_get_plugin_info_invalid(self, mock_isfile):
        """
        Unittest to get a plugin info.
        :return:
        """
        name = "dummy1"
        audisp_plugin = PluginModel()
        mock_isfile.return_value = False
        self.assertRaises(NotFoundError, audisp_plugin.get_plugin_info, name)

    @mock.patch('wok.plugins.ginger.model.utils.'
                'write_to_conf')
    def test_write_to_conf(self, mock_write):
        """
        Unittest to write the data to the conf file.
        :return:
        """
        data = 'active = yes\n' \
               'direction = out\n' \
               'path = /usr/sbin/sedispatch\n' \
               'type = always\n' \
               'format = string\n'
        name = 'dummy1'
        plugins_dir = '/etc/audisp/plugins.d'
        path_to_plugin = plugins_dir + "/" + name + ".conf"
        key = "active"
        value = "no"
        open_mock = mock.mock_open(read_data=data)
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            # audisp_plugin = PluginModel()
            mock_write.return_value = {}
            write_to_conf(key, value, path_to_plugin)

    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.'
                'audisp_plugins.write_to_conf')
    @mock.patch('wok.plugins.ginger.model.'
                'audisp_plugins.del_lines_of_attribute')
    def test_update(self, mock_del, mock_write, mock_os):
        """
        Unittest to update the plugin info.
        :param mock_del:
        :param mock_write:
        :return:
        """
        params = {"active": "yes"}
        name = 'af_uncvc'
        mock_os.return_value = True
        mock_del.return_value = {}
        mock_write.return_value = {}
        audisp_plugin = PluginModel()
        audisp_plugin.update(name, params)
