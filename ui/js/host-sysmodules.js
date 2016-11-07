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

ginger.loadSysmodules = function() {
    ginger.getSysmodules(function(data) {
        $("#sysmodules-body").empty();
        for (var i = 0; i < data.length; i++) {

            data[i].depends = data[i].depends.length != 0 ? data[i].depends : i18n['GINSYS0001M'];
            data[i].version = data[i].version != undefined ? data[i].version : i18n['GINSYS0002M'];

            var tempNode = $.parseHTML(wok.substitute($("#sysmodulesItem").html(), data[i]));

            $("#sysmodules-body").append(tempNode);
            $('#sysmodules-datagrid').removeClass('hidden');
            $('#sysmodules-content-area .wok-mask').fadeOut(300, function() {});

            $(".btn-unload").on("click", function(event) {
                event.preventDefault();
                event.stopImmediatePropagation();
                var sysmoduleItem = $(this).parent();
                var selectedModule = sysmoduleItem.prop("id");

                var settings = {
                    title: i18n['GINSYS0005M'],
                    content: i18n['GINSYS0006M'].replace("%1", '<strong>'+selectedModule+'</strong>'),
                    confirm: i18n['GINSYS0003M'],
                    cancel: i18n['GINSYS0004M']
                };

                wok.confirm(settings, function() {
                    ginger.removeSysmodule(selectedModule, function() {
                        wok.message.success(i18n['GINSYS0013M'].replace("%1", '<strong>'+selectedModule+'</strong>'),'#sysmodules-alert-container',true);
                        $('#sysmodules-content-area .wok-mask').fadeIn();
                        ginger.loadSysmodules();
                        $('body').animate({ scrollTop: 0 }, 1000);
                    }, function(err) {
                        wok.message.error(err.responseJSON.reason,'#sysmodules-alert-container',true);
                        $('body').animate({ scrollTop: 0 }, 1000);
                    });
                }, function() {});
            });
        }

        $('.arrow').on('click', function(event) {
            var that = $(this).parent().parent();
            var module = that.data("id");
            var slide = $('.sysmodules-details', $(this).parent().parent());
            if (that.hasClass('in')) {
                ginger.getSysmoduleDetails(module);
                that.css('height', 'auto');
                that.removeClass('in');
                ginger.changeArrow($('.arrow-down', that));
                slide.slideDown();
            } else {
                slide.slideUp(function() {
                    that.css('height', '');
                });
                that.addClass('in');
                ginger.changeArrow($('.arrow-up', that));
            }
        });

        var sysModOptions = {
            valueNames: ['name-filter', 'depends-filter', 'version-filter']
        };
        var sysModFilterList = new List('sysmodules-content-area', sysModOptions);

        sysModFilterList.sort('name-filter', {
            order: "asc"
        });
    });
};

ginger.getSysmoduleDetails = function(module) {
    var that = $('[data-id='+module+']').find('.details-list');
    that.html('');
    ginger.getSysmodule(module, function(data) {
        $.each(data, function(key, obj) {
            if(key !== 'name' && key !== 'depends' && key !== 'version') {
                if(obj && obj.length > 0){
                    switch (key){
                       case "sig_key":
                          text = i18n['GINSYS0014M'];
                          break;
                       case "description":
                          text = i18n['GINSYS0015M'];
                          break;
                       case "license":
                          text = i18n['GINSYS0016M'];
                          break;
                       case "vermagic":
                          text = i18n['GINSYS0017M'];
                          break;
                       case "intree":
                          text = i18n['GINSYS0018M'];
                          break;
                       case "filename":
                          text = i18n['GINSYS0019M'];
                          break;
                       case "srcversion":
                          text = i18n['GINSYS0020M'];
                          break;
                       case "authors":
                          text = i18n['GINSYS0021M'];
                          break;
                       case "signer":
                          text = i18n['GINSYS0022M'];
                          break;
                       case "sig_hashalgo":
                          text = i18n['GINSYS0023M'];
                          break;
                       case "aliases":
                          text = i18n['GINSYS0024M'];
                          break;
                       default:
                           text = key;
                    }
                    var pathNode = $.parseHTML(wok.substitute($("#detail-head").html(), {
                        key: key,
                        title: text
                    }));
                    $(that).append(pathNode);
                    if(typeof obj !== 'object') {
                        obj = obj.split(',');
                    }
                    $.each(obj, function(i,j){
                        var parentPathNode = $.parseHTML(wok.substitute($("#detail-body").html(), {
                            index: key,
                            object: j
                        }));
                        $(that).find('.body-'+key).append(parentPathNode);
                    });
                } else if (typeof key !== 'object' && key.length > 0) {
                    switch (key){
                        case "parms":
                            text = i18n['GINSYS0025M'];
                            break;
                        case "features":
                            text = i18n['GINSYS0026M'];
                            break;
                        default:
                            text = key;
                    }
                    var paramBody = $.parseHTML(wok.substitute($("#detail-head").html(),{
                        key: key,
                        title: text
                    }));
                    $(that).append(paramBody);
                    $.each(obj, function(i,j){
                        if (j && typeof j !== 'object'  && j.length > 0) {
                            var paramPathNode = $.parseHTML(wok.substitute($("#detail-body-obj").html(), {
                                index: key,
                                key: i,
                                value: j
                            }));
                            $(that).find('.body-'+key).append(paramPathNode);
                        }else {
                            var paramPathNode = $.parseHTML(wok.substitute($("#detail-body-obj").html(), {
                                index: key,
                                key: i,
                                value: j.desc
                            }));
                            $(that).find('.body-'+key).append(paramPathNode);
                        }
                    });
                }
            }
        });
    });
};

ginger.changeArrow = function(obj) {
    if ($(obj).hasClass('arrow-down')) {
        $(obj).removeClass('arrow-down').addClass('arrow-up');
    } else {
        $(obj).removeClass('arrow-up').addClass('arrow-down');
    }
}

ginger.modalSysmodules = function() {

    ginger.toggleLoadButton('disable');
    $("#loadingIcon").show();
    $("#module").prop("disabled", true);

    ginger.getAllSysmodules(function(dataReturn) {

    var modulesData = [];
    var modulesTimer;

    $.each(dataReturn, function(i, obj) {
        var special = false;
        if(!jQuery.isEmptyObject(obj.features)) {
            special = true;
        }
        modulesData.push({"name": obj.name, "code": obj.name, "special": special});
    });

    var modules = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            local: modulesData
        });
        $("#loadingIcon").hide();
        $("#module").prop("value", "");
        $("#module").prop("disabled", false);

        modules.initialize();

        $('.typeahead').typeahead(
            {
                autoselect: 'first'
            }, {
            name: 'modules',
            displayKey: 'name',
            source: modules.ttAdapter()
        }).on('typeahead:selected keyup keydown typeahead:opened typeahead:open', function(event, data){
            var input;
            var match;
            if(event.type === 'typeahead:selected'){
                clearTimeout(modulesTimer);
                $('.typeahead').val(data.code);
                $('#module').val(data.code);
                input = data.code;
            }else if(event.type === 'keydown'){
                clearTimeout(modulesTimer);
            }else if(event.type === 'typeahead:opened') {
                $('span.tt-dropdown-menu').unbind();
                clearTimeout(modulesTimer);
            }
            $.each(modules.index.datums, function(index) {
                if(input == modules.index.datums[index].name){
                    match = true;
                }
            });
            if(match){
                $('#module').parent().parent().addClass('has-loading');
                clearTimeout(modulesTimer);
                setTimeout(function(){ginger.loadParms(input)},500);
            }else {
                input = $('#module').val();
                if(event.type === 'keyup'){
                    $('#module').parent().parent().addClass('has-loading');
                    clearTimeout(modulesTimer);
                    modulesTimer  = setTimeout('ginger.loadParms("'+input+'")', 1500);
                }
                if(input === ''){
                    $('#module').parent().parent().removeClass('has-loading');
                    if($('#parms-body, .parms-fields').data('module') === 'none'){
                        $('#parms-body, .parms-fields').data('module', 'notlisted');
                    } else if($('#parms-body, .parms-fields').data('module') !== 'notlisted'){
                        ginger.clearParms();
                    }
                }
            };
        });
        $('.typeahead').focus();
    });

    $('#loadButton').on('click',function(event){
        event.preventDefault();
        $('form[name="sysmodule"]' ).submit();
    });

    $('form[name="sysmodule"]').submit(function(event) {
        var name = '';
        var parm = '';
        var module = '';
        event.preventDefault();
        var sysmodule = $(this).serializeArray();
        $.each(sysmodule, function(i,obj) {
            if(obj.name === 'name') {
                name = obj.value;
            }else if(obj.name === 'custom-load' && obj.value !== '') {
                parm = obj.value;
            }else if(obj.name !== 'load-type' && obj.value !== '') {
                parm +=  obj.name+'='+obj.value+' ';
            }
        });
        module = '{"name":"'+name+'", "parms":"'+$.trim(parm)+'"}';
        module = $.parseJSON(module);
        ginger.loadSysmodule(module, function(suc){
            ginger.toggleLoadButton('disable');
            $('.typeahead').typeahead('destroy');
            ginger.loadSysmodules();
            wok.window.close();
            wok.message.success(i18n['GINSYS0012M'].replace("%1", '<strong>'+module.name+'</strong>'),'#sysmodules-alert-container',true);
        },function(err){
            wok.message.error(err.responseJSON.reason,'#alert-modal-container',true);
            ginger.toggleLoadButton();
        })
    });

};

ginger.clearParms = function() {
    ginger.toggleLoadButton('disable');
    $('#parameters').slideUp(400, function(){
        $('#parms-body, .parms-fields').data('module', 'notlisted');
        $('#parms-body').empty();
        $('#special-load-radio').empty();
        $('.parms-pager').empty();
    });
}

ginger.loadParms = function(module) {
    if($('#parms-body, .parms-fields').data('module') !== module){
        var parmItem;
        var parmsHeight = 0;
        var parmItem = '<div id='+module+' class="wok-datagrid-row"><span>'+i18n['GINSYS0007M']+'</span></div>';
        var infoAlert = '<div class="alert alert-info" role="alert">'+i18n['GINSYS0010M']+'</div>';
        var infoCustomAlert = '<div class="alert alert-info" role="alert">'+i18n['GINSYS0011M']+'</div>';
        var defaultOption = '<input type="radio" name="load-type" id="custom-load" value="parms-custom-load" class="wok-radio"><label for="custom-load">'+i18n['GINSYS0008M']+'</label>'
        var defaultField = '<div class="form-group" id="parms-custom-load">'+
                  '<label for="custom-load-parm">'+i18n['GINSYS0009M']+'</label>'+
                  '<input id="custom-load-parm" name="custom-load" class="form-control" type="text" disabled="true"  />'+
               '</div>';
        ginger.getSysmodule(module, function(data) {
            $('#parms-body').empty().hide();
            $('.parms-fields').data('module', module);
            $('#special-load-radio').hide().empty();
            $('.parms-pager').hide().empty();
            if(data.parms && Object.keys(data.parms).length > 0){
                $('#parameters').show();
                $.each(data.parms, function(key, obj) {
                    var row = $.parseHTML(wok.substitute($("#parms-item").html(), {
                            name: key,
                            description: obj
                    }));
                    $('#parms-body').append(row).data('module', module);
                });
                $('#parms-body').show().height(0);
                $("#parms-body .wok-datagrid-row").each(function(){
                    parmsHeight += $(this).height() + 0.5;
                });
                parmsHeight  = (parmsHeight > 175) ? 175 : parmsHeight;
                $('#parms-body').animate({
                    height: parmsHeight+"px"
                }, 400);
                ginger.toggleLoadButton('disable');
            }else if(data.parms && Object.keys(data.parms).length <= 0) {
                $('.parms-pager').slideUp();
                $('#special-load-radio').slideUp();
                $('#parameters').slideDown();
                $('#parms-body').append(parmItem).data('module', module);
                $('#parms-body').show().animate({
                    height: "35px"
                }, 400);
                ginger.toggleLoadButton('enable');
            }

            if(data.features && Object.keys(data.features).length > 0){
                //SR-IOV
                $.each(data.features, function(key, obj) {
                    featureItem = $.parseHTML(wok.substitute($("#specialparms-radio").html(), {
                            configname: key
                    }));
                    $('#special-load-radio').append(featureItem);
                    $('.parms-pager').append('<div class="form-group clearfix special-load" id="parms-'+key+'" />');
                    $('#parms-'+key).append('<p class="form-control-static">'+obj.desc+'</p>');
                    $('#parms-'+key).append(infoAlert);
                    $.each(obj.parms, function(i, j){
                            featureParm = $.parseHTML(wok.substitute($('#specialparms-item').html(), {
                            parmName: j
                    }));
                    $('#parms-'+key).append(featureParm);
                    });
                });
                $('#special-load-radio').append(defaultOption);
                $('.parms-pager').append(defaultField);
                $('#parms-custom-load').prepend(infoCustomAlert);
                $("input[name=load-type]:first-child").attr('checked', true);
                $('#special-load-radio').slideDown();
                $('.parms-pager').slideDown();

                $('.parms-pager input[type="text"]').on('keyup', function(event) {
                    ginger.toggleLoadButton();
                });

                $('input[name=load-type').on('change', function(event) {
                    var value = $(this).val();
                    $('.parms-pager div input').attr('disabled', true);
                    $('.parms-pager div').not('#'+value).slideUp();
                    $('.parms-pager div#'+value).slideDown(function(){
                        $('.parms-pager div#'+value+' .alert').slideDown();
                        $('.parms-pager div#'+value+' input').attr('disabled', false);
                        ginger.toggleLoadButton();
                    });
                });

            }else if(data.parms && Object.keys(data.parms).length > 0){
                    $('.parms-pager').append(defaultField);
                    $('#parms-custom-load').prepend(infoCustomAlert);
                    $('#parms-custom-load').show();
                    $('.parms-pager div input').attr('disabled', false);
                    $('.parms-pager').slideDown();
                    ginger.toggleLoadButton('enable');
            }
        }, function(){
            ginger.clearParms();
        });

        if(!$('#parms-grid').hasClass('wok-datagrid')){
            $('#parms-grid').dataGrid({enableSorting: false});
        }
    }
    $('#module').parent().parent().removeClass('has-loading');
}

ginger.toggleLoadButton = function(args) {
    if (args === 'enable') {
        $("#loadButton").prop('disabled', false)
    } else if (args === 'disable'){
        $("#loadButton").prop('disabled', true);
    } else {
        if($('.parms-pager input[type="text"]:visible').length > 1){
            $.each($('.parms-pager input[type="text"]:visible'),function() {
                if ($(this).val().length === 0) {
                    $("#loadButton").prop('disabled', true);
                    $(this).parent().removeClass('has-success').addClass('has-error');
                }else {
                    $(this).parent().removeClass('has-error').addClass('has-success');
                    $("#loadButton").prop('disabled', false);
                }
            });
        }else {
            $("#loadButton").prop('disabled', false);
        }
    }

};
