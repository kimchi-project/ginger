ginger.initNwInterfaceBond = function() {

  nwApplyButton = $('#nw-interface-bond-button-apply');
  nwGeneralForm = $('#form-nw-bond-general');
  nwIpv4Form = $('#form-nw-bond-ipv4');
  nwIpv6Form = $('#form-nw-bond-ipv6');
  nwAdvanceForm = $('#form-nw-bond-advance');

  interfaceBondTabs = $('#nw-bond-tabs');
  nwTitle = $('#nw-bond-title');

  nwBondDeviceTextbox = $('#nw-bond-device-textbox', interfaceBondTabs);
  bondMode = $('#nw-bond-general-mode', interfaceBondTabs);
  bondMemberAdd = $('#nw-bond-member-add', interfaceBondTabs);
  onBootCheckbox = $('#nw-bond-connect-auto', interfaceBondTabs);

  ipv4AddressAddButton = $('#nw-bond-ipv4-address-add', interfaceBondTabs);
  ipv4RoutesAddButton = $('#nw-bond-ipv4-routes-add', interfaceBondTabs);
  ipv4DnsAddButton = $('#nw-bond-ipv4-dns-add', interfaceBondTabs);
  ipv4BondIPv4Method = $('#nw-bond-ipv4-method', interfaceBondTabs);

  ipv6AddressAddButton = $('#nw-bond-ipv6-address-add', interfaceBondTabs);
  ipv6RoutesAddButton = $('#nw-bond-ipv6-routes-add', interfaceBondTabs);
  ipv6DnsAddButton = $('#nw-bond-ipv6-dns-add', interfaceBondTabs);
  ipv6BondMethod = $('#nw-bond-ipv6-method', interfaceBondTabs);

  zoneSelect = $('#nw-bond-firewall-select', interfaceBondTabs);
  linkMonitoring = $('#nw-bond-link-monitoring', interfaceBondTabs);
  bondMonitoringInterval = $('#nw-bond-monitoring-interval', interfaceBondTabs);
  linkUpDelay = $('#nw-bond-link-up-delay', interfaceBondTabs);
  linkDownDelay = $('#nw-bond-link-down-delay', interfaceBondTabs);

  selectedInterface = ginger.selectedInterface;

  if (selectedInterface == null) {
    // New BOND interface creation
    populateGeneralTab(null); //populate general tab
    populateAdvanceTab(null); //populate advance tab
    populateIpv4SettingsTab(null); //populate ipv4 setting tab
    populateIpv6SettingsTab(null); //populate ipv6 setting tab
  } else if (selectedInterface != null) {
    // Get the interface setting details
    ginger.retrieveCfgInterface(selectedInterface, function suc(result) {
      populateGeneralTab(result); //populate general tab
      populateAdvanceTab(result); //populate advance tab
      populateIpv4SettingsTab(result); //populate ipv4 setting tab
      populateIpv6SettingsTab(result); //populate ipv6 setting tab
    });
  }

  applyOnClick();
};

var applyOnClick = function() {

  // on Apply button click
  nwApplyButton.on('click', function() {
    var data = {};
    var opts = {};
    nwApplyButton.prop('disabled', true);
    var interfaceDevice = nwBondDeviceTextbox.val();

    var getBasicInfoData = function() {
      var basic_info = {};
      var bond_info = {};
      var bond_opts = {};

      basic_info['TYPE'] = "Bond";
      basic_info['DEVICE'] = interfaceDevice; // Keep till Jaya fix
      if (onBootCheckbox.is(":checked")) {
        basic_info["ONBOOT"] = "yes";
      } else {
        basic_info["ONBOOT"] = "no";
      }

      //Get bond member grid data
      opts['id'] = 'nw-general-bond-member';
      opts['gridId'] = "nw-bond-member-grid";
      bondMembers = ginger.getCurrentRows(opts);

      if (bondMembers.length > 0) {
        bondMember = []
        for (var i = 0; i < bondMembers.length; i++) {
          bondMemberValue = bondMembers[i].member;
          bondMember.push(bondMemberValue);
        }
        bond_info['SLAVES'] = bondMember;
      }

      bond_info['BONDING_MASTER'] = 'yes';

      bond_opts['mode'] = bondMode.val();
      bond_opts['miimon'] = bondMonitoringInterval.val();
      bond_opts['updelay'] = linkUpDelay.val();
      bond_opts['downdelay'] = linkDownDelay.val();

      bond_info['BONDING_OPTS'] = bond_opts;
      basic_info['BONDINFO'] = bond_info;
      data['BASIC_INFO'] = basic_info;

      //alert("Basic Information : " + JSON.stringify(data));
    }
    getBasicInfoData();

    var getIpv4InfoData = function() {
      var ipv4_info = {}; //All ipv4 info from ipv4 tab

      if ($('#nw-bond-ipv4-init').bootstrapSwitch('state')) {
        ipv4_info['IPV4INIT'] = 'yes';
        ipv4_info['BOOTPROTO'] = 'none';


        //Get IP address grid data
        opts['id'] = 'nw-bond-ipv4-addresses';
        opts['gridId'] = "nw-bond-ipv4-addresses-grid";
        ipv4Addresses = ginger.getCurrentRows(opts);
        // alert("IPv4 Address : " + ipv4Addresses);

        //Get DNS grid data
        opts['id'] = 'nw-bond-ipv4-dns';
        opts['gridId'] = "nw-bond-ipv4-dns-grid";
        ipv4Dns = ginger.getCurrentRows(opts);

        //Get Routes grid data
        opts['id'] = 'nw-bond-ipv4-routes';
        opts['gridId'] = "nw-bond-ipv4-routes-grid";
        ipv4Routes = ginger.getCurrentRows(opts);

        if (ipv4Addresses.length > 0) {
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
      } else {
        ipv4_info['IPV4INIT'] = 'no';
      }

      data['IPV4_INFO'] = ipv4_info
    }
    getIpv4InfoData();

    var getIpv6InfoData = function() {
      var ipv6_info = {}; //All ipv6 info from ipv6 tab

      if ($('option:selected', ipv6BondMethod).text() == 'Manual') {
        ipv6_info['IPV6_AUTOCONF'] = 'no';
      } else {
        ipv6_info['IPV6_AUTOCONF'] = 'yes';
      }

      if ($('#nw-bond-ipv6-init').bootstrapSwitch('state')) {
        ipv6_info['IPV6INIT'] = 'yes';
        // ipv6_info['BOOTPROTO'] = 'none';
        var opts = {};

        //Get IP address grid data
        opts['id'] = 'nw-bond-ipv6-addresses';
        opts['gridId'] = "nw-bond-ipv6-addresses-grid";
        ipv6Addresses = ginger.getCurrentRows(opts);

        //Get DNS grid data
        opts['id'] = 'nw-bond-ipv6-dns';
        opts['gridId'] = "nw-bond-ipv6-dns-grid";
        ipv6Dns = ginger.getCurrentRows(opts);

        //Get Routes grid data
        opts['id'] = 'nw-bond-ipv6-routes';
        opts['gridId'] = "nw-bond-ipv6-routes-grid";
        ipv6Routes = ginger.getCurrentRows(opts);

        if (ipv6Addresses.length > 0) {
          ipv6_info['IPV6Addresses'] = ipv6Addresses;
        }

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
      } else {
        ipv6_info['IPV6INIT'] = 'no';
      }

      data['IPV6_INFO'] = ipv6_info
    }
    getIpv6InfoData(); //Commented for now as getting some issue from backend
    //alert(JSON.stringify(data));
    if (ginger.selectedInterface == null) {
      ginger.createCfgInterface(data, function(result) {
        // kimchi.doListTemplates();
        wok.message.success(i18n['GINNET0020M'] + result.BASIC_INFO.DEVICE, '#alert-nw-bond-modal-container');
        $(nwApplyButton).prop('disabled', false);
        // wok.window.close();
      }, function(err) {
        //alert(err.responseJSON.reason);
        wok.message.error(err.responseJSON.reason, '#alert-nw-bond-modal-container', true);
        $(nwApplyButton).prop('disabled', false);
      });
    } else {
      ginger.updateCfgInterface(interfaceDevice, data, function(result) {
        // kimchi.doListTemplates();
        wok.message.success(i18n['GINNET0020M'] + result, '#alert-nw-bond-modal-container');
        $(nwApplyButton).prop('disabled', false);
        // wok.window.close();
      }, function(err) {
        //alert(err.responseJSON.reason);
        wok.message.error(err.responseJSON.reason, '#alert-nw-bond-modal-container', true);
        $(nwApplyButton).prop('disabled', false);
      });
    }
  });
}

// function to populate general tab
var populateGeneralTab = function(interface) {
  ginger.listCfgInterface(function suc(result) {
    ginger.interfaceList = result;
    var memberOptions = [];
    var interfaceList = ginger.interfaceList;

    for (var i = 0; i < interfaceList.length; i++) {
      var interfaceInfo = interfaceList[i];
      var interfaceDetails = {};

      if ("BASIC_INFO" in interfaceInfo && "DEVICE" in (interfaceInfo.BASIC_INFO)) {
        interfaceDetails["value"] = interfaceList[i].BASIC_INFO.DEVICE;
        interfaceDetails["text"] = interfaceList[i].BASIC_INFO.DEVICE;
        memberOptions.push(interfaceDetails);
      }
    }
    ginger.bondMemberOption = memberOptions;
  });

  var bondModeOptions = ['balance-rr', 'active-backup', 'balance-xor', 'broadcast', '802.3ad', 'balance-tlb', 'balance-alb'];
  for (var i = 0; i < bondModeOptions.length; i++) {
    var bondOptionValue = bondModeOptions[i];
    bondMode.append($("<option></option>")
      .attr("value", (bondOptionValue).replace(/"/g, ""))
      .text((bondOptionValue).replace(/"/g, "")));

  }

  createBondMembersGrid(interface);
  if (interface == null) {
    nwTitle.append("BOND");
    nwBondDeviceTextbox.val('');
  } else {
    nwTitle.append(interface.BASIC_INFO.NAME);
    //  nwNameTextbox.val(interface.BASIC_INFO.Device);

    if (interface.BASIC_INFO.DEVICE) {
      nwBondDeviceTextbox.val(interface.BASIC_INFO.DEVICE);
      nwBondDeviceTextbox.prop("disabled", true);
    }
    bondMode.val(interface.BASIC_INFO.BONDINFO.BONDING_OPTS.mode);

    if (interface.BASIC_INFO.ONBOOT == "\"yes\"" || interface.BASIC_INFO.ONBOOT == "yes") {
      onBootCheckbox.prop('checked', true);
    }
  }
};
var createBondMembersGrid = function(interface) {
    var gridFields = [];
    var opts = [];
    opts['noResults'] = " ";

    opts['id'] = 'nw-general-bond-member';
    opts['gridId'] = "nw-bond-member-grid";
    opts['selection'] = false;
    opts['navigation'] = 0;

    gridFields = [{
      "column-id": 'member',
      "type": 'string',
      "width": "70%",
      "title": " ",
      "identifier": true,
      "header-class": "text-center",
      "data-class": "center",
      "formatter": "editable-bond-member"
    }, {
      "column-id": "member",
      "type": 'string',
      "title": " ",
      "width": "20%",
      "header-class": "text-center",
      "data-class": "center",
      "formatter": "row-edit-delete"
    }];

    opts['gridFields'] = JSON.stringify(gridFields);
    var bondMemberGrid = ginger.createBootgrid(opts);

    if (interface != null) {
      if ("BONDINFO" in interface.BASIC_INFO && "SLAVES" in (interface.BASIC_INFO.BONDINFO)) {
        var bondMemberList = interface.BASIC_INFO.BONDINFO.SLAVES;

        for (var i = 0; i < bondMemberList.length; i++) {
          bondMemberList[i] = {
              "member": bondMemberList[i]
            } // convert from List to Map
        }
        ginger.loadBootgridData(opts['gridId'], bondMemberList);
        //ginger.loadBootgridData(opts['gridId'], interface.BASIC_INFO.BONDINFO.SLAVES);
      }
    }

    bondMemberGrid.bootgrid().on("loaded.rs.jquery.bootgrid", function(e) {
      $('#nw-bond-member-grid span.xedit').editable({
        type: 'select',
        showbuttons: false,
        send: 'never',
        toggle: 'manual',
        savenochange: true,
        mode: 'inline',
        source: ginger.bondMemberOption
      });
      bondMemberGrid.find(".command-edit").on("click", function(e) {
        e.stopPropagation();
        $('span.xedit', $(this).closest('tr')).editable('show');
        $(this).closest('td').find(".command-save").removeClass('hidden');
        $(this).addClass("hidden");
      }).end().find(".command-delete").on("click", function(e) {
        var data = $(this).data('row-id');
        var gridRows = ginger.getCurrentRows({
          "gridId": opts['gridId']
        });

        $.each(gridRows, function(i, row) {
          if (row['member'] == data) {
            $(this).closest('tr').remove();
            gridRows.splice(gridRows.indexOf(row), 1);
            ginger.clearBootgridData(opts['gridId']);
            ginger.appendBootgridData(opts['gridId'], gridRows);
            return false;
          }
        });
      }).end().find(".command-save").on("click", function(e) {
        var gridRows = ginger.getCurrentRows({
          "gridId": opts['gridId']
        });
        var editableField = $('span.xedit', $(this).closest('tr'));
        var selectedValue = editableField.text();

        var columnname = editableField.attr("data-column-name");
        var datarowid = editableField.attr("data-row-id");

        $.each(gridRows, function(i, row) {
          if (row['member'] == datarowid) {
            row['member'] = selectedValue;
          }
          gridRows.push.apply(gridRows, row);
        });
        ginger.clearBootgridData(opts['gridId']);
        ginger.appendBootgridData(opts['gridId'], gridRows);
      });
    });

    bondMemberAdd.on('click', function() {
      $('<tr></tr>').appendTo($('#nw-bond-member-grid tbody'));

      var columnHtml = ['<td style="width:80%"',
        ' class="text-center"',
        '>',
        '<select id="slave" class="form-control"><select>',
        '</td>'
      ].join('');
      var selectField = $(columnHtml).appendTo($('tr:last', '#nw-bond-member-grid'));
      var interfaceList = ginger.interfaceList;

      for (var i = 0; i < interfaceList.length; i++) {
        var interfacedetails = interfaceList[i];
        if ("BASIC_INFO" in interfacedetails && "DEVICE" in (interfacedetails.BASIC_INFO)) {
          $('select', selectField).append($("<option></option>")
            .attr("value", (interfaceList[i].BASIC_INFO.DEVICE).replace(/"/g, ""))
            .text((interfaceList[i].BASIC_INFO.DEVICE).replace(/"/g, "")));
        }
      }
      $('<td><span class=\"fa fa-floppy-o new-row-save\"></span><span class=\"fa fa-trash-o new-row-delete\"></span></td>').appendTo($('tr:last', '#nw-bond-member-grid'));
      $('.new-row-save', '#nw-bond-member-grid').on('click', function(e) {
        var rowdata = {};
        var fieldValue = $('#slave option:selected', $(this).closest('tr')).val();
        rowdata['member'] = fieldValue;

        var rowdetails = [];
        rowdetails.push(rowdata);
        ginger.appendBootgridData('nw-bond-member-grid', rowdetails);
      });

      $('.new-row-delete', '#nw-bond-member-grid').on("click", function(e) {
        $('tr:last', $(this).closest('tbody')).remove();
      });
    });
  }
  // function to populate advance tab
var populateAdvanceTab = function(interface) {
  if (interface == null) {
    linkMonitoring.append($("<option></option>")
      .attr("value", "MI(Recommended)")
      .text("MI(Recommended)"));

    zoneSelect.append($("<option></option>")
      .attr("value", "Default")
      .text("Default"));
  } else {
    if ("BONDINFO" in (interface.BASIC_INFO)) {
      if ("miimon" in (interface.BASIC_INFO.BONDINFO.BONDING_OPTS)) {
        bondMonitoringInterval.val(interface.BASIC_INFO.BONDINFO.BONDING_OPTS.miimon)
      }

      if ("updelay" in (interface.BASIC_INFO.BONDINFO.BONDING_OPTS)) {
        linkUpDelay.val(interface.BASIC_INFO.BONDINFO.BONDING_OPTS.updelay)
      }

      if ("downdelay" in (interface.BASIC_INFO.BONDINFO.BONDING_OPTS)) {
        linkDownDelay.val(interface.BASIC_INFO.BONDINFO.BONDING_OPTS.downdelay)
      }
    }
    if ("ZONE" in (interface.BASIC_INFO)) {
      zoneSelect.append($("<option></option>")
        .attr("value", interface.BASIC_INFO.ZONE)
        .text(interface.BASIC_INFO.ZONE));
    }
  }

  bondMonitoringInterval.on('keyup', validateTimeField(bondMonitoringInterval));
  linkUpDelay.on('keyup', validateTimeField(linkUpDelay));
  linkDownDelay.on('keyup', validateTimeField(linkDownDelay));
};
// function to ipv4 Settings tab
var populateIpv4SettingsTab = function(interface) {
  if (interface != null) {
    if ("IPV4_INFO" in interface && "IPV4INIT" in (interface.IPV4_INFO)) {
      if (interface.IPV4_INFO.IPV4INIT == "yes" || interface.IPV4_INFO.IPV4INIT == "\"yes\"")
        $('#nw-bond-ipv4-init').bootstrapSwitch('state', true);
      ginger.enableclass('form-nw-bond-ipv4-method');
    } else {
      $('#nw-bond-ipv4-init').bootstrapSwitch('state', false);
      ginger.disableclass('form-nw-bond-ipv4-method');
    }

    if (interface.IPV4_INFO.BOOTPROTO && (interface.IPV4_INFO.BOOTPROTO == "None" || interface.IPV4_INFO.BOOTPROTO == "none")) {
      ipv4BondIPv4Method.val("Manual");
      ginger.enableclass('form-nw-bond-ipv4-manual');
    } else if (interface.IPV4_INFO.BOOTPROTO && (interface.IPV4_INFO.BOOTPROTO == "dhcp")) {
      ipv4BondIPv4Method.val("Automatic(DHCP)");
      ginger.disableclass('form-nw-bond-ipv4-manual');
    }
  } else {
    $('#nw-bond-ipv4-init').bootstrapSwitch('state', true);
    ginger.disableclass('form-nw-bond-ipv4-manual');
  }


  $('#nw-bond-ipv4-init').on('switchChange.bootstrapSwitch', function(event, state) {
    if (state) {
      ginger.enableclass('form-nw-bond-ipv4-method');
      changeState();
    } else {
      ginger.disableclass('form-nw-bond-ipv4-manual');
      ginger.disableclass('form-nw-bond-ipv4-method');
    }
  });



  ipv4BondIPv4Method.change(function() {
    changeState();
  });

  var changeState = function() {
    if (ipv4BondIPv4Method.val() == "Automatic(DHCP)") {
      ginger.disableclass('form-nw-bond-ipv4-manual');
    } else {
      ginger.enableclass('form-nw-bond-ipv4-manual');
    }
  }

  createIpv4AddressGrid(interface);
  createIpv4RouteGrid(interface);
  createIpv4DnsGrid(interface);

}

// function to ipv4 grid
var createIpv4AddressGrid = function(interface) {
  var gridFields = [];
  var opts = [];
  opts['noResults'] = " ";

  opts['id'] = 'nw-bond-ipv4-addresses';
  opts['gridId'] = "nw-bond-ipv4-addresses-grid";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'IPADDR',
    "type": 'string',
    "width": "20%",
    "title": "Address",
    "identifier": true,
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv4-addresses"
  }, {
    "column-id": 'PREFIX',
    "type": 'string',
    "width": "30%",
    "title": "Mask",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv4-addresses"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    "width": "30%",
    "title": "Gateway",
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
      if (interface.IPV4_INFO.IPV4Addresses) {
        ipv4BondIPv4Method.val(i18n['Manual']);
        $('#nw-bond-ipv4-init').bootstrapSwitch('state', true);
      }
      ginger.loadBootgridData(opts['gridId'], interface.IPV4_INFO.IPV4Addresses);
    }
  } else {
    ipv4BondIPv4Method.val(i18n['Automatic(DHCP)']);
  }
  ginger.createEditableBootgrid(ipv4AddressesGrid, opts, 'IPADDR');

  ipv4AddressAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'IPADDR',
      'width': '30%',
      'td-class': 'text-center',
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
    }];
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    };
    ginger.addNewRecord(columnSettings, 'nw-bond-ipv4-addresses-grid', commandSettings);
  });
};

var createIpv4DnsGrid = function(interface) {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'nw-bond-ipv4-dns';
  opts['gridId'] = "nw-bond-ipv4-dns-grid";
  opts['noResults'] = " ";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'DNS',
    "type": 'string',
    "width": "80%",
    "header-class": "col-xs-12 text-center",
    "title": "DNS",
    "identifier": true,
    "formatter": "editable-nw-ipv4-dns"
  }, {
    "column-id": "DNS",
    "type": 'string',
    "title": "",
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
          } // convert from List to Map
      }
      ginger.loadBootgridData(opts['gridId'], DNSAddresses);
    }
  }

  ginger.createEditableBootgrid(dnsGrid, opts, 'DNS');

  // ipv4DnsAddButton.on('click', function() {
  //
  //   columnSettings = [{
  //     'id': 'DNS',
  //     'width': '80%',
  //     'td-class': 'text-center',
  //     'validation': function() {
  //       var isValid = ginger.validateIp($(this).val());
  //       markInputInvalid($(this), isValid);
  //     }
  //   }]
  //   commandSettings = {
  //     "width": "20%",
  //     "td-class": "text-center"
  //   }
  //   addNewRecord(columnSettings, 'nw-bond-ipv4-dns-grid', commandSettings);
  // });

  ipv4DnsAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'DNS',
      'width': '80%',
      "td-class": "text-center",
      'validation': function() {
        var isValid = ginger.isValidIp($(this).val());
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

  opts['id'] = 'nw-bond-ipv4-routes';
  opts['gridId'] = "nw-bond-ipv4-routes-grid";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'ADDRESS',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Address",
    "identifier": true,
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": 'NETMASK',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Mask",
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Gateway",
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": 'METRIC',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Metric",
    "formatter": "editable-nw-ipv4-routes"
  }, {
    "column-id": "ADDRESS",
    "type": 'string',
    "title": "",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var routeGrid = ginger.createBootgrid(opts);

  if (interface != null) {
    if ("IPV4_INFO" in interface && "ROUTES" in (interface.IPV4_INFO)) {
      ginger.loadBootgridData(opts['gridId'], interface.IPV4_INFO.ROUTES);
    }
  }

  ginger.createEditableBootgrid(routeGrid, opts, 'ADDRESS');

  ipv4RoutesAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'ADDRESS',
      'width': '20%',
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'NETMASK',
      'width': '20%',
      'validation': function() {
        var isValid = ginger.validateMask($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'GATEWAY',
      'width': '20%',
      'validation': function() {
        var isValid = ginger.validateIp($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'METRIC',
      'width': '20%',
      'validation': function() {
        var isValid = /^[0-9]+$/.test($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }];
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    }
    ginger.addNewRecord(columnSettings, 'nw-bond-ipv4-routes-grid', commandSettings);
  });
};


// function to ipv4 Settings tab
var populateIpv6SettingsTab = function(interface) {
  createIpv6AddressGrid(interface);
  createIpv6RouteGrid(interface);
  createIpv6DnsGrid(interface);

  if (interface != null) {
    if ("IPV6_INFO" in interface && "IPV6INIT" in (interface.IPV6_INFO)) {
      if (interface.IPV6_INFO.IPV6INIT == "yes" || interface.IPV6_INFO.IPV6INIT == "\"yes\"")
        $('#nw-bond-ipv6-init').bootstrapSwitch('state', true);
      ginger.enableclass('form-nw-bond-ipv6-manual');
      ginger.enableclass('form-nw-bond-ipv6-method');
    } else {
      $('#nw-bond-ipv6-init').bootstrapSwitch('state', false);
      ginger.disableclass('form-nw-bond-ipv6-manual');
      ginger.disableclass('form-nw-bond-ipv6-method');
    }

    if (interface.IPV6_INFO.IPV6_AUTOCONF && (interface.IPV6_INFO.IPV6_AUTOCONF == "yes" || interface.IPV6_INFO.IPV6_AUTOCONF == "Yes")) {
      ipv6BondMethod.val("Automatic");
      ginger.disableclass('form-nw-bond-ipv6-manual');
    } else if (interface.IPV6_INFO.IPV6_AUTOCONF && (interface.IPV6_INFO.IPV6_AUTOCONF == "no" || interface.IPV6_INFO.IPV6_AUTOCONF == "No")) {
      ipv6BondMethod.val("Manual");
      ginger.enableclass('form-nw-bond-ipv6-manual');
    }
  } else {
    $('#nw-bond-ipv6-init').bootstrapSwitch('state', true);
    ginger.disableclass('form-nw-bond-ipv6-manual');
    //ginger.disableclass('form-nw-bond-ipv6-method');
  }


  $('#nw-bond-ipv6-init').on('switchChange.bootstrapSwitch', function(event, state) {
    if (state) {
      ginger.enableclass('form-nw-bond-ipv6-method');
      changeState();
    } else {
      ginger.disableclass('form-nw-bond-ipv6-manual');
      ginger.disableclass('form-nw-bond-ipv6-method');
    }
  });



  ipv6BondMethod.change(function() {
    changeState();
  });

  var changeState = function() {
    if (ipv6BondMethod.val() == "Automatic(DHCP)") {
      ginger.disableclass('form-nw-bond-ipv6-manual');
    } else {
      ginger.enableclass('form-nw-bond-ipv6-manual');
    }
  }
}

// function to ipv4 grid
var createIpv6AddressGrid = function(interface) {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'nw-bond-ipv6-addresses';
  opts['gridId'] = "nw-bond-ipv6-addresses-grid";
  opts['noResults'] = " ";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'IPADDR',
    "type": 'string',
    "width": "30%",
    "title": "Address",
    "identifier": true,
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv6-addresses"
  }, {
    "column-id": 'PREFIX',
    "type": 'string',
    "width": "30%",
    "title": "Mask",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv6-addresses"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    "width": "30%",
    "title": "Default Gateway",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "editable-nw-ipv4-addresses"
  }, {
    "column-id": "IPADDR",
    "type": 'string',
    "title": " ",
    "width": "10%",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var ipv6AddressesGrid = ginger.createBootgrid(opts);

  if (interface != null) {
    if ("IPV6_INFO" in interface && "IPV6Addresses" in (interface.IPV6_INFO)) {
      ginger.loadBootgridData(opts['gridId'], interface.IPV6_INFO.IPV6Addresses);

    }
  }
  ginger.createEditableBootgrid(ipv6AddressesGrid, opts, 'IPADDR');

  ipv6AddressAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'IPADDR',
      'width': '30%',
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'PREFIX',
      'width': '30%',
      'validation': function() {
        //var isValid = ginger.validateMask($(this).val());
        ginger.markInputInvalid($(this), (ginger.isValidIPv6Prefix($(this).val()) || ginger.isValidIPv6($(this).val())));
      }
    }, {
      'id': 'GATEWAY',
      'width': '30%',
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }];
    commandSettings = {
      "width": "10%",
      "td-class": "text-center"
    };
    ginger.addNewRecord(columnSettings, 'nw-bond-ipv6-addresses-grid', commandSettings);
  });
};

// var createIpv6DnsGrid = function(interface) {
//   var gridFields = [];
//   var opts = [];
//
//   opts['id'] = 'nw-settings-ipv6-dns';
//   opts['gridId'] = "nw-settings-ipv6-dns-grid";
//   opts['noResults'] = " ";
//   opts['selection']=false;
//   opts['navigation']=0;
//
//   gridFields = [{
//     "column-id": 'DNS',
//     "type": 'string',
//     "header-class": "col-xs-12 text-center",
//     "title": "DNS",
//     "identifier": true,
//     "formatter": "editable-nw-ipv6-dns"
//   }, {
//     "column-id": "DNS",
//     "type": 'string',
//     "title": "",
//     "formatter": "row-edit-delete"
//   }];
//
//   opts['gridFields'] = JSON.stringify(gridFields);
//   var dnsGrid = ginger.createBootgrid(opts);
//
//   if ("IPV4_INFO" in interface && "DNSAddresses" in (interface.IPV6_INFO)) {
//    var DNSAddresses = interface.IPV6_INFO.DNSAddresses
//     var dns = {}
//     for(var i=0;i<DNSAddresses.length; i++){
//       // dns =DNSAddresses[i];
//       dns['DNS'] = DNSAddresses[i];
//     }
//     ginger.loadBootgridData(opts['gridId'], dns);
//     updateBootgrid(dnsGrid, opts, 'DNS');
//   }
// };


var createIpv6RouteGrid = function(interface) {
  var gridFields = [];
  var opts = [];
  opts['noResults'] = " ";

  opts['id'] = 'nw-bond-ipv6-routes';
  opts['gridId'] = "nw-bond-ipv6-routes-grid";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'ADDRESS',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Address",
    "identifier": true,
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": 'NETMASK',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Mask",
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": 'GATEWAY',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Default Gateway",
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": 'METRIC',
    "type": 'string',
    'width': '20%',
    "header-class": "text-center",
    "data-class": "center",
    "title": "Metric",
    "formatter": "editable-nw-ipv6-routes"
  }, {
    "column-id": "ADDRESS",
    "type": 'string',
    "title": "",
    "header-class": "text-center",
    "data-class": "center",
    "formatter": "row-edit-delete"
  }];

  opts['gridFields'] = JSON.stringify(gridFields);
  var routesGrid = ginger.createBootgrid(opts);

  if (interface != null) {
    if ("IPV6_INFO" in interface && "ROUTES" in (interface.IPV6_INFO)) {
      ginger.loadBootgridData(opts['gridId'], interface.IPV6_INFO.ROUTES);
    }
  }

  ginger.createEditableBootgrid(routesGrid, opts, 'ADDRESS');

  ipv6RoutesAddButton.on('click', function() {
    var columnSettings = [{
      'id': 'ADDRESS',
      'width': '20%',
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'NETMASK',
      'width': '20%',
      'validation': function() {
        ginger.markInputInvalid($(this), (ginger.isValidIPv6Prefix($(this).val()) || ginger.isValidIPv6($(this).val())));
      }
    }, {
      'id': 'GATEWAY',
      'width': '20%',
      'validation': function() {
        var isValid = ginger.isValidIPv6($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }, {
      'id': 'METRIC',
      'width': '20%',
      'validation': function() {
        var isValid = /^[0-9]+$/.test($(this).val());
        ginger.markInputInvalid($(this), isValid);
      }
    }];
    commandSettings = {
      "width": "20%",
      "td-class": "text-center"
    };
    ginger.addNewRecord(columnSettings, 'nw-bond-ipv6-routes-grid', commandSettings);
  });
};
var createIpv6DnsGrid = function(interface) {
  var gridFields = [];
  var opts = [];

  opts['id'] = 'nw-bond-ipv6-dns';
  opts['gridId'] = "nw-bond-ipv6-dns-grid";
  opts['noResults'] = " ";
  opts['selection'] = false;
  opts['navigation'] = 0;

  gridFields = [{
    "column-id": 'DNS',
    "type": 'string',
    "header-class": "text-center",
    "data-class": "center",
    "width": "80%",
    "title": "DNS",
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
      var dns = {}
      for (var i = 0; i < DNSAddresses.length; i++) {
        // dns =DNSAddresses[i];
        DNSAddresses[i] = {
          "DNS": DNSAddresses[i]
        };
        // dns['DNS'] = DNSAddresses[i];
      }
      ginger.loadBootgridData(opts['gridId'], dns);

    }
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
}

var validateTimeField = function(field) {
  var isValid = /^[0-9]+$/.test(field.val());
  ginger.markInputInvalid(field, isValid);
}

var getBondModeValue = function(value) {
  var bondModeOptionDetails = {
    '0': 'balance-rr',
    '1': 'active-backup',
    '2': 'balance-xo r',
    '3': 'broadcast',
    '4': '802.3ad',
    '5': 'balance-tlb',
    '6': 'balance-alb'
  };
  return bondModeOptionDetails[value];
}
