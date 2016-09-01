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

ginger.initSelConfig = function() {
  ginger.opts_sel_if = {};
  ginger.opts_sel_if['id'] = 'sel-configuration';
  ginger.opts_sel_if['gridId'] = "selConfigGrid";
  ginger.opts_sel_if['identifier'] = "id";
  ginger.opts_sel_if['loadingMessage'] = i18n['GINNET0025M'];

  ginger.listSelData();
}

ginger.listSelData = function(){
  var selGrid = [];
  var gridFields = [];
   gridFields = [{
      "column-id": 'id',
      "type": 'string',
      "width": "5%",
      "identifier" : "true",
      "title": "ID"
    }, {
      "column-id": 'eventType',
      "type": 'string',
      "width": "25%",
      "title": "Event Type"
    }, {
      "column-id": 'eventAction',
      "type": 'string',
      "width": "12%",
      "title": "Action"
    }, {
      "column-id": 'date',
        "type": 'string',
      "width": "14%",
        "identifier" : "true",
        "title": "Date"
    }, {
      "column-id": 'time',
      "type": 'string',
      "width": "11%",
      "identifier" : "true",
      "title": "Time"
    }, {
      "column-id": 'eventData',
      "type": 'string',
      "width": "33%",
      "identifier" : "true",
      "title": "Event Data"
    }
  ];
  ginger.opts_sel_if['gridFields'] = JSON.stringify(gridFields);
  srvGrid = ginger.createBootgrid(ginger.opts_sel_if);
  ginger.initSelEventGridData();
};

ginger.initSelEventGridData = function() {
  ginger.clearBootgridData(ginger.opts_sel_if['gridId']);
  ginger.hideBootgridData(ginger.opts_sel_if);
  ginger.showBootgridLoading(ginger.opts_sel_if);
  var serverName = ginger.getSelectedRowsData(ginger.opts_srv_if)[0]["name"];
    ginger.getSel(serverName,function(res) {
    jobj= JSON.parse(JSON.stringify(res));
    ginger.loadBootgridData(ginger.opts_sel_if['gridId'], res);
    ginger.hideBootgridLoading(ginger.opts_sel_if);
  }, function(error) {
    var errmessage = i18n['GINSERV0010M'];
    wok.message.error(errmessage + " " + error.responseJSON.reason, '#message-sel-container-area', true);
    ginger.hideBootgridLoading(ginger.opts_sel_if);
    ginger.serverConfiguration.enableAllButtons();
    });
};

ginger.delSel = function(){
    var i;
    for(i=0; i < ginger.getSelectedRowsData(ginger.opts_sel_if).length ; i++){
    (function(count){
    var serverName = ginger.getSelectedRowsData(ginger.opts_srv_if)[0]["name"];
    var eventId = ginger.getSelectedRowsData(ginger.opts_sel_if)[i]["id"];
    ginger.deleteSel(serverName, eventId, function(result) {
                var message = i18n['GINSERV0017M'] + " " + eventId;
                wok.message.success(message, '#message-sel-container-area');
                ginger.initSelEventGridData();
          } , function (result){
                if (result['responseJSON']) {
                var errText = result['responseJSON']['reason'];
                }
              errText = i18n['GINSERV0018M'] + " " + eventId + " Reason :" + errText;
              result && wok.message.error(errText, '#message-sel-container-area', true);
              ginger.initSelConfig();
          });
    })(i);
    }
};