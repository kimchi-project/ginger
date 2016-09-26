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

ginger.initSystemServices = function() {

    // Set height and panel scrollbars
    var panelHeight = function() {
        var viewportHeight = $(window).height();
        $('.well', '#sysmodules-accordion, #system-services-accordion').css({'height': viewportHeight - 400 +'px', 'overflow-y': 'scroll'});
    };
    panelHeight();

    // Hide other collapses once one is clicked

    $("#gingerHostAdmin >  div > h3 > a[data-toggle=collapse]").click(function(e){
        e.preventDefault();
        e.stopPropagation();
        $("#gingerHostAdmin > div > .panel-collapse.collapse.in").collapse("hide");
        $($(this).attr("href")).collapse("show");
    });

    // System modules call
    ginger.loadSysmodules();
    ginger.loadSystemServices(ginger.buildSystemServicesUi);
    ginger.systeServicesClickHandler();

    // System modules modal window
    $('#load_sysmodules_button').on('click', function(event) {
        wok.window.open('plugins/ginger/host-sysmodules-load.html');
    });

    $(window).on('resize', function(){
        panelHeight();
    });

    $('.panel-group.accordion > h3 > a', '#sysmodules-accordion, #system-services-accordion').on('click', function(){
        panelHeight();
    });

};

ginger.systeServicesClickHandler = function() {

    // Autostart checkbox Change block

    $('#system-services-body').on('change', '.wok-toggleswitch-checkbox', function(event) {
        var service = $(this).parent().parent().data('id');
        if($(this).is(":checked")){
            ginger.enableSystemService(service, function(){
                ginger.getSystemService(service, function(result){
                    ginger.generateSystemServiceElem(result);
                },function(){
                    wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
                });
            }, function(){
                wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
            });
        }else {
            ginger.disableSystemService(service, function(){
                ginger.getSystemService(service, function(result){
                    ginger.generateSystemServiceElem(result);
                },function(){
                    wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
                });
            }, function(){
                wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
            });
        }
    });

    // Start click block

    $('#system-services-body').on('click', '.service-start', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var service = $(this).data('service');
        if(!$(this).parent().is('.disabled')){
            ginger.startSystemService(service,function(){
                ginger.loadSystemServices(ginger.systemServicesFilterList.update);
                $('.dropdown.menu-flat.system-service-actions.open').removeClass("open");
                $('html, body').animate({
                    scrollTop: $("#system-services-alert-container").offset().top
                }, 1000);
                wok.message.success(i18n['GINSYS0027M'].replace("%1", '<strong>'+service+'</strong>'),'#system-services-alert-container',true);
            },function(){
                wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
            });
        }
    });

    // Restart click block

    $('#system-services-body').on('click', '.service-restart', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var service = $(this).data('service');
        if(!$(this).parent().is('.disabled')){
            ginger.restartSystemService(service,function(){
                ginger.loadSystemServices(ginger.systemServicesFilterList.update);
                $('.dropdown.menu-flat.system-service-actions.open').removeClass("open");
                $('html, body').animate({
                    scrollTop: $("#system-services-alert-container").offset().top
                }, 1000);
                wok.message.success(i18n['GINSYS0029M'].replace("%1", '<strong>'+service+'</strong>'),'#system-services-alert-container',true);
            },function(){
                wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
            });
        }
    });

    // Stop click block

    $('#system-services-body').on('click', '.service-stop', function(event) {
        event.preventDefault();
        event.stopPropagation();
        var service = $(this).data('service');
        if(!$(this).parent().is('.disabled')){
            ginger.stopSystemService(service,function(){
                ginger.loadSystemServices(ginger.systemServicesFilterList.update);
                $('.dropdown.menu-flat.system-service-actions.open').removeClass("open");
                $('html, body').animate({
                    scrollTop: $("#system-services-alert-container").offset().top
                }, 1000);
                wok.message.success(i18n['GINSYS0028M'].replace("%1", '<strong>'+service+'</strong>'),'#system-services-alert-container',true);
            },function(){
                wok.message.error(err.responseJSON.reason,'#system-services-alert-container',true);
            });
        }
    });

};

ginger.generateSystemServiceElem = function(value){
        var name = ''
        if (value.name !== undefined) {
            name = value.name.toLowerCase();
        }
        var servicename = name.split(".service").join("").replace(/[`~!@#$%^&*()_|+\-=?;:'",.<>\{\}\[\]\\\/]/gi, '');
        var id = 'service-'+servicename;
        var collapse_target = id+'-details';
        var loaded = value.load;
        var active = value.active;
        var sub = value.sub;
        var status = active + ' ('+sub+')';
        var icon = (sub === 'running') ? 'fa-check' : (sub === 'exited') ? 'fa-times' : 'fa-exclamation-triangle';
        var label = (sub === 'running') ? 'success' : (sub === 'exited') ? 'primary' : 'danger';
        var description = value.desc;
        var checked = (value.autostart) ? 'checked' : '';
        var autostartonoff  = (value.autostart) ? 'On' : 'Off';
        var cgroup = ''
        if (value.cgroup !== undefined) {
            cgroup = value.cgroup.name;
        }
        var systemServicesItem = $.parseHTML(wok.substitute($("#systemServicesItem").html(), {
            id: id,
            name: name,
            servicename: servicename,
            collapse_target: collapse_target,
            loaded: loaded,
            status: status,
            icon: icon,
            label: label,
            checked: checked,
            autostartonoff: autostartonoff,
            description: description,
            cgroup: cgroup
        }));
        if(!value.cgroup){
            $('.system-services-cgroup',systemServicesItem).remove();
            $('.column-service-details',systemServicesItem).empty().append('--');
        }
        else {
            if(!jQuery.isEmptyObject(value.cgroup.processes)){
                $.each(value.cgroup.processes, function(pid,process){
                    var processItem = $.parseHTML(wok.substitute($("#systemServiceProcessItem").html(), {
                        pid: pid,
                        process: process
                    }));
                    $('.system-service-process-body',systemServicesItem).append(processItem);
                });
            }else {
                $('.system-services-process',systemServicesItem).remove();
            }
            if(sub === 'running') {
                $('.service-start',systemServicesItem).parent().addClass('disabled');
            }else {
                $('.service-stop',systemServicesItem).parent().addClass('disabled');
            }
            if($('#system-services-body > li#'+id).length){
                $('#system-services-body > li#'+id).replaceWith(systemServicesItem);
            }else {
                $('#system-services-body').append(systemServicesItem);
            }
        }
};

ginger.loadSystemServices = function(callback){
    ginger.getSystemServices(function(result) {
        if (result && result.length) {
            result.sort(function(a, b) {
                if (a.name !== undefined && b.name !== undefined) {
                    return a.name.localeCompare( b.name );
                } else {
                    return 0
                }
            });
            $("#system-services-body").empty();
            $.each(result, function(i,value){
                ginger.generateSystemServiceElem(value);
            });
            $('#system-services-datagrid').dataGrid({enableSorting: false});
        }
        if(callback){
          callback();
        }
    });
};

ginger.buildSystemServicesUi = function() {
    $('#ovs_search_input').prop('disabled',false);
    $('#system-services-datagrid').dataGrid({enableSorting: false});
    $('#system-services-datagrid').removeClass('hidden');
    $('#system-services-content-area .wok-mask').fadeOut(300, function() {});

    ginger.systemServicesOptions = {
        valueNames: ['service-name-filter', 'service-loaded-filter', 'service-status-filter', 'service-description-filter']
    };
    ginger.systemServicesFilterList = new List('system-services-content-area', ginger.systemServicesOptions);

    ginger.systemServicesFilterList.sort('service-name-filter', {
        order: "asc"
    });

};
