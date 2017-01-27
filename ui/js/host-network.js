/*
 * Copyright IBM Corp, 2015-2017
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

ginger.initOvsBridges = function() {
    if (ginger.ovsbridges !== undefined && !ginger.ovsbridges) {
        $('#ovsbridge-container').remove();
    } else {
        $('#ovsbridge-container').removeClass('hidden');
        var ovsAccordion = wok.substitute($('#ovsBridgesPanel').html());
        $('#ovsbridge-container').append(ovsAccordion);
        ginger.listOvsBridges();
        ginger.initOvsClickHandler();
    }
}

ginger.refreshOvsBridges = function() {
    if ($("#ovsbridgeList .collapse.in").length > 0) {
        $("#ovsbridgeList .collapse.in").one('hidden.bs.collapse', function(e) {
            e.stopPropagation();
            ginger.refreshOvsBridgesUi();
        });
        $("#ovsbridgeList .collapse.in").collapse("hide");
    } else {
        ginger.refreshOvsBridgesUi();
    }
}

ginger.refreshOvsBridgesUi = function() {
    $('#ovsbridgeList').height($('#ovsbridgeList').innerHeight());
    $('#ovsbridge-content-area .wok-mask').removeClass('hidden');
    $('#ovsbridgeList').empty();
    ginger.listOvsBridges();
}

ginger.listOvsBridges = function() {
    ginger.getOvsBridges(function(result) {
        if (result && result.length) {
            result.sort(function(a, b) {
                return a.name.localeCompare(b.name);
            });
            $.each(result, function(i, value) {
                var id = i + 1 + '-' + value.name.toLowerCase();
                var collapse_target = 'bridge-' + id + '-interfaces';
                var name = value.name;
                var bonds = [];
                var interfaces = [];
                var interfaceCount = '';
                var bondCount = '';
                var interfacePlus = '';
                var bondPlus = '';
                var empty_bond_stat = $();
                var empty_iface_stat = $();
                var emptyPortHtml = '<span title="' + i18n['GINNET0056M'] + '">' + i18n['GINNET0056M'] + '</span>';
                $('#bridge-' + id + ' > .column-bonds, #bridge-' + id + ' > .column-interfaces').empty().append(emptyPortHtml);
                if (Object.keys(value.ports).length) {
                    $.each(value.ports, function(j, interface) {
                        if (interface.type === 'bond') {
                            bonds.push(interface.name);
                            $.each(interface.interfaces, function(k, bondiface) {
                                var state = (bondiface.admin_state === 'up' && bondiface.link_state === 'up') ? i18n['GINNET0040M'] : i18n['GINNET0041M'];
                                var stateClass = (bondiface.admin_state === 'up' && bondiface.link_state === 'up') ? 'up' : 'down';
                                var bondIfaceStatItem = $.parseHTML(wok.substitute($("#interfaceBodyTmpl").html(), {
                                    id: bondiface.name,
                                    name: bondiface.name + ' (' + interface.name + ')',
                                    state: state,
                                    stateClass: stateClass,
                                    rxBytes: bondiface.statistics.rx_bytes,
                                    txBytes: bondiface.statistics.tx_bytes,
                                    rxPackets: bondiface.statistics.rx_packets,
                                    txPackets: bondiface.statistics.tx_packets,
                                    rxErr: bondiface.statistics.rx_errors,
                                    txErr: bondiface.statistics.tx_errors
                                }));
                                empty_bond_stat = empty_bond_stat.add(bondIfaceStatItem);
                            });
                        } else if (interface.type === 'interface') {
                            interfaces.push(interface.name);
                            var state = (interface.admin_state === 'up' && interface.link_state === 'up') ? i18n['GINNET0040M'] : i18n['GINNET0041M'];
                            var stateClass = (interface.admin_state === 'up' && interface.link_state === 'up') ? 'up' : 'down';
                            var IfaceStatItem = $.parseHTML(wok.substitute($("#interfaceBodyTmpl").html(), {
                                id: interface.name,
                                name: interface.name,
                                state: state,
                                stateClass: stateClass,
                                rxBytes: interface.statistics.rx_bytes,
                                txBytes: interface.statistics.tx_bytes,
                                rxPackets: interface.statistics.rx_packets,
                                txPackets: interface.statistics.tx_packets,
                                rxErr: interface.statistics.rx_errors,
                                txErr: interface.statistics.tx_errors
                            }));
                            empty_iface_stat = empty_iface_stat.add(IfaceStatItem);
                        }
                    });
                }
                if (interfaces.length) {
                    if (interfaces.length > 3) {
                        interfacePlus = i18n['GINNET0061M'].replace("%1", (interfaces.length - 3));
                        interfaces = interfaces.slice(0, 3);
                        interfaces[2] = interfaces[2] + '...';
                    }
                    interfaceCount = interfaces.join(', ');
                } else {
                    interfaceCount = i18n['GINNET0056M'];
                    interfacePlus = i18n['GINNET0056M'];
                }
                if (bonds.length) {
                    if (bonds.length > 3) {
                        bondPlus = i18n['GINNET0060M'].replace("%1", (bonds.length - 3));
                        bonds = bonds.slice(0, 3);
                        bonds[2] = bonds[2] + '...';
                    }
                    bondCount = bonds.join(', ');
                } else {
                    bondCount = i18n['GINNET0056M'];
                    bondPlus = i18n['GINNET0056M'];
                }
                var ovsbridgeItem = $.parseHTML(wok.substitute($("#ovsbridgeTmpl").html(), {
                    id: id,
                    name: name,
                    bonds: bondCount,
                    interfaces: interfaceCount,
                    bondPlus: bondPlus,
                    interfacePlus: interfacePlus
                }));
                if (empty_bond_stat.length) {
                    $('.bridge-interfaces-body', ovsbridgeItem).append(empty_bond_stat);
                }
                if (empty_iface_stat.length) {
                    $('.bridge-interfaces-body', ovsbridgeItem).append(empty_iface_stat);
                }
                if (empty_iface_stat.length || empty_bond_stat.length) {
                    var stat_handle = $('<span role="button" class="handle" data-toggle="collapse" data-target="#' + collapse_target + '"><i class="fa fa-chevron-down"></i></span>');
                    $('.column-statistics', ovsbridgeItem).append(stat_handle);
                    $('.bridge-interface', ovsbridgeItem).dataGrid({ enableSorting: false });
                } else {
                    $('.column-statistics', ovsbridgeItem).append('--');
                }
                $('#ovsbridgeList').height('auto').append(ovsbridgeItem);
            });
            $('#add_ovsbridge_button').prop('disabled', false);
            $('#ovs_search_input').prop('disabled', false);
            if ($('#ovsbridgeGrid').hasClass('wok-datagrid')) {
                $('#ovsbridgeGrid').dataGrid('destroy');
            }
            $('#ovsbridgeGrid').dataGrid({ enableSorting: false });
            $('#ovsbridge-content-area .wok-mask').addClass('hidden');
            $('#ovsbridgeGrid').removeClass('hidden');
            $("#ovsbridgeList > .wok-datagrid-row> span > [data-toggle=collapse]").click(function(e) {
                e.preventDefault();
                e.stopPropagation();
                $("#ovsbridgeList > .wok-datagrid-row > div > .collapse.in").collapse("hide");
                $($(this).attr("data-target")).collapse("show");
            });
            var ovsBridgeOptions = {
                valueNames: ['name-filter', 'bond-filter', 'interface-filter']
            };
            var ovsBridgeFilterList = new List('ovsbridge-content-area', ovsBridgeOptions);

            ovsBridgeFilterList.sort('name-filter', {
                order: "asc"
            });

        } else {
            var emptyIList = '<div id="no-results" class="bridge"<span class="no-results">' + i18n['GINNET0056M'] + '</span>';
            $('#ovsbridgeList').append(emptyIList);
            if ($('#ovsbridgeGrid').hasClass('wok-datagrid')) {
                $('#ovsbridgeGrid').dataGrid('destroy');
            }
            $('#ovsbridgeGrid').dataGrid({ enableSorting: false });
            $('#ovsbridgeGrid').removeClass('hidden');
            $('#ovsbridge-content-area .wok-mask').addClass('hidden');
        }
    }, function(err) {
        $('#add_ovsbridge_button').prop('disabled', true);
        $('#ovs_search_input').prop('disabled', true);
        $('#ovsbridge-content-area .wok-mask').addClass('hidden');
        wok.message.error(err.responseJSON.reason, '#ovs-alert-container');
    });
}

ginger.initOvsClickHandler = function() {
    $('#add_ovsbridge_button').on('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        wok.window.open('plugins/ginger/host-network-ovs-add.html');
    });
    $('#ovsbridgeGrid').on('click', '.edit-bridge', function(e) {
        e.preventDefault();
        e.stopPropagation();
        ginger.selectedBridge = $(this).data('name');
        wok.window.open('plugins/ginger/host-network-ovs-edit.html');
    });
    $('#ovsbridgeGrid').on('click', '.remove-bridge', function(e) {
        e.preventDefault();
        e.stopPropagation();
        ginger.selectedBridge = $(this).data('name');
        var settings = {
            title: i18n['GINNET0048M'],
            content: i18n['GINNET0049M'].replace("%1", '<strong>' + ginger.selectedBridge + '</strong>'),
            confirm: i18n['GINNET0045M'],
            cancel: i18n['GINNET0046M']
        };
        wok.confirm(settings, function() {
            ginger.delOvsBridge(ginger.selectedBridge, function() {
                var bridgeItem = $('div.wok-datagrid-row[data-name="' + ginger.selectedBridge + '"');
                wok.message.success(i18n['GINNET0050M'].replace("%1", '<strong>' + ginger.selectedBridge + '</strong>'), '#ovs-alert-container');
                bridgeItem.remove();
                refreshOvsBridges();
                $('body').animate({ scrollTop: 0 }, 1000);
            }, function(err) {
                wok.message.error(err.responseJSON.reason, '#ovs-alert-container');
                $('body').animate({ scrollTop: 0 }, 1000);
            });
        }, function() {});
    });
}

ginger.addOvsBridgeModal = function() {
    $('#addButton').prop('disabled', true);
    $('input#bridge[name="name"]').on('input propertychange', function() {
       var ovsNamePattern  = /^[a-zA-Z0-9-_.]+$/;
        if ($(this).val().length != 0) {
          var isValidOvsName = ovsNamePattern.test($(this).val());
          $('#addButton').prop('disabled', !isValidOvsName);
          $(this).toggleClass("invalid-field", !isValidOvsName);
        } else {
            $('#addButton').prop('disabled', true);
        }
    });
    $('#addButton').on('click', function() {
        $('form[name="ovsbridgeadd"]').submit();
    });
    $('form[name="ovsbridgeadd"]').on('submit', function(e) {
        e.preventDefault();
        var name = $("#bridge").val();
        var data = {};
        data = {
            name: name
        };
        ginger.addOvsBridge(data, function() {
            $('form[name="ovsbridgeadd"] input').prop('disabled', true);
            $('#addButton').prop('disabled', true);
            ginger.refreshOvsBridges();
            wok.window.close();
            $('body').animate({ scrollTop: 0 }, 1000);
        }, function(err) {
            wok.message.error(err.responseJSON.reason, '#alert-modal-container');
            $('form[name="ovsbridgeadd"] input').prop('disabled', false);
            $('#addButton').prop('disabled', false);
            $("#bridge").focus();
        });
    });
}

ginger.initNetworkConfig = function() {
    // Redesigned Network Configuration table
    //ginger.renderNetworkConfig();
    ginger.listNetworkConfig = ginger.renderNetworkConfig();
    var buttons = $.parseHTML(wok.substitute($("#networkConfigButtonsTmpl").html(), {}));
    $('#network-configuration-actions').append(buttons);
}

ginger.renderNetworkConfig = function() {
    var networkConfigTable;
    var nwConfigDataSet = new Array();
    var rows_indexes = new Array();

    var updateDataTableSelectAllCtrl = function(table) {
        updateDataTableSelectAllCtrl = function() {};
        var $table = networkConfigTable.table().node();
        var $chkbox_all = $('tbody input[type="checkbox"]', $table);
        var $chkbox_checked = $('tbody input[type="checkbox"]:checked', $table);
        var chkbox_select_all = $('thead input[name="select_all"]', $table).get(0);

        // If none of the checkboxes are checked
        if ($chkbox_checked.length === 0) {
            chkbox_select_all.checked = false;
            if ('indeterminate' in chkbox_select_all) {
                chkbox_select_all.indeterminate = false;
            }

            // If all of the checkboxes are checked
        } else if ($chkbox_checked.length === $chkbox_all.length) {
            chkbox_select_all.checked = true;
            if ('indeterminate' in chkbox_select_all) {
                chkbox_select_all.indeterminate = false;
            }

            // If some of the checkboxes are checked
        } else {
            chkbox_select_all.checked = true;
            if ('indeterminate' in chkbox_select_all) {
                chkbox_select_all.indeterminate = true;
            }
        }
    };

    var updateButtonStatus = function() {
        if (rows_indexes.length && rows_indexes.length === 1) {
            ginger.nwConfiguration.enableActions();
            var networkStatus = networkConfigTable.row(rows_indexes[0]).data()[1];
            var networkType = networkConfigTable.row(rows_indexes[0]).data()[3];
            var networkNicType = networkConfigTable.row(rows_indexes[0]).data()[4];
            var networkModule = networkConfigTable.row(rows_indexes[0]).data()[7];
            // 1 - Enable settings button
            ginger.nwConfiguration.enableSettings();
            if (networkStatus === 'up' || networkStatus === 'unknown') {
                // 2 - Disable up button, enable down & restart
                ginger.nwConfiguration.disableUp();
                ginger.nwConfiguration.enableDown();
                ginger.nwConfiguration.enableRestart();
            } else {
                // 2 - Disable down button, enable down & restart
                ginger.nwConfiguration.enableUp();
                ginger.nwConfiguration.disableDown();
                ginger.nwConfiguration.disableRestart();
            }
            if ((networkModule === 'mlx5_core' || networkModule === 'mlx5-core')
                && networkNicType === 'physical') {
                ginger.nwConfiguration.showSrIov();
            } else {
                ginger.nwConfiguration.hideSrIov();
            }
            if (networkType.toLowerCase() === 'nic') {
                // 4 - Disable delete button
                ginger.nwConfiguration.disableDelete();
            } else {
                ginger.nwConfiguration.enableDelete();
            }
            if(networkType.toLowerCase() == 'bonding' || networkType.toLowerCase() == 'bond' || networkType.toLowerCase() == 'vlan'){
                ginger.nwConfiguration.disableSetOSAPort();
            }else{
                ginger.nwConfiguration.enableSetOSAPort();
            }
        } else if (rows_indexes.length && rows_indexes.length > 1) {
            var networkType = 0;
            ginger.nwConfiguration.enableActions();
            // 1 - Disable settings button;
            ginger.nwConfiguration.disableSettings();
            ginger.nwConfiguration.disableSrIov();
            $.each(rows_indexes, function(key, value) {
                if (networkConfigTable.row(rows_indexes[key]).data()[3] == "nic") {
                    networkType = 1;
                }
                if (networkConfigTable.row(rows_indexes[key]).data()[1] == "up" || networkConfigTable.row(rows_indexes[key]).data()[1] == "unknown") {
                    // 2 - Disable up button, enable down & restart
                    ginger.nwConfiguration.disableUp();
                    ginger.nwConfiguration.enableDown();
                    ginger.nwConfiguration.enableRestart();
                } else if (networkConfigTable.row(rows_indexes[key]).data()[1] == "down") {
                    // 2 - Disable down button, enable down & restart
                    ginger.nwConfiguration.enableUp();
                    ginger.nwConfiguration.disableDown();
                    ginger.nwConfiguration.disableRestart();

                }
if(networkConfigTable.row(rows_indexes[key]).data()[3] == "bonding" || networkConfigTable.row(rows_indexes[key]).data()[3] == "Bond" || networkConfigTable.row(rows_indexes[key]).data()[3] == "vlan"){
                  ginger.nwConfiguration.disableSetOSAPort();
                }
else{
               ginger.nwConfiguration.enableSetOSAPort();
                        }
            });
            if (networkType === 1) {
                ginger.nwConfiguration.disableDelete();
            }
        } else {
            ginger.nwConfiguration.disableActions();
        }
    };

    var loadNetworkConfigDatatable = function(nwConfigDataSet) {
        networkConfigTable = $('#network-configuration').DataTable({
            "processing": true,
            "data": nwConfigDataSet,
            "order": [],
            "dom": '<"pull-right"f><"row"<"col-sm-12"t>><"row datatable-footer"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
            "scrollY": "269px",
            "columnDefs": [{
                "targets": 0,
                "searchable": false,
                "orderable": false,
                "width": "2%",
                "className": "nw-config-align-center",
                "render": function(data, type, full, meta) {
                    return '<input type="checkbox">';
                }
            }, {
                "targets": 1,
                "searchable": false,
                "orderable": false,
                "width": "4%",
                "className": "nw-config-align-center",
                "render": function(data, type, full, meta) {
                    if (data === 'up') {
                        return '<span class="nw-interface-status-enabled enabled" title="' + i18n['GINNET0009M'] + '"><i role="presentation" class="fa fa-power-off"></i></span>';
                    } else {
                        return '<span class="nw-interface-status-disabled disabled" title="' + i18n['GINNET0010M'] + '"><i role="presentation" class="fa fa-power-off"></i></span>';
                    }
                }
            }, {
                "targets": 2,
                "width": "10%"
            }, {
                "targets": 3,
                "width": "7%"
            }, {
                "targets": 4,
                "width": "7%"
            }, {
                "targets": 5,
                'type': 'ip-address',
                "className": "tabular-data",
                "width": "23%"
            }, {
                "targets": 6,
                "searchable": true,
                "orderable": true,
                "width": "13%",
                "render": function(data, type, full, meta) {
                    if (data === true) {
                        return i18n['GINNET0077M'];
                    } else {
                        return i18n['GINNET0078M'];
                    }
                }
            }, {
                "targets": 7,
                "width": "8%"
            }, {
                "targets": 8,
                "className": "tabular-data",
                "width": "25%"
            }],
            "initComplete": function(settings, json) {
                wok.initCompleteDataTableCallback(settings);
                $('#network-configuration-content-area > .wok-mask').addClass('hidden');
            }
        });
        //$(globalNetworkConfigTable.column('1').header()).wrapInner('<span class="sr-only"></span>');
        $('input[name="select_all"]', networkConfigTable.table().container()).prop('checked', false);
        ginger.nwConfiguration.enableRefresh();
        ginger.nwConfiguration.toggleAdd();
        //tableAdd();

        // Handle click on checkbox
        $('#network-configuration tbody').on('click', 'input[type="checkbox"]', function(e) {
            var $row = $(this).closest('tr');

            // Get row ID
            var rowId = networkConfigTable.row($row).index();

            // Determine whether row ID is in the list of selected row IDs
            var index = $.inArray(rowId, rows_indexes);

            // If checkbox is checked and row ID is not in list of selected row IDs
            if (this.checked && index === -1) {
                rows_indexes.push(rowId);

                // Otherwise, if checkbox is not checked and row ID is in list of selected row IDs
            } else if (!this.checked && index !== -1) {
                rows_indexes.splice(index, 1);
            }

            if (this.checked) {
                $row.addClass('active');
            } else {
                $row.removeClass('active');
            }

            // Update state of "Select all" control
            updateDataTableSelectAllCtrl(networkConfigTable);
            updateButtonStatus();

            // Prevent click event from propagating to parent
            e.stopPropagation();
        });

        // Handle click on table cells with checkboxes
        $('#network-configuration').on('click', 'tbody td, thead th:first-child', function(e) {
            $(this).parent().find('input[type="checkbox"]').trigger('click');
        });

        // Handle click on "Select all" control
        $('input[name="select_all"]', networkConfigTable.table().container()).on('click', function(e) {
            if (this.checked) {
                $('tbody input[type="checkbox"]:not(:checked)', networkConfigTable.table().container()).trigger('click');
            } else {
                $('tbody input[type="checkbox"]:checked', networkConfigTable.table().container()).trigger('click');
            }

            // Prevent click event from propagating to parent
            e.stopPropagation();
        });

        // Handle table draw event
        networkConfigTable.on('draw', function() {
            // Update state of "Select all" control
            updateDataTableSelectAllCtrl(networkConfigTable);
        });

    };

    var getNetworkConfiguration = function(callback) {
        ginger.getInterfaces(function(result) {
            nwConfigDataSet.length = 0;
            for (var i = 0; i < result.length; i++) {
                var tempArr = [];
                tempArr.push("");
                tempArr.push(result[i].status);
                tempArr.push(result[i].device);
                tempArr.push(result[i].type);
                tempArr.push(result[i].nic_type);
                tempArr.push(result[i].ipaddr);
                tempArr.push(result[i].rdma_enabled);
                tempArr.push(result[i].module);
                tempArr.push(result[i].macaddr);
                nwConfigDataSet.push(tempArr);
            }
            if (callback !== 'refresh') {
                loadNetworkConfigDatatable(nwConfigDataSet);
            }
        }, function(error) {
            errmsg = i18n['GINNET0035E'] + ' ' + error.responseJSON.reason;
            wok.message.error(errmsg, '#message-network-configuration-container-area', true);
        });
    }
    getNetworkConfiguration();

    var refreshNetworkConfigurationDatatable = function() {
        rows_indexes = [];
        $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
        $('#network-configuration tbody').off('click', 'input[type="checkbox"]');
        $('#network-configuration').off('click', 'tbody td, thead th:first-child');
        $('#network-configuration').off('click', 'input[name="select_all"]');
        networkConfigTable.destroy();
        getNetworkConfiguration('refresh');
        setTimeout(function(){
          loadNetworkConfigDatatable(nwConfigDataSet);
        },1200);
    };

    var networkConfigurationClickHandler = function() {
        // Refresh Button
        $('#network-configuration-content-area').on('click', '#nw-config-refresh-btn', function(e) {
            e.preventDefault();
            e.stopPropagation();
            refreshNetworkConfigurationDatatable();
        });

        // Network Up Button
        $('#network-configuration-content-area').on('click', '.nw-up', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!$(this).parent().is('.disabled')) {
                $('.nw-configuration-action > .dropdown-toggle').dropdown('toggle');
                if ((rows_indexes && rows_indexes.length === 1)) {
                    var selectedIf = networkConfigTable.row(rows_indexes[0]).data();
                    var ifStatus = selectedIf[1];
                    var ifDevice = selectedIf[2];
                    if (ifStatus === "down") {
                        $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                        ginger.enableInterface(ifDevice, "up", function(result) {
                            var message = i18n['GINNET0081M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.success(message, '#message-network-configuration-container-area');
                            refreshNetworkConfigurationDatatable();
                        }, function(err) {
                            $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                            var message = i18n['GINNET0082M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                        });
                    }
                } else if (rows_indexes && rows_indexes.length > 1) {
                    $.each(rows_indexes, function(key, value) {
                        var ifStatus = networkConfigTable.row(rows_indexes[key]).data()[1];
                        var ifDevice = networkConfigTable.row(rows_indexes[key]).data()[2];
                        if (ifStatus === "down") {
                            $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                            ginger.enableInterface(ifDevice, "up", function(result) {
                                var message = i18n['GINNET0081M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.success(message, '#message-network-configuration-container-area');
                                if(key==rows_indexes.length-1) {
                                    refreshNetworkConfigurationDatatable();
                                }
                            }, function(err) {
                                var message = i18n['GINNET0082M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                                if(key==rows_indexes.length-1) {
                                    refreshNetworkConfigurationDatatable();
                                }
                            });
                        }
                    });
                } else {
                    var settings = {
                        content: i18n["GINNET0022M"],
                        confirm: i18n["GINNET0015M"]
                    };
                    wok.confirm(settings, function() {});
                }
            } else {
                return false;
            }
        });

        // Network Down Button
        $('#network-configuration-content-area').on('click', '.nw-down', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!$(this).parent().is('.disabled')) {
                $('.nw-configuration-action > .dropdown-toggle').dropdown('toggle');
                if ((rows_indexes && rows_indexes.length === 1)) {
                    var selectedIf = networkConfigTable.row(rows_indexes[0]).data();
                    var ifStatus = selectedIf[1];
                    var ifDevice = selectedIf[2];
                    if (ifStatus === "up" || ifStatus === "unknown") {
                        $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                        ginger.enableInterface(ifDevice, "down", function(result) {
                            var message = i18n['GINNET0079M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.success(message, '#message-network-configuration-container-area');
                            refreshNetworkConfigurationDatatable();
                        }, function(err) {
                            $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                            var message = i18n['GINNET0080M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                        });
                    }
                } else if (rows_indexes && rows_indexes.length > 1) {
                    $.each(rows_indexes, function(key, value) {
                        var ifStatus = networkConfigTable.row(rows_indexes[key]).data()[1];
                        var ifDevice = networkConfigTable.row(rows_indexes[key]).data()[2];
                        if ((ifStatus === "up") || (ifStatus === "unknown")) {
                            $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                            ginger.enableInterface(ifDevice, "down", function(result) {
                                var message = i18n['GINNET0079M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.success(message, '#message-network-configuration-container-area');
                                if(key==rows_indexes.length-1) {
                                    refreshNetworkConfigurationDatatable();
                                }
                            }, function(err) {
                                var message = i18n['GINNET0080M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                                if(key==rows_indexes.length-1) {
                                    refreshNetworkConfigurationDatatable();
                                }
                            });
                        }
                    });
                } else {
                    var settings = {
                        content: i18n["GINNET0022M"],
                        confirm: i18n["GINNET0015M"]
                    };
                    wok.confirm(settings, function() {});
                }
            } else {
                return false;
            }
        });

        // Network Restart Button
        $('#network-configuration-content-area').on('click', '.nw-restart', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!$(this).parent().is('.disabled')) {
                $('.nw-configuration-action > .dropdown-toggle').dropdown('toggle');
                if ((rows_indexes && rows_indexes.length === 1)) {
                    var selectedIf = networkConfigTable.row(rows_indexes[0]).data();
                    var ifStatus = selectedIf[1];
                    var ifDevice = selectedIf[2];
                    if (ifStatus === "up" || ifStatus === "unknown") {
                        $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                        // First Bring down the interface
                        ginger.enableInterface(ifDevice, "down", function(result) {
                            // Second Bring the interface up back again
                            ginger.enableInterface(ifDevice, "up", function(result) {
                                var message = i18n['GINNET0083M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.success(message, '#message-network-configuration-container-area', true);
                                refreshNetworkConfigurationDatatable();
                            }, function(err) {
                                $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                                var message = i18n['GINNET0084M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                            });
                        }, function(err) {
                            $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                            var message = i18n['GINNET0084M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                        });
                    } else if (ifStatus === "down") {
                        $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                        // Assuming interface is down already and just needs to brought up
                        ginger.enableInterface(ifDevice, "up", function(result) {
                            var message = i18n['GINNET0083M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.success(message, '#message-network-configuration-container-area', true);
                            refreshNetworkConfigurationDatatable();
                        }, function(err) {
                            $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                            var message = i18n['GINNET0084M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                            wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                        });
                    }
                } else if (rows_indexes && rows_indexes.length > 1) {
                    $.each(rows_indexes, function(key, value) {
                        var ifStatus = networkConfigTable.row(rows_indexes[key]).data()[1];
                        var ifDevice = networkConfigTable.row(rows_indexes[key]).data()[2];
                        //this is for up
                        if (ifStatus === 'up' || ifStatus === "unknown") {
                            $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                            // First Bring down the interface
                            ginger.enableInterface(ifDevice, "down", function(result) {
                                // Second Bring the interface up back again
                                ginger.enableInterface(ifDevice, "up", function(result) {
                                    var message = i18n['GINNET0083M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                    wok.message.success(message, '#message-network-configuration-container-area', true);
                                    if(key==rows_indexes.length-1) {
                                        refreshNetworkConfigurationDatatable();
                                    }
                                }, function(err) {
                                    var message = i18n['GINNET0084M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                    wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                                    if(key==rows_indexes.length-1) {
                                        refreshNetworkConfigurationDatatable();
                                    }
                                });
                            }, function(err) {
                                $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                                var message = i18n['GINNET0084M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                            });
                        } else if (value.status == 'down') {
                            // Assuming interface is down already and just needs to brought up
                            ginger.enableInterface(value.device, "up", function(result) {
                                var message = i18n['GINNET0083M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.success(message, '#message-network-configuration-container-area', true);
                            }, function(err) {
                                $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                                var message = i18n['GINNET0084M'].replace('%1', '<strong>' + ifDevice + '</strong>');
                                wok.message.error(message + " " + error.responseJSON.reason, '#message-network-configuration-container-area', true);
                            });
                        }
                    });
                } else {
                    var settings = {
                        content: i18n["GINNET0022M"],
                        confirm: i18n["GINNET0015M"]
                    };
                    wok.confirm(settings, function() {});
                }
            } else {
                return false;
            }
        });

        // Network SR-IOV Button
        $('#network-configuration-content-area').on('click', '.nw-sriov', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!$(this).parent().is('.disabled') && (rows_indexes && rows_indexes.length === 1)) {
                var selectedIf = networkConfigTable.row(rows_indexes[0]).data();
                ginger.selectedInterface = selectedIf[2];
                wok.window.open('plugins/ginger/host-network-enable-sriov.html');
            } else {
                return false;
            }
        });

        // Network Delete Button
        $('#network-configuration-content-area').on('click', '.nw-delete', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!$(this).parent().is('.disabled')) {
                var selectedIf = networkConfigTable.row(rows_indexes[0]).data();
                var ifDevice = selectedIf[2];
                var ifType = selectedIf[3];
                $('.nw-configuration-action > .dropdown-toggle').dropdown('toggle');
                if (ifDevice && (rows_indexes.length == 1) && (ifType).toLowerCase() != 'nic') {
                    ginger.selectedNWInterface = ifDevice;
                    var settings = {
                        content: i18n['GINNET0028M'].replace("%1", '<strong>' + ginger.selectedNWInterface + '</strong>'),
                        confirm: i18n["GINNET0015M"]
                    };
                    wok.confirm(settings, function() {
                        $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                        ginger.deleteInterface(ginger.selectedNWInterface, function(result) {
                            var message = i18n['GINNET0085M'].replace('%1', '<strong>' + ginger.selectedNWInterface + '</strong>');
                            wok.message.success(message, '#message-network-configuration-container-area', true);
                            //Re-load the network interfaces after delete action
                            refreshNetworkConfigurationDatatable();
                        }, function(err) {
                            $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                            var message = i18n['GINNET0086M'].replace('%1', '<strong>' + ginger.selectedNWInterface + '</strong>');
                            wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                        });
                    }, function() {
                        $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                    });
                } else if (rows_indexes && rows_indexes.length > 1) {
                    var checkNetworkType = 0;
                    $.each(rows_indexes, function(key, value) {
                        selectedIf = networkConfigTable.row(rows_indexes[key]).data();
                        ifDevice = selectedIf[2];
                        ifType = selectedIf[3];
                        if ((ifType).toLowerCase() == "nic") {
                            checkNetworkType = 1;
                        }
                    });
                    if (checkNetworkType == 0) {
                        $.each(rows_indexes, function(key, value) {
                            ginger.selectedNWInterface = networkConfigTable.row(rows_indexes[key]).data()[2];
                            var settings = {
                                content: i18n['GINNET0028M'].replace("%1", '<strong>' + ginger.selectedNWInterface + '</strong>'),
                                confirm: i18n["GINNET0015M"]
                            };
                            wok.confirm(settings, function() {
                                $('#network-configuration-content-area > .wok-mask').removeClass('hidden');
                                ginger.deleteInterface(ginger.selectedNWInterface, function(result) {
                                    var message = i18n['GINNET0085M'].replace('%1', '<strong>' + ginger.selectedNWInterface + '</strong>');
                                    wok.message.success(message, '#message-network-configuration-container-area', true);
                                    refreshNetworkConfigurationDatatable();
                                }, function(err) {
                                    $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                                    var message = i18n['GINNET0086M'].replace('%1', '<strong>' + ginger.selectedNWInterface + '</strong>');
                                    wok.message.error(message + " " + err.responseJSON.reason, '#message-network-configuration-container-area', true);
                                });
                            }, function() {
                                $('#network-configuration-content-area > .wok-mask').addClass('hidden');
                            });
                        });
                    }
                }
            } else {
                return false;
            }
        });

        // Network Settings Button
        $('#network-configuration-content-area').on('click', '.nw-settings', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (!$(this).parent().is('.disabled')) {
                $('.nw-configuration-action > .dropdown-toggle').dropdown('toggle');
                if ((rows_indexes && rows_indexes.length === 1)) {
                    var selectedIf = networkConfigTable.row(rows_indexes[0]).data();
                    var ifDevice = selectedIf[2];
                    var ifType = selectedIf[3];
                    ginger.selectedInterface = (ifDevice === "undefined" ? null : ifDevice);
                    ginger.retrieveCfgInterface(ginger.selectedInterface, function(result) {
                        if ((ifType).toLowerCase() == "vlan") {
                            wok.window.open('plugins/ginger/host-network-vlan.html');
                        } else if (((ifType).toLowerCase() == "bond") || ((ifType).toLowerCase() == "bonding")) {
                            wok.window.open('plugins/ginger/host-network-bond.html');
                        } else if (((ifType).toLowerCase() == "ethernet") || ((ifType).toLowerCase() == "nic")) {
                            // condition nic should go away if #104 to be correct and resolved
                            wok.window.open('plugins/ginger/host-network-settings.html');
                        }
                    }, function(error) {
                        wok.message.error(i18n['GINNET0034E'].replace("%1", '<strong>' + ginger.selectedInterface + '</strong>'), '#message-network-configuration-container-area', true);
                        //Re-load the network interfaces after to clear other inactive interfaces without ifcfg files
                        refreshNetworkConfigurationDatatable();
                    });
                } else {
                    var settings = {
                        content: i18n["GINNET0022M"],
                        confirm: i18n["GINNET0015M"]
                    };
                    wok.confirm(settings, function() {});
                }
            } else {
                return false;
            }
        });

        // Network Add Bond
        $('#network-configuration-content-area').on('click', '.nw-add-bond', function(e) {
            e.preventDefault();
            e.stopPropagation();
            wok.window.open('plugins/ginger/host-network-bond.html');
        });

        // Network VLAN
        $('#network-configuration-content-area').on('click', '.nw-add-vlan', function(e) {
            e.preventDefault();
            e.stopPropagation();
            wok.window.open('plugins/ginger/host-network-vlan.html');
        });

    }
    networkConfigurationClickHandler();
    return {
        refreshNetworkConfigurationDatatable: refreshNetworkConfigurationDatatable,
        rows_indexes : rows_indexes
    };
}

ginger.loadGlobalNetworkConfig = function() {
    var globalNetworkConfigTable;
    var dataSet = new Array();

    var loadGlobalNetworkConfigDatatable = function(dataSet) {
        globalNetworkConfigTable = $('#global-network').DataTable({
            "processing": true,
            "data": dataSet,
            "bSort": false,
            "dom": 't',
            "scrollY": "234px",
            "columns": [{
                title: "DNS",
                className: 'col-sm-2',
                render: function(r, t, data, meta) {
                    if (data[0] !== 'add-new-dns') {
                        return '<span class="dns-readonly">' + data + '</span>' +
                            '<span class="dns-edit hidden">' +
                            '<label for="dns-input-' + meta.row + '"><span class="sr-only">DNS:</span>' +
                            '<input type="text" value="' + data + '" name="dns-edit[]" id="dns-input-' + meta.row + '" class="form-control" readonly="readonly">' +
                            '</label>' +
                            '</span>'
                    } else {
                        return '<span class="dns-add-readonly">&nbsp;</span>' +
                            '<span class="dns-add-edit hidden">' +
                            '<label for="dns-input-' + meta.row + '"><span class="sr-only">DNS:</span>' +
                            '<input type="text" value="" name="dns-add" id="dns-input-' + meta.row + '" class="form-control" readonly="readonly">' +
                            '</label>' +
                            '</span>'
                    }
                }
            }, {
                title: "Actions",
                render: function(r, t, data, meta) {
                    if (data[0] !== 'add-new-dns') {
                        return '<span class="column-dns-actions">' +
                            '<span class="readonly-dns-actions">' +
                            '<button class="btn btn-link edit-dns btn-xs">' +
                            '<i role="presentation" class="fa fa-pencil"></i> <span>' + i18n['GINNET0074M'] + '</span>' +
                            '</button>' +
                            '<button class="btn btn-link remove-dns btn-xs">' +
                            '<i role="presentation" class="fa fa-trash-o"></i> <span>' + i18n['GINNET0064M'] + '</span>' +
                            '</button>' +
                            '</span>' +
                            '<span class="editable-dns-actions hidden">' +
                            '<button class="btn btn-primary save-dns btn-xs">' + i18n['GINNET0065M'] + '</button>' +
                            '<button class="btn btn-primary cancel-dns btn-xs">' + i18n['GINNET0066M'] + '</button>' +
                            '</span>' +
                            '</span>'
                    } else {
                        return '<span class="column-dns-actions">' +
                            '<span class="readonly-dns-add-actions">' +
                            '<button class="btn btn-primary add-dns btn-xs">' +
                            '<i role="presentation" class="fa fa-plus-circle"></i> <span>' + i18n['GINNET0067M'] + '</span>' +
                            '</button>' +
                            '</span>' +
                            '<span class="editable-dns-add-actions hidden">' +
                            '<button class="btn btn-primary save-add-dns btn-xs" disabled="disabled">' + i18n['GINNET0065M'] + '</button>' +
                            '<button class="btn btn-primary cancel-add-dns btn-xs">' + i18n['GINNET0066M'] + '</button>' +
                            '</span>' +
                            '</span>'
                    }
                }
            }],
            createdRow: function(row, data, dataIndex) {
                $(row).find('td:eq(0)').parent().attr('data-dns', data[0]); // This ensures that the data attribute will always get the first position in the datatables' data array
            }
        });
        $(globalNetworkConfigTable.column('1').header()).wrapInner('<span class="sr-only"></span>');
        $('#network-global-configuration-content-area > .wok-mask').addClass('hidden');
        tableAdd();
    };

    var tableAdd = function() {
        globalNetworkConfigTable.row.add(['add-new-dns']).draw(false);
    };
    var tableClickHandler = function() {
        $('#network-global-configuration-content-area').on('click', '.edit-dns', function(e) {
            var row = $(this).parents('tr');
            var complete = function() {
                row.find('.readonly-dns-actions').addClass('hidden');
                row.find('.editable-dns-actions').removeClass('hidden');
                row.find('.dns-readonly').addClass('hidden');
                row.find('.dns-edit').removeClass('hidden');
                row.find('input').prop('readonly', false);
            }
            var toggleEdit = function() {
                if ($(row.parent()).find('.editable-dns-actions').not('.hidden').length) {
                    $(row.parent()).find('.editable-dns-actions').not('.hidden').each(function() {
                        if (!$(this).parents('tr').find('label.has-error').length) {
                            wok.confirm({
                                title: i18n['GINNET0068M'],
                                content: i18n['GINNET0069M'],
                                confirm: i18n['GINNET0072M'],
                                cancel: i18n['GINNET0073M']
                            }, function() {
                                $(row.parent()).find('tr').not(row).each(function() {
                                    $('.save-dns', this).trigger('click');
                                });
                                complete();
                            }, function() {
                                $(row.parent()).find('tr').not(row).each(function() {
                                    $('.cancel-dns', this).trigger('click');
                                });
                                complete();
                            });
                        } else {
                            complete();
                        }
                    });
                } else {
                    complete();
                }
            };
            var toggleSave = function() {
                $(row.parent()).find('.editable-dns-add-actions').not('.hidden').each(function() {
                    if (!$(this).parents('tr').find('label.has-error').length) {
                        wok.confirm({
                            title: i18n['GINNET0068M'],
                            content: i18n['GINNET0069M'],
                            confirm: i18n['GINNET0072M'],
                            cancel: i18n['GINNET0073M']
                        }, function() {
                            $(row.parent()).find('tr').not(row).each(function() {
                                $('.save-add-dns', this).trigger('click');
                            });
                            complete();
                        }, function() {
                            $(row.parent()).find('tr').not(row).each(function() {
                                $('.cancel-add-dns', this).trigger('click');
                            });
                            complete();
                        });
                    } else {
                        wok.confirm({
                            title: i18n['GINNET0070M'],
                            content: i18n['GINNET0071M'],
                            confirm: i18n['GINNET0074M'],
                            cancel: i18n['GINNET0073M']
                        }, function() {
                            $('label.has-error input', row.parent()).focus();
                        }, function() {
                            $('.cancel-add-dns', row.parent()).trigger('click');
                            complete();
                        });
                    }
                });
            };

            if ($(row.parent()).find('.dns-add-edit').not('.hidden').length) {
                if ($(row.parent()).find('.dns-add-edit input').val().length) {
                    toggleSave();
                } else {
                    $('.cancel-add-dns', row.parent()).trigger('click');
                    toggleEdit();
                }
            } else {
                toggleEdit();
            }
        });

        $('#network-global-configuration-content-area').on('click', '.save-dns', function(e) {
            var row = $(this).parents('tr');
            var cell = $(this).parents('tr').find('td:eq(0)');
            var newDns = cell.find('span > label > input').val();
            globalNetworkConfigTable.cell(cell).data(newDns);
            globalNetworkConfigTable.row(row).invalidate().draw();
        });
        $('#network-global-configuration-content-area').on('click', '.cancel-dns', function(e) {
            var row = $(this).parents('tr');
            globalNetworkConfigTable.row(row).invalidate().draw();
        });
        $('#network-global-configuration-content-area').on('click', '.remove-dns', function(e) {
            globalNetworkConfigTable.row($(this).parents('tr')).remove().draw();
        });
        $('#network-global-configuration-content-area').on('click', '.add-dns', function(e) {
            var row = $(this).parents('tr');
            $(row.parent()).find('tr').not(row).each(function() {
                $('.cancel-dns', this).trigger('click');
            });
            $(this).parents('.column-dns-actions').find('.readonly-dns-add-actions').addClass('hidden');
            $(this).parents('.column-dns-actions').find('.editable-dns-add-actions').removeClass('hidden');
            $(this).parents('tr').find('.dns-add-readonly').addClass('hidden');
            $(this).parents('tr').find('.dns-add-edit').removeClass('hidden');
            $(this).parents('tr').find('input').prop('readonly', false);
        });
        $('#network-global-configuration-content-area').on('click', '.save-add-dns', function(e) {
            var row = $(this).parents('tr');
            var cell = $(this).parents('tr').find('td:eq(0)');
            var newDns = cell.find('span > label > input').val();
            globalNetworkConfigTable.row($(this).parents('tr')).remove().draw();
            globalNetworkConfigTable.row.add([newDns]).draw();
            tableAdd();
        });
        $('#network-global-configuration-content-area').on('click', '.cancel-add-dns', function(e) {
            var row = $(this).parents('tr');
            var staticRowsLength = globalNetworkConfigTable.columns(0).data().eq(0).sort().length;
            var uniqueRowsLength = globalNetworkConfigTable.columns(0).data().eq(0).sort().unique().length;
            if (staticRowsLength > uniqueRowsLength) {
                globalNetworkConfigTable.row($(this).parents('tr')).remove().draw();
            } else {
                globalNetworkConfigTable.row(row).invalidate().draw();
            }
        });

        $('#network-global-configuration-content-area').on('click', '#nw-global-config-refresh-btn', function(e) {
            $('#network-global-configuration-content-area > .wok-mask').removeClass('hidden');
            globalNetworkConfigTable.destroy();
            getNetworkGlobalConfiguration('refresh');
            loadGlobalNetworkConfigDatatable(dataSet);
        });

        $('#network-global-configuration-content-area').on('click', '#nw-global-config-apply-btn', function(e) {
            var global_info = {};
            var globalDnsAddresses;
            var globalDnsGateway = $('#global-network-config-gateway');
            var applyData = function() {
                globalDnsAddresses = globalNetworkConfigTable.columns(0).data().eq(0).unique();
                globalDnsAddresses.pop(); // it removes the last empy row from the 1d array
                if (globalDnsAddresses.length > 0) {
                    dns = []
                    for (var i = 0; i < globalDnsAddresses.length; i++) {
                        dnsValue = globalDnsAddresses[i];
                        dns.push(dnsValue);
                    }
                    global_info['nameservers'] = dns;
                } else {
                    global_info['nameservers'] = '[]'
                }
                if (globalDnsGateway.val() != "") {
                    global_info['gateway'] = globalDnsGateway.val();
                }
                $('#network-global-configuration-content-area > .wok-mask').removeClass('hidden');
                ginger.updateNetworkGlobals(global_info, function(result) {
                    var message = i18n['GINNET0024M'] + " " + i18n['GINNET0020M'];
                    globalNetworkConfigTable.destroy();
                    getNetworkGlobalConfiguration();
                    wok.message.success(message, '#message-nw-global-container-area');
                    $('#network-global-configuration-content-area > .wok-mask').addClass('hidden');
                }, function(error) {
                    $('#network-global-configuration-content-area > .wok-mask').addClass('hidden');
                    var message = i18n['GINNET0024M'] + " " + i18n['GINNET0021M'] + " " + error.responseJSON.reason;
                    wok.message.error(error.responseJSON.reason, '#message-nw-global-container-area', true);
                });
            }

            if ($('.dns-edit, .dns-add-edit').not('.hidden').length) {
                wok.confirm({
                    title: i18n['GINNET0068M'],
                    content: i18n['GINNET0076M'],
                    confirm: i18n['GINNET0075M'],
                    cancel: i18n['GINNET0073M']
                }, function() {
                    applyData();
                }, null);
            } else {
                applyData();
            }
        });
    }
    // disable nw-settings for Ubuntu
    ginger.getHostDetails(function(result) {
        if (result["os_distro"] == "Ubuntu") {
            $(".nw-configuration-action > .btn").hide();
        }
    });
    tableClickHandler();

    var tableInputValidation = function() {
        $('#global-network').on('input propertychange', 'input[type="text"]', function(e) {
            var row = $(this).parents('tr');
            var currInput = $(this).val();
            var inputs = new Array();
            if(currInput.trim() == ""){
              $(this).parent().addClass('has-error');
              $(row).find('.save-add-dns,.save-dns').prop('disabled', true);
            } else {
              if((ginger.isValidIPv6(currInput)) || ginger.validateIp(currInput) || ginger.validateHostName(currInput)){
                // This will make sure that if the user has typed an IP address but not saved it, it will prevent typing the same value in another input:
                $('#global-network input[type="text"]').not(this).each(function() {
                    inputs.push($(this).val());
                });
                if (_.includes(inputs, currInput)) {
                    $(this).parent().addClass('has-error');
                    $(row).find('.save-add-dns,.save-dns').prop('disabled', true);
                } else {
                    $(this).parent().removeClass('has-error');
                    $(row).find('.save-add-dns,.save-dns').prop('disabled', false);
                }
             } else {
               $(this).parent().addClass('has-error');
               $(row).find('.save-add-dns,.save-dns').prop('disabled', true);
             }
           }
        });
    }
    tableInputValidation();

    var gatewayInputValidation = function() {
        $('#global-network-config-gateway').on('input propertychange', function(e) {
            var gatewayIP = $('#global-network-config-gateway').val();

            if (gatewayIP.trim() == "") {
                $(this).parent().toggleClass('has-error', true);
                $('#nw-global-config-apply-btn').prop('disabled', true);
            } else {
                $(this).parent().toggleClass("has-error", !((ginger.isValidIPv6(gatewayIP)) || ginger.validateIp(gatewayIP)));
                $('#nw-global-config-apply-btn').prop('disabled', !((ginger.isValidIPv6(gatewayIP)) || ginger.validateIp(gatewayIP)));
            }
        });
    }
    gatewayInputValidation();

    var getNetworkGlobalConfiguration = function(callback) {
        ginger.getNetworkGlobals(function(dnsAddresses) {
            if ("nameservers" in (dnsAddresses)) {
                dataSet.length = 0;
                var DNSNameServers = dnsAddresses.nameservers
                for (var i = 0; i < DNSNameServers.length; i++) {
                    dataSet.push([DNSNameServers[i]]);
                }
            }
            if ("gateway" in (dnsAddresses)) {
                $('#global-network-config-gateway').val(dnsAddresses.gateway);
            }
            if (callback !== 'refresh') {
                loadGlobalNetworkConfigDatatable(dataSet);
            }
        }, function(error) {
            errmsg = i18n['GINNET0035E'] + ' ' + error.responseJSON.reason;
            wok.message.error(errmsg, '#message-nw-global-container-area', true);
        });
    }
    getNetworkGlobalConfiguration();
};


ginger.initNetwork = function() {
    $(".content-area", "#gingerHostNetwork").css("height", "100%");
    ginger.getHostDetails(function(result) {
        ginger.hostarch = result["architecture"];
        ginger.getCapabilities(function(result) {
            $.each(result, function(enableItem, capability) {
                var itemLowCase = enableItem.toLowerCase();
                switch (itemLowCase) {
                    case "network":
                        ginger.initNetworkConfig();
                        ginger.loadGlobalNetworkConfig();
                        break;
                    case "cfginterfaces":
                        ginger.cfginterfaces = capability;
                        ginger.cfginterfaces;
                        break;
                    case "ovsbridges":
                        ginger.ovsbridges = capability;
                        ginger.initOvsBridges();
                        break;
                }
            });
        });
    });
};

// Redesigned Network Configuration cfginterfaces Button status handlers

ginger.changeButtonStatus = function(buttonIds, state) {
    $.each(buttonIds, function(i, buttonId) {
        if (state) {
            $('#' + buttonId).show();
        } else {
            $('#' + buttonId).hide();
        }
    });
}

// Redesigned Network Configuration Button status handlers

ginger.nwConfiguration = {};

ginger.nwConfiguration.enableAllButtons = function() {
    ginger.nwConfiguration.enableActions();
    ginger.nwConfiguration.enableRefresh();
    ginger.nwConfiguration.enableAdd();
}

ginger.nwConfiguration.disableAllButtons = function() {
    ginger.nwConfiguration.disableActions();
    ginger.nwConfiguration.disableRefresh();
    ginger.nwConfiguration.disableAdd();
}

ginger.nwConfiguration.enableActions = function() {
    $(".nw-configuration-action > .btn").prop("disabled", false);
};

ginger.nwConfiguration.disableActions = function() {
    $(".nw-configuration-action").removeClass('open');
    $(".nw-configuration-action > .btn").prop("disabled", true);
};

ginger.nwConfiguration.enableUp = function() {
    $('.nw-configuration-action .nw-up').parent().removeClass('disabled');
};

ginger.nwConfiguration.disableUp = function() {
    $('.nw-configuration-action .nw-up').parent().addClass('disabled');
};

ginger.nwConfiguration.enableDown = function() {
    $('.nw-configuration-action .nw-down').parent().removeClass('disabled');
};

ginger.nwConfiguration.disableDown = function() {
    $('.nw-configuration-action .nw-down').parent().addClass('disabled');
};

ginger.nwConfiguration.enableRestart = function() {
    $('.nw-configuration-action .nw-restart').parent().removeClass('disabled');
};

ginger.nwConfiguration.disableRestart = function() {
    $('.nw-configuration-action .nw-restart').parent().addClass('disabled');
};

ginger.nwConfiguration.showSrIov = function() {
    $('.nw-configuration-action .nw-sriov').parent().removeClass('hidden');
};

ginger.nwConfiguration.hideSrIov = function() {
    $('.nw-configuration-action .nw-sriov').parent().addClass('hidden');
};
ginger.nwConfiguration.enableSrIov = function() {
    $('.nw-configuration-action .nw-sriov').parent().removeClass('disabled');
};

ginger.nwConfiguration.disableSrIov = function() {
    $('.nw-configuration-action .nw-sriov').parent().addClass('disabled');
};

ginger.nwConfiguration.enableDelete = function() {
    $('.nw-configuration-action .nw-delete').parent().removeClass('disabled');
};

ginger.nwConfiguration.disableDelete = function() {
    $('.nw-configuration-action .nw-delete').parent().addClass('disabled');
};

ginger.nwConfiguration.enableSettings = function() {
    $('.nw-configuration-action .nw-settings').parent().removeClass('disabled');
};

ginger.nwConfiguration.disableSettings = function() {
    $('.nw-configuration-action .nw-settings').parent().addClass('disabled');
};

ginger.nwConfiguration.enableRefresh = function() {
    $("#nw-config-refresh-btn").prop("disabled", false);
};

ginger.nwConfiguration.disableRefresh = function() {
    $("#nw-config-refresh-btn").prop("disabled", true);
};

ginger.nwConfiguration.enableAdd = function() {
    $(".nw-configuration-add > .btn").prop("disabled", false);
};

ginger.nwConfiguration.disableAdd = function() {
    $(".nw-configuration-add > .btn").prop("disabled", true);
};

ginger.nwConfiguration.showAdd = function() {
    ginger.nwConfiguration.enableAdd();
    $(".nw-configuration-add").show();
};

ginger.nwConfiguration.hideAdd = function() {
    ginger.nwConfiguration.disableAdd();
    $(".nw-configuration-add").hide();
};

ginger.nwConfiguration.toggleAdd = function() {
    if (ginger.cfginterfaces) {
        ginger.nwConfiguration.showAdd();
    } else {
        ginger.nwConfiguration.hideAdd();
    }
};

ginger.nwConfiguration.disableSetOSAPort = function() {
    $("#nw-osa-port-button").parent().addClass('disabled');
};

ginger.nwConfiguration.enableSetOSAPort = function() {
    $("#nw-osa-port-button").parent().removeClass('disabled');
};
