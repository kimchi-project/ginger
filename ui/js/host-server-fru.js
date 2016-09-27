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
  console.log('inside init fru config');
  ginger.opts_fru_if = {};
  ginger.opts_fru_if['id'] = 'fru-configuration';
  ginger.opts_fru_if['gridId'] = "fruConfigGrid";
  ginger.opts_fru_if['identifier'] = "ID";
  ginger.opts_fru_if['loadingMessage'] = i18n['GINNET0025M'];
  ginger.opts_fru_if['selection'] = false;
  ginger.listFruData();
}

ginger.listFruData = function(){
  var fruGrid = [];
  var gridFields = [];
   gridFields = [{
      "column-id": 'ID',
      "type": 'string',
      "width": "70px",
      "identifier" : "true",
      "title": "ID"
    },{
      "column-id": 'FRU Device Description',
      "type": 'string',
      "width": "200px",
      "identifier" : "true",
      "title": "Device Description"
    },{
      "column-id": 'Board Mfg Date',
      "type": 'string',
      "width": "220px",
      "identifier" : "true",
      "title": "Board Mfg Date"
    }, {
      "column-id": 'Board Product',
      "type": 'string',
      "width": "150px",
      "title": "Board Product"
    }, {
      "column-id": 'Board Serial',
      "type": 'string',
      "width": "150px",
      "title": "Board Serial"
    }, {
      "column-id": 'Board Part Number',
      "type": 'string',
      "width": "180px",
      "identifier" : "true",
      "title": "Board Part Number"
    }, {
      "column-id": 'Product Manufacturer',
      "type": 'string',
      "width": "200px",
      "identifier" : "true",
      "title": "Product Manufacturer"
    }, {
      "column-id": 'Product Name',
      "type": 'string',
      "width": "150px",
      "identifier" : "true",
      "title": "Product Name"
    }, {
      "column-id": 'Product Part Number',
      "type": 'string',
      "width": "200px",
      "identifier" : "true",
      "title": "Product Part Number"
    }, {
      "column-id": 'Product Serial',
      "type": 'string',
      "width": "150px",
      "identifier" : "true",
      "title": "Product Serial"
    }
  ];
  console.log('before createboot');
  ginger.opts_fru_if['gridFields'] = JSON.stringify(gridFields);
  fruGrid = ginger.createBootgrid(ginger.opts_fru_if);
  ginger.initFruEventGridData();
  console.log('after createboot');
};

ginger.initFruEventGridData = function() {
  console.log('Inside initFruEventGrid');
  ginger.clearBootgridData(ginger.opts_fru_if['gridId']);
  ginger.hideBootgridData(ginger.opts_fru_if);
  ginger.showBootgridLoading(ginger.opts_fru_if);
  console.log('After show boot grid');
  var serverName = ginger.getSelectedRowsData(ginger.opts_srv_if)[0]["name"];
    console.log('Server name :: ' + serverName);
    ginger.getFru(serverName,function(res) {
    jobj= JSON.parse(JSON.stringify(res));
    console.log('get fru REST');
    ginger.loadBootgridData(ginger.opts_fru_if['gridId'], res);
    ginger.hideBootgridLoading(ginger.opts_fru_if);
  }, function(error) {
    var errmessage = i18n['GINSERV0010M'];
    wok.message.error(errmessage + " " + error.responseJSON.reason, '#message-fru-container-area', true);
    ginger.hideBootgridLoading(ginger.opts_fru_if);
    ginger.serverConfiguration.enableAllButtons();
    });
};
