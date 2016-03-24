ginger.initEnableSriov = function() {
	$("#modal-interface-name").text(ginger.selectedInterface['device']);
	ginger.enableJustNumbers();

    $(".save-button").on('click', function() {
    	var data = {
    		"name": "SR-IOV",
    		"args": {
    			"num_vfs": $("#number-virtual-functions").val()
    		}
    	};
    	ginger.enableNetworkSRIOV(data, function(result){
    		ginger.initNetworkConfigGridData();
    	}, function(error){
    		wok.message.error(error.responseJSON.reason, '#message-nw-container-area', true);
    	});
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
        // Ensure that it is a number and stop the keypress
        if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
            e.preventDefault();
        }
    });
}

