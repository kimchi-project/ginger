#
# Project Kimchi
#
# Copyright IBM, Corp. 2013
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

RESOLV_CONF = '/etc/resolv.conf'


class NetworkModel(object):

    def lookup(self, name):
        return {'nameservers': self._get_nameservers()}

    def _get_nameservers(self):
        try:
            with open(RESOLV_CONF) as f:
                return [line.split()[1] for line in f
                        if line.startswith('nameserver')]
        except IOError as e:
            raise OperationFailed('GINNET0001E', {'reason': e.message})

    def update(self, name, params):
        try:
            with open(RESOLV_CONF, 'w') as f:
                f.write(''.join('nameserver %s\n' % server
                        for server in params['nameservers']))
        except IOError as e:
            raise OperationFailed('GINNET0002E', {'reason': e.message})
