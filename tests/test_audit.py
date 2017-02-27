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

import mock
import unittest

from wok.plugins.ginger.model.audit import AuditModel


class AuditTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.get_audit_rule_info')
    @mock.patch('wok.plugins.ginger.model.rules.get_list_of_persisted_rules')
    def test_get_list_of_pre_rules(self, mock_get_list_of_persisted_rules,
                                   mock_audit_rule_info):
        """
         Unittest to test the get list of predefined rules.
        :param mock_get_lis_predef_rules:
        :param mock_audit_rule_info:
        :return:
        """
        rule_list = '-a always,exit -F arch=b32 -F arch=b64' \
                    ' -S init_module,delete_module,finit_module' \
                    ' -F key=abc99'
        audit_info = {'loaded': 'yes', 'persisted': 'yes',
                      'type': 'System Rule',
                      'rule_info': {'action': u'always',
                                    'filter': u'exit',
                                    'systemcall': u'init_module,'
                                                  u'delete_module,'
                                                  u'finit_module',
                                    'key': u'abc99', 'field': [u'arch=b32',
                                                               u'arch=b64',
                                                               u'key=abc99']
                                    },
                      'rule': u'-a always,exit -F arch=b32 '
                              u'-F arch=b64 -S init_module,'
                              u'delete_module,finit_module'
                              u' -F key=abc99'
                      }
        mock_get_list_of_persisted_rules.return_value = rule_list
        mock_audit_rule_info.return_value = audit_info
        auditmodel = AuditModel()
        result = auditmodel.get_list_of_pre_rules()
        self.assertEquals(result['rule1'], audit_info)

    @mock.patch('wok.plugins.ginger.model.audit.AuditModel.'
                'load_predefined_rules')
    def test_load(self, mock_load_redef_rules):
        """
        Unnittest to lead the loadof predef rules.
        :param mock_load_redef_rules:
        :return:
        """
        name = 'name'
        auditrule_file = '/var/tmp/test.txt'
        mock_load_redef_rules.return_value = {}
        auditmodel = AuditModel()
        auditmodel.load_rules(name, auditrule_file)
