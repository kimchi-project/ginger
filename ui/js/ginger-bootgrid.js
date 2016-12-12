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

ginger.createBootgrid = function(opts) {
  var containerId = opts['id'];
  var gridId = opts['gridId'];
  noResults = opts['noResults'];
  var fields = JSON.parse(opts['gridFields']);
  var selection = ('selection' in opts) ? opts['selection'] : true;
  var navigation = ('navigation' in opts) ? opts['navigation'] : 3;
  var multiselection = ('multiSelection' in opts) ? opts['multiSelection'] : true;
  var converters = ('converters' in opts) ? opts['converters'] : {};

  var gridMessage = ('loadingMessage' in opts && opts['loadingMessage'].trim() && opts['loadingMessage'].length > 0) ? opts['loadingMessage'] : i18n['GINBG00001M'];
  var gridloadingHtml = ['<div id="' + gridId + '-loading" class="wok-list-loader-container wok-list-loading">',
    '<div class="wok-list-loading-icon"></div>',
    '<div class="wok-list-loading-text">' + gridMessage + '</div>',
    '</div>'
  ].join('');

  $(gridloadingHtml).appendTo('#' + containerId);

  var gridHtml = [
    '<table id="', gridId, '" class="table table-condensed table-hover table-striped" >',
    '<thead>',
    '<tr>',
    '</tr>',
    '</thead>'
  ].join('');
  $(gridHtml).appendTo('#' + containerId);
  var gridHeader = $('tr', gridHtml);

  for (var i = 0; i < fields.length; i++) {
    var columnHtml = [
      '<th data-type="', fields[i]["type"], '" data-column-id="', fields[i]["column-id"],
      '"', (fields[i].identifier) ? 'data-identifier="true"' : '',
      ("header-class" in fields[i]) ? 'data-header-css-class="gridHeader ' + fields[i]["header-class"] + '"' : 'gridHeader',
      ("data-class" in fields[i]) ? ' data-align="' + fields[i]["data-class"] + '"' + ' headerAlign="center"' : ' data-align="left" headerAlign="center"',
      ("formatter" in fields[i]) ? 'data-formatter=' + fields[i]["formatter"] : '',
      (fields[i].width) ? (' data-width="' + fields[i].width + '"') : '',
      ("converter" in fields[i]) ? 'data-converter=' + fields[i]["converter"] : '',
      '>', ("title" in fields[i]) ? fields[i]["title"] : fields[i]["column-id"],
      '</th>'
    ].join('');
    $(columnHtml).appendTo($('tr', '#' + gridId));
  }

  var grid = $('#' + gridId).bootgrid({
    selection: selection,
    multiSelect: multiselection,
    keepSelection: true,
    rowCount: -1,
    sorting: true,
    columnSelection: false,
    navigation: navigation,
    rowSelect: true,
    converters: converters,
    formatters: {
      "percentage-used": function(column, row) {
        var usage = ((row[column['id']])*100).toFixed(2);
        var iconClass='';
          if (usage <= 100 && usage >= 85) {
              iconClass = 'icon-high';
          }else if (usage <= 85 && usage >= 75 ) {
              iconClass = 'icon-med';
          } else {
              iconClass = 'icon-low';
          }
        return '<span class="column-usage"><span class="usage-icon '+iconClass+'">'+row[column['id']].toLocaleString(wok.lang.get_locale(),{style: 'percent', maximumFractionDigits:2})+'</span></span>';
      },
      "srv-status": function(column, row) {
        var value = row[column.id];
        if (column.id == "status") {
          if (value == "on" || value == "unknown"){
            return "<span class=\"server-status-enabled enabled\"> <i class=\"fa fa-power-off\"></i></span>";
          }
          return "<span class=\"server-status-disabled disabled\"> <i class=\"fa fa-power-off\"></i></span>";
        }
      },
      "nw-interface-status": function(column, row) {
        var value = row[column.id];
        if (column.id == "status") {
          if (value == "up" || value == "unknown")
            return "<span class=\"nw-interface-status-enabled enabled\"> <i class=\"fa fa-power-off\"></i></span>";
          return "<span class=\"nw-interface-status-disabled disabled\"> <i class=\"fa fa-power-off\"></i></span>";
        }
      },
      "nw-address-space": function(column, row) {
        var ipaddr = row[column.id];
        var netmask = row['netmask'];
        if (!ipaddr) {
          return "";
        }
        return ipaddr + "/" + netmask;
      },
      "editable-global-dns": function(column, row) {
        return '<span class="xedit" data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.GLOBAL + '">' + row[column.id] + '</span>	';
      },
      "editable-nw-ipv4-addresses": function(column, row) {
        return '<span class="xedit" data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.IPADDR + '">' + row[column.id] + '</span>	';
      },
      "editable-nw-ipv4-dns": function(column, row) {
        return '<span class="xedit" data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.DNS + '">' + row[column.id] + '</span>	';
      },
      "editable-nw-ipv4-routes": function(column, row) {
        return '<span class="xedit" data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.ADDRESS + '">' + row[column.id] + '</span>	';
      },
      "editable-nw-ipv6-addresses": function(column, row) {
        return '<span class="xedit" data-ipv6=true data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.IPADDR + '">' + row[column.id] + '</span>	';
      },
      "editable-nw-ipv6-dns": function(column, row) {
        return '<span class="xedit" data-ipv6=true data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.DNS + '">' + row[column.id] + '</span>	';
      },
      "editable-nw-ipv6-routes": function(column, row) {
        return '<span class="xedit" data-ipv6=true data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.ADDRESS + '">' + row[column.id] + '</span>	';
      },
      "editable-bond-member": function(column, row) {
        return '<span class="xedit" data-xedit=true data-column-name="' + column.id + '" data-row-id="' + row.member + '">' + row[column.id] + '</span>	';
      },
      "row-edit-delete": function(column, row) {
        return "<span class=\"fa fa-pencil command-edit\" data-row-id=\"" + row[column.id] + "\"></span> " +
          "<span class=\"fa fa-floppy-o command-save hidden\" data-row-id=\"" + row[column.id] + "\"></span>" +
          "<span class=\"fa fa-trash-o command-delete\" data-row-id=\"" + row[column.id] + "\"></span>";
      },
      "row-details": function(column, row) {
          if(row['status']!='n/f')
          return "<span class=\"fa fa-chevron-down common-down fa-lg\" data-row-id=\"" + row[column.id] + "\"></span> ";
        }
    },
    css: {
      iconDown: "fa fa-sort-desc",
      iconUp: "fa fa-sort-asc",
      center: "text-center"
    },
    labels: {
      search: i18n['GINBG00002M'],
      noResults: (opts['noResults']) ? opts['noResults'] : i18n['GINNET0055M'],
      infos: i18n['GINBG00005M']
    }
  }).on("loaded.rs.jquery.bootgrid", function(e) {
	    $('.input-group .glyphicon-search').removeClass('.glyphicon-search').addClass('fa fa-search');
	    if ($('#' + gridId).bootgrid('getTotalRowCount') > 0) {
	      // This need to be in if block to avoid showing no-record-found
	      ginger.showBootgridData(opts);
	    }
	  }).on("load.rs.jquery.bootgrid", function(e) {
    $('.input-group .glyphicon-search').removeClass('.glyphicon-search').addClass('fa fa-search');
  }).on("appended.rs.jquery.bootgrid", function(e, appendedRows) {
	    if ($('#' + gridId).bootgrid('getTotalRowCount') === 0 && appendedRows == 0) {
	        ginger.deselectAll(opts);
	      }
	    });
  ginger.hideBootgridLoading(opts);
  return grid;
}

ginger.loadBootgridData = function(gridId, data) {
  ginger.clearBootgridData(gridId);
  ginger.appendBootgridData(gridId, data);
};

ginger.deselectAll = function(opts) {
	  $('#' + opts['gridId']).bootgrid("deselect");
	  $('#' + opts['gridId'] + ' input.select-box').attr('checked', false);
	};

ginger.clearBootgridData = function(gridId) {
  $('#' + gridId).bootgrid("clear");
};

ginger.appendBootgridData = function(gridId, data) {
  $('#' + gridId).bootgrid("append", data);
};

ginger.getSelectedRowsData = function(opts) {
  var selectedRowDetails = [];
  var currentRows = ginger.getCurrentRows(opts);
  var selectedRowIds = ginger.getSelectedRows(opts);
  var identifier = opts['identifier'];
  $.each(currentRows, function(i, row) {
    var rowDetails = row;
    if (selectedRowIds.indexOf(rowDetails[identifier]) != -1) {
      selectedRowDetails.push(rowDetails);
    }
  });
  return selectedRowDetails;
};

ginger.getCurrentRows = function(opts) {
  return $('#' + opts['gridId']).bootgrid("getCurrentRows");
}

ginger.getSelectedRows = function(opts) {
  return $('#' + opts['gridId']).bootgrid("getSelectedRows");
}

ginger.getTotalRowCount = function(opts) {
  return $('#' + opts['gridId']).bootgrid("getTotalRowCount");
}

ginger.reloadGridData = function(opts) {
  return $('#' + opts['gridId']).bootgrid("reload");
}

ginger.createActionList = function(settings) {
  var toolbarNode = null;
  var btnHTML, dropHTML = [];
  var container = settings.panelID;
  var toolbarButtons = settings.buttons;
  var buttonType = settings.type;
  toolbarNode = $('<div class="btn-group"></div>');
  toolbarNode.appendTo($("#" + container));
  dropHTML = ['<div class="dropdown menu-flat">',
    '<button id="action-dropdown-button-', container, '" class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">', (buttonType === 'action') ? '<span class="edit-alt"></span>'+ i18n['GINBG00003M'] : '<i class="fa fa-plus-circle"></i>'+ i18n['GINBG00004M'], '<span class="caret"></span>',
    '</button>',
    '<ul class="dropdown-menu"></ul>',
    '</div>'
  ].join('');
  $(dropHTML).appendTo(toolbarNode);

  $.each(toolbarButtons, function(i, button) {
    var btnHTML = [
      '<li role="presentation"', button.critical === true ? ' class="critical"' : '', '>',
      '<a role="menuitem" tabindex="-1" data-backdrop="static"  data-keyboard="false" data-dismiss="modal"', (button.id ? (' id="' + button.id + '"') : ''), (button.disabled === true ? ' class="disabled"' : ''),
      '>',
      button.class ? ('<i class="' + button.class) + '"></i>' : '',
      button.label,
      '</a></li>'
    ].join('');
    var btnNode = $(btnHTML).appendTo($('.dropdown-menu', toolbarNode));
    button.onClick && btnNode.on('click', button.onClick);
  });
}

ginger.changeButtonStatus = function(buttonIds, state) {
  $.each(buttonIds, function(i, buttonId) {
    if (state) {
      $('#' + buttonId).show();
    } else {
      $('#' + buttonId).hide();
    }
  });
}

ginger.showBootgridLoading = function(opts) {
  var gridMessage = ('loadingMessage' in opts && opts['loadingMessage'].trim() && opts['loadingMessage'].length > 0) ? opts['loadingMessage'] : i18n['GINBG00001M'];
  $("#" + opts['gridId'] + "-loading .wok-list-loading-text").text(gridMessage);
  $("#" + opts['gridId'] + "-loading").show();
  $("#" + opts['gridId'] + "-loading").css("zIndex", 1);
};

ginger.hideBootgridLoading = function(opts) {
  var gridMessage = ('loadingMessage' in opts && opts['loadingMessage'].trim() && opts['loadingMessage'].length > 0) ? opts['loadingMessage'] : i18n['GINBG00001M'];
  $("#" + opts['gridId'] + "-loading .wok-list-loading-text").text(gridMessage);
  $("#" + opts['gridId'] + "-loading").hide();
  $("#" + opts['gridId'] + "-loading").css("zIndex", 1);
};

ginger.showBootgridData = function(opts) {
  $("#" + opts['gridId'] + " tbody").show();
};

ginger.hideBootgridData = function(opts) {
  $("#" + opts['gridId'] + " tbody").hide();
};

ginger.createEditableBootgrid = function(gridInstance, opts, rowKey) {
  gridInstance.bootgrid().on("loaded.rs.jquery.bootgrid", function(e) {

    $.fn.editable.defaults.mode = 'inline';
    $('[data-xedit]').each(function() {
      $('span.xedit').editable({
        type: 'text',
        onblur: 'submit',
        showbuttons: false,
        send: 'never',
        toggle: 'manual',
        savenochange: true,
        success: function(response, newvalue) {
          var currentValue = $(this).closest('span').text(newvalue);
          var columnname = $(this).closest('span').attr("data-column-name");
          var datarowid = $(this).closest('span').attr("data-row-id");

          var changedData = {};
          var changedRow = {};
          var changeValueDetails = ginger.changedNwConfigValue;
          if (!$.isEmptyObject(changeValueDetails) && (changeValueDetails[datarowid] != undefined)) {
            changedData = ginger.changedNwConfigValue[datarowid];
          }

          changedData[columnname] = newvalue;
          changedRow[datarowid] = changedData;
          ginger.changedNwConfigValue = $.extend({}, changeValueDetails, changedRow);
          $(this).editable('hide');
          //get the next field in the row -- need to change the logic- now it's focusing on last
          //$('span.xedit:last',$(this).closest('tr')).editable('show');
          $(this).closest('td').next().find('span.xedit').editable('show');
        },
        validate: function(value) {

          var columnname = $(this).closest('span').attr("data-column-name");
          var isValid;
          var isIpv6 = $(this).closest('span').attr("data-ipv6");
          if (columnname == 'IPADDR' || columnname == 'GATEWAY' || columnname == 'ADDRESS' || columnname == 'DNS') {
            if (isIpv6 == 'true') {
              isValid = ginger.isValidIPv6(value);
            } else {
              isValid = ginger.validateIp(value);
            }
          } else if (columnname == 'MASK' || columnname == 'PREFIX' || columnname == 'NETMASK') {
            if (isIpv6 == 'true') {
              isValid = ginger.isValidIPv6(value) || ginger.isValidIPv6Prefix(value);
            } else {
              isValid = ginger.validateMask(value);
            }
          } else if (columnname == 'GLOBAL') {
            isValid = ginger.isValidIPv6($(this).val()) || ginger.validateIp($(this).val()) || ginger.validateHostName($(this).val());
          } else if (columnname == 'METRIC') {
            isValid = /^[0-9]+$/.test(value);
          } else {
            isValid = true;
          }

          $(this).toggleClass("invalid-field", !isValid);
          var saveButton = $("span.command-save", $(this).closest('tr'));

          saveButton.css('pointer-events', 'auto');

          if (!isValid) {
            saveButton.css('pointer-events', 'none');
            return 'invalid field';
          }
        }
      }).on('shown', function(e, editable) {
        editable.input.$input.on('keyup', function(e) {
          var columnname = $(this).closest('td').find('span.xedit').attr("data-column-name");
          var isValid;
          var isIpv6 = $(this).closest('td').find('span.xedit').attr("data-ipv6");
          if (columnname == 'IPADDR' || columnname == 'GATEWAY' || columnname == 'ADDRESS' || columnname == 'DNS') {
            if (isIpv6 == 'true') {
              isValid = ginger.isValidIPv6($(this).val());
            } else {
              isValid = ginger.validateIp($(this).val());
            }
          } else if (columnname == 'MASK' || columnname == 'PREFIX' || columnname == 'NETMASK') {
            if (isIpv6 == 'true') {
              isValid = ginger.isValidIPv6($(this).val()) || ginger.isValidIPv6Prefix($(this).val());
            } else {
              isValid = ginger.validateMask($(this).val());
            }
          } else if (columnname == 'GLOBAL') {
            isValid = ginger.isValidIPv6($(this).val()) || ginger.validateIp($(this).val()) || ginger.validateHostName($(this).val());
          } else if (columnname == 'METRIC') {
            isValid = /^[0-9]+$/.test($(this).val());
          } else {
            isValid = true;
          }

          $(this).toggleClass("invalid-field", !isValid);
          var saveButton = $("span.command-save", $(this).closest('tr'));

          saveButton.css('pointer-events', 'auto');

          if (!isValid) {
            saveButton.css('pointer-events', 'none');
          } else {
            saveButton.css('pointer-events', 'auto');

            if (e.which == 9) {
              e.preventDefault();
              if (e.shiftKey) {
                $(this).closest('td').prev().find('span.xedit').editable('show');
              } else {
                $(this).closest('td').next().find('span.xedit').editable('show');
              }
            }
          }

        });

      });
    });
    gridInstance.find(".command-edit").on("click", function(e) {
      e.stopPropagation();
      $('span.xedit:first', $(this).closest('tr')).editable('show');
      $(this).closest('td').find(".command-save").removeClass('hidden');
      $(this).addClass("hidden");
    }).end().find(".command-delete").on("click", function(e) {
      var data = $(this).data('row-id');
      var gridRows = ginger.getCurrentRows({
        "gridId": opts['gridId']
      });

      $.each(gridRows, function(i, row) {
        if (row[rowKey] == data) {
          $(this).closest('tr').remove();
          gridRows.splice(gridRows.indexOf(row), 1);
          ginger.clearBootgridData(opts['gridId']);
          ginger.appendBootgridData(opts['gridId'], gridRows);
          return false;
        }
      });
    }).end().find(".command-save").on("click", function(e) {
      var gridRows = ginger.getCurrentRows({
        "gridId": opts['gridId']
      });
      var inputfield = $('input', $(this).closest('tr'));

      if (inputfield != undefined) {
        var inputfieldvalue = inputfield.val();
        var columnname = inputfield.closest('td').find('span.xedit').attr("data-column-name");
        var datarowid = inputfield.closest('td').find('span.xedit').attr("data-row-id");

        var changedData = {};
        var changedRow = {};
        var changeValueDetails = ginger.changedNwConfigValue;
        if (!$.isEmptyObject(changeValueDetails) && (changeValueDetails[datarowid] != undefined)) {
          changedData = ginger.changedNwConfigValue[datarowid];
        }

        changedData[columnname] = inputfieldvalue;
        changedRow[datarowid] = changedData;
        ginger.changedNwConfigValue = $.extend({}, changeValueDetails, changedRow);
      }

      var changedRowDetails = ginger.changedNwConfigValue;

      $.each(gridRows, function(i, row) {
        var changedRowKey = Object.keys(changedRowDetails)[0];
        var changedFields = changedRowDetails[changedRowKey];
        if (row[rowKey] == changedRowKey) {
          var changedFieldsList = Object.keys(changedFields);
          $.each(changedFieldsList, function(i, field) {
            row[field] = changedFields[field];
          });
        }
        gridRows.push.apply(gridRows, row);
      });
      ginger.clearBootgridData(opts['gridId']);
      ginger.appendBootgridData(opts['gridId'], gridRows);
      ginger.changedNwConfigValue = {};
    });

  });
};

ginger.addNewRecord = function(columnSettings, gridId, commandSettings) {
  $('<tr></tr>').appendTo($('#' + gridId + ' tbody'));

  for (var i = 0; i < columnSettings.length; i++) {
    var columnHtml = ['<td ', (columnSettings[i]["width"]) ? (' style="width:' + columnSettings[i]["width"] + '"') : '', (columnSettings[i]["td-class"]) ? (' class="' + columnSettings[i]["td-class"] + '"') : '',
      '>',
      '<input type="text" id="', columnSettings[i]["id"], '" class="form-control input">',
      '</td>'
    ].join('');
    var inputField = $(columnHtml).appendTo($('tr:last', '#' + gridId));
    $('input', inputField).keyup(columnSettings[i]['validation']);
  }

  var commandHtml = ['<td ', (commandSettings['td-class']) ? (' class="' + commandSettings['td-class'] + '"') : '', (commandSettings['width']) ? (' style="width:' + commandSettings['width'] + '"') : '',
    '>'
  ].join('');
  $(commandHtml + '<span class=\"fa fa-floppy-o new-row-save\"></span><span class=\"fa fa-trash-o new-row-delete\"></span></td>').appendTo($('tr:last', '#' + gridId));

  $('.new-row-save', '#' + gridId).on('click', function(e) {
    var rowdata = {};
    for (var i = 0; i < columnSettings.length; i++) {
      var fieldName = columnSettings[i]["id"];
      var fieldValue = $('#' + columnSettings[i]["id"], $(this).closest('tr')).val();
      rowdata[fieldName] = fieldValue;
    }
    var rowdetails = [];
    rowdetails.push(rowdata);
    ginger.appendBootgridData(gridId, rowdetails);
  });

  $('.new-row-delete', '#' + gridId).on("click", function(e) {
    $('tr:last', $(this).closest('tbody')).remove();
  });
}

ginger.markInputInvalid = function(elem, isValid) {
  elem.toggleClass("invalid-field", !isValid);
  var newRowSaveButton = $("span.new-row-save", elem.closest('tr'));

  if (!isValid) {
    newRowSaveButton.css('pointer-events', 'none');
  } else {
    newRowSaveButton.css('pointer-events', 'auto');
  }
}
