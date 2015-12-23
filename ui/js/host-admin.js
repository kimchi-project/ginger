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

ginger.initBakDialog = function() {
    $('#newBakDialog').on('show.bs.modal', function(event) {
        var setBtnState = function() {
            var isValid = $(".invalid-field", "#newBakDialog").length === 0;
            if (isValid) {
                $("#newBakFormBtn").prop("disabled", false);
            } else {
                $("#newBakFormBtn").prop("disabled", true);
            }
        };
        var attachEvent = function(pathItem) {
            $(".delete", pathItem).on("click", function() {
                if (pathItem.parent().children().length === 1) {
                    $("input", pathItem).prop("value", null);
                    $("input", pathItem).removeClass("invalid-field");
                } else {
                    pathItem.remove();
                }
                setBtnState();
            });
            $("input", pathItem).on("keyup", function() {
                $(this).toggleClass("invalid-field", !(/(^\/.*)$/.test($(this).val()) || $(this).val().trim() === ""));
                setBtnState();
            });
        };
        $(".add").on("click", function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            var pathNode = $.parseHTML('<div class="path-item">' +
                '<input type="text" class="form-control input" />' +
                '<span class="column-delete btn btn-link delete del-label">' +
                '<i class="fa fa-minus-circle"></i>Remove</span>' +
                '</div>');
            if (this.parentElement != undefined) {
                if (this.parentElement.className === 'add-path-to-include') {
                    $("#includeBox").append(pathNode);
                } else {
                    $("#excludeBox").append(pathNode);
                }
            }
            attachEvent($(pathNode));
        });

        $("#newBakFormBtn").on("click", function(e) {
            e.preventDefault();
            var content = {
                description: $("#description-textbox", "#newBakDialog").val().trim(),
                include: [],
                exclude: []
            };
            $("input:text", "#includeBox").each(function() {
                if ($(this).val().trim() !== "")
                    content.include.push($(this).val().trim())
            });
            $("input:text", "#excludeBox").each(function() {
                if ($(this).val().trim() !== "")
                    content.exclude.push($(this).val().trim())
            });
            if (content.description == "") delete content.description;
            if (content.include.length == 0) delete content.include;
            if (content.exclude.length == 0) delete content.exclude;
            // Disable Ok button and changing cursor
            // while processing.
            $("body").css("cursor", "wait");
            $("body input").prop("readonly", "readonly");
            $("body button").prop("disabled", "disabled");
            $("body input").css("cursor", "wait");
            $("body button").css("cursor", "wait");
            ginger.createBackupArchive(content, function() {
                $('#newBakDialog').modal('hide');
                $("#bakGridBody").empty();
                ginger.setupBakGrid();
            }, function(result) {
                $("body").css('cursor', 'default');
                $("body input").prop("readonly", false);
                $("body button").prop("disabled", false);
                $("body input").css("cursor", "text");
                $("body button").css("cursor", "pointer");
                wok.message.error(result.responseJSON.reason,'#alert-backup-modal');
            });
        });

        var tempNode = $.parseHTML($("#pathItem").html());
        $("#includeBox").append(tempNode);
        attachEvent($(tempNode));
        tempNode = $.parseHTML($("#pathItem").html());
        $("#excludeBox").append(tempNode);
        attachEvent($(tempNode));
    });

    $('#newBakDialog').on('hide.bs.modal', function(event) {
        clearForm();
        ginger.setupBakGrid();
    });

    var clearForm = function() {
        $("body").css('cursor', 'default');
        $("#description-textbox", "#newBakDialog").prop("value", null);
        $("#includeBox").empty();
        $("#excludeBox").empty();
        $("body input").prop("readonly", false);
        $("body button").prop("disabled", false);
        $("body input").css("cursor", "text");
        $("body button").css("cursor", "pointer");
    };
};

ginger.initBatDelDialog = function() {
    $('#batDelDialog').on('show.bs.modal', function(event) {
        $("#batdel-submit", $(this)).on("click", function(event) {
            var content = {
                counts_ago: -1,
                days_ago: -1
            };
            var delOption = $("input:radio[name=batDelType]:checked");
            var delValue = $("input:text", delOption.parent()).prop("value");
            content[delOption.val()] = parseInt(delValue);
            ginger.deleteBackupArchives(content, function() {
                $('#batDelDialog').modal('hide');
                $("#bakGridBody").empty();
                clearForm();
                ginger.setupBakGrid();
            }, function(data) {
                wok.message.error(data.responseJSON.reason,'#alert-backup-batch-modal');
            });
        });
        var clearForm = function() {
            $("input:text", "#batDelDialog").prop("value", null);
            $("input:text", "#batDelDialog").prop("disabled", true);
            $("input:text", "#batDelDialog").removeClass("invalid-field");
            $("input:text:first", "#batDelDialog").prop("disabled", false);
            $("input:radio[name=batDelType]:first").prop("checked", true);
            $("#batdel-submit").prop("disabled", true);
        };
        var validateInput = function(input) {
            var isValid = new RegExp('^[0-9]*$').test(input.val());
            input.toggleClass("invalid-field", !isValid);

            if (isValid && input.val().trim() !== "") {
                $("#batdel-submit").prop("disabled", false);
            } else {
                $("#batdel-submit").prop("disabled", true);
            }
        };
        $("input:radio[name=batDelType]").on("click", function() {
            $("input:text", "#batDelDialog").prop("disabled", true);
            var activeInput = $("input:text", $("input:radio[name=batDelType]:checked").parent());
            activeInput.prop("disabled", false);
            validateInput(activeInput);
        });
        $("input:text", "#batDelDialog").on("keyup", function() {
            validateInput($(this));
        });
    });
};

ginger.setupBakGrid = function() {
    $(".body", "#bakGridBody").remove();
    ginger.listBackupArchives(function(data) {
        for (var i = 0; i < data.length; i++) {
            data[i].timestamp = new Date(data[i].timestamp * 1000).toLocaleString();
            data[i].filename = data[i].file.split('/');
            data[i].filename = data[i].filename[data[i].filename.length - 1];
            var tempNode = $.parseHTML(wok.substitute($("#backupItem").html(), data[i]));
            $("#bakGridBody").append(tempNode);
            var parts = ["include", "exclude"];
            for (var x = 0; x < parts.length; x++) {
                var path = "";
                for (var y = 0; y < data[i][parts[x]].length; y++) {
                    path += "<div class='path-item'>" + data[i][parts[x]][y] + "</div>"
                }
                data[i][parts[x]] = path;
            }
            var tooltipContent = wok.substitute($("#backupTooltip").html(), data[i]);
            tooltipContent = tooltipContent.replace("includePlaceHodler", data[i].include);
            tooltipContent = tooltipContent.replace("excludePlaceHodler", data[i].exclude);
            $(".backup-history-list", tempNode).append(tooltipContent);

            $(".btn-download").on("click", function(event) {
                event.preventDefault();
                event.stopImmediatePropagation();
                var bakItem = $(this).parent();
                window.open('plugins/ginger/backup/archives/' + encodeURIComponent(bakItem.prop("id")) + '/file');
            });
            $(".btn-delete").on("click", function(event) {
                event.preventDefault();
                event.stopImmediatePropagation();
                var bakItem = $(this).parent();
                ginger.deleteBackupArchive(bakItem.prop("id"), function() {
                    bakItem.remove();
                });
            });
        }

        $('.arrow').on('click', function(event) {
            var that = $(this).parent().parent();
            var slide = $('.backup-history', $(this).parent().parent());
            if (that.hasClass('in')) {
                that.css('height', 'auto');
                that.removeClass('in');
                ginger.changeArrow($('.arrow-down', that));
                slide.slideDown('slow');
            } else {
                slide.slideUp('slow', function() {
                    that.css('height', '');
                });
                that.addClass('in');
                ginger.changeArrow($('.arrow-up', that));
            }
        });
    });
};

ginger.changeArrow = function(obj) {
    if ($(obj).hasClass('arrow-down')) {
        $(obj).removeClass('arrow-down').addClass('arrow-up');
    } else {
        $(obj).removeClass('arrow-up').addClass('arrow-down');
    }
}

ginger.initConfigBak = function() {
    $("#newDefaultBakBtn").on("click", function(event) {
        event.preventDefault();
        ginger.createBackupArchive({}, function() {
            $("#bakGridBody").empty();
            ginger.setupBakGrid();
        })
    });

    ginger.setupBakGrid();
    ginger.initBakDialog();
    ginger.initBatDelDialog();
};

ginger.initPowerMgmt = function() {
    var selectedClass = "pwr-activated";
    var toSelectClass = "pwr-unselected";
    var onSelectClass = "pwr-selected";

    $(".actBtn", "#gingerPowerMgmt").on("click", function(event) {
        $(".actBtn", "#gingerPowerMgmt").prop('disabled', true);
        var currentSelected = $('.' + selectedClass, $(".body", "#gingerPowerMgmt"));
        var toBeSelected = $('.' + onSelectClass, $(".body", "#gingerPowerMgmt"));
        var optName = $(":last-child", toBeSelected.parent()).html();
        $("#progressIndicator", ".ginger .host-admin").addClass("wok-loading-icon");
        $(".actBtn", "#gingerPowerMgmt").prop('disabled', true);

        ginger.activatePowerProfile(optName, function() {
            currentSelected.removeClass(selectedClass).addClass(toSelectClass);
            currentSelected.next().addClass("to-select");
            toBeSelected.removeClass(onSelectClass).addClass(selectedClass);
            toBeSelected.next().removeClass("to-select");
            $(".actBtn", "#gingerPowerMgmt").prop('disabled', true);
            $("#progressIndicator", ".ginger .host-admin").removeClass("wok-loading-icon");
        });
    });
    ginger.getPowerProfiles(function(data) {
        for (var i = 0; i < data.length; i++) {
            data[i].selected = data[i].active ? selectedClass : toSelectClass;
            data[i].toSelect = data[i].active ? "" : "to-select";
            var tempNode = $.parseHTML(wok.substitute($("#pwMgmtItem").html(), data[i]));
            $(".power-options", "#gingerPowerMgmt").append(tempNode);
            $(tempNode).on("click", function() {
                $(".pwr-item :first-child", $(this).parent()).each(function() {
                    if ($(this).hasClass(onSelectClass)) {
                        $(this).removeClass(onSelectClass).addClass(toSelectClass);
                    }
                });
                var iconNode = $(":first-child", $(this));
                if (iconNode.hasClass(toSelectClass)) {
                    iconNode.removeClass(toSelectClass).addClass(onSelectClass);
                    $(".actBtn", "#gingerPowerMgmt").prop('disabled', false);
                } else {
                    $(".actBtn", "#gingerPowerMgmt").prop('disabled', true);
                }
            });
        }
    });
};

ginger.listSensors = function() {
    $(".progress-icon-sensor").show();
    ginger.getSensors(function(result) {
        if ($(".ginger .host-admin .sensor-inline").length > 0) {
            $(".ginger .host-admin .sensor-inline").remove();
        }
        $(".progress-icon-sensor").hide();
        $.each(result, function(i1, d1) {
            if (d1 && d1 != null && i1 != "hdds") {
                $.each(d1, function(i2, d2) {
                    var pathNode = $.parseHTML(wok.substitute($("#sensorItem").html(), {
                        labelHead: i2
                    }));
                    $(".sensor-panel").append(pathNode);
                    if (d2 && d2 != null) {
                        $.each(d2, function(i3, d3) {
                            if (i3 && d3 != null && i3 != "unit") {
                                $.each(d3, function(i4, d4) {
                                    if (i4.match("input")) {
                                        var pathNodeU = $.parseHTML(wok.substitute($("#sensorItem").html(), {
                                            labelBody: i3,
                                            labelNumber: d4,
                                            labelUnit: d2["unit"]
                                        }));
                                        $("#" + i2).append(pathNodeU);
                                    }
                                });
                            }
                        });
                    }
                });
            } else {
                if (d1 != null) {
                    var pathNode = $.parseHTML(wok.substitute($("#sensorItem").html(), {
                        labelHead: i1
                    }));
                    $(".sensor-panel").append(pathNode);
                    $.each(d1, function(i5, d5) {
                        if (i5 != "unit") {
                            var pathNodeU = $.parseHTML(wok.substitute($("#sensorItem").html(), {
                                labelBody: i5,
                                labelNumber: d5,
                                labelUnit: d1["unit"]
                            }));
                            $("#" + i1).append(pathNodeU);
                        }
                    });
                }
            }
            $(".progress-icon-sensor").hide();
        });
        setTimeout(ginger.listSensors, 5000);
    });
};

ginger.initSensorsMonitor = function() {
    ginger.listSensors();
};

ginger.initSEPConfig = function() {
    var sepStatus = function() {
        ginger.getSEPStatus(function(result) {
            if (result.status === "running") {
                $("#sep-ppc-content-area, .fa-circle").removeClass("hidden");
                $("#sep-ppc-content-area, .fa-times-circle").addClass("hidden");
                $("#sepStatusLog").text("Running");
                $("#sepStart").button().attr("style", "display:none");
                $("#sepStop").button().attr("style", "display");
            } else {
                $("#sep-ppc-content-area, .fa-circle").addClass("hidden");
                $("#sep-ppc-content-area, .fa-times-circle").removeClass("hidden");
                $("#sepStatusLog").text("Stopped");
                $("#sepStart").button().attr("style", "display");
                $("#sepStop").button().attr("style", "display:none");
            }
        });
    };
    var listSubscriptions = function() {
        sepStatus();
        $(".wok-datagrid-row", ".ginger .host-admin .subsc-manage").remove();
        ginger.getSEPSubscriptions(function(result) {
            for (var i = 0; i < result.length; i++) {
                var subscItem = $.parseHTML(wok.substitute($("#subscItem").html(), {
                    hostname: result[i]["hostname"],
                    port: result[i]["port"],
                    community: result[i]["community"]
                }));
                $(".ginger .host-admin .subsc-manage").append(subscItem);
            }
            $(".detach", ".ginger .host-admin .subsc-manage").on('click', function(event) {
                var that = $(this).parent();
                ginger.deleteSubscription($("div[data-type='hostname']", that).text(), function() {
                    that.remove();
                });
            });
        });
    };
    var sepStart = function() {
        ginger.startSEP(function() {
            $("#sepStart").hide();
            $("#sepStop").show();
            listSubscriptions();
        });
    };
    var sepStop = function() {
        ginger.stopSEP(function() {
            $("#sepStart").show();
            $("#sepStop").hide();
            listSubscriptions();
        });
    };

    $('#subscriptionAdd').on('show.bs.modal', function(event) {
        var clearSubscriptionSubmit = function(clear) {
            if (clear) {
                $("form#form-subscription-add :input", "#subscriptionAdd").val("");
            }
            $("form#form-subscription-add :input").attr("disabled", false);
            $("#subsc-submit").prop("disabled", true);
            $("#subsc-cancel").prop("disabled", false);
        };
        $("#subscriptionAdd, .input").keyup(function() {
            var sum = 0;
            $("form#form-subscription-add :input").each(function(index, data) {
                if ($(data).val() === "") {
                    sum += 1;
                }
            })
            if (sum != 0) {
                $("#subsc-submit").prop("disabled", true);
            } else {
                $("#subsc-submit").prop("disabled", false);
            }
        });
        $("#subsc-submit", $(this)).button().click(function(event) {
            $("form#form-subscription-add :input").attr("disabled", true);
            $("#subsc-submit").prop("disabled", true);
            $("#subsc-cancel").prop("disabled", true);
            var hostname = $("#subscriptionAdd, .input[name='hostname']", ".modal-body").val();
            var port = parseInt($("#subscriptionAdd, .input[name='port']", ".modal-body").val());
            var community = $("#subscriptionAdd, .input[name='community']", ".modal-body").val();
            var dataSubmit = {
                hostname: hostname,
                port: port,
                community: community,
            };
            ginger.addSEPSubscription(dataSubmit, function() {
                clearSubscriptionSubmit(true);
                $('#subscriptionAdd').modal('hide')
                listSubscriptions();
            }, function(error) {
                wok.message.error(error.responseJSON.reason);
                clearSubscriptionSubmit(false);
            });

        });
        $("#subsc-cancel", $(this)).button().click(function(event) {
            $('#subscriptionAdd').modal('hide')
        });
    });
    $("#sepStart").button().click(function() {
        sepStart();
    });
    $("#sepStop").button().click(function() {
        sepStop();
    });
    listSubscriptions();
};

ginger.initUserManagement = function() {
    var listUsers = function() {
        $(".wok-datagrid-row", ".ginger .host-admin .user-manage").remove();
        ginger.getUsers(function(result) {
            for (var i = 0; i < result.length; i++) {
                var nodeNameItem = $.parseHTML(wok.substitute($("#userItem").html(), {
                    userName: result[i]["name"],
                    userGroup: result[i]["group"],
                    userProfile: result[i]["profile"]
                }));
                $(".ginger .host-admin .user-manage").append(nodeNameItem);
            }
            $(".detach", ".ginger .host-admin .user-manage").on('click', function(event) {
                var that = $(this).parent().parent();
                ginger.deleteUser($("span[data-type='name']", that).text(), function() {
                    that.remove();
                }, function() {});
            });
        }, function() {});
    };

    $('#hostUserAdd').on('show.bs.modal', function(event) {
        $("#kimchiuser").prop("checked", true);
        $("#hostUserAdd, .inputbox[name='userName']", ".modal-body").keyup(function() {
            var tmpVal = $(this).val();
            $("#hostUserAdd, .inputbox[name='userName']", ".modal-body").val(tmpVal);
        });
        $("#enableEditGroup").click(function() {
            if ($(this).prop("checked")) {
                $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", false);
            } else {
                $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", true);
            }
        });
        $(".modal-body .inputbox").keyup(function() {
            var sum = 0;
            $(".modal-body .inputbox").each(function(index, data) {
                if ($(data).val() === "") {
                    sum += 1;
                }
            })
            if (sum != 0) {
                $("#user-submit").prop("disabled", true);
            } else {
                $("#user-submit").prop("disabled", false);
            }
        });
        $("#user-submit", $(this)).on('click', function(event) {
            event.preventDefault();
            $(".modal-body .inputbox").attr("disabled", true);
            $(".modal-body input[type=radio]").attr("disabled", true);
            $("#user-submit").prop("disabled", true);
            $("#user-cancel").prop("disabled", true);

            var userName = $("#hostUserAdd, .inputbox[name='userName']", ".modal-body").val();
            var userPasswd = $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").val();
            var userConfirmPasswd = $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").val();
            var userGroup = $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").val();
            var userProfile = $(".modal-body input[name=userProfile]:checked").val();

            var dataSubmit = {
                name: userName,
                password: userPasswd,
                group: userGroup,
                profile: userProfile
            };
            if (userPasswd === userConfirmPasswd) {
                ginger.addUser(dataSubmit, function() {
                    $('#hostUserAdd').modal('hide');
                    clearUMSubmit();
                    listUsers();
                }, function(data) {
                    wok.message.error(data.responseJSON.reason,'#alert-user-modal');
                    enableFields();
                });
            } else {
                wok.confirm({
                    title: i18n['KCHAPI6006M'],
                    content: i18n['GINUM0002E'],
                    confirm: i18n['KCHAPI6002M'],
                    cancel: i18n['KCHAPI6003M']
                }, function() {
                    clearPasswords();
                }, function() {
                    clearUMSubmit();
                });
            }
        });
        $("#user-cancel", $(this)).button().click(function(event) {
            $('#hostUserAdd').modal('hide')
        });
        var enableFields = function() {
            $("#user-cancel").prop("disabled", false);
            $(".modal-body .inputbox").attr("disabled", false);
            $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", false);
            $(".modal-body input[type=radio]").attr("disabled", false);
            $("#hostUserAdd, .inputbox[name='userName']", ".modal-body").focus();
        }
        var clearPasswords = function() {
            $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").parent().addClass('has-error');
            $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").parent().addClass('has-error');
            $(".modal-body .inputbox").attr("disabled", false);
            $(".modal-body input[type=radio]").attr("disabled", false);
            $(".modal-body .inputbox").attr("disabled", false);
            $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", false);
            $("#user-submit").prop("disabled", true);
            $("#user-cancel").prop("disabled", false);
            $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").val('');
            $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").focus();
        };
        var clearUMSubmit = function() {
            $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").parent().removeClass('has-error');
            $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").parent().removeClass('has-error');
            $("#kimchiuser").prop("checked", true);
            $("#enableEditGroup").prop("checked", false);
            $(".modal-body .inputbox").val("");
            $(".modal-body .inputbox").attr("disabled", false);
            $(".modal-body input[type=radio]").attr("disabled", false);
            $(".modal-body .inputbox").attr("disabled", false);
            $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", true);
            $("#user-submit").prop("disabled", true);
            $("#user-cancel").prop("disabled", false);
        };
    });
    listUsers();
};

ginger.initFirmware = function() {
    ginger.getFirmware(function(data) {
        $("#gingerFWVer").html(data.level);
    });
    $("#gingerPackPath").on("keyup", function(evt) {
        var packPath = $("#gingerPackPath").prop("value");
        var isValid = /(^\/.*)$/.test(packPath);
        $("#gingerPackPath").toggleClass("invalid-field", !isValid && packPath !== "");
        $("#gingerPackPathSub").prop('disabled', !isValid);
    });
    $("#gingerPackPathSub").on("click", function(event) {
        event.preventDefault();
        wok.confirm({
            title: i18n['KCHAPI6006M'],
            content: "The system will be immediately reset to flash the firmware. It may take longer than normal for it to reboot.",
            confirm: i18n['KCHAPI6002M'],
            cancel: i18n['KCHAPI6003M']
        }, function() {
            ginger.updateFirmware({
                path: $("#gingerPackPath").prop("value")
            }, function() {
                $("#gingerFWUpdateMess").css("display", "inline-block");
                $("#gingerPackPathSub").prop('disabled', true);
                $("#gingerPackPath").prop("disabled", true);
            });
        }, null);
    });
};

ginger.initAdmin = function() {
    $(".content-area", "#gingerHostAdmin").css("height", "100%");
    ginger.getCapabilities(function(result) {
        $.each(result, function(enableItem, capability) {
            var itemLowCase = enableItem.toLowerCase();
            if (capability) {
                $("." + itemLowCase + "-ppc-enabled").show();
                switch (itemLowCase) {
                    case "firmware":
                        ginger.initFirmware();
                        break;
                    case "backup":
                        ginger.initConfigBak();
                        break;
                    case "powerprofiles":
                        ginger.initPowerMgmt();
                        break;
                    case "sensors":
                        ginger.initSensorsMonitor();
                        break;
                    case "sep":
                        ginger.initSEPConfig();
                        break;
                    case "users":
                        ginger.initUserManagement();
                        break;
                }
            } else {
                $("." + itemLowCase + "-ppc-enabled").hide();
            }
        });
    });
};
