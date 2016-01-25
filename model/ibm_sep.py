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

import os
import re

from wok.exception import OperationFailed, NotFoundError
from wok.utils import wok_log, run_command

SUBSCRIBER = re.compile("(Subscriber_[0-9]*: hostname=)(?P<hostname>.*)\
(,port=)(?P<port>.*)(,community=)(?P<community>.*)")


def addSEP(params):
    """
    Add a subscription hostname to IBM SEP tool.
    """
    #  add a new one.
    cmd = ['/opt/ibm/seprovider/bin/subscribe',
           '-h', params['hostname'],
           '-p', str(params['port']),
           '-c', params['community']]
    output, error, rc = run_command(cmd)
    if rc != 0:
        wok_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                      error))
        raise OperationFailed('GINSEP0010E', {'error': error})

    return params['hostname']


class SepModel(object):
    """
    The IBM Serviceable Event Provider (SEP) class for model
    """

    def lookup(self, params):
        cmd = ['systemctl', 'status', "sepctl"]
        output, error, rc = run_command(cmd)

        # workarround to get the correct output from this command
        if rc == 0:
            return {"status": "running"}

        return {"status": "not running"}

    def start(self, params=None):
        cmd = ['systemctl', 'start', 'sepctl']
        output, error, rc = run_command(cmd)
        if rc != 0:
            wok_log.error('SEP service initialization error: %s - %s - %s'
                          % (cmd, rc, error))
            raise OperationFailed('GINSEP0008E', {'error': error})

    def stop(self, params=None):
        cmd = ['systemctl', 'stop', 'sepctl']
        output, error, rc = run_command(cmd)
        if rc != 0:
            wok_log.error('Error stopping SEP service: %s - %s - %s' % (cmd,
                          rc, error))
            raise OperationFailed('GINSEP0009E', {'error': error})

    def is_feature_available(self):
        return (os.path.isfile('/opt/ibm/seprovider/bin/getSubscriber') and
                os.path.isfile('/opt/ibm/seprovider/bin/subscribe') and
                os.path.isfile('/opt/ibm/seprovider/bin/unsubscribe'))


class SubscribersModel(object):
    """
    Manages subscriptions of IBM Service Provider
    """

    def _get_subscriber(self):

        activation_info = []
        entry = {}
        cmd = ['/opt/ibm/seprovider/bin/getSubscriber']
        output, error, rc = run_command(cmd)

        # no subscriber: return empty
        if rc == 1:
            return activation_info

        # error: report
        if rc != 0:
            wok_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                          error))
            raise OperationFailed('GINSEP0007E')

        if len(output) > 1:

            # iterate over lines and parse to dict
            for line in output.splitlines():
                if len(line) > 0:
                    entry = SUBSCRIBER.search(line).groupdict()
                    activation_info.append(entry["hostname"])

        return activation_info

    def create(self, params):
        """
        Create a subscription machine at IBM SEP tool.
        """
        return addSEP(params)

    def get_list(self):
        return self._get_subscriber()


class SubscriptionModel(object):
    """
    Represents a subscription
    """

    def lookup(self, subscription):
        """
        Returns a dictionary with all SEP information.
        """
        cmd = ['/opt/ibm/seprovider/bin/getSubscriber']
        output, error, rc = run_command(cmd)

        # error: report
        if rc != 0:
            wok_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                          error))
            raise OperationFailed('GINSEP0005E', {'error': error})

        if len(output) > 1:

            # iterate over lines and parse to dict
            for line in output.splitlines():
                if len(line) > 0:
                    entry = SUBSCRIBER.search(line).groupdict()

                    # subscriber found
                    if entry["hostname"] == subscription:
                        return entry

        raise NotFoundError("GINSEP0006E", {'hostname': subscription})

    def update(self, name, params):
        """
        Update/add a subscription machine at IBM SEP tool.
        """
        bkp_params = self.lookup(name)
        if len(bkp_params) == 0:
            raise NotFoundError("GINSEP0006E", {'hostname': name})

        self.delete(name)
        try:
            addSEP(params)
        except Exception as e:
            # Rollback on error
            addSEP(bkp_params)
            raise e

    def delete(self, host):
        """
        Removes a SEP subscription
        """
        # subscription not found: raise exception
        if len(self.lookup(host)) == 0:
            raise NotFoundError("GINSEP0006E", {'hostname': host})

        # unsubscribe
        cmd = ['/opt/ibm/seprovider/bin/unsubscribe', '-h', host]
        output, error, rc = run_command(cmd)

        if rc != 0:
            wok_log.error('SEP execution error: %s - %s - %s' % (cmd, rc,
                                                                 error))
            raise OperationFailed('GINSEP0011E', {'error': error})
