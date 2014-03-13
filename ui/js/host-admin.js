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
            $(".desc", "#newBakDialog").prop("value", null);
            $("#includeBox").empty();
            $("#excludeBox").empty();
            $("#newBakFormBtn").button("enable");
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
                ginger.createBackupArchive(content, function(){
                    $("#newBakDialog").dialog("close");
                    $("#bakGridBody").empty();
                    ginger.setupBakGrid();
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
            var tempNode = $.parseHTML(kimchi.template($("#backupItem").html(), data[i]));
            $("#bakGridBody").append(tempNode);
            var parts = ["include", "exclude"];
            for(var x=0;x<parts.length;x++){
                var path = "";
                for(var y=0;y<data[i][parts[x]].length;y++){
                    path += "<div class='path-item'>"+data[i][parts[x]][y]+"</div>"
                }
                data[i][parts[x]] = path;
            }
            var tooltipContent = kimchi.template($("#backupTooltip").html(), data[i]);
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
}

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
};
