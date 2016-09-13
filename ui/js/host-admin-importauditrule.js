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
ginger.initImportRule = function() {
    $('#AuditImport-submit').on('click', function(event) {
        var path = $("#import-filepath").val();
        var resultpath = {};
        resultpath['auditrule_file'] = path;
        if (path.length == 0) {
            wok.message.error(i18n["GINAUDIT0032M"], "#importrule-message");
        } else {
            ginger.loadPredefinedRule(resultpath, function() {
                wok.window.close();
                $('#Audit-Rule-refresh-btn').trigger('click');
                wok.message.success(i18n["GINAUDIT0025M"], "#audit-message")
            }, function(result) {
                wok.message.error(result.responseJSON.reason, "#importrule-message", true);
            });
        }
    });
}
