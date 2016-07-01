#
# Project Ginger
#
# Copyright IBM Corp, 2014-2016
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

from control import Backup, Capabilities, Config, DASDdevs, DASDPartitions
from control import Firmware, FirmwareProgress, FileSystems, LogicalVolumes
from control import Network, OVSBridges, Partitions, PhysicalVolumes
from control import PowerProfiles, SanAdapters, Sensors, Sep, Services
from control import StgServers, StorageDevs, Swaps, SysModules, Users
from control import VolumeGroups
from i18n import messages

from wok import config
from wok.config import PluginPaths
from wok.control.tasks import Tasks
from wok.root import WokRoot
from model import GingerModel


class Ginger(WokRoot):
    def __init__(self, wok_options=None):
        object_store = config.get_object_store()
        objstore_dir = os.path.dirname(os.path.abspath(object_store))
        if not os.path.isdir(objstore_dir):
            os.makedirs(objstore_dir)

        self.model = GingerModel()
        super(Ginger, self).__init__(self.model)

        self.api_schema = json.load(open(os.path.join(os.path.dirname(
                                    os.path.abspath(__file__)), 'API.json')))
        self.domain = "ginger"
        self.messages = messages
        self.paths = PluginPaths('ginger')

        self.backup = Backup(self.model)
        self.capabilities = Capabilities(self.model)
        self.config = Config(self.model)
        self.dasddevs = DASDdevs(self.model)
        self.dasdpartitions = DASDPartitions(self.model)
        self.filesystems = FileSystems(self.model)
        self.firmware = Firmware(self.model)
        self.fwprogress = FirmwareProgress(self.model)
        self.ibm_sep = Sep(self.model)
        self.lvs = LogicalVolumes(self.model)
        self.network = Network(self.model)
        self.ovsbridges = OVSBridges(self.model)
        self.partitions = Partitions(self.model)
        self.powerprofiles = PowerProfiles(self.model)
        self.pvs = PhysicalVolumes(self.model)
        self.san_adapters = SanAdapters(self.model)
        self.sensors = Sensors(self.model)
        self.services = Services(self.model)
        self.stgdevs = StorageDevs(self.model)
        self.stgserver = StgServers(self.model)
        self.swaps = Swaps(self.model)
        self.sysmodules = SysModules(self.model)
        self.tasks = Tasks(self.model)
        self.users = Users(self.model)
        self.vgs = VolumeGroups(self.model)

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
