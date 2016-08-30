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

from wok.control.base import Resource
from wok.control.utils import UrlSubNode

from conf import Conf
from graph import Graphs
from log import Logs
from report import Reports
from rules import Rules
from syscall import Syscall

AUDIT_REQUESTS = {
    'POST': {
        'load_rules': "GINAUD0001L"
    },
}


@UrlSubNode('audit', True)
class Audit(Resource):

    def __init__(self, model, id=None):
        super(Audit, self).__init__(model, id)
        self.role_key = "administration"
        self.conf = Conf(model)
        self.graphs = Graphs(model)
        self.logs = Logs(model)
        self.reports = Reports(model)
        self.rules = Rules(model)
        self.syscall = Syscall(model)
        self.uri_fmt = '/audit/%s'
        self.load_rules = self.generate_action_handler('load_rules',
                                                       ['auditrule_file'])
        self.log_map = AUDIT_REQUESTS

    @property
    def data(self):
        return self.info
