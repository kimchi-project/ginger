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

import inspect

from backup import ArchiveModel, ArchivesModel, BackupModel
from capabilities import CapabilitiesModel
from cfginterfaces import CfginterfaceModel, CfginterfacesModel
from dasddevs import DASDdevsModel, DASDdevModel
from dasdpartitions import DASDPartitionsModel, DASDPartitionModel
from diskparts import PartitionsModel, PartitionModel
from filesystem import FileSystemsModel, FileSystemModel
from firmware import FirmwareModel
from ibm_sep import SepModel, SubscribersModel, SubscriptionModel
from interfaces import InterfacesModel, InterfaceModel
from log_volume import LogicalVolumesModel, LogicalVolumeModel
from network import NetworkModel
from powermanagement import PowerProfilesModel, PowerProfileModel
from physical_vol import PhysicalVolumesModel, PhysicalVolumeModel
from sanadapters import SanAdapterModel, SanAdaptersModel
from sensors import SensorsModel
from users import UsersModel, UserModel
from swaps import SwapsModel, SwapModel
from vol_group import VolumeGroupsModel, VolumeGroupModel

from wok import config
from wok.basemodel import BaseModel
from wok.objectstore import ObjectStore
from wok.utils import import_module


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

        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

        sub_models = []
        firmware = FirmwareModel()
        powerprofiles = PowerProfilesModel()
        powerprofile = PowerProfileModel()
        users = UsersModel()
        user = UserModel()
        interfaces = InterfacesModel()
        interface = InterfaceModel()
        cfginterface = CfginterfaceModel()
        cfginterfaces = CfginterfacesModel()
        dasddevs = DASDdevsModel()
        dasddev = DASDdevModel(objstore=self._objstore)
        dasdpartitions = DASDPartitionsModel()
        dasdpartition = DASDPartitionModel()
        network = NetworkModel()
        filesystems = FileSystemsModel()
        filesystem = FileSystemModel()
        log_volumes = LogicalVolumesModel(objstore=self._objstore)
        log_volume = LogicalVolumeModel(objstore=self._objstore)
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
        sensors = SensorsModel()
        ibm_sep = SepModel()
        subscription = SubscriptionModel()
        subscriber = SubscribersModel()
        physical_vols = PhysicalVolumesModel(objstore=self._objstore)
        physical_vol = PhysicalVolumeModel(objstore=self._objstore)
        vol_groups = VolumeGroupsModel(objstore=self._objstore)
        vol_group = VolumeGroupModel(objstore=self._objstore)

        features = [firmware, swaps, backup, network, powerprofiles,
                    san_adapters, sensors, ibm_sep, users, filesystems,
                    dasddevs, dasdpartitions, partitions, physical_vols,
                    vol_groups, log_volumes]
        capabilities = CapabilitiesModel(features)

        sub_models = [
            backup, archives, archive,
            firmware,
            interfaces, interface,
            cfginterface, cfginterfaces,
            dasddevs, dasddev,
            dasdpartitions, dasdpartition,
            network,
            filesystems, filesystem,
            log_volumes, log_volume,
            partitions, partition,
            physical_vols, physical_vol,
            powerprofiles, powerprofile,
            users, user,
            san_adapters, san_adapter,
            sensors,
            swaps, swap,
            vol_groups, vol_group,
            ibm_sep, subscription, subscriber,
            capabilities]

        # Import task model from Wok
        kargs = {'objstore': self._objstore}
        task_model_instances = []
        instances = get_instances('wok.model.tasks')
        for instance in instances:
            task_model_instances.append(instance(**kargs))

        sub_models += task_model_instances

        super(GingerModel, self).__init__(sub_models)
