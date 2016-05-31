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

from wok.exception import OperationFailed
from wok.model.notifications import add_notification
from wok.model.tasks import TaskModel, TasksModel
from wok.utils import add_task, run_command, wok_log

fw_tee_log = '/tmp/fw_tee_log.txt'


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
            wok_log.error('Unable to retreive firmware level.')
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

    def upgrade(self, fw_path=None, pow_ok=None):
        if detect_live_vm():
            wok_log.error('Cannot update system fw while running VMs.')
            raise OperationFailed('GINFW0001E')

        # Process argumets provided by user: firmware path and overwrite-perm
        if fw_path is None:
            wok_log.error('FW update failed: '
                          'No image file found in the package file.')
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
                wok_log.error('FW update failed: '
                              'No image file found in the package file.')
                raise OperationFailed('GINFW0003E')
        else:
            image_file = fw_path
        ms.close()

        command = ['update_flash', '-f', image_file]
        if pow_ok is not None:
            command.insert(1, '-n')
        wok_log.info('FW update: System will reboot to flash the firmware.')

        cmd_params = {'command': command, 'operation': 'update'}
        taskid = add_task('/plugins/ginger/firmware/upgrade',
                          self._execute_task, self.objstore, cmd_params)
        return self.task.lookup(taskid)

    def commit(self, name):
        command = ['update_flash', '-c']
        output, error, rc = run_command(command)
        if rc:
            raise OperationFailed('GINFW0005E', {'rc': rc})
        # update_flash returns a message on success, so log it.
        wok_log.info(output)

    def reject(self, name):
        command = ['update_flash', '-r']
        output, error, rc = run_command(command)
        if rc:
            raise OperationFailed('GINFW0006E', {'rc': rc})
        # update_flash returns a message on success, so log it.
        wok_log.info(output)

    def is_feature_available(self):
        return platform.machine().startswith('ppc')

    def _execute_task(self, cb, params):
        cmd = params['command']
        cb("%s running." % cmd[0])

        output, error, rc = run_command(cmd, tee=fw_tee_log)

        if rc:
            if params['operation'] == 'update':
                wok_log.error('Error flashing firmware. Details:\n %s' % error)
                cb("Error flashing firmware: %(error)s. \
                    Please see /usr/sbin/update_flash for rc reasons.", True)
                raise OperationFailed('GINFW0004E', {'rc': rc})
            else:
                wok_log.error('Async run_command error: ', error)
                cb('Async run_command error: %s' % error, True)
        cb("OK", True)


class FirmwareProgressModel(object):
    def __init__(self, **kargs):
        self.tasks = TasksModel(**kargs)
        self.task = TaskModel(**kargs)
        self.current_taskid = 0
        self.objstore = kargs['objstore']

    def is_update_flash_running(self):
        for task in self.tasks.get_list():
            info = self.task.lookup(task)
            if info['target_uri'] == '/plugins/ginger/firmware/upgrade':
                if info['status'] == 'running':
                    return True
        self.current_taskid = 0
        return False

    def tailUpdateLogs(self, cb, tee_log_file=None):
        """
        Read the log_file to return it's content (the output of update_flash
        command). If the file is not found, a simple '*' is displayed to track
        progress.
        """
        if not self.is_update_flash_running():
            msg = "Error flashing firmware.\n"
            msg = msg+"Please see /usr/sbin/update_flash for rc reasons."
            return cb(msg, True)

        fd = None
        try:
            fd = os.open(tee_log_file, os.O_RDONLY)

        # cannot open file, print something to let users know that the
        # system is being upgrading until the package manager finishes its
        # job
        except (TypeError, OSError):
            msgs = []
            while self.is_update_flash_running():
                msgs.append('*')
                cb(''.join(msgs))
                time.sleep(1)
            msgs.append('\n')
            return cb(''.join(msgs), True)

        cb('Firmware update is initializing. \
           System will reboot in order to flash the firmware.')
        add_notification('GINFW0007I', plugin_name='/plugins/ginger')

        # go to the end of logfile and starts reading, if nothing is read or
        # a pattern is not found in the message just wait and retry until
        # the package manager finishes
        os.lseek(fd, 0, os.SEEK_END)
        msgs = []
        progress = []
        while True:
            read = os.read(fd, 1024)
            if not read:
                if not self.is_update_flash_running():
                    break

                if not msgs:
                    progress.append('*')
                    cb(''.join(progress))

                time.sleep(1)
                continue

            msgs.append(read)
            cb(''.join(msgs))

        os.close(fd)
        return cb(''.join(msgs), True)

    def lookup(self, *name):
        if self.current_taskid == 0:
            self.current_taskid = add_task('/plugins/ginger/fwprogress',
                                           self.tailUpdateLogs, self.objstore,
                                           fw_tee_log)
        return self.task.lookup(self.current_taskid)
