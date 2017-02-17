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
ginger.initConfigRule = function() {
        $('.selectpicker').selectpicker();

        AuditConfigTabs = $('#Audit-Config-tabs');

        local_event = $('#local_event', AuditConfigTabs);
        log_file = $('#log_file', AuditConfigTabs);
        write_logs = $('#write_logs', AuditConfigTabs);
        log_format = $('#log_format', AuditConfigTabs);
        log_group = $('#log_group', AuditConfigTabs);
        priority_boost = $('#priority_boost', AuditConfigTabs);
        flushid = $('#flushid', AuditConfigTabs);
        freq = $('#freq', AuditConfigTabs);
        nums_logs = $('#nums_logs', AuditConfigTabs);
        logfile_size = $('#logfile_size', AuditConfigTabs);
        disp_qos = $('#disp_qos', AuditConfigTabs);
        disp_path = $('#disp_path', AuditConfigTabs);
        nameformat = $('#nameformat', AuditConfigTabs);
        namefor = $('#namefor', AuditConfigTabs);
        logfilesize = $('#logfilesize', AuditConfigTabs);
        logfile_action = $('#logfile_action', AuditConfigTabs);
        action_mail_acct = $('#action_mail_acct', AuditConfigTabs);
        space_left = $('#space_left',AuditConfigTabs);
        space_left_action = $('#space_left_action', AuditConfigTabs);
        Adminspace_left = $('#Adminspace_left', AuditConfigTabs);
        Admin_spaceleft_action = $('#Admin_spaceleft_action', AuditConfigTabs);
        diskfull_action = $('#diskfull_action', AuditConfigTabs);
        diskerror_action = $('#diskerror_action', AuditConfigTabs);
        tcp_listen_port = $('#tcp_listen_port', AuditConfigTabs);
        tcp_listen_queue = $('#tcp_listen_queue', AuditConfigTabs);
        tcp_max_per_address = $('#tcp_max_per_address', AuditConfigTabs);
        use_libwrap = $('#use_libwrap', AuditConfigTabs);
        tcp_client_port = $('#tcp_client_port', AuditConfigTabs);
        tcp_client_max_idle = $('#tcp_client_max_idle', AuditConfigTabs);
        enable_krb5 = $('#enable_krb5', AuditConfigTabs);
        krb5_principle = $('#krb5_principle', AuditConfigTabs);
        krb5_key_file = $('#krb5_key_file', AuditConfigTabs);
        distribute_network = $('#distribute_network', AuditConfigTabs);

        $('#Audit-Config-general').on('change', function(){
            $("#AuditdConfig-submit").prop("disabled", false);
        });

        //get details
        ginger.retrieveConfigInfo(function suc(result) {
            ginger.populateAuditConfigGeneralTab(result);
        }, function(result) {
            if (result['responseJSON']) {
                var errText = result['responseJSON']['reason'];
            }
            result && wok.message.error(errText, '#configrule-message', true);
        });
    }
    //populate values
ginger.populateAuditConfigGeneralTab = function(interface) {
    local_event.selectpicker("val", interface.local_events);
    log_file.val(interface.log_file);
    write_logs.selectpicker("val", interface.write_logs);
    log_format.selectpicker("val", interface.log_format);
    log_group.val(interface.log_group);
    priority_boost.val(interface.priority_boost);
    flushid.selectpicker("val", interface.flush);
    freq.val(interface.freq);
    nums_logs.val(interface.num_logs);
    disp_path.val(interface.dispatcher);
    disp_qos.selectpicker("val", interface.disp_qos);
    nameformat.selectpicker("val", interface.name_format);
    namefor.val(interface.name);
    logfilesize.val(interface.max_log_file);
    logfile_action.selectpicker("val", interface.max_log_file_action);
    action_mail_acct.val(interface.action_mail_acct);
    space_left.val(interface.space_left);
    space_left_action.selectpicker("val", interface.space_left_action);
    Adminspace_left.val(interface.admin_space_left);
    Admin_spaceleft_action.selectpicker("val", interface.admin_space_left_action);
    diskfull_action.selectpicker("val", interface.disk_full_action);
    diskerror_action.selectpicker("val", interface.disk_error_action);
    tcp_listen_port.val(interface.tcp_listen_port);
    tcp_listen_queue.val(interface.tcp_listen_queue);
    tcp_max_per_address.val(interface.tcp_max_per_addr);
    use_libwrap.selectpicker("val", interface.use_libwrap);
    tcp_client_port.val(interface.tcp_client_ports);
    tcp_client_max_idle.val(interface.tcp_client_max_idle);
    enable_krb5.selectpicker("val", interface.enable_krb5);
    krb5_key_file.val(interface.krb5_key_file);
    krb5_principle.val(interface.krb5_principal);
    distribute_network.selectpicker("val", interface.distribute_network);
    $('.selectpicker').selectpicker('refresh');
};
$('#AuditdConfig-submit').on('click', function(event) {
    var configvalues = {};
    if($('#local_event').val() == null){
    configvalues['local_events'] = $('#local_event').val("");
    } else{
    configvalues['local_events'] = $('#local_event').val();
    }
    configvalues['log_file'] = $('#log_file').val();
    if($('#write_logs').val() == null){
    configvalues['write_logs'] = $('#write_logs').val("");
    } else{
    configvalues['write_logs'] = $('#write_logs').val();
    }
    if($('#log_format').val() == null){
    configvalues['log_format'] = $('#log_format').val("");
    }else{
    configvalues['log_format'] = $('#log_format').val();
    }
    configvalues['log_group'] = $('#log_group').val();
    configvalues['priority_boost'] = $('#priority_boost').val();
    if($('#flushid').val() == null){
    configvalues['flush'] = $('#flushid').val("");
    } else{
    configvalues['flush'] = $('#flushid').val();
    }
    configvalues['freq'] = $('#freq').val();
    configvalues['num_logs'] = $('#nums_logs').val();
    if($('#disp_qos').val() == null){
    configvalues['disp_qos'] = $('#disp_qos').val("");
    } else{
    configvalues['disp_qos'] = $('#disp_qos').val();
    }
    configvalues['dispatcher'] = $('#disp_path').val();
    if($('#nameformat').val() == null){
    configvalues['name_format'] = $('#nameformat').val("");
    } else{
    configvalues['name_format'] = $('#nameformat').val();
    }
    configvalues['name'] = $('#namefor').val();
    configvalues['max_log_file'] = $('#logfilesize').val();
    if($('#logfile_action').val() == null){
    configvalues['max_log_file_action'] = $('#logfile_action').val("");
    } else{
    configvalues['max_log_file_action'] = $('#logfile_action').val();
    }
    configvalues['action_mail_acct'] = $('#action_mail_acct').val();
    configvalues['space_left'] = $('#space_left').val();
    if($('#space_left_action').val() == null){
    configvalues['space_left_action'] = $('#space_left_action').val("");
    } else{
    configvalues['space_left_action'] = $('#space_left_action').val();
    }
    configvalues['admin_space_left'] = $('#Adminspace_left').val();
    if($('#Admin_spaceleft_action').val() == null){
    configvalues['admin_space_left_action'] = $('#Admin_spaceleft_action').val("");
    } else{
    configvalues['admin_space_left_action'] = $('#Admin_spaceleft_action').val();
    }
    if($('#diskfull_action').val() == null){
    configvalues['disk_full_action'] = $('#diskfull_action').val("");
    } else{
    configvalues['disk_full_action'] = $('#diskfull_action').val();
    }
    if($('#diskerror_action').val() == null){
    configvalues['disk_error_action'] = $('#diskerror_action').val("");
    } else{
    configvalues['disk_error_action'] = $('#diskerror_action').val();
    }
    configvalues['tcp_listen_port'] = $('#tcp_listen_port').val();
    configvalues['tcp_listen_queue'] = $('#tcp_listen_queue').val();
    configvalues['tcp_max_per_addr'] = $('#tcp_max_per_address').val();
    if($('#use_libwrap').val() == null){
    configvalues['use_libwrap'] = $('#use_libwrap').val("");
    } else{
    configvalues['use_libwrap'] = $('#use_libwrap').val();
    }
    configvalues['tcp_client_ports'] = $('#tcp_client_port').val();
    configvalues['tcp_client_max_idle'] = $('#tcp_client_max_idle').val();
    if($('#enable_krb5').val() == null){
    configvalues['enable_krb5'] = $('#enable_krb5').val("");
    } else{
    configvalues['enable_krb5'] = $('#enable_krb5').val();
    }
    configvalues['krb5_key_file'] = $('#krb5_key_file').val();
    configvalues['krb5_principal'] = $('#krb5_principle').val();
    if($('#distribute_network').val() == null){
    configvalues['distribute_network'] = $('#distribute_network').val("");
    } else{
    configvalues['distribute_network'] = $('#distribute_network').val();
    }
    ginger.AuditConfig(configvalues, function() {
        wok.window.close();
        $('#Audit-Rule-refresh-btn').trigger('click');
        wok.message.success(i18n["GINAUDIT0034M"], "#audit-message")
    }, function(result) {
        $('#Audit-Rule-refresh-btn').trigger('click');
        wok.message.error(result.responseJSON.reason, "#configrule-message", true);
    });
});
