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

ginger.sidebarObj = [
    {
        title: i18n['Administration'],
        url: 'plugins/ginger/host-admin.html',
        id: 'ginger-admin'
    },
    {
        title: i18n['Network'],
        url: 'plugins/ginger/host-network.html',
        id: 'ginger-network'
    },
    {
        title: i18n['Storage'],
        url: 'plugins/ginger/host-storage.html',
        id: 'ginger-storage'
    },
    {
        title: i18n['System Services'],
        url: 'plugins/ginger/host-system-services.html',
        id: 'ginger-system-services'
    }
];

Sidebar = function(el, obj) {
    "use strict";
    this.obj = obj;
    this.el = el;
    this.createSidebar();
    this.clickHandlers();
};

Sidebar.prototype = (function() {
    "use strict";
    var THIS_PLUGIN = location.hash.split('/')[1];

    var createSidebar = function() {
        var el = this.el;
        var obj = this.obj;
        var listGroup = $('<ul class="list-group" id="sidebar" />').appendTo(el);
        for (var i = 0; i < obj.length; i++) {
            $('<li id="' + obj[i].id + '" class="list-group-item"><a href="' + obj[i].url + '">' + obj[i].title + ' <i class="fa fa-chevron-right"></i></a></li>').appendTo(listGroup);
        }
    };

    var onSidebarRedirect = function(url) {
        var link = $('#sidebar.list-group > li > a[href="' + url + '"]');
        $('#sidebar.list-group > li').removeClass('active');

        $(link).parent().addClass('active');
        $(link).focus();

        $('#rightCol .row').empty();
        $('#rightCol > .wok-mask').show();

        // Load page content.
        loadPanel(url);
    };

    var loadPanel = function(url) {
        // Get the page content through Ajax and render it.
        url && $('#rightCol .row').load(url, function(responseText, textStatus, jqXHR) {
                if (jqXHR['status'] === 401 || jqXHR['status'] === 303) {
                    var isSessionTimeout = jqXHR['responseText'].indexOf("sessionTimeout") != -1;
                    document.location.href = isSessionTimeout ? 'login.html?error=sessionTimeout' : 'login.html';
                    return;
                } else if (status === "error") {
                    wok.message.error(xhr.status + " " + xhr.statusText, '#rightCol .row', true);
                }
                wok.cookie.set('lastGingerPage', url)
            }).promise()
            .done(function() {
                $('#rightCol > .wok-mask').hide();
            });
    };

    var checkHash = function(url) {
        var hashClick = url.split('/')[1];
        var hashPage = url.split('/')[2];
        if (hashPage === 'host-settings' && (THIS_PLUGIN === hashClick)) {
            wok.topic('redirect').publish(url + '.html');
        } else if (hashPage !== 'host-settings' && (THIS_PLUGIN === hashClick)) {
            wok.topic('sidebarClicked').publish(url + '.html');
        } else {
            // Logs every datatable instance and destroys them to avoid warnings
            var tables = $.fn.dataTable.tables();
            if (tables.length){
                $.each(tables, function(i, table) {
                  $(table).DataTable().clear().destroy();
                });
            }
            wok.topic('sidebarClicked').unsubscribe(onSidebarRedirect);
            wok.topic('redirect').publish(url + '.html');
        }
    }

    var clickHandlers = function() {
        wok.topic('sidebarClicked').subscribe(onSidebarRedirect);

        $('#sidebar.list-group').on('click', 'a', function(e) {
            e.preventDefault();
            e.stopPropagation();
            var href = $(this).attr('href');
            checkHash(href.substring(0, href.lastIndexOf('.')));
        });
    };

    var triggerFirstAvailableOption = function() {
        var el = this.el;
        $('li > a', el).first().trigger('click');
    }

    return {
        THIS_PLUGIN: THIS_PLUGIN,
        createSidebar: createSidebar,
        onSidebarRedirect: onSidebarRedirect,
        loadPanel: loadPanel,
        checkHash: checkHash,
        clickHandlers: clickHandlers,
        triggerFirstAvailableOption: triggerFirstAvailableOption
    };
})();

ginger.initSidebar = function() {
    var $sidebar = $('#sidebar');
    var $leftCol = $('#leftCol');
    var $content = $('#rightCol');
    var $body = $(document.body);
    var navHeight = $('.topbar').outerHeight(true) + 40;

    ginger.getCapabilities(function(result) {
        if (result.Audit) {
            ginger.sidebarObj.push({
                title: i18n['Audit'],
                url: 'plugins/ginger/host-audit.html',
                id: 'ginger-audit'
            });
        }

        var start = new Sidebar($leftCol, ginger.sidebarObj);
        lastGingerPage = wok.cookie.get('lastGingerPage')
        if (!lastGingerPage)
            start.triggerFirstAvailableOption();
        else
            wok.topic('sidebarClicked').publish(lastGingerPage);
    });

    var checkScrollPosition = function() {
        if ($(window).scrollTop() + $(window).height() > $(document).height() - 66) {
            var $bottom = ($(window).scrollTop() + $(window).height()) - $(document).height();
            $('#sidebar.affix').css('bottom', '66px');
        } else {
            $('#sidebar.affix').css('bottom', '6px');
        }
    };

    /* activate sidebar */
    if ($content.height() > $sidebar.height()) {
        $sidebar.affix({
            offset: {
                top: 210
            }
        });

        $body.scrollspy({
            target: '#leftCol',
            offset: navHeight
        });

        $(window).on("load resize scroll", function(e) {
            checkScrollPosition();
        });
    }
};
