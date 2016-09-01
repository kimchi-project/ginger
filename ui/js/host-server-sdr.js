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

ginger.initSdrConfig = function() {
  ginger.opts_sdr_if = {};
  ginger.opts_sdr_if['id'] = 'sdr-configuration';
  ginger.opts_sdr_if['gridId'] = "sdrConfigGrid";
  ginger.opts_sdr_if['identifier'] = "id";
  ginger.opts_sdr_if['loadingMessage'] = i18n['GINNET0025M'];
  ginger.opts_sdr_if['selection'] = false;
  ginger.listsdrData();
}

ginger.listsdrData = function(){
  var sdrGrid = [];
  var gridFields = [];
   gridFields = [{
      "column-id": 'SensorId',
      "type": 'string',
      "width": "25%",
      "title": "Sensor ID"
    }, {
      "column-id": 'Status',
      "type": 'string',
      "width": "12%",
      "title": "Status"
    }, {
      "column-id": 'EntityId',
      "type": 'string',
      "width": "12%",
      "title": "Entity ID"
    }, {
      "column-id": 'SensorReading',
        "type": 'string',
      "width": "20%",
        "identifier" : "true",
        "title": "Sensor Reading"
    }, {
      "column-id": 'DiscreteState',
      "type": 'string',
      "width": "31%",
      "identifier" : "true",
      "title": "Discrete State"
    }
  ];
  ginger.opts_sdr_if['gridFields'] = JSON.stringify(gridFields);
  srvGrid = ginger.createBootgrid(ginger.opts_sdr_if);
  ginger.initsdrEventGridData();
};

ginger.initsdrEventGridData = function() {
  ginger.clearBootgridData(ginger.opts_sdr_if['gridId']);
  ginger.hideBootgridData(ginger.opts_sdr_if);
  ginger.showBootgridLoading(ginger.opts_sdr_if);
  var serverName = ginger.getSelectedRowsData(ginger.opts_srv_if)[0]["name"];
    ginger.getSdr(serverName,function(res) {
    jobj= JSON.parse(JSON.stringify(res));
    ginger.loadBootgridData(ginger.opts_sdr_if['gridId'], res);
    ginger.hideBootgridLoading(ginger.opts_sdr_if);
  }, function(error) {
    var errmessage = i18n['GINSERV0010M'];
    wok.message.error(errmessage + " " + error.responseJSON.reason, '#message-sdr-container-area', true);
    ginger.hideBootgridLoading(ginger.opts_sdr_if);
    ginger.serverConfiguration.enableAllButtons();
    });
};