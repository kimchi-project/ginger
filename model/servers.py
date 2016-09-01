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

import base64
import json
import os
import random
import string
import time

from Crypto.Cipher import AES

from wok.config import PluginPaths
from wok.exception import OperationFailed, MissingParameter, InvalidParameter
from wok.utils import run_command

SERVERCONFIGPATH = os.path.join(
    PluginPaths('ginger').conf_dir,
    'server.config')
ALPHABET = string.digits + string.ascii_letters
SDR_LOCAL_CACHE_DIR = PluginPaths('ginger').conf_dir
SDR_CACHE = 'sdr_cache'


def _check_if_server_with_name_exists(nameToCheck, existingServers):
    for server in existingServers:
        if nameToCheck == server['name']:
            return True
        else:
            continue
    return False


def _check_if_server_with_ipaddr_exists(ipaddrToCheck, existingServers):
    for server in existingServers:
        if ipaddrToCheck == server['ipaddr']:
            return True
        else:
            continue
    return False


def _read_server_data():
    existingServers = []
    if os.path.isfile(SERVERCONFIGPATH):
        with open(SERVERCONFIGPATH) as fr:
            if os.stat(SERVERCONFIGPATH).st_size != 0:
                existingServers = json.load(fr)
    return existingServers


def _update_server_data(serverData):
    with open(SERVERCONFIGPATH, 'wb') as fw:
        json.dump(serverData, fw)


def add_config(serverConfig):
    existingServers = _read_server_data()
    newServerName = serverConfig['name']
    newServerIpAddr = serverConfig['ipaddr']
    if _check_if_server_with_name_exists(newServerName, existingServers):
        raise OperationFailed('GINSE00002E', {'name': newServerName})
    elif _check_if_server_with_ipaddr_exists(newServerIpAddr, existingServers):
        raise OperationFailed('GINSE00004E', {'ipaddr': newServerIpAddr})
    else:
        existingServers.append(serverConfig)
    _update_server_data(existingServers)


def get_config(name):
    existingServers = _read_server_data()

    for server in existingServers:
        if name == server['name']:
            return server
    raise OperationFailed('GINSE00005E', {'name': name})


def get_server_status(serverData):
    if 'username' in serverData.keys() and serverData['username']:
        out, err, rc = run_command(
            ['ipmitool', '-H', serverData['ipaddr'], '-I', 'lanplus', '-U',
             serverData['username'], '-P',
             decrypt(serverData['password'], serverData['salt']),
             'chassis', 'status'])
    else:
        out, err, rc = run_command(
            ['ipmitool', '-H', serverData['ipaddr'], '-I', 'lanplus', '-P',
             decrypt(serverData['password'], serverData['salt']),
             'chassis', 'status'])
    if rc == 0:
        output = out.split('\n')
        status = output[0].split(':')
        systemStatus = status[1].strip(' ').strip('\n')
        serverData.update({'status': systemStatus})
    else:
        return {}  # return - raising exception is handled by the caller
    return serverData


def update_config(serverConfig):
    existingServers = _read_server_data()
    for each in existingServers:
        if serverConfig['name'] == each['name']:
            each.update(serverConfig)
            _update_server_data(existingServers)
            break


def server_power_cycle(serverData, cmd):
    count = 0
    if 'username' in serverData.keys() and serverData['username']:
        out, err, rc = run_command(
            ['ipmitool', '-H', serverData['ipaddr'], '-I', 'lanplus', '-U',
             serverData['username'], '-P',
             decrypt(serverData['password'], serverData['salt']),
             'chassis', 'power', cmd])
    else:
        out, err, rc = run_command(
            ['ipmitool', '-H', serverData['ipaddr'], '-I', 'lanplus', '-P',
             decrypt(serverData['password'], serverData['salt']),
             'chassis', 'power', cmd])
    if rc == 0:
        while True:
            serverData = get_server_status(serverData)
            if 'on' in cmd and 'on' in serverData['status']:
                return True
            elif 'off' in cmd and 'off' in serverData['status']:
                return True
            else:
                if count == 15:
                    return False
                count += 1
                time.sleep(20)
    else:
        return False  # raising exception is handled by the caller


def delete_config(serverName):
    existingServers = _read_server_data()
    foundServer = False

    for server in existingServers:
        if serverName == server['name']:
            foundServer = True
            existingServers.remove(server)
            break

    if not foundServer:
        raise OperationFailed('GINSE00005E', {'name': serverName})

    _update_server_data(existingServers)
    localSdrCache = os.path.join(
        SDR_LOCAL_CACHE_DIR,
        SDR_CACHE + "_" + serverName)
    if os.path.isfile(localSdrCache):
        os.remove(localSdrCache)


def encrypt(text, salt):
    PAD = "X"
    if len(text) % 16 != 0:
        text += PAD * (16 - (len(text) % 16))
    cipher = AES.new(salt)
    encrypted = cipher.encrypt(text.encode())
    return base64.b64encode(encrypted).decode()


def decrypt(text, salt):
    PAD = "X"
    cipher = AES.new(salt)
    plain = cipher.decrypt(base64.b64decode(text))
    return plain.decode().rstrip(PAD)


class ServersModel(object):

    def get_list(self):
        """
        """
        serverNames = []
        existingServers = []
        if os.path.isfile(SERVERCONFIGPATH):
            with open(SERVERCONFIGPATH) as fr:
                if os.stat(SERVERCONFIGPATH).st_size != 0:
                    existingServers = json.load(fr)

        for server in existingServers:
            serverNames.append(server['name'])
        return serverNames

    def create(self, params):
        """
        """
        if (
                'ipaddr' not in params or 'name' not in params or
                'password' not in params
                ):
            raise MissingParameter('GINSE00001E')
        params['salt'] = ''.join(random.choice(ALPHABET) for i in range(16))
        params['password'] = encrypt(params['password'], params['salt'])
        serverData = get_server_status(params)
        if serverData:
            if 'status' in serverData:
                del serverData['status']
            add_config(serverData)
            return serverData['name']
        else:
            raise OperationFailed('GINSE00003E', params)


class ServerModel(object):

    def delete(self, name):
        delete_config(name)

    def lookup(self, name):
        """
        """
        serverData = get_config(name)
        info = {}
        status = "Unknown"
        if serverData:
            serverData = get_server_status(serverData)
            if serverData:
                status = serverData['status']
            info = {
                'name': serverData['name'],
                'ipaddr': serverData['ipaddr'],
                'status': status
            }
        return info

    def poweron(self, name):
        """
        """
        serverData = get_config(name)
        if serverData:
            serverIpaddr = serverData['ipaddr']
            serverData = get_server_status(serverData)
        else:
            raise OperationFailed('GINSE00005E', {'name': name})
        if not serverData:
            raise OperationFailed(
                'GINSE00003E',
                {'name': name,
                 'ipaddr': serverIpaddr})
        if 'off' in serverData['status']:
            if not server_power_cycle(serverData, 'on'):
                raise OperationFailed('GINSE00006E', {'name': name})
        else:
            return  # "server is already in powered ON"

    def poweroff(self, name):
        """
        """
        serverData = get_config(name)
        if serverData:
            serverIpaddr = serverData['ipaddr']
            serverData = get_server_status(serverData)
        else:
            raise OperationFailed('GINSE00005E', {'name': name})
        if not serverData:
            raise OperationFailed(
                'GINSE00003E',
                {'name': name,
                 'ipaddr': serverIpaddr})
        if 'on' in serverData['status']:
            if not server_power_cycle(serverData, 'off'):
                raise OperationFailed('GINSE00007E', {'name': name})
        else:
            return  # "server is already in powered OFF"

    def update(self, name, params):
        if params.get('name') or params.get('ipaddr'):
            raise InvalidParameter("GINSE00009E")
        if not params.get('password'):
            raise MissingParameter("GINSE00008E")
        serverData = get_config(name)
        ipaddr = serverData['ipaddr']
        serverData['salt'] = ''.join(random.choice(ALPHABET)
                                     for i in range(16))
        serverData['password'] = encrypt(params['password'],
                                         serverData['salt'])
        if params.get('username'):
            serverData['username'] = params['username']
        serverData = get_server_status(serverData)
        if not serverData:
            raise OperationFailed('GINSE00003E', {'name': name,
                                                  'ipaddr': ipaddr})
        else:
            update_config(serverData)
            return serverData['name']
