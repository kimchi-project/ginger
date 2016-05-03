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

// This variable is used while deleting multiple interfaces
// to pass the interface name in case of error message print
ginger.selectedNWInterface = null;

ginger.initNetworkConfig = function() {
  ginger.opts_nw_if = {};
  ginger.opts_nw_if['id'] = 'nw-configuration';
  ginger.opts_nw_if['gridId'] = "nwConfigGrid";
  ginger.opts_nw_if['identifier'] = "device";
  ginger.opts_nw_if['loadingMessage'] = i18n['GINNET0025M'];

  ginger.listNetworkConfig();
}

ginger.loadBootgridNWActions = function() {

  var addActionsId = "nw-configuration-add";
  var tabActionsId = "nw-configuration-actions";
  // Add actions for Network Configuration
  var addButton = [{
    id: 'nw-add-bond-button',
    class: 'fa fa-plus-circle',
    label: i18n['GINNET0006M'],
    onClick: function(event) {
      ginger.selectedInterface = null;
      wok.window.open('plugins/ginger/host-network-bond.html');
    }
  }, {
    id: 'nw-add-vlan-button',
    class: 'fa fa-plus-circle',
    label: i18n['GINNET0007M'],
    onClick: function(event) {
      ginger.selectedInterface = null;
      wok.window.open('plugins/ginger/host-network-vlan.html');
    }
  }];

  // Actions for Network Configuration
  var actionButton = [{
    id: 'nw-up-button',
    class: 'fa fa-power-off',
    label: i18n['GINNET0009M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
      if ((selectedIf && selectedIf.length == 1) && (selectedIf[0]["status"] == "down")) {
        ginger.showBootgridLoading(ginger.opts_nw_if);
        ginger.enableInterface(selectedIf[0]["device"], "up", function(result) {
          var message = i18n['GINNET0016M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0020M'];
          wok.message.success(message, '#message-nw-container-area');
          ginger.getInterfaces(function(result) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
            ginger.loadBootgridData(ginger.opts_nw_if['gridId'], result);
          }, function(error) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
          });
        }, function(error) {
          ginger.hideBootgridLoading(ginger.opts_nw_if);
          var message = i18n['GINNET0016M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0021M'];
          wok.message.error(message + " " + error.responseJSON.reason, '#message-nw-container-area', true);
        });
      } else {
        var settings = {
          content: i18n["GINNET0022M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  }, {
    id: 'nw-down-button',
    class: 'fa fa-ban',
    label: i18n['GINNET0010M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
      if ((selectedIf && selectedIf.length == 1) &&
        ((selectedIf[0]["status"] == "up") || (selectedIf[0]["status"] == "unknown"))) {
        ginger.showBootgridLoading(ginger.opts_nw_if);
        ginger.enableInterface(selectedIf[0]["device"], "down", function(result) {
          var message = i18n['GINNET0017M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0020M'];
          wok.message.success(message, '#message-nw-container-area');
          ginger.getInterfaces(function(result) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
            ginger.loadBootgridData(ginger.opts_nw_if['gridId'], result);
          }, function(error) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
          });
        }, function(error) {
          ginger.hideBootgridLoading(ginger.opts_nw_if);
          var message = i18n['GINNET0017M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0021M'];
          wok.message.error(message + " " + error.responseJSON.reason, '#message-nw-container-area', true);
        });
      } else {
        var settings = {
          content: i18n["GINNET0022M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  }, {
    id: 'nw-restart-button',
    class: 'fa fa-undo',
    label: i18n['GINNET0011M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
      if ((selectedIf && selectedIf.length == 1) &&
        ((selectedIf[0]["status"] == "up") || (selectedIf[0]["status"] == "unknown"))) {
        ginger.showBootgridLoading(ginger.opts_nw_if);
        // First Bring down the interface
        ginger.enableInterface(selectedIf[0]["device"], "down", function(result) {
          // Second Bring the interface up back again
          ginger.enableInterface(selectedIf[0]["device"], "up", function(result) {
            var message = i18n['GINNET0018M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0020M'];
            wok.message.success(message, '#message-nw-container-area');
            ginger.getInterfaces(function(result) {
              ginger.hideBootgridLoading(ginger.opts_nw_if);
              ginger.loadBootgridData(ginger.opts_nw_if['gridId'], result);
            }, function(error) {
              ginger.hideBootgridLoading(ginger.opts_nw_if);
            });
          }, function(error) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
            var message = i18n['GINNET0018M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0021M'];
            wok.message.error(message + " " + error.responseJSON.reason, '#message-nw-container-area', true);
          });
        }, function(error) {
          ginger.hideBootgridLoading(ginger.opts_nw_if);
          var message = "Failed to brought down the interface " + selectedIf[0]["device"];
          wok.message.error(message + " " + error.responseJSON.reason, '#message-nw-container-area', true);
        });
      } else if (selectedIf && selectedIf.length == 1 && (selectedIf[0]["status"] == "down")) {
        ginger.showBootgridLoading(ginger.opts_nw_if);
        // Assuming interface is down already and just needs to brought up
        ginger.enableInterface(selectedIf[0]["device"], "up", function(result) {
          var message = i18n['GINNET0018M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0020M'];
          wok.message.success(message, '#message-nw-container-area');
          ginger.getInterfaces(function(result) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
            ginger.loadBootgridData(ginger.opts_nw_if['gridId'], result);
          }, function(error) {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
          });
        }, function(error) {
          ginger.hideBootgridLoading(ginger.opts_nw_if);
          var message = i18n['GINNET0018M'] + " " + selectedIf[0]["device"] + " " + i18n['GINNET0021M'];
          wok.message.error(message + " " + error.responseJSON.reason, '#message-nw-container-area', true);
        });
      } else {
        var settings = {
          content: i18n["GINNET0022M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  }, {
    id: 'nw-settings-button',
    class: 'fa fa-cog',
    label: i18n['GINNET0012M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
      if (selectedIf && (selectedIf.length == 1)) {
        ginger.selectedInterface = (selectedIf[0]["device"] == "undefined" ? null : selectedIf[0]["device"]);
        ginger.retrieveCfgInterface(ginger.selectedInterface, function (result) {
            if ((selectedIf[0]["type"]).toLowerCase() == "vlan") {
              wok.window.open('plugins/ginger/host-network-vlan.html');
            } else if ((selectedIf[0]["type"]).toLowerCase() == "bond") {
              wok.window.open('plugins/ginger/host-network-bond.html');
            } else if (((selectedIf[0]["type"]).toLowerCase() == "ethernet") || ((selectedIf[0]["type"]).toLowerCase() == "nic")) {
              // condition nic should go away if #104 to be correct and resolved
              wok.window.open('plugins/ginger/host-network-settings.html');
            }
        }, function(error){
            wok.message.error(i18n['GINNET0034E'].replace("%1", ginger.selectedInterface), '#message-nw-container-area', true);
            //Re-load the network interfaces after to clear other inactive interfaces without ifcfg files
            ginger.initNetworkConfigGridData();
        });
      } else {
        var settings = {
          content: i18n["GINNET0022M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'nw-enable-sriov',
    class: 'fa fa-minus-circle',
    label: i18n['GINNET0037E'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
      ginger.selectedInterface = selectedIf[0];
      wok.window.open('plugins/ginger/host-network-enable-sriov.html');
    }
  },{
    id: 'nw-delete-button',
    class: 'fa fa-minus-circle',
    label: i18n['GINNET0013M'],
    critical: true,
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
      if (selectedIf && (selectedIf.length == 1) && selectedIf[0]["type"] != 'nic') {
        ginger.selectedNWInterface = selectedIf[0]["device"];
          var settings = {
            content: i18n['GINNET0028M'].replace("%1", ginger.selectedNWInterface),
            confirm: i18n["GINNET0015M"]
          };
          wok.confirm(settings, function() {
            ginger.showBootgridLoading(ginger.opts_nw_if);
            ginger.deleteInterface(ginger.selectedNWInterface, function(result) {
              var message = i18n['GINNET0019M'] + " " + ginger.selectedNWInterface + " " + i18n['GINNET0020M'];
              wok.message.success(message, '#message-nw-container-area');

              //Re-load the network interfaces after delete action
              ginger.getInterfaces(function(result) {
                ginger.hideBootgridLoading(ginger.opts_nw_if);
                ginger.loadBootgridData(ginger.opts_nw_if['gridId'], result);
              }, function(error) {
                ginger.hideBootgridLoading(ginger.opts_nw_if);
              });
            }, function(error) {
              ginger.hideBootgridLoading(ginger.opts_nw_if);
              var message = i18n['GINNET0019M'] + " " + ginger.selectedNWInterface + " " + i18n['GINNET0021M'];
              wok.message.error(message + " " + error.responseJSON.reason, '#message-nw-container-area', true);
            });
          }, function() {
            ginger.hideBootgridLoading(ginger.opts_nw_if);
          });
      } else if (selectedIf.length > 1) {
        var settings = {
          content: i18n["GINNET0022M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  }];

  ginger.opts_nw_if['addButtons'] = JSON.stringify(addButton);
  ginger.opts_nw_if['actions'] = JSON.stringify(actionButton);

  var addListSettings = {
    panelID: addActionsId,
    buttons: addButton,
    type: 'add'
  };

  var actionListSettings = {
    panelID: tabActionsId,
    buttons: actionButton,
    type: 'action'
  };

  ginger.createActionList(addListSettings);

  // Hide button "Add VLAN" and "Add BOND "in case of capability "cfginterfaces" false
  if (ginger.cfginterfaces != undefined && !ginger.cfginterfaces) {
    $('#nw-add-bond-button').hide();
    $('#nw-add-vlan-button').hide();
    $('#nw-configuration-add').hide();
  } else {
    $('#nw-add-bond-button').show();
    $('#nw-add-vlan-button').show();
    $('#nw-configuration-add').show();
  }

  ginger.createActionList(actionListSettings);

  $("#nw-configuration-refresh-btn").on('click', function() {
	  ginger.networkConfiguration.disableAllButtons();
	  ginger.initNetworkConfigGridData();
  });
  ginger.networkConfiguration.disableActions();
}

ginger.listNetworkConfig = function() {

  var nwGrid = [];
  var gridFields = [];

  ginger.loadBootgridNWActions();
  //Network Configuration grid columns
  gridFields = [{
      "column-id": 'status',
      "type": 'string',
      "width": "5%",
      "formatter": "nw-interface-status",
      "title": ""
    }, {
      "column-id": 'device',
      "type": 'string',
      "width": "15%",
      "identifier": true,
      "title": i18n['GINNET0001M']
    }, {
      "column-id": 'type',
      "type": 'string',
      "width": "10%",
      "title": i18n['GINNET0003M']
    }, {
      "column-id": 'ipaddr',
      "formatter": "nw-address-space",
      "type": 'string',
      "width": "20%",
      "title": i18n['GINNET0004M']
    },
    {
      "column-id": 'rdma_enabled',
      "type": 'string',
      "width": "15%",
      "title": i18n['GINNET0039E']
    },
    {
      "column-id": 'module',
      "type": 'string',
      "width": "10%",
      "title": i18n['GINNET0036E']
    },
    {
      "column-id": 'macaddr',
      "type": 'string',
      "width": "20%",
      "title": i18n['GINNET0005M']
    }
  ];

  ginger.opts_nw_if['gridFields'] = JSON.stringify(gridFields);

  nwGrid = ginger.createBootgrid(ginger.opts_nw_if);
  ginger.hideBootgridLoading(ginger.opts_nw_if);

  nwGrid.bootgrid().on("selected.rs.jquery.bootgrid", function(e, rows) {
    changeActionButtonsState();
  }).on("deselected.rs.jquery.bootgrid", function(e, rows) {
    changeActionButtonsState();
  }).on("loaded.rs.jquery.bootgrid", function(e, rows) {
    changeActionButtonsState();
  });

  var changeActionButtonsState = function() {
    // By default enable them all
    ginger.changeButtonStatus(["nw-up-button", "nw-down-button", "nw-restart-button",
      "nw-settings-button", "nw-delete-button", "nw-enable-sriov"
    ], true);
    // Based on the interface status hide/show the right buttons
    var selectedIf = ginger.getSelectedRowsData(ginger.opts_nw_if);
    if (selectedIf && selectedIf.length == 1) {
      ginger.networkConfiguration.enableActions();
      if (selectedIf && (selectedIf[0]["status"] == 'up' || selectedIf[0]["status"] == 'unknown')) {
        ginger.changeButtonStatus(["nw-up-button"], false);
      } else {
        ginger.changeButtonStatus(["nw-down-button"], false);
      }
      if(selectedIf[0]["module"] != 'mlx5_core' && selectedIf[0]["module"] != 'mlx5-core') {
        ginger.changeButtonStatus(["nw-enable-sriov"], false);
      }
      if (selectedIf[0]["type"] == 'nic') {
        ginger.changeButtonStatus(["nw-delete-button"], false);
      }
    }
    else{
       ginger.networkConfiguration.disableActions();
    }
    //hide or show settings button based on cfginterfaces value
    ginger.changeButtonStatus(["nw-settings-button"], ginger.cfginterfaces);
  };
  ginger.initNetworkConfigGridData();
};

ginger.initNetworkConfigGridData = function() {
  ginger.clearBootgridData(ginger.opts_nw_if['gridId']);
  ginger.hideBootgridData(ginger.opts_nw_if);
  ginger.showBootgridLoading(ginger.opts_nw_if);

  ginger.getInterfaces(function(result) {

    $.each(result, function(index, value){
        if(value.rdma_enabled) {
          value.rdma_enabled = 'Yes';
        } else {
          value.rdma_enabled = 'No';
        }
    });

    ginger.loadBootgridData(ginger.opts_nw_if['gridId'], result);
    ginger.showBootgridData(ginger.opts_nw_if);
    ginger.hideBootgridLoading(ginger.opts_nw_if);
    ginger.networkConfiguration.enableAllButtons();
  }, function(error) {
    var errmessage = i18n['GINNET0033E'];
    wok.message.error(errmessage + " " + error.responseJSON.reason, '#message-nw-container-area', true);
    ginger.hideBootgridLoading(ginger.opts_nw_if);
    ginger.networkConfiguration.enableAllButtons();
    });
};

ginger.initGlobalNetworkConfig = function() {
  globalDnsAddButton = $('#nw-global-dns-add');
  globalDnsGateway = $('#nw-global-gateway-textbox');
  nwGlobalApplyBtn = $('#nw-global-apply-btn');
  nwGlobalRefreshBtn = $('#nw-global-dns-refresh-btn');

  ginger.opts_global_dns = {};
  ginger.opts_global_dns['id'] = 'nw-global-dns';
  ginger.opts_global_dns['gridId'] = "nw-global-dns-grid";
  ginger.opts_global_dns['noResults'] = " ";
  ginger.opts_global_dns['selection'] = false;
  ginger.opts_global_dns['navigation'] = 0;
  ginger.opts_global_dns['loadingMessage'] = i18n['GINNET0025M'];

  var gridFields = [];
  gridFields = [{
    "column-id": 'GLOBAL',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "80%",
    "title": i18n['GINNET0038M'],
    "identifier": true,
    "formatter": "editable-global-dns"
  }, {
    "column-id": "GLOBAL",
    "type": 'string',
    "title": "",
    "width": "20%",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "row-edit-delete"
  }];

  ginger.opts_global_dns['gridFields'] = JSON.stringify(gridFields);
  var globalDnsGrid = ginger.createBootgrid(ginger.opts_global_dns);

  ginger.loadGlobalNetworks();
  ginger.createEditableBootgrid(globalDnsGrid, ginger.opts_global_dns, 'GLOBAL');
  globalDnsAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'GLOBAL',
      'width': '80%',
      'validation': function() {
        var isValid = (ginger.isValidIPv6($(this).val()) || ginger.validateIp($(this).val()) || ginger.validateHostName($(this).val()));
        ginger.markInputInvalid($(this), isValid);
      }
    }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, ginger.opts_global_dns['gridId'], commandSettings);
  });

  globalDnsGateway.on('keyup', function() {
    var gatewayIP = globalDnsGateway.val();

    if(gatewayIP.trim() == "") {
      $(this).toggleClass("invalid-field", true);
    } else {
      $(this).toggleClass("invalid-field", !((ginger.isValidIPv6(gatewayIP)) || ginger.validateIp(gatewayIP)));
    }
  });

  nwGlobalApplyBtn.on('click', function() {
    var global_info = {};
    globalDnsAddresses = ginger.getCurrentRows(ginger.opts_global_dns);

    if (globalDnsAddresses.length > 0) {
      dns = []
      for (var i = 0; i < globalDnsAddresses.length; i++) {
        dnsValue = globalDnsAddresses[i].GLOBAL;
        dns.push(dnsValue);
      }
      global_info['nameservers'] = dns;
    } else {
      global_info['nameservers'] = '[]'
    }

    if (globalDnsGateway.val() != "")
      global_info['gateway'] = globalDnsGateway.val();

    ginger.showBootgridLoading(ginger.opts_global_dns);
    ginger.updateNetworkGlobals(global_info, function(result) {
      var message = i18n['GINNET0024M'] + " " + i18n['GINNET0020M'];
      wok.message.success(message, '#message-nw-global-container-area');
      ginger.hideBootgridLoading(ginger.opts_global_dns);
      ginger.loadGlobalNetworks();
    }, function(error) {
      ginger.hideBootgridLoading(ginger.opts_global_dns);
      var message = i18n['GINNET0024M'] + " " + i18n['GINNET0021M'] + " " + error.responseJSON.reason ;
      wok.message.error(error.responseJSON.reason, '#message-nw-global-container-area', true);
    });
  });

  nwGlobalRefreshBtn.on('click',function(){
	  ginger.loadGlobalNetworks();
  });
};

ginger.loadGlobalNetworks = function() {
	ginger.clearBootgridData(ginger.opts_global_dns['gridId']);
	ginger.hideBootgridData(ginger.opts_global_dns);
	ginger.showBootgridLoading(ginger.opts_global_dns);

  ginger.getNetworkGlobals(function(dnsAddresses) {
    if ("nameservers" in (dnsAddresses)) {
      var DNSNameServers = dnsAddresses.nameservers
      for (var i = 0; i < DNSNameServers.length; i++) {
        DNSNameServers[i] = {
          "GLOBAL": DNSNameServers[i]
        }
      }
      ginger.loadBootgridData(ginger.opts_global_dns['gridId'], DNSNameServers);
      ginger.showBootgridData(ginger.opts_global_dns);
      ginger.hideBootgridLoading(ginger.opts_global_dns);
    }
    if ("gateway" in (dnsAddresses)) {
      globalDnsGateway.val(dnsAddresses.gateway);
    }
  }, function(error){
    ginger.hideBootgridLoading(ginger.opts_global_dns);
    errmsg = i18n['GINNET0035E'] + ' ' + error.responseJSON.reason;
    wok.message.error(errmsg, '#message-nw-global-container-area', true);
  });
}

ginger.initNetwork = function() {
  $(".content-area", "#gingerHostNetwork").css("height", "100%");
  ginger.getHostDetails(function(result) {
    ginger.hostarch = result["architecture"];
    ginger.getCapabilities(function(result) {
      $.each(result, function(enableItem, capability) {
        var itemLowCase = enableItem.toLowerCase();
        switch (itemLowCase) {
          case "network":
            ginger.initGlobalNetworkConfig();
            ginger.initNetworkConfig();
            break;
          case "cfginterfaces":
            ginger.cfginterfaces = capability;
            ginger.changeButtonStatus(["nw-add-bond-button", "nw-add-vlan-button", "nw-configuration-add"], capability);
            break;
        }
      });
    });
  });
};

ginger.networkConfiguration = {};

ginger.networkConfiguration.enableAllButtons = function(){
	ginger.networkConfiguration.enableActions();
	ginger.networkConfiguration.enableRefresh();
	ginger.networkConfiguration.enableAdd();
}

ginger.networkConfiguration.disableAllButtons = function(){
	ginger.networkConfiguration.disableActions();
	ginger.networkConfiguration.disableRefresh();
	ginger.networkConfiguration.disableAdd();
}

ginger.networkConfiguration.enableActions = function (){
	$("#action-dropdown-button-nw-configuration-actions").prop("disabled", false);
};

ginger.networkConfiguration.disableActions = function (){
	$("#action-dropdown-button-nw-configuration-actions").parent().removeClass('open');
	$("#action-dropdown-button-nw-configuration-actions").prop("disabled", true);
};

ginger.networkConfiguration.enableRefresh = function (){
	$("#nw-configuration-refresh-btn").prop("disabled", false);
};

ginger.networkConfiguration.disableRefresh = function (){
	$("#nw-configuration-refresh-btn").prop("disabled", true);
};
ginger.networkConfiguration.enableAdd = function (){
	$("#action-dropdown-button-nw-configuration-add").prop("disabled", false);
};

ginger.networkConfiguration.disableAdd = function (){
	$("#action-dropdown-button-nw-configuration-add").prop("disabled", true);
};
