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


PHYSICALVOLUMES_REQUESTS = {
    'POST': {'default': "GINPV0001L"},
}

PHYSICALVOLUME_REQUESTS = {
    'DELETE': {'default': "GINPV0002L"},
}


@UrlSubNode('pvs', True)
class PhysicalVolumes(AsyncCollection):
    """
    Collection representing the Physical volumes of the system
    """
    def __init__(self, model):
        super(PhysicalVolumes, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = PhysicalVolume

        # set user log messages and make sure all parameters are present
        self.log_map = PHYSICALVOLUMES_REQUESTS
        self.log_args.update({'pv_name': ''})


class PhysicalVolume(Resource):
    """
    Resource representing a single Physical volume
    """
    def __init__(self, model, ident):
        super(PhysicalVolume, self).__init__(model, ident)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/pvs/%s"
        self.log_map = PHYSICALVOLUME_REQUESTS

    @property
    def data(self):
        return {
            'PVName': self.info['PV Name'],
            'Allocatable': self.info['Allocatable'],
            'PVUUID': self.info['PV UUID'],
            'TotalPE': self.info['Total PE'],
            'AllocatedPE': self.info['Allocated PE'],
            'PVSize': self.info['PV Size'],
            'PESize': self.info['PE Size'],
            'FreePE': self.info['Free PE'],
            'VGName': self.info['VG Name'] if self.info['VG Name'] else 'None'}
