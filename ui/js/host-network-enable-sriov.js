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

ginger.initEnableSriov = function() {
    $("#modal-interface-name").text(ginger.selectedInterface['device']);
    ginger.enableJustNumbers();

    var message = '';
    var reloadProgressArea = function(result) {

        if (result['status'] == 'finished') {
            message = 'FINISHED: \n' + result['message'];
            $("#action-dropdown-button-nw-configuration-actions").prop("disabled", false);
        } else if (result['status'] == 'failed') {
            message = 'FAILED: \n' + result['message'];
            $("#action-dropdown-button-nw-configuration-actions").prop("disabled", false);
        } else if(result['status'] == 'running') {
            message += result['message'] + '\n';
            $("#action-dropdown-button-nw-configuration-actions").prop("disabled", true);
        }

        $('#status-sriov').text(message);
    };

    $(".save-button").on('click', function() {
        var numVFs = 0;
        if (!$("#disableSrIov").is(":checked")) {
            numVFs = $("#number-virtual-functions").val();
        }
        var data = {
            "num_vfs": numVFs
        };
        $('#enable-sriov-progress-container').show();
        wok.window.close();
        ginger.enableNetworkSRIOV(data, ginger.selectedInterface['device'], function(result){
            setTimeout(function() {
                reloadProgressArea(result);
            }, 700);
            ginger.initNetworkConfigGridData();
        }, function(error){
            wok.message.error(error.responseJSON.reason, '#message-nw-container-area', true);
        }, reloadProgressArea);
    });

    $("#disableSrIov").on("click", function() {
        $("#number-virtual-functions").prop("disabled", this.checked);
    });
};

ginger.enableJustNumbers = function() {
    $("#number-virtual-functions").keydown(function (e) {
    // Allow: backspace, delete, tab, escape, enter and .
    if ($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110, 190]) !== -1 ||
        // Allow: Ctrl+A, Command+A
        (e.keyCode == 65 && ( e.ctrlKey === true || e.metaKey === true ) ) ||
        // Allow: home, end, left, right, down, up
        (e.keyCode >= 35 && e.keyCode <= 40)) {
            // let it happen, don't do anything
            return;
        }
        // Ensure that it is a number and stop the keypress; do not allow the number 0 either
        if ((e.shiftKey || (e.keyCode < 49 || e.keyCode > 57)) && (e.keyCode < 97 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
}
