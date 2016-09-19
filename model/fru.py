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

from servers import get_config, decrypt
from wok.utils import run_command
from wok.exception import NotFoundError, OperationFailed


def get_frus(server):
    frus = []
    serverData = get_config(server)
    if serverData:
        password = serverData['password']
        ipaddr = serverData['ipaddr']
        salt = serverData['salt']
        if serverData.get('username'):
            out, err, rc = run_command(
                ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-U',
                 serverData['username'], '-P', decrypt(password, salt),
                 'fru', 'print'])
        else:
            out, err, rc = run_command(
                ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-P',
                 decrypt(password, salt), 'fru', 'print'])
        if rc == 0:
            output = out.rstrip().split('\n\n')
            for each in output:
                frus.append(process_each_fru(each))
        else:
            raise OperationFailed(
                'GINFRU00001E',
                {'name': server,
                 'err': err,
                 'rc': rc})
    else:
        raise OperationFailed('GINSEL00002E', {'name': server})
    return frus


def process_each_fru(eachFru):
    try:
        fruRecords = {}
        eachFruRecord = eachFru.split('\n')
        deviceDescriptionSplit = eachFruRecord[0].split(':')
        deviceDescriptionKey = deviceDescriptionSplit[0].strip()
        deviceDescriptionValue = deviceDescriptionSplit[1].strip()
        deviceDescription = deviceDescriptionValue[
            :deviceDescriptionValue.rindex('(') - 1].strip()
        deviceId = deviceDescriptionValue[
            deviceDescriptionValue.rindex(
                '(') +
            1:deviceDescriptionValue.rindex(
                ')')].strip(
        )
        idSplit = deviceId.split(' ')
        fruRecords['ID'] = idSplit[1].strip()
        fruRecords[deviceDescriptionKey] = deviceDescription
        for each in eachFruRecord[1:]:
            fruEntries = each.split(':', 1)
            if(len(fruEntries) == 2):
                fruRecords[fruEntries[0].strip()] = fruEntries[1].strip()
            else:
                fruRecords['Info'] = fruEntries[0]
    except:
        raise OperationFailed('GINFRU00003E', {'eachFru': eachFru})
    return fruRecords


def get_fru(server, name):
    frus = get_frus(server)
    for each in frus:
        if name == each['ID']:
            return each
    raise NotFoundError('GINFRU00002E', {'name': server, 'fru_id': name})


class FrusModel(object):

    def get_list(self, server):
        """
        """
        fru = get_frus(server)
        return fru


class FruModel(object):

    def lookup(self, server, name):
        """
        """
        fru = get_fru(server, name)
        return fru
