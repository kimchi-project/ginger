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


from kimchi.exception import OperationFailed
from kimchi.utils import kimchi_log, run_command


class SepModel(object):
    """
    The IBM Serviceable Event Provider (SEP) class for model
    """
    def __init__(self, **kargs):
        self._activation_info = {}
        self._sep_status = None

    def _get_subscriber(self):
        cmd = ['/opt/ibm/seprovider/bin/getSubscriber']
        output, error, rc = run_command(cmd)
        if rc > 1:
            kimchi_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                             error))
            raise OperationFailed('GINSEP0004E', {'cmd': cmd, 'rc': rc,
                                  'error': error})

        if (len(output) < 1) or (rc == 1):
            self._activation_info['hostname'] = ''
            self._activation_info['port'] = ''
            self._activation_info['community'] = ''
        else:
            # parse the output and return the content
            (hostname, port, community) = output.split()[1].split(',')

            self._activation_info['hostname'] = hostname.split('=')[1]
            self._activation_info['port'] = port.split('=')[1]
            self._activation_info['community'] = community.split('=')[1]

        return self._activation_info

    def start(self, params=None):
        cmd = ['/opt/ibm/seprovider/bin/sepcli', 'start']
        output, error, rc = run_command(cmd)
        if rc != 0:
            kimchi_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                             error))
            raise OperationFailed('GINSEP0004E', {'cmd': cmd, 'rc': rc,
                                  'error': error})
        self._sep_status = 'running'

    def stop(self, params=None):
        cmd = ['/opt/ibm/seprovider/bin/sepcli', 'stop']
        output, error, rc = run_command(cmd)
        if rc != 10:
            kimchi_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                             error))
            raise OperationFailed('GINSEP0004E', {'cmd': cmd, 'rc': rc,
                                  'error': error})
        self._sep_status = 'not running'

    def _status(self):
        cmd = ['/opt/ibm/seprovider/bin/sepcli', 'status']
        output, error, rc = run_command(cmd)

        # workarround to get the correct output from this command
        if len(output) == 0:
            output = error

        if rc == 10:
            # sep is ** officially** not running
            self._sep_status = 'not running'
            kimchi_log.error(output)
        elif rc != 0:
            # command not success
            self._sep_status = 'not running'
            kimchi_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                             error))
            raise OperationFailed('GINSEP0004E', {'cmd': cmd, 'rc': rc,
                                  'error': error})
        else:
            # sep is running
            self._sep_status = 'running'
            kimchi_log.error(output)

    def lookup(self, params=None):
        """
        Returns a dictionary with all SEP information.
        """
        info = {}
        self._status()
        info['status'] = self._sep_status
        info['subscription'] = self._get_subscriber()
        return info

    def update(self, name, params):
        """
        Update/add a subscription machine at IBM SEP tool.
        """
        # check if the hostname to update is the same of the current
        # subscription and unsubscribe it if not - we are working with
        # only one subscription at the moment.
        if ((self._activation_info['hostname'] != '') and
           (params['hostname'] != self._activation_info['hostname'])):
            cmd = ['/opt/ibm/seprovider/bin/unsubscribe',
                   '-h', self._activation_info['hostname']]
            output, error, rc = run_command(cmd)
            if rc != 0:
                kimchi_log.error('SEP execution error: %s - %s - %s' % (cmd,
                                 rc, error))
                raise OperationFailed('GINSEP0004E', {'cmd': cmd, 'rc': rc,
                                      'error': error})

        # update the current subscription info, or add a new one.
        cmd = ['/opt/ibm/seprovider/bin/subscribe',
               '-h', params['hostname'],
               '-p', params['port'],
               '-c', params['community']]
        output, error, rc = run_command(cmd)
        if rc != 0:
            kimchi_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                             error))
            raise OperationFailed('GINSEP0004E', {'cmd': cmd, 'rc': rc,
                                  'error': error})
        self._sep_status = 'running'
