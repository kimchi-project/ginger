#
# Project Ginger
#
# Copyright IBM, Corp. 2014-2016
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

import cherrypy
from cherrypy.lib.static import serve_file

from wok.control.base import Collection, Resource
from wok.control.utils import UrlSubNode


@UrlSubNode('backup', True)
class Backup(Resource):
    def __init__(self, model):
        super(Backup, self).__init__(model)
        self.role_key = "administration"
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.archives = Archives(model)
        self.discard_archives = self.generate_action_handler(
            'discard_archives', ['days_ago', 'counts_ago'])
        self.uri_fmt = '/backup/%s'
        # In future we will add self.schedules


class Archives(Collection):
    def __init__(self, model):
        super(Archives, self).__init__(model)
        self.resource = Archive


class Archive(Resource):
    def __init__(self, model, ident):
        super(Archive, self).__init__(model, ident)

    @property
    def data(self):
        info = {'identity': self.ident}
        info.update(self.info)
        return info

    @cherrypy.expose
    def file(self):
        self.lookup()
        return serve_file(self.info['file'], disposition='attachment',
                          debug=True)
