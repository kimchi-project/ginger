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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

import os
import threading

from utils import del_lines_of_attribute, write_to_conf
from wok.exception import NotFoundError, OperationFailed

audit_configpath = 'etc/audit/'
plugins_dir = '/etc/audisp/plugins.d'

gingerAuditPluginLock = threading.RLock()


class PluginsModel(object):
    """
    Class to perform operation on rules.
    """
    def get_list(self):
        """
        Returns list of plugins.
        :return:
        """
        plugins_list = []
        try:
            dir_contents = os.listdir(plugins_dir)
        except OSError:
            return
        for name in dir_contents:
            plugins_list.append(name.split('.conf')[0])
        return plugins_list

    @staticmethod
    def is_feature_available():
        return os.path.isdir(os.sep + audit_configpath)


class PluginModel(object):
    def __init__(self):
        self._rollback_timer = None

    def lookup(self, name):
        info = self.get_plugin_info(name)
        return info

    def get_plugin_info(self, name):
        audisp_plugin_conf = dict()
        audisp_plugin_conf['details'] = {}
        audisp_plugin_conf['name'] = name
        plugin_with_path = os.path.join(plugins_dir, name + ".conf")
        if not os.path.isfile(plugin_with_path):
            raise NotFoundError("GINAUDISP0006E", {'name': name})
        try:
            with open(plugin_with_path, "r") as plugin_file:
                for each_line in plugin_file:
                    if each_line[:1] not in "#,\n":
                        list = each_line.split('=')
                        audisp_plugin_conf['details'][list[0].strip()] = \
                            list[1].strip()
            return audisp_plugin_conf
        except Exception:
            raise OperationFailed("GINAUDISP0001E", {"name": name})

    def update(self, name, params):
        try:
            gingerAuditPluginLock.acquire()
            path_to_plugin = os.path.join(plugins_dir, name + ".conf")
            if not os.path.isfile(path_to_plugin):
                raise NotFoundError("GINAUDISP0006E", {'name': name})
            for each_key in params:
                del_lines_of_attribute(each_key, path_to_plugin)
                write_to_conf(each_key, params[each_key], path_to_plugin)
        except NotFoundError:
            raise
        except OperationFailed:
            raise
        except Exception:
            raise OperationFailed("GINAUDISP0004E", {"name": name})
        finally:
            gingerAuditPluginLock.release()
