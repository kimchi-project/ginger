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

            data[i].depends = data[i].depends.length != 0 ? data[i].depends : 'None';
            data[i].version = data[i].version != undefined ? data[i].version : 'n/a';

            var tempNode = $.parseHTML(wok.substitute($("#sysmodulesItem").html(), data[i]));

            $("#sysmodules-body").append(tempNode);

            // TODO: Implement logic to fill details
            $(".details-list", tempNode).append('Details');

            $(".btn-unload").on("click", function(event) {
                event.preventDefault();
                event.stopImmediatePropagation();

                var settings = {
                    title: i18n['KCHAPI6001M'],
                    content: i18n['GINSYSMOD00001M'],
                    confirm: i18n['KCHAPI6002M'],
                    cancel: i18n['KCHAPI6003M']
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

        $('.load-modules-btn').on('click', function(event) {
            // TODO: Implement load modules action
        });

        $('.arrow').on('click', function(event) {
            var that = $(this).parent().parent();
            var slide = $('.sysmodules-details', $(this).parent().parent());
            if (that.hasClass('in')) {
                that.css('height', 'auto');
                that.removeClass('in');
                ginger.changeArrow($('.arrow-down', that));
                slide.slideDown('slow');
            } else {
                slide.slideUp('slow', function() {
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

ginger.changeArrow = function(obj) {
    if ($(obj).hasClass('arrow-down')) {
        $(obj).removeClass('arrow-down').addClass('arrow-up');
    } else {
        $(obj).removeClass('arrow-up').addClass('arrow-down');
    }
}