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

import os
import shutil
import threading

from distutils.spawn import find_executable


import rules

from wok.exception import OperationFailed
from wok.utils import run_command

gingerAuditLock = threading.RLock()


RULE_FILE = '/etc/audit/audit.rules'


class AuditModel(object):
    _confirm_timeout = 10.0

    def __init__(self, **kargs):
        pass

    @staticmethod
    def is_feature_available():
        return find_executable('auditctl') is not None

    def lookup(self, name):
        return self.get_list_of_pre_rules()

    def get_list_of_pre_rules(self):
        rules_record = {}
        i = 1
        rules_list = rules.get_list_of_persisted_rules()
        for each_rule in rules_list:
            record_details = {}
            record = 'rule' + str(i)
            i += 1
            record_details[record] = {}
            record_details[record] = \
                rules.RuleModel().get_audit_rule_info(each_rule)
            rules_record.update(record_details)
        return rules_record

    def load_rules(self, name, auditrule_file):
        try:
            gingerAuditLock.acquire()
            self.load_predefined_rules(auditrule_file)
        finally:
            gingerAuditLock.release()

    def load_predefined_rules(self, auditrule_file):
        flag = 0
        if os.path.isfile(str(auditrule_file)):
            backup_file = RULE_FILE + "_bak"
            try:
                shutil.copy(RULE_FILE, backup_file)
                with open(RULE_FILE, 'wb') as destination:
                    with open(backup_file, 'rb') as source:
                        shutil.copyfileobj(source, destination)
                    with open(auditrule_file, 'rb') as source:
                        shutil.copyfileobj(source, destination)
                    destination.close()
                flag = 1
            except Exception, e:
                raise OperationFailed('GINAUD0019E',  {'Error': e.message})
        else:
            raise OperationFailed('GINAUD0021E')
        if flag == 1:
            command = ['auditctl', '-R', auditrule_file]
            output, error, rc = run_command(command)
            if rc:
                self.recover_rulesfile(RULE_FILE, backup_file)
                raise OperationFailed('GINAUD0019E', {'Error': error})

    def recover_rulesfile(self, rulefile, backupfile):
        """
        """
        if os.path.isfile(backupfile):
            shutil.copy(backupfile, rulefile)
