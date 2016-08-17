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

import inspect

from backup import ArchiveModel, ArchivesModel, BackupModel
from capabilities import CapabilitiesModel
from config import ConfigModel
from cfginterfaces import CfginterfaceModel, CfginterfacesModel
from dasddevs import DASDdevsModel, DASDdevModel
from dasdpartitions import DASDPartitionsModel, DASDPartitionModel
from diskparts import PartitionsModel, PartitionModel
from filesystem import FileSystemsModel, FileSystemModel
from firmware import FirmwareModel
from ibm_sep import SepModel, SubscribersModel, SubscriptionModel
from interfaces import InterfacesModel, InterfaceModel
from iscsitargets import DiscoveredISCSIQNsModel, DiscoveredISCSIQNModel
from iscsitargets import ISCSITargetsModel, ISCSIAuth
from log_volume import LogicalVolumesModel, LogicalVolumeModel
from network import NetworkModel
from nfsshares import NFSSharesModel
from ovsbridges import OVSBridgesModel, OVSBridgeModel
from powermanagement import PowerProfilesModel, PowerProfileModel
from physical_vol import PhysicalVolumesModel, PhysicalVolumeModel
from rules import RulesModel, RuleModel
from sanadapters import SanAdapterModel, SanAdaptersModel
from sensors import SensorsModel
from services import ServicesModel, ServiceModel
from stgserver import StgServersModel, StgServerModel
from storage_devs import StorageDevsModel
from swaps import SwapsModel, SwapModel
from sysmodules import SysModulesModel, SysModuleModel
from users import UsersModel, UserModel
from vol_group import VolumeGroupsModel, VolumeGroupModel

from wok import config as wok_config
from wok.basemodel import BaseModel
from wok.objectstore import ObjectStore
from wok.utils import import_module, upgrade_objectstore_schema


class GingerModel(BaseModel):

    def __init__(self):
        def get_instances(module_name):
            instances = []
            module = import_module(module_name)
            members = inspect.getmembers(module, inspect.isclass)
            for cls_name, instance in members:
                if inspect.getmodule(instance) == module and \
                   cls_name.endswith('Model'):
                    instances.append(instance)

            return instances

        objstore_loc = wok_config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        # Some paths or URI's present in the objectstore have changed after
        # Wok 2.0.0 release. Check here if a schema upgrade is necessary.
        upgrade_objectstore_schema(objstore_loc, 'version')

        sub_models = []
        firmware = FirmwareModel(objstore=self._objstore)
        powerprofiles = PowerProfilesModel()
        powerprofile = PowerProfileModel()
        users = UsersModel()
        user = UserModel()
        interfaces = InterfacesModel()
        interface = InterfaceModel(objstore=self._objstore)
        cfginterface = CfginterfaceModel()
        cfginterfaces = CfginterfacesModel()
        dasddevs = DASDdevsModel()
        dasddev = DASDdevModel(objstore=self._objstore)
        dasdpartitions = DASDPartitionsModel()
        dasdpartition = DASDPartitionModel()
        discoveredISCSIQNs = DiscoveredISCSIQNsModel()
        discoveredISCSIQN = DiscoveredISCSIQNModel()
        network = NetworkModel()
        filesystems = FileSystemsModel()
        filesystem = FileSystemModel()
        iscsitargets = ISCSITargetsModel()
        iscsiAuth = ISCSIAuth()
        log_volumes = LogicalVolumesModel(objstore=self._objstore)
        log_volume = LogicalVolumeModel(objstore=self._objstore)
        ovsbridges = OVSBridgesModel()
        ovsbridge = OVSBridgeModel()
        partitions = PartitionsModel()
        partition = PartitionModel(objstore=self._objstore)
        archives = ArchivesModel(objstore=self._objstore)
        archive = ArchiveModel(objstore=self._objstore)
        backup = BackupModel(objstore=self._objstore, archives_model=archives,
                             archive_model=archive)
        san_adapters = SanAdaptersModel()
        san_adapter = SanAdapterModel()
        swaps = SwapsModel(objstore=self._objstore)
        swap = SwapModel()
        sysmodules = SysModulesModel()
        sysmodule = SysModuleModel()
        sensors = SensorsModel()
        stgdevs = StorageDevsModel()
        ibm_sep = SepModel()
        subscription = SubscriptionModel()
        subscriber = SubscribersModel()
        physical_vols = PhysicalVolumesModel(objstore=self._objstore)
        physical_vol = PhysicalVolumeModel(objstore=self._objstore)
        vol_groups = VolumeGroupsModel(objstore=self._objstore)
        vol_group = VolumeGroupModel(objstore=self._objstore)
        services = ServicesModel()
        service = ServiceModel()
        stgservers = StgServersModel()
        stgserver = StgServerModel()
        nfsshares = NFSSharesModel()
        rules = RulesModel()
        rule = RuleModel()

        capabilities = CapabilitiesModel()
        config = ConfigModel()

        sub_models = [
            backup, archives, archive,
            firmware,
            interfaces, interface,
            cfginterface, cfginterfaces,
            dasddevs, dasddev,
            dasdpartitions, dasdpartition,
            discoveredISCSIQN, discoveredISCSIQNs,
            network, nfsshares, iscsitargets, iscsiAuth,
            filesystems, filesystem,
            log_volumes, log_volume,
            partitions, partition,
            physical_vols, physical_vol,
            powerprofiles, powerprofile,
            users, user,
            san_adapters, san_adapter,
            sensors, stgdevs,
            swaps, swap,
            sysmodules, sysmodule,
            vol_groups, vol_group,
            ibm_sep, subscription, subscriber,
            capabilities, config, ovsbridge, ovsbridges,
            services, service, stgservers, stgserver,
            rules, rule]

        # Import task model from Wok
        kargs = {'objstore': self._objstore}
        task_model_instances = []
        instances = get_instances('wok.model.tasks')
        for instance in instances:
            task_model_instances.append(instance(**kargs))

        sub_models += task_model_instances

        super(GingerModel, self).__init__(sub_models)
