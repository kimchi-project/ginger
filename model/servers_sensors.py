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

import os

from wok.exception import OperationFailed
from wok.utils import run_command

from servers import get_config, decrypt, SDR_LOCAL_CACHE_DIR, SDR_CACHE


ALLOWED_SENSOR_TYPES = [
    'Temperature', 'Voltage', 'Current', 'Fan', 'Physical Security',
    'Platform Security', 'Processor', 'Power Supply', 'Power Unit',
    'Cooling Device', 'Other', 'Memory', 'Drive Slot / Bay',
    'POST Memory Resize', 'System Firmwares', 'Event Logging Disabled',
    'Watchdog1', 'System Event', 'Critical Interrupt', 'Button',
    'Module / Board', 'Microcontroller', 'Add-in Card', 'Chassis',
    'Chip Set', 'Other FRU', 'Cable / Interconnect', 'Terminator',
    'System Boot Initiated', 'Boot Error', 'OS Boot', 'OS Critical Stop',
    'Slot / Connector', 'System ACPI Power State', 'Watchdog2',
    'Platform Alert', 'Entity Presence', 'Monitor ASIC', 'LAN',
    'Management Subsys Health', 'Battery', 'Session Audit',
    'Version Change', 'FRU State']


def list_sensor_data(server, sensor_type):
    sdrs = []
    serverData = get_config(server)
    if serverData:
        out = get_sdr_data(serverData, sensor_type)
        output = out.rstrip().split('\n')
        for each in output:
            sdrs.append(get_each_sdr(each))
    else:
        raise OperationFailed('GINSEL00002E', {'name': server})
    return sdrs


def get_sdr_data(serverData, sensor_type):
    password = serverData['password']
    ipaddr = serverData['ipaddr']
    salt = serverData['salt']
    serverName = serverData['name']
    if serverData.get('username'):
        username = serverData['username']
    else:
        username = ''
    localSdrCache = os.path.join(
        SDR_LOCAL_CACHE_DIR,
        SDR_CACHE + "_" + serverName)
    if os.path.isfile(localSdrCache):
        return run_sdr_command(username, password, ipaddr, salt,
                               serverName, sensor_type, localSdrCache, True)
    else:
        if create_local_sdr_cache(username, password, ipaddr, salt,
                                  localSdrCache, serverName):
            return run_sdr_command(username, password, ipaddr, salt,
                                   serverName, sensor_type,
                                   localSdrCache, True)
        else:
            return run_sdr_command(username, password, ipaddr, salt,
                                   serverName, sensor_type,
                                   localSdrCache, False)


def run_sdr_command(
    username, password, ipaddr, salt, server, sensor_type,
        localSdrCache, sdrCachePresent):
    cmdlist = [
        'ipmitool', '-H', ipaddr, '-I', 'lanplus',
        '-P', decrypt(password, salt)]
    if sdrCachePresent:
        cmdlist.extend(['-S', localSdrCache])
    if username != '':
        cmdlist.extend(['-U', username])
    if sensor_type == 'all':
        cmdlist.extend(['sdr', 'elist'])
    else:
        cmdlist.extend(['sdr', 'type', sensor_type])
    out, err, rc = run_command(cmdlist)
    if rc == 0:
        return out
    else:
        raise OperationFailed('GINSDR00001E', {'name': server,
                              'err': err, 'rc': rc})


def create_local_sdr_cache(
    username, password, ipaddr, salt,
        localSdrCache, server):
    out, err, rc = run_command(
        ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-U', username, '-P',
         decrypt(password, salt), 'sdr', 'dump', localSdrCache])
    if rc == 0:
        return True
    else:
        return False


def get_each_sdr(sdrString):
    try:
        sdr = {}
        sdrSplit = sdrString.split(' | ')
        sdr['SensorId'] = sdrSplit[0].strip()
        sdr['SensorReading'] = sdrSplit[1]
        sdr['Status'] = sdrSplit[2]
        sdr['EntityId'] = sdrSplit[3]
        if len(sdrSplit) == 5:
            sdr['DiscreteState'] = sdrSplit[4]
        else:
            sdr['DiscreteState'] = ''
    except:
        raise OperationFailed('GINSDR00002E', {'sdrString': sdrString})
    return sdr


def check_sensor_types(sensor_types):
    for sensor_type in sensor_types:
        if sensor_type not in ALLOWED_SENSOR_TYPES:
            raise OperationFailed(
                'GINSDR00003E',
                {'sensor_type': sensor_type})


class ServerSensorsModel(object):

    def get_list(self, server, sensor_type=None):
        sensor_data = []
        if not sensor_type:
            return list_sensor_data(server, 'all')
        else:
            sensor_types = sensor_type.split(',')
            check_sensor_types(sensor_types)
        for sensor in sensor_types:
            sensor_data.extend(list_sensor_data(server, sensor))

        return sensor_data
