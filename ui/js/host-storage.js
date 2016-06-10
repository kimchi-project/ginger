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
    "converters": "locale_num",
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

  $('#file-systems-refresh-btn').on('click', function(event) {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initFileSystemsGridData();
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
    "title": i18n['GINTITLE0006M'],
    "column-id": "size",
    "width": "10%",
    "converters": "locale_num",
    "type": 'numeric'
  }, {
    "title": i18n['GINTITLE0005M'],
    "column-id": "use_percent",
    "type": 'numeric',
    "width": "50%",
    "formatter": "percentage-used"
  }];
  opts['gridFields'] = JSON.stringify(gridFields);
  ginger.createBootgrid(opts);
  ginger.initSwapDevicesGridData();

  $('#swap-devices-refresh-btn').on('click', function(event) {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initSwapDevicesGridData();
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
  });
};

// ******************** Volume Group ********************

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
    "type": 'numeric',
    "width": "70%",
    "converters": "locale_num",
    "title": i18n['GINTITLE0006M']
  }];
  opts['gridFields'] = JSON.stringify(gridFields);

  ginger.createBootgrid(opts);
  ginger.initVolumeGroupGridData();

  $('#volume-groups-refresh-btn').on('click', function(event) {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initVolumeGroupGridData();
  });
};

ginger.initVolumeGroupGridData = function() {
  var opts = [];
  opts['gridId'] = "volumeGroupsGrid";
  ginger.getVolumegroups(function(result) {
    for (i = 0; i < result.length; i++) {
      // convert size in bytes to Mega bytes
      result[i]['vgSize'] = parseInt(result[i]['vgSize']) / 1024;
      result[i]['vgSize'] = Number(result[i]['vgSize'].toFixed(2));
    }
    ginger.loadBootgridData(opts['gridId'], result);
    ginger.showBootgridData(opts);
    ginger.hideBootgridLoading(opts);
  });
};

// ******************** SAN Adapters ********************

ginger.loadSanAdapters = function() {
  var gridFields = [];
  var opts = [];
  opts['id'] = 'san-adapter-list';
  opts['gridId'] = "SanAdaptersGrid";
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
      "width": "10%",
      "title": i18n['GINTITLE0010M']
    }, {
      "column-id": 'speed',
      "type": 'string',
      "width": "6%",
      "title": i18n['GINTITLE0011M']
    }, {
      "column-id": 'symbolic_name',
      "type": 'string',
      "width": "25%",
      "title": i18n['GINTITLE0012M']
    }, {
      "column-id": 'port_type',
      "type": 'string',
      "width": "10%",
      "title": i18n['GINTITLE0026M']
    }];
  opts['gridFields'] = JSON.stringify(gridFields);
  ginger.createBootgrid(opts);
  ginger.initSanAdaterGridData();
    var refreshButtonHtml = '<div class="btn-group">' +
      '<button class="btn btn-primary" id="refresh-san-button" aria-expanded="false"><i class="fa fa-refresh"></i> ' + i18n['GINTITLE0021M'] + '</button>' +
      '</div>';
    $(refreshButtonHtml).appendTo('#san-adapter-refresh');

    $('#refresh-san-button').on('click', function() {
      ginger.hideBootgridData(opts);
      ginger.showBootgridLoading(opts);
      ginger.initSanAdaterGridData();
    });
};

ginger.initSanAdaterGridData = function() {
  var opts = [];
  opts['gridId'] = "SanAdaptersGrid";
  ginger.getSANAdapters(function(result) {
    for (i = 0; i < result.length; i++) {
      //format ports information
      result[i]['ports_info'] = result[i]['vports_inuse'] + '/' + result[i]['max_vports'];
      if (result[i]['port_type'] === 'virtual') {
          result[i]['ports_info'] = i18n['GINTITLE0027M'];
      }
    }
    ginger.loadBootgridData(opts['gridId'], result);
    ginger.showBootgridData(opts);
    ginger.hideBootgridLoading(opts);
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
}

ginger.loadStorageDeviceDetails = function() {
  var gridFields = [];
  var opts = [];
  opts['id'] = 'stg-devs';
  opts['gridId'] = "stgDevGrid";

  gridFields = [{
    "column-id": 'id',
    "type": 'string',
    "identifier": true,
    "width": "50%",
    "title": i18n['GINTITLE0018M']
  }, {
    "column-id": 'mpath_count',
    "type": 'numeric',
    "width": "20%",
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
    "formatter":"sizeFormatter"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  grid = ginger.createBootgrid(opts);
  ginger.hideBootgridData(opts);
  ginger.showBootgridLoading(opts);
  ginger.initStorageDevicesGridData();
  ginger.initStorageDevicesGridEvents(grid,opts);
  $('#storage-device-refresh-btn').on('click', function(event) {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initStorageDevicesGridData();
  });
};

ginger.initStorageDevicesGridData = function() {
  var opts = [];
  opts['gridId'] = "stgDevGrid";
  ginger.getStgdevs(function(result) {
    ginger.loadBootgridData(opts['gridId'], result);
    ginger.hideBootgridLoading(opts);
  });
};

ginger.initStorageDevicesGridEvents = function(grid,opts) {
  grid.bootgrid().on("selected.rs.jquery.bootgrid", function(e, rows) {
    ginger.changeActionButtonsState();
  }).on("deselected.rs.jquery.bootgrid", function(e, rows) {
    ginger.changeActionButtonsState();
  }).on("loaded.rs.jquery.bootgrid", function(e, rows) {
    ginger.changeActionButtonsState();
  }).on("appended.rs.jquery.bootgrid", function(e, rows) {
     if(rows.length==0){
      ginger.showBootgridData(opts);
    }
  });
};

ginger.changeActionButtonsState = function() {
  var opts = [];
  opts['gridId'] = "stgDevGrid";
  opts['identifier'] = "id";
  var selectedRows = ginger.getSelectedRowsData(opts);

  if (selectedRows && selectedRows.length == 0) {
    ginger.disableActionsMenu('action-dropdown-button-file-systems-actions');
    $('#action-dropdown-button-file-systems-actions').prop('title', i18n["GINSD00003M"]);
  } else {
    ginger.enableActionsMenu('action-dropdown-button-file-systems-actions');
    $('#action-dropdown-button-file-systems-actions').prop('title', '');

    var dasd = false;
    $.each(ginger.getSelectedRowsData(opts), function(i, row) {
      if (row['type'] == "dasd") {
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
    if (row['type'] != "dasd") {
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
