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
    ginger.hostarch = result["architecture"];
    ginger.loadSanAdapters();
  });
  ginger.loadFileSystemDetails();
  ginger.loadSwapDeviceDetails();
  ginger.loadVolumeGroupDetails();
  ginger.loadStorageDeviceDetails();
};

// ******************** File Systems ********************

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
    "type": 'numeric',
    "width": "10%",
    "converter": "number-locale-converter",
    "title": i18n['GINTITLE0004M']
  }, {
    "column-id": "use%",
    "type": 'string',
    "title": i18n['GINTITLE0005M'],
    "width": "35%",
    "formatter": "percentage-used"
  }];
  opts['gridFields'] = JSON.stringify(gridFields);
  opts['converters'] = wok.localeConverters;

  ginger.createBootgrid(opts);
  ginger.initFileSystemsGridData();

  $('#file-systems-refresh-btn').on('click', function() {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initFileSystemsGridData();
  });

  $('#file-systems-unmount-btn').on('click', function(){
   var opts = [];
   opts['id'] = 'file-systems';
   opts['gridId'] = "fileSystemsGrid";
   opts['identifier'] = 'mounted_on';

    var selectedRows= ginger.getSelectedRowsData(opts);

    var settings = {
      content: i18n['GINFS0004M'],
      confirm: i18n["GINNET0015M"]
    };
    wok.confirm(settings, function(){
     $.each(selectedRows,function(index,row){
       ginger.unmountFileSystem(row['mounted_on'],function(result){
        wok.message.success(i18n['GINFS0001M'], '#file-systems-alert-container',true);
        ginger.initFileSystemsGridData();
      },function(error){
        wok.message.error(error.responseJSON.reason, '#file-systems-alert-container', true);
        ginger.initFileSystemsGridData();
      })
    });
  });

  });

  $('#file-systems-mount-btn').on('click', function(){
     wok.window.open("plugins/ginger/host-storage-fs-mount.html");
  });

};

ginger.initFileSystemsGridData = function() {
  var opts = [];
  opts['gridId'] = "fileSystemsGrid";
  ginger.getFilesystems(function(result) {
    for (i = 0; i < result.length; i++) {
      //convert string representing percent to decimal
      //to enable formatting based on locale
        result[i]['use%'] = Number(result[i]['use%'].slice(0,-1)) / 100;
      // convert size in KBs to MBs
        result[i]['size'] = parseInt(result[i]['size']) / 1024;
        result[i]['size'] = Number(result[i]['size'].toFixed(2));
    }
    ginger.loadBootgridData(opts['gridId'], result);
    ginger.showBootgridData(opts);
    ginger.hideBootgridLoading(opts);
  },function(err){
    wok.message.error(err.responseJSON.reason, '#file-systems-alert-container');
  });
};

// ******************** Swap Devices ********************

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
    "title": i18n['GINTITLE0004M'],
    "column-id": "size",
    "width": "10%",
    "converter": "number-locale-converter",
    "type": 'numeric'
  }, {
    "title": i18n['GINTITLE0005M'],
    "column-id": "use_percent",
    "type": 'numeric',
    "width": "50%",
    "formatter": "percentage-used"
  }];
  opts['gridFields'] = JSON.stringify(gridFields);
  opts['converters'] = wok.localeConverters;
  ginger.createBootgrid(opts);
  ginger.initSwapDevicesGridData();

  $('#swap-devices-refresh-btn').on('click', function() {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initSwapDevicesGridData();
  });

  $("#delete-swap-device-btn").on('click', function(event) {
      opts['gridId'] = "swapDevicesGrid";
      opts['identifier'] = "filename";
      var deleteRecord = [];
      var selectedrowdata = ginger.getSelectedRowsData(opts);
      if (selectedrowdata && selectedrowdata.length >= 1) {
          for (var i = 0; i < selectedrowdata.length; i++) {
              deleteRecord[i] = JSON.stringify(selectedrowdata[i].filename);
          }
      }
      wok.confirm({
          title: i18n['GINSWP0001M'],
          content: i18n['GINSWP0002M'] + " - " + deleteRecord,
          confirm: i18n['GINSWP0003M'],
          cancel: i18n['GINSWP0004M']
      }, function() {
          if (selectedrowdata && selectedrowdata.length >= 1) {
              for (var i = 0; i < selectedrowdata.length; i++) {
                  var deleteSwapInputData = {};
                  deleteSwapInputData = selectedrowdata[i].filename;
                  ginger.deleteswap(deleteSwapInputData, function() {
                      ginger.initSwapDevicesGridData();
                      wok.message.success(i18n['GINSWP0005M'], "#swap-message")
                  }, function(result) {
                      ginger.initSwapDevicesGridData();
                      wok.message.error(result.message, "#swap-message", true);
                  });
              }
          }
      }, null);
  });
};

ginger.initSwapDevicesGridData = function() {
  var opts = [];
  opts['gridId'] = "swapDevicesGrid";
  ginger.getSwapdevices(function(result) {
    for (i = 0; i < result.length; i++) {
      //calculate usage % from size and used (both are in bytes)
      result[i]['use_percent'] = (parseInt(result[i]['used']) / parseInt(result[i]['size']));
      //convert size in KBs to MBs
      result[i]['size'] = parseInt(result[i]['size']) / 1024;
      result[i]['size'] = Number(result[i]['size'].toFixed(2));
    }
    ginger.loadBootgridData(opts['gridId'], result);
    ginger.showBootgridData(opts);
    ginger.hideBootgridLoading(opts);
  },function(err){
    wok.message.error(err.responseJSON.reason, '#swap-devices-alert-container');
  });
};

  $('#add-swap-device-btn').click(function(){
    wok.window.open('plugins/ginger/host-storage-add-swap.html');
  });
// ******************** Volume Group ********************

ginger.loadVolumeGroupDetails = function() {
  ginger.initVolumeGroupGridData();
};

ginger.initVolumeGroupGridData = function() {
  $(".vg-loader").show();
  ginger.getVolumegroups(function(result) {

    if (result.length > 0) {
      var rows = "";
      $.each(result, function(index, volume){
        rows += "<tr><td>" + volume.vgName + "</td>";
        rows += "<td>" + wok.localeConverters["number-locale-converter"].to(Number((parseInt(volume.vgSize) / 1024).toFixed(2))) + "</td></tr>";
      });
      $("#volume-group-table tbody").html(rows);
    }

    var volumeGroupTable = $("#volume-group-table").DataTable({
        "dom": '<"row"<"col-sm-3 vg-buttons"><"col-sm-9 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
        "initComplete": function(settings, json) {
          wok.initCompleteDataTableCallback(settings);
          var refreshButton = '<button class="btn btn-primary pull-left" id="volume-groups-refresh-btn" aria-expanded="false"><i class="fa fa-refresh"></i> ' + i18n['GINTITLE0021M'] + '</button>';
          $(".vg-buttons").html(refreshButton);
        },
        "oLanguage": {
          "sEmptyTable": i18n['GINNET0063M']
        }
    });

    $('#volume-groups-refresh-btn').on('click', function() {
      $("#volume-group-table tbody").html("");
      volumeGroupTable.destroy();
      ginger.initVolumeGroupGridData();
    });
    $(".vg-loader").hide();
  },function(err){
    $(".vg-loader").hide();
    wok.message.error(err.responseJSON.reason, '#volume-group-alert-container');
  });
};

// ******************** SAN Adapters ********************

ginger.loadSanAdapters = function() {
  ginger.initSanAdaterGridData();
};

ginger.initSanAdaterGridData = function() {
  $(".sa-loading").show();
  ginger.getSANAdapters(function(result) {
    if (result.length > 0) {
      var rows = "";
      $.each(result, function(index, adapter){
        rows += "<tr><td>" + adapter.name + "</td>";
        rows += "<td>" + adapter.wwpn + "</td>";
        rows += "<td>" + adapter.wwnn + "</td>";
        rows += "<td>" + adapter.state + "</td>";
        rows += "<td>" + adapter.vports_inuse + "/" + adapter.max_vports + "</td>";
        rows += "<td>" + adapter.speed + "</td>";
        rows += "<td>" + adapter.symbolic_name + "</td>";
        rows += "<td>" + adapter.port_type + "</td></tr>";
      });
      $("#adapters-table tbody").html(rows);
    }
    var adaptersTable = $("#adapters-table").DataTable({
        "dom": '<"row"<"col-sm-3 buttons"><"col-sm-9 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
        "initComplete": function(settings, json) {
          wok.initCompleteDataTableCallback(settings);
          var refreshButton = '<button class="btn btn-primary pull-left" id="refresh-san-button" aria-expanded="false"><i class="fa fa-refresh"></i> ' + i18n['GINTITLE0021M'] + '</button>';
          $(".buttons").html(refreshButton);
        },
        "oLanguage": {
          "sEmptyTable": i18n['GINNET0063M']
        }
    });
    $('#refresh-san-button').on('click', function() {
      $("#adapters-table tbody").html("");
      adaptersTable.destroy();
      ginger.initSanAdaterGridData();
    });
    $(".sa-loading").hide();
  },function(err){
    $(".sa-loading").hide();
    wok.message.error(err.responseJSON.reason, '#san-adapter-alert-container');
  });
};

// ******************** Storage Devices ********************

ginger.cleanModalDialog = function() {
  $(document).ready(function() {
    $('body').on('hidden.bs.modal', '.modal', function() {
      $(this).removeData('bs.modal');
      $("#" + $(this).attr("id") + " .modal-content").empty();
      $("#" + $(this).attr("id") + " .modal-content").append("Loading...");
    });
  });
};

ginger.loadStorageDeviceDetails = function() {
  var gridFields = [];
  var opts = [];
  opts['id'] = 'stg-devs';
  opts['gridId'] = "stgDevGrid";

  gridFields = [{
    "column-id": 'name',
    "type": 'string',
    "identifier": true,
    "width": "50%",
    "title": i18n['GINTITLE0001M']
  }, {
    "column-id": 'mpath_count',
    "type": 'numeric',
    "width": "10%",
    "title": i18n['GINTITLE0019M']
  }, {
    "column-id": 'type',
    "type": 'string',
    "width": "15%",
    "title": i18n['GINTITLE0002M']
  }, {
    "column-id": 'size',
    "type": 'numeric',
    "width": "10%",
    "title": i18n['GINTITLE0004M'],
    "converter": "number-locale-converter"
 },{
	    "column-id": "id",
	    "type": 'string',
	    "title": i18n['GINTITLE0028M'],
	    "width": "10%",
	    "header-class": "text-center",
	    "data-class": "center",
	    "formatter": "row-details"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  opts['converters'] = wok.localeConverters;
  grid = ginger.createBootgrid(opts);
  ginger.hideBootgridData(opts);
  ginger.showBootgridLoading(opts);
  ginger.initStorageDevicesGridData();
  ginger.initStorageDevicesGridEvents(grid,opts);
  $('#storage-device-refresh-btn').on('click', function() {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initStorageDevicesGridData();
  });
  ginger.partition.initAddPartition(opts);
};

ginger.initStorageDevicesGridData = function() {
  var opts = [];
  opts['gridId'] = "stgDevGrid";
  ginger.getStgdevs(function(result) {
    ginger.loadBootgridData(opts['gridId'], result);
    ginger.hideBootgridLoading(opts);
  },function(err){
    wok.message.error(err.responseJSON.reason, '#storage-devices-alert-container');
  });
};

ginger.initStorageDevicesGridEvents = function(grid,opts) {
  grid.bootgrid().on("selected.rs.jquery.bootgrid", function(e, rows) {
    ginger.changeActionButtonsState();
  }).on("deselected.rs.jquery.bootgrid", function(e, rows) {
    ginger.changeActionButtonsState();
  }).on("loaded.rs.jquery.bootgrid", function(e, rows) {
    ginger.changeActionButtonsState();
    ginger.partition.storageInitPartition(opts);
  }).on("appended.rs.jquery.bootgrid", function(e, rows) {
     if(rows.length===0){
      ginger.showBootgridData(opts);
    }
  });
};

ginger.changeActionButtonsState = function() {
  var opts = [];
  opts['gridId'] = "stgDevGrid";
  opts['identifier'] = "id";
  var selectedRows = ginger.getSelectedRowsData(opts);

  if (selectedRows && selectedRows.length === 0) {
    ginger.disableActionsMenu('action-dropdown-button-file-systems-actions');
    $('#action-dropdown-button-file-systems-actions').prop('title', i18n["GINSD00003M"]);
  } else {
    ginger.enableActionsMenu('action-dropdown-button-file-systems-actions');
    $('#action-dropdown-button-file-systems-actions').prop('title', '');

    var dasd = false;
    $.each(ginger.getSelectedRowsData(opts), function(i, row) {
      if (row['type'] === "dasd") {
        dasd = true;
      }
    });

    ginger.changeButtonStatus(["sd-format-button"], dasd);
  }
};

ginger.selectionContainNonDasdDevices = function() {
  var opts = [];
  opts['gridId'] = "stgDevGrid";
  opts['identifier'] = "id";
  var selectedRows = ginger.getSelectedRowsData(opts);
  var result = false;

  $.each(selectedRows, function(i, row) {
    if (row['type'] !== "dasd") {
      result = true;
    }
  });

  return result;
};

ginger.disableActionsMenu = function (actionButtonId){
       $("#"+actionButtonId).parent().removeClass('open');
       $("#"+actionButtonId).prop("disabled", true);
};
ginger.enableActionsMenu = function (actionButtonId){
       $("#"+actionButtonId).parent().removeClass('open');
       $("#"+actionButtonId).prop("disabled", false);
};
