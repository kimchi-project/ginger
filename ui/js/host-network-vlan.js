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

ginger.initVLANInterfaceSettings = function() {

  nwApplyButton = $('#nw-vlan-button-apply');
  nwGeneralForm = $('#form-nw-vlan-general');
  nwIpv4Form = $('#form-nw-vlan-ipv4');
  nwIpv6Form = $('#form-nw-vlan-ipv6');
  nwAdvanceForm = $('#form-nw-vlan-advance');

  interfaceVLANTabs = $('#nw-vlan-tabs');
  nwTitle = $('#nw-vlan-title');
  hiddenDeviceTextbox = $('#vlan-interface-device', interfaceVLANTabs);

  //General Tab fields
  parentInterfaceSelect = $('#nw-vlan-interfaces-select', interfaceVLANTabs);
  nwVLANIDTextbox = $('#nw-vlan-vlanid-textbox', interfaceVLANTabs);
  nwVLANInterfaceTextbox = $('#nw-vlan-interface-textbox', interfaceVLANTabs);
  nwHwaddressTextbox = $('#nw-vlan-hwaddress-textbox', interfaceVLANTabs);
  onBootCheckbox = $('#nw-vlan-connect-auto', interfaceVLANTabs);

  ipv4MethodSelect = $('#nw-vlan-ipv4-method', interfaceVLANTabs);
  ipv6MethodSelect = $('#nw-vlan-ipv6-method', interfaceVLANTabs);
  ipv4VlanIPv4Method = $('#nw-vlan-ipv4-method', interfaceVLANTabs);
  ipv4AddressAddButton = $('#nw-vlan-ipv4-add', interfaceVLANTabs);
  ipv4DnsAddButton = $('#nw-vlan-ipv4-dns-add', interfaceVLANTabs);
  ipv4RoutesAddButton = $('#nw-vlan-ipv4-routes-add', interfaceVLANTabs);
  ipv4DefRouteCheckbox = $('#nw-vlan-ipv4-defroute', interfaceVLANTabs);

  ipv6GatewayTextbox = $('#nw-vlan-ipv6-gateway-textbox', interfaceVLANTabs);
  ipv6MethodSelect = $('#nw-vlan-ipv6-method', interfaceVLANTabs);
  ipv6AddressAddButton = $('#nw-vlan-ipv6-add', interfaceVLANTabs);
  ipv6DnsAddButton = $('#nw-vlan-ipv6-dns-add', interfaceVLANTabs);
  ipv6RoutesAddButton = $('#nw-vlan-ipv6-routes-add', interfaceVLANTabs);
  ipv6DefRouteCheckbox = $('#nw-vlan-ipv6-defroute', interfaceVLANTabs);

  //Advanced Tab fields
  mtuTextbox = $('#nw-vlan-mtu-textbox', interfaceVLANTabs);
  // zoneSelect = $('#nw-vlan-firewall-select', interfaceVLANTabs);

  selectedInterface = ginger.selectedInterface;

  if (selectedInterface == null) {
    // New VLAN interface creation
    populateGeneralTab(null); //populate general tab
    populateAdvanceTab(null); //populate advance tab
    populateIpv4SettingsTab(null); //populate ipv4 setting tab
    populateIpv6SettingsTab(null); //populate ipv6 setting tab
  } else if (selectedInterface != null) {
    hiddenDeviceTextbox.val(selectedInterface);
    // Get the interface setting details
    ginger.retrieveCfgInterface(selectedInterface, function suc(result) {
      populateGeneralTab(result); //populate general tab
      populateAdvanceTab(result); //populate advance tab
      populateIpv4SettingsTab(result); //populate ipv4 setting tab
      populateIpv6SettingsTab(result); //populate ipv6 setting tab
    }, function(error) {
      wok.message.error(error.responseJSON.reason, '#alert-nw-vlan-modal-container', true);
    });
  }

  applyOnClick();

  $('#nw-vlan-button-cancel').on('click', function() {
    wok.window.close();
    ginger.listNetworkConfig.refreshNetworkConfigurationDatatable();
  });

  $('#nw-vlan-button-close').on('click', function() {
    wok.window.close();
    ginger.listNetworkConfig.refreshNetworkConfigurationDatatable();
  });
}

var applyOnClick = function() {

  // on Apply button click
  nwApplyButton.on('click', function() {
    var data = {};

    nwApplyButton.prop('disabled', true);
    var interfaceDevice = nwVLANInterfaceTextbox.val();
    if(interfaceDevice == "") {
      wok.message.error(i18n['GINNWVLANS0001M'], '#alert-nw-vlan-modal-container', true);
      nwApplyButton.prop('disabled', false);
      return;
    }

    var getBasicInfoData = function() {
      var basic_info = {};
      var vlan_info = {};

      basic_info['TYPE'] = "vlan";
      if (onBootCheckbox.is(":checked")) {
        basic_info["ONBOOT"] = "yes";
      } else {
        basic_info["ONBOOT"] = "no";
      }
      basic_info["MTU"] = mtuTextbox.val();


      vlan_info['VLAN'] = 'yes';

      if(isValidDeviceName(interfaceDevice)) {
        basic_info['DEVICE'] = interfaceDevice
      } else {
        wok.message.error(i18n['GINNWVLANS0001M'], '#alert-nw-vlan-modal-container', true);
        nwApplyButton.prop('disabled', false);
        return false;
      }

      // If interface do not have VLANID in it then VLANID is must if interface name doesn't contains it
      var vlanID = nwVLANIDTextbox.val();
      if(vlanID != "" && isValidVLAN(vlanID)) {
        // Take out VLAN ID
        vlan_info['VLAN_ID'] = vlanID;
      } else if(getVLANIDFromDeviceName(interfaceDevice) != "") {
        vlan_info['VLAN_ID'] = getVLANIDFromDeviceName(interfaceDevice);
      } else if ((getVLANIDFromDeviceName(interfaceDevice) == "") && (vlanID == "") && (interfaceDevice.length <= 15)) {
      // If interface length is <= 15 && if it doesn't have vlan details within it or VLAND ID field
        wok.message.error(i18n['GINNWVLANS0002M'], '#alert-nw-vlan-modal-container', true);
        nwApplyButton.prop('disabled', false);
        return false;
      }

      vlan_info['PHYSDEV'] = parentInterfaceSelect.val();
      basic_info['VLANINFO'] = vlan_info;
      data['BASIC_INFO'] = basic_info;
      return true;
    }

    if(getBasicInfoData() == false)
      return;

    var getIpv4InfoData = function() {
      var ipv4_info = {}; //All ipv4 info from ipv4 tab

      if ($('.ipv4-on-off').bootstrapSwitch('state')) {
        ipv4_info['IPV4INIT'] = 'yes';

        var method = ipv4MethodSelect.val();
        if (method == i18n['Automatic(DHCP)']) {
          ipv4_info['BOOTPROTO'] = 'dhcp';
        } else if (method == "Manual") {
          ipv4_info['BOOTPROTO'] = 'none';
        }

        var opts = {};

        //Get IP address grid data
        opts['id'] = 'nw-vlan-ipv4-addresses';
        opts['gridId'] = "nw-vlan-ipv4-addresses-grid";
        ipv4Addresses = ginger.getCurrentRows(opts);

        //Get DNS grid data
        opts['id'] = 'nw-vlan-ipv4-dns';
        opts['gridId'] = "nw-vlan-ipv4-dns-grid";
        ipv4Dns = ginger.getCurrentRows(opts);

        //Get Routes grid data
        opts['id'] = 'nw-vlan-ipv4-routes';
        opts['gridId'] = "nw-vlan-ipv4-routes-grid";
        ipv4Routes = ginger.getCurrentRows(opts);

        if (method != i18n['Automatic(DHCP)'] && ipv4Addresses.length > 0) {
          ipv4_info['IPV4Addresses'] = ipv4Addresses;
        }

        if (ipv4Dns.length > 0) {
          dns = [];
          for (var i = 0; i < ipv4Dns.length; i++) {
            dnsValue = ipv4Dns[i].DNS;
            dns.push(dnsValue);
          }
          ipv4_info['DNSAddresses'] = dns;
        }

        if (ipv4Routes.length > 0) {
          ipv4_info['ROUTES'] = ipv4Routes;
        }

        if (ipv4DefRouteCheckbox.is(":checked")) {
          ipv4_info["DEFROUTE"] = "yes";
        } else {
          ipv4_info["DEFROUTE"] = "no";
        }
      } else {
        ipv4_info['IPV4INIT'] = 'no';
      }

      data['IPV4_INFO'] = ipv4_info
    }
    getIpv4InfoData();

    var getIpv6InfoData = function() {
      var ipv6_info = {}; //All ipv6 info from ipv6 tab

      if ($('.ipv6-on-off').bootstrapSwitch('state')) {
        ipv6_info['IPV6INIT'] = 'yes';

        var method = ipv6MethodSelect.val();
        if (method == i18n['Automatic']) {
          ipv6_info['IPV6_AUTOCONF'] = 'yes';
        } else if (method == "Manual") {
          ipv6_info['IPV6_AUTOCONF'] = 'no';
        }


        var opts = {};

        //Get IP address grid data
        opts['id'] = 'nw-vlan-ipv6-addresses';
        opts['gridId'] = "nw-vlan-ipv6-addresses-grid";
        ipv6Addresses = ginger.getCurrentRows(opts);

        //Get DNS grid data
        opts['id'] = 'nw-vlan-ipv6-dns';
        opts['gridId'] = "nw-vlan-ipv6-dns-grid";
        ipv6Dns = ginger.getCurrentRows(opts);

        //Get Routes grid data
        opts['id'] = 'nw-vlan-ipv6-routes';
        opts['gridId'] = "nw-vlan-ipv6-routes-grid";
        ipv6Routes = ginger.getCurrentRows(opts);

        if (method == i18n['GINNWS0003M'] && ipv6Addresses.length > 0) {
          ipv6_info['IPV6Addresses'] = ipv6Addresses;
        }

        if (ipv6GatewayTextbox.val() != "")
          ipv6_info["IPV6_DEFAULTGW"] = ipv6GatewayTextbox.val();

        // var nwIpv6FormData = nwIpv6Form.serializeObject();
        // ipv6_info["IPV6_DEFAULTGW"] = nwIpv6FormData["GATEWAY"];

        if (ipv6Dns.length > 0) {
          var dns = []
          for (var i = 0; i < ipv6Dns.length; i++) {
            dnsValue = ipv6Dns[i].DNS;
            dns.push(dnsValue);
          }
          ipv6_info['DNSAddresses'] = dns;
        }

        if (ipv6Routes.length > 0) {
          ipv6_info['ROUTES'] = ipv6Routes;
        }

        if (ipv6DefRouteCheckbox.is(":checked")) {
          ipv6_info["IPV6_DEFROUTE"] = "yes";
        } else {
          ipv6_info["IPV6_DEFROUTE"] = "no";
        }
      } else {
        ipv6_info['IPV6INIT'] = 'no';
      }
      data['IPV6_INFO'] = ipv6_info
    }
    getIpv6InfoData();

    if (ginger.selectedInterface == null) {
      ginger.createCfgInterface(data, function(result) {
        var message = i18n['GINNET0087M'].replace("%1", '<strong>' + nwVLANInterfaceTextbox.val() + '</strong>');
        wok.message.success(message, '#alert-nw-vlan-modal-container',true);
        $(nwApplyButton).prop('disabled', false);
        ginger.listNetworkConfig.refreshNetworkConfigurationDatatable();
        wok.window.close();
      }, function(err) {
        wok.message.error(err.responseJSON.reason, '#alert-nw-vlan-modal-container', true);
        $(nwApplyButton).prop('disabled', false);
      });
    } else {
      ginger.updateCfgInterface(interfaceDevice, data, function(result) {
        var message = i18n['GINNET0089M'].replace("%1", '<strong>' + nwVLANInterfaceTextbox.val() + '</strong>');
        wok.message.success(message, '#alert-nw-vlan-modal-container',true);
        $(nwApplyButton).prop('disabled', false);
        ginger.listNetworkConfig.refreshNetworkConfigurationDatatable();
        wok.window.close();
      }, function(err) {
        wok.message.error(err.responseJSON.reason, '#alert-nw-vlan-modal-container', true);
        $(nwApplyButton).prop('disabled', false);
      });
    }
  });
}

// function to populate general tab
var populateGeneralTab = function(interface) {
  //Populate the parent interfaces information
  ginger.listCfgInterface(function suc(result) {
    parentInterfaceSelect.empty();
    for (var i = 0; i < result.length; i++) {
      if (result[i].BASIC_INFO.DEVICE) {
        if ((interface != null) &&
           (result[i].BASIC_INFO.DEVICE == interface.BASIC_INFO.DEVICE)) {
            continue;
        }
        parentInterfaceSelect.append($("<option></option>")
          .attr("value", (result[i].BASIC_INFO.DEVICE).replace(/"/g, ""))
          .text((result[i].BASIC_INFO.DEVICE).replace(/"/g, "")));
      }else if (result[i].BASIC_INFO.NAME) {
        if ((interface != null) &&
           (result[i].BASIC_INFO.NAME == interface.BASIC_INFO.NAME)) {
            continue;
        }
        parentInterfaceSelect.append($("<option></option>")
          .attr("value", (result[i].BASIC_INFO.NAME).replace(/"/g, ""))
          .text((result[i].BASIC_INFO.NAME).replace(/"/g, "")));
      }

    }

    if ((interface != null) && (interface.BASIC_INFO.VLANINFO.PHYSDEV).replace(/"/g, "")) {
      var exists = false;
      $('#nw-vlan-interfaces-select option').each(function() {
        if (this.value == (interface.BASIC_INFO.VLANINFO.PHYSDEV).replace(/"/g, "")) {
          exists = true;
          return false;
        }
      });

      if (!exists) {
        parentInterfaceSelect.append($("<option></option>")
          .attr("value", (interface.BASIC_INFO.VLANINFO.PHYSDEV).replace(/"/g, ""))
          .text((interface.BASIC_INFO.VLANINFO.PHYSDEV).replace(/"/g, "")));
      }
      parentInterfaceSelect.val((interface.BASIC_INFO.VLANINFO.PHYSDEV).replace(/"/g, ""));
    }
  });

  if (interface == null) {
    nwTitle.append(i18n['GINNWS0014M']);
  } else {
    if(interface.BASIC_INFO.DEVICE){
      nwTitle.append(interface.BASIC_INFO.DEVICE);
      nwVLANInterfaceTextbox.val(interface.BASIC_INFO.DEVICE);
    }else {
      nwTitle.append(interface.BASIC_INFO.NAME);
      nwVLANInterfaceTextbox.val(interface.BASIC_INFO.NAME);
    }

    if (interface.BASIC_INFO.HWADDR)
      nwHwaddressTextbox.val(interface.BASIC_INFO.HWADDR);

    nwVLANInterfaceTextbox.prop('disabled', true);
    var VLANID;
    // Some issue with VLANID vs VLAN_ID
    if (interface.BASIC_INFO.VLANINFO.VLAN_ID)
      nwVLANIDTextbox.val(interface.BASIC_INFO.VLANINFO.VLAN_ID);

    if (interface.BASIC_INFO.DEVICE){
      nwVLANInterfaceTextbox.val(interface.BASIC_INFO.DEVICE);
    }else if (interface.BASIC_INFO.NAME){
      nwVLANInterfaceTextbox.val(interface.BASIC_INFO.NAME);
    }

    if (interface.BASIC_INFO.ONBOOT == "\"yes\"" || interface.BASIC_INFO.ONBOOT == "yes") {
      onBootCheckbox.prop('checked', true);
    }
  }

  nwVLANIDTextbox.on('keyup', function() {
    // Validate VLAN Id value, It should be integer and range 0-4094
    var vlanID = nwVLANIDTextbox.val();
    if (vlanID.length > 0) {
      var deviceName = nwVLANInterfaceTextbox.val();
      var isVlanIdValid = isValidVLAN(vlanID);
      if(deviceName!=""){
        if(deviceName.length==15 && deviceName.indexOf('.')!=-1){
          var interfaceName =deviceName.substring(0,deviceName.lastIndexOf("."));
          var interfaceNameLength=interfaceName.length+vlanID.length;

          if(interfaceNameLength>14){
              if(!isVlanIdValid){
                $("#nw-vlan-interface-textbox").toggleClass("invalid-field", isVlanIdValid);
              }else{
                $("#nw-vlan-interface-textbox").toggleClass("invalid-field", true);
              }
              $(this).toggleClass("invalid-field", !isVlanIdValid);
          }else{
              $(this).toggleClass("invalid-field", !isVlanIdValid);
              $("#nw-vlan-interface-textbox").toggleClass("invalid-field", false);
          }
        }else{
          if((deviceName.length+vlanID.length)>14){
            if(!isVlanIdValid){
              $("#nw-vlan-interface-textbox").toggleClass("invalid-field", isVlanIdValid);
            }else{
              $("#nw-vlan-interface-textbox").toggleClass("invalid-field", true);
            }
            $(this).toggleClass("invalid-field", !isVlanIdValid);
          }else{
            $(this).toggleClass("invalid-field", !isVlanIdValid);
            $("#nw-vlan-interface-textbox").toggleClass("invalid-field", false);
          }
        }
      }else{
         $(this).toggleClass("invalid-field", !(isValidVLAN(vlanID)));
       }
    } else {
      $(this).toggleClass("invalid-field", false);
    }
  });

  nwVLANInterfaceTextbox.on('keyup', function() {
    var deviceName = nwVLANInterfaceTextbox.val();
    if (isValidDeviceName(deviceName)) {
      $("#nw-vlan-interface-textbox").toggleClass("invalid-field", false);
      if (getVLANIDFromDeviceName(deviceName) != "")
        nwVLANIDTextbox.val(getVLANIDFromDeviceName(deviceName));
      else
        nwVLANIDTextbox.val("");
    } else {
      $("#nw-vlan-interface-textbox").toggleClass("invalid-field", true);
      nwVLANIDTextbox.val("");
    }
  });
};

var isValidDeviceName = function(deviceName) {
  var vlanID = ""
  // Check if vlan name contains string of formatters
  if ((deviceName.length >= 1) && (deviceName.length <= 15)) {
    if ((deviceName.indexOf("vlan") == 0)) {
      // vlan name convention vlan<VLANID> or vlan.<VLANID>
      if ((deviceName.length <= 9) && (deviceName.indexOf(".") != -1)) {
        vlanID = deviceName.split(".", 2).length == 2 ? deviceName.split(".", 2)[1] : null;
        return isValidVLAN(vlanID);
      } else if ((deviceName.length < 9) && (deviceName.indexOf(".") == -1)) {
        vlanID = deviceName.split("vlan", 2).length == 2 ? deviceName.split("vlan", 2)[1] : null;
        if (ginger.isInteger(vlanID))
          return isValidVLAN(vlanID);
        else
          return false;
      }
    } else if (deviceName.length <= 15) {
      // In this case String can be 15 characters ifname.<VLANID>
      return isValidIFName(deviceName);
    }
    return isValidVLAN(vlanID);
  } else if (deviceName.length > 15) {
    return false;
  }
  return true;
};

var isValidIFName = function (ifName) {
  if (ifName.length==15 && ifName.indexOf(".") != -1) {
    vlanID = ifName.substring(ifName.lastIndexOf(".")+1);
    return isValidVLAN(vlanID);
  } else {
    return (/^[0-9a-zA-Z.]+$/.test(ifName))
  }
  return false;
};

var isValidVLAN = function(vlanID) {
  return ((ginger.isInteger(vlanID)) && (vlanID != "-0") &&
    !((vlanID < 0 || vlanID > 4095) ? true : false))
};

var getVLANIDFromDeviceName  = function(deviceName) {
  var vlanID = ""
  if (deviceName.indexOf("vlan") == 0 && deviceName.length <= 15) {
    // vlan name convention vlan<VLANID> or vlan.<VLANID>
    if ((deviceName.length <= 9) && (deviceName.indexOf(".") != -1)) {
      vlanID = deviceName.split(".", 2).length == 2 ? deviceName.split(".", 2)[1] : null;
    } else if ((deviceName.length < 9) && (deviceName.indexOf(".") == -1)) {
        vlanID = deviceName.split("vlan", 2).length == 2 ? deviceName.split("vlan", 2)[1] : null;
    } else {
      return "";
    }

    if (ginger.isInteger(vlanID) && isValidVLAN(vlanID))
       return vlanID;

  } else if ((deviceName.length == 15) && (deviceName.indexOf(".") != -1)) {
      // In this case String can be 15 characters  or ifname.<VLANID>
      return deviceName.substring(deviceName.lastIndexOf(".")+1);
  }

  return "";
};

// function to populate advance tab
var populateAdvanceTab = function(interface) {
  if (interface == null) {
    mtuTextbox.val(1500);
  } else if ((interface != null) && ("MTU" in (interface.BASIC_INFO))) {
    mtuTextbox.val(interface.BASIC_INFO.MTU);
  }

  mtuTextbox.on('keyup click', function() {
    // Validate MTU value, It should be i> 9198
    var mtu = mtuTextbox.val();
    if(!((ginger.isInteger(mtu) && mtu <= 9198 && mtu > 0))){
      mtuTextbox.val('');
      $(this).addClass("invalid-field");
    }else{
      $(this).removeClass("invalid-field");
    }
  });

  // For now commenting the zone selection code
  // if ("ZONE" in (interface.BASIC_INFO)) {
  //   // $('#nw-vlan-firewall-select', interfaceSetting).val(result.BASIC_INFO.ZONE);
  //   //  zoneSelect.prop('disabled', false);
  //   zoneSelect.append($("<option></option>")
  //     .attr("value", interface.BASIC_INFO.ZONE)
  //     .text(interface.BASIC_INFO.ZONE));
  // }
};

// function to ipv4 Settings tab
var populateIpv4SettingsTab = function(interface) {
  if (interface != null) {
    if ("IPV4_INFO" in interface && "IPV4INIT" in (interface.IPV4_INFO)) {
      if (interface.IPV4_INFO.IPV4INIT == "yes" || interface.IPV4_INFO.IPV4INIT == "\"yes\"") {
        $('.ipv4-on-off').bootstrapSwitch('state', true);
      } else {
        $('.ipv4-on-off').bootstrapSwitch('state', false);
        ginger.disableIPSettings('ipv4');
      }
    } else {
      $('.ipv4-on-off').bootstrapSwitch('state', false);
      ginger.disableIPSettings('ipv4');
    }

    if (interface.IPV4_INFO.BOOTPROTO && ((interface.IPV4_INFO.BOOTPROTO).toLowerCase() == "none" || (interface.IPV4_INFO.BOOTPROTO).toLowerCase() == "static")) {
      ipv4MethodSelect.val(i18n['Manual']);
    } else if (interface.IPV4_INFO.BOOTPROTO && ((interface.IPV4_INFO.BOOTPROTO).toLowerCase() == "dhcp" || (interface.IPV4_INFO.BOOTPROTO).toLowerCase() == "bootp" || (interface.IPV4_INFO.BOOTPROTO).toLowerCase() == "autoip")) {
      ipv4MethodSelect.val(i18n['Automatic(DHCP)']);
      ginger.disableclass('form-nw-vlan-ipv4-manual');
    }

    if (interface.IPV4_INFO.DEFROUTE == "yes" || interface.IPV4_INFO.DEFROUTE == "\"yes\"")
      ipv4DefRouteCheckbox.prop('checked', true);

  } else {
    $('.ipv4-on-off').bootstrapSwitch('state', true);
    ipv4MethodSelect.val(i18n['Automatic(DHCP)']);
    ginger.disableclass('form-nw-vlan-ipv4-manual');
  }

  $('#nw-vlan-ipv4-init').on('switchChange.bootstrapSwitch', function(event, state) {
    if (state) {
      ginger.enableclass('form-nw-vlan-ipv4-method');
      changeState();
    } else {
      ginger.disableIPSettings('ipv4');
    }
  });

  ipv4MethodSelect.change(function() {
    changeState();
  });

  var changeState = function() {
    ginger.enableclass('form-nw-vlan-ipv4-manual-dhcp');
    if (ipv4MethodSelect.val() == i18n['Automatic(DHCP)']) {
      ginger.disableclass('form-nw-vlan-ipv4-manual');
    } else {
      ginger.enableclass('form-nw-vlan-ipv4-manual');
    }
  }

  createIpv4AddressGrid(interface);
  createIpv4DnsGrid(interface);
  createIpv4RouteGrid(interface);
}

// function to ipv4 grid
var createIpv4AddressGrid = function(interface) {
  var gridFields = [];
  var opts = [];
  opts['noResults'] = " ";

  opts['id'] = 'nw-vlan-ipv4-addresses';
  opts['gridId'] = "nw-vlan-ipv4-addresses-grid";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'IPADDR',
    "type": 'string',
    "width": "20%",
    "title": i18n['GINNWS0004M'],
    "identifier": true,
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv4-addresses"
  }, {
    "column-id": 'PREFIX',
    "type": 'string',
    "width": "30%",
    "title": i18n['GINNWS0007M'],
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv4-addresses"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    "width": "30%",
    "title": i18n['GINNWS0008M'],
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv4-addresses"
  }, {
    "column-id": "IPADDR",
    "type": 'string',
    "title": " ",
    "width": "20%",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var ipv4AddressesGrid = ginger.createBootgrid(opts);

  if (interface != null) {
    if ("IPV4_INFO" in interface && "IPV4Addresses" in (interface.IPV4_INFO)) {
      // $('.ipv4-on-off').bootstrapSwitch('state', true);
      if (interface.IPV4_INFO.IPV4Addresses) {
        ipv4VlanIPv4Method.val(i18n['Manual']);
        $('.ipv4-on-off').bootstrapSwitch('state', true);
      }

      ginger.loadBootgridData(opts['gridId'], interface.IPV4_INFO.IPV4Addresses);
    }
  } else {
    ipv4VlanIPv4Method.val(i18n['Automatic(DHCP)']);
  }

  ginger.createEditableBootgrid(ipv4AddressesGrid, opts, 'IPADDR');
  ipv4AddressAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'IPADDR',
      'width': '20%',
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'PREFIX',
      'width': '30%',
      'validation': function() {
        var isValid = ginger.validateMask($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'GATEWAY',
      'width': '30%',
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, opts['gridId'], commandSettings);
  });
};

var createIpv4DnsGrid = function(interface) {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'nw-vlan-ipv4-dns';
  opts['gridId'] = "nw-vlan-ipv4-dns-grid";
  opts['noResults'] = " ";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'DNS',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "80%",
    "title": i18n['GINNWS0006M'],
    "identifier": true,
    "formatter": "editable-nw-ipv4-dns"
  }, {
    "column-id": "DNS",
    "type": 'string',
    "title": "",
    "width": "20%",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var dnsGrid = ginger.createBootgrid(opts);

  if (interface != null) {
    if ("IPV4_INFO" in interface && "DNSAddresses" in (interface.IPV4_INFO)) {
      var DNSAddresses = interface.IPV4_INFO.DNSAddresses
      for (var i = 0; i < DNSAddresses.length; i++) {
        DNSAddresses[i] = {
          "DNS": DNSAddresses[i]
        }
      }
      ginger.loadBootgridData(opts['gridId'], DNSAddresses);
    }
  } else {
    // NEW VLAN DNS Settings
    ipv4VlanIPv4Method.val(i18n['Automatic(DHCP)']);
  }

  ginger.createEditableBootgrid(dnsGrid, opts, 'DNS');
  ipv4DnsAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'DNS',
      'width': '80%',
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, opts['gridId'], commandSettings);
  });

};


var createIpv4RouteGrid = function(interface) {
  var gridFields = [];
  var opts = [];
  opts['noResults'] = " ";

  opts['id'] = 'nw-vlan-ipv4-routes';
  opts['gridId'] = "nw-vlan-ipv4-routes-grid";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'ADDRESS',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0004M'],
    "identifier": true,
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": 'NETMASK',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "title": i18n['GINNWS0007M'],
    "width": "20%",
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0008M'],
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": 'METRIC',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0009M'],
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": "ADDRESS",
    "type": 'string',
    "title": "",
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var routesGrid = ginger.createBootgrid(opts);

  if (interface != null) {
    if ("IPV4_INFO" in interface && "ROUTES" in (interface.IPV4_INFO)) {
      ginger.loadBootgridData(opts['gridId'], interface.IPV4_INFO.ROUTES);
    }
  } else {
    ipv4VlanIPv4Method.val(i18n['Automatic(DHCP)']);
  }

  ginger.createEditableBootgrid(routesGrid, opts, 'ADDRESS');
  ipv4RoutesAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'ADDRESS',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'NETMASK',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.validateMask($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'GATEWAY',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'METRIC',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = /^[0-9]+$/.test($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, opts['gridId'], commandSettings);
  });
};


// function to ipv4 Settings tab
var populateIpv6SettingsTab = function(interface) {
  createIpv6AddressGrid(interface);
  createIpv6DnsGrid(interface);
  createIpv6RouteGrid(interface);

  if (interface != null) {
    if ("IPV6_INFO" in interface && "IPV6INIT" in (interface.IPV6_INFO)) {
      if (interface.IPV6_INFO.IPV6INIT == "yes" || interface.IPV6_INFO.IPV6INIT == "\"yes\"") {
        $('.ipv6-on-off').bootstrapSwitch('state', true);
      } else {
        $('.ipv6-on-off').bootstrapSwitch('state', false);
        ginger.disableIPSettings('ipv6');
      }

      if (interface.IPV6_INFO.IPV6_AUTOCONF && ((interface.IPV6_INFO.IPV6_AUTOCONF).toLowerCase() == "yes")) {
        ipv6MethodSelect.val(i18n['Automatic']);
        ginger.disableclass('form-nw-vlan-ipv6-manual');
      } else if (interface.IPV6_INFO.IPV6_AUTOCONF && ((interface.IPV6_INFO.IPV6_AUTOCONF).toLowerCase() == "no")) {
        ipv6MethodSelect.val(i18n['Manual']);
        ginger.enableclass('form-nw-vlan-ipv6-manual');
      }
    } else {
      $('.ipv6-on-off').bootstrapSwitch('state', false);
      ginger.disableIPSettings('ipv6');
    }

    if (interface.IPV6_INFO.IPV6_DEFAULTGW) {
      ipv6GatewayTextbox.val(interface.IPV6_INFO.IPV6_DEFAULTGW);
    }

    if (interface.IPV6_INFO.IPV6_DEFROUTE == "yes" || interface.IPV6_INFO.IPV6_DEFROUTE == "\"yes\"")
      ipv6DefRouteCheckbox.prop('checked', true);
  } else {
    $('.ipv6-on-off').bootstrapSwitch('state', true);
    ipv6MethodSelect.val(i18n['Automatic']);
    ginger.disableclass('form-nw-vlan-ipv6-manual');
  }


  $('#nw-vlan-ipv6-init').on('switchChange.bootstrapSwitch', function(event, state) {
    if (state) {
      ginger.enableclass('form-nw-vlan-ipv6-method');
      changeState();
    } else {
      ginger.disableIPSettings('ipv6');
    }
  });

  ipv6MethodSelect.change(function() {
    changeState();
  });


  var changeState = function() {
    ginger.enableclass('form-nw-vlan-ipv6-manual-dhcp');
    if (ipv6MethodSelect.val() == i18n['Automatic']) {
      ginger.disableclass('form-nw-vlan-ipv6-manual');
    } else {
      ginger.enableclass('form-nw-vlan-ipv6-manual');
    }
  }

  ipv6GatewayTextbox.on('keyup', function() {
    var ipv6_defaultgw = ipv6GatewayTextbox.val();
    $(this).toggleClass("invalid-field", !(ginger.isValidIPv6(ipv6_defaultgw)));
  });
}

ginger.disableIPSettings = function(settings) {
  if (settings == 'ipv4') {
    ginger.disableclass('form-nw-vlan-ipv4-manual');
    ginger.disableclass('form-nw-vlan-ipv4-manual-dhcp');
    ginger.disableclass('form-nw-vlan-ipv4-method');
  } else if (settings == 'ipv6') {
    ginger.disableclass('form-nw-vlan-ipv6-manual');
    ginger.disableclass('form-nw-vlan-ipv6-manual-dhcp');
    ginger.disableclass('form-nw-vlan-ipv6-method');
  }
}

// function to ipv6 grid
var createIpv6AddressGrid = function(interface) {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'nw-vlan-ipv6-addresses';
  opts['gridId'] = "nw-vlan-ipv6-addresses-grid";
  opts['noResults'] = " ";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
      "column-id": 'IPADDR',
      "type": 'string',
      "width": "20%",
      "title": i18n['GINNWS0004M'],
      "identifier": true,
      "header-class": "text-center",
      "data-class": "center",
      "formatter": "editable-nw-ipv6-addresses"
    }, {
      "column-id": 'PREFIX',
      "type": 'string',
      "width": "30%",
      "title": i18n['GINNWS0005M'],
      "header-class": "text-center",
      "data-class": "center",
      "formatter": "editable-nw-ipv6-addresses"
    },
    // {
    //   "column-id": 'GATEWAY',
    //   "type": 'string',
    //   "width": "30%",
    //   "title": "Gateway",
    //   "header-class":"text-center",
    //   "data-class":"center",
    //   "formatter": "editable-nw-ipv6-addresses"
    // },
    {
      "column-id": "IPADDR",
      "type": 'string',
      "title": " ",
      "width": "20%",
      "header-class": "text-center",
      "data-class": "center",
      "formatter": "row-edit-delete"
    }
  ];

  opts['gridFields'] = JSON.stringify(gridFields);
  var ipv6AddressesGrid = ginger.createBootgrid(opts);
  if (interface != null) {
    if ("IPV6_INFO" in interface && "IPV6Addresses" in (interface.IPV6_INFO)) {
      if (interface.IPV6_INFO.IPV6Addresses) {
        ipv4VlanIPv4Method.val(i18n['Manual']);
        $('.ipv6-on-off').bootstrapSwitch('state', true);
      }

      ginger.loadBootgridData(opts['gridId'], interface.IPV6_INFO.IPV6Addresses);
    }
  } else {
    // New VLAN interface
    ipv6MethodSelect.val(i18n['Automatic']);
  }

  ginger.createEditableBootgrid(ipv6AddressesGrid, opts, 'IPADDR');
  ipv6AddressAddButton.on('click', function() {
    var columnSettings = [{
        'id': 'IPADDR',
        'width': '20%',
        "td-class": "text-center",
        'validation': function() {
          var isValid = ginger.isValidIPv6($(this).val());
          ginger.markInputInvalid($(this), isValid);
        }
      }, {
        'id': 'PREFIX',
        'width': '30%',
        "td-class": "text-center",
        'validation': function() {
          //  var isValid = ginger.isValidIPv6Prefix($(this).val());
          ginger.markInputInvalid($(this), (ginger.isValidIPv6Prefix($(this).val())));
        }
      }]
      // {
      //   'id':'GATEWAY',
      //   'width':'30%',
      //   "td-class": "text-center",
      //   'validation':function() {
      //      var isValid = ginger.isValidIPv6($(this).val());
      //         ginger.markInputInvalid($(this),isValid);
      //    }
      // }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, opts['gridId'], commandSettings);
  });
};

var createIpv6DnsGrid = function(interface) {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'nw-vlan-ipv6-dns';
  opts['gridId'] = "nw-vlan-ipv6-dns-grid";
  opts['noResults'] = " ";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'DNS',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "80%",
    "title": i18n['GINNWS0006M'],
    "identifier": true,
    "formatter": "editable-nw-ipv6-dns"
  }, {
    "column-id": "DNS",
    "type": 'string',
    "title": "",
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var dnsGrid = ginger.createBootgrid(opts);
  if (interface != null) {
    if ("IPV6_INFO" in interface && "DNSAddresses" in (interface.IPV6_INFO)) {
      var DNSAddresses = interface.IPV6_INFO.DNSAddresses
        // var dns = {}
      for (var i = 0; i < DNSAddresses.length; i++) {
        DNSAddresses[i] = {
          "DNS": DNSAddresses[i]
        };
      }
      ginger.loadBootgridData(opts['gridId'], DNSAddresses);
    }
  } else {
    ipv6MethodSelect.val(i18n['Automatic']);
  }

  ginger.createEditableBootgrid(dnsGrid, opts, 'DNS');
  ipv6DnsAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'DNS',
      'width': '80%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, opts['gridId'], commandSettings);
  });
};


var createIpv6RouteGrid = function(interface) {
  var gridFields = [];
  var opts = [];
  opts['noResults'] = " ";


  opts['id'] = 'nw-vlan-ipv6-routes';
  opts['gridId'] = "nw-vlan-ipv6-routes-grid";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'ADDRESS',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0004M'],
    "identifier": true,
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": 'NETMASK',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0005M'],
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0008M'],
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": 'METRIC',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "title": i18n['GINNWS0009M'],
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": "ADDRESS",
    "type": 'string',
    "title": "",
    "header-class": "text-center",
    "data-class": "center",
    "width": "20%",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var routesGrid = ginger.createBootgrid(opts);
  if (interface != null) {
    if ("IPV6_INFO" in interface && "ROUTES" in (interface.IPV6_INFO)) {
      ginger.loadBootgridData(opts['gridId'], interface.IPV6_INFO.ROUTES);
    }
  } else {
    ipv6MethodSelect.val(i18n['Automatic']);
  }

  ginger.createEditableBootgrid(routesGrid, opts, 'ADDRESS');
  ipv6RoutesAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'ADDRESS',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'NETMASK',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        //  var isValid = ginger.isValidIPv6Prefix($(this).val());
        ginger.markInputInvalid($(this), (ginger.isValidIPv6Prefix($(this).val())));
      }
    }, {
      'id': 'GATEWAY',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'METRIC',
      'width': '20%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = /^[0-9]+$/.test($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }]
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, opts['gridId'], commandSettings);
  });

};
