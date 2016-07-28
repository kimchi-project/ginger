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

import mock
import unittest

from wok.plugins.ginger.model.rules import get_list_of_loaded_rules
from wok.plugins.ginger.model.rules import RuleModel
from wok.plugins.ginger.model.rules import RulesModel


class RulesTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.rules.run_command')
    def test_get_list_of_loaded_rules(self, mock_run_cmd):
        """
        Unittest to test list the loaded rules.
        :param mock_run_cmd:
        :return:
        """
        """
        :param mock_run_cmd:
        :return:
        """
        cmd = ['auditctl', '-l']
        rule_list = '-w /etc/sudoers.d/ -p wa -k actions\n-a always,' \
                    'exit -F arch=b64' \
                    ' -S adjtimex,settimeofday -F key=time_change'
        mock_run_cmd.return_value = [rule_list, '', 0]
        get_list_of_loaded_rules()
        mock_run_cmd.assert_called_once_with(cmd)

    def test_create_control_rule(self):
        params = {"type": "Control Rule",
                  "rule": "-b 1238"}
        actual_out = '-b 1238'
        rulesmodel = RulesModel()
        expected_out = rulesmodel.create_control_rule(params)
        self._baseAssertEqual(actual_out, expected_out)

    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.create_fs_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.'
                'write_to_audit_rules')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.load_audit_rule')
    def test_create_fs_rule_success(self, mock_load_audit_rule,
                                    mock_write_to_audit_rules, mock_fs_rule):
        param = {"type": "Filesystem Rule",
                 "rule_info": {"key": "modules",
                               "permissions": "rwxa",
                               "file_to_watch": "/home/jkatta/1.txt",
                               "key": "wacth_me"}}
        rule_type = '-w'
        rule = '-w /home/mesmriti/1.txt -p rwxa -k wacth_me'
        mock_fs_rule.return_value = rule
        mock_write_to_audit_rules.return_value = {}
        mock_load_audit_rule.return_value = {}
        rulesmodel = RulesModel()
        rule_out = rulesmodel.create(param)
        mock_fs_rule.assert_called_with(rule_type, param)
        self.assertEquals(rule, rule_out)

    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.create_sc_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.'
                'write_to_audit_rules')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.load_audit_rule')
    def test_create_sc_rule_success(self, mock_load_audit_rule,
                                    mock_write_to_audit_rules, mock_sc_rule):
        param = {"type": "System Rule",
                 "rule_info": {"action": "always",
                               "filter": "exit",
                               "systemcall": "init_module,delete_module"
                                             ",finit_module",
                               "field": ["arch=b32", "arch=b64"],
                               "key": "abc99"}}
        rule_type = '-a'
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        mock_sc_rule.return_value = rule
        mock_write_to_audit_rules.return_value = {}
        mock_load_audit_rule.return_value = {}
        rulesmodel = RulesModel()
        rule_out = rulesmodel.create(param)
        mock_sc_rule.assert_called_with(rule_type, param)
        self.assertEquals(rule, rule_out)

    @mock.patch('wok.plugins.ginger.model.rules.RulesModel'
                '.create_control_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.'
                'write_to_aucontrol_rules')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.load_audit_rule')
    def test_create_controrule_rule_success(self, mock_load_audit_rule,
                                            mock_write_to_aucontrol_rules,
                                            mock_control_rule):
        param = {"type": "Control Rule",
                 "rule": "-r 2"}
        rule = '-r 2'
        mock_control_rule.return_value = rule
        mock_write_to_aucontrol_rules.return_value = {}
        mock_load_audit_rule.return_value = {}
        rulesmodel = RulesModel()
        rule_out = rulesmodel.create(param)
        mock_control_rule.assert_called_with(param)
        self.assertEquals(rule, rule_out)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.delete_rule_line')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.reload_rules')
    def test_delete_success(self, mock_reload, mock_delete_rule):
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        mock_delete_rule.return_value = {}
        mock_reload.return_value = {}
        rulemodel = RuleModel()
        rulemodel.delete(rule)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.get_auditrule_type')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.loaded_or_persisted')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.'
                'get_system_rule_info')
    def test_get_audit_rule_info(self, mock_system_info,
                                 mock_load_persist, mock_type):
        rule_type = 'System Rule'
        name = 'a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        mock_type.return_value = rule_type
        audit_info = {'rule': 'a always,exit -F arch=b32 -F '
                              'arch=b64 -S init_module,'
                              'delete_module,finit_module -F key=abc99',
                      'type': 'System Rule'}
        mock_load_persist.return_value = {}
        expected_out = {'type': 'System Rule',
                        'rule': 'a always,exit -F arch=b32 -F'
                                ' arch=b64 -S init_module,delete_module,'
                                'finit_module -F key=abc99'}
        mock_system_info.return_value = {}
        rulemodel = RuleModel()
        actualout = rulemodel.get_audit_rule_info(name)
        mock_system_info.assert_called_with(audit_info, name)
        self.assertEquals(actualout, expected_out)
