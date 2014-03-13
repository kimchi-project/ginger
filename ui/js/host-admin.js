ginger.initAdmin = function(){
    $("#gingerHostAdmin").accordion();
    $(".content-area", "#gingerHostAdmin").css("height", "100%");
    ginger.getFirmware(function(data){
        $("#gingerFWVer").html(data.level);
    });
    $("#gingerPackPath").on("keyup", function(evt) {
        var packPath = $("#gingerPackPath").prop("value");
        var isValid = /(^\/.*)$/.test(packPath);
        $("#gingerPackPath").toggleClass("invalid-field", !isValid && packPath!=="");
        $("#gingerPackPathSub").button(isValid ? "enable" : "disable");
    });
    $("#gingerPackPathSub").button({disabled: true}).click(function(){
        kimchi.confirm({
            title : i18n['KCHAPI6006M'],
            content : "The system will be immediately reset to flash the firmware. It may take longer than normal for it to reboot.",
            confirm : i18n['KCHAPI6002M'],
            cancel : i18n['KCHAPI6003M']
        }, function() {
            ginger.updateFirmware({ path: $("#gingerPackPath").prop("value") }, function(){
                $("#gingerFWUpdateMess").css("display", "inline-block");
                $("#gingerPackPathSub").button("disable");
                $("#gingerPackPath").prop("disabled", true);
            });
        }, null);
    });
};
