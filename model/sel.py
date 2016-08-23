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

from wok.utils import run_command
from wok.exception import NotFoundError, OperationFailed

from servers import get_config, decrypt


def get_sels(server):
    sels = []
    serverData = get_config(server)
    if serverData:
        password = serverData['password']
        ipaddr = serverData['ipaddr']
        salt = serverData['salt']
        if serverData.get('username'):
            out, err, rc = run_command(
                ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-U',
                 serverData['username'], '-P', decrypt(password, salt),
                 'sel', 'list'])
        else:
            out, err, rc = run_command(
                ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-P',
                 decrypt(password, salt), 'sel', 'list'])
        if rc == 0:
            output = out.rstrip().split('\n')
            for each in output:
                sels.append(get_each_sel(each))
        else:
            raise OperationFailed(
                'GINSEL00001E',
                {'name': server,
                 'err': err,
                 'rc': rc})
    else:
        raise OperationFailed('GINSEL00002E', {'name': server})
    return sels


def get_each_sel(selString):
    try:
        sel = {}
        selSplit = selString.split(' | ')
        sel['id'] = selSplit[0].lstrip()
        sel['date'] = selSplit[1]
        sel['time'] = selSplit[2]
        sel['eventType'] = selSplit[3]
        sel['eventData'] = selSplit[4]
        sel['eventAction'] = selSplit[5]
    except:
        raise OperationFailed('GINSEL00005E', {'selString': selString})
    return sel


def get_sel(server, name):
    sels = get_sels(server)
    for each in sels:
        if name == each['id']:
            return each
    raise NotFoundError('GINSEL00003E', {'name': server, 'sel_id': name})


def delete_sel(server, sel_id):
    serverData = get_config(server)
    sel_id_int = int(sel_id, 16)
    if serverData:
        password = serverData['password']
        ipaddr = serverData['ipaddr']
        salt = serverData['salt']
        if serverData.get('username'):
            out, err, rc = run_command(
                ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-U',
                 serverData['username'], '-P', decrypt(password, salt),
                 'sel', 'delete', str(sel_id_int)])
        else:
            out, err, rc = run_command(
                ['ipmitool', '-H', ipaddr, '-I', 'lanplus', '-P',
                 decrypt(password, salt), 'sel', 'delete', str(sel_id_int)])
        if rc != 0:
            raise OperationFailed(
                'GINSEL00004E',
                {'name': server,
                 'sel_id': sel_id,
                 'err': err,
                 'rc': rc})
    else:
        raise OperationFailed('GINSEL00002E', {'name': server})


class SelsModel(object):

    def get_list(self, server):
        """
        """
        return get_sels(server)


class SelModel(object):

    def delete(self, server, sel_id):
        delete_sel(server, sel_id)

    def lookup(self, server, name):
        """
        """
        return get_sel(server, name)
