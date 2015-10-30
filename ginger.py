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

import json
import os

from controls import Backup, Capabilities, Firmware, Network, PowerProfiles
from controls import FileSystems, SanAdapters, Sensors, Sep, Users
from i18n import messages
from wok.config import PluginPaths
from wok.root import WokRoot
from models import GingerModel


class Ginger(WokRoot):
    def __init__(self, wok_options=None):
        self.model = GingerModel()
        super(Ginger, self).__init__(self.model)
        self.backup = Backup(self.model)
        self.capabilities = Capabilities(self.model)
        self.filesystems = FileSystems(self.model)
        self.firmware = Firmware(self.model)
        self.powerprofiles = PowerProfiles(self.model)
        self.sensors = Sensors(self.model)
        self.users = Users(self.model)
        self.network = Network(self.model)
        self.api_schema = json.load(open(os.path.join(os.path.dirname(
                                    os.path.abspath(__file__)), 'API.json')))
        self.paths = PluginPaths('ginger')
        self.domain = "ginger"
        self.messages = messages
        self.san_adapters = SanAdapters(self.model)
        self.ibm_sep = Sep(self.model)
