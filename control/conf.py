#
# Project Ginger
#
# Copyright IBM Corp, 2016-2017
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

from wok.control.base import Resource
from wok.control.utils import UrlSubNode

CONF_REQUESTS = {
    'POST': {
        'audisp_enable': "GINAUD0002L",
        'audisp_disable': "GINAUD0006L",
    }
}


@UrlSubNode('conf', True)
class Conf(Resource):
    def __init__(self, model, id=None):
        super(Conf, self).__init__(model, id)
        self.uri_fmt = '/audit/conf/%s'
        self.audisp_enable = self.generate_action_handler('audisp_enable')
        self.audisp_disable = self.generate_action_handler('audisp_disable')
        self.log_map = CONF_REQUESTS

    @property
    def data(self):
        return self.info
