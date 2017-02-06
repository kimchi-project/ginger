#
# Project Ginger
#
# Copyright IBM Corp, 2014-2017
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

import json
import os

from i18n import messages
from model import GingerModel
from wok import config
from wok.config import PluginPaths
from wok.plugins.ginger.control import sub_nodes
from wok.root import WokRoot


class Ginger(WokRoot):
    def __init__(self, wok_options=None):
        object_store = config.get_object_store()
        objstore_dir = os.path.dirname(os.path.abspath(object_store))
        if not os.path.isdir(objstore_dir):
            os.makedirs(objstore_dir)

        self.model = GingerModel()
        super(Ginger, self).__init__(self.model)

        for ident, node in sub_nodes.items():
            setattr(self, ident, node(self.model))

        self.api_schema = json.load(open(os.path.join(os.path.dirname(
                                    os.path.abspath(__file__)), 'API.json')))
        self.domain = "ginger"
        self.depends = ['gingerbase']
        self.messages = messages
        self.paths = PluginPaths('ginger')

    def get_custom_conf(self):
        custom_config = {
            '/help': {
                'tools.staticdir.on': True,
                'tools.nocache.on': True,
                'tools.staticdir.dir':  os.path.join(self.paths.ui_dir,
                                                     'pages/help')
            }
        }

        for dirname in ('css', 'js', 'images'):
            custom_config['/' + dirname] = {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': os.path.join(self.paths.ui_dir,
                                                    dirname),
                'tools.wokauth.on': False,
                'tools.nocache.on': False}

        return custom_config
