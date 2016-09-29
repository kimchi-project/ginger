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

import threading

from utils import del_lines_of_attribute, write_to_conf
from wok.exception import OperationFailed


gingerAuditdispLock = threading.RLock()

AUDISPD_CONF = '/etc/audisp/audispd.conf'
AUDITD_CONF = '/etc/audit/auditd.conf'


class AuditdispModel(object):
    _confirm_timeout = 10.0

    def __init__(self, **kargs):
        pass

    def lookup(self, name):
        return self.get_auditdisp_conf()

    def get_auditdisp_conf(self):
        try:
            auditdisp_conf = {}
            with open(AUDISPD_CONF, "r") as conf_file:
                for each_line in conf_file:
                    if each_line[:1] not in "#,\n":
                        list = each_line.split('=')
                        auditdisp_conf[list[0].strip()] = list[1].strip()
            return auditdisp_conf
        except Exception:
            raise OperationFailed("GINAUDISP0005E")

    def update(self, name, params):
        try:
            gingerAuditdispLock.acquire()
            for each_key in params:
                del_lines_of_attribute(each_key, AUDISPD_CONF)
                write_to_conf(each_key, params[each_key], AUDISPD_CONF)
        except OperationFailed:
            raise
        except Exception:
            raise OperationFailed("GINAUDISP0004E", {"name": name})
        finally:
            gingerAuditdispLock.release()
