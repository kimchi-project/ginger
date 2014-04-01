#
# Project Kimchi
#
# Copyright IBM, Corp. 2014
#
# Authors:
#  Christy Perez <christy@linux.vnet.ibm.com>
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


import os

from kimchi.exception import OperationFailed
from kimchi.utils import kimchi_log
from kimchi.utils import run_command


class FirmwareModel():
    """
    The model class for viewing and updating the Power firmware level
    """

    def lookup(self, params=None):
        def parse_fw_levels():
            FW_INFO_DIR = '/proc/device-tree/ibm,opal/firmware'
            fw_info = []
            for name in ('ml-version', 'mi-version'):
                with open(os.path.join(FW_INFO_DIR, name)) as f:
                            fw_info.append(f.readline().split()[1])
            return fw_info

        level = 'Unknown'
        try:
            levels = parse_fw_levels()
            level = '%s (%s)' % (levels[0], levels[1])
        except IOError as e:
            kimchi_log.error('Error parsing firmware level: %s' % e.message)
        return {'level': level}

    def update(self, name, params):

        # FIXME: When model is restructured, use
        # vms_get_list_by_state('running') instead
        def detect_live_vm():
            with open('/proc/modules') as f:
                for line in f:
                    column = line.split()
                    if column[0].startswith('kvm_') and column[2] != '0':
                        return True
            return False

        fw_path = params['path']
        if detect_live_vm():
            kimchi_log.error('Cannot update system fw while running VMs.')
            raise OperationFailed('GINFW0001E')

        # First unpack the rpm to get the fw img file
        # FIXME: When there's a .deb package available, add support for that
        command = ['rpm', '-U', '--force', '--ignoreos', fw_path]
        output, error, rc = run_command(command)
        if rc:
            # rpm returns num failed pkgs on failure or neg for unknown
            raise OperationFailed('GINFW0002E', {'rc': rc, 'err': error})

        # The image file should now be in /tmp/fwupdate/
        # and match the rpm name.
        image_file, ext = os.path.splitext(os.path.basename(fw_path))
        if image_file is None:
            kimchi_log.error('FW update failed: '
                             'No image file found in the package file.')
            raise OperationFailed('GINFW0003E')
        command = ['update_flash', '-f',
                   os.path.join('/tmp/fwupdate', '%s.img' % image_file)]
        kimchi_log.info('FW update: System will reboot to flash the firmware.')
        output, error, rc = run_command(command)
        if rc :
            raise OperationFailed('GINFW0004E', {'rc': rc})
