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

import fileinput
import re
import sys
import threading

from services import ServiceModel
from wok.exception import OperationFailed

gingerAuditConfLock = threading.RLock()

AUDISPD_CONF = '/etc/audisp/audispd.conf'
AUDITD_CONF = '/etc/audit/auditd.conf'


class ConfModel(object):
    _confirm_timeout = 10.0

    def __init__(self, **kargs):
        pass

    def lookup(self, name):
        return self.get_auditd_conf()

    def get_auditd_conf(self):
        """
        Method to get the contents of the audit
        conf file.
        :return: dictionary of conf details.
        """
        try:
            auditd_conf = {}
            with open(AUDITD_CONF, "r") as conf_file:
                for each_line in conf_file:
                    if each_line[:1] not in "#,\n":
                        list = each_line.split('=')
                        auditd_conf[list[0].strip()] = list[1].strip()
            return auditd_conf
        except Exception:
            raise OperationFailed("GINAUD0023E")

    def audisp_enable(self, name):
        """
        Method to enable the audit dispatcher in conf file.
        """
        try:
            gingerAuditConfLock.acquire()
            ServiceModel().lookup("auditd")
            self.del_lines_of_attribute("dispatcher")
            for line in fileinput.input(AUDITD_CONF, inplace=True):
                sys.stdout.write(line)
            with open(AUDITD_CONF, 'a+') as auditd_conf:
                auditd_conf.write("dispatcher = /sbin/audispd\n")
                auditd_conf.close()
        except Exception:
            raise OperationFailed("GINAUD0024E")
        finally:
            gingerAuditConfLock.release()

    def audisp_disable(self, name):
        """
        Method to disable the audit dispatcher in conf file.
        """
        try:
            gingerAuditConfLock.acquire()
            self.del_lines_of_attribute("dispatcher")
            for line in fileinput.input(AUDITD_CONF, inplace=True):
                sys.stdout.write(line)
            with open(AUDITD_CONF, 'a+') as auditd_conf:
                auditd_conf.write("#dispatcher = /sbin/audispd\n")
                auditd_conf.close()
        except Exception:
            raise OperationFailed("GINAUD0025E")
        finally:
            gingerAuditConfLock.release()

    def del_lines_of_attribute(self, key_string):
        for line in fileinput.input(AUDITD_CONF, inplace=True):
            my_regex = "(#)+(" + re.escape(key_string) + ")+\s*\W+\s*(\W+\w+)*"
            if not re.match(my_regex, line):
                sys.stdout.write(line)

        for line in fileinput.input(AUDITD_CONF, inplace=True):
            my_regex = "(" + re.escape(key_string) + ")+\s*\W+\s*(\W+\w+)*"
            if not re.match(my_regex, line):
                sys.stdout.write(line)

    def write_to_conf(self, key, value):
        with open(AUDITD_CONF, 'a+') as auditd_conf:
            auditd_conf.write(key + " = " + value + "\n")
            auditd_conf.close()

    def update(self, name, params):
        """
        Method to update data in conf file.
        """
        try:
            gingerAuditConfLock.acquire()
            for each_key in params:
                self.del_lines_of_attribute(each_key)
                self.write_to_conf(each_key, params[each_key])
        except Exception:
            raise OperationFailed("GINAUD0026E")
        finally:
            gingerAuditConfLock.release()
