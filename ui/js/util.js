/*
 * Copyright IBM Corp, 2014-2016
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

ginger.updateFirmware = function(content, suc, err, progress) {
    var onResponse = function(data) {
        ginger.trackTask(data['id'], suc, suc, progress);
    };

    $.ajax({
        url : "plugins/ginger/firmware/upgrade",
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: onResponse,
        error: err
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

ginger.SwapDeviceList = function(suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/partitions/',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        resend: true,
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.addDeviceswap = function(selectedRowIds, suc, err) {
    var onResponse = function(data) {
        taskID = data['id'];
        ginger.trackTask(taskID, suc, err);
    };
    wok.requestJSON({
        url: 'plugins/ginger/swaps/',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(selectedRowIds),
        dataType: 'json',
        success: onResponse,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.deleteswap = function(file_loc, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/swaps/' + encodeURIComponent(file_loc),
        type: 'DELETE',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.createBackupArchive = function(bak, suc, err, progress) {

  var onResponse = function(data) {
     taskID = data['id'];
     ginger.trackTask(taskID, suc, err, progress);
  };

    wok.requestJSON({
        url : 'plugins/ginger/backup/archives',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(bak),
        success : onResponse,
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

ginger.enableNetworkSRIOV = function(settings, name, suc, err, progress) {
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
            }, 3000);
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
        url : 'plugins/ginger/network/interfaces/' + name + '/enable_sriov',
        type : 'POST',
        contentType : 'application/json',
        data : JSON.stringify(settings),
        dataType : 'json',
        success: onResponse,
        error: err
    });
}

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

ginger.validateHostName = function(hostname) {
  var hostNameRegex = /^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$/;
  return hostNameRegex.test(hostname);
};

ginger.validateMask = function(mask) {
  if (mask.indexOf('.') != -1) {
    var secs = mask.split('.');
    if (secs.length == 4) {
      // Check first if the given input is following valid IP format.
      if (ginger.validateIp(mask)) {
        // Validate the netmask format
        var binMask = "";
        for (var i = 0; i < secs.length; i++) {
          var binNumber = parseInt(secs[i]).toString(2);
          if (binNumber.length != 8) {
            for (var bits = binNumber.length; bits < 8; bits++) {
              // Binary number should be of 8 digits to validate netmask properly
              binNumber = '0' + binNumber;
            }
          }
          binMask += binNumber;
        }
        return /^1+0*$/.test(binMask);
      }
    } else {
      return false;
    }
  } else {
    return mask >= 1 && mask <= 32;
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
        headers: {'Wok-Robot': 'wok-robot'},
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

ginger.changeUserPassword = function (username, content, suc, err) {
  $.ajax({
        url : "plugins/ginger/users/" + username + "/chpasswd",
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: suc,
        error: err || function(data) {
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

        if (ipv6addr.split(":").length == 1 && ipv6addr.indexOf('.')==-1) {
             var octet = '(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9][0-9]|[0-9])';
             var ip = '(?:' + octet + '\\.){3}' + octet;
             var ipRE = new RegExp('^' + ip + '$');
             return ipRE.test(ipv6addr);
      }else {
         if(/^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$|^(([a-fA-f]|[a-fA-f][a-fA-f0-9\-]*[a-fA-f0-9])\.)*([A-fa-f]|[A-fa-f][A-fa-f0-9\-]*[A-fa-f0-9])$|^(?:(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){6})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:::(?:(?:(?:[0-9a-fA-F]{1,4})):){5})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:(?:[0-9a-fA-F]{1,4})):){4})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,1}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:(?:[0-9a-fA-F]{1,4})):){3})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,2}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:(?:[0-9a-fA-F]{1,4})):){2})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,3}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:[0-9a-fA-F]{1,4})):)(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,4}(?:(?:[0-9a-fA-F]{1,4})))?::)(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,5}(?:(?:[0-9a-fA-F]{1,4})))?::)(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,6}(?:(?:[0-9a-fA-F]{1,4})))?::))))$/.test(ipv6addr)){
           if (!ginger.validateIp(ipv6addr)) {
                   return true;
            }
           return false;
         }
         return false;
      }
}

ginger.isValidIPv6Prefix = function(prefix) {
  return prefix >= 1 && prefix <= 128;
}

ginger.isValidMacAddress = function(macaddress) {
    var macaddrRE = new RegExp('^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$');
    return macaddrRE.test(macaddress);
}

ginger.getSysmodules = function(suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/sysmodules',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
 }

ginger.getSysmodule = function(module, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/sysmodules/' + encodeURIComponent(module),
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 }

 ginger.loadSysmodule = function(parms, suc, err){
    $.ajax({
        url : "plugins/ginger/sysmodules",
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(parms),
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.removeSysmodule = function(moduleId, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/sysmodules/' + moduleId,
        type: 'DELETE',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}

ginger.getOvsBridges = function(suc,err) {
     wok.requestJSON({
        url: 'plugins/ginger/ovsbridges',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
 }

ginger.getOvsBridge = function(br, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/' + encodeURIComponent(br),
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 }

ginger.addOvsBridge = function(data, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(data),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.delOvsBridge = function(br, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/' + encodeURIComponent(br),
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason, '#ovs-alert-container');
        }
    });
};

ginger.addOvsBridgeInterface = function(br, data, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/'+encodeURIComponent(br)+'/add_interface',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(data),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.delOvsBridgeInterface = function(br, data, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/'+encodeURIComponent(br)+'/del_interface',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify({ 'interface': data }),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason, '#ovs-alert-container');
        }
    });
};

ginger.addOvsBridgeBond = function(br, data, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/'+encodeURIComponent(br)+'/add_bond',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(data),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.modifyOvsBridgeBond = function(br, data, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/'+encodeURIComponent(br)+'/modify_bond',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(data),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

ginger.delOvsBridgeBond = function(br, bond, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/ovsbridges/'+encodeURIComponent(br)+'/del_bond',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify({ 'bond': bond }),
        resend : true,
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason, '#ovs-alert-container');
        }
    });
};

ginger.getSystemServices = function (suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};

ginger.getSystemService = function (service, suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services/' + encodeURIComponent(service),
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};

ginger.startSystemService = function (service, suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services/' + encodeURIComponent(service) + '/start',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};

ginger.stopSystemService = function (service, suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services/' + encodeURIComponent(service) + '/stop',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};

ginger.restartSystemService = function (service, suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services/' + encodeURIComponent(service) + '/restart',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};

ginger.enableSystemService = function (service, suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services/' + encodeURIComponent(service) + '/enable',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};

ginger.disableSystemService = function (service, suc, err){
     wok.requestJSON({
        url: 'plugins/ginger/services/' + encodeURIComponent(service) + '/disable',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
};
