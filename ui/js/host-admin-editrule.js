/*
 * Copyright IBM Corp, 2016
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 */
ginger.initEditRule = function() {
    var ruleName = ginger.loadRuleValues();
    $('#EditRule-submit').on('click', function(event) {
        var editrule = {};
        var rule_info = {};
        var permissions;
        var per = $('.form-check-input');
        permissions = per.filter(':checked').map(function() {
            return this.value;
        }).get().join("");
        editrule['type'] = $('#rule-type').val();
        rule_info['permissions'] = permissions;
        rule_info['file_to_watch'] = $('#filetowatch').val();
        rule_info['key'] = $('#keyedit').val();
        editrule['rule_info'] = rule_info;
        ginger.EditAuditRule(ruleName, editrule, function() {
            wok.window.close();
            $('#Audit-Rule-refresh-btn').trigger('click');
            wok.message.success(i18n["GINAUDIT0035M"], "#audit-message")
        }, function(result) {
            wok.message.error(result.responseJSON.reason, "#editrule-message", true);
        });
    });
}
ginger.loadRuleValues = function() {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0030M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = {};
        var Rtype;
        var ruleName;
        $.each(selectedRowsData, function(index, value) {
            Rtype = value[1];
            selectedRows = value[6];
            ruleName = value[2];
        });
        EditRule = $('#AuditEdit');
        Ruletype = $('#rule-type', EditRule);
        Permission = $('#permissionID', EditRule);
        File = $('#filetowatch', EditRule);
        Key = $('#keyedit', EditRule);
        Ruletype.val(Rtype);
        var per = (JSON.parse(selectedRows)['permissions']);
        for (var i = 0; i < per.length; i++) {
            if (per[i] == "r") {
                $('#readp').prop('checked', true);
            } else if (per[i] == "w") {
                $('#writep').prop('checked', true);
            } else if (per[i] == "x") {
                $('#executep').prop('checked', true);
            } else if (per[i] == "a") {
                $('#changep').prop('checked', true);
            }
        }
        File.val(JSON.parse(selectedRows)['file_to_watch']);
        Key.val(JSON.parse(selectedRows)['key']);
        return ruleName;
    }
}
ginger.initEditControlRule = function() {
    $('.selectpicker').selectpicker();
    var ruleName = ginger.loadControlRuleValues();
    $('#EditControlRule-submit').on('click', function(event) {
        var editrule = {};
        var rule_info = {};
        if ($('#optionid').val() == "-b") {
            val = $('#bvaluedata').val();
        } else if ($('#optionid').val() == "-f") {
            val = $('#fvaluedata').val();
        } else if ($('#optionid').val() == "-r") {
            val = $('#rvaluedata').val();
        }
        editrule['type'] = $('#rule-type').val();
        rule = $('#optionid').val() + ' ' + val;
        editrule['rule'] = rule;
        ginger.EditAuditRule(ruleName, editrule, function() {
            wok.window.close();
            $('#Audit-Rule-refresh-btn').trigger('click');
            wok.message.success(i18n["GINAUDIT0035M"], "#audit-message")
        }, function(result) {
            wok.message.error(result.responseJSON.reason, "#editrule-message", true);
        });
    });
}
ginger.loadControlRuleValues = function() {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0030M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = {};
        var Rtype, ruleName;
        var controloption = "";
        var currentindex;
        var controlvalue = "";
        $.each(selectedRowsData, function(index, value) {
            ruleName = value[2];
            Rtype = value[1];
        });
        for (var i = 0; i < ruleName.length; i++) {
            if (ruleName[i] != " ") {
                controloption = controloption + ruleName[i];
            } else {
                currentindex = i;
                break;
            }
        }
        for (var i = currentindex; i < ruleName.length; i++) {
            controlvalue = controlvalue + ruleName[i];
        }
        EditRule = $('#AuditControl');
        Ruletype = $('#rule-type', EditRule);
        option = $('#optionid', EditRule);
        var picker = $('.selectpicker');
        if (controloption == "-b") {
            $('#bvalue').show();
            $('#optionid').val(controloption);
            picker.selectpicker("refresh");
            $('#bvaluedata').val(controlvalue.trim());
        } else if (controloption == "-f") {
            $('#fvalue').show();
            $('.selectpicker').selectpicker('refresh');
            $('#optionid').val(controloption);
            $('#fvaluedata').selectpicker("val", controlvalue.trim());
            $('.selectpicker').selectpicker('refresh');
        } else if (controloption == "-r") {
            $('#rvalue').show();
            $('#optionid').val(controloption);
            $('.selectpicker').selectpicker('refresh');
            $('#rvaluedata').val(controlvalue.trim());
        }
        Ruletype.val(Rtype);
        $('.selectpicker').selectpicker('refresh');
        return ruleName;
    }
}
ginger.initEditSyscallRule = function() {
    $('.selectpicker').selectpicker();
    ginger.listofsyscall(function suc(result) {
        $('#syscallsload').empty();
        var syscallresult = result.syscalls;
        $.each(syscallresult, function(key, value) {
            $('#syscallsload').append($("<option></option>").attr("value", value).text(value));
        });
        $('.selectpicker').selectpicker('refresh');
    });
    var ruleName = ginger.loadSystemcallRuleValues();
    $('#EditSyscallRule-submit').on('click', function(event) {
        var arraydata = [];
        var field = [];
        var rule_info = {};
        var syscall = [];
        var syscalldata = {};
        var archfield = [];
        syscalldata['type'] = "System Call Rule";
        $('#syscallsload option:selected').each(function() {
            syscall.push($(this).text());
        })
        $("#sysCalls").find('tr').each(function() {
            var val1 = $(this).find('td:eq(0) select').val();
            var val2 = $(this).find('td:eq(1) select').val();
            var val3 = $(this).find('td:eq(2) input[type="text"]').val();
            var data = val1 + val2 + val3;
            arraydata.push(data);
        });
        for (var i = 1; i < arraydata.length; i++) {
          if(arraydata[i].includes("arch")){
                      archfield.push(arraydata[i]);
          } else {
            field.push(arraydata[i]);
          }
        }
        rule_info['action'] = $('#sysaction').val();
        rule_info['filter'] = $('#sysfilter').val();
        rule_info['archfield'] = archfield;
        rule_info['systemcall'] = syscall.toString();
        rule_info['field'] = field;
        rule_info['key'] = $('#Syskeyname').val();
        syscalldata['rule_info'] = rule_info;
        ginger.EditSyscallAudit(ruleName, syscalldata, function() {
            wok.window.close();
            $('#Audit-Rule-refresh-btn').trigger('click');
            wok.message.success(i18n["GINAUDIT0035M"], "#audit-message");
        }, function(error) {
            wok.message.error(error.responseJSON.reason, "#editrule-message", true);
        });
    });
}
ginger.loadSystemcallRuleValues = function() {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0030M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = {};
        var Rtype;
        var ruleName;
        var rulearray = {};
        var rule = {};
        var array;
        var sysfiledoperatorarray = [];
        var sysfiledname;
        var sysfilednamearray = [];
        var sysfiledvaluearray = [];
        var sysfiledvalue;
        var sysfiledoperator;
        var sysycall_symbols = "=!><&";
        $.each(selectedRowsData, function(index, value) {
            rulearray = JSON.parse(value[6]);
            ruleName = value[2];
            Rtype = value[1];
        });
        array = rulearray['field'];
        for (var i = 0; i < ((rulearray['field'].length) - 2); i++) {
            $('#sysCalls').append('<tr><td><select name="name" class="col-md-11 col-lg-11 form-control"><option value="arch">architecture</option><option value="auid">audit uid</option><option value="devmajor">Device Major Number</option><option value="devminor">Device Minor Number</option><option value="dir">Directory</option><option value="egid">Effective Group ID</option><option value="euid">Effectice user ID</option><option value="exit">exit</option><option value="fsgid">Filesystem group ID</option><option value="fsuid">Filesystem user ID</option><option value="gid">Group ID</option><option value="inode">Inode Number</option><option value="key">Key</option><option value="msgtype">msgtype</option><option value="obj_uid">Objects UID</option><option value="obj_gid">Objects GID</option><option value="obj_user">Resource SE Linux User</option><option value="obj_role">Resource SE Linux Role</option><option value="obj_type">Resource SE Linux Type</option><option value="obj_lev_low">Resource SE Linux Low Level</option><option value="obj_lev_high">Resource SE Linux High Level</option><option value="path">path</option><option value="perm">permission</option><option value="pers">Personality Number</option><option value="pid">Process ID</option><option value="ppid">Parents process ID</option><option value="subj_user">Programs SE Linux User</option><option value="subj_role">Programs SE Linux Role</option><option value="subj_type">Programs SE Linux Type</option><option value="subj_sen">Programs SE Linux Sensitivity</option><option value="subj_clr">Programs SE Linux Clearance</option><option value="sgid">Saved GroupID</option><option value="success">success</option><option value="suid">Saved User ID</option><option value="uid">User ID</option></select></td><td><select id="fieldoperator" name="operator" class="col-md-11 col-lg-11 form-control"><option value="=">=</option><option value="!=">!=</option><option value="<"><</option><option value="<="><=</option><option value=">">></option><option value=">=">>=</option><option value="&">&</option><option value="&=">&=</option></select></td><td><input type="text" class="form-control inputbox " name="FieldValue" /></td><td><span class="valueDelete btn btn-link"><i class="fa fa-trash"></i> Delete</span></td></tr>');
            $('#sysCalls span.valueDelete').off();
        }
        for (i = 0; i < array.length; i++) {
            var arraylist = array[i].replace('&lt;','<').replace('&gt;','>');
            sysfiledname = '';
            sysfiledvalue = '';
            sysfiledoperator = '';
            var test = 0;
            for (j = 0; j < arraylist.length; j++) {
                if ((sysycall_symbols.indexOf(arraylist[j])) == -1) {
                    if (test == 0)
                        sysfiledname = sysfiledname + arraylist[j];
                    else {
                        sysfiledvalue = sysfiledvalue + arraylist[j];
                    }
                } else {
                    test = 1;
                    if (arraylist[j] == '=' || arraylist[j] == "!" || arraylist[j] == ">" || arraylist[j] == "<" || arraylist[j] == "&")
                        sysfiledoperator = sysfiledoperator + arraylist[j];
                }
                sysfiledoperatorarray[i] = sysfiledoperator.trim();
                sysfilednamearray[i] = sysfiledname.trim();
                sysfiledvaluearray[i] = sysfiledvalue.trim();
            }
        }
        $('#rule-type').val("System Call Rule");
        $('#sysaction').selectpicker("val", rulearray['action'].trim());
        $('#sysfilter').selectpicker("val", rulearray['filter'].trim());
        var selectrule = [];
        var finalselect = [];
        var selecttest = rulearray['systemcall'];
        selectrule = selecttest.split(",");
        for (i = 0; i < selectrule.length; i++) {
            finalselect.push(selectrule[i].trim());
        }
        i = -1;
        $("#sysCalls").find('tr').each(function() {
            var val1 = $(this).find('td:eq(0) select').val(sysfilednamearray[i]);
            var val2 = $(this).find('td:eq(1) select').val(sysfiledoperatorarray[i]);
            var val3 = $(this).find('td:eq(2) input[type="text"]').val(sysfiledvaluearray[i]);
            i++;
        });
        setTimeout(function() {
            $('#syscallsload').selectpicker("val", finalselect);
        }, 300);
        $('#Syskeyname').val(rulearray['key']);
        $('.selectpicker').selectpicker('refresh');
        $('#sysCalls span.valueadd').on('click', function() {
            $('#sysCalls').append('<tr><td><select name="name" class="col-md-7 col-lg-7 form-control"><option value="arch">architecture</option><option value="auid">audit uid</option><option value="devmajor">Device Major Number</option><option value="devminor">Device Minor Number</option><option value="dir">Directory</option><option value="egid">Effective Group ID</option><option value="euid">Effectice user ID</option><option value="exit">exit</option><option value="fsgid">Filesystem group ID</option><option value="fsuid">Filesystem user ID</option><option value="gid">Group ID</option><option value="inode">Inode Number</option><option value="key">Key</option><option value="msgtype">msgtype</option><option value="obj_uid">Objects UID</option><option value="obj_gid">Objects GID</option><option value="obj_user">Resource SE Linux User</option><option value="obj_role">Resource SE Linux Role</option><option value="obj_type">Resource SE Linux Type</option><option value="obj_lev_low">Resource SE Linux Low Level</option><option value="obj_lev_high">Resource SE Linux High Level</option><option value="path">path</option><option value="perm">permission</option><option value="pers">Personality Number</option><option value="pid">Process ID</option><option value="ppid">Parents process ID</option><option value="subj_user">Programs SE Linux User</option><option value="subj_role">Programs SE Linux Role</option><option value="subj_type">Programs SE Linux Type</option><option value="subj_sen">Programs SE Linux Sensitivity</option><option value="subj_clr">Programs SE Linux Clearance</option><option value="sgid">Saved GroupID</option><option value="success">success</option><option value="suid">Saved User ID</option><option value="uid">User ID</option></select></td><td><select id="fieldoperator" name="operator" class="col-md-7 col-lg-7 form-control"><option value="=">=</option><option value="!=">!=</option><option value="<"><</option><option value="<="><=</option><option value=">">></option><option value=">=">>=</option><option value="&">&</option><option value="&=">&=</option></select></td><td><input type="text" class="form-control inputbox " name="FieldValue" /></td><td><span class="valueDelete btn btn-link"><i class="fa fa-trash"></i> Delete</span></td></tr>');
            $('#sysCalls span.valueDelete').off();
            $('#sysCalls span.valueDelete').on('click', function() {
                $(this).parents('tr:first').remove();
            });
        });
        $('#sysCalls span.valueDelete').on('click', function() {
            $(this).parents('tr:first').remove();
        });
        return ruleName;
    }
}
