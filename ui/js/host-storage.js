/*
 * Copyright IBM Corp, 2015-2016
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

ginger.initStorage = function() {
  $(".content-area", "#storage-section").css("height", "100%");
  ginger.getHostDetails(function(result) {
    ginger.hostarch = result["architecture"]
    ginger.loadSanAdapters();
    ginger.getPlugins(function(result) {
      if ((ginger.hostarch == "s390x") && ($.inArray("gingers390x", result) != -1)) {
        ginger.loadFcpTapeDevices();
      }
    });
  });
  ginger.loadFileSystemDetails();
  ginger.loadSwapDeviceDetails();
  ginger.loadVolumeGroupDetails();
  ginger.loadStorageDeviceDetails();
};

ginger.loadFileSystemDetails = function() {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'file-systems';
  opts['gridId'] = "fileSystemsGrid";

  gridFields = [{
    "column-id": 'filesystem',
    "type": 'string',
    "width": "20%",
    "title": i18n['GINTITLE0001M']
  }, {
    "column-id": 'mounted_on',
    "type": 'string',
    "identifier": true,
    "width": "20%",
    "title": i18n['GINTITLE0003M']
  }, {
    "column-id": 'type',
    "type": 'string',
    "width": "10%",
    "title": i18n['GINTITLE0002M']
  }, {
    "column-id": 'size',
    "type": 'string',
    "width": "10%",
    "title": i18n['GINTITLE0004M']
  }, {
    "column-id": "use%",
    "type": 'string',
    "title": i18n['GINTITLE0005M'],
    "width": "35%",
    "formatter": "percentage-used"
  }];
  opts['gridFields'] = JSON.stringify(gridFields);

  ginger.createBootgrid(opts);
  ginger.initFileSystemsGridData();
};

ginger.initFileSystemsGridData = function() {
  var opts = [];
  opts['gridId'] = "fileSystemsGrid";
  ginger.clearBootgridData(opts['gridId']);
  ginger.getFilesystems(function(result) {
    ginger.loadBootgridData(opts['gridId'], result);
  });
};

ginger.loadSwapDeviceDetails = function() {
  var gridFields = [];
  var opts = [];
  opts['id'] = 'swap-devices';
  opts['gridId'] = "swapDevicesGrid";

  gridFields = [{
    "column-id": 'filename',
    "type": 'string',
    "width": "20%",
    "title": i18n['GINTITLE0001M'],
    "identifier": true
  }, {
    "title": i18n['GINTITLE0002M'],
    "column-id": 'type',
    "width": "15%",
    "type": 'string'
  }, {
    "title": i18n['GINTITLE0006M'],
    "column-id": "size",
    "width": "10%",
    "type": 'string'
  }, {
    "title": i18n['GINTITLE0005M'],
    "column-id": "use_percent",
    "type": 'string',
    "width": "50%",
    "formatter": "percentage-used"
  }];
  opts['gridFields'] = JSON.stringify(gridFields);
  ginger.createBootgrid(opts);
  ginger.initSwapDevicesGridData();
};

ginger.initSwapDevicesGridData = function() {
  var opts = [];
  opts['gridId'] = "swapDevicesGrid";
  ginger.clearBootgridData(opts['gridId']);
  ginger.getSwapdevices(function(result) {
    for (i = 0; i < result.length; i++) {
      //calculate usage % from size and used (both are in bytes)
      result[i]['use_percent'] = (parseInt(result[i]['used']) / parseInt(result[i]['size'])) * 100;
      result[i]['use_percent'] = result[i]['use_percent'].toFixed(2) + "%";
      // convert size in bytes to readable format
      result[i]['size'] = wok.formatMeasurement(parseInt(result[i]['size']), {
        fixed: 2
      });
      result[i]['size'] = result[i]['size'].toString();
    }
    ginger.loadBootgridData(opts['gridId'], result);
  });
};

ginger.loadVolumeGroupDetails = function() {
  var gridFields = [];
  var opts = [];
  opts['id'] = 'volume-groups';
  opts['gridId'] = "volumeGroupsGrid";

  gridFields = [{
    "column-id": 'vgName',
    "type": 'string',
    "identifier": true,
    "width": "25%",
    "title": i18n['GINTITLE0001M']
  }, {
    "column-id": 'vgSize',
    "type": 'string',
    "width": "70%",
    "title": i18n['GINTITLE0006M']
  }];
  opts['gridFields'] = JSON.stringify(gridFields);

  ginger.createBootgrid(opts);
  ginger.initVolumeGroupGridData();

};

ginger.initVolumeGroupGridData = function(){
  var opts = [];
  opts['gridId'] = "volumeGroupsGrid";
  ginger.clearBootgridData(opts['gridId']);
  ginger.getVolumegroups(function(result) {
    ginger.loadBootgridData(opts['gridId'], result);
  });
};

ginger.loadSanAdapters = function() {
  var gridFields = [];
  var opts = [];
  opts['id'] = 'san-adapter-list';
  opts['gridId'] = "SanAdaptersGrid";
  if (ginger.hostarch == 's390x') {
    gridFields = [{
      "column-id": 'name',
      "type": 'string',
      "identifier": true,
      "width": "5%",
      "title": i18n['GINTITLE0001M']
    }, {
      "column-id": 'wwpn',
      "type": 'string',
      "width": "14%",
      "title": i18n['GINTITLE0007M']
    }, {
      "column-id": 'wwnn',
      "type": 'string',
      "width": "13.5%",
      "title": i18n['GINTITLE0008M']
    }, {
      "column-id": 'state',
      "type": 'string',
      "width": "4.5%",
      "title": i18n['GINTITLE0009M']
    }, {
      "column-id": 'speed',
      "type": 'string',
      "width": "4.5%",
      "title": i18n['GINTITLE0011M']
    }, {
      "column-id": 'symbolic_name',
      "type": 'string',
      "width": "58.5%",
      "title": i18n['GINTITLE0012M']
    }];
  } else {
    gridFields = [{
      "column-id": 'name',
      "type": 'string',
      "identifier": true,
      "width": "6%",
      "title": i18n['GINTITLE0001M']
    }, {
      "column-id": 'wwpn',
      "type": 'string',
      "width": "14%",
      "title": i18n['GINTITLE0007M']
    }, {
      "column-id": 'wwnn',
      "type": 'string',
      "width": "14%",
      "title": i18n['GINTITLE0008M']
    }, {
      "column-id": 'state',
      "type": 'string',
      "width": "6%",
      "title": i18n['GINTITLE0009M']
    }, {
      "column-id": 'ports_info',
      "type": 'string',
      "width": "14%",
      "title": i18n['GINTITLE0010M']
    }, {
      "column-id": 'speed',
      "type": 'string',
      "width": "6%",
      "title": i18n['GINTITLE0011M']
    }, {
      "column-id": 'symbolic_name',
      "type": 'string',
      "width": "35%",
      "title": i18n['GINTITLE0012M']
    }];
  }
  opts['gridFields'] = JSON.stringify(gridFields);
  ginger.createBootgrid(opts);
  ginger.initSanAdaterGridData();
  ginger.getPlugins(function(result){
    if ((ginger.hostarch == "s390x") && ($.inArray("gingers390x", result) != -1)) {
      var actionButtonHtml = '<div class="btn-group">' +
        '<button class="btn btn-primary" id="add-san-button" aria-expanded="false"><i class="fa fa-plus-circle"></i>' + i18n['GINTITLE0020M'] + '</button>' +
        '</div>';
      $(actionButtonHtml).appendTo('#san-adapter-add');
      }

    $('#add-san-button').on('click', function() {
      wok.window.open('plugins/gingers390x/fcpsanadapter.html');
    });
  });

};

ginger.initSanAdaterGridData = function(){
  var opts = [];
  opts['gridId'] = "SanAdaptersGrid";
  ginger.clearBootgridData(opts['gridId']);
  ginger.getSANAdapters(function(result) {
    for (i = 0; i < result.length; i++) {
      //format ports information
      result[i]['ports_info'] = result[i]['vports_inuse'] + '/' + result[i]['max_vports'];
    }
    ginger.loadBootgridData(opts['gridId'], result);
  });
};

ginger.loadFcpTapeDevices = function() {
  $("#fcp-tape-devices-panel").removeClass("hidden")
  var gridFields = [];
  var opts = [];
  opts['id'] = 'fcp-tape-devices';
  opts['gridId'] = "fcptapeDevicesGrid";
  gridFields = [{
    "column-id": 'Generic',
    "type": 'string',
    "width": "10%",
    "title": i18n['GINTITLE0013M'],
    "identifier": true
  }, {
    "title": i18n['GINTITLE0014M'],
    "column-id": 'Device',
    "width": "10%",
    "type": 'string'
  }, {
    "title": i18n['GINTITLE0015M'],
    "column-id": "Target",
    "width": "10%",
    "type": 'string'
  }, {
    "title": i18n['GINTITLE0016M'],
    "column-id": "Model",
    "type": 'string',
    "width": "20%",
  }, {
    "title": i18n['GINTITLE0002M'],
    "column-id": 'Type',
    "width": "20%",
    "type": 'string'
  }, {
    "title": i18n['GINTITLE0009M'],
    "column-id": "State",
    "width": "20%",
    "type": 'string'
  }];
  opts['gridFields'] = JSON.stringify(gridFields);
  ginger.createBootgrid(opts);
  ginger.initFcpTapeGridData();
};

ginger.initFcpTapeGridData = function() {
  var opts = [];
  opts['gridId'] = "fcptapeDevicesGrid";
  ginger.clearBootgridData(opts['gridId']);
  ginger.getFcpTapeDevices(function(result) {
    ginger.loadBootgridData(opts['gridId'], result);
  });
};

ginger.cleanModalDialog = function(){
   $(document).ready(function(){
      $('body').on('hidden.bs.modal', '.modal', function () {
         $(this).removeData('bs.modal');
         $("#" + $(this).attr("id") + " .modal-content").empty();
         $("#" + $(this).attr("id") + " .modal-content").append("Loading...");
      });
   });
}

ginger.loadStorageActionButtons = function(){
  var addButton =[
    {
        id:'sd-add-FCP-button',
        class: 'fa fa-plus-circle',
        label: 'Add FCP Device',
        onClick: function(event) {
        $('#sd-add-FCP-button').attr('href','plugins/gingers390x/addFCPLuns.html');
        $('#sd-add-FCP-button').attr('data-toggle','modal');
        $('#sd-add-FCP-button').attr('data-target','#storage-AddFCP-modal');
        ginger.cleanModalDialog();
        }
     },
    {
        id:'sd-add-ECKD-button',
        class: 'fa fa-plus-circle',
        label: 'Add ECKD Device',
        onClick: function(event) {
          wok.window.open('plugins/gingers390x/eckd.html');
        }
    },
    // {
    //     id:'sd-add-iSCSI-button',
    //     class: 'fa fa-plus-circle',
    //     label: 'Add iSCSI',
    //     onClick: function(event) {
    //     }
    // }
  ];

  var actionButton = [
    {
        id:'sd-format-button',
        class: 'fa fa-pencil-square-o',
        label: 'Format DASD',
        onClick: function(event) {
        var opts = [];
        opts['gridId'] = "stgDevGrid";
        opts['identifier'] = "id";
        opts['loadingMessage'] = 'Formatting...';

        var selectedIf = ginger.getSelectedRowsData(opts);
        if ((selectedIf && selectedIf.length > 0)){

        var settings = {

                content: i18n['GINSD00002'],
                confirm: i18n['GGBAPI6002M'],
                cancel: i18n['GGBAPI6003M']
            };

            wok.confirm(settings, function() {
                var selectedRows = ginger.getSelectedRowsData(opts);
                ginger.selectedrows = selectedRows;
                var trackingNums = selectedRows.length;
                var taskAccepted = false;
                var onTaskAccepted = function() {
                    if(taskAccepted) {
                        return;
                    }
                    taskAccepted = true;
                };
                var selectedRowDetails = JSON.stringify(ginger.selectedrows);
                ginger.showBootgridLoading(opts);
                $('#sd-format-button').hide();
                $.each(ginger.selectedrows,function(i,row){
                    var busId = row['bus_id'];
                    var deviceId = row['id'];
                    var settings = {'blk_size' : '4096'};
                    ginger.formatDASDDevice(busId, settings, function(result){
                    trackingNums = trackingNums - 1;
                    wok.message.success(deviceId + " formatted successfully",'#alert-modal-nw-container');
                    if(trackingNums == 0){
                        ginger.hideBootgridLoading(opts);
                        $('#sd-format-button').show();
                        ginger.getStgdevs(function(result){
                        ginger.loadBootgridData("stgDevGrid",result);
                        });
                    }
                    },function(result){
                    trackingNums = trackingNums - 1;
                    wok.message.error("Failed to format " + deviceId,'#alert-modal-nw-container');
                    errorMsg = i18n['GINDASD0001E'].replace("%1", deviceId);
                    wok.message.error(errorMsg,'#alert-modal-nw-container', true);
                    if(trackingNums == 0){
                        $('#sd-format-button').show();
                        ginger.hideBootgridLoading(opts);
                        ginger.getStgdevs(function(result){
                        opts['loadingMessage'] = 'Loading...';
                        ginger.showBootgridLoading(opts);
                        ginger.loadBootgridData("stgDevGrid",result);
                        });
                    }
                    }, onTaskAccepted);
               });
               }, function(){});
               }else{
                    var settings = {
                    content: i18n["GINSD00003M"],
                    confirm: i18n["GINSD00004M"]
                    };
                    wok.confirm(settings, function() {});
               }
        }
    },
    {
        id:'sd-remove-button',
        class: 'fa fa-minus-circle',
        label: 'Remove',
        critical: true,
        onClick: function(event) {
        var opts = [];
        opts['gridId'] = "stgDevGrid";
        opts['identifier'] = "id";
        var selectedIf = ginger.getSelectedRowsData(opts);
        if ((selectedIf && selectedIf.length > 0)){
            var settings = {
                content: i18n['GINSD00001'],
                confirm: i18n['GGBAPI6002M'],
                cancel: i18n['GGBAPI6003M']
            };

            wok.confirm(settings, function() {
                var selectedRows = ginger.getSelectedRowsData(opts);
                ginger.selectedrows = selectedRows;
                var rowNums = selectedRows.length;
                var selectedRowDetails = JSON.stringify(ginger.selectedrows);
                $.each(ginger.selectedrows,function(i,row){
                    var diskType = row['type'];
                    var deviceId = row['id'];
                    if (diskType == "dasd") {
                        var busId = row['bus_id'];
                        var settings = {'blk_size' : '4096'};
                        ginger.removeDASDDevice(busId, settings, function(result){
                            wok.message.success(deviceId + " removed successfully",'#alert-modal-nw-container');
                            rowNums = rowNums - 1;
                            if (rowNums == 0) {
                              ginger.getStgdevs(function(result){
                                ginger.loadBootgridData("stgDevGrid",result);
                              });
                            }
                        },function(result){
                            if (result['responseJSON']) {
                              var errText = result['responseJSON']['reason'];
                            }
                            result && wok.message.error(errText, '#alert-modal-nw-container', true);
                            rowNums = rowNums - 1;
                            if (rowNums == 0) {
                              ginger.getStgdevs(function(result){
                                ginger.loadBootgridData("stgDevGrid",result);
                              });
                            }
                        }, function(){});

                    } else if (diskType == "fc"){
                        var fcp_lun = row['fcp_lun'];
                        var wwpn = row['wwpn'];
                        var hba_id = row['hba_id'];
                        var lun_path = hba_id+":"+wwpn+":"+fcp_lun
                        var settings = {};
                        ginger.removeFCDevice(lun_path, settings, function(result){
                            wok.message.success(deviceId + " removed successfully",'#alert-modal-nw-container');
                            rowNums = rowNums - 1;
                            if (rowNums == 0) {
                              ginger.getStgdevs(function(result){
                                ginger.loadBootgridData("stgDevGrid",result);
                              });
                            }
                        },function(result){
                            wok.message.error("Failed to remove " + deviceId,'#alert-modal-nw-container');
                            rowNums = rowNums - 1;
                            if (rowNums == 0) {
                              ginger.getStgdevs(function(result){
                                ginger.loadBootgridData("stgDevGrid",result);
                              });
                            }
                        }, function(){});
                    }
               });
            }, function() {
        });
        }else{
           var settings = {
           content: i18n["GINSD00003M"],
           confirm: i18n["GINSD00004M"]
         };
           wok.confirm(settings, function() {});
       }
     }
  }];

  var addListSettings = {
      panelID : 'file-systems-add',
      buttons : addButton,
      type :'add'
  };

  var actionListSettings = {
      panelID:'file-systems-actions',
      buttons : actionButton,
      type :'action'
  };

  ginger.createActionList(addListSettings);
  ginger.getHostDetails(function(result) {
      ginger.hostarch = result["architecture"]
      ginger.getPlugins(function(result) {
      if ((ginger.hostarch == "s390x") && ($.inArray("gingers390x", result) != -1)) {
          ginger.createActionList(actionListSettings);
      }
      });
  });
};

ginger.loadStorageDeviceDetails = function(){
  var gridFields = [];
  var opts =[];
  opts['id']='stg-devs';
  opts['gridId']= "stgDevGrid";

  ginger.loadStorageActionButtons();
  gridFields = [
    {
      "column-id":'id',
      "type": 'string',
      "identifier":true,
      "width":"50%",
      "title":i18n['GINTITLE0018M']
    },
   {
      "column-id": 'mpath_count',
      "type": 'numeric',
      "width": "20%",
      "title": i18n['GINTITLE0019M']
    },
    {
      "column-id": 'type',
      "type": 'string',
      "width":"15%",
      "title": i18n['GINTITLE0002M']
    },
    {
      "column-id": 'size',
      "type": 'string',
      "width":"10%",
      "title": i18n['GINTITLE0004M']
    }
  ];

  opts['gridFields']=JSON.stringify(gridFields);
  ginger.createBootgrid(opts);
  ginger.initStorageDevicesGridData();
};

ginger.initStorageDevicesGridData = function() {
  var opts = [];
  opts['gridId'] = "stgDevGrid";
  ginger.clearBootgridData(opts['gridId']);
  ginger.getStgdevs(function(result){
    ginger.loadBootgridData(opts['gridId'],result);
  });
};
