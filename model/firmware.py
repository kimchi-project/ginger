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


import magic
import os
import platform
import time

from wok.asynctask import AsyncTask
from wok.exception import OperationFailed
from wok.model.notifications import add_notification
from wok.model.tasks import TaskModel
from wok.utils import run_command, wok_log


# FIXME: When model is restructured, use
# vms_get_list_by_state('running') instead
def detect_live_vm():
    with open('/proc/modules') as f:
        for line in f:
            column = line.split()
            if column[0].startswith('kvm_') and column[2] != '0':
                return True
    return False


class FirmwareModel(object):
    """
    The model class for viewing and updating the Power firmware level
    """

    def __init__(self, **kargs):
        self.task = TaskModel(**kargs)
        self.objstore = kargs['objstore']

    def lookup(self, *args):
        output, error, rc = run_command('lsmcode')
        if rc:
            wok_log.error('Unable to retrieve firmware level.')
            return {'level': 'Unknown'}
        # Cut out the chatter from the command output
        # First, need check what type of output was returned due to diffs
        # between some machine version
        if output.split()[5] != 'Product':
            levels = output.split()[5:]
            levels = " ".join(levels)
        else:
            levels = output.split()[13]
        return {'level': levels}

    def upgrade(self, ident, fw_path=None, pow_ok=None):
        if detect_live_vm():
            raise OperationFailed('GINFW0001E')

        # Process argumets provided by user: firmware path and overwrite-perm
        if fw_path is None:
            raise OperationFailed('GINFW0003E')

        ms = magic.open(magic.NONE)
        ms.load()
        if ms.file(fw_path).lower().startswith('rpm'):
            # First unpack the rpm to get the fw img file
            command = ['rpm', '-U', '--force', '--ignoreos', fw_path]
            output, error, rc = run_command(command)
            if rc:
                # rpm returns num failed pkgs on failure or neg for unknown
                raise OperationFailed('GINFW0002E', {'rc': rc, 'err': error})

            # The image file should now be in /tmp/fwupdate/
            # and match the rpm name.
            image_file, ext = os.path.splitext(os.path.basename(fw_path))
            image_file = os.path.join('/tmp/fwupdate', '%s.img' % image_file)
            if not os.path.exists(image_file):
                raise OperationFailed('GINFW0003E')
        else:
            image_file = fw_path
        ms.close()

        command = ['update_flash', '-f', image_file]
        if pow_ok is not None:
            command.insert(1, '-n')

        # update_flash may take some time to restart the system. Inform user.
        wok_log.info('FW update: System will reboot to flash the firmware.')

        cmd_params = {'command': command, 'operation': 'update'}
        taskid = AsyncTask('/plugins/ginger/firmware/upgrade',
                           self._execute_task, cmd_params).id

        return self.task.lookup(taskid)

    def commit(self, ident):
        command = ['update_flash', '-c']
        output, error, rc = run_command(command)
        if rc:
            raise OperationFailed('GINFW0005E', {'rc': rc})

        # update_flash returns a message on success, so log it.
        wok_log.info(output)

    def reject(self, ident):
        command = ['update_flash', '-r']
        output, error, rc = run_command(command)
        if rc:
            raise OperationFailed('GINFW0006E', {'rc': rc})

        # update_flash returns a message on success, so log it.
        wok_log.info(output)

    @staticmethod
    def is_feature_available():
        return platform.machine().startswith('ppc')

    def _execute_task(self, cb, params):
        cmd = params['command']
        add_notification('GINFW0007I', plugin_name='/plugins/ginger')
        cb('Firmware update is initializing. '
           'System will reboot in order to flash the firmware.')

        # update_flash may take some time to restart host. Sleep to make sure
        # user notification will show up
        # FIXME this timer is based on a UI constraint. This is not a good
        # design.
        time.sleep(3)
        output, error, rc = run_command(cmd, out_cb=cb)

        if rc:
            if params['operation'] == 'update':
                raise OperationFailed('GINFW0004E', {'error': error})
            else:
                raise OperationFailed('GINFW0008E', {'error': error})

        cb('OK', True)
