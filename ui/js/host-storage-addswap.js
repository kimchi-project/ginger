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
ginger.initAddSwap = function() {

    ginger.loadSwapDeviceList();
    $("#swapType").selectpicker();
    var type = $("#swapType").val();
    var fileType = $('#AddSwap-file-container');
    var deviceType = $('#AddSwap-device-container');
    if (type == "device") {
        var opts = [];
        opts['gridId'] = "AddSwapGrid";
        fileType.hide();
        deviceType.show();
        ginger.initSwapDeviceGridData();
    };
    $("#swapType").on('change', function() {
        var type = $("#swapType").val();
        if (type == "device") {
            var opts = [];
            opts['gridId'] = "AddSwapGrid";
            fileType.hide();
            deviceType.show();
            ginger.initSwapDeviceGridData();
       } else if (type == "file") {
            deviceType.hide();
            fileType.show();
            $('#spanvalue').text('1M');
            $('#slider-id').slider({
                min: 1,
                max: 10240,
                value: 1,
                change: function(event, ui) {
                    $('#slider-value').val((ui.value).toLocaleString(wok.lang.get_locale()));
                    $('#spanvalue').text((ui.value) + 'M');
                },
            });
            $('#max-slider-value').text((10240).toLocaleString(wok.lang.get_locale()) + ' MB');
            $('#min-slider-value').text('1 MB');
          ginger.initfileswap();
        };
    });
};

ginger.initfileswap = function(){
  $("#swapname-textbox").keyup(function() {
      if (($("#swapname-textbox").val()).length == 0) {
          $("#Swap-submit").attr("disabled", true);
      } else {
          $("#Swap-submit").attr("disabled", false);
      }
  });
}
ginger.loadSwapDeviceList = function() {

    var gridFields = [];
    var opts = [];
    opts['id'] = 'AddSwap-device-container';
    opts['gridId'] = "AddSwapGrid";
    opts['multiSelection'] = false;
    opts['selection'] = true;
    opts['identifier'] = "path";
    gridFields = [{
        "column-id": 'path',
        "type": 'string',
        "identifier": true,
        "width": "50%",
        "title": i18n['GINSWP0006M']
    }, {
        "column-id": 'size',
        "type": 'numeric',
        "width": "50%",
        "converter": "number-locale-converter",
        "title": i18n['GINTITLE0004M']
    }];
    opts['gridFields'] = JSON.stringify(gridFields);
    opts['converters'] = wok.localeConverters;
    var grid = ginger.createBootgrid(opts);
    ginger.showBootgridLoading(opts);
    grid.on("loaded.rs.jquery.bootgrid", function(e) {
        $('#AddSwapGrid .select-box').hide();
    }).on("selected.rs.jquery.bootgrid", function(e) {
      var selectedRowIds = ginger.getSelectedRowsData(opts);
            if (selectedRowIds.length === 0) {
                $("#Swap-submit").attr("disabled", true);
                } else {
                  $("#Swap-submit").attr("disabled", false);
                }
    });
};

ginger.initSwapDeviceGridData = function() {
    var opts = [];
    opts['gridId'] = "AddSwapGrid";
    ginger.SwapDeviceList(function(result) {
        var filtered_results = [];
        for (i = 0; i < result.length; i++) {
            result[i]['size'] = parseInt(result[i]['size']) / 1024;
            result[i]['size'] = Number(result[i]['size'].toFixed(2));
            // Above condition tells that it is a block device and it's not partition
            if((result[i].name).startsWith("dasd") && result[i].pkname == "") {
                continue
          }
          filtered_results.push(result[i]);
        }
        ginger.loadBootgridData(opts['gridId'], filtered_results);
        ginger.showBootgridData(opts);
        ginger.hideBootgridLoading(opts);
    });
};

$("#Swap-submit").on('click', function(event) {
    var type = $("#swapType").val();
    if (type == "device") {
        var opts = [];
        opts['gridId'] = "AddSwapGrid";
        opts['identifier'] = "path";
        var selectedRowIds = ginger.getSelectedRowsData(opts);
        if (selectedRowIds.length == 0) {
            wok.message.error(i18n['GINSWP0010M'], "#swapadd-message");
        }
        if (selectedRowIds && selectedRowIds.length >= 1) {
            for (var i = 0; i < selectedRowIds.length; i++) {
                var addSwapInputData = {};
                addSwapInputData['file_loc'] = selectedRowIds[i].path;
                addSwapInputData['type'] = "device";
                ginger.addDeviceswap(addSwapInputData, function() {
                    wok.window.close();
                    ginger.initSwapDevicesGridData();
                    wok.message.success(i18n['GINSWP0007M'] + addSwapInputData.file_loc, "#swap-message")
                }, function(result) {
                    wok.window.close();
                    ginger.initSwapDevicesGridData();
                    wok.message.error(result.message, "#swap-message", true);
                });
            }
        }
    } else if (type == "file") {
        var opts = [];
        opts['gridId'] = "AddSwapGrid";
        var filename = $("#swapname-textbox").val();
        var filesize = $('#spanvalue').text();
        var fileSwapInputData = {};
        fileSwapInputData['file_loc'] = filename;
        fileSwapInputData['type'] = "file";
        fileSwapInputData['size'] = filesize;
        if ((($("#swapname-textbox").val()).length) == 0 ) {
            wok.message.error(i18n['GINSWP0009M'], "#swapadd-message");
        } else {
            ginger.addDeviceswap(fileSwapInputData, function() {
                wok.window.close();
                ginger.initSwapDevicesGridData();
                wok.message.success(i18n['GINSWP0008M'] + fileSwapInputData.file_loc, "#swap-message")
            }, function(result) {
                wok.window.close();
                ginger.initSwapDevicesGridData();
                var message = result.message ? result.message : result.responseJSON.reason;
                wok.message.error(message, "#swap-message", true);
            });
        }
    }
});
