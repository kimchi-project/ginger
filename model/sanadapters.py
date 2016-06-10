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
"""A module to fetch information of FC devices."""
import os


from wok.exception import NotFoundError


FC_HOST_SYS_PATH = '/sys/class/fc_host/%s'

FC_HOST_INFOS = {'wwpn': '/port_name',
                 'wwnn': '/node_name',
                 'max_vports': '/max_npiv_vports',
                 'vports_inuse': '/npiv_vports_inuse',
                 'state': '/port_state',
                 'speed': '/speed',
                 'symbolic_name': '/symbolic_name'}

FC_VIRTUAL_INFOS = {'wwpn': '/port_name',
                    'wwnn': '/node_name',
                    'state': '/port_state',
                    'speed': '/speed',
                    'symbolic_name': '/symbolic_name'}


def get_port_type(name):
    """Get the port type of a FC host.

    Args:
        name (str): the name of the FC host

    Returns:
        str: 'physical' or 'virtual'

    Raises:
        NotFoundError if the fc_host 'name' is invalid.

    """
    fc_path = FC_HOST_SYS_PATH % name

    if not os.path.isdir(fc_path):
        raise NotFoundError('GINADAP0001E', {'adapter': name})

    max_vports_file = os.path.join(fc_path, 'max_npiv_vports')
    vports_inuse_file = os.path.join(fc_path, 'npiv_vports_inuse')
    if os.path.isfile(max_vports_file) and os.path.isfile(vports_inuse_file):
        return 'physical'

    return 'virtual'


class SanAdaptersModel(object):
    """Collection model class for SAN adapters."""

    @staticmethod
    def get_list():
        """Retrieves a list of the available FC hosts.

        Returns:
            List[str]: list of FC hosts.

        """
        try:
            return os.listdir(FC_HOST_SYS_PATH % '')
        except OSError:
            return []


class SanAdapterModel(object):
    """Resource model class for SAN adapters."""

    @staticmethod
    def lookup(name):
        """Method that retrieves details about a FC host.

        Args:
            name (str): the name of the FC host

        Returns:
            dict: a dictionary with information about the FC
                host. Format:
                {
                    'wwpn': (str),
                    'wwnn': (str),
                    'max_vports': (str),
                    'vports_inuse': (str),
                    'state': (str),
                    'speed': (str),
                    'symbolic_name': (str),
                    'port_type': (str)
                }

        Raises:
            NotFoundError if the fc_host 'name' is invalid.

        """

        def read_info(fpath):
            """Helper method to retrieve the content of a file.

            Args:
                fpath (str): the full file path

            Returns:
                str: the file contents

            """
            try:
                with open(fpath) as fc_file:
                    return fc_file.read().strip()
            except IOError:
                return 'Unknown'

        if not os.path.isdir(FC_HOST_SYS_PATH % name):
            raise NotFoundError('GINADAP0001E', {'adapter': name})

        info = {}
        info['port_type'] = get_port_type(name)
        fc_host_keys = FC_HOST_INFOS

        if info['port_type'] == 'virtual':
            fc_host_keys = FC_VIRTUAL_INFOS
            info['max_vports'] = 'Not applicable'
            info['vports_inuse'] = 'Not applicable'

        for key in fc_host_keys:
            info[key] = read_info(FC_HOST_SYS_PATH % name +
                                  fc_host_keys[key])
        return info
