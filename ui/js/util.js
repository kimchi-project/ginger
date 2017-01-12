/*
 * Copyright IBM Corp, 2014-2017
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
        url: 'plugins/ginger/partitions?available=True',
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

ginger.restoreBackupArchive = function(id, suc, err, progress) {

    var onResponse = function(data) {
      taskID = data['id'];
      ginger.trackTask(taskID, suc, err, progress);
    };

    wok.requestJSON({
        url : 'plugins/ginger/backup/archives/' + encodeURIComponent(id) +
              '/restore/',
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        success : onResponse,
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
            $('html').addClass('in-progress');
            setTimeout(function() {
                trackTask();
            }, 3000);
            break;
        case 'finished':
        case 'failed':
            suc(result);
            $('html').removeClass('in-progress');
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

ginger.getDevicePartition =  function(devicename, suc , err){
    wok.requestJSON({
        url : 'plugins/ginger/partitions?name='+ devicename +'&&type=part',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
}

ginger.addDASDDevicePartition =  function(content, suc , err){

    wok.requestJSON({
        url : 'plugins/ginger/dasdpartitions',
        type : 'POST',
        data : JSON.stringify(content),
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
        });
}

ginger.getDevicePartitionPath =  function(device, suc , err, sync=false){

    wok.requestJSON({
        url : 'plugins/ginger/partitions/'+device,
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        async : !sync,
        success : suc,
        error : err
        });
}

ginger.addDevicePartition =  function(content, suc , err){

    wok.requestJSON({
        url : 'plugins/ginger/partitions',
        type : 'POST',
        data : JSON.stringify(content),
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
        });
}

ginger.deleteDASDDevicePartition =  function(devicename, suc , err){

    wok.requestJSON({
        url : 'plugins/ginger/dasdpartitions/'+ devicename,
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
}

ginger.deleteDevicePartition =  function(devicename, suc , err){

    wok.requestJSON({
        url : 'plugins/ginger/partitions/'+ devicename,
        type : 'DELETE',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
    });
}

ginger.formatPartitionDevice =  function(content, suc , err, progress){

    var onResponse = function(data) {
       taskID = data['id'];
       ginger.trackTask(taskID, suc, err, progress);
    };

    wok.requestJSON({
        url : 'plugins/ginger/partitions/'+ content.deviceName +'/format',
        type : 'POST',
        data : JSON.stringify(content.fstype),
        contentType : 'application/json',
        dataType : 'json',
        success : onResponse,
        error : err
      });
}

ginger.PartitionCreatePVs =  function(pv_name, suc , err, progress){

    var onResponse = function(data) {
       taskID = data['id'];
       ginger.trackTask(taskID, suc, err, progress);
    };

    wok.requestJSON({
        url : 'plugins/ginger/pvs',
        type : 'POST',
        data : JSON.stringify(pv_name),
        contentType : 'application/json',
        dataType : 'json',
        success : onResponse,
        error : err
      });
}

ginger.PartitionDeviceAddtoVG =  function(content, suc , err){

        wok.requestJSON({
        url : 'plugins/ginger/vgs/'+ content.vg +'/extend',
        type : 'POST',
        data : JSON.stringify(content.pv_paths),
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
      });
}

ginger.PartitionDeviceRemoveFromVG =  function(content, suc , err){

        wok.requestJSON({
        url : 'plugins/ginger/vgs/'+ content.vg +'/reduce',
        type : 'POST',
        data : JSON.stringify(content.pv_paths),
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err
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
            $('html').addClass('in-progress');
            setTimeout(function() {
                ginger.trackTask(taskID, suc, err, progress);
            }, 2000);
            break;
        case 'finished':
            suc && suc(result);
            $('html').removeClass('in-progress');
            break;
        case 'failed':
            err && err(result);
            $('html').removeClass('in-progress');
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
    } else {
        var ipv6regex = new RegExp(['^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])',
            '$|^(([a-fA-f]|[a-fA-f][a-fA-f0-9\\-]*[a-fA-f0-9])\\.)*([A-fa-f]|[A-fa-f][A-fa-f0-9\\-]*[A-fa-f0-9])',
            '$|^(?:(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){6})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))',
            '|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))',
            '|(?:(?:::(?:(?:(?:[0-9a-fA-F]{1,4})):){5})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]',
            '|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})))?::',
            '(?:(?:(?:[0-9a-fA-F]{1,4})):){4})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]',
            '|2[0-4])?[0-9]))\\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,1}(?:(?:[0-9a-fA-F]{1,4})))',
            '?::(?:(?:(?:[0-9a-fA-F]{1,4})):){3})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])',
            '?[0-9]))\\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,2}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:',
            '(?:[0-9a-fA-F]{1,4})):){2})(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\\.)',
            '{3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,3}(?:(?:[0-9a-fA-F]{1,4})))?::(?:(?:[0-9a-fA-F]{1,4}))',
            ':)(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\\.){3}(?:(?:25[0-5]|',
            '(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,4}(?:(?:[0-9a-fA-F]{1,4})))?::)(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4}))',
            ':(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9]))\\.){3}(?:(?:25[0-5]|(?:[1-9]|1[0-9]|2[0-4])?[0-9])))))))|',
            '(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):){0,5}(?:(?:[0-9a-fA-F]{1,4})))?::)(?:(?:[0-9a-fA-F]{1,4})))|(?:(?:(?:(?:(?:(?:[0-9a-fA-F]{1,4})):)',
            '{0,6}(?:(?:[0-9a-fA-F]{1,4})))?::))))$'])

        if(ipv6regex.test(ipv6addr)){
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

ginger.getAllSysmodules = function(suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/sysmodules?_all=true',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
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

ginger.createActionButtons = function(settings) {
  var toolbarNode = null;
  var btnHTML, dropHTML = [];
  var container = settings.panelID;
  var toolbarButtons = settings.buttons;
  var buttonType = settings.type;
  toolbarNode = $('<div class="btn-group"></div>');
  toolbarNode.appendTo($("#" + container));
  dropHTML = ['<div class="dropdown menu-flat">',
    '<button id="action-dropdown-button-', container, '" class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">', (buttonType === 'action') ? '<span class="edit-alt"></span>'+ i18n['GINBG00003M'] : '<i class="fa fa-plus-circle"></i>'+ i18n['GINBG00004M'], '<span class="caret"></span>',
    '</button>',
    '<ul class="dropdown-menu"></ul>',
    '</div>'
  ].join('');
  $(dropHTML).appendTo(toolbarNode);

  $.each(toolbarButtons, function(i, button) {
    var btnHTML = [
      '<li role="presentation"', button.critical === true ? ' class="critical"' : '', '>',
      '<a role="menuitem" tabindex="-1" data-backdrop="static"  data-keyboard="false" data-dismiss="modal"', (button.id ? (' id="' + button.id + '"') : ''), (button.disabled === true ? ' class="disabled"' : ''),
      '>',
      button.class ? ('<i class="' + button.class) + '"></i>' : '',
      button.label,
      '</a></li>'
    ].join('');
    var btnNode = $(btnHTML).appendTo($('.dropdown-menu', toolbarNode));
    button.onClick && btnNode.on('click', button.onClick);
  });
}

/**
 * Get the partition list.
 */
ginger.getPartition = function(suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/partitions?fstype=ext4|ext3|xfs&mountpoint=None',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };

/**
* Mount file system.
*/
ginger.mountFileSystem = function(content, suc, err) {
     wok.requestJSON({
         url: "/plugins/ginger/filesystems",
         type: 'POST',
         contentType: "application/json",
         dataType: 'json',
         data : JSON.stringify(content),
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };

 /**
  * Unmount file system.
  */
 ginger.unmountFileSystem = function(mountPoint, suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/filesystems/' + encodeURIComponent(mountPoint),
       type : 'DELETE',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Get the file system details.
  */
 ginger.getFileSystemDetails = function(mountPoint, suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/filesystems/' + encodeURIComponent(mountPoint),
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Getting nfs paths on a specific nfs server.
  */
  ginger.getNfsShare = function(ipaddress,suc, err) {
       wok.requestJSON({
          url: 'plugins/ginger/stgserver/'+ipaddress+'/nfsshares',
          type: 'GET',
          contentType: 'application/json',
          dataType: 'json',
          success: suc,
          error: err || function(data) {
               wok.message.error(data.responseJSON.reason);
           }
       });
   };

/**
 * Get the volume group details.
 */
ginger.getVolumeGroupDetails = function(vgName, suc, err) {
  wok.requestJSON({
      url : '/plugins/ginger/vgs/'+encodeURIComponent(vgName.trim()),
      type : 'GET',
      contentType : 'application/json',
      dataType : 'json',
      success : suc,
      error : err || function(data) {
          wok.message.error(data.responseJSON.reason);
      }
  });
};

/**
 * Create volume group with pvs.
 */
ginger.createVolumeGroup= function(content, suc, err, progress){

    var onResponse = function(data) {
      taskID = data['id'];
      ginger.trackTask(taskID, suc, err, progress);
    };

    $.ajax({
        url : "plugins/ginger/vgs",
        type : 'POST',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(content),
        success: onResponse,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};

/**
 * Delete Volume group.
 */
ginger.deleteVolumeGroup = function(vgName, suc, err) {
  wok.requestJSON({
      url : '/plugins/ginger/vgs/'+encodeURIComponent(vgName.trim()),
      type : 'DELETE',
      contentType : 'application/json',
      dataType : 'json',
      success : suc,
      error : err || function(data) {
          wok.message.error(data.responseJSON.reason);
      }
  });
};

/**
 * Get the physical volumes list.
 */
ginger.getPhysicalVolumes = function(suc, err) {
  wok.requestJSON({
      url : '/plugins/ginger/pvs?VGName=None',
      type : 'GET',
      contentType : 'application/json',
      dataType : 'json',
      success : suc,
      error : err || function(data) {
          wok.message.error(data.responseJSON.reason);
      }
  });
};

/**
 * Create  physical volume.
 */
ginger.createPhysicalVolume = function(pv_path,suc, err, progress) {
  var onResponse = function(data) {
    taskID = data['id'];
    ginger.trackTask(taskID, suc, err, progress);
  };

  wok.requestJSON({
      url : '/plugins/ginger/pvs/',
      type : 'POST',
      contentType : 'application/json',
      data: JSON.stringify(pv_path),
      dataType : 'json',
      success : onResponse,
      error : err || function(data) {
          wok.message.error(data.responseJSON.reason);
      }
  });
};
/**
 * Get the partition list.
 */
ginger.getPartitionsDevices = function(type,suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/partitions?vgname=N/A&available=True',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };

 /**
  * Get the  expand/reduce volume group .
  */
 ginger.editgetVolumeGroup = function(vgName,pvPaths,type, suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/vgs/'+encodeURIComponent(vgName.trim())+"/"+type,
       type : 'POST',
       contentType : 'application/json',
       dataType : 'json',
       data : JSON.stringify(pvPaths),
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

/*
* ISCSI
*/

ginger.getiSCSIqns =  function(suc , err){
	wok.requestJSON({
        url : 'plugins/ginger/iscsi_qns',
        type : 'GET',
        contentType : 'application/json',
        dataType : 'json',
        success : suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
}

ginger.getiSCSItargets = function(content, suc, err){
  wok.requestJSON({
     url: 'plugins/ginger/stgserver/'+ content.ip + ':' + content.port +'/iscsitargets',
     type: 'GET',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.iSCSItargetslogin = function(target, suc, err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_qns/'+ target +'/login',
     type: 'POST',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.iSCSItargetslogout = function(target, suc, err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_qns/'+ target +'/logout',
     type: 'POST',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.iSCSItargetsremove = function(target, suc, err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_qns/'+ target,
     type: 'DELETE',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};
ginger.iSCSItargetsrescan = function(target, suc, err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_qns/'+ target +'/rescan',
     type: 'POST',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.getiSCSIglobalAuthdetails = function(suc, err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_auth',
     type: 'GET',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.getiSCSItargetSettings = function(target,suc,err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_qns/'+target,
     type: 'GET',
     contentType: 'application/json',
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.iSCSIupdateTargetsettingsDetail = function(content,suc,err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_qns/'+ content.target +'/'+content.api,
     type: 'POST',
     contentType: 'application/json',
     data : JSON.stringify(content.data),
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

ginger.iSCSIupdateSettingsDetail = function(content,suc,err){
  wok.requestJSON({
     url: 'plugins/ginger/iscsi_auth/'+content.api,
     type: 'POST',
     contentType: 'application/json',
     data : JSON.stringify(content.data),
     dataType: 'json',
     success: suc,
     error : err || function(data) {
         wok.message.error(data.responseJSON.reason);
     }
  });
};

/**
 * Get the Audit Rules list.
 */

ginger.getAuditRules = function(suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/rules',
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };
 ginger.addFileAudit = function(filerule, suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/rules',
         type: 'POST',
         contentType: 'application/json',
         data: JSON.stringify(filerule),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.addControlAudit = function(cntrlrule, suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/rules',
         type: 'POST',
         contentType: 'application/json',
         data: JSON.stringify(cntrlrule),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.addSyscallAudit = function(syscallrule, suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/rules',
         type: 'POST',
         contentType: 'application/json',
         data: JSON.stringify(syscallrule),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.deleteAuditRule = function(ruleName, suc, err) {
     wok.requestJSON({
         url: '/plugins/ginger/audit/rules/' + encodeURIComponent(ruleName.replace('&lt;','<').replace('&gt;','>').trim()),
         type: 'DELETE',
         contentType: 'application/json',
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.LoadAuditRule = function(ruleName, suc, err) {
     wok.requestJSON({
         url: '/plugins/ginger/audit/rules/' + encodeURIComponent(ruleName.trim()) + "/load",
         type: 'POST',
         contentType: 'application/json',
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.UnLoadAuditRule = function(ruleName, suc, err) {
     wok.requestJSON({
         url: '/plugins/ginger/audit/rules/' + encodeURIComponent(ruleName.trim()) + "/unload",
         type: 'POST',
         contentType: 'application/json',
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.PersistAuditRule = function(ruleName, suc, err) {
     wok.requestJSON({
         url: '/plugins/ginger/audit/rules/' + encodeURIComponent(ruleName.trim()) + "/persist",
         type: 'POST',
         contentType: 'application/json',
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.retrieveConfigInfo = function(suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/conf',
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
 ginger.loadPredefinedRule = function(path, suc, err) {
     wok.requestJSON({
         url: '/plugins/ginger/audit/load_rules',
         type: 'POST',
         contentType: 'application/json',
         data: JSON.stringify(path),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.AuditConfig = function(configvalues, suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/conf',
         type: 'PUT',
         contentType: 'application/json',
         data: JSON.stringify(configvalues),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.EditAuditRule = function(ruleName, updatedRule, suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/rules/' + encodeURIComponent(ruleName.trim()),
         type: 'PUT',
         contentType: 'application/json',
         data: JSON.stringify(updatedRule),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.EditSyscallAudit = function(ruleName, updatedRule, suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/rules/' + encodeURIComponent(ruleName.replace('&lt;','<').replace('&gt;','>').trim()),
         type: 'PUT',
         contentType: 'application/json',
         data: JSON.stringify(updatedRule),
         dataType: 'json',
         success: suc,
         error: err || function(data) {
             wok.message.error(data.responseJSON.reason);
         }
     });
 };
 ginger.listofsyscall = function(suc, err) {
     wok.requestJSON({
         url: 'plugins/ginger/audit/syscall',
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
/**
  * Get the Audit logs list.
  */
 ginger.getAuditLogs = function(suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/logs',
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Get the Audit logs filter.
  */
 ginger.filterAuditLogs = function(params, suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/logs?_filter='+encodeURIComponent(params),
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Get the Audit summary report.
  */
 ginger.getAuditSummaryReport = function(suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/reports',
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Get the Audit report after filtering.
  */
 ginger.getAuditReport = function(params,suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/reports?_filter='+encodeURIComponent(params),
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };
 /**
  * Get the report graph.
  */
 ginger.getReportGraph = function(params,suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/graphs?_filter='+params,
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };
/**
  * Get the Audit dispatcher plugin.
  */
 ginger.getDispatcherPlugin = function(suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/auditdisp/plugins',
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Get the audit dispatcher status.
  */
 ginger.getAuditStatus = function(suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/conf',
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * Change audit dispatcher status.
  */
 ginger.changeAuditDispatcherStatus = function(action,suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/audit/conf/audisp_'+action,
       type : 'POST',
       contentType : 'application/json',
       dataType : 'json',
       data :'',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * get audit dispatcher details.
  */
 ginger.getDispatcherConfiguration = function(suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/auditdisp',
       type : 'GET',
       contentType : 'application/json',
       dataType : 'json',
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * update audit dispatcher details.
  */
 ginger.updateDispatcherConfiguration = function(params, suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/auditdisp',
       type : 'PUT',
       contentType : 'application/json',
       dataType : 'json',
       data : JSON.stringify(params),
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

 /**
  * update audit dispatcher plugin.
  */
 ginger.updateDispatcherPlugin = function(name,params, suc, err) {
   wok.requestJSON({
       url : '/plugins/ginger/auditdisp/plugins/'+name,
       type : 'PUT',
       contentType : 'application/json',
       dataType : 'json',
       data : JSON.stringify(params),
       success : suc,
       error : err || function(data) {
           wok.message.error(data.responseJSON.reason);
       }
   });
 };

/**
 * Systems Platform Management
 */
ginger.getServer = function(suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/servers',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.addServer = function(parms, suc, err){
    $.ajax({
        url : "plugins/ginger/servers",
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
ginger.UpdServer = function(name, params, suc, err){
    $.ajax({
        url : 'plugins/ginger/servers/' + name,
        type : 'PUT',
        contentType : 'application/json',
        dataType : 'json',
        data : JSON.stringify(params),
        success: suc,
        error: err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
    });
};
ginger.removeServer = function(moduleId, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/servers/' + moduleId,
        type: 'DELETE',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.serverPowerOn = function(moduleId, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/servers/' + moduleId + '/poweron',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.serverPowerOff = function(moduleId, suc, err) {
    wok.requestJSON({
        url: 'plugins/ginger/servers/' + moduleId + '/poweroff',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.getSel = function(serverName, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/servers/'+ serverName + '/sels',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
 }
ginger.deleteSel = function(serverName, eventId, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/servers/'+ serverName + '/sels/' + eventId,
        type: 'DELETE',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.getSdr = function(serverName, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/servers/'+ serverName + '/sensors',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.getSdrType = function(serverName, sdrType, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/servers/'+ serverName + '/sensors' + '?sensor_type=' + sdrType,
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
ginger.getFru = function(serverName, suc, err) {
     wok.requestJSON({
        url: 'plugins/ginger/servers/'+ serverName + '/frus',
        type: 'GET',
        contentType: 'application/json',
        dataType: 'json',
        success: suc,
        error : err || function(data) {
            wok.message.error(data.responseJSON.reason);
        }
     });
}
