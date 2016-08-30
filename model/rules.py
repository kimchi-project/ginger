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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

import os
import re
import threading

from wok.exception import MissingParameter, OperationFailed
from wok.utils import run_command, wok_log

audit_configpath = 'etc/audit/'
persisted_rules_file = '/etc/audit/audit.rules'
tmp_rules_file = '/etc/audit/tmpaudit.rules'

gingerAuditLock = threading.RLock()

action_list = ['always', 'never']
filter_list = ['task', 'user', 'exit', 'exclude']


def merge_rules(loaded_rules, persisted_rules):
    return set(loaded_rules + persisted_rules)


def get_list_of_persisted_rules():
    """
    Returns list of persisted rules.
    :return:
    """
    persist_rules = []
    try:
        with open(persisted_rules_file, "r") as rule_file:
            for each_rule in rule_file:
                if each_rule[:2] in "-a,-w":
                    persist_rules.append(each_rule.rstrip('\n'))
        return persist_rules + get_list_of_persisted_control_rules()
    except Exception, e:
        raise OperationFailed('GINAUD0001E', {'error': e.message})


def get_list_of_loaded_rules():
    cmd_sc = ['auditctl', '-l']
    out, err, returncode = run_command(cmd_sc)
    if returncode == 0:
        audit_rules = out.split('\n')
        audit_rules.pop()
        if audit_rules[0] == "No rules":
            audit_rules.pop()
        return audit_rules + get_list_of_loaded_control_rules()
    else:
        raise OperationFailed('GINAUD0002E', {'name': ' '.join(cmd_sc)})


def get_list_of_loaded_control_rules():
    control_rules = []
    control_rules_dict = {'backlog_limit': '-b',
                          'enabled': '-e',
                          'failure': '-f',
                          'rate_limit': '-r'}
    cmd_cntl = ['auditctl', '-s']
    out, err, returncode = run_command(cmd_cntl)
    if returncode == 0:
        audit_status = out.split('\n')
        for each_line in audit_status:
            if each_line.split(' ')[0] in control_rules_dict:
                audit_control_rule = control_rules_dict[
                                         each_line.split(' ')[0]] + \
                                     " " + each_line.split(' ')[1]
                control_rules.append(audit_control_rule)
        return control_rules
    else:
        raise OperationFailed('GINAUD0002E', {'name': ' '.join(cmd_cntl)})


def get_list_of_persisted_control_rules():
    control_rules = []
    with open(persisted_rules_file, "r") as rule_file:
        for each_rule in rule_file:
            if each_rule[:2] in "-b,-e,-f,-r,-D":
                control_rules.append(each_rule.rstrip('\n'))
    return control_rules


class RulesModel(object):
    """
    Class to perform operation on rules.
    """
    def get_list(self):
        """
        Returns list of loaded and persisted rules.
        :return:
        """
        return merge_rules(get_list_of_loaded_rules(),
                           get_list_of_persisted_rules())

    def create(self, params):
        """
        Creates rules.
        :param params:
        :return:
        """
        try:
            gingerAuditLock.acquire()
            rule = self.construct_rules(params)
            self.load_audit_rule(rule)
            return rule
        except Exception, e:
            raise OperationFailed('GINAUD0003E', {'error': e.message})
        finally:
            gingerAuditLock.release()

    def construct_rules(self, params):
        """
        Creates file system, system rule and control rules.
        :param params: dict with rules params
        :return: the rule
        """
        try:
            rule = ''
            if params["type"] == "Filesystem Rule":
                rule = '-w'
                rule = self.construct_fs_rule(rule, params)
            elif params["type"] == "System Rule":
                rule = '-a'
                rule = self.construct_sc_rule(rule, params)
            elif params["type"] == "Control Rule":
                rule = self.construct_control_rule(params)
                self.write_to_aucontrol_rules(rule)
            return rule
        except Exception, e:
            raise OperationFailed("GINAUD0003E", {'error': e.message})

    def construct_control_rule(self, params):
        if "rule" in params:
            return params["rule"]

    def construct_fs_rule(self, rule, params):
        if "rule_info" in params:
            if "file_to_watch" in params["rule_info"]:
                rule = rule + " " + params["rule_info"]["file_to_watch"]
            if "permissions" in params["rule_info"]:
                rule = rule + " -p " + params["rule_info"]["permissions"]
            if "key" in params["rule_info"]:
                rule = rule + " -k " + params["rule_info"]["key"]
        else:
            raise MissingParameter("GINAUD0004E")
        return rule

    def construct_sc_rule(self, rule, params):
        if "rule_info" in params:
            if "action" in params["rule_info"]:
                rule = rule + " " + params["rule_info"]["action"]

            if "filter" in params["rule_info"]:
                rule = rule + ',' + params["rule_info"]["filter"]

            if "field" in params["rule_info"]:
                rule = self.construct_fields(rule, params)

            if "systemcall" in params["rule_info"]:
                rule = rule + ' -S ' + params["rule_info"]["systemcall"]

            if "key" in params["rule_info"]:
                rule = rule + " -F key=" + params["rule_info"]["key"]
        else:
            raise MissingParameter("GINAUD0004E")
        return rule

    def construct_fields(self, rule, params):
        for each_field in list(params["rule_info"]["field"]):
            rule = rule + " -F " + each_field
        return rule

    def load_audit_rule(self, rule):
        ops = rule.split(' ')
        rule_cmd = ['auditctl']
        load_cmd = rule_cmd + ops
        out, err, returncode = run_command(load_cmd)
        if returncode != 0:
            raise OperationFailed('GINAUD0022E', {'error': err})

    def write_to_audit_rules(self, rule):
        try:
            with open(persisted_rules_file, "a") as rule_file:
                rule_file.write(rule + '\n')
            rule_file.close()
        except Exception as e:
            raise OperationFailed('GINAUD0005E', {'err': e.message})

    def write_to_aucontrol_rules(self, rule):
        try:
            with open(persisted_rules_file, "a") as rule_file:
                for line in open(persisted_rules_file, "r"):
                    if line[:2] == rule[:2]:
                        RuleModel().delete_rule_line(line)
                rule_file.write(rule + '\n')
            rule_file.close()
        except Exception as e:
            raise OperationFailed('GINAUD0005E', {'err': e.message})

    @staticmethod
    def is_feature_available():
        return os.path.isdir(os.sep + audit_configpath)


class RuleModel(object):
    def __init__(self):
        self._rollback_timer = None

    def lookup(self, name):
        info = self.get_audit_rule_info(name)
        return info

    def delete(self, name):
        """
        Deletes the rules and loads them.
        :param name:
        :return:
        """
        try:
            gingerAuditLock.acquire()
            if self.is_rule_exists(name):
                self.delete_rule(name)
                wok_log.info('Rule has been deleted succesfully ' + name)
        except Exception, e:
            raise OperationFailed('GINAUD0006E', {'err': e.message})
        finally:
            gingerAuditLock.release()

    def delete_rule(self, name):
        """
        Deletes the rule from the rules file and
        reloads the rule file.
        :param name:
        :return:
        """
        self.delete_rule_line(name)
        info = self.get_audit_rule_info(name)
        if info['loaded'] == 'yes':
            self.reload_rules(name)

    def delete_rule_line(self, name):
        rule_file = open(persisted_rules_file).read()
        filter_file = open(tmp_rules_file, 'w')
        filter_file.write(rule_file)
        filter_file.close()
        rule_file = open(persisted_rules_file, 'w')
        for line in open(tmp_rules_file):
            if name not in line:
                rule_file.write(line)
            else:
                pass
        rule_file.close()
        os.remove(tmp_rules_file)

    def persist(self, name):
        try:
            gingerAuditLock.acquire()
            if not self.is_rule_exists(name):
                info = self.get_audit_rule_info(name)
                if info['persisted'] == 'no':
                    RulesModel().write_to_audit_rules(name)
            else:
                raise OperationFailed("GINAUD0020E", {"name": name})
        finally:
            gingerAuditLock.release()

    def unload(self, name):
        """
        Unloads the filesystem and system rules.
        :param name: rule name
        :return:
        """
        try:
            gingerAuditLock.acquire()
            info = self.get_audit_rule_info(name)
            if info['type'] == 'Filesystem Rule' or info['type'] \
                    == 'System Rule':
                self.reload_rules(name)
            else:
                raise OperationFailed('GINAUD0012E', {'name': name})
        except Exception:
            raise OperationFailed('GINAUD0013E', {'name': name})
        finally:
            gingerAuditLock.release()

    def reload_rules(self, name):
        rules_list = get_list_of_loaded_rules()
        unload_all_rules = ['auditctl', '-D']
        out, err, returncode = run_command(unload_all_rules)
        if returncode != 0:
            raise OperationFailed('GINAUD0002E', {'name': unload_all_rules})
        for each_rule in rules_list:
            if each_rule != str(name):
                self.load(each_rule)

    def load(self, name):
        """
        Loads a persisted rule.
        :param name: rule
        :return:
        """
        try:
            gingerAuditLock.acquire()
            info = self.get_audit_rule_info(name)
            if info['loaded'] == 'no':
                RulesModel().load_audit_rule(name)
        except Exception:
            raise OperationFailed('GINAUD0018E', {'name': name})
        finally:
            gingerAuditLock.release()

    def get_audit_rule_info(self, name):
        try:
            rule_type = self.get_auditrule_type(name)
            audit_info = {'rule': name,
                          'type': rule_type}
            self.loaded_or_persisted(audit_info, name)
            if rule_type == "Filesystem Rule":
                self.get_filesystem_rule_info(audit_info, name)
            elif rule_type == "System Rule":
                self.get_system_rule_info(audit_info, name)
            elif rule_type == "Control Rule":
                self.get_control_rule_info(audit_info, name)
            return audit_info
        except Exception, e:
            raise OperationFailed("GINAUD0007E", {"error": e.message})

    def get_control_rule_info(self, audit_info, name):
        try:
            control_rules_dict = {'-b': 'Sets the maximum amount of existing'
                                        ' Audit buffers in the kernel',
                                  '-e': 'Enables(1) and disables(0) the Audit'
                                        ' system or locks(2) its '
                                        'configuration',
                                  '-f': 'Sets the action that is performed'
                                        ' when a critical error is detected',
                                  '-r': 'Sets the rate of generated messages'
                                        ' per second,',
                                  '-D': 'Delete all rules'}
            control_info = {}
            control_info['rule_info'] = {}
            if name.split(" ")[0] != "-D":
                control_info['rule_info']['conf_value'] = name.split(" ")[1]
            control_info['rule_info']['conf_option'] = \
                name.split(" ")[0] + ": " + \
                control_rules_dict[name.split(" ")[0]]
            audit_info.update(control_info)
        except Exception, e:
            raise OperationFailed("GINAUD0007E", {"error": e.message})

    def get_system_rule_info(self, audit_info, name):
        try:
            systemcall_info = {}
            systemcall_info['rule_info'] = {}
            systemcall_info['rule_info']['key'] = \
                self.get_systemauditrule_keyname(name)
            self.get_systemcall_action_filter(systemcall_info, name)
            systemcall_info['rule_info']['systemcall'] = \
                self.get_systemauditrule_call(name)
            systemcall_info['rule_info']['field'] = \
                self.get_systemauditrule_field(name)
            audit_info.update(systemcall_info)
        except Exception, e:
            raise OperationFailed("GINAUD0008E", {"error": e.message})

    def get_filesystem_rule_info(self, audit_info, name):
        try:
            filesystemcall_info = {}
            filesystemcall_info['rule_info'] = {}
            if name.startswith("-w"):
                filesystemcall_info['rule_info']['status'] = "enable"
            if name.startswith("-W"):
                filesystemcall_info['rule_info']['status'] = "disable"
            filesystemcall_info['rule_info']['permissions'] = \
                self.get_fsauditrule_permissions(name)
            filesystemcall_info['rule_info']['key'] = \
                self.get_fsauditrule_keyname(name)
            audit_info.update(filesystemcall_info)
            filesystemcall_info['rule_info']['file_to_watch'] = \
                self.get_fsauditrule_filetowatch(name)
        except Exception, e:
            raise OperationFailed("GINAUD0009E", {"error": e.message})

    def loaded_or_persisted(self, audit_info, name):
        yes_no = {True: 'yes', False: 'no'}
        audit_info['loaded'] = yes_no[name in get_list_of_loaded_rules()]
        audit_info['persisted'] = yes_no[name in get_list_of_persisted_rules()]

    def get_systemauditrule_field(self, rule):
        regex = '[-][F]\s+(\S+)'
        return re.findall(regex, rule)

    def get_systemauditrule_call(self, rule):
        try:
            match = re.search(r'\S.\s+\w+\S\w+\s+\S.\s+\w+\S\w+\s+\S[S]\s+('
                              r'\S+)\s+\S+\s+\S+', rule)
            return match.group(1)
        except:
            return "N/A"

    def get_systemcall_action_filter(self, systemcall_info, rule):
        try:
            match = re.search(r'\-a\s*(\w+)(,)(\w+)', rule)
            if match.group(1) in action_list:
                systemcall_info['rule_info']['action'] = match.group(1)
            if match.group(3) in action_list:
                systemcall_info['rule_info']['action'] = match.group(3)
            if match.group(1) in filter_list:
                systemcall_info['rule_info']['filter'] = match.group(1)
            if match.group(3) in filter_list:
                systemcall_info['rule_info']['filter'] = match.group(3)
        except:
            return ""

    def get_auditrule_type(self, rule):
        try:
            if rule.startswith("-w"):
                rule_type = "Filesystem Rule"
            if rule.startswith("-a"):
                rule_type = "System Rule"
            if rule[:2] in "-b,-e,-f,-r,-D":
                rule_type = "Control Rule"
            return rule_type
        except IndexError:
            return ""

    def get_fsauditrule_keyname(self, rule):
        try:
            key_name = rule.split("-k", 1)[1]
            if key_name:
                return key_name.lstrip()
        except IndexError:
            return "N/A"

    def get_systemauditrule_keyname(self, rule):
        try:
            match = re.search(r'key=\s*(\w+)', rule)
            return match.group(1)
        except AttributeError:
            return "N/A"

    def get_fsauditrule_permissions(self, rule):
        try:
            match = re.search(r'\-p\s*(\w+)', rule)
            return match.group(1)
        except AttributeError:
            return "N/A"

    def get_fsauditrule_filetowatch(self, rule):
        try:
            match = re.search(r'\S+\s+(\S+)(\s+\S+)*', rule)
            return match.group(1)
        except AttributeError:
            return "N/A"

    def is_rule_exists(self, name):
        """
        Check if the rule exists in the rule file.
        :param name: rule name
        :return: boolean value
        """
        with open(persisted_rules_file) as f:
            for line in f:
                if name in line:
                    return True

    def update(self, name, params):
        """
        Modifies the rule.
        :param name: the existing rule.
        :param params: The dict of params for the new rule.
        :return: the new rule.
        """
        try:
            gingerAuditLock.acquire()
            if self.is_rule_exists(name):
                info = self.get_audit_rule_info(name)
                if info['loaded'] == 'yes':
                    RulesModel().create(params)
                rule = RulesModel().construct_rules(params)
                RulesModel().write_to_audit_rules(rule)
                wok_log.info("Deleting the existing rule %s" % name)
                self.delete_rule(name)
                wok_log.info("The rule has been modified successfully.")
                return rule
            else:
                raise MissingParameter("GINAUD0010E", {"name": name})
        except Exception:
            raise OperationFailed("GINAUD0011E", {"name": name})
        finally:
            gingerAuditLock.release()
