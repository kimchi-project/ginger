/*
 * Copyright IBM Corp, 2017
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

ginger.initAudit = function() {
    $(".content-area", "#gingerHostAudit").css("height", "100%");
    $(".audit-ppc-enabled").show();
    ginger.loadAuditRulesData();
    ginger.loadAuditlogsData();
    ginger.loadAuditDispatcher();
};

ginger.loadAuditRulesData =  function() {
    $(".rules-loader").show();
    ginger.getAuditRules(function(result) {

        if (result.length > 0) {
            var rows = "";
            $.each(result, function(index, rule) {
                rows += "<tr><td>" + (index+1) + "</td>";
                if (rule.type == "System Call Rule") {
                    type = i18n['GINAUDIT0078M'];
                } else if (rule.type == "Control Rule") {
                    type = i18n['GINAUDIT0079M'];
                } else if (rule.type == "File System Rule") {
                    type = i18n['GINAUDIT0080M'];
                }
                rows += "<td>" + type + "</td>";
                var ruleDetails = rule.rule;
                var titleValue = "";
                var syscallStartIndex = ruleDetails.indexOf("-S");

                if (ruleDetails.substring(syscallStartIndex,ruleDetails.indexOf("-F",syscallStartIndex)).split(",").length > 10) {
                    titleValue=ruleDetails.replace(/.{70}/g,"$&"+"\n");
                } else {
                    titleValue = ruleDetails;
                }
                rows += "<td class=\"content\" title=\""+titleValue+"\">" + ruleDetails + "</td>";
                rows += "<td style=\"text-align:center;\" class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\"></span> </td>";

                if (rule.loaded=='yes') {
                    rows +="<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-loaded-enable enabled\"> <i class=\"fa fa-power-off\"></i></span></td>"
                } else if (rule.loaded=='no') {
                    rows +="<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-loaded-disable disabled\"> <i class=\"fa fa-power-off\"></i></span></td>";
                } else {
                    rows +="<td style=\"text-align:center;\" class=\"loaded\">--</td>";
                }

                if (rule.persisted=='yes') {
                    rows += "<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-persisted-enable enabled\"> <i class=\"fa fa-floppy-o\"></i></span></td>"
                } else if (rule.persisted=='no') {
                    rows +="<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-persisted-disable disabled\"> <i class=\"fa fa-floppy-o\"></i></span></td>";
                } else {
                    rows +="<td style=\"text-align:center;\" class=\"loaded\">--</td>";
                }

                if (rule.rule_info) {
                    rows += "<td>" + JSON.stringify(rule.rule_info) + "</td>";
                } else {
                    rows += "<td></td>";
                }
                rows += "<td>" + rule.persisted + "</td>";
                rows += "<td>" + rule.loaded + "</td></tr>";
            });
            $("#audit-rules-table tbody").html(rows);
        }

        var auditRulesTable = $("#audit-rules-table").DataTable({
            columnDefs: [{"width":"10%", "targets" : 0},
                         {"width":"15%", "targets" : 1},
                         {"width":"45%", "targets" : 2},
                         {"width":"10%", "targets" : 3},
                         {"width":"10%", "targets" : 4},
                         {"width":"10%", "targets" : 5},
                         {orderable: false, targets: [3,4,5]},
                         {visible : false,  targets: [6,7,8]}],
            autoWidth:false,
            "initComplete": function(settings, json) {
                wok.initCompleteDataTableCallback(settings);
            },
            "oLanguage": {
                "sEmptyTable": i18n['GINNET0063M']
            }
        });
        // Add event listener for opening and closing details
        $('#audit-rules-table tbody').on('click', 'td.details-control', function () {
            //,td span.fa
            var tr = $(this).closest('tr');
            var row = auditRulesTable.row( tr );
            var ruleInfo = (row.data()[6]!="")?JSON.parse(row.data()[6]):i18n['GINAUDIT0001M'];

            if (row.child.isShown()) {
                // This row is already open - close it
                row.child.hide();
                $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
                tr.removeClass('shown');
            } else {
                // Open this row
                ginger.ruleDetailsPopulation(ruleInfo,row);
                $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
                tr.addClass('shown');
                $('.audit-rules-details',$("#audit-rules-table tbody")).closest("tr").css("color","black");
            }
        });

        //Row selection
        $('#audit-rules-table tbody').on('click', 'tr', function () {
            $(this).toggleClass("selected");
        });

        $(".rules-loader").hide();
    }, function(err) {
        $(".rules-loader").hide();
        wok.message.error(err.responseJSON.reason, '#alert-modal-audit-rules-container');
    });
};

$('#audit-rule-add-btn').click(function() {
    wok.window.open('plugins/ginger/host-admin-addAuditRule.html');
});

$('#Audit-Rule-Configure-btn').click(function() {
    wok.window.open('plugins/ginger/host-admin-ConfigAuditRule.html');
});

$('#Audit-Rule-Import-btn').click(function() {
    wok.window.open('plugins/ginger/host-admin-ImportAuditRule.html');
});

$('#Audit-Rule-Edit-btn').click(function() {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0 || auditRulesTable.rows('.selected').data().length > 1) {
        var settings = {
            content: i18n["GINAUDIT0030M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var ruleName,ruleValue;
        var persistcheck;
        var ruleCheck = "";
        $.each(selectedRowsData, function(index, value) {
            ruleName = value[1];
            ruleValue = value[2];
            persistcheck = value[7];
        });
        for (var i = 0; i < ruleValue.length; i++) {
            if (ruleValue[i] != " ") {
                ruleCheck = ruleCheck + ruleValue[i];
            } else {
              break;
            }
          }
        if (ruleCheck == "-e" || ruleCheck == "-D") {
            wok.message.error("Cant edit these rules", "#audit-message", true);
        } else {
            if (persistcheck == "no") {
                var settings = {
                    content: i18n["GINAUDIT0031M"],
                    confirm: i18n["GINNET0015M"]
                };
                wok.confirm(settings, function() {}, function() {});
            } else {
                if (ruleName==i18n['GINAUDIT0078M']) {
                    ruleName = "System Call Rule";
                } else if (ruleName==i18n['GINAUDIT0079M']) {
                    ruleName = "Control Rule";
                } else if (ruleName==i18n['GINAUDIT0080M']) {
                    ruleName = "File System Rule";
                }
                if (ruleName == "File System Rule") {
                    wok.window.open('plugins/ginger/host-admin-EditAuditRule.html');
                } else if (ruleName == "Control Rule") {
                    wok.window.open('plugins/ginger/host-admin-editControlRule.html');
                } else if (ruleName == "System Call Rule") {
                    wok.window.open('plugins/ginger/host-admin-editSystemRule.html');
                }
            }
        }
    }
});

$('#Audit-Rule-refresh-btn').on('click', function() {
    $('#audit-rules-table tbody').off();
    $("#audit-rules-table tbody").html("");
    $("#audit-rules-table").DataTable().destroy();
    ginger.loadAuditRulesData();
});

//delete Audit rules
$('#audit-rule-delete-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRowsDataLength = auditRulesTable.rows('.selected').data().length;
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0022M"] + '<br>' + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRowsData, function(key, value) {
                if (value[1] == "Control Rule" && value[7] == "no" && value[8] == "yes") {
                    wok.message.error(i18n["GINAUDIT0036M"]+' '+value[2], '#audit-message', true);
                    selectedRowsDataLength = selectedRowsDataLength - 1;
                } else if (value[1] == "Control Rule" && (value[2] == "-D" || value[2].includes("-e"))) {
                    wok.message.error(i18n["GINAUDIT0039M"]+' '+value[2], '#audit-message', true);
                    selectedRowsDataLength = selectedRowsDataLength - 1;
                } else {
                    ginger.deleteAuditRule(value[2], function(result) {
                        if (value[1] == "Control Rule") {
                            wok.message.success(i18n["GINAUDIT0037M"]+' '+value[2], '#audit-message');
                            selectedRowsDataLength = selectedRowsDataLength - 1;
                            if (selectedRowsDataLength === 0) {
                                $('#Audit-Rule-refresh-btn').trigger('click');
                            }
                        } else {
                            wok.message.success(i18n["GINAUDIT0023M"]+' '+value[2], '#audit-message');
                            selectedRowsDataLength = selectedRowsDataLength - 1;
                            if (selectedRowsDataLength === 0) {
                                $('#Audit-Rule-refresh-btn').trigger('click');
                            }
                        }
                    }, function(error) {
                        wok.message.error(error.responseJSON.reason, '#audit-message', true);
                        selectedRowsDataLength = selectedRowsDataLength - 1;
                        if (selectedRowsDataLength === 0) {
                            $('#Audit-Rule-refresh-btn').trigger('click');
                        }
                    });
                }
                if (selectedRowsDataLength === 0) {
                    $('#Audit-Rule-refresh-btn').trigger('click');
                }
            });
        });
    }
});

//audit load
$('#Audit-Rule-Load-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0024M"] + '<br>' + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRows, function(index, value) {
                ginger.LoadAuditRule(value.replace('&lt;','<').replace('&gt;','>'), function(result) {
                    wok.message.success(i18n["GINAUDIT0025M"]+' '+value, '#audit-message');
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                })
            });
            setTimeout(function() {$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});

//unload rule
$('#Audit-Rule-unload-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0026M"] + '<br>' + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRowsData, function(index, value) {
              if (value[1] == "Control Rule") {
                wok.message.error(i18n["GINAUDIT0038M"], '#audit-message', true);
              } else {
                ginger.UnLoadAuditRule(value[2].replace('&lt;','<').replace('&gt;','>'), function(result) {
                    wok.message.success(i18n["GINAUDIT0027M"]+' '+value[2], '#audit-message');
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                })
              }
            });
            setTimeout(function() {$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});

//persist audit
$('#Audit-Rule-Persist-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0028M"] + '<br>' + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRows, function(key, value) {
                ginger.PersistAuditRule(value.replace('&lt;','<').replace('&gt;','>'), function(result) {
                    wok.message.success(i18n["GINAUDIT0029M"]+' '+value, '#audit-message');
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                })
            });
            setTimeout(function() {$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});

ginger.ruleDetailsPopulation = function(data , row) {
    var text='';
    var value;
    var ruleDetails = '';
    if (typeof data === 'object') {
        $.each(data, function(key, obj) {
            value = obj;
            switch (key) {
                case "action":
                    text = i18n['GINAUDIT0002M'];
                    break;
                case "filter":
                    text = i18n['GINAUDIT0003M'];
                    break;
                case "systemcall":
                    text = i18n['GINAUDIT0004M'];
                    if (value.length > 10) {
                        value=value.toString().replace(/.{70}/g,"$&"+"\n");
                    }
                    break;
                case "field":
                    text = i18n['GINAUDIT0005M'];
                    if (value.length > 10) {
                        value=value.toString().replace(/.{70}/g,"$&"+"\n");
                    }
                    break;
                case "key":
                    text = i18n['GINAUDIT0006M'];
                    break;
                default:
                    text = key;
            }

            var detailsHtml = ['<div>',
                '<span class="column-'+key+'">',
                '<span class="header-'+key+'">'+text+'</span>',
                '<span class="row-'+key+'">'+value+'</span>',
                '</span>',
                '</div>'].join('');
            ruleDetails+=detailsHtml;
        });
        row.child('<div class="audit-rules-details" style="display: block;"><div class="details-list">'+ruleDetails+'</div></div>').show();
    } else {
        ruleDetails = data;
        row.child('<div class="audit-rules-details" style="display: block;"><div class="noRuleInfo">'+ruleDetails+'</div></div>').show();
    }
};

ginger.loadAuditlogsData =  function() {
    $(".logs-loader").show();
    ginger.getAuditLogs(function(result) {
        ginger.createAuditLogsTable(result);
    },function(err) {
        $(".logs-loader").hide();
        wok.message.error(err.responseJSON.reason, '#alert-modal-audit-logs-container');
    });

    ginger.initFilterInfo();
    ginger.initSummaryInfo();
};

ginger.createAuditLogsTable = function(data) {
    var rows = "";
    if (data.length > 0) {
        $.each(data, function(index, log) {
            var logDetails = log['record'+(index+1)];
            if (logDetails) {
                rows += "<tr><td>" + logDetails['Date and Time'] + "</td>";
                rows += "<td>" + logDetails['TYPE'] + "</td>";
                rows += "<td class=\"content\">" + logDetails['MSG']+ "</td>";
                rows += "<td style=\"text-align:center;\" class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\"></span> </td></tr>";
            }
        });
    }
    $("#audit-logs-table tbody").html(rows);

    var auditLogsTable = $("#audit-logs-table").DataTable({
        columnDefs: [
            {"width":"15%", "targets" : 0},
            {"width":"15%", "targets" : 1},
            {"width":"60%", "targets" : 2},
            {"width":"10%", "targets" : 3},
            {orderable: false, targets: [3]}],
        autoWidth:false,
        "dom": '<"row"<"log-report pull-left"><"log-filter pull-left"><"log-reset pull-left"><"col-sm-12 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
        "initComplete": function(settings, json) {
            wok.initCompleteDataTableCallback(settings);
            var reportButton = '<button class="btn btn-primary pull-left" id="log-report-btn" aria-expanded="false" data-toggle="modal" data-target="#auditlogReport"><i class="fa fa-file-archive-o">&nbsp;</i> ' + i18n['GINAUDIT0008M'] + '</button>';
            var filterButton = '<button class="btn btn-primary" id="log-filter-btn" aria-expanded="false" data-toggle="modal" data-target="#auditlogFilter"><i class="fa fa-filter">&nbsp;</i>' + i18n['GINAUDIT0007M']  + '</button>';
            var resetButton = '<button class="btn btn-primary" id="log-reset-btn" aria-expanded="false"><i class="fa fa-undo">&nbsp;</i>' + i18n['GINAUDIT0019M']  + '</button>';
            $(".log-report").html(reportButton);
            $(".log-filter").append(filterButton);
            $(".log-reset").html(resetButton);
        },
        "oLanguage": {
            "sEmptyTable": i18n['GINAUDIT0012M']
        }
    });

    // Add event listener for opening and closing details
    $('#audit-logs-table tbody').off();
    $('#audit-logs-table tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = auditLogsTable.row( tr );
        var logMessage = (row.data()[2]!="")?row.data()[2]:i18n['GINAUDIT0001M'];
        var dateTime = (row.data()[0]!="")?row.data()[0]:'';
        var type = (row.data()[1]!="")?row.data()[1]:'';

        $('.audit-log-details',$('#audit-logs-table tbody')).parent().remove();
        $('.fa-chevron-up',$('#audit-logs-table tbody')).addClass('fa-chevron-down').removeClass('fa-chevron-up');
        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
            tr.removeClass('shown');
        } else {
            // Open this row
            row.child('<div class="audit-log-details"><dl class="audit-log-info"><dt>'+dateTime+'</dt><dd>'+i18n['GINAUDIT0013M']+'</dd><dt>'+type+'</dt><dd>'+i18n['GINAUDIT0014M']+'</dd><dt>'+logMessage+'</dt><dd>'+i18n['GINAUDIT0015M']+'</dd></dl></div>').show();
            $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
            tr.addClass('shown');
            $('.audit-log-details',$('#audit-logs-table tbody')).closest("tr").css("color","black");
        }
    });

    //Row selection
    $('#audit-logs-table tbody').on('click', 'tr', function () {
        if ($(this).hasClass("selected")) {
            $(this).removeClass("selected");
        } else {
            auditLogsTable.$('tr.selected').removeClass('selected');
            $(this).addClass("selected");
        }
    });

    $('#log-reset-btn').on('click', function(e) {
        $(".logs-loader").show();
        ginger.getAuditLogs(function(result) {
            $("#audit-logs-table tbody").empty();
            $("#audit-logs-table").DataTable().destroy();
            ginger.createAuditLogsTable(result);
        },function(error) {
            wok.message.error(data.responseJSON.reason,"#alert-modal-audit-logs-container");
        });
    });
    $(".logs-loader").hide();
};

ginger.loadAuditDispatcher = function() {
    ginger.getDispatcherPlugin(function(result) {
        ginger.createDispatcherPluginTable(result);
    },function(error) {
        wok.message.error(data.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
    });
    ginger.getDispatcherDetails();
    ginger.getPluginDetails();
};

ginger.createDispatcherPluginTable = function(data) {
    var rows = "";
    if (data.length > 0) {
        $.each(data, function(index, log) {
            if (log) {
                rows += "<tr><td>" + log['name'] + "</td>";
                if (log['details']['active'] == "yes") {
                    active = i18n['GINNET0077M'];
                } else {
                    active = i18n['GINNET0078M'];
                }
                rows += "<td>" + active + "</td>";
                rows += "<td style=\"text-align:center;\" class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\"></span></td>";
                details = log['details'];
                if (details["active"] == "yes") {
                    details["active"] = i18n['GINNET0077M'];
                } else {
                    details["active"] = i18n['GINNET0078M'];
                }
                rows +="<td>" +JSON.stringify(details)+"</td></tr>";
            }
        });
    }
    $("#audit-disp-plugin-table tbody").html(rows);

    var auditDispPluginTable = $("#audit-disp-plugin-table").DataTable({
        columnDefs: [
            {orderable: false, targets: [2]},
            {visible : false,  targets: [3]}],
        autoWidth:false,
        "dom": '<"row"<"plugin-edit pull-left"><"#dispatcher.pull-left"><"refresh pull-left"><"status-value hidden"><"col-sm-12 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
        "initComplete": function(settings, json) {
            wok.initCompleteDataTableCallback(settings);
            var editButton = '<button class="btn btn-primary" id="plugin-edit-btn" aria-expanded="false"><i class="fa fa-pencil-square-o">&nbsp;</i>' + i18n['GINNET0074M']  + '</button>';
            var refreshButton = '<button class="btn btn-primary" id="disp-refresh-btn" aria-expanded="false"><i class="fa fa-refresh">&nbsp;</i>' + i18n['GINIS00001M']  + '</button>';

            var actionButton = [{id: 'dispatch-status-btn'},
                {id: 'disp-settings-btn',
                 class: 'fa fa-cogs',
                 label: i18n['GINNET0012M']}];

            var actionListSettings = {
                panelID: 'dispatcher',
                buttons: actionButton,
                type: 'action'
            };
            ginger.createActionButtons(actionListSettings);

            $(".plugin-edit").append(editButton);
            $(".refresh").html(refreshButton);
            $("#action-dropdown-button-dispatcher").empty().append('<i class="fa fa-angle-double-down" style="padding-right:7px;"></i>'+i18n['GINAUDITDISP0012M']);
            $("#action-dropdown-button-dispatcher").css({'height':'38.7px','font-weight':'500','width':'auto','background-color':'#3a393b'});

            ginger.getAuditStatus(function(result) {
                if (result['dispatcher']!=undefined) {
                    $("#dispatch-status-btn").empty().html('<i class="fa fa-pause">&nbsp;</i>'+i18n['GINAUDITDISP0011M']);
                    $(".status-value").text('enabled');
                } else {
                    $("#dispatch-status-btn").empty().html('<i class="fa fa-play">&nbsp;</i>'+i18n['GINAUDITDISP0010M']);
                    $(".status-value").text('disabled');
                }
            },function(error) {
                wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
            });
        },
        "oLanguage": {
            "sEmptyTable": i18n['GINAUDIT0012M']
        }
    });

    // Add event listener for opening and closing details
    $('#audit-disp-plugin-table tbody').off();
    $('#audit-disp-plugin-table tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = auditDispPluginTable.row( tr );
        var details = (row.data()[3]!="")?JSON.parse(row.data()[3]):i18n['GINAUDIT0001M'];

        $('.audit-log-details',$('#audit-disp-plugin-table tbody')).parent().remove();
        $('.fa-chevron-up',$('#audit-disp-plugin-table tbody')).addClass('fa-chevron-down').removeClass('fa-chevron-up');
        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
            tr.removeClass('shown');
        } else {
            // Open this row
            var direction  = (details['direction']!=undefined)?details['direction']:'--';
            var format  = (details['format']!=undefined)?details['format']:'--';
            var args  = (details['args']!=undefined)?details['args']:'--';
            var active  = (details['active']!=undefined)?details['active']:'--';
            var path  = (details['path']!=undefined)?details['path']:'--';
            var type  = (details['type']!=undefined)?details['type']:'--';

            row.child('<div class="audit-log-details"><dl class="audit-log-info"><dt>'+
                direction+'</dt><dd>'+i18n['GINAUDITDISP0001M']+'</dd><dt>'+
                format+'</dt><dd>'+i18n['GINAUDITDISP0002M']+'</dd><dt>'+
                args+'</dt><dd>'+i18n['GINAUDITDISP0003M']+'</dd><dt>'+
                active+'</dt><dd>'+i18n['GINAUDITDISP0004M']+'</dd><dt>'+
                path+'</dt><dd>'+i18n['GINAUDITDISP0005M']+'</dd><dt>'+
                type+'</dt><dd>'+i18n['GINAUDITDISP0006M']+'</dd>'+
                '</dl></div>').show();
            $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
            tr.addClass('shown');
            $('.audit-log-details',$('#audit-disp-plugin-table tbody')).closest("tr").css('color','black');
        }
    });


    //Row selection
    $('#audit-disp-plugin-table tbody').on('click', 'tr', function () {
        if ($(this).hasClass("selected")) {
            $(this).removeClass("selected");
        } else {
            auditDispPluginTable.$('tr.selected').removeClass('selected');
            $(this).addClass("selected");
        }
    });

    $('#disp-refresh-btn').off();
    $('#disp-refresh-btn').on('click', function(e) {
        $(".dispatcher-loader").show();
        ginger.getDispatcherPlugin(function(result) {
            $("#audit-disp-plugin-table tbody").empty();
            $("#audit-disp-plugin-table").DataTable().destroy();
            ginger.createDispatcherPluginTable(result);
        },function(error) {
            wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
        });
    });

    $("#dispatch-status-btn").off();
    $("#dispatch-status-btn").on('click',function(e) {
        var getCurrentStatus = $(".status-value").text();
        var action = (getCurrentStatus=='enabled')?'disable':'enable';
        ginger.changeAuditDispatcherStatus(action,function(result) {
            if (result['dispatcher']!=undefined) {
                $("#dispatch-status-btn").empty().append('<i class="fa fa-pause">&nbsp;</i>'+i18n['GINAUDITDISP0011M']);
                wok.message.success(i18n['GINAUDITDISP0013M'],"#alert-modal-audit-dispatcher-container");
                $(".status-value").text('enabled');
            } else {
                $("#dispatch-status-btn").empty().append('<i class="fa fa-play">&nbsp;</i>'+i18n['GINAUDITDISP0010M']);
                wok.message.success(i18n['GINAUDITDISP0014M'],"#alert-modal-audit-dispatcher-container");
                $(".status-value").text('disabled');
            }
        },function(error) {
            wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
        });
    });

    $("#plugin-edit-btn").off();
    $("#plugin-edit-btn").on('click',function() {
        var selectedRowsData = $("#audit-disp-plugin-table").DataTable().rows('.selected').data();
        if (selectedRowsData.length>0) {
            $("#auditPluginDetails").modal("show");
        } else {
            var settings = {
                content: i18n['GINAUDITDISP0009M'],
                confirm: i18n["GINNET0015M"]
            };
            wok.confirm(settings, function() {},function() {});
        }
    });

    $("#disp-settings-btn").off();
    $("#disp-settings-btn").on('click',function() {
        $("#auditDisprConf").modal("show");
    });
    $(".dispatcher-loader").hide();
};

ginger.getDispatcherDetails = function() {
    $('#auditDisprConf').on('show.bs.modal', function(event) {
        ginger.getDispatcherConfiguration(function(result) {
            $("#overflowAction").val(result["overflow_action"]);
            $("#priorityBoost").val(result["priority_boost"]);
            $("#qDepth").val(result["q_depth"]);
            $("#maxRestarts").val(result["max_restarts"]);
            $("#nameFormat").val(result["name_format"]);
        },function(error) {
            wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
        });

        $("#disp-conf-button-apply").on("click",function() {
            var params = {};
            params['overflow_action'] = $("#overflowAction").val();
            params['priority_boost']  = $("#priorityBoost").val();
            params['q_depth'] = $("#qDepth").val();
            params['max_restarts'] = $("#maxRestarts").val();
            params['name_format'] = $("#nameFormat").val();

            ginger.updateDispatcherConfiguration(params, function(result) {
                $('#auditDisprConf').modal('hide');
                wok.message.success(i18n['GINAUDITDISP0007M'],"#alert-modal-audit-dispatcher-container");
            },function(error) {
                wok.message.error(error.responseJSON.reason,"#alert-modal-disp-conf-container");
            });
        });
    });

    $('#auditDisprConf').on('hide.bs.modal', function(event) {
        $("#disp-conf-button-apply").off();
    });
};

ginger.getPluginDetails = function() {
    $('#auditPluginDetails').on('show.bs.modal', function(event) {
        var selectedRowsData = $("#audit-disp-plugin-table").DataTable().rows('.selected').data();
        var pluginDetails = selectedRowsData[0];
        var detailsInfo =  JSON.parse(pluginDetails[3]);
        var pluginName = pluginDetails[0];

        $("#direction").val(detailsInfo['direction']);
        $("#format").val(detailsInfo['format']);
        $("#args").val(detailsInfo['args']);
        if (detailsInfo['active'] == i18n['GINNET0077M']) {
            $("#active").val("yes");
        } else {
            $("#active").val("no");
        }
        $("#path").val(detailsInfo['path']);
        $("#type").val(detailsInfo['type']);
        $("#active").selectpicker();
        $('#active').selectpicker('refresh');

        $("#plugin-update-button-apply").on("click",function() {
            var params = {};
            params['direction'] = $("#direction").val();
            params['format'] = $("#format").val();
            params['args'] = $("#args").val();
            params['active'] = $("#active").val();
            params['path'] = $("#path").val();
            params['type'] = $("#type").val();

            ginger.updateDispatcherPlugin(pluginName, params, function(result) {
                $('#auditPluginDetails').modal('hide');
                wok.message.success((i18n['GINAUDITDISP0008M']).replace("%1",pluginName),"#alert-modal-audit-dispatcher-container");
                $(".dispatcher-loader").show();
                ginger.getDispatcherPlugin(function(result) {
                    $("#audit-disp-plugin-table tbody").html("");
                    $("#audit-disp-plugin-table").DataTable().destroy();
                    ginger.createDispatcherPluginTable(result);
                },function(error) {
                    wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
                });
            },function(error) {
                wok.message.error(error.responseJSON.reason,"#alert-modal-plugin-container");
            });
        });
    });

    $('#auditPluginDetails').on('hide.bs.modal', function(event) {
        $("#plugin-update-button-apply").off();
    });
};

ginger.populateFilterOptions =  function(row) {
    var optionsList =
        {'-a':i18n['GINAUDIFILTER0001M'],
         '--arch':i18n['GINAUDIFILTER0002M'],
         '-c':i18n['GINAUDIFILTER0003M'],
         '--debug':i18n['GINAUDIFILTER0004M'],
         '-e':i18n['GINAUDIFILTER0005M'],
         '-f':i18n['GINAUDIFILTER0006M'],
         '-gi':i18n['GINAUDIFILTER0007M'],
         '-hn':i18n['GINAUDIFILTER0008M'],
         '--just-one':i18n['GINAUDIFILTER0009M'],
         '-k':i18n['GINAUDIFILTER0010M'],
         '-m':i18n['GINAUDIFILTER0011M'],
         '-p':i18n['GINAUDIFILTER0012M'],
         '-pp':i18n['GINAUDIFILTER0013M'],
         '-r':i18n['GINAUDIFILTER0014M'],
         '-sc':i18n['GINAUDIFILTER0015M'],
         '--session':i18n['GINAUDIFILTER0016M'],
         '-sv':i18n['GINAUDIFILTER0017M'],
         '-te':i18n['GINAUDIFILTER0018M'],
         '-ts':i18n['GINAUDIFILTER0019M'],
         '-tm':i18n['GINAUDIFILTER0020M'],
         '-ui':i18n['GINAUDIFILTER0021M'],
         '-ul':i18n['GINAUDIFILTER0022M'],
         '-uu':i18n['GINAUDIFILTER0023M'],
         '-vm':i18n['GINAUDIFILTER0024M'],
         '-w':i18n['GINAUDIFILTER0025M'],
         '-x':i18n['GINAUDIFILTER0026M']};

    var filterField = $('.selectpicker',row);
    $.each(optionsList,function(key,value) {
        filterField.append($("<option></option>")
            .attr("value", key.replace(/"/g, ""))
            .text(value.replace(/"/g, "")));
    });
    filterField.selectpicker();
};

ginger.populateReportOptions =  function(row) {
    var detailReportOptionsList =
        {'-au':i18n['GINAUDIREPORT0001M'],
         '-a':i18n['GINAUDIREPORT0002M'],
         '--comm':i18n['GINAUDIREPORT0003M'],
         '-c':i18n['GINAUDIREPORT0004M'],
         '-cr':i18n['GINAUDIREPORT0005M'],
         '-e':i18n['GINAUDIREPORT0006M'],
         '-f':i18n['GINAUDIREPORT0007M'],
         '-h':i18n['GINAUDIREPORT0008M'],
         '--integrity':i18n['GINAUDIREPORT0009M'],
         '-k':i18n['GINAUDIREPORT0010M'],
         '-l':i18n['GINAUDIREPORT0011M'],
         '-m':i18n['GINAUDIREPORT0012M'],
         '-ma':i18n['GINAUDIREPORT0013M'],
         '-n':i18n['GINAUDIREPORT0014M'],
         '-p':i18n['GINAUDIREPORT0015M'],
         '-r':i18n['GINAUDIREPORT0016M'],
         '-s':i18n['GINAUDIREPORT0017M'],
         '--success':i18n['GINAUDIREPORT0018M'],
         '-t':i18n['GINAUDIREPORT0019M'],
         '--tty':i18n['GINAUDIREPORT0020M'],
         '-tm':i18n['GINAUDIREPORT0021M'],
         '-u':i18n['GINAUDIREPORT0022M'],
         '--virt':i18n['GINAUDIREPORT0023M'],
         '-x':i18n['GINAUDIREPORT0024M']};

    var summaryReportOptionList = {'--failed':i18n['GINAUDIREPORT0025M'],
        '-nc':i18n['GINAUDIREPORT0026M'],
        '-te':i18n['GINAUDIREPORT0027M'],
        '-ts':i18n['GINAUDIREPORT0028M']};

    var type = $('#reportType').val();

    var optionsList = (type=='detailed')?detailReportOptionsList:summaryReportOptionList;
    var filterField = $('#log-report-fields',row);

    $.each(optionsList,function(key,value) {
        filterField.append($("<option></option>")
            .attr("value", key.replace(/"/g, ""))
            .text(value.replace(/"/g, "")));
    });
    filterField.selectpicker();
};

ginger.initFilterInfo = function() {
    $('#auditlogFilter').on('show.bs.modal', function(event) {
        $('#log-filter-title').text(i18n['GINAUDIT0011M']);
        $('#log-path-info','#auditlogFilter').val("/var/log/audit/audit.log");

        var attachEvent = function(row) {
            $(".delete", row).on("click", function() {
                row.remove();

                if ($('#newRow').children().length===0)
                    $("#filterList",'#auditlogFilter').addClass('hidden');
            });

            ginger.populateFilterOptions(row);

            $('.selectpicker',row).change(function() {
                var inputRequiredFieldsList = ['-a','--arch','-c','-e','-f','-ga','-ge','-gi','-hn','-k','-m','-n','-o','-p','-pp','-sc','-se','--session','-su','-sv','-tm','-ua','-ue','-ui','-ul','-uu','-vm','-x'];
                var selectedValue = $(this).val();

                if (selectedValue=="-te" || selectedValue=="-ts" ) {
                    var textField = $('input[type=text]',row);
                    if (textField.length!=0) {
                        var parentDiv = textField.parent();
                        textField.remove();
                        parentDiv.show();
                        var selectOptionHtml = $.parseHTML('<select class="selectpicker col-md-12 timeOption">'+
                            '<option value="now">'+i18n['GINAUDIREPORT0029M']+'</option>'+
                            '<option value="recent">'+i18n['GINAUDIREPORT0030M']+'</option>'+
                            '<option value="today">'+i18n['GINAUDIREPORT0031M']+'</option>'+
                            '<option value="yesterday">'+i18n['GINAUDIREPORT0032M']+'</option>'+
                            '<option value="this-week">'+i18n['GINAUDIREPORT0033M']+'</option>'+
                            '<option value="week-ago">'+i18n['GINAUDIREPORT0034M']+'</option>'+
                            '<option value="this-month">'+i18n['GINAUDIREPORT0035M']+'</option>'+
                            '<option value="this-year">'+i18n['GINAUDIREPORT0036M']+'</option>'+
                            '</select>');
                        parentDiv.append(selectOptionHtml);
                        $('.selectpicker',parentDiv).selectpicker();
                    }
                } else if (inputRequiredFieldsList.indexOf(selectedValue)===-1) {
                    var textField = $('input[type=text]',row);
                    if (textField.length==0) {
                        if ($('.timeOption',row).length!=0) {
                            $('.timeOption',row).parent().append('<input type="text" class="form-control input"  placeholder="'+i18n['GINAUDIT0010M']+'" />');
                            $('.timeOption',row).remove();
                        }
                    }
                    $('input[type=text]',row).val("").parent().hide();
                } else {
                    var textField = $('input[type=text]',row);
                    if (textField.length==0) {
                        if ($('.timeOption',row).length!=0) {
                            $('.timeOption',row).parent().append('<input type="text" class="form-control input"  placeholder="'+i18n['GINAUDIT0010M']+'" />');
                            $('.timeOption',row).remove();
                        }
                    }
                    textField.attr("disabled",false);
                    $('input[type=text]',row).val("").parent().show();
                }
            });
        };

        $(".add-filter",'#auditlogFilter').on("click", function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            $("#filterList").removeClass("hidden");

            var newNode = $.parseHTML('<div class="row" style="margin-bottom:5px;">'+
                '<div class="col-md-5">' +
                '<select class="selectpicker col-md-10" id="log-filter-fields">'+
                '</select>' +
                '</div>'+
                '<div class="col-md-5">'+
                '<input type="text" class="form-control input"  placeholder="'+i18n['GINAUDIT0010M']+'" style="height:40px;"/>' +
                '</div>'+
                '<div class="col-md-2">'+
                '<span class="column-delete btn btn-link delete del-label" style="float:right;">' +
                '<i class="fa fa-trash"></i></span>' +
                '</div>'+
                '</div>'+
                '</div>');

            $('#newRow','#auditlogFilter').append(newNode);
            attachEvent($(newNode));
        });

        $('#log-filter-button-apply').on('click',function() {
            $(".logs-loader").show();
            $('.Audit-log-loader').show();
            var filterarray = [];
            var filtervaluearray = [];
            var filterarray_len,sortarray_len;
            var valuecheck,filtercheck;
            $('#newRow div.row','#auditlogFilter').each(function() {
                filterarray.push($('.selectpicker',$(this)).val());
                filtercheck = $('.selectpicker',$(this)).val();
                if (filtercheck == "-te" || filtercheck =="-ts") {
                    filtervaluearray.push("eventfilter");
                } else if ($('input[type=text]',$(this)).parent().css('display') != 'none') {
                    filtervaluearray.push($('input[type=text]',$(this)).val());
                }
            });
            for (var i=0; i<filtervaluearray.length; i++) {
                if (filtervaluearray[i].length == 0)
                    valuecheck = 1;
            }
            filterarray_len = filterarray.length;
            var sortarray = $.unique(filterarray.sort()).sort();
            sortarray_len = sortarray.length;
            if (filterarray_len != sortarray_len) {
                wok.message.error(i18n['GINAUDIFILTER0027M'],"#addfielderror-message");
                $('.Audit-log-loader').hide();
            } else if (valuecheck == 1) {
                $('.Audit-log-loader').hide();
                wok.message.error(i18n['GINAUDIFILTER0028M'],"#addfielderror-message");
            } else {
                var params = '';
                var logFile= ($('#log-path-info',"#auditlogFilter").val()!='')?'-if '+ $('#log-path-info').val():'';
                params+=logFile;

                if ($('input[type=checkbox]:checked',$('#auditlogFilter')).length!==0) {
                    params.length>0?params+=' -i':params+='-i';
                }

                $('#newRow div.row','#auditlogFilter').each(function() {
                    var field = $('.selectpicker',$(this)).val();
                    var value = "";

                    if ($('.timeOption',$(this)).length!=0) {
                        value = $('.timeOption',$(this)).find('option:selected').val();
                    } else {
                        value = $('input[type=text]',$(this)).val();
                    }
                    var inputRequiredFieldsList = ['-a','--arch','-c','-e','-f','-ga','-ge','-gi','-hn','-k','-m','-n','-o','-p','-pp','-sc','-se','--session','-su','-sv','-tm','-ua','-ue','-ui','-ul','-uu','-vm','-x'];
                    if (inputRequiredFieldsList.indexOf(field)!=-1) {
                        if (value!='') {
                            if (params.length>0) {
                                params+=" ";
                            }
                            params+=field+" "+value;
                        }
                    } else {
                        if (params.length>0) {
                            params+=" ";
                        }
                        params+=field+(value!=''?(" "+value):'');
                    }
                });

                if (params=='') {
                    ginger.getAuditLogs(function(result) {
                        reloadAuditLogs(result);
                    },function(error) {
                        $('.Audit-log-loader').hide();
                        wok.message.error(error.responseJSON.reason,"#alert-modal-audit-filter-container");
                    });
                } else {
                    ginger.filterAuditLogs(params,function(result) {
                        reloadAuditLogs(result);
                    },function(error) {
                        $('.Audit-log-loader').hide();
                        wok.message.error(error.responseJSON.reason,"#alert-modal-audit-filter-container");
                    });
                }

                var reloadAuditLogs =  function(result) {
                    $('#auditlogFilter').modal('hide');
                    wok.message.success(i18n['GINAUDIT0016M'],"#alert-modal-audit-logs-container");
                    $("#audit-logs-table tbody").empty();
                    $("#audit-logs-table").DataTable().destroy();
                    ginger.createAuditLogsTable(result);
                }
            }
        });
    });

    $('#auditlogFilter').on('hide.bs.modal', function(event) {
       $(".logs-loader").hide();
       $('.Audit-log-loader').hide();
       $('#log-path-info',$(this)).val('');
       $('#newRow',$(this)).empty();
       $('#interpret',$(this)).attr('checked',false);
       $('#log-filter-button-apply').off();
       $("#addfielderror-message").empty();
       $("#alert-modal-audit-filter-container").empty();
   });
};

ginger.initSummaryInfo = function() {
    $('#auditlogReport').on('show.bs.modal', function(event) {
        $("#reportType").selectpicker();
        $('#log-path-info','#auditlogReport').val("/var/log/audit/audit.log");

        var attachEvent = function(row) {
            $(".delete", row).on("click", function() {
                row.remove();

                if ($('#newRow','#auditlogReport').children().length===0)
                    $("#filterList",'#auditlogReport').addClass('hidden');
            });

            ginger.populateReportOptions(row);

            $('#log-report-fields.selectpicker',row).change(function() {
                var selectedValue = $(this).val();
                if (selectedValue=="-te" || selectedValue=="-ts" ) {
                    var optionDropdown = $('select.timeOption',row);
                    optionDropdown.empty();
                    var selectOptionHtml = $.parseHTML('<option value="now">'+i18n['GINAUDIREPORT0029M']+'</option>'+
                        '<option value="recent">'+i18n['GINAUDIREPORT0030M']+'</option>'+
                        '<option value="today">'+i18n['GINAUDIREPORT0031M']+'</option>'+
                        '<option value="yesterday">'+i18n['GINAUDIREPORT0032M']+'</option>'+
                        '<option value="this-week">'+i18n['GINAUDIREPORT0033M']+'</option>'+
                        '<option value="week-ago">'+i18n['GINAUDIREPORT0034M']+'</option>'+
                        '<option value="this-month">'+i18n['GINAUDIREPORT0035M']+'</option>'+
                        '<option value="this-year">'+i18n['GINAUDIREPORT0036M']+'</option>');
                    optionDropdown.append(selectOptionHtml);
                    optionDropdown.selectpicker();
                    $('.timeOption',row).show();
                } else {
                    var optionDropdown = $('.timeOption',row);
                    optionDropdown.hide();
                }
            });
        };

        $(".add-filter",'#auditlogReport').on("click", function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            $("#filterList",'#auditlogReport').removeClass("hidden");

            var newNode = $.parseHTML('<div class="row" style="margin-bottom:5px;">'+
                '<div class="col-md-5">' +
                '<select class="selectpicker col-md-10" id="log-report-fields">'+
                '</select>' +
                '</div>'+
                '<div class="col-md-5">'+
                '<select class="selectpicker col-md-10 timeOption">'+
                '</select>' +
                '</div>'+
                '<div class="col-md-2">'+
                '<span class="column-delete btn btn-link delete del-label" style="float:right">' +
                '<i class="fa fa-trash"></i></span>' +
                '</div>'+
                '</div>'+
                '</div>');

            $('#newRow','#auditlogReport').append(newNode);
            attachEvent($(newNode));
        });

        $("#reportType").change(function() {
            $('#newRow','#auditlogReport').empty();
            $('#filterList','#auditlogReport').addClass('hidden');
        });

        $('#log-report-button-apply').on('click',function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            $('.report-loader').show();
            var reportarray = [];
            var reportarray_len,repsortarray_len;
            var filtercheck;
            $('#newRow div.row','#auditlogReport').each(function() {
                reportarray.push($('.selectpicker',$(this)).val());
            });
            reportarray_len = reportarray.length;
            var repsortarray = $.unique(reportarray.sort()).sort();
            repsortarray_len = repsortarray.length;
            if (reportarray_len != repsortarray_len) {
                $('.report-loader').hide();
                wok.message.error(i18n['GINAUDIFILTER0029M'],"#Filterfielderror-message");
                $('#summaryreport').empty();
            } else {
                var params = '';
                var logFile= ($('#log-path-info','#auditlogReport').val()!='')?'-if '+ $('#log-path-info','#auditlogReport').val():'';
                params+=logFile;

                if ($('input[type=checkbox]:checked',$('#auditlogReport')).length!==0) {
                    params.length>0?params+=' -i':params+='-i';
                }

                $('#newRow div.row','#auditlogReport').each(function() {
                    if (params.length>0) {
                        params+=" ";
                    }
                    var field = $('.selectpicker',$(this)).val();
                    var value = "";

                    if ($('.timeOption',$(this)).length!=0) {
                        value = $('.timeOption',$(this)).find('option:selected').val();
                    }
                    params+=field+(value!=undefined?(" "+value):'');
                });

                if (params=='') {
                    ginger.getAuditSummaryReport(function(result) {
                        populateReport(result);
                    },function(error) {
                        $('.report-loader').hide();
                        wok.message.error(error.responseJSON.reason,"#alert-modal-audit-report-container");
                        $('#summaryreport').empty();
                    });
                } else {
                    ginger.getAuditReport(params,function(result) {
                        populateReport(result);
                    },function(error) {
                        $('.report-loader').hide();
                        wok.message.error(error.responseJSON.reason,"#alert-modal-audit-report-container");
                        $('#summaryreport').empty();
                    });
                }

                var populateReport = function(result) {
                    $('#report-details').removeClass("hidden").focus();
                    $('#summaryreport').empty();
                    var columnInfo = {};
                    var summary = [];

                    if (result.length>1) {
                        columnInfo  = result[0]["column_info"];
                        summary   = result[1]["summary"];
                        $("#report-graph-button").removeClass("hidden");
                    } else {
                        summary = result[0]["summary"];
                        $("#report-graph-button").addClass("hidden");
                    }

                    var  details = "";
                    $.each(summary,function(index,info) {
                        if (info!="") {
                            details+=info+"<br>";
                        }
                    });

                    ginger.initGraphDetails(columnInfo);
                    $('#summaryreport').append(details);
                    $("#summaryReportPathInfo").html(i18n['GINAUDIT0017M']).removeClass('hidden');
                    $('.report-loader').hide();
                }
            }
        });

        $("#report-download-button").on("click",function(e) {
            var reportFilePath = '/data/logs/audit_summary_report.txt';
            window.open(reportFilePath, '_blank');
        });
    });

    $('#auditlogReport').on('hide.bs.modal', function(event) {
        $('#log-path-info',$(this)).val('');
        $('#newRow',$(this)).empty();
        $('#interpret',$(this)).attr('checked',false);
        $('#log-report-button-apply').off();
        $("#report-download-button").off();
        $("#report-graph-button").off();
        $('#summaryreport').empty();
        $('#summaryReportPathInfo').empty().hide();
        $("#report-details").addClass("hidden");
        $("#Filterfielderror-message").empty();
        $("#alert-modal-audit-report-container").empty();
    });
};

ginger.initGraphDetails = function(columnInfo) {
    $('#reportGraph').on('show.bs.modal', function(event) {
        $("#graphPathInfo").addClass("hidden");
        $("#graph-name").val(i18n['GINAUDIT0020M']);
        $("#generate-report-graph-button").addClass("hidden");
        var graphColumns = $("#graphColumns");
        graphColumns.empty().selectpicker('destroy');
        $.each(columnInfo,function(key,value) {
            graphColumns.append($("<option></option>")
                .attr("value",value)
                .text(key.replace(/"/g, "")));
        });
        graphColumns.selectpicker();

        var checkFields  = function() {
            if ($("#graphColumns").val()!=null && $("#graphColumns").val().length==2 && $("#graphFormat").val()!="" && $("#graph-name").val()!="") {
                $("#generate-report-graph-button").removeClass("hidden");
            } else {
                $("#generate-report-graph-button").addClass("hidden");
            }
        }

        $("#graphFormat").selectpicker();

        $("#graphColumns").change(function(e) {
            checkFields();
        });

        $("#graph-name").keyup(function(e) {
            checkFields();
        });

        $("#generate-report-graph-button").on('click',function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            $("#graph").empty();
            var columns = $("#graphColumns").val();
            var format = $("#graphFormat").val();
            var graphName = $("#graph-name").val();
            var params = graphName+","+columns.toString()+","+format;
            ginger.getReportGraph(params,function(result) {
                var graphLocation = result[0]['Graph:'];
                $("#graphPathInfo").html(i18n['GINAUDIT0018M'].replace("%1",graphLocation).replace("data","var/lib/wok")).removeClass("hidden");
                window.open(graphLocation, '_blank');
            },function(error) {
                wok.message.error(data.responseJSON.reason,"#alert-modal-audit-graph-container");
            });
        });
    });

    $('#reportGraph').on('hide.bs.modal', function(event) {
        $("#graphColumns").selectpicker('deselectAll');
        $("#graphColumns").selectpicker('destroy');
        $("#graphFormat").selectpicker('destroy');
        $("#graph-name").val('');
        $("#graph").empty();
        $("#generate-report-graph-button").off();
    });
};
