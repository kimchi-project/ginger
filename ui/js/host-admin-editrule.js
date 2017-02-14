/*
 * Copyright IBM Corp, 2016-2017
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
        var file_to_watch = $("#filetowatch").val();
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

        if (file_to_watch.length == 0 && permissions.length == 0) {
            wok.message.error(i18n["GINAUDIT0032M"], "#editrule-message");
            return false;
        }
        if (file_to_watch.length == 0) {
            wok.message.error(i18n["GINAUDIT0075M"], "#editrule-message");
            return false;
        }
        if (permissions.length == 0) {
            wok.message.error(i18n["GINAUDIT0076M"], "#editrule-message");
            return false;
        } else {
            ginger.EditAuditRule(ruleName, editrule, function() {
                wok.window.close();
                $('#Audit-Rule-refresh-btn').trigger('click');
                wok.message.success(i18n["GINAUDIT0035M"], "#audit-message")
            }, function(result) {
                wok.message.error(result.responseJSON.reason, "#editrule-message", true);
            });
        }
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
        TRuletype = $('#t-rule-type', EditRule);
        Permission = $('#permissionID', EditRule);
        File = $('#filetowatch', EditRule);
        Key = $('#keyedit', EditRule);
        TRuletype.val(i18n['GINAUDIT0080M']);
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
    var inputValidation = function(input){
      var value  = $(input).val().replace(/[^0-9]/g,'');
      $(input).val(value);
    }
    $("#rvaluedata , #bvaluedata").on('change keyup',function(){
      inputValidation($(this));
    });
    var ruleName = ginger.loadControlRuleValues();
    $('#EditControlRule-submit').on('click', function(event) {
        var editrule = {};
        var rule_info = {};
        var val;
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
        if (val.length == 0) {
                wok.message.error(i18n["GINAUDIT0077M"], "#editrule-message");
                return false;
        } else {
        ginger.EditAuditRule(ruleName, editrule, function() {
            wok.window.close();
            $('#Audit-Rule-refresh-btn').trigger('click');
            wok.message.success(i18n["GINAUDIT0035M"], "#audit-message")
        }, function(result) {
            wok.message.error(result.responseJSON.reason, "#editrule-message", true);
        });
       }
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
        TRuletype = $('#t-rule-type', EditRule);
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
        TRuletype.val(i18n['GINAUDIT0079M']);
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
        var syscallSelected = $('#syscallsload option:selected');

        if(syscallSelected.length==0){
          wok.message.error(i18n['GINAUDIT0040M'], "#editrule-message", true);
          return false;
        }else{
          syscallSelected.each(function() {
              syscall.push($(this).text());
          });
        }

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
        var Rtype,checkkeyfield;
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
        for (var i = 0; i < ((rulearray['field'].length) - 1); i++) {
             $('#sysCalls').append('<tr><td><select name="name" class="col-md-11 col-lg-11 form-control"><option value="arch">'+i18n['GINAUDIT0041M']+'</option><option value="auid">'+i18n['GINAUDIT0042M']+'</option><option value="devmajor">'+i18n['GINAUDIT0043M']+'</option><option value="devminor">'+i18n['GINAUDIT0044M']+'</option><option value="dir">'+i18n['GINAUDIT0045M']+'</option><option value="egid">'+i18n['GINAUDIT0046M']+'</option><option value="euid">'+i18n['GINAUDIT0047M']+'</option><option value="exit">'+i18n['GINAUDIT0048M']+'</option><option value="fsgid">'+i18n['GINAUDIT0049M']+'</option><option value="fsuid">'+i18n['GINAUDIT0050M']+'</option><option value="gid">'+i18n['GINAUDIT0051M']+'</option><option value="inode">'+i18n['GINAUDIT0052M']+'</option><option value="msgtype">'+i18n['GINAUDIT0053M']+'</option><option value="obj_uid">'+i18n['GINAUDIT0054M']+'</option><option value="obj_gid">'+i18n['GINAUDIT0055M']+'</option><option value="obj_user">'+i18n['GINAUDIT0056M']+'</option><option value="obj_role">'+i18n['GINAUDIT0057M']+'</option><option value="obj_type">'+i18n['GINAUDIT0058M']+'</option><option value="obj_lev_low">'+i18n['GINAUDIT0059M']+'</option><option value="obj_lev_high">'+i18n['GINAUDIT0060M']+'</option><option value="path">'+i18n['GINAUDIT0061M']+'</option><option value="perm">'+i18n['GINAUDIT0062M']+'</option><option value="pers">'+i18n['GINAUDIT0063M']+'</option><option value="pid">'+i18n['GINAUDIT0064M']+'</option><option value="ppid">'+i18n['GINAUDIT0065M']+'</option><option value="subj_user">'+i18n['GINAUDIT0066M']+'</option><option value="subj_role">'+i18n['GINAUDIT0067M']+'</option><option value="subj_type">'+i18n['GINAUDIT0068M']+'</option><option value="subj_sen">'+i18n['GINAUDIT0069M']+'</option><option value="subj_clr">'+i18n['GINAUDIT0070M']+'</option><option value="sgid">'+i18n['GINAUDIT0071M']+'</option><option value="success">'+i18n['GINAUDIT0072M']+'</option><option value="suid">'+i18n['GINAUDIT0073M']+'</option><option value="uid">'+i18n['GINAUDIT0074M']+'</option></select></td><td><select id="fieldoperator" name="operator" class="col-md-11 col-lg-11 form-control"><option value="=">=</option><option value="!=">!=</option><option value="<"><</option><option value="<="><=</option><option value=">">></option><option value=">=">>=</option><option value="&">&</option><option value="&=">&=</option></select></td><td><input type="text" class="form-control inputbox " name="FieldValue" /></td><td><span class="valueDelete btn btn-link"><i class="fa fa-trash"></i>'+i18n['GINNET0013M']+'</span></td></tr>');
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
                if(sysfiledname.trim()!="key"){
                      sysfiledoperatorarray[i] = sysfiledoperator.trim();
                      sysfilednamearray[i] = sysfiledname.trim();
                      sysfiledvaluearray[i] = sysfiledvalue.trim();
                } else{
                  checkkeyfield = 1;
                }
            }
        }
        $('#rule-type').val("System Call Rule");
        $('#t-rule-type').val(i18n['GINAUDIT0078M']);
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
        if(sysfilednamearray.length == 0 && rulearray['field'].length == 0){
            $('#sysCalls span.valueDelete').parents('tr:first').remove();
        }
        if(checkkeyfield == 1){
            $('#sysCalls span.valueDelete').parents('tr:first').remove();
        }

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
            $('#sysCalls').append('<tr><td><select name="name" class="col-md-11 col-lg-11 form-control"><option value="arch">'+i18n['GINAUDIT0041M']+'</option><option value="auid">'+i18n['GINAUDIT0042M']+'</option><option value="devmajor">'+i18n['GINAUDIT0043M']+'</option><option value="devminor">'+i18n['GINAUDIT0044M']+'</option><option value="dir">'+i18n['GINAUDIT0045M']+'</option><option value="egid">'+i18n['GINAUDIT0046M']+'</option><option value="euid">'+i18n['GINAUDIT0047M']+'</option><option value="exit">'+i18n['GINAUDIT0048M']+'</option><option value="fsgid">'+i18n['GINAUDIT0049M']+'</option><option value="fsuid">'+i18n['GINAUDIT0050M']+'</option><option value="gid">'+i18n['GINAUDIT0051M']+'</option><option value="inode">'+i18n['GINAUDIT0052M']+'</option><option value="msgtype">'+i18n['GINAUDIT0053M']+'</option><option value="obj_uid">'+i18n['GINAUDIT0054M']+'</option><option value="obj_gid">'+i18n['GINAUDIT0055M']+'</option><option value="obj_user">'+i18n['GINAUDIT0056M']+'</option><option value="obj_role">'+i18n['GINAUDIT0057M']+'</option><option value="obj_type">'+i18n['GINAUDIT0058M']+'</option><option value="obj_lev_low">'+i18n['GINAUDIT0059M']+'</option><option value="obj_lev_high">'+i18n['GINAUDIT0060M']+'</option><option value="path">'+i18n['GINAUDIT0061M']+'</option><option value="perm">'+i18n['GINAUDIT0062M']+'</option><option value="pers">'+i18n['GINAUDIT0063M']+'</option><option value="pid">'+i18n['GINAUDIT0064M']+'</option><option value="ppid">'+i18n['GINAUDIT0065M']+'</option><option value="subj_user">'+i18n['GINAUDIT0066M']+'</option><option value="subj_role">'+i18n['GINAUDIT0067M']+'</option><option value="subj_type">'+i18n['GINAUDIT0068M']+'</option><option value="subj_sen">'+i18n['GINAUDIT0069M']+'</option><option value="subj_clr">'+i18n['GINAUDIT0070M']+'</option><option value="sgid">'+i18n['GINAUDIT0071M']+'</option><option value="success">'+i18n['GINAUDIT0072M']+'</option><option value="suid">'+i18n['GINAUDIT0073M']+'</option><option value="uid">'+i18n['GINAUDIT0074M']+'</option></select></td><td><select id="fieldoperator" name="operator" class="col-md-11 col-lg-11 form-control"><option value="=">=</option><option value="!=">!=</option><option value="<"><</option><option value="<="><=</option><option value=">">></option><option value=">=">>=</option><option value="&">&</option><option value="&=">&=</option></select></td><td><input type="text" class="form-control inputbox " name="FieldValue" /></td><td><span class="valueDelete btn btn-link"><i class="fa fa-trash"></i>'+i18n['GINNET0013M']+'</span></td></tr>');
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
