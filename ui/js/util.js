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
