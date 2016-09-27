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

// This variable is used while deleting multiple servers
// to pass the server name in case of error message print


ginger.selectedSRVInterface = null;
ginger.opts_srv_if = {};
ginger.opts_srv_if['id'] = 'srv-configuration';
ginger.opts_srv_if['gridId'] = "srvConfigGrid";
ginger.opts_srv_if['identifier'] = "ipaddr";
ginger.opts_srv_if['loadingMessage'] = i18n['GINNET0025M'];

ginger.initServerConfig = function() {
  ginger.opts_srv_if = {};
  ginger.opts_srv_if['id'] = 'srv-configuration';
  ginger.opts_srv_if['gridId'] = "srvConfigGrid";
  ginger.opts_srv_if['identifier'] = "ipaddr";
  ginger.opts_srv_if['loadingMessage'] = i18n['GINNET0025M'];

  ginger.listServerConfig();
}

ginger.saveServer = function() {
  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;
  var ipaddr  = document.getElementById('ipaddr').value;
  var servername = document.getElementById('servername').value;
  if (validateAddServer("Server Name", servername) || validateAddServer("IP Address", ipaddr) ||
  validateAddServer("Password", password)){
    return;
  }
  ginger.showBootgridLoading(ginger.opts_srv_if);
  ginger.addServer( { 'ipaddr' : ipaddr, 'name' : servername , 'username' : username, 'password' : password}, function(result) {
	wok.window.close();
	ginger.initServerConfigGridData();
        ginger.hideBootgridLoading(ginger.opts_srv_if);
  }, function(result) {
    ginger.hideBootgridLoading(ginger.opts_srv_if);
    if (result['responseJSON']) {
        var errText = result['responseJSON']['reason'];
       }
    var errmessage = errText;
    wok.message.error(errmessage, '#message-srv-container-area', true);
    wok.window.close();
    });
};

ginger.updateServer = function() {
  var username = document.getElementById('username').value;
  var password = document.getElementById('password').value;
  var servername = document.getElementById('servername').value;
  ginger.showBootgridLoading(ginger.opts_srv_if);
  ginger.UpdServer(servername, { 'username' : username, 'password' : password}, function(result) {
        wok.window.close();
        ginger.initServerConfigGridData();
        ginger.hideBootgridLoading(ginger.opts_srv_if);
  }, function(error) {
    ginger.hideBootgridLoading(ginger.opts_srv_if);
    var errmessage = error.responseJSON.reason;
    alert(errmessage);
    wok.window.close();
    });
};

function validateAddServer(fieldName, value){
  if(value == null || value == ""){
    errmessage = fieldName + " is mandantory and cannot be left empty";
    wok.message.error(errmessage, '#message-add-container-area', true);
    return true;
  }
}

ginger.loadBootgridSRVActions = function() {

  var addActionsId = "srv-configuration-add";
  var tabActionsId = "srv-configuration-actions";
  // Add actions for Server Configuration
  var addButton = [{
  }];
  // Actions for Server Configuration
  var actionButton = [{
    id: 'srv-on-button',
    class: 'fa fa-power-off',
    label: i18n['GINSERV0004M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if ((selectedIf && selectedIf.length == 1) && (selectedIf[0]["status"] == "off")) {
        var settings = {
          content: i18n['GINSERV0013M'].replace("%1", selectedIf[0]["name"]),
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
          ginger.showBootgridLoading(ginger.opts_srv_if);
          ginger.serverPowerOn(selectedIf[0]["name"], function(result) {
            var message = i18n['GINSERV0007M'] + " " + selectedIf[0]["name"] + " " + i18n['GINNET0020M'];
            wok.message.success(message, '#message-srv-container-area');
	        ginger.initServerConfigGridData();
          }, function(error) {
            ginger.hideBootgridLoading(ginger.opts_srv_if);
            var message = i18n['GINSERV0007M'] + " " + selectedIf[0]["name"] + " " + i18n['GINNET0021M'];
            wok.message.error(message + " " + error.responseJSON.reason, '#message-srv-container-area', true);
	        ginger.initServerConfigGridData();
          });
        });
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  }, {
    id: 'srv-off-button',
    class: 'fa fa-ban',
    label: i18n['GINSERV0005M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if ((selectedIf && selectedIf.length == 1) &&
        ((selectedIf[0]["status"] == "on") || (selectedIf[0]["status"] == "unknown"))) {
        var settings = {
          content: i18n['GINSERV0012M'].replace("%1", selectedIf[0]["name"]),
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
          ginger.showBootgridLoading(ginger.opts_srv_if);
          ginger.serverPowerOff(selectedIf[0]["name"], function(result) {
            var message = i18n['GINSERV0008M'] + " " + selectedIf[0]["name"] + " " + i18n['GINNET0020M'];
            wok.message.success(message, '#message-srv-container-area');
            ginger.initServerConfigGridData();
          }, function(error) {
            ginger.hideBootgridLoading(ginger.opts_srv_if);
            var message = i18n['GINSERV0008M'] + " " + selectedIf[0]["name"] + " " + i18n['GINNET0021M'];
            wok.message.error(message + " " + error.responseJSON.reason, '#message-srv-container-area', true);
            ginger.initServerConfigGridData();
          });
	});
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'srv-delete-button',
    class: 'fa fa-minus-circle',
    label: i18n['GINSERV0006M'],
    critical: true,
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if (selectedIf && (selectedIf.length == 1)) {
        var settings = {
          content: i18n['GINSERV0011M'].replace("%1", selectedIf[0]["name"]),
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
          ginger.selectedSRVInterface = selectedIf[0]["status"];
          ginger.removeServer(selectedIf[0]["name"], function(result) {
                var message = i18n['GINSERV0006M'] + " " + selectedIf[0]["name"] + " " + i18n['GINNET0020M'];
                wok.message.success(message, '#message-srv-container-area');
                ginger.initServerConfigGridData();
          } , function (err){
                var message = i18n['GINSERV0006M'] + " " + selectedIf[0]["name"] + " " + i18n['GINNET0021M'];
                wok.message.success(message, '#message-srv-container-area');
                ginger.initServerConfigGridData();
          });
	});
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'srv-update-button',
    class: 'fa fa-plus-circle',
    label: i18n['GINSERV0015M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if (selectedIf && (selectedIf.length == 1)) {
       wok.window.open('plugins/ginger/host-upd-server.html');
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'srv-sdr-button',
    class: 'fa fa-file',
    label: i18n['GINSERV0019M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if (selectedIf && (selectedIf.length == 1)) {
       wok.window.open('plugins/ginger/host-server-sdr.html');
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'srv-sel-button',
    class: 'fa fa-file',
    label: i18n['GINSERV0016M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if (selectedIf && (selectedIf.length == 1)) {
       wok.window.open('plugins/ginger/host-server-sel.html');
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'srv-temp-button',
    class: 'fa fa-file',
    label: i18n['GINSERV0020M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if (selectedIf && (selectedIf.length == 1)) {
       wok.window.open('plugins/ginger/host-server-temp.html');
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  },{
    id: 'srv-fru-button',
    class: 'fa fa-file',
    label: i18n['GINSERV0021M'],
    onClick: function(event) {
      var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
      if (selectedIf && (selectedIf.length == 1)) {
       wok.window.open('plugins/ginger/host-server-fru.html');
      } else {
        var settings = {
          content: i18n["GINSERV0009M"],
          confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {});
      }
    }
  }];

  ginger.opts_srv_if['addButtons'] = JSON.stringify(addButton);
  ginger.opts_srv_if['actions'] = JSON.stringify(actionButton);

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

  ginger.createActionList(actionListSettings);

  $("#srv-configuration-refresh-btn").on('click', function() {
	  ginger.initServerConfigGridData();
  });
  $("#srv-configuration-add-btn").on('click', function() {
           wok.window.open('plugins/ginger/host-add-server.html');
  });
  $("#add-server-btn").on('click', function() {
	ginger.getServer();
   });

  ginger.serverConfiguration.disableActions();
}

ginger.listServerConfig = function() {

  var srvGrid = [];
  var gridFields = [];

  ginger.loadBootgridSRVActions();
  gridFields = [{
      "column-id": 'status',
      "type": 'string',
      "width": "10%",
      "formatter": "srv-status",
      "title": "Status"
    }, {
      "column-id": 'ipaddr',
      "type": 'string',
      "width": "30%",
      "identifier" : "true",
      "title": i18n['GINSERV0002M']
    }, {
      "column-id": 'name',
      "type": 'string',
      "width": "30%",
      "title": i18n['GINSERV0001M']
    }
  ];

  ginger.opts_srv_if['gridFields'] = JSON.stringify(gridFields);
  srvGrid = ginger.createBootgrid(ginger.opts_srv_if);
  ginger.hideBootgridLoading(ginger.opts_srv_if);
  srvGrid.bootgrid().on("selected.rs.jquery.bootgrid", function(e, rows) {
	changeActionButtonsState();
  }).on("deselected.rs.jquery.bootgrid", function(e, rows) {
	changeActionButtonsState();
  }).on("loaded.rs.jquery.bootgrid", function(e, rows) {
	changeActionButtonsState();
  });

var changeActionButtonsState = function() {
    // By default enable them all
    ginger.changeButtonStatus(["srv-on-button", "srv-off-button", "srv-delete-button"], true);
    // Based on the server status hide/show the right buttons
    var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
    if (selectedIf && selectedIf.length == 1) {
        ginger.serverConfiguration.enableActions();
	if (selectedIf[0]["status"] == "off"){
		ginger.changeButtonStatus(["srv-off-button"], false);
	}
	else{
		ginger.changeButtonStatus(["srv-on-button"], false);
	}
    }
    else{
       ginger.serverConfiguration.disableActions();
    }

  };
  ginger.initServerConfigGridData();
};

ginger.initServerConfigGridData = function() {
  ginger.clearBootgridData(ginger.opts_srv_if['gridId']);
  ginger.hideBootgridData(ginger.opts_srv_if);
  ginger.showBootgridLoading(ginger.opts_srv_if);

  ginger.getServer(function(result) {
    ginger.loadBootgridData(ginger.opts_srv_if['gridId'], result);
    ginger.showBootgridData(ginger.opts_srv_if);
    ginger.hideBootgridLoading(ginger.opts_srv_if);
    ginger.serverConfiguration.enableAllButtons();
  }, function(error) {
    var errmessage = i18n['GINSERV0010M'];
    wok.message.error(errmessage + " " + error.responseJSON.reason, '#message-srv-container-area', true);
    ginger.hideBootgridLoading(ginger.opts_srv_if);
    ginger.serverConfiguration.enableAllButtons();
    });
};


ginger.initServer = function() {
  $(".content-area", "#gingerHostServer").css("height", "100%");
  ginger.getHostDetails(function(result) {
    ginger.hostarch = result["architecture"];
    ginger.getCapabilities(function(result) {
      $.each(result, function(enableItem, capability) {
        var itemLowCase = enableItem.toLowerCase();
        switch (itemLowCase) {
          case "servers":
            ginger.initServerConfig();
            ginger.serverCapability = capability;
            break;
        }
      });
    });
  });


};


ginger.serverConfiguration = {};

ginger.serverConfiguration.enableAllButtons = function(){
	ginger.serverConfiguration.enableActions();
	ginger.serverConfiguration.enableRefresh();
};

ginger.serverConfiguration.disableAllButtons = function(){
	ginger.serverConfiguration.disableActions();
	ginger.serverConfiguration.disableRefresh();
	ginger.serverConfiguration.disableAdd();
};

ginger.serverConfiguration.enableActions = function (){
	$("#action-dropdown-button-srv-configuration-actions").prop("disabled", false);
};

ginger.serverConfiguration.disableActions = function (){
	$("#action-dropdown-button-srv-configuration-actions").parent().removeClass('open');
	$("#action-dropdown-button-srv-configuration-actions").prop("disabled", true);
};

ginger.serverConfiguration.enableRefresh = function (){
	$("#srv-configuration-refresh-btn").prop("disabled", false);
};

ginger.serverConfiguration.disableRefresh = function (){
	$("#srv-configuration-refresh-btn").prop("disabled", true);
};
ginger.serverConfiguration.enableAdd = function (){
	$("#action-dropdown-button-srv-configuration-add").prop("disabled", false);
};

ginger.serverConfiguration.disableAdd = function (){
	$("#action-dropdown-button-srv-configuration-add").prop("disabled", true);
};

ginger.serverConfiguration.enablePowerOn = function (){
	$("#srv-on-button").prop("disabled", false);
};

ginger.serverConfiguration.disablePowerOn = function (){
	$("#srv-on-button").prop("disabled", true);
};

function GetServerName() {
    var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
    return selectedIf[0]["name"];
}
function GetIPAddress() {
    var selectedIf = ginger.getSelectedRowsData(ginger.opts_srv_if);
    return selectedIf[0]["ipaddr"];
}
