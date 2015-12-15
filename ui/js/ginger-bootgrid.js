/*
 * Copyright IBM Corp, 2015
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

 ginger.createBootgrid = function(opts){
	var containerId = opts['id'];
	var gridId=opts['gridId'];
	var fields = JSON.parse(opts['gridFields']);

	var gridHtml = [
	                '<table id="',gridId,'" class="table table-condensed table-hover table-striped" >',
	                  '<thead>',
		                   '<tr>',
		                   '</tr>',
	                  '</thead>'
	               ].join('');
	$(gridHtml).appendTo('#'+containerId);
	var gridHeader = $('tr',gridHtml);

	for(var i=0;i<fields.length;i++){

		var columnHtml = [
                      '<th data-type="',fields[i]["type"],'" data-column-id="',fields[i]["column-id"],'"',
                       (fields[i].identifier)?'data-identifier="true"':'',' data-align="left" headerAlign="center"',
                       ("formatter" in fields[i])?'data-formatter='+fields[i]["formatter"]:'',
                       (fields[i].width)?(' data-width="'+fields[i].width+'"'):'',
                       'data-header-css-class="gridHeader">',
                      ("title" in fields[i])?fields[i]["title"]:fields[i]["column-id"],
                      '</th>'
		                  ].join('');
		$(columnHtml).appendTo($('tr','#'+gridId));

	}

	var grid = $('#'+gridId).bootgrid({
        selection: true,
        multiSelect: true,
        keepSelection: true,
        rowCount:-1,
        sorting:true,
        columnSelection:false,
        rowSelect:true,
        formatters:{
          "percentage-used" : function(column , row){
          return '<div class="progress"><div class="progress-bar-info" style="width:'+row[column['id']]+'">'+row[column['id']]+'</div></div>';
        },
          "nw-interface-status": function(column, row)
           {
             var value = row[column.id];
             if (column.id == "status") {
               if (value == "up")
                 return "<span class=\"nw-interface-status-enabled enabled\"> <i class=\"fa fa-power-off\"></i></span>";
             return "<span class=\"nw-interface-status-disabled disabled\"> <i class=\"fa fa-power-off\"></i></span>";
           }
         },
         "nw-address-space": function(column, row)
          {
            var ipaddr = row[column.id];
            var netmask = row['netmask'];
            if (!ipaddr) {
              return "";
            }
            return ipaddr + "/" + netmask;
          },
					"editableSize":function(column, row)
					{
		        return '<a href="#" id="fsSize">'+row['size']+'</a>	';
					}
       },
        css:{
            iconDown : "fa fa-sort-desc",
            iconUp: "fa fa-sort-asc"
         },
         labels :{
           search : "Filter"
         }
    }).on("load.rs.jquery.bootgrid", function (e) {
        $('.input-group .glyphicon-search').removeClass('.glyphicon-search').addClass('fa fa-search');
     });
		 return grid;
}

ginger.loadBootgridData = function(gridId, data){
	ginger.clearBootgridData(gridId);
  ginger.appendBootgridData(gridId,data);
};

ginger.clearBootgridData = function(gridId){
	$('#'+gridId).bootgrid("clear");
};

ginger.appendBootgridData = function(gridId, data){
	  $('#'+gridId).bootgrid("append",data);
};

ginger.getSelectedRowsData = function(opts){
  var selectedRowDetails = [];
  var currentRows = ginger.getCurrentRows(opts);
  var selectedRowIds = ginger.getSelectedRows(opts);
  var identifier = opts['identifier'];
  $.each(currentRows,function(i,row){
    var rowDetails = row;
    if(selectedRowIds.indexOf(rowDetails[identifier])!=-1){
      selectedRowDetails.push(rowDetails);
    }
  });
  return selectedRowDetails;
};

ginger.getCurrentRows =  function(opts){
	return $('#'+opts['gridId']).bootgrid("getCurrentRows");
}

ginger.getSelectedRows =  function(opts){
	return $('#'+opts['gridId']).bootgrid("getSelectedRows");
}

ginger.getTotalRowCount =  function(opts){
	return $('#'+opts['gridId']).bootgrid("getTotalRowCount");
}

ginger.reloadGridData =  function(opts){
	return $('#'+opts['gridId']).bootgrid("reload");
}

ginger.createActionList = function(settings){
  var toolbarNode = null;
  var btnHTML, dropHTML = [];
  var container = settings.panelID;
  var toolbarButtons = settings.buttons;
  var buttonType = settings.type;
  toolbarNode = $('<div class="btn-group"></div>');
  toolbarNode.appendTo($("#"+container));
  dropHTML = ['<div class="dropdown menu-flat">',
                      '<button id="action-dropdown-button-', container, '" class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">',
                       (buttonType==='action')?'<span class="edit-alt"></span>Actions':'<i class="fa fa-plus-circle"></i>Add ','<span class="caret"></span>',
                      '</button>',
                      '<ul class="dropdown-menu"></ul>',
                      '</div>'
                  ].join('');
   $(dropHTML).appendTo(toolbarNode);

     $.each(toolbarButtons, function(i, button) {
                    var btnHTML = [
                        '<li role="presentation"', button.critical === true ? ' class="critical"' : '', '>',
                        '<a role="menuitem" tabindex="-1" data-dismiss="modal"', (button.id ? (' id="' + button.id + '"') : ''), (button.disabled === true ? ' class="disabled"' : ''),
                        '>',
                        button.class ? ('<i class="' + button.class) + '"></i>' : '',
                        button.label,
                        '</a></li>'
                    ].join('');
                    var btnNode = $(btnHTML).appendTo($('.dropdown-menu', toolbarNode));
                    button.onClick && btnNode.on('click', button.onClick);
                });
}

ginger.changeButtonStatus = function(buttonIds, state){
  $.each(buttonIds, function(i, buttonId) {
    if (state) {
     $('#'+buttonId).show();
    } else {
     $('#'+buttonId).hide();
    }
  });
}
