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
  ginger.loadiSCSIDetails();
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

  grid = ginger.createBootgrid(opts);
  ginger.initFileSystemsGridData();

  $('#file-systems-refresh-btn').on('click', function() {
    ginger.hideBootgridData(opts);
    ginger.showBootgridLoading(opts);
    ginger.initFileSystemsGridData();
  });

  grid.bootgrid().on("selected.rs.jquery.bootgrid", function(e, rows) {
    disabledUnmount();
  }).on("deselected.rs.jquery.bootgrid", function(e, rows) {
    disabledUnmount();
  }).on("loaded.rs.jquery.bootgrid", function(e, rows) {
    disabledUnmount();
  });

   var disabledUnmount = function(){
     var selectedRows = ginger.getSelectedRows(opts);
     if(selectedRows.length==0){
         $('#file-systems-unmount-btn').attr('disabled',true);
     }else{
         $('#file-systems-unmount-btn').attr('disabled',false);
     }
   }

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
        wok.message.success(i18n['GINFS0001M'].replace('%1',row['mounted_on']),'#file-systems-alert-container',false);
        ginger.initFileSystemsGridData();
      },function(error){
        wok.message.error(error.responseJSON.reason, '#file-systems-alert-container', true);
        ginger.initFileSystemsGridData();
      });
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
  opts['identifier'] = "filename";
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
  grid = ginger.createBootgrid(opts);
  ginger.initSwapDevicesGridData();
  ginger.changeDeleteButtonstate(grid,opts);

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
              $.each(selectedrowdata, function(key, value) {
                  var deleteSwapInputData = {};

                  deleteSwapInputData = value.filename;
                  ginger.deleteswap(deleteSwapInputData, function() {
                     ginger.initSwapDevicesGridData();
                     wok.message.success(i18n['GINSWP0005M']+' '+deleteSwapInputData, "#swap-message")
                  }, function(result) {
                      ginger.initSwapDevicesGridData();
                      wok.message.error(result.message, "#swap-message", true);
                  });
              });
          }
      }, null);
  });
};
ginger.changeDeleteButtonstate = function(grid,opts){
  grid.bootgrid().on("selected.rs.jquery.bootgrid", function(e, rows) {
    changeDeleteButtonStatus();
  }).on("deselected.rs.jquery.bootgrid", function(e, rows) {
    changeDeleteButtonStatus();
  });
}
var changeDeleteButtonStatus = function(){
  var opts = [];
  opts['gridId'] = "swapDevicesGrid";
  opts['identifier'] = "filename";
  var selectedrowdata = ginger.getSelectedRowsData(opts);
  if (selectedrowdata && selectedrowdata.length === 0) {
    $("#delete-swap-device-btn").prop("disabled", true);
  }
  else{
    $("#delete-swap-device-btn").prop("disabled", false);
  }
}
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
    var rows = "";

    if (result.length > 0) {
      $.each(result, function(index, volume){
        rows += "<tr><td>" + volume.vgName + "</td>";
        rows += "<td>" + wok.changetoProperUnit(volume.vgSize, 1) + "</td>";
        rows += "<td class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\" data-row-id=\""+volume.vgName+"\"></span> </td></tr>";
      });
    }
    $("#volume-group-table tbody").html(rows);

    var volumeGroupTable = $("#volume-group-table").DataTable({
        columnDefs: [
          {
            orderable: false,
            targets: 2
          }],
        "dom": '<"#vg-buttons.row"<"#vg-actions.col-sm-2"><"vg-buttons pull-right"><"add pull-right">><"row"<"col-sm-12 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
        "initComplete": function(settings, json) {
          wok.initCompleteDataTableCallback(settings);
          var refreshButton = '<button class="btn btn-primary pull-left" id="volume-groups-refresh-btn" aria-expanded="false"><i class="fa fa-refresh"></i> ' + i18n['GINTITLE0021M'] + '</button>';
          var addButton = '<button class="btn btn-primary" id="volume-groups-add-btn" aria-expanded="false"><i class="fa fa-plus-circle">&nbsp;</i>' + i18n['GINBG00004M']  + '</button>';
          $(".vg-buttons").html(refreshButton);
          $(".add").append(addButton).css('padding-right','3px');
          ginger.createVgActionButtons();
        },
        "oLanguage": {
          "sEmptyTable": i18n['GINNET0063M']
        }
    });

    $('#vg-buttons').css('padding-bottom','15px');

    $('#volume-groups-refresh-btn').on('click', function() {
      $("#volume-group-table tbody").html("");
      volumeGroupTable.destroy();
      ginger.initVolumeGroupGridData();
    });

    //New volume group creation handler
    $('#volume-groups-add-btn').on('click',function(event){
      ginger.vgactionmode = "add";
      wok.window.open('plugins/ginger/host-storage-vg-add.html');
    });

    //Volume group deletion handler
    $('#volume-group-delete-btn').on('click',function(event){
       if(volumeGroupTable.rows('.selected').data().length==0){
         var settings = {
           content: i18n['GINVG00037M'],
           confirm: i18n["GINNET0015M"]
          };
           wok.confirm(settings,function(){},function(){});
      }else{
       var selectedRowsData = volumeGroupTable.rows('.selected').data();
       var selectedRows = [];
          $.each(selectedRowsData,function(index,row){
            selectedRows.push(row[0]);
          });
       var settings = {
         content: i18n['GINVG0003M'].replace('%1',selectedRows),
         confirm: i18n["GINNET0015M"]
       };
       wok.confirm(settings, function(){
        $.each(selectedRows,function(index,row){
          ginger.deleteVolumeGroup(row,function(result){
           wok.message.success(i18n['GINVG0002M'].replace("%1",row), '#alert-vg-container');
           $("#volume-group-table tbody").html("");
           volumeGroupTable.destroy();
           ginger.initVolumeGroupGridData();
         },function(error){
           wok.message.error(error.responseJSON.reason, '#alert-vg-container', true);
           $('#volume-groups-refresh-btn').trigger('click');
         })
       });
     });
     }
    });

    // Add event listener for opening and closing details
    $('#volume-group-table tbody').off();
    $('#volume-group-table tbody').on('click', 'td.details-control', function () {
        //,td span.fa
        var tr = $(this).closest('tr');
        var row = volumeGroupTable.row( tr );
        var vgName = $("td:nth-child(1)",tr).text();

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
              $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
            tr.removeClass('shown');
        }else{
            // Open this row
            ginger.volumeGroupDetailsPopulation(vgName,row);
            $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
            tr.addClass('shown');
        }
    });

    //Row selection
    $('#volume-group-table tbody').on('click', 'tr', function () {
       if($(this).attr('role')=='row'){
        $(this).toggleClass("selected");
       }

        if(volumeGroupTable.rows('.selected').data().length>1){
          $('#volume-group-edit-btn').off();
          $('#volume-group-edit-btn').addClass("disablelink");
         }else{
            $('#volume-group-edit-btn').off();
            $('#volume-group-edit-btn').removeClass("disablelink");
            $('#volume-group-edit-btn').on('click',function(){
              ginger.vgResizeHandler(volumeGroupTable.rows('.selected').data());
            });
         }
    });

    $(".vg-loader").hide();
  },function(err){
    $(".vg-loader").hide();
    wok.message.error(err.responseJSON.reason, '#volume-group-alert-container');
  });
};

//Volume group buttons list
ginger.createVgActionButtons = function(){
  var actionButton = [{
    id: 'volume-group-edit-btn',
    class: 'fa fa-arrows-h',
    label: i18n['GINVG00031M']
  },
  {
    id: 'volume-group-delete-btn',
    class: 'fa fa-minus-circle',
    label: i18n['GINNET0013M'],
    critical:true,
  }];

    var actionListSettings = {
      panelID: 'vg-actions',
      buttons: actionButton,
      type: 'action'
    };
    ginger.createActionButtons(actionListSettings);
};

ginger.volumeGroupDetailsPopulation = function(volumeGroupName,row){
  var vgDetails = '';
  ginger.getVolumeGroupDetails(volumeGroupName,function(data){
    vgDetails =  ginger.populateVolumeGroupDetails(data);
    row.child('<div class="volumeGroup-details" style="display: block;"><div class="details-list">'+vgDetails+'</div></div>').show();
  },function(e){
    vgDetails = '';
  });

   return vgDetails;
};

ginger.populateVolumeGroupDetails = function(data){
    var text='';
    var value;
    var vgDetails = '';
    $.each(data, function(key, obj) {
      value = obj;
      switch (key){
       case "vgName":
          text = i18n['GINVG00010M'];
          break;
       case "vgStatus":
          text = i18n['GINVG00011M'];
          break;
       case "vgSize":
          text = i18n['GINVG00012M'];
          value = wok.changetoProperUnit(obj, 1);
          break;
       case "maxLV":
          text = i18n['GINVG00013M'];
          value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
          break;
       case "freePESize":
          text = i18n['GINVG00014M'];
          value = ginger.convertSizeToLocaleString(obj,i18n['GINVG00030M']);
          break;
       case "format":
          text = i18n['GINVG00015M'];
          break;
       case "curLV":
          text = i18n['GINVG00016M'];
          value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
          break;
        case "metadataAreas":
           text = i18n['GINVG00017M'];
           value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
           break;
        case "permission":
           text = i18n['GINVG00018M'];
           break;
        case "allocPE":
           text = i18n['GINVG00019M'];
           value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
           break;
        case "pvNames":
           text = i18n['GINVG00020M'];
           break;
        case "peSize":
           text = i18n['GINVG00021M'];
           value = ginger.convertSizeToLocaleString(obj,i18n['GINVG00030M']);
           break;
        case "systemID":
           text = i18n['GINVG00022M'];
           break;
         case "curPV":
            text = i18n['GINVG00023M'];
            value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
            break;
         case "freePE":
            text = i18n['GINVG00024M'];
            value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
            break;
         case "maxPV":
            text = i18n['GINVG00025M'];
            value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
            break;
         case "totalPE":
            text = i18n['GINVG00026M'];
            value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
            break;
         case "vgUUID":
            text = i18n['GINVG00027M'];
            break;
         case "allocPESize":
            text = i18n['GINVG00028M'];
            if (obj == 0) {
              value = ginger.convertSizeToLocaleString(parseInt(obj),i18n['GINVG00030M']);
            } else {
              value = wok.changetoProperUnit(obj, 1);
            }
            break;
          case "metadataSequenceNo":
             text = i18n['GINVG00029M'];
             value = wok.numberLocaleConverter(parseInt(obj), wok.lang.get_locale()).toString().replace(/\s/g,' ');
             break;
          default:
             text = key;
      }

  var detailsHtml = [
        '<div>',
          '<span class="column-'+key+'">',
             '<span class="header-'+key+'">'+text+'</span>',
             '<span class="row-'+key+'">'+value+'</span>',
          '</span>',
        '</div>'

   ].join('');
   vgDetails+=detailsHtml;
  });
 return vgDetails;
};

ginger.vgResizeHandler =  function(data){
  if(data.length==0){
    var settings = {
      content: i18n['GINVG00039M'],
      confirm: i18n["GINNET0015M"]
     };
      wok.confirm(settings,function(){},function(){});
 }else{
  ginger.vgactionmode = "edit";
  ginger.resizeVg = data[0];
  wok.window.open('plugins/ginger/host-storage-vg-add.html');
 }
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

  ginger.getPlugins(function(result) {
      if (ginger.hostarch != 's390x') {
        ginger.createStorageActionButtons(opts);
      }
    });

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
  ginger.partition.initCreatePartition(opts);
};

ginger.createStorageActionButtons = function(opts){
  var actionButton = [{
    id: 'storage-device-create-partition-btn',
    class: 'fa fa-plus-circle',
    label: i18n['GINPT00015M'],
    onClick: function(event) {
      opts['identifier'] = "name";
      var selectedRows = ginger.getSelectedRowsData(opts);
      ginger.partition.PartitionDeviceInfo = selectedRows[0];
      if (selectedRows && selectedRows.length === 1) {
          wok.window.open('plugins/ginger/host-storage-addpartitions.html');
      } else {
          wok.message.error(i18n['GINPT00014M'], '#alert-modal-nw-container', true);
      }
    }
  }];

    var actionListSettings = {
      panelID: 'file-systems-actions',
      buttons: actionButton,
      type: 'action'
    };
    ginger.createActionButtons(actionListSettings);
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
  opts['identifier'] = "name";
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
ginger.convertSizeToLocaleString = function(value,unit){
     var convertedString = '';
     if(value != null){
       var _toMb = Number((parseInt(value) / 1024).toFixed(2));
       convertedString = wok.numberLocaleConverter(_toMb, wok.lang.get_locale()).toString().replace(/\s/g,' ') +' '+unit;
     }
      return convertedString;
};
