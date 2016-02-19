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

ginger.initSysmodules = function() {
    $(".content-area", "#gingerHostAdmin").css("height", "100%");
    ginger.loadSysmodules();
};

ginger.loadSysmodules = function() {
    ginger.getSysmodules(function(data) {
        $("#sysmodules-body").empty();
        for (var i = 0; i < data.length; i++) {

            data[i].depends = data[i].depends.length != 0 ? data[i].depends : i18n['GINSYS0001M'];
            data[i].version = data[i].version != undefined ? data[i].version : i18n['GINSYS0002M'];

            var tempNode = $.parseHTML(wok.substitute($("#sysmodulesItem").html(), data[i]));

            $("#sysmodules-body").append(tempNode);
            $('#sysmodules-datagrid').removeClass('hidden');
            $('.wok-mask').fadeOut(300, function() {});

            $(".btn-unload").on("click", function(event) {
                event.preventDefault();
                event.stopImmediatePropagation();

                var settings = {
                    title: i18n['GINSYS0005M'],
                    content: i18n['GINSYS0006M'],
                    confirm: i18n['GINSYS0003M'],
                    cancel: i18n['GINSYS0004M']
                };

                wok.confirm(settings, function() {
                    var sysmoduleItem = $(this).parent();
                    ginger.removeSysmodule(sysmoduleItem.prop("id"), function() {
                        sysmoduleItem.remove();
                    }, function(err) {
                        wok.message.error(err.responseJSON.reason);
                        $('body').scrollTop(0);
                    });
                }, function() {});
            });
        }

        $('#load_sysmodules_button').on('click', function(event) {
            // wok.window.open();
        });

        $('.arrow').on('click', function(event) {
            var that = $(this).parent().parent();
            var module = that.data("id");
            var slide = $('.sysmodules-details', $(this).parent().parent());
            if (that.hasClass('in')) {
                ginger.loadSysmodule(module);
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

ginger.loadSysmodule = function(module) {
    var that = $('[data-id='+module+']').find('.details-list');
    that.html('');
    ginger.getSysmodule(module, function(data) {
        $.each(data, function(key, obj) {
            if(key !== 'name' && key !== 'depends' && key !== 'version') {
                if(obj && obj.length > 0){
                    var pathNode = $.parseHTML(wok.substitute($("#detail-head").html(), {
                        key: key
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
                    $.each(obj, function(i,j){
                        if (j && j.length > 0) {
                            var paramBody = $.parseHTML(wok.substitute($("#detail-head").html(),{
                                key: key
                            }));
                            $(that).append(paramBody);
                            var paramPathNode = $.parseHTML(wok.substitute($("#detail-body-obj").html(), {
                                index: key,
                                key: i,
                                value: j
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