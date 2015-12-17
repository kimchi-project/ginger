/*
 * Copyright IBM Corp, 2015
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

ginger = {};

ginger.getFirmware = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/firmware',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.updateFirmware = function(content, suc, err){
    $.ajax({
        url : "plugins/ginger/firmware",
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.listBackupArchives = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/backup/archives',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.createBackupArchive = function(bak, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/backup/archives',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(bak),
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getBackupArchiveFile = function(id, suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/backup/archives/' + encodeURIComponent(id) + '/file',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.deleteBackupArchive = function(id, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/backup/archives/' + encodeURIComponent(id),
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.deleteBackupArchives = function(content, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/backup/discard_archives',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getInterfaces = function(suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/network/interfaces',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.updateInterface = function(name, content, suc, err){
    $.ajax({
        url : 'plugins/ginger/network/interfaces/' + encodeURIComponent(name),
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getNetworkGlobals = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/network',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.updateNetworkGlobals = function(content, suc, err){
    $.ajax({
        url : 'plugins/ginger/network',
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.confirmNetworkUpdate = function(suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/network/confirm_change',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.confirmInterfaceUpdate = function(name, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/network/interfaces/' + encodeURIComponent(name) + '/confirm_change',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
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
};

ginger.getPowerProfiles = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/powerprofiles',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.activatePowerProfile = function(name, suc, err){
    $.ajax({
        url : "plugins/ginger/powerprofiles/" + encodeURIComponent(name),
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify({ active: true }),
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getSANAdapters = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/san_adapters',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getSensors = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/sensors',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getSEPSubscriptions = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/ibm_sep',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.deleteSubscription = function (hostname, suc, err) {
    wok.requestJSON({
        url : wok.url + 'plugins/ginger/ibm_sep/subscribers/' + hostname,
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.addSEPSubscription = function(subscription, suc, err){
    wok.requestJSON({
        url : wok.url + 'plugins/ginger/ibm_sep/subscribers',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(subscription),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getSEPStatus = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/ibm_sep',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.startSEP = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/ibm_sep/start',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.stopSEP = function(suc, err){
    wok.requestJSON({
        url : 'plugins/ginger/ibm_sep/stop',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.getUsers = function(suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/users',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        resend : true,
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.addUser = function(username, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/users',
        type : 'POST',
        contentType : 'application/json',
        data : JSON.stringify(username),
        dataType : 'json',
        resend : true,
        success : suc,
        error :  err || function(data) {
             wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.deleteUser = function (username, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/users/' + username,
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.getCapabilities = function(suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/capabilities',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}
