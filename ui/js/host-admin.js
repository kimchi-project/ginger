ginger.initBakDialog = function() {
    $("#newBakDialog").dialog({
        autoOpen : false,
        modal : true,
        width : 800,
        height: 600,
        draggable : false,
        resizable : false,
        closeText: "X",
        open : function(){
            $(".ui-dialog-titlebar-close", $("#newBakDialog").parent()).removeAttr("title");
            var setBtnState = function(){
                var isValid = $(".invalid-field", "#newBakDialog").length===0;
                $("#newBakFormBtn").button(isValid ? "enable" : "disable");
            };
            var attachEvent = function(pathItem){
                $(".add", pathItem).button({
                    icons: { primary: "ui-icon-plusthick" },
                    text: false
                }).click(function(){
                    var pathNode = $.parseHTML($("#pathItem").html());
                    $(this).parent().after(pathNode);
                    attachEvent($(pathNode));
                });
                $(".delete", pathItem).button({
                    icons: { primary: "ui-icon-minusthick" },
                    text: false
                }).click(function(){
                    if(pathItem.parent().children().length===1){
                        $("input", pathItem).prop("value", null);
                        $("input", pathItem).removeClass("invalid-field");
                    }else{
                        pathItem.remove();
                    }
                    setBtnState();
                });
                $("input", pathItem).on("keyup", function(){
                    $(this).toggleClass("invalid-field", !(/(^\/.*)$/.test($(this).val())||$(this).val().trim()===""));
                    setBtnState();
                });
            };
            var tempNode = $.parseHTML($("#pathItem").html());
            $("#includeBox").append(tempNode);
            attachEvent($(tempNode));
            tempNode = $.parseHTML($("#pathItem").html());
            $("#excludeBox").append(tempNode);
            attachEvent($(tempNode));
        },
        beforeClose: function(){
            $("body").css('cursor', 'default');
            $(".desc", "#newBakDialog").prop("value", null);
            $("#includeBox").empty();
            $("#excludeBox").empty();
            $("body input").prop("readonly", false);
            $("body button").prop("disabled", false);
            $("body input").css("cursor", "text");
            $("body button").css("cursor", "pointer");
        },
        buttons : [{
            id: "newBakFormBtn",
            text: "OK",
            click: function(){
                var content = {
                    description: $(".desc", "#newBakDialog").val().trim(),
                    include: [],
                    exclude: []
                };
                $("input:text","#includeBox").each(function(){
                    if($(this).val().trim()!=="")
                        content.include.push($(this).val().trim())
                });
                $("input:text","#excludeBox").each(function(){
                    if($(this).val().trim()!=="")
                        content.exclude.push($(this).val().trim())
                });
                if(content.description=="") delete content.description;
                if(content.include.length==0) delete content.include;
                if(content.exclude.length==0) delete content.exclude;
                // Disable Ok button and changing cursor
                // while processing.
                $("body").css("cursor", "wait");
                $("body input").prop("readonly", "readonly");
                $("body button").prop("disabled", "disabled");
                $("body input").css("cursor", "wait");
                $("body button").css("cursor", "wait");
                ginger.createBackupArchive(content, function(){
                    $("#newBakDialog").dialog("close");
                    $("#bakGridBody").empty();
                    ginger.setupBakGrid();
                }, function(result) {
                    $("body").css('cursor', 'default');
                    $("body input").prop("readonly", false);
                    $("body button").prop("disabled", false);
                    $("body input").css("cursor", "text");
                    $("body button").css("cursor", "pointer");
                    kimchi.message.error(result.responseJSON.reason);
                });
            }
        }]
    });
};

ginger.initBatDelDialog = function() {
    $("#batDelDialog").dialog({
        autoOpen : false,
        modal : true,
        width : 600,
        draggable : false,
        resizable : false,
        closeText: "X",
        open: function(){
            $(".ui-dialog-titlebar-close", $("#batDelDialog").parent()).removeAttr("title");
        },
        beforeClose: function(){
            $("input:text", "#batDelDialog").prop("value", null);
            $("input:text", "#batDelDialog").prop("disabled", true);
            $("input:text", "#batDelDialog").removeClass("invalid-field");
            $("input:text:first", "#batDelDialog").prop("disabled", false);
            $("input:radio[name=batDelType]:first").prop("checked", true);
            $("#batDelFormBtn").button("disable");
        },
        buttons : [{
            id: "batDelFormBtn",
            text: "OK",
            disabled: true,
            click: function(){
                var content = {counts_ago: -1, days_ago: -1};
                var delOption = $("input:radio[name=batDelType]:checked");
                var delValue = $("input:text", delOption.parent()).prop("value");
                content[delOption.val()] = parseInt(delValue);
                ginger.deleteBackupArchives(content, function(){
                    $("#batDelDialog").dialog("close");
                    $("#bakGridBody").empty();
                    ginger.setupBakGrid();
                });
            }
        }]
    });

    var validateInput = function(input){
        var isValid = new RegExp('^[0-9]*$').test(input.val());
        input.toggleClass("invalid-field", !isValid);
        $("#batDelFormBtn").button(isValid && input.val().trim()!=="" ? "enable" : "disable");
    };
    $("input:radio[name=batDelType]").on("click", function(){
        $("input:text", "#batDelDialog").prop("disabled", true);
        var activeInput = $("input:text", $("input:radio[name=batDelType]:checked").parent());
        activeInput.prop("disabled", false);
        validateInput(activeInput);
    });
    $("input:text", "#batDelDialog").on("keyup", function(){
        validateInput($(this));
    });
};

ginger.setupBakGrid = function() {
    ginger.listBackupArchives(function(data){
        for(var i=0;i<data.length;i++){
            data[i].timestamp = new Date(data[i].timestamp*1000).toLocaleString();
            var tempNode = $.parseHTML(kimchi.substitute($("#backupItem").html(), data[i]));
            $("#bakGridBody").append(tempNode);
            var parts = ["include", "exclude"];
            for(var x=0;x<parts.length;x++){
                var path = "";
                for(var y=0;y<data[i][parts[x]].length;y++){
                    path += "<div class='path-item'>"+data[i][parts[x]][y]+"</div>"
                }
                data[i][parts[x]] = path;
            }
            var tooltipContent = kimchi.substitute($("#backupTooltip").html(), data[i]);
            tooltipContent = tooltipContent.replace("includePlaceHodler", data[i].include);
            tooltipContent = tooltipContent.replace("excludePlaceHodler", data[i].exclude);
            $(".file-col,.time-col", tempNode).tooltip({
                items: $(tempNode),
                content: tooltipContent,
                tooltipClass: "ginger-dialog",
                position: { my: "left top-3", at: "left+30 bottom", collision: "flipfit" },
                hide: 100
            });
            $(".download", $(tempNode)).button({
                icons: { primary: "ui-icon ui-icon-arrowthickstop-1-s" },
                text: false
            }).click(function(){
                var bakItem = $(this).parent();
                window.open(kimchi.url + 'plugins/ginger/backup/archives/'+encodeURIComponent(bakItem.prop("id"))+'/file');
            });
            $(".delete", $(tempNode)).button({
                icons: { primary: "ui-icon ui-icon-close" },
                text: false
            }).click(function(){
                var bakItem = $(this).parent();
                ginger.deleteBackupArchive(bakItem.prop("id"), function(){ bakItem.remove(); });
            });
        }
    });
};

ginger.initConfigBak = function() {
    $("#newDefaultBakBtn").button().click(function(){ginger.createBackupArchive({}, function(){
        $("#bakGridBody").empty();
        ginger.setupBakGrid();
    })});
    $("#newCustomBakBtn").button().click(function(){$("#newBakDialog").dialog("open");});
    $("#batDelBtn").button().click(function(){$("#batDelDialog").dialog("open");});
    ginger.setupBakGrid();
    ginger.initBakDialog();
    ginger.initBatDelDialog();
};

ginger.initNetworkConfig = function() {
    var toggleBtnEdit = function(item, on){
        $("button", item).toggleClass("hide");
        $(".cancel", item).toggleClass("hide", !on);
    };
    var attachBtnEvt = function(node, editFunc, saveFunc, cancelFunc){
        $("input", node).each(function(){
            $(this).on("keyup", function(){
                var isValid = ginger.validateIp($(this).val());
                if($(this).parent().hasClass("mask")){
                    isValid = isValid && ginger.validateMask($(this).val());
                }
                isValid = isValid || $(this).val().trim()=="";
                $(this).toggleClass("invalid-field", !isValid);
                $(".save", node).prop("disabled", !isValid);
            });
        });
        $(".edit", node).button({
            icons: { primary: "ui-icon-pencil" },
            text: false
        }).click(editFunc);
        $(".save", node).button({
            icons: { primary: "ui-icon-disk" },
            text: false
        }).click(saveFunc);
        $(".cancel", node).button({
            icons: { primary: "ui-icon-arrowreturnthick-1-w" },
            text: false
        }).click(cancelFunc);
    };
    ginger.getInterfaces(function(data){
        var toggleInterfaceEdit = function(item, on){
            $("label", item).toggleClass("hide", on);
            $("input", item).toggleClass("hide", !on)
            toggleBtnEdit(item, on);
        };
        for(var i=0;i<data.length;i++){
            var isEdit = data[i].ipaddr=="" || data[i].netmask=="";
            data[i].viewMode = isEdit ? "hide" : "";
            data[i].editMode = isEdit ? "" : "hide";
            var tempNode = $.parseHTML(kimchi.substitute($("#nicItem").html(), data[i]));
            $("#gingerInterface").append(tempNode);
            attachBtnEvt(tempNode, function(){
                var item = $(this).parent().parent();
                toggleInterfaceEdit(item, true);
            }, function(){
                var item = $(this).parent().parent();
                var name = $("span", item).first().html();
                var ip = $(".ip", item);
                var mask = $(".mask", item);
                var interface = {
                    ipaddr: $("input", ip).val(),
                    netmask: $("input", mask).val()
                };
                ginger.updateInterface(name, interface, function(){
                    ginger.confirmInterfaceUpdate(name, function(){
                        $("label", ip).text(interface.ipaddr);
                        $("label", mask).text(interface.netmask);
                        toggleInterfaceEdit(item, false);
                    });
                });
            }, function(){
                var item = $(this).parent().parent();
                $("input", item).removeClass("invalid-field");
                $("button", item).prop("disabled", false);
                var ip = $(".ip", item);
                var mask = $(".mask", item);
                $("input", ip).val($("label", ip).text());
                $("input", mask).val($("label", mask).text());
                toggleInterfaceEdit(item, false);
            });
        }
    });
    ginger.getNetworkGlobals(function(data){
        var toggleNWGlobalsEdit = function(item, on){
            $("input", item).prop("disabled", !on);
            toggleBtnEdit(item, on);
        };
        var attachNWGlobalBtnEvt = function(node, saveFunc){
            attachBtnEvt(node, function(){
                toggleNWGlobalsEdit($(this).parent(), true);
            }, function(){
                saveFunc();
            }, function(){
                toggleNWGlobalsEdit($(this).parent(), false);
            });
        };
        if(!data.nameservers || data.nameservers.length==0){
            data.nameservers = [""];
        }
        var addGlobalItem = function(container, itemValue, saveFunc){
            var ip = itemValue;
            var tempNode = $.parseHTML(kimchi.substitute($("#nwGlobalItem").html(), {
                ip: ip,
                viewMode: ip=="" ? "hide" : "",
                editMode: ip=="" ? "": "hide"
            }));
            $("input", tempNode).prop("disabled", ip!="");
            $("#"+container).append(tempNode);
            $("input", tempNode).prop("oriVal", ip);
            attachBtnEvt(tempNode, function(){
                toggleNWGlobalsEdit($(this).parent(), true);
            }, function(){
                saveFunc($(this).parent(), function(item){
                    var input = $("input", item);
                    if(input.val()=="" && $(".sec-content", "#"+container).length!=1){
                        item.remove();
                    }else{
                        input.prop("oriVal", input.val());
                        toggleNWGlobalsEdit(item, false);
                    }
                });
            }, function(){
                var input = $("input", $(this).parent());
                input.removeClass("invalid-field");
                $("button", $(this).parent()).prop("disabled", false);
                input.val(input.prop("oriVal"));
                if(input.prop("oriVal")==""){
                    $(this).parent().remove();
                }else{
                    toggleNWGlobalsEdit($(this).parent(), false);
                }
            });
            return tempNode;
        };
        var addDnsItem = function(dnsVal){
            return addGlobalItem("gingerDNS", dnsVal, function(item, postSave){
                if(!($("input", item).val().trim()==""&&$("input", item).prop("oriVal").trim()=="")){
                    var nwGol = {nameservers:[]};
                    $("input", item.parent()).each(function(){
                        if($(this).val().trim()!=""){
                            nwGol.nameservers.push($(this).val());
                        }
                    });
                    if(nwGol.nameservers.length==0){
                        delete nwGol.nameservers;
                    }
                    ginger.updateNetworkGlobals(nwGol, function(){
                        postSave(item);
                    });
                }
            });
        };
        $("#gingerDnsAdd").button({
            icons: { primary: "ui-icon-plusthick" },
            text: false
        }).click(function(){
            var item = addDnsItem("");
            $(".cancel", item).removeClass("hide");
        });
        for(var i=0;i<data.nameservers.length;i++){
            addDnsItem(data.nameservers[i]);
        }
        addGlobalItem("gingerGateway", data.gateway ? data.gateway : "", function(item, postSave){
            var gateway = $("input", item.parent()).val();
            if(gateway.trim()!=""){
                ginger.updateNetworkGlobals({
                    gateway: gateway
                }, function(){
                    ginger.confirmNetworkUpdate(function(){
                        postSave(item);
                    });
                });
            }
        });
    });
};

ginger.initPowerMgmt = function(){
    var selectedClass = "ui-icon-check";
    var toSelectClass = "ui-icon-radio-off";
    var onSelectClass = "ui-icon-radio-on";
    $(".actBtn", "#gingerPowerMgmt").button({disabled: true}).click(function(){
        var currentSelected = $('.'+selectedClass, $(".body", "#gingerPowerMgmt"));
        var toBeSelected = $('.'+onSelectClass, $(".body", "#gingerPowerMgmt"));
        var optName = $(":last-child", toBeSelected.parent()).html();
        $("#progressIndicator", ".ginger .host-admin").addClass("progress-icon");
        $(".actBtn", "#gingerPowerMgmt").button("option", "disabled", true);
        ginger.activatePowerProfile(optName, function(){
            currentSelected.removeClass(selectedClass).addClass(toSelectClass);
            currentSelected.next().addClass("to-select");
            toBeSelected.removeClass(onSelectClass).addClass(selectedClass);
            toBeSelected.next().removeClass("to-select");
            $(".actBtn", "#gingerPowerMgmt").button("option", "disabled", false);
            $("#progressIndicator", ".ginger .host-admin").removeClass("progress-icon");
        });
    });
    ginger.getPowerProfiles(function(data){
        for(var i=0;i<data.length;i++){
            data[i].selected = data[i].active ? selectedClass : toSelectClass;
            data[i].toSelect = data[i].active ? "" : "to-select";
            var tempNode = $.parseHTML(kimchi.substitute($("#pwMgmtItem").html(), data[i]));
            $(".body", "#gingerPowerMgmt").append(tempNode);
            $(tempNode).on("click", function(){
                $(".item :first-child", $(this).parent()).each(function(){
                    if($(this).hasClass(onSelectClass)){
                        $(this).removeClass(onSelectClass).addClass(toSelectClass);
                    }
                });
                var iconNode = $(":first-child", $(this));
                if(iconNode.hasClass(toSelectClass)){
                    iconNode.removeClass(toSelectClass).addClass(onSelectClass);
                    $(".actBtn", "#gingerPowerMgmt").button("option", "disabled", false);
                }
            });
        }
    });
};

ginger.initSANAdapter = function(){
    ginger.getSANAdapters(function(data){
        var temStr = "<div class='item'>{value}</div>";
        for(var i=0; i<data.length; i++){
            $(".body", $(".name", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].name}));
            $(".body", $(".wwpn", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].wwpn}));
            $(".body", $(".wwnn", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].wwnn}));
            $(".body", $(".state", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].state}));
            $(".body", $(".port", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].vports_inuse+"/"+data[i].max_vports}));
            $(".body", $(".speed", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].speed}));
            $(".body", $(".symbolic", ".san-adapter")).append(kimchi.substitute(temStr, {value: data[i].symbolic_name}));
        }
    });
};

ginger.listSensors = function() {
    ginger.getSensors(function(result) {
        if($(".ginger .host-admin .sensor-inline").length > 0) {
            $(".ginger .host-admin .sensor-inline").remove();
        }
        $.each(result, function(i1, d1) {
            if(d1 && d1 != null && i1 != "hdds") {
                $.each(d1, function(i2, d2) {
                    var pathNode = $.parseHTML(kimchi.substitute($("#sensorBody").html(), {
                        labelHead : i2
                    }));
                    $(".sensor-panel").append(pathNode);
                    if(d2 && d2 != null) {
                        $.each(d2, function(i3, d3) {
                            if(i3 && d3 != null && i3 != "unit") {
                                $.each(d3, function(i4, d4) {
                                    if(i4.match("input")) {
                                        var pathNodeU = $.parseHTML(kimchi.substitute($("#sensorUnit").html(), {
                                            labelBody : i3,
                                            labelNumber : d4,
                                            labelUnit : d2["unit"]
                                        }));
                                        $("#" + i2).append(pathNodeU);
                                    }
                                });
                            }
                        });
                    }
                });
            } else {
                if(d1 != null) {
                    var pathNode = $.parseHTML(kimchi.substitute($("#sensorBody").html(), {
                        labelHead : i1
                    }));
                    $(".sensor-panel").append(pathNode);
                    $.each(d1, function(i5, d5) {
                        if(i5 != "unit") {
                            var pathNodeU = $.parseHTML(kimchi.substitute($("#sensorUnit").html(), {
                                labelBody : i5,
                                labelNumber : d5,
                                labelUnit : d1["unit"]
                            }));
                           $("#" + i1).append(pathNodeU);
                        }
                    });
                }
            }
        });
        setTimeout(ginger.listSensors, 5000);
    });
};

ginger.initSensorsMonitor = function() {
    ginger.listSensors();
};

ginger.initSEPConfig = function() {
    var listSEPContent = function() {
        ginger.getSEPContent(function(result) {
            $("#sepStatusLog").val(result.status)
            $("#sepHostName").val(result["subscription"].hostname);
            $("#sepPort").val(result["subscription"].port);
            $("#sepSNMPCommunity").val(result["subscription"].community);
            if(result.status != "running") {
                $("#sepStart").button().attr("style", "display");
                $("#sepStop").button().attr("style", "display:none");
            } else {
                $("#sepStart").button().attr("style","display:none");
                $("#sepStop").button().attr("style","display");
            }
        }, function() {
            kimchi.message.error.code('GINSEP0005E');
        });
    };
    var sepSubscription = function(sepHostName, sepPort, sepCommunity) {
        var data = {
            hostname : sepHostName,
            port : sepPort,
            community : sepCommunity
        };
        ginger.updateSEPContent(data, function() {
            listSEPContent();
        }, function() {
            kimchi.message.error.code('GINSEP0006E');
        });

    };
    var sepStart = function() {
        ginger.startSEP(function() {
            $("#sepStart").val("style", "display:none");
            $("#sepStop").val("style", "display");
            listSEPContent();
        }, function(){
            kimchi.message.error.code('GINSEP0007E');
        });
    };
    var sepStop = function() {
        ginger.stopSEP(function() {
            $("#sepStart").val("style", "display");
            $("#sepStop").val("style", "display:none");
            listSEPContent();
        }, function(){
            kimchi.message.error.code('GINSEP0008E');
        });
    };
    $("#sepSubscribe").button().click(function() {
        if($("#sepHostName").val() === "") {
            kimchi.message.error.code("GINSEP0001E");
            listSEPContent();
        } else if($("#sepPort").val() === "") {
            kimchi.message.error.code("GINSEP0002E");
            listSEPContent();
        } else if($("#sepSNMPCommunity").val() === "") {
            kimchi.message.error.code("GINSEP0003E");
            listSEPContent();
        } else {
            sepSubscription($("#sepHostName").val(), $("#sepPort").val(), $("#sepSNMPCommunity").val());
        }
    });
    $("#sepStart").button().click(function() {
        sepStart();
    });
    $("#sepStop").button().click(function() {
        sepStop();
    });
    listSEPContent();
};

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
    ginger.initConfigBak();
    ginger.initNetworkConfig();
    ginger.initPowerMgmt();
    ginger.initSANAdapter();
    ginger.initSensorsMonitor();
    ginger.initSEPConfig();
};
