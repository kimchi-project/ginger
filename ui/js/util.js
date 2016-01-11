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
ginger.hostarch = null;
ginger.selectedInterface = null;

trackingTasks = [];
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

ginger.fwProgress = function(suc, err, progress) {
    var taskID = -1;
    var onResponse = function(data) {
        taskID = data['id'];
        trackTask();
    };

    var trackTask = function() {
        ginger.getTask(taskID, onTaskResponse, err);
    };

    var onTaskResponse = function(result) {
        var taskStatus = result['status'];
        switch(taskStatus) {
        case 'running':
            progress && progress(result);
            setTimeout(function() {
                trackTask();
            }, 1000);
            break;
        case 'finished':
        case 'failed':
            suc(result);
            break;
        default:
            break;
        }
    };

    wok.requestJSON({
        url : 'plugins/ginger/fwprogress',
        type : "GET",
        contentType : "application/json",
        dataType : "json",
        success : onResponse,
        error : err
    });
},


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

ginger.enableInterface = function(name, status, suc, err) {
    wok.requestJSON({
        url : "plugins/ginger/network/interfaces/" + name +
              '/' + (status == "down" ? 'deactivate' : 'activate'),
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
};

ginger.deleteInterface = function(name, suc, err) {
  wok.requestJSON({
      url : 'plugins/ginger/network/cfginterfaces/' + name,
      type : 'DELETE',
      contentType : 'application/json',
      dataType : 'json',
      success : suc,
      error : err || function(data) {
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

/**
 * Get the host information.
 */
ginger.getHostDetails = function (suc,err) {
  wok.requestJSON({
      url : 'plugins/gingerbase/host',
      type : 'GET',
      resend: true,
      contentType : 'application/json',
      dataType : 'json',
      success : suc,
      error: err
  });
}

/**
 * Get the host plugins information.
 */
ginger.getPlugins = function(suc, err) {
    wok.requestJSON({
        url : 'plugins',
        type : 'GET',
        resend: true,
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error: err
    });
};
ginger.getFilesystems =  function(suc , err){
	wok.requestJSON({
        url : 'plugins/ginger/filesystems',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}
ginger.getSwapdevices =  function(suc , err){
	wok.requestJSON({
        url : 'plugins/ginger/swaps',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.getVolumegroups =  function(suc , err){
	wok.requestJSON({
        url : 'plugins/ginger/vgs',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}
ginger.getStgdevs =  function(suc , err){
    wok.requestJSON({
        url : 'plugins/ginger/stgdevs',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.getFcpTapeDevices =  function(suc , err){
    wok.requestJSON({
        url : 'plugins/gingers390x/lstapes',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}
ginger.formatDASDDevice = function(busId, settings, suc, err, progress) {
    var onResponse = function(data) {
       taskID = data['id'];
       ginger.trackTask(taskID, suc, err, progress);
    };

    wok.requestJSON({
        url : '/plugins/ginger/dasddevs/'+busId+'/format',
        type : 'POST',
        contentType : 'application/json',
        data : JSON.stringify(settings),
        dataType : 'json',
        success: onResponse,
        error: err
    });
}

ginger.removeDASDDevice = function(busId, settings, suc, err, progress) {
    wok.requestJSON({
        url : "/plugins/gingers390x/storagedevices/"+ busId +"/offline",
        type : 'POST',
        contentType : 'application/json',
        data : JSON.stringify(settings),
        dataType : 'json',
        success: suc,
        error: err
    });
}

ginger.removeFCDevice = function(lunPath, settings, suc, err, progress) {
    wok.requestJSON({
        url : "/plugins/gingers390x/fcluns/"+ lunPath,
        type : 'DELETE',
        contentType : 'application/json',
        data : JSON.stringify(settings),
        dataType : 'json',
        success: suc,
        error: err
    });
}

ginger.getTask = function(taskId, suc, err) {
    wok.requestJSON({
        url : 'plugins/ginger/tasks/' + encodeURIComponent(taskId),
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
}
ginger.trackTask = function(taskID, suc, err, progress) {
    var onTaskResponse = function(result) {
        var taskStatus = result['status'];
        switch(taskStatus) {
        case 'running':
            progress && progress(result);
            setTimeout(function() {
                ginger.trackTask(taskID, suc, err, progress);
            }, 2000);
            break;
        case 'finished':
            suc && suc(result);
            break;
        case 'failed':
            err && err(result);
            break;
        default:
            break;
        }
    };

    ginger.getTask(taskID, onTaskResponse, err);
    if(trackingTasks.indexOf(taskID) < 0)
        trackingTasks.push(taskID);
}

ginger.trackdevices = function(trackDevicelist,removeItem) {
    "use strict";
    trackDevicelist = jQuery.grep(trackDevicelist, function(value) {
          return value != removeItem;
        });
    return trackDevicelist;
};

/**
 * Create a network interface with new information.
 */
ginger.createCfgInterface = function(settings, suc, err) {
  wok.requestJSON({
    url: 'plugins/ginger/network/cfginterfaces/',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify(settings),
    dataType: 'json',
    success: suc,
    error: err || function(data) {
      wok.message.error(data.responseJSON.reason);
    }
  });
}

/**
 * Retrieve the information of a cfg interfaces by its name from it's cfg file.
 *
 * @param interface name
 * @param suc callback for success
 * @param err callback for error
 */
ginger.listCfgInterface = function(suc, err) {
    wok.requestJSON({
      url: 'plugins/ginger/network/cfginterfaces/',
      type: 'GET',
      contentType: 'application/json',
      dataType: 'json',
      success: suc,
      error: err
    });
}
/**
 * Retrieve the information of a given network interface by its name from it's cfg file.
 *
 * @param interface name
 * @param suc callback for success
 * @param err callback for error
 */
ginger.retrieveCfgInterface = function(interface, suc, err) {
    wok.requestJSON({
      url: 'plugins/ginger/network/cfginterfaces/'+interface,
      type: 'GET',
      contentType: 'application/json',
      dataType: 'json',
      success: suc,
      error: err
    });
}
  /**
   * Update a network interface with new information.
   */
ginger.updateCfgInterface = function(interface, settings, suc, err) {
  wok.requestJSON({
    url: 'plugins/ginger/network/cfginterfaces/' + encodeURIComponent(interface),
    type: 'PUT',
    contentType: 'application/json',
    data: JSON.stringify(settings),
    dataType: 'json',
    success: suc,
    error: err
  });
}

ginger.disableclass =  function(clas){
  jQuery("."+clas).css('pointer-events', 'none')
  jQuery("."+clas).find("input, select, button, textarea, div").attr("disabled",true);
  jQuery("."+clas).css('opacity', '0.5')
}

ginger.enableclass =  function(clas){
  jQuery("."+clas).css('pointer-events', 'auto')
  jQuery("."+clas).find("input, select, button, textarea, div").attr("disabled",false);
  jQuery("."+clas).css('opacity', 'initial')
}

ginger.isInteger = function(value) {
return !isNaN(value) &&
       parseInt(Number(value)) == value &&
       !isNaN(parseInt(value, 10));
}

ginger.isValidIPv6 = function(ipv6addr) {
  if (/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$|^(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])$|^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))(%.+)?\s*$/.test(ipv6addr)) {
      return true;
  } else {
      return false;
  }
  return false;
}

ginger.isValidIPv6Prefix = function(prefix) {
  return prefix > 0 && prefix < 127;
}
