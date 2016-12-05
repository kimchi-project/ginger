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

ginger.loadiSCSIDetails = function() {
    ginger.initiSCSIGridData();
};

ginger.initiSCSIGridData = function() {
    $(".iSCSI-loader").show();
    ginger.getiSCSIqns(function(result) {
        ginger.iSCSITable = $("#iSCSI-table").DataTable({
            "sProcessing": true,
            "lengthMenu": [
                [10, 25, 50, -1],
                [10, 25, 50, "All"]
            ],
            data: result,
            columns: [{
                "data": "iqn"
            }, {
                "data": "status"
            }],
            columnDefs: [{
                "render": function(data, type, row) {
                    if (data) {
                        return '<span class="iSCSI-status-enable" data-toggle="tooltip" data-placement="right" title="Logged In"><i class="fa fa-sign-in"></i></span>';
                    } else {
                        return '<span class="iSCSI-status-disabled disabled"  data-toggle="tooltip" data-placement="right" title="Logged Out"><i class="fa fa-sign-out"></i></span>';
                    }
                },
                "targets": 1
            }],
            "dom": '<"row"<"col-sm-7 iSCSI-buttons"><"col-sm-5 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
            "initComplete": function(settings, json) {
                wok.initCompleteDataTableCallback(settings);
                var refreshButton = '<div class="btn-group" style="margin-left:-5px;"><button class="btn btn-primary" id="iSCSI-refresh-btn" aria-expanded="false"><i class="fa fa-refresh"></i> ' + i18n['GINIS00001M'] + '</button></div>';
                var discoverButton = '<button id="iSCSI-add" class="btn btn-primary" style="margin-left:-5px;"><i class="fa fa-plus-circle"></i> ' + i18n['GINIS00002M'] + '</button>';
                var settingsButton = '<button id="iSCSI-settings" class="btn btn-primary" style="margin-left:-5px;"><i class="fa fa-cogs"></i> ' + i18n['GINIS00003M'] + '</button>';
                var actionButton = ['<div class="btn-group" style="margin-left:-5px;">',
                    '<div class="dropdown menu-flat iSCSI-action">',
                    '<button id="iSCSI-action-btn" class="btn btn-primary dropdown-toggle disabled" type="button" data-toggle="dropdown" aria-expanded="false" aria-haspopup="true"><span class="edit-alt"></span>' + i18n['GINIS00004M'] + '<span class="caret"></span></button>',
                    '<ul class="dropdown-menu actionsheet">',
                    '<li role="presentation"><a id="iSCSI-login-btn" class="iSCSI-login  disablelink"><i class="fa fa-sign-in"></i>' + i18n['GINIS00005M'] + '</a></li>',
                    '<li role="presentation"><a id="iSCSI-logout-btn" class="iSCSI-logout disablelink"><i class="fa fa-sign-out"></i>' + i18n['GINIS00006M'] + '</a></li>',
                    '<li role="presentation"><a id="iSCSI-rescan-btn" class="iSCSI-rescan"><i class="fa fa fa-play-circle-o"></i>' + i18n['GINIS00007M'] + '</a></li>',
                    '<li role="presentation"><a id="iSCSI-auth-btn" class="iSCSI-auth disablelink"><i class="fa fa fa-cog"></i>' + i18n['GINIS00009M'] + '</a></li>',
                    '<li role="presentation" class="critical"><a id="iSCSI-remove-btn" class="iSCSI-remove"><i class="fa fa fa-times"></i>' + i18n['GINIS00008M'] + '</a></li>',
                    '</ul>',
                    '</div></div>'
                ].join('');
                $(".iSCSI-buttons").html(actionButton + ' ' + discoverButton + '  ' + settingsButton + ' ' + refreshButton);
            },
            "createdRow": function(row, data, index) {
                $(row).on('click', function() {
                    $(this).toggleClass("selected");
                });
            },
            "oLanguage": {
                "sEmptyTable": i18n['GINNET0063M'],
            }
        });

        $(".iSCSI-loader").hide();
        ginger.initiSCSIActionButtons(ginger.iSCSITable);
    }, function(err) {
        $(".iSCSI-loader").hide();
        wok.message.error(err.responseJSON.reason, '#iSCSI-alert-container');
    });
}

ginger.initiSCSIActionButtons = function(iSCSITable) {

    $('#iSCSI-refresh-btn').on('click', function() {
        $("#iSCSI-table tbody").html("");
        iSCSITable.destroy();
        ginger.initiSCSIGridData();
    });

    iSCSITable.$('tr').on('click', function() {
        ginger.iSCSItoggleButtonState(iSCSITable);
    });

    $('#iSCSI-login-btn').on('click', function() {
        ginger.loginiSCSIdevice(iSCSITable);
    });

    $('#iSCSI-logout-btn').on('click', function() {
        ginger.logoutiSCSIdevice(iSCSITable);
    });

    $('#iSCSI-remove-btn').on('click', function() {
        ginger.removeiSCSIdevice(iSCSITable);
    });

    $('#iSCSI-rescan-btn').on('click', function() {
        ginger.rescaniSCSIdevice(iSCSITable);
    });

    $('#iSCSI-settings').on('click', function() {
        wok.window.open('plugins/ginger/host-storage-iSCSI-settings.html');
    });

    $('#iSCSI-add').on('click', function() {
        wok.window.open('plugins/ginger/host-storage-iSCSI-discoverIQN.html');
    });
}

ginger.loginiSCSIdevice = function(iSCSITable) {
    var loginDevicesSelected = false;
    var logoutDevicesList = [];

    iSCSITable
        .rows(function(idx, data, node) {
            if ($(node).hasClass('selected')) {
                switch (data.status) {
                    case true:
                        loginDevicesSelected = true;
                        break;
                    case false:
                        logoutDevicesList.push(data.iqn);
                        break;
                }
            }
        });

    var DeviceList = logoutDevicesList.length;
    wok.confirm({
        title: i18n['GINIS00010M'],
        content: (loginDevicesSelected) ? i18n['GINIS00011M'] : i18n['GINIS00012M'],
        confirm: i18n['GINIS00013M'],
        cancel: i18n['GINIS00014M']
    }, function() {
        $(".iSCSI-loader").show();
        $.each(logoutDevicesList, function(key, value) {
            ginger.iSCSItargetslogin(value, function(result) {
                wok.message.success(value + ' ' + i18n['GINIS00015M'], '#iSCSI-alert-container');
                DeviceList--;
                if (DeviceList <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            }, function(err) {
                wok.message.error(err.responseJSON.reason, '#iSCSI-alert-container');
                DeviceList--;
                if (DeviceList <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            });
        });
    }, null);
}

ginger.logoutiSCSIdevice = function(iSCSITable) {
    var logoutDevicesSelected = false;
    var loginDevicesList = [];

    iSCSITable
        .rows(function(idx, data, node) {
            if ($(node).hasClass('selected')) {
                switch (data.status) {
                    case true:
                        loginDevicesList.push(data.iqn);
                        break;
                    case false:
                        logoutDevicesSelected = true;
                        break;
                }
            }
        });

    var DeviceList = loginDevicesList.length;
    wok.confirm({
        title: i18n['GINIS00016M'],
        content: (logoutDevicesSelected) ? i18n['GINIS00017M'] : i18n['GINIS00018M'],
        confirm: i18n['GINIS00019M'],
        cancel: i18n['GINIS00020M']
    }, function() {
        $(".iSCSI-loader").show();
        $.each(loginDevicesList, function(key, value) {
            ginger.iSCSItargetslogout(value, function(result) {
                wok.message.success(value + ' ' + i18n['GINIS00021M'], '#iSCSI-alert-container');
                DeviceList--;
                if (DeviceList <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            }, function(err) {
                wok.message.error(err.responseJSON.reason, '#iSCSI-alert-container');
                DeviceList--;
                if (DeviceList <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            });
        });
    }, null);
}

ginger.removeiSCSIdevice = function(iSCSITable) {
    $(".iSCSI-loader").show();
    var RowSelected = iSCSITable.rows('.selected');
    var RowSelectedLength = parseInt(RowSelected.data().length);

    wok.confirm({
        title: i18n['GINIS00022M'],
        content: i18n['GINIS00023M'],
        confirm: i18n['GINIS00024M'],
        cancel: i18n['GINIS00025M']
    }, function() {
        RowSelected.every(function() {
            var tData = this.data();
            ginger.iSCSItargetsremove(tData.iqn, function(result) {
                wok.message.success(tData.iqn + ' ' + i18n['GINIS00026M'], '#iSCSI-alert-container');
                RowSelectedLength--;
                if (RowSelectedLength <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            }, function(err) {
                wok.message.error(err.responseJSON.reason, '#iSCSI-alert-container');
                RowSelectedLength--;
                if (RowSelectedLength <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            });
        });
    }, null);
}

ginger.rescaniSCSIdevice = function(iSCSITable) {
    $(".iSCSI-loader").show();
    var RowSelected = iSCSITable.rows('.selected');
    var RowSelectedLength = parseInt(RowSelected.data().length);
    if (RowSelectedLength) {
        RowSelected.every(function() {
            var tData = this.data();
            if(tData.status){
            ginger.iSCSItargetsrescan(tData.iqn, function(result) {
                wok.message.success(tData.iqn + ' ' + i18n['GINIS00027M'], '#iSCSI-alert-container');
                RowSelectedLength--;
                if (RowSelectedLength <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            }, function(err) {
                wok.message.error(err.responseJSON.reason, '#iSCSI-alert-container');
                RowSelectedLength--;
                if (RowSelectedLength <= 0) {
                    $('#iSCSI-refresh-btn').trigger('click');
                }
            });
          }else{
            wok.message.warn(tData.iqn + ' ' + i18n['GINIS00033M'], '#iSCSI-alert-container');
            RowSelectedLength--;
            if (RowSelectedLength <= 0) {
                $('#iSCSI-refresh-btn').trigger('click');
            }
          }
        });
    }
}

ginger.initiSCSIDiscovery = function() {
    $('#iSCSI-discovery-table').css('visibility', 'hidden');

    $('#iSCSI-add-discovery-ip').on('input propertychange',function(){
        var isValid = ginger.validateIp($(this).val()) || ginger.validateHostName($(this).val());
        (isValid) ? $(this).removeClass('form-control invalid-field') : $(this).addClass('form-control invalid-field');
    });

    $('a.iSCSI-discovery').on('click', function() {
        $(".iSCSI-discovery-loader").show();
        var content = {};
        content.ip = $('#iSCSI-add-discovery-ip').val();
        content.port = $('#iSCSI-add-discovery-port').val();

        ginger.getiSCSItargets(content, function(result) {
            wok.message.success(i18n['GINIS00028M'], '#alert-iSCSI-add-iqn');
            $('#iSCSI-refresh-btn').trigger('click');
            var iSCSItargetTable = $("#iSCSI-discovery-table").DataTable({
                processing: true,
                scrollY: '40vh',
                paging: false,
                scrollCollapse: true,
                data: result,
                columns: [{
                    "data": "iqn"
                }],
                "dom": '<"row"<"col-sm-3 buttons"><"col-sm-9 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
                "initComplete": function(settings, json) {
                    wok.initCompleteDataTableCallback(settings);
                    $('#iSCSI-discovery-table').css('visibility', 'visible');
                },
                "oLanguage": {
                    "sEmptyTable": i18n['GINNET0063M']
                },
                "deferRender": true
            });
            $(".iSCSI-discovery-loader").hide();
        }, function(err) {
            $(".iSCSI-discovery-loader").hide();
            $('#iSCSI-discovery-table').css('visibility', 'hidden');
            wok.message.error(err.responseJSON.reason, '#alert-iSCSI-add-iqn');
        });
    });
}

ginger.initiSCSIsettings = function(api) {
    $(".iSCSI-settings-loader").show();
    var api = (api) ? api : 'initiator_auth';

    ginger.getiSCSIglobalAuthdetails(function(result) {
        $(".iSCSI-settings-loader").hide();

        ginger.displayiSCSIglobalsettings(result, api);
        $('#iSCSI-settings-authentication').off();
        $('#iSCSI-settings-authentication').on('change', function() {
            ginger.displayiSCSIglobalsettings(result, $(this).val());
        });

        $('#iSCSI-settings-type').on('change', function() {
            if ($(this).val() == 'None') {
                $('.iSCSI-credential').hide();
            } else {
                $('.iSCSI-credential').show();
            }
        });
        $('#iSCSI-settings-update').off();
        $('#iSCSI-settings-update').on('click', function() {
            ginger.updateiSCSIglobalsettings();
        });
    }, function(err) {
        $(".iSCSI-settings-loader").hide();
        wok.message.error(err.responseJSON.reason, '#iSCSI-settings-iqn-message');
    });
}

ginger.updateiSCSIglobalsettings = function() {
    $(".iSCSI-settings-loader").show();
    var content = {};
    content.api = $('#iSCSI-settings-authentication').val();
    content.data = {};
    content.data.auth_type = $('#iSCSI-settings-type').val();
    if(content.data.auth_type === null || content.data.auth_type === undefined){
        wok.message.error(i18n['GINIS00034M'], '#iSCSI-settings-iqn-message');
    }else{
      if (content.data.auth_type != 'None') {
          content.data.username = $('#iSCSI-settings-username').val();
          content.data.password = $('#iSCSI-settings-password').val();
      }

      ginger.iSCSIupdateSettingsDetail(content, function(result) {
          $(".iSCSI-settings-loader").hide();
          wok.message.success(i18n['GINIS00030M'], '#iSCSI-alert-container');
          $('#iSCSI-refresh-btn').trigger('click');
          $('#iSCSI-settings-close').trigger('click');
      }, function(err) {
          $(".iSCSI-settings-loader").hide();
          wok.message.error(err.responseJSON.reason, '#iSCSI-settings-iqn-message');
      });
    }
}

ginger.displayiSCSIglobalsettings = function(data, auth) {
    $('#iSCSI-settings-authentication').val(auth);
    switch (auth) {
        case 'initiator_auth':
            $('#iSCSI-settings-type').val(data['node.session.auth.authmethod']);
            $('#iSCSI-settings-username').val(data['node.session.auth.username']);
            $('#iSCSI-settings-password').val(data['node.session.auth.password']);
            break;
        case 'target_auth':
            $('#iSCSI-settings-type').val(data['node.session.auth.authmethod']);
            $('#iSCSI-settings-username').val(data['node.session.auth.username_in']);
            $('#iSCSI-settings-password').val(data['node.session.auth.password_in']);
            break;
        case 'discovery_initiator_auth':
            $('#iSCSI-settings-type').val(data['discovery.sendtargets.auth.authmethod']);
            $('#iSCSI-settings-username').val(data['discovery.sendtargets.auth.username']);
            $('#iSCSI-settings-password').val(data['discovery.sendtargets.auth.password']);
            break;
        case 'discovery_target_auth':
            $('#iSCSI-settings-type').val(data['discovery.sendtargets.auth.authmethod']);
            $('#iSCSI-settings-username').val(data['discovery.sendtargets.auth.username_in']);
            $('#iSCSI-settings-password').val(data['discovery.sendtargets.auth.password_in']);
            break;
    }
    $('#iSCSI-settings-container').css('visibility', 'visible');

    if($('#iSCSI-settings-type').val() == 'None'){
      $('.iSCSI-credential').hide();
    }else{
      $('.iSCSI-credential').show();
    }
}

ginger.displayiSCSITargetsettings = function(data, auth) {

    $('#iSCSI-target-settings-authentication').val(auth);

    switch (auth) {
        case 'initiator_auth':
            $('#iSCSI-target-settings-type').val(data['node.session.auth.authmethod']);
            $('#iSCSI-target-settings-username').val(data['node.session.auth.username']);
            $('#iSCSI-target-settings-password').val(data['node.session.auth.password']);
            break;
        case 'target_auth':
            $('#iSCSI-target-settings-type').val(data['node.session.auth.authmethod']);
            $('#iSCSI-target-settings-username').val(data['node.session.auth.username_in']);
            $('#iSCSI-target-settings-password').val(data['node.session.auth.password_in']);
            break;
        case 'discovery_initiator_auth':
            $('#iSCSI-target-settings-type').val(data['discovery.sendtargets.auth.authmethod']);
            $('#iSCSI-target-settings-username').val(data['discovery.sendtargets.auth.username']);
            $('#iSCSI-target-settings-password').val(data['discovery.sendtargets.auth.password']);
            break;
        case 'discovery_target_auth':
            $('#iSCSI-target-settings-type').val(data['discovery.sendtargets.auth.authmethod']);
            $('#iSCSI-target-settings-username').val(data['discovery.sendtargets.auth.username_in']);
            $('#iSCSI-target-settings-password').val(data['discovery.sendtargets.auth.password_in']);
            break;
    }
    $('#iSCSI-target-settings-container').css('visibility', 'visible');
    if($('#iSCSI-target-settings-type').val() == 'None'){
      $('.iSCSI-credential').hide();
    }else{
      $('.iSCSI-credential').show();
    }
}

ginger.initiSCSItargetSettings = function(api, row) {
    $('.iSCSI-target-settings-loader').show();
    var api = (api) ? api : 'initiator_auth';
    var RowSelected = (row) ? row : ginger.iSCSITable.rows('.selected');
    var RowSelectedLength = parseInt(RowSelected.data().length);
    var target = RowSelected.data()[0].iqn;
    $('#iSCSI-target-settings-target').html(target);

    ginger.getiSCSItargetSettings(target, function(result) {

        $(".iSCSI-target-settings-loader").hide();

        ginger.displayiSCSITargetsettings(result.targets[0].auth, api);
        $('#iSCSI-target-settings-authentication').off();
        $('#iSCSI-target-settings-authentication').on('change', function() {
            ginger.displayiSCSITargetsettings(result.targets[0].auth, $(this).val());
        });

        $('#iSCSI-target-settings-type').on('change', function() {
            if ($(this).val() == 'None') {
                $('.iSCSI-credential').hide();
            } else {
                $('.iSCSI-credential').show();
            }
        });
        $('#iSCSI-target-settings-update').off();
        $('#iSCSI-target-settings-update').on('click', function() {
            ginger.updateiSCSItargetsettings(target, RowSelected);
        });
    }, function(err) {
        $(".iSCSI-target-settings-loader").hide();
        wok.message.error(err.responseJSON.reason, '#iSCSI-target-settings-iqn-message');
    });
}

ginger.updateiSCSItargetsettings = function(target, RowSelected) {
    $(".iSCSI-target-settings-loader").show();
    var content = {};
    content.api = $('#iSCSI-target-settings-authentication').val();
    content.target = target;
    content.data = {};
    content.data.auth_type = $('#iSCSI-target-settings-type').val();
    if (content.data.auth_type != 'None') {
        content.data.username = $('#iSCSI-target-settings-username').val();
        content.data.password = $('#iSCSI-target-settings-password').val();
    }

    ginger.iSCSIupdateTargetsettingsDetail(content, function(result) {
        $(".iSCSI-target-settings-loader").hide();
        wok.message.success(i18n['GINIS00032M'], '#iSCSI-alert-container');
        $('#iSCSI-refresh-btn').trigger('click');
        $('#iSCSI-target-settings-close').trigger('click');
    }, function(err) {
        $(".iSCSI-target-settings-loader").hide();
        wok.message.error(err.responseJSON.reason, '#iSCSI-target-settings-iqn-message');
    });
}

ginger.iSCSItoggleButtonState = function(iSCSITable) {
    var RowSelected = iSCSITable.rows('.selected');
    var RowSelectedLength = parseInt(RowSelected.data().length);
    var loginDevicesSelected = false;
    var logoutDevicesSelected = false;

    $('#iSCSI-auth-btn').off();
    $('#iSCSI-login-btn').off();
    $('#iSCSI-logout-btn').off();

    $('#iSCSI-auth-btn').addClass('disablelink');
    $('#iSCSI-action-btn').addClass("disabled");

    if (RowSelectedLength > 0) {
        $('#iSCSI-action-btn').removeClass("disabled");
        if (RowSelectedLength == 1) {
            if (!(RowSelected.data()[0].status)) {
                $('#iSCSI-auth-btn').on('click', function() {
                    wok.window.open('plugins/ginger/host-storage-iSCSI-targetsettings.html');
                });
                $('#iSCSI-auth-btn').removeClass('disablelink');
            }
        }
    }

    iSCSITable
        .rows(function(idx, data, node) {
            if ($(node).hasClass('selected')) {
                switch (data.status) {
                    case true:
                        loginDevicesSelected = true;
                        break;
                    case false:
                        logoutDevicesSelected = true;
                        break;
                }
            }
        });

        if(loginDevicesSelected){ //if already logged in device is selected then enable logout button
            $('#iSCSI-logout-btn').removeClass('disablelink');
            $('#iSCSI-logout-btn').on('click', function() {
                ginger.logoutiSCSIdevice(iSCSITable);
            });

        }else{
            $('#iSCSI-logout-btn').addClass('disablelink');
        }

        if(logoutDevicesSelected){ //if already logged out device is selected then enable login button
            $('#iSCSI-login-btn').removeClass('disablelink');
            $('#iSCSI-login-btn').on('click', function() {
                ginger.loginiSCSIdevice(iSCSITable);
            });
        }else{
            $('#iSCSI-login-btn').addClass('disablelink');
        }
}
$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})
