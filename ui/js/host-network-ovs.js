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

ginger.editOvsBridgeModal = function(){
 ginger.getOvsBridge(ginger.selectedBridge, function(result){
    var emptyGrid = [
        '<div role="row">',
            '<span role="gridcell" class="column-empty">',
                i18n['GINNET0055M'],
            '</span>',
        '</div>'
    ].join('');
    $('.ovs-selected-bridge', '#modalWindow').text(ginger.selectedBridge);
    $('.ovs-bond-body').append(emptyGrid);
    $('.ovs-interface-body').append(emptyGrid);
    if(Object.keys(result.ports).length){
        $.each(result.ports, function(i,value){
            if(value.type === 'bond') {
                $('.ovs-bond-body > div > .column-empty').parent().remove();
                var bondName = value.name;
                var bondInterfaces = value.interfaces;
                // Init Bond Interfaces Select
                var bondInterfacesOptionHtml = '';
                var bondInterfacesText = '';
                for (var i = 0; i < bondInterfaces.length; i++) {
                    bondInterfacesOptionHtml += '<option value="'+ bondInterfaces[i].name + '">' + bondInterfaces[i].name + '</option>';
                    (i + 1 < bondInterfaces.length) ? bondInterfacesText += bondInterfaces[i].name +', ' : bondInterfacesText += bondInterfaces[i].name;
                }
                // Call when availabel interfaces when edit only
                var bridgeBondItem = $.parseHTML(wok.substitute($("#bondsBodyTmpl").html(), {
                    id: i,
                    name: bondName,
                    interfaces: bondInterfacesText
                }));
                // Compare available interfaces!!!
                $(bridgeBondItem).find('select[name="interface_del"]').append(bondInterfacesOptionHtml);

                $('.ovs-bond-body').append(bridgeBondItem);
            }else if(value.type === 'interface') {
                $('.ovs-interface-body > div > .column-empty').parent().remove();
                var interfaceName = value.name;
                var interfaceMac = value.mac_in_use;
                var bridgeInterfaceItem = $.parseHTML(wok.substitute($("#interfacesBodyTmpl").html(), {
                    id: i,
                    name: interfaceName,
                    address: interfaceMac
                }));
                $('.ovs-interface-body').append(bridgeInterfaceItem);
            }
        });
    }
    $('.bridge-bonds').dataGrid({enableSorting: false});
    $('.bridge-interfaces').dataGrid({enableSorting: false});
    ginger.editBridgeClickHandlers();
  },
  function(){
    wok.message.error(err.responseJSON.reason, '#alert-modal-container', true);
  });
}


ginger.editBridgeClickHandlers = function() {

    // Add Bond block

    $('#ovs-edit-bond-add-button').on('click',function(e){
        e.preventDefault();
        e.stopPropagation();
        if(!$('.new-bond').length){
            $('.column-empty','.ovs-bond-body').addClass('hidden');
            var newBridgeBondItem = $.parseHTML(wok.substitute($("#bondAddBodyTmpl").html(), {
                name: ginger.selectedBridge
            }));
            ginger.loadAvailableInterfaces($('select[name="new-bond-interfaces"]',newBridgeBondItem));
            $('.ovs-bond-body').prepend(newBridgeBondItem);
            $('.bridge-bonds').dataGrid('destroy');
            $('.bridge-bonds').dataGrid({enableSorting: false});
        }
    });

    // Save Add New Bond block

    $('.bridge-bonds').on('click','.save-new-bond',function(e){
        e.preventDefault();
        e.stopPropagation();
        $('.bootstrap-select.open').removeClass('open');
        var row = $(this).parent().parent();
        var name = $('input[name="new-bond-name"]', row).val();
        var ifaces = $('select[name="new-bond-interfaces"]', row).val();
        if(!ifaces){
            $('.bridge-bonds .btn-group.bootstrap-select > button').click();
        }else if(!name){
            $('input[name="new-bond-name"]').focus();
        }else {
            var data = {};
            data = {
                bond: name,
                interfaces: ifaces
            };
            ginger.addOvsBridgeBond(ginger.selectedBridge, data, function() {
                  $('input[name="new-bond-name"]', row).prop('disabled', true);
                  $('select[name="new-bond-interfaces"]', row).prop('disabled', true);
                  $('.save-new-bond', row).prop('disabled', true);
                  $('.cancel-new-bond', row).prop('disabled', true);
                  row.remove();
                  wok.message.success(i18n['GINNET0058M'].replace("%1", '<strong>'+name+'</strong>'), '#alert-modal-container',true);
                  ginger.refreshThisBridgeBonds(ginger.selectedBridge);
              }, function(err) {
                  wok.message.error(err.responseJSON.reason, '#alert-modal-container', true);
                  $('input[name="new-bond-name"]', row).prop('disabled', false);
                  $('select[name="new-bond-interfaces"]', row).prop('disabled', false);
                  $('.save-new-bond', row).prop('disabled', false);
                  $('.cancel-new-bond', row).prop('disabled', false);
              });
        }
    });

    // Cancel Add New Bond block

    $('.bridge-bonds').on('click','.cancel-new-bond',function(e){
        e.preventDefault();
        e.stopPropagation();
        $('.bootstrap-select.open').removeClass('open');
        $('.column-empty','.ovs-bond-body').removeClass('hidden');
        $(this).parent().parent().remove();
        $('.bridge-interfaces').dataGrid('destroy');
        $('.bridge-interfaces').dataGrid({enableSorting: false});
    });

    // Modify Bond block

    $('.bridge-bonds').on('click','.modify-bond',function(e){
        e.preventDefault();
        e.stopPropagation();
        var row = $(this).parent().parent().parent();
        $('.interfaces-readonly',row).addClass('hidden');
        $('.readonly-bond-actions',row).addClass('hidden');
        $('.modify-bond-on',row).removeClass('hidden');
        $('.editable-bond-actions',row).removeClass('hidden');
        $('select[name="interface_del"]', row).prop('disabled',false);
        $('select[name="interface_add"]', row).prop('disabled',false);
        $('select[name="interface_del"]', row).selectpicker('refresh');
        ginger.loadAvailableInterfaces($('select[name="interface_add"]',row));
    });

    // Save Modify Bond block

    $('.bridge-bonds').on('click','.save-bond',function(e){
        e.preventDefault();
        e.stopPropagation();
        var row = $(this).parent().parent().parent();
        ginger.selectedBond = row.data('name');
        var interface_del = $('select[name="interface_del"]', row).val();
        var interface_add = $('select[name="interface_add"]', row).val();
        if(!interface_del){
            $('label[for="interface_del"] .btn-group.bootstrap-select > button').click();
        }else if(!interface_add){
            $('label[for="interface_add"] .btn-group.bootstrap-select > button').click();
        }else {
            var data = {};
            data = {
                bond: ginger.selectedBond,
                interface_del: interface_del,
                interface_add: interface_add
            };
            ginger.modifyOvsBridgeBond(ginger.selectedBridge, data, function() {
                $('select[name="interface_del"]', row).prop('disabled',true);
                $('select[name="interface_add"]', row).prop('disabled',true);
                  ginger.refreshThisBridgeBonds(ginger.selectedBridge);
                  wok.message.success(i18n['GINNET0054M'].replace("%1", '<strong>'+ginger.selectedBond+'</strong>'),'#alert-modal-container',true);
             }, function(err) {
                  wok.message.error(err.responseJSON.reason, '#alert-modal-container', true);
                  $('select[name="interface_del"]', row).prop('disabled',false);
                  $('select[name="interface_add"]', row).prop('disabled',false);
             });
        }
    });

    // Cancel Modify Bond block

    $('.bridge-bonds').on('click','.cancel-bond',function(e){
        e.preventDefault();
        e.stopPropagation();
        var row = $(this).parent().parent().parent();
        $('.interfaces-readonly',row).removeClass('hidden');
        $('.readonly-bond-actions',row).removeClass('hidden');
        $('.modify-bond-on',row).addClass('hidden');
        $('select[name="interface_del"]', row).prop('disabled',true);
        $('select[name="interface_add"]', row).prop('disabled',true);
        $('.editable-bond-actions',row).addClass('hidden');
    });

    // Remove Bond block

    $('.bridge-bonds').on('click','.remove-bond',function(e){
        e.preventDefault();
        e.stopPropagation();
        var row = $(this).parent().parent().parent();
        ginger.selectedBond = row.data('name');

        var settings = {
          title: i18n['GINNET0051M'],
          content: i18n['GINNET0052M'].replace("%1", '<strong>'+ginger.selectedBond+'</strong>'),
          confirm: i18n['GINNET0045M'],
          cancel: i18n['GINNET0046M']
        };
        wok.confirm(settings, function() {
          ginger.delOvsBridgeBond(ginger.selectedBridge,ginger.selectedBond, function() {
              wok.message.success(i18n['GINNET0053M'].replace("%1", '<strong>'+ginger.selectedBond+'</strong>'), '#alert-modal-container',true);
              ginger.refreshThisBridgeBonds(ginger.selectedBridge);
          }, function(err) {
              wok.message.error(err.responseJSON.reason, '#alert-modal-container',true);
          });
        }, function(){});
    });

    // Add Interface block

    $('#ovs-edit-interface-add-button').on('click',function(e){
        e.preventDefault();
        e.stopPropagation();
        if(!$('.new-interface').length){
            $('.column-empty','.ovs-interface-body').addClass('hidden');
            var newBridgeInterfaceItem = $.parseHTML(wok.substitute($("#interfaceAddBodyTmpl").html(), {
                name: ginger.selectedBridge
            }));
            ginger.loadAvailableInterfaces($('select[name="new-interface"]',newBridgeInterfaceItem));
            $('.ovs-interface-body').prepend(newBridgeInterfaceItem);
            $('.bridge-interfaces').dataGrid('destroy');
            $('.bridge-interfaces').dataGrid({enableSorting: false});
        }
    });

    // Save Add New Interface block

    $('.bridge-interfaces').on('click','.save-interface',function(e){
        e.preventDefault();
        e.stopPropagation();
        var row = $(this).parent().parent();
        var newiface = $('select[name="new-interface"]', row).val();
        if(!newiface){
            $('.btn-group.bootstrap-select > button').click();
        }else {
            var data = {};
            data = {
                interface: newiface
            };
            ginger.addOvsBridgeInterface(ginger.selectedBridge, data, function() {
                  $('select[name="new-interface"]', row).prop('disabled', true);
                  $('.save-interface', row).prop('disabled', true);
                  $('.cancel-interface', row).prop('disabled', true);
                  row.remove();
                  wok.message.success(i18n['GINNET0057M'].replace("%1", '<strong>'+newiface+'</strong>'), '#alert-modal-container',true);
                  ginger.refreshThisBridgeInterfaces(ginger.selectedBridge);
              }, function(err) {
                  wok.message.error(err.responseJSON.reason, '#alert-modal-container',true);
                  $('select[name="new-interface"]', row).prop('disabled', false);
                  $('.save-interface', row).prop('disabled', false);
                  $('.cancel-interface', row).prop('disabled', false);
              });
        }
    });

    // Cancel Add New Interface block

    $('.bridge-interfaces').on('click','.cancel-interface',function(e){
        e.preventDefault();
        e.stopPropagation();
        $('.column-empty','.ovs-interface-body').removeClass('hidden');
        $(this).parent().parent().remove();
        $('.bridge-interfaces').dataGrid('destroy');
        $('.bridge-interfaces').dataGrid({enableSorting: false});
    });

    // Remove Interface block

    $('.bridge-interfaces').on('click','.remove-iface',function(e){
        e.preventDefault();
        e.stopPropagation();
        var row = $(this).parent().parent();
        ginger.selectedInterface = row.data('name');

        var settings = {
          title: i18n['GINNET0043M'],
          content: i18n['GINNET0044M'].replace("%1", '<strong>'+ginger.selectedInterface+'</strong>').replace("%2", '<strong>'+ginger.selectedBridge+'</strong>'),
          confirm: i18n['GINNET0045M'],
          cancel: i18n['GINNET0046M']
        };
        wok.confirm(settings, function() {
          ginger.delOvsBridgeInterface(ginger.selectedBridge,ginger.selectedInterface, function() {
              wok.message.success(i18n['GINNET0047M'].replace("%1", '<strong>'+ginger.selectedInterface+'</strong>'), '#alert-modal-container',true);
              ginger.refreshThisBridgeInterfaces(ginger.selectedBridge);
          }, function(err) {
              wok.message.error(err.responseJSON.reason, '#alert-modal-container');
          });
        }, function(){});
    });
}

ginger.refreshThisBridgeInterfaces = function(br) {
    ginger.getOvsBridge(ginger.selectedBridge, function(result){
        if(Object.keys(result.ports).length){
            $('.ovs-interface-body > div').remove();
            $.each(result.ports, function(i,value){
                if(value.type === 'interface') {
                    var interfaceName = value.name;
                    var interfaceMac = value.mac_in_use;
                    var bridgeInterfaceItem = $.parseHTML(wok.substitute($("#interfacesBodyTmpl").html(), {
                        id: i,
                        name: interfaceName,
                        address: interfaceMac
                    }));
                    $('.ovs-interface-body').append(bridgeInterfaceItem);
                }
            });
            $('.bridge-interfaces').dataGrid('destroy');
            $('.bridge-interfaces').dataGrid({enableSorting: false});
        }else {
            var emptyGrid = [
                '<div role="row">',
                    '<span role="gridcell" class="column-empty">',
                        i18n['GINNET0055M'],
                    '</span>',
                '</div>'
            ].join('');
            $('.ovs-interface-body > div').remove();
            $('.ovs-interface-body').append(emptyGrid);
            $('.bridge-interfaces').dataGrid('destroy');
            $('.bridge-interfaces').dataGrid({enableSorting: false});
        }
        ginger.refreshOvsBridges();
    },
    function(){
        wok.message.error(err.responseJSON.reason, '#alert-modal-container',true);
    });
}

ginger.refreshThisBridgeBonds = function(br) {
    ginger.getOvsBridge(ginger.selectedBridge, function(result){
        if(Object.keys(result.ports).length){
            $('.ovs-bond-body > div').remove();
            $.each(result.ports, function(i,value){
                if(value.type === 'bond') {
                var bondName = value.name;
                var bondInterfaces = value.interfaces;
                var bondInterfacesOptionHtml = '';
                var bondInterfacesText = '';
                for (var i = 0; i < bondInterfaces.length; i++) {
                    bondInterfacesOptionHtml += '<option value="'+ bondInterfaces[i].name + '">' + bondInterfaces[i].name + '</option>';
                    (i + 1 < bondInterfaces.length) ? bondInterfacesText += bondInterfaces[i].name +', ' : bondInterfacesText += bondInterfaces[i].name;
                }
                var bridgeBondItem = $.parseHTML(wok.substitute($("#bondsBodyTmpl").html(), {
                    id: i,
                    name: bondName,
                    interfaces: bondInterfacesText
                }));
                $(bridgeBondItem).find('select[name="interface_del"]').append(bondInterfacesOptionHtml);
                $('.ovs-bond-body').append(bridgeBondItem);
                }
            });
            $('.bridge-bonds').dataGrid('destroy');
            $('.bridge-bonds').dataGrid({enableSorting: false});
        }else {
            var emptyGrid = [
                '<div role="row">',
                    '<span role="gridcell" class="column-empty">',
                        i18n['GINNET0055M'],
                    '</span>',
                '</div>'
            ].join('');
            $('.ovs-bond-body > div').remove();
            $('.ovs-bond-body').append(emptyGrid);
            $('.bridge-bonds').dataGrid('destroy');
            $('.bridge-bonds').dataGrid({enableSorting: false});
        }
        ginger.refreshOvsBridges();
    },
    function(){
        wok.message.error(err.responseJSON.reason, '#alert-modal-container',true);
    });
}

ginger.loadAvailableInterfaces = function(target) {
   ginger.getInterfaces(function(result) {
        interfaceSelect = $(target);
        interfaceSelect.find('option').remove();
        var selectInterfaceOptionHtml = '';
        for (var i = 0; i < result.length; i++) {
            selectInterfaceOptionHtml += '<option value="'+ result[i].device + '">' + result[i].device + '</option>';
        }
        interfaceSelect.append(selectInterfaceOptionHtml);
        interfaceSelect.selectpicker('refresh');
    });
};
