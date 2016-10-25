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
ginger.partition = {};
ginger.partition.PartitionDeviceInfo = {};

ginger.partition.storageInitPartition = function(opts) {

    $('#stgDevGrid').find(".common-down").on("click", function() {

        var Obj = $(this);
        var selectedRowId = Obj.data('row-id');
        opts['identifier'] = 'id';

        if (typeof ginger.partition.PartitionDeviceInfo.obj === 'undefined') {
            ginger.partition.PartitionDeviceInfo.obj = {};
        }

        if (Obj.hasClass("fa-chevron-down")) {
            if (!($.isEmptyObject(ginger.partition.PartitionDeviceInfo.obj))) {
                ginger.partition.removePartitionDetails(ginger.partition.PartitionDeviceInfo.obj);
            }
            ginger.partition.PartitionDeviceInfo = ginger.partition.getPartitionRecordDetails(opts, selectedRowId);
            ginger.partition.PartitionDeviceInfo.obj = Obj;
            ginger.partition.InitPartitionDetails(ginger.partition.PartitionDeviceInfo, Obj);
        } else {
            ginger.partition.removePartitionDetails(Obj);
        }
    });
};

ginger.partition.initCreatePartition = function(opts) {
  $('#storage-device-create-partition-btn').off();
  $('#storage-device-create-partition-btn').on('click', function() {
        opts['identifier'] = "name";
        var selectedRows = ginger.getSelectedRowsData(opts);
        ginger.partition.PartitionDeviceInfo = selectedRows[0];
        if (selectedRows && selectedRows.length === 1) {
            wok.window.open('plugins/ginger/host-storage-addpartitions.html');
        } else {
            wok.message.error(i18n['GINPT00014M'], '#alert-modal-nw-container', true);
        }
    });
}

ginger.partition.InitPartitionDetails = function(DeviceInfo, Obj) {
    ginger.partition.InitPartitionLayout(DeviceInfo, Obj);
    ginger.partition.listPartitiondetails(DeviceInfo);
};

ginger.partition.RefreshPartitionDetails = function() {

    var DeviceInfo = ginger.partition.PartitionDeviceInfo;
    $('#partition-detail-list').empty();
    $("div.column-partition-details").css('visibility', 'hidden');
    $("#partition-detail-container").css('visibility', 'hidden');
    $('#partition-loading').show();
    ginger.partition.listPartitiondetails(DeviceInfo);
};

ginger.partition.listPartitiondetails = function(DeviceInfo) {

    var DeviceName = DeviceInfo.name;
    ginger.getDevicePartition(DeviceName, function(results) {
        ginger.partition.loadPartitionData(DeviceName, results);
    }, function(error) {
        wok.message.error(error.responseJSON.reason, '#alert-partition-details', true);
        $('#partition-loading').hide();
        $("#partition-detail-container").css('visibility', 'visible');
    });
};

ginger.partition.getPartitionRecordDetails = function(opts, selectedRowId) {

    var currentRows = ginger.getCurrentRows(opts);
    var identifier = opts['identifier'];
    var finalRow = '';

    $.each(currentRows, function(i, row) {
        var rowDetails = row;
        if (selectedRowId.indexOf(rowDetails[identifier]) != -1) {
            finalRow = row;
        }
    });
    return finalRow;
};

ginger.partition.InitPartitionLayout = function(DeviceInfo, Obj) {

    var PartitionDeviceHtml = '';
    switch (DeviceInfo.type) {
        case 'dasd':
            PartitionDeviceHtml = ginger.partition.getDASDPartitionLayout(DeviceInfo);
            break;
        default:
            PartitionDeviceHtml = ginger.partition.getPartitionLayout(DeviceInfo);
            break;
    }

    if (PartitionDeviceHtml != '') {
        $(PartitionDeviceHtml).insertAfter($(Obj).closest("tr"));
        $(Obj).addClass('fa-chevron-up common-up').removeClass('fa-chevron-down common-down');
        $(Obj).closest("tr").next("tr").show("slow");
        $('#partition-loading').show();
    } else {
        wok.message.error('Device Not supported.', '#alert-modal-nw-container', true);
    }
};

ginger.partition.getPartitionLayout = function(DeviceInfo) {

    var HTMLlayout = $('#storage-device-details-tmpl').html();
    var HTMLtmpl = document.createElement('div');
    HTMLtmpl.innerHTML = HTMLlayout;

    DeviceInfo.id = (DeviceInfo.id) ? DeviceInfo.id : '';
    DeviceInfo.fcp_lun = (DeviceInfo.fcp_lun) ? DeviceInfo.fcp_lun : ginger.partition.hideColumn(HTMLtmpl, 'column-fcplun');
    DeviceInfo.wwpn = (DeviceInfo.wwpn) ? DeviceInfo.wwpn : ginger.partition.hideColumn(HTMLtmpl, 'column-wwpn');
    DeviceInfo.hba_id = (DeviceInfo.hba_id) ? DeviceInfo.hba_id : ginger.partition.hideColumn(HTMLtmpl, 'column-hbaid');

    HTMLtmpl = wok.substitute(HTMLtmpl.innerHTML, DeviceInfo);
    return HTMLtmpl;
};

ginger.partition.getDASDPartitionLayout = function(DeviceInfo) {

    DeviceInfo.id = (DeviceInfo.id) ? DeviceInfo.id : '';
    DeviceInfo.bus_id = (DeviceInfo.bus_id) ? DeviceInfo.bus_id : '';

    var HTMLtmpl = $('#storage-DASDdevice-details-tmpl').html();
    HTMLtmpl = wok.substitute(HTMLtmpl, DeviceInfo);
    return HTMLtmpl;
};

ginger.partition.loadPartitionData = function(DeviceName, result) {

    var listHtml = '';

    if (result.length > 0) {
        var partitionlistHtml = $('#storage-partition-data-tmpl').html();
        $.each(result, function(index, value) {
            var sizetoMB = Number((parseInt(value.size) / (1024 * 1024)).toFixed(2));
            var Localesize = wok.numberLocaleConverter(parseFloat(sizetoMB), wok.lang.get_locale());
            value.size = Localesize;

            listHtml += wok.substitute(partitionlistHtml, value);

        });
    } else {
        var partitionlistHtml = $('#storage-partition-nodata-tmpl').html();
        listHtml += wok.substitute(partitionlistHtml, DeviceName);
    }
    $('#partition-detail-list').html(listHtml);
    $('#partition-loading').hide();
    $("div.column-partition-details").css('visibility', 'visible');
    $("#partition-detail-container").css('visibility', 'visible');

    ginger.partition.initPartitionActions(DeviceName);
};

ginger.partition.initPartitionActions = function(DeviceName) {

    $('a.partition-delete').on('click', function() {
        var PartitionDevice = $(this).closest('li.wok-datagrid-row').attr('id');
        ginger.partition.deletePartitionDevice(PartitionDevice, DeviceName);
    });


    $('a.partition-format').on('click', function() {
        ginger.partition.PartitionDeviceInfo.formatdevice = $(this).closest('li.wok-datagrid-row').attr('id');
        wok.window.open('plugins/ginger/host-storage-formatpartitions.html');
    });

    $('a.partition-add-vg').on('click', function() {
        ginger.partition.PartitionDeviceInfo.pv_name = $(this).closest('li.wok-datagrid-row').children('span.column-path').html();
        wok.window.open('plugins/ginger/host-storage-partition-addtoVG.html');
    });

    $('a.partition-delete-vg').on('click', function() {
        var pv_name = $(this).closest('li.wok-datagrid-row').children('span.column-path').html();
        var vg = $(this).closest('li.wok-datagrid-row').children('span.column-vgname').html();

        if (vg == 'N/A') {
            wok.message.error(i18n['GINPT00013M'], '#alert-partition-details', true);
        } else {
            settings = {
                content: i18n['GINPT00001M'],
                confirm: i18n['GINPT00002M'],
                cancel: i18n['GINPT00003M']
            };
            wok.confirm(settings, function() {
                var vgcontent = {};
                vgcontent.pv_paths = {
                    "pv_paths": [pv_name]
                };
                vgcontent.vg = vg;

                ginger.PartitionDeviceRemoveFromVG(vgcontent, function(response) {
                    wok.message.success(i18n['GINPT00004M'], '#alert-partition-details');
                    $('#partition-addtovg-select').show();
                    $('#partition-addtovg-loading').hide();
                    ginger.partition.RefreshPartitionDetails();
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#alert-partition-details', true);
                });
            }, function() {});
        }
    });
};

ginger.partition.initPartitionAddButton = function() {

    var DeviceInfo = ginger.partition.PartitionDeviceInfo;
    var deviceName = DeviceInfo.name;

    $('#addpartition').on('click', function() {

        $('#partition-add-loading').show();
        var partitionSize = $('#addpartition_size').val();
        var content = {};
        content.dev_name = deviceName;
        content.size = parseInt(partitionSize);

        switch (DeviceInfo.type) {
            case 'dasd':
                ginger.partition.addDASDDevicePartition(content);
                break;
            case 'fc':
            case 'iscsi':
                content.dev_name = DeviceInfo.id;
                ginger.partition.addDevicePartition(content);
                break;
            default:
                ginger.partition.addDevicePartition(content);
                break;
        }
    });
    $('#addDeviceName').html(deviceName);

    $('#slider-id').slider({

        min: 1,
        max: ginger.partition.PartitionDeviceInfo.size,
        value: 1,
        step: 1,
        change: function(event, ui) {
            var Localesize = (ui.value).toLocaleString(wok.lang.get_locale());
            $('#slider-value').val(Localesize);
            $('#addpartition_size').val((ui.value));
        },
    });
    $('#max-slider-value').text((ginger.partition.PartitionDeviceInfo.size).toLocaleString(wok.lang.get_locale()) + ' MB');
    $('#min-slider-value').text('1 MB');
    $('#slider-value').val(1);
    $('#addpartition_size').val(1);
};

ginger.partition.addDASDDevicePartition = function(content) {

    ginger.addDASDDevicePartition(content, function(response) {
        wok.message.success(i18n['GINPT00005M'], '#alert-modal-nw-container');
        ginger.partition.RefreshPartitionDetails(content.dev_name);
        $('#partition-loading').show();
        $('#addpartition_cancel').trigger('click');
    }, function(error) {
        wok.message.error(error.responseJSON.reason, '#alert-add-partition', true);
        $('#partition-add-loading').hide();
    });
};

ginger.partition.addDevicePartition = function(content) {

    ginger.getDevicePartitionPath(content.dev_name, function(response) {
        var data = {};
        data.devname = response.path;
        data.partsize = content.size;

        ginger.addDevicePartition(data, function(response) {
            wok.message.success(i18n['GINPT00005M'], '#alert-modal-nw-container');
            ginger.partition.RefreshPartitionDetails(content.dev_name);
            $('#partition-loading').show();
            $('#addpartition_cancel').trigger('click');
        }, function(error) {
            wok.message.error(error.responseJSON.reason, '#alert-add-partition', true);
            $('#partition-add-loading').hide();
        });

    }, function(error) {
        wok.message.error(error.responseJSON.reason, '#alert-modal-nw-container', true);
        $('#partition-add-loading').hide();
    });
};

ginger.partition.initPartitionFormatButton = function() {

    var deviceName = ginger.partition.PartitionDeviceInfo.formatdevice;
    $('#formatpartition').on('click', function() {

        var fstype = $('#formatpartition_fstype').val();
        var content = {};
        content.fstype = {
            'fstype': fstype
        };
        content.deviceName = deviceName;
        var taskAccepted = false;

        var onTaskAccepted = function() {
            if (taskAccepted) {
                return;
            }
            taskAccepted = true;
        };

        $('#partition-format-select').hide();
        $('#partition-format-loading').show();

        ginger.formatPartitionDevice(content, function(response) {
            wok.message.success(i18n['GINPT00006M'], '#partition-format-alert');
            $('#partition-format-select').show();
            $('#partition-format-loading').hide();
            ginger.partition.RefreshPartitionDetails();
        }, function(error) {
            wok.message.error(error.message, '#partition-format-alert', true);
        }, onTaskAccepted);
    });
    $('#formatDeviceName').html(deviceName);
};

ginger.partition.initPartitionAddtoVGButton = function() {

    ginger.partition.initPartitionAddtoVGSelect();
    var pv_name = ginger.partition.PartitionDeviceInfo.pv_name;
    $('#partitionaddtoVG').on('click', function() {

        var vg = $('#partition_addtovg').val();
        var content = {
            'pv_name': pv_name
        };
        var taskAccepted = false;
        var onTaskAccepted = function() {
            if (taskAccepted) {
                return;
            }
            taskAccepted = true;
        };

        $('#partition-addtovg-select').hide();
        $('#partition-addtovg-loading').show();

        ginger.PartitionCreatePVs(content, function(response) {
            onTaskAccepted();
            wok.message.success(i18n['GINPT00007M'], '#partition-addtovg-alert');
            var vgcontent = {};
            vgcontent.pv_paths = {
                "pv_paths": [pv_name]
            };
            vgcontent.vg = vg;

            ginger.PartitionDeviceAddtoVG(vgcontent, function(response) {
                wok.message.success(i18n['GINPT00008M'], '#partition-addtovg-alert');
                $('#partition-addtovg-select').show();
                $('#partition-addtovg-loading').hide();
                ginger.partition.RefreshPartitionDetails();
            }, function(error) {
                wok.message.error(error.responseJSON.reason, '#partition-addtovg-alert', true);
            });

        }, function(error) {
            wok.message.error(error.message, '#partition-addtovg-alert', true);
            $('#partition-addtovg-select').show();
            $('#partition-addtovg-loading').hide();
            taskAccepted;
        }, onTaskAccepted);
    });
    $('#addtovgDeviceName').html(pv_name);
};

ginger.partition.initPartitionAddtoVGSelect = function() {
    ginger.getVolumegroups(function(result) {
        var VGList = '';
        if (result.length > 0) {
            $.each(result, function(index, value) {
                VGList += '<option>' + value.vgName + '</option>';
            });
        }
        $('#partition_addtovg').append(VGList);
    });
}

ginger.partition.removePartitionDetails = function(Obj) {
    $(Obj).addClass('fa-chevron-down common-down').removeClass('fa-chevron-up common-up');
    $(Obj).closest("tr").next("tr").hide("slow");
    $(Obj).closest('tr').next().remove();
    ginger.partition.PartitionDeviceInfo.obj = {};
};

ginger.partition.deletePartitionDevice = function(PartitionDevice, DeviceName) {

    var DeviceInfo = ginger.partition.PartitionDeviceInfo;

    switch (DeviceInfo.type) {
        case 'dasd':
            ginger.partition.deleteDASDDevicePartition(PartitionDevice, DeviceName);
            break;
        default:
            ginger.partition.deleteDevicePartition(PartitionDevice, DeviceName);
            break;
    }
};

ginger.partition.deleteDASDDevicePartition = function(PartitionDevice, DeviceName) {

  var vg = $('#' + PartitionDevice).children('span.column-vgname').html();
  var message = (vg == 'N/A' || vg == '')? i18n['GINPT00009M'] : i18n['GINPT00016M'];


    var settings = {
        content: message,
        confirm: i18n['GINPT00010M'],
        cancel: i18n['GINPT00011M']
    };
    wok.confirm(settings, function() {
        ginger.deleteDASDDevicePartition(PartitionDevice, function(response) {
            wok.message.success(PartitionDevice + i18n['GINPT00012M'], '#alert-partition-details');
            ginger.partition.RefreshPartitionDetails(DeviceName);
        }, function(error) {
            wok.message.error(error.responseJSON.reason, '#alert-partition-details', true);
        });
    }, function() {});
};

ginger.partition.deleteDevicePartition = function(PartitionDevice, DeviceName) {

  var vg = $('#' + PartitionDevice).children('span.column-vgname').html();
  var message = (vg == 'N/A' || vg == '')? i18n['GINPT00009M'] : i18n['GINPT00016M'];

    var settings = {
        content: message,
        confirm: i18n['GINPT00010M'],
        cancel: i18n['GINPT00011M']
    };
    wok.confirm(settings, function() {
        ginger.deleteDevicePartition(PartitionDevice, function(response) {
            wok.message.success(PartitionDevice + ' ' + i18n['GINPT00012M'], '#alert-partition-details');
            ginger.partition.RefreshPartitionDetails(DeviceName);
        }, function(error) {
            wok.message.error(error.responseJSON.reason, '#alert-partition-details', true);
        });
    }, function() {});
};

ginger.partition.hideColumn = function(HTMLtmpl, content) {
    $(HTMLtmpl).find("div." + content).css('display', 'none');
    return ' ';
};
