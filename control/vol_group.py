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

from wok.control.base import AsyncCollection, Resource
from wok.control.utils import UrlSubNode


VOLUMEGROUPS_REQUESTS = {
    'POST': {'default': "GINVG0001L"},
}

VOLUMEGROUP_REQUESTS = {
    'DELETE': {'default': "GINVG0002L"},
    'POST': {
        'extend': "GINVG0003L",
        'reduce': "GINVG0004L",
    },
}


@UrlSubNode('vgs', True)
class VolumeGroups(AsyncCollection):
    """
    Collection representing the Volume groups on the system
    """
    def __init__(self, model):
        super(VolumeGroups, self).__init__(model)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = VolumeGroup

        # set user log messages and make sure all parameters are present
        self.log_map = VOLUMEGROUPS_REQUESTS
        self.log_args.update({'vg_name': ''})


class VolumeGroup(Resource):
    """
    Resource representing a single Volume group
    """
    def __init__(self, model, ident):
        super(VolumeGroup, self).__init__(model, ident)
        self.role_key = 'host'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/vgs/%s"
        self.log_map = VOLUMEGROUP_REQUESTS
        self.extend = self.generate_action_handler('extend', ['pv_paths'])
        self.reduce = self.generate_action_handler('reduce', ['pv_paths'])

    @property
    def data(self):
        return {'vgName': self.info['VG Name'],
                'systemID': self.info['System ID']
                if self.info['System ID'] else "None",
                'format': self.info['Format'],
                'metadataAreas': self.info['Metadata Areas'],
                'metadataSequenceNo': self.info['Metadata Sequence No'],
                'permission': self.info['Permission'],
                'vgStatus': self.info['VG Status'],
                'maxLV': self.info['Max LV'],
                'curLV': self.info['Cur LV'],
                'maxPV': self.info['Max PV'],
                'curPV': self.info['Cur PV'],
                'vgSize': self.info['VG Size'],
                'peSize': self.info['PE Size'],
                'totalPE': self.info['Total PE'],
                'allocPE': self.info['Alloc PE'],
                'allocPESize': self.info['Alloc PE Size'],
                'freePE': self.info['Free PE'],
                'freePESize': self.info['Free PE Size'],
                'pvNames': self.info['PV Names'],
                'vgUUID': self.info['VG UUID']}
