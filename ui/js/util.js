ginger = {};

ginger.getFirmware = function(suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/firmware',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.updateFirmware = function(content, suc, err){
    $.ajax({
        url : kimchi.url + "plugins/ginger/firmware",
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.listBackupArchives = function(suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/backup/archives',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.createBackupArchive = function(bak, suc, err) {
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/backup/archives',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(bak),
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getBackupArchiveFile = function(id, suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/backup/archives/' + encodeURIComponent(id) + '/file',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.deleteBackupArchive = function(id, suc, err) {
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/backup/archives/' + encodeURIComponent(id),
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.deleteBackupArchives = function(content, suc, err) {
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/backup/discard_archives',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getInterfaces = function(suc, err) {
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/network/interfaces',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.updateInterface = function(name, content, suc, err){
    $.ajax({
        url : kimchi.url + 'plugins/ginger/network/interfaces/' + encodeURIComponent(name),
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getNetworkGlobals = function(suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/network',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.updateNetworkGlobals = function(content, suc, err){
    $.ajax({
        url : kimchi.url + 'plugins/ginger/network',
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.confirmNetworkUpdate = function(suc, err) {
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/network/confirm_change',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.confirmInterfaceUpdate = function(name, suc, err) {
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/network/interfaces/' + encodeURIComponent(name) + '/confirm_change',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.validateIp = function(ip){
    var ipReg = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
    return ipReg.test(ip);
};

ginger.validateMask = function(mask){
    if(mask.indexOf('.')!=-1){
        var secs = mask.split('.');
        var binMask = "";
        for(var i=0; i<secs.length; i++)
            binMask += parseInt(secs[i]).toString(2);
        return /^1+0+$/.test(binMask);
    }else{
        return mask > 0 && mask < 32;
    }
}

ginger.getPowerProfiles = function(suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/powerprofiles',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.activatePowerProfile = function(name, suc, err){
    $.ajax({
        url : kimchi.url + "plugins/ginger/powerprofiles/" + encodeURIComponent(name),
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify({ active: true }),
        success: suc,
        error: err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getSANAdapters = function(suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/san_adapters',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getSensors = function(suc, err){
    kimchi.requestJSON({
        url : kimchi.url + 'plugins/ginger/sensors',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            kimchi.message.error(data.responseJSON.reason);
        }
    });
};
