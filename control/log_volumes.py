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

from wok.control.base import AsyncCollection, Resource
from wok.control.utils import UrlSubNode


LOGICALVOLUMES_REQUESTS = {
    'POST': {'default': "GINLV0001L"},
}

LOGICALVOLUME_REQUESTS = {
    'DELETE': {'default': "GINLV0002L"},
}


@UrlSubNode('lvs', True)
class LogicalVolumes(AsyncCollection):
    """
    Collection representing the logical volumes on the system
    """
    def __init__(self, model):
        super(LogicalVolumes, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = LogicalVolume

        # set user log messages and make sure all parameters are present
        self.log_map = LOGICALVOLUMES_REQUESTS
        self.log_args.update({'vg_name': ''})


class LogicalVolume(Resource):
    """
    Resource representing a single logical volume
    """
    def __init__(self, model, ident):
        super(LogicalVolume, self).__init__(model, ident)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/lvs/%s"
        self.log_map = LOGICALVOLUME_REQUESTS

    @property
    def data(self):
        out_ret = {}
        out_ret['lvPath'] = self.info['LV Path']
        out_ret['lvName'] = self.info['LV Name']
        out_ret['vgName'] = self.info['VG Name']
        out_ret['lvUUID'] = self.info['LV UUID']
        out_ret['lvWriteAccess'] = self.info['LV Write Access']
        out_ret['lvCreationhost, time'] = self.info['LV Creation host, time']
        out_ret['lvStatus'] = self.info['LV Status']
        out_ret['#open'] = self.info['# open']
        out_ret['lvSize'] = self.info['LV Size']
        out_ret['currentLE'] = self.info['Current LE']
        out_ret['segments'] = self.info['Segments ']
        out_ret['allocation'] = self.info['Allocation ']
        out_ret['readAheadSectors'] = self.info['Read ahead sectors']
        out_ret['-currentlySetTo'] = self.info['- currently set to']
        out_ret['blockDevice'] = self.info['Block device']
        if 'LV snapshot status' in self.info.keys():
            out_ret['lvSnapshotStatus'] = self.info['LV snapshot status']
        if 'COW-table LE' in self.info.keys():
            out_ret['COW-tableLE'] = self.info['COW-table LE']
            out_ret['COW-tableSize'] = self.info['COW-table size']
            out_ret['snapshotChunkSize'] = self.info['Snapshot chunk size']

        return out_ret
