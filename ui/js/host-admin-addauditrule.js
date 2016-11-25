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
ginger.initAddRule = function() {
    var type = $("#Ruletype").val();
    $('.selectpicker').selectpicker();
    $('.selectpicker').selectpicker('refresh');
    var filesystemRule = $('#AddFilesystemRule');
    var systemcallRule = $('#AddSystemcallRule');
    var controlRule = $('#AddControlRule');
    if (type == "filesystem") {
        systemcallRule.hide();
        controlRule.hide();
        filesystemRule.show();
        ginger.initfilerule();
    };
    $("#Ruletype").on('change', function() {
        var type = $("#Ruletype").val();
        if (type == "filesystem") {
            systemcallRule.hide();
            controlRule.hide();
            filesystemRule.show();
            ginger.initfilerule();
        } else if (type == "systemcall") {
            filesystemRule.hide();
            controlRule.hide();
            systemcallRule.show();
            ginger.initsyscallrule();
        } else if (type == "controlrule") {
            filesystemRule.hide();
            systemcallRule.hide();
            controlRule.show();
            $('#bvalue').show();
        }
    });
};
$("#option").on('change', function() {
    var optvalue = $("#option").val();
    if (optvalue == "-b") {
        $('#evalue').hide();
        $('#fvalue').hide();
        $('#rvalue').hide();
        $('#bvalue').show();
    } else if (optvalue == "-e") {
        $('#bvalue').hide();
        $('#fvalue').hide();
        $('#rvalue').hide();
        $('#evalue').show();
    } else if (optvalue == "-f") {
        $('#evalue').hide();
        $('#bvalue').hide();
        $('#rvalue').hide();
        $('#fvalue').show();
    } else if (optvalue == "-r") {
        $('#evalue').hide();
        $('#fvalue').hide();
        $('#bvalue').hide();
        $('#rvalue').show();
    }
    var inputValidation = function(input){
      var value  = $(input).val().replace(/[^0-9]/g,'');
      $(input).val(value);
    }
    $("#rvaluedata , #bvaluedata").on('change keyup',function(){
      inputValidation($(this));
    });
});
ginger.initfilerule = function() {
    $("#AuditRule-submit").on('click', function(event) {
        var type = $("#Ruletype").val();
        $("#Ruletype").selectpicker();
        if (type == "filesystem") {
            var file_to_watch = $("#fpath").val();
            var permissions;
            var per = $('.form-check-input');
            permissions = per.filter(':checked').map(function() {
                return this.value;
            }).get().join("");
            var key = $('#Filekeyname').val();
            var filerule = {};
            var fileruleinfo = {};
            filerule['permissions'] = permissions;
            filerule['file_to_watch'] = file_to_watch;
            filerule['key'] = key;
            fileruleinfo['type'] = "File System Rule";
            fileruleinfo['rule_info'] = filerule;
            if (file_to_watch.length == 0 && permissions.length == 0) {
                wok.message.error(i18n["GINAUDIT0032M"], "#addrule-message",true);
                return false;
            }
            if (file_to_watch.length == 0) {
               wok.message.error(i18n["GINAUDIT0075M"], "#addrule-message",true);
               return false;
            }
            if (permissions.length == 0) {
               wok.message.error(i18n["GINAUDIT0076M"], "#addrule-message",true);
               return false;
            }
            else {
                ginger.addFileAudit(fileruleinfo, function() {
                    wok.window.close();
                    $('#Audit-Rule-refresh-btn').trigger('click');
                    wok.message.success(i18n["GINAUDIT0033M"], "#audit-message")
                }, function(result) {
                    wok.message.error(result.responseJSON.reason, "#addrule-message", true);
                });
            }
        } else if (type == "controlrule") {
            var controloption = $("#option").val();
            var val;
            if (controloption == "-b") {
                val = $('#bvaluedata').val();
            } else if (controloption == "-e") {
                val = $('#evaluedata').val();
            } else if (controloption == "-f") {
                val = $('#fvaluedata').val();
            } else if (controloption == "-r") {
                val = $('#rvaluedata').val();
            }
            var result = controloption + " " + val;
            var cntrlrule = {};
            cntrlrule['type'] = "Control Rule";
            cntrlrule['rule'] = result;
            if (val.length == 0) {
                wok.message.error(i18n["GINAUDIT0077M"], "#addrule-message");
            } else {
                ginger.addControlAudit(cntrlrule, function() {
                    wok.window.close();
                    $('#Audit-Rule-refresh-btn').trigger('click');
                    wok.message.success(i18n["GINAUDIT0033M"], "#audit-message")
                }, function(result) {
                    wok.message.error(result.responseJSON.reason, "#addrule-message", true);
                });
            }
        } else if (type == "systemcall") {
            var arraydata = [];
            var field = [];
            var rule_info = {};
            var syscall = [];
            var syscalldata = {};
            var archfield = [];
            syscalldata['type'] = "System Call Rule";
            var syscallSelected = $('#syscallsload option:selected');

            if(syscallSelected.length==0){
              wok.message.error(i18n['GINAUDIT0040M'], "#addrule-message", true);
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
            ginger.addSyscallAudit(syscalldata, function() {
                wok.window.close();
                $('#Audit-Rule-refresh-btn').trigger('click');
                wok.message.success(i18n["GINAUDIT0033M"], "#audit-message");
            }, function(result) {
                wok.message.error(result.responseJSON.reason, "#addrule-message", true);
            });
        }
    });
}
ginger.initsyscallrule = function() {
    ginger.listofsyscall(function suc(result) {
        $('#syscallsload').empty();
        var syscallresult = result.syscalls;
        $.each(syscallresult, function(key, value) {
            $('#syscallsload').append($("<option></option>").attr("value", key).text(value));
        });
        $('.selectpicker').selectpicker('refresh');
    });
    $('#sysCalls span.valueDelete').on('click', function() {
        $(this).parents('tr:first').remove();
    });
    $('#sysCalls span.valueadd').on('click', function() {
        $('#sysCalls').append('<tr><td><select name="name" class="col-md-11 col-lg-11 form-control"><option value="arch">'+i18n['GINAUDIT0041M']+'</option><option value="auid">'+i18n['GINAUDIT0042M']+'</option><option value="devmajor">'+i18n['GINAUDIT0043M']+'</option><option value="devminor">'+i18n['GINAUDIT0044M']+'</option><option value="dir">'+i18n['GINAUDIT0045M']+'</option><option value="egid">'+i18n['GINAUDIT0046M']+'</option><option value="euid">'+i18n['GINAUDIT0047M']+'</option><option value="exit">'+i18n['GINAUDIT0048M']+'</option><option value="fsgid">'+i18n['GINAUDIT0049M']+'</option><option value="fsuid">'+i18n['GINAUDIT0050M']+'</option><option value="gid">'+i18n['GINAUDIT0051M']+'</option><option value="inode">'+i18n['GINAUDIT0052M']+'</option><option value="msgtype">'+i18n['GINAUDIT0053M']+'</option><option value="obj_uid">'+i18n['GINAUDIT0054M']+'</option><option value="obj_gid">'+i18n['GINAUDIT0055M']+'</option><option value="obj_user">'+i18n['GINAUDIT0056M']+'</option><option value="obj_role">'+i18n['GINAUDIT0057M']+'</option><option value="obj_type">'+i18n['GINAUDIT0058M']+'</option><option value="obj_lev_low">'+i18n['GINAUDIT0059M']+'</option><option value="obj_lev_high">'+i18n['GINAUDIT0060M']+'</option><option value="path">'+i18n['GINAUDIT0061M']+'</option><option value="perm">'+i18n['GINAUDIT0062M']+'</option><option value="pers">'+i18n['GINAUDIT0063M']+'</option><option value="pid">'+i18n['GINAUDIT0064M']+'</option><option value="ppid">'+i18n['GINAUDIT0065M']+'</option><option value="subj_user">'+i18n['GINAUDIT0066M']+'</option><option value="subj_role">'+i18n['GINAUDIT0067M']+'</option><option value="subj_type">'+i18n['GINAUDIT0068M']+'</option><option value="subj_sen">'+i18n['GINAUDIT0069M']+'</option><option value="subj_clr">'+i18n['GINAUDIT0070M']+'</option><option value="sgid">'+i18n['GINAUDIT0071M']+'</option><option value="success">'+i18n['GINAUDIT0072M']+'</option><option value="suid">'+i18n['GINAUDIT0073M']+'</option><option value="uid">'+i18n['GINAUDIT0074M']+'</option></select></td><td><select id="fieldoperator" name="operator" class="col-md-11 col-lg-11 form-control"><option value="=">=</option><option value="!=">!=</option><option value="<"><</option><option value="<="><=</option><option value=">">></option><option value=">=">>=</option><option value="&">&</option><option value="&=">&=</option></select></td><td><input type="text" class="form-control inputbox " name="FieldValue" /></td><td><span class="valueDelete btn btn-link"><i class="fa fa-trash"></i>'+i18n['GINNET0013M']+'</span></td></tr>');
        $('#sysCalls span.valueDelete').off();
        $('#sysCalls span.valueDelete').on('click', function() {
            $(this).parents('tr:first').remove();
        });
    });
}
