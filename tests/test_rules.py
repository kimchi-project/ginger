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

import mock
import unittest

from wok.plugins.ginger.model.rules import RuleModel
from wok.plugins.ginger.model.rules import RulesModel


class RulesTests(unittest.TestCase):

    def test_create_control_rule(self):
        params = {"type": "Control Rule",
                  "rule": "-b 1238"}
        actual_out = '-b 1238'
        rulesmodel = RulesModel()
        expected_out = rulesmodel.construct_control_rule(params)
        self._baseAssertEqual(actual_out, expected_out)

    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.construct_fs_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.'
                'write_to_audit_rules')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.load_audit_rule')
    def test_create_fs_rule_success(self, mock_load_audit_rule,
                                    mock_write_to_audit_rules, mock_fs_rule):
        param = {"type": "Filesystem Rule",
                 "rule_info": {"key": "modules",
                               "permissions": "rwxa",
                               "file_to_watch": "/home/jkatta/1.txt",
                               "key": "watch_me"}}
        rule_type = '-w'
        rule = '-w /home/mesmriti/1.txt -p rwxa -k watch_me'
        mock_fs_rule.return_value = rule
        mock_write_to_audit_rules.return_value = {}
        mock_load_audit_rule.return_value = {}
        rulesmodel = RulesModel()
        rule_out = rulesmodel.create(param)
        mock_fs_rule.assert_called_with(rule_type, param)
        self.assertEquals(rule, rule_out)

    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.construct_sc_rule')
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
                '.construct_control_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.'
                'write_to_aucontrol_rules')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.load_audit_rule')
    def test_create_control_rule_success(self, mock_load_audit_rule,
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

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.delete_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.reload_rules')
    def test_delete_success(self, mock_reload, mock_delete_rule):
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        mock_delete_rule.return_value = {}
        mock_reload.return_value = {}
        rulemodel = RuleModel()
        rulemodel.delete(rule)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.'
                'get_audit_rule_info')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.'
                'write_to_audit_rules')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.'
                'is_rule_exists')
    def test_persist(self, mock_exist, mock_write, mock_get_audit_info):
        """
        Unittest to persist the rule in the rules file
        :param mock_write:
        :param mock_get_audit_info:
        :return:
        """
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
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
        mock_exist.return_value = False
        mock_get_audit_info.return_value = audit_info
        mock_write.return_value = {}
        ruleModel = RuleModel()
        ruleModel.persist(rule)
        mock_get_audit_info.assert_called_with(rule)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.get_auditrule_type')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.'
                'loaded_or_persisted')
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

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.get_audit_rule_info')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.reload_rules')
    def test_unload_loaded_persisted(self, mock_reload, mock_get_audit_info):
        """
        Unnitest to unload a loaded and persisted rule.
        :param mock_reload:
        :param mock_delete:
        :param mock_get_audit_info:
        :return:
        """
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        audit_info = {'loaded': 'yes',
                      'persisted': 'yes',
                      'type': 'System Rule',
                      'rule_info': {'action': u'always',
                                    'filter': u'exit',
                                    'systemcall': u'init_module,'
                                                  u'delete_module,'
                                                  u'finit_module',
                                    'key': u'abc99',
                                    'field': [u'arch=b32',
                                              u'arch=b64',
                                              u'key=abc99']
                                    },
                      'rule': u'-a always,exit -F arch=b32'
                              u' -F arch=b64 -S init_module,'
                              u'delete_module,finit_module -F'
                              u' key=abc99'
                      }
        mock_get_audit_info.return_value = audit_info
        mock_reload.return_value = {}
        rulemodel = RuleModel()
        rulemodel.unload(rule)
        mock_get_audit_info.assert_called_with(rule)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.'
                'get_audit_rule_info')
    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.reload_rules')
    def test_unload_loaded_unpersisted(self, mock_reload, mock_get_audit_info):
        """
        Unnitest to unload a loaded and unpersisted rule.
        :param mock_reload:
        :param mock_delete:
        :param mock_get_audit_info:
        :return:
        """
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        audit_info = {'loaded': 'yes', 'persisted': 'no',
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
        mock_get_audit_info.return_value = audit_info
        mock_reload.return_value = {}
        rulemodel = RuleModel()
        rulemodel.unload(rule)
        mock_get_audit_info.assert_called_with(rule)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.get_audit_rule_info')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.load_audit_rule')
    def test_load(self, mock_load, mock_get_audit_info):
        """
         Unittest to load a rule.
        :param mock_write:
        :param mock_get_audit_info:
        :return:
        """
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        audit_info = {'loaded': 'no', 'persisted': 'yes',
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
        mock_get_audit_info.return_value = audit_info
        mock_load.return_value = {}
        ruleModel = RuleModel()
        ruleModel.load(rule)
        mock_get_audit_info.assert_called_with(rule)

    @mock.patch('wok.plugins.ginger.model.rules.RuleModel.is_rule_exists')
    @ mock.patch('wok.plugins.ginger.model.rules.RuleModel.delete_rule')
    @mock.patch('wok.plugins.ginger.model.rules.RulesModel.construct_rules')
    def test_update(self, mock_create_rules, mock_delete_rule,
                    mock_rule_exists):
        """
        Unittest to update a rule.
        :param mock_create_rules:
        :param mock_delete_rule:
        :param mock_rule_exists:
        :return:
        """
        param = {"type": "System Rule",
                 "rule_info": {"action": "always",
                               "filter": "exit",
                               "systemcall": "init_module,delete_module"
                                             ",finit_module",
                               "field": ["arch=b32", "arch=b64"],
                               "key": "abcde"}}
        old_rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
                   'delete_module,finit_module -F key=abc99'
        new_rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
                   'delete_module,finit_module -F key=abcde'
        mock_rule_exists.return_value = True
        mock_delete_rule.return_value = {}
        mock_create_rules.return_value = new_rule
        ruleModel = RuleModel()
        out_rule = ruleModel.update(old_rule, param)
        self.assertEquals(out_rule, new_rule)

    def test_audit_rule_type(self):
        """
         Unittest to get rule type.
        :return:
        """
        rule = '-a always,exit -F arch=b32 -F arch=b64 -S init_module,' \
               'delete_module,finit_module -F key=abc99'
        rule_type = "System Rule"
        ruleModel = RuleModel()
        out_type = ruleModel.get_auditrule_type(rule)
        self.assertEquals(out_type, rule_type)
