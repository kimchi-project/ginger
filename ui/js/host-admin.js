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
                    $("input", pathItem).toggleClass("invalid-field", $(this).val().trim() === "" && pathItem.parent().prop('id') !=='excludeBox');
                } else {
                    pathItem.remove();
                }
                checkFields();
            });
            $("input", pathItem).on("keyup", function() {
                if (pathItem.parent().prop('id') !== 'includeBox') {
                    return;
                }
                $(this).toggleClass("invalid-field", $(this).val().trim() === "");
                setBtnState();
            });
        };
        var checkFields = function() {
            $("#includeBox .path-item input").each(function(idx, elm) {
                $(this).toggleClass("invalid-field", $(this).val().trim() === "");
            });
            setBtnState();
        };
        $(".add").on("click", function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
            var pathNode = $.parseHTML('<div class="path-item">' +
                '<input type="text" class="form-control input"  placeholder="/Path/to/folder/" />' +
                '<span class="column-delete btn btn-link delete del-label">' +
                '<i class="fa fa-minus-circle"></i>'+ i18n['GINTITLE0022M'] + '</span>' +
                '</div>');
            if (this.parentElement != undefined) {
                if (this.parentElement.className === 'add-path-to-include') {
                    $("#includeBox").append(pathNode);
                } else {
                    $("#excludeBox").append(pathNode);
                }
            }
            checkFields();
            attachEvent($(pathNode));
        });

        $("#newBakFormBtn").on("click", function(e) {
            e.preventDefault();
            e.stopImmediatePropagation();
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
            var taskAccepted = false;
            var onTaskAccepted = function() {
              if (taskAccepted) {
                return;
              }
              taskAccepted = true;
            };
            $('#newBakDialog').modal('hide');
            wok.message.success(i18n['GINCFGB00001M'], '#alert-modal-container');
            $("#newDefaultBakBtn").hide();
            $("#newCustomBakBtn").hide();
            $("#batchDeleteButton").hide();
            ginger.createBackupArchive(content, function() {
                wok.message.success(i18n['GINCFGB00002M'], '#alert-modal-container');
                $("#newDefaultBakBtn").show();
                $("#newCustomBakBtn").show();
                $("#batchDeleteButton").show();
                ginger.setupBakGrid();
            }, function(result) {
                wok.message.error(result.message,'#alert-modal-container',true);
                $("#newDefaultBakBtn").show();
                $("#newCustomBakBtn").show();
                $("#batchDeleteButton").show();
                $("body").css('cursor', 'default');
                $("body input").prop("readonly", false);
                $("body button").prop("disabled", false);
                $("body input").css("cursor", "text");
                $("body button").css("cursor", "pointer");
            }, onTaskAccepted);
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
        $("#newBakFormBtn").prop("disabled", true);
    };
};

ginger.initBatDelDialog = function() {
    $('#batDelDialog').on('show.bs.modal', function(event) {
        $("#batdel-submit", $(this)).on("click", function(event) {
            var content = {
                counts_ago: "-1",
                days_ago: "-1"
            };
            var delOption = $("input:radio[name=batDelType]:checked");
            var delValue = $("input:text", delOption.parent()).prop("value");
            content[delOption.val()] = delValue;
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
            var isValid = input.val() ? true : false;
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

        $("label[for=days-ago-text]").on("click", function() {
              $("#days-ago-radio").prop('checked',true);
              $("#days-ago-radio").trigger('click');
        });

        $("label[for=counts-ago-text]").on("click", function() {
              $("#counts-ago-radio").prop('checked',true);
              $("#counts-ago-radio").trigger('click');
        });

        $("input:text", "#batDelDialog").on("keyup", function() {
            validateInput($(this));
        });
    });
};

ginger.setupBakGrid = function() {
    ginger.listBackupArchives(function(data) {
        $("#bakGridBody").empty();
        if (data.length == 0) {
            $("#batchDeleteButton").prop("disabled", true);
            var rowNoResults = "<li class='no-results-found'><span style='font-size: 12.5pt;'>" + i18n['GINNET0063M'] + "</span></li>";
            $("#bakGridBody").html(rowNoResults);
        } else {
            $("#batchDeleteButton").prop("disabled", false);
        }
        for (var i = 0; i < data.length; i++) {
            data[i].timestamp = new Date(data[i].timestamp * 1000).toLocaleString(wok.lang.get_locale());
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
                    ginger.setupBakGrid();
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
        var taskAccepted = false;
        var onTaskAccepted = function() {
          if (taskAccepted) {
            return;
          }
          taskAccepted = true;
        };
        wok.message.success(i18n['GINCFGB00001M'], '#alert-modal-container');
        $("#newDefaultBakBtn").hide();
        $("#newCustomBakBtn").hide();
        $("#batchDeleteButton").hide();
        ginger.createBackupArchive({}, function() {
            wok.message.success(i18n['GINCFGB00002M'], '#alert-modal-container');
            $("#newDefaultBakBtn").show();
            $("#newCustomBakBtn").show();
            $("#batchDeleteButton").show();
            ginger.setupBakGrid();
        }, function() {}, onTaskAccepted )
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
        var currentSelected = $('.' + selectedClass, $(".pw-opt", "#gingerPowerMgmt"));
        var toBeSelected = $('.' + onSelectClass, $(".pw-opt", "#gingerPowerMgmt"));
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

var sensorsData;
ginger.lastActiveSensors = [];

ginger.getSensorAdapters = function(data) {
    ginger.lastActiveSensors.length = 0;
    for (i = 0; i < data.sensors.length; i++) {
     $('#sensors-ppc-content-area #adapters').append('<option value="' + data.sensors[i].adapter + '">' + data.sensors[i].adapter + '</option>');
    };
    $('#sensors-ppc-content-area #adapters').selectpicker();
    ginger.getSensorInputs($('#sensors-ppc-content-area #adapters').val());
};

ginger.listSensors = function() {
    ginger.getSensors(function(data) {
        sensorsData = data;
        ginger.getSensorAdapters(sensorsData);
    });
};

ginger.getSensorsByAdapter = function(adapter) {
  var sensorsByAdapter = function(x) {
    return x.adapter == adapter;
  };
  return sensorsByAdapter;
}

ginger.getSensorInputs = function(adapter) {
  var adapterSensors = _.filter(sensorsData.sensors, ginger.getSensorsByAdapter(adapter));
  var adapterDrives = sensorsData.hdds;
  $('#sensors-ppc-content-area #sensors').empty().append('<ul id="' + adapter + '-sensors" class="nav nav-list" />');
  $.each(adapterSensors[0].inputs, function(key, value) {
    if (value.length) {
      switch (key) {
        case 'cores':
          $('ul#' + adapter + '-sensors').append('<li class="cores"><span class="tree-toggle nav-header">'+i18n['GINSEN0005M']+'</span></li>');
          break;
        case 'pci':
          $('ul#' + adapter + '-sensors').append('<li class="pci"><span class="tree-toggle nav-header">'+i18n['GINSEN0006M']+'</span></li>');
          break;
        case 'fans':
          $('ul#' + adapter + '-sensors').append('<li class="fans"><span class="tree-toggle nav-header">'+i18n['GINSEN0007M']+'</span></li>');
          break;
        case 'ambient':
          $('ul#' + adapter + '-sensors').append('<li class="ambient"><span class="tree-toggle nav-header">'+i18n['GINSEN0008M']+'</span></li>');
          break;
        case 'power':
          $('ul#' + adapter + '-sensors').append('<li class="power"><span class="tree-toggle nav-header">'+i18n['GINSEN0009M']+'</span></li>');
          break;
        default:
          $('ul#' + adapter + '-sensors').append('<li class="others"><span class="tree-toggle nav-header">'+i18n['GINSEN00010M']+'</span></li>');
      }
      $('ul#' + adapter + '-sensors > li.' + key).append('<ul style="display:none" class="nav nav-list tree"/>');
      $.each(value, function(k, l) {
        if (typeof(this.name) !== 'undefined') {
          var objId = this.name;
          objId = objId.replace(/\s+/g, '-').toLowerCase();
          $('ul#' + adapter + '-sensors > li.' + key + ' > ul').append('<li class="' + key + '-' + objId + '-' + k + '"><span class="tree-toggle nav-header">' + this.name + '</span><ul style="display:none" class="nav nav-list tree"></ul></li>');
          if (typeof(this.input) !== 'undefined') {
            $('ul#' + adapter + '-sensors > li.' + key + ' > ul > li.' + key + '-' + objId + '-' + k + ' > ul').append('<li><span>'+i18n['GINSEN0001M']+': ' + this.input + ' ' + this.unit + '</span></li>');
          }
          if (typeof(this.min) !== 'undefined') {
            $('ul#' + adapter + '-sensors > li.' + key + ' > ul > li.' + key + '-' + objId + '-' + k + ' > ul').append('<li><span>'+i18n['GINSEN0002M']+': ' + this.min + ' ' + this.unit + '</span></li>');
          }
          if (typeof(this.max) !== 'undefined') {
            $('ul#' + adapter + '-sensors > li.' + key + ' > ul > li.' + key + '-' + objId + '-' + k + ' > ul').append('<li><span>'+i18n['GINSEN0003M']+': ' + this.max + ' ' + this.unit + '</span></li>');
          }
          if (typeof(this.fault) !== 'undefined') {
            $('ul#' + adapter + '-sensors > li.' + key + '  > ul > li.' + key + '-' + objId + '-' + k + ' > ul').append('<li><span>'+i18n['GINSEN0004M']+': ' + this.fault + ' ' + this.unit + '</span></li>');
          }
        }
      });
    };
  });
  if(Object.keys(adapterDrives).length > 1){
    $('ul#' + adapter + '-sensors').append('<li class="hdd"><span class="tree-toggle nav-header">'+i18n['GINSEN00011M']+'</span></li>');
    $('ul#' + adapter + '-sensors > li.hdd').append('<ul style="display:none" class="nav nav-list tree"/>');
    $.each(adapterDrives, function(key, value) {
        if(key !== 'unit'){
                $('ul#' + adapter + '-sensors > li.hdd > ul').append('<li><span>'+key+': '+value +' '+ adapterDrives.unit+ '</span></li>');
      }
    });
  };
};

ginger.refreshSensors = function() {
    ginger.getSensors(function(data) {
        sensorsData = data;
    });
    var currentAdapter = $('#sensors-ppc-content-area #adapters').val();
    ginger.getSensorInputs(currentAdapter);
    $.each(ginger.lastActiveSensors, function(i, cssClass) {
        $('#sensors-ppc-content-area #sensors li.' + cssClass).children('ul.tree').show();
        $('#sensors-ppc-content-area #sensors li.' + cssClass).toggleClass('active');
    });
};

ginger.initSensorsMonitor = function() {
    ginger.listSensors();
    ginger.refreshSensorsInterval = setInterval(ginger.refreshSensors, 5000);

    $('#administration-root-container').on('remove', function() {
        ginger.refreshSensorsInterval && clearInterval(ginger.refreshSensorsInterval);
    });

    $('.update-sensors').on('click', function() {
      ginger.lastActiveSensors.length = 0;
      var currentAdapter = $('#sensors-ppc-content-area #adapters').val();
      ginger.getSensorInputs(currentAdapter);
    });

    $('#sensors-ppc-content-area #sensors').on('click', '.tree-toggle', function() {
      ginger.lastActiveSensors.length = 0;
      $(this).parent().children('ul.tree').toggle(200);
      $(this).parent().toggleClass('active');
      $('#sensors-ppc-content-area #sensors > ul .active').each(function(index, value) {
        ginger.lastActiveSensors.push($(value).attr('class').replace(' active', ''));
      });
    });
};

ginger.initSEPConfig = function() {
    var sepStatus = function() {
        ginger.getSEPStatus(function(result) {
            if (result.status === "running") {
                $("#sep-ppc-content-area .fa-circle").removeClass("hidden");
                $("#sep-ppc-content-area .fa-times-circle").addClass("hidden");
                $("#sepStatusLog").text("Running");
                $("#sepStart").button().attr("style", "display:none");
                $("#sepStop").button().attr("style", "display");
            } else {
                $("#sep-ppc-content-area .fa-circle").addClass("hidden");
                $("#sep-ppc-content-area .fa-times-circle").removeClass("hidden");
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
        }, function(err) {
          wok.message.error(err.responseJSON.reason, '#alert-modal-user-container', true);
        });
    };

    $('#usrMgmtRefreshBtn').on('click', function() {
        listUsers();
    });

    $("#usermangementgrid").on('click','#user-remove', function(event) {
        event.preventDefault();
        var wokUserName = wok.user.getUserName();
        var that = $(this).closest(".wok-datagrid-row");
        var currentUser = $("span[data-type='name']", that).text();
        if (wokUserName === currentUser ) {
          errorMsg = i18n['GINUSR0003M'];
          wok.message.error(errorMsg, '#alert-modal-user-container', true);
        } else {
        var settings = [];
        settings = {
          title: i18n['GINUSR0001M'] + " - " + currentUser,
          content: i18n['GINUSR0002M'],
          cancel: i18n['GGBAPI6003M']
        };
        wok.confirm(settings,function (){
        ginger.deleteUser(currentUser, function() {
            that.remove();
            wok.message.success(i18n['GINUM0007M'].replace("%1", '<strong>'+currentUser+'</strong>'), '#alert-modal-user-container');
        }, function(err) {
          wok.message.error(err.responseJSON.reason, '#alert-modal-user-container', true);
        })},
         function() {});
        }
    });

    $('#hostUserAdd').on('show.bs.modal', function(event) {
        var enableFields = function() {
          $("#user-cancel").prop("disabled", false);
          $(".modal-body .inputbox").attr("disabled", false);
          $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", false);
          $(".modal-body input[type=radio]").attr("disabled", false);
          $("#hostUserAdd, .inputbox[name='userName']", ".modal-body").focus();
        };
        var clearPasswords = function() {
          $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").parent().addClass('has-error');
          $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").parent().addClass('has-error');
          $(".modal-body .inputbox").attr("disabled", false);
          $(".modal-body input[type=radio]").attr("disabled", false);
          $(".modal-body .inputbox").attr("disabled", false);
          $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", false);
          $("#user-submit").prop("disabled", true);
          $("#user-cancel").prop("disabled", false);
          $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").val('');
          $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").val('');
          $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").focus();
        };
        var clearUMSubmit = function() {
          $("#hostUserAdd, .inputbox[name='userPasswd']", ".modal-body").parent().removeClass('has-error');
          $("#hostUserAdd, .inputbox[name='userConfirmPasswd']", ".modal-body").parent().removeClass('has-error');
          $("#userLogin").prop("checked", true);
          $("#enableEditGroup").prop("checked", false);
          $(".modal-body .inputbox").val("");
          $(".modal-body .inputbox").attr("disabled", false);
          $(".modal-body input[type=radio]").attr("disabled", false);
          $(".modal-body .inputbox").attr("disabled", false);
          $("#hostUserAdd, .inputbox[name='userGroup']", ".modal-body").attr("disabled", true);
          $("#user-submit").prop("disabled", true);
          $("#user-cancel").prop("disabled", false);
        };
        clearUMSubmit();
        $("#alert-user-modal").empty();
        $("#userLogin").prop("checked", true);
        // clear user-submit handlers before assigning
        $("#user-submit").off();
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
        $(".modal-body .inputbox", "#hostUserAdd").keyup(function() {
            var sum = 0;
            $(".modal-body .inputbox", "#hostUserAdd").not("[name='userGroup']").each(function(index, data) {
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
        $("#user-submit").on('click', function(event) {
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
            var no_login = false
            if (userProfile === "userNologin") {
                userProfile = "regularuser"
                no_login = true
            }
            var dataSubmit = {
                name: userName,
                password: userPasswd,
                profile: userProfile,
                no_login : no_login
            };
            if ($("#enableEditGroup").prop('checked')) {
                dataSubmit['group'] = userGroup;
            } else {
                dataSubmit['group'] = "";
            }
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
                    content: i18n['GINUM0002E'],
                    confirm: i18n['GINUM0004M'],
                    cancel: i18n['GINUM0005M']
                }, function() {
                    clearPasswords();
                }, function() {
                    clearUMSubmit();
                }, function(){
                  clearPasswords();
                });
            }
        });
        $("#user-cancel", $(this)).button().click(function(event) {
            $('#hostUserAdd').modal('hide')
        });
    });

    $('#usermangementgrid').on('click','#user-passwdchange', function(event) {
        event.preventDefault();
        var that = $(this).closest(".wok-datagrid-row");
        var username = $("span[data-type='name']", that).text();
        var wokUserName = wok.user.getUserName();
        $('#hostUserPasswordChange').modal('show');
        var enableFields = function() {
          $("#hostUserPasswordChange, .inputbox[name='newUserPasswd']", ".modal-body").parent().removeClass('has-error');
          $("#hostUserPasswordChange, .inputbox[name='confirmNewPasswd']", ".modal-body").parent().removeClass('has-error');
          $("#user-password-change-cancel").prop("disabled", false);
          $(".modal-body .inputbox").val("");
          $(".modal-body .inputbox").attr("disabled", false);
          $("#hostUserPasswordChange, .inputbox[name='newUserPasswd']", ".modal-body").focus();
          $("#user-password-change-submit").prop("disabled", true);
        };
        var clearPasswords = function() {
          $("#hostUserPasswordChange, .inputbox[name='newUserPasswd']", ".modal-body").parent().addClass('has-error');
          $("#hostUserPasswordChange, .inputbox[name='confirmNewPasswd']", ".modal-body").parent().addClass('has-error');
          $(".modal-body .inputbox").attr("disabled", false);
          $("#user-password-change-submit").prop("disabled", true);
          $("#user-password-change-cancel").prop("disabled", false);
          $(".modal-body .inputbox").val("");
          $("#hostUserPasswordChange, .inputbox[name='newUserPasswd']", ".modal-body").focus();
        };
        enableFields();
        $("#alert-user-password-change-modal").empty();
        // clear user-password-change-submit handlers before assigning
        $("#user-password-change-submit").off();
        $(".modal-body .inputbox", "#hostUserPasswordChange").keyup(function() {
            var sum = 0;
            $(".modal-body .inputbox", "#hostUserPasswordChange").each(function(index, data) {
                if ($(data).val() === "") {
                    sum += 1;
                }
            })
            if (sum != 0) {
                $("#user-password-change-submit").prop("disabled", true);
            } else {
                $("#user-password-change-submit").prop("disabled", false);
            }
        });
        $("#user-password-change-submit").on('click', function(event) {
            event.preventDefault();
            $(".modal-body .inputbox").attr("disabled", true);
            $("#user-password-change-submit").prop("disabled", true);
            $("#user-password-change-cancel").prop("disabled", true);

            var newUserPasswd = $("#hostUserPasswordChange, .inputbox[name='newUserPasswd']", ".modal-body").val();
            var confirmNewPasswd = $("#hostUserPasswordChange, .inputbox[name='confirmNewPasswd']", ".modal-body").val();
            var dataSubmit = {
                password: newUserPasswd
            };
            if (newUserPasswd === confirmNewPasswd) {
                ginger.changeUserPassword(username, dataSubmit, function() {
                    if (wokUserName === username){
                      wok.confirm({
                          content: i18n['GINUM0003M'],
                          confirm: i18n['GINUM0004M'],
                          cancel: i18n['GINUM0005M']
                      }, function() {
                          document.location.href = 'login.html';
                      }, function() {
                          document.location.href = 'login.html';
                      });
                    }
                    else {
                      wok.message.success(i18n['GINUM0006M'].replace("%1", '<strong>'+username+'</strong>'), '#alert-modal-user-container');
                      $('#hostUserPasswordChange').modal('hide');
                      enableFields();
                    }
                }, function(data) {
                    wok.message.error(data.responseJSON.reason,'#alert-user-password-change-modal');
                    enableFields();
                });
            } else {
                wok.confirm({
                    content: i18n['GINUM0002E'],
                    confirm: i18n['GINUM0004M'],
                    cancel: i18n['GINUM0005M']
                }, function() {
                    clearPasswords();
                }, function() {
                    clearPasswords();
                });
            }
        });
        $("#user-password-change-cancel", $(this)).button().click(function(event) {
            $('#hostUserPasswordChange').modal('hide');
        });
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
            $("#gingerPackPathSub").prop('disabled', true);
            $("#gingerPackPath").prop("disabled", true);
            startFwProgress();
            ginger.updateFirmware({
                path: $("#gingerPackPath").prop("value")
            }, function(result) {
                $("#gingerPackPath").prop("disabled", false);
                var status = result['status'];
                if (status == "failed") {
                    wok.message.error(result['message'])
                };
                reloadProgressArea(result);
                wok.topic('ginger/').publish({result: result})
            }, function(error) {
                $("#gingerPackPath").prop("disabled", false);
                wok.message.error(error.responseJSON.reason);
            }, reloadProgressArea);
        }, null);
    });

    var progressAreaID = 'fwprogress-textarea';

    var reloadProgressArea = function(result) {
        var progressArea = $('#' + progressAreaID)[0];
        $(progressArea).text(result['message']);
        var scrollTop = $(progressArea).prop('scrollHeight');
        $(progressArea).prop('scrollTop', scrollTop);
    };

    var startFwProgress = function() {
        var progressArea = $('#' + progressAreaID)[0];
        $('#fwprogress-container').removeClass('hidden');
        $(progressArea).text('');
        !wok.isElementInViewport(progressArea) &&
            progressArea.scrollIntoView();
    };
};

ginger.initAuditRules = function(){
   ginger.loadAuditRulesData();
   ginger.loadAuditlogsData();
   ginger.loadauditDispatcher();
};

ginger.loadAuditRulesData =  function(){
  $(".rules-loader").show();
  ginger.getAuditRules(function(result) {

    if (result.length > 0) {
      var rows = "";
      $.each(result, function(index, rule){
        rows += "<tr><td>" + (index+1) + "</td>";
        rows += "<td>" + rule.type + "</td>";
        var ruleDetails = rule.rule;
        var titleValue = "";
        var syscallStartIndex = ruleDetails.indexOf("-S");

        if(ruleDetails.substring(syscallStartIndex,ruleDetails.indexOf("-F",syscallStartIndex)).split(",").length > 10) {
           titleValue=ruleDetails.replace(/.{70}/g,"$&"+"\n");
        }else {
           titleValue = ruleDetails;
         }
        rows += "<td class=\"content\" title=\""+titleValue+"\">" + ruleDetails + "</td>";
        rows += "<td style=\"text-align:center;\" class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\"></span> </td>";

        if(rule.loaded=='yes'){
          rows +="<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-loaded-enable enabled\"> <i class=\"fa fa-power-off\"></i></span></td>"
        }else if(rule.loaded=='no'){
          rows +="<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-loaded-disable disabled\"> <i class=\"fa fa-power-off\"></i></span></td>";
        }else{
          rows +="<td style=\"text-align:center;\" class=\"loaded\">--</td>";
        }

        if(rule.persisted=='yes'){
          rows += "<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-persisted-enable enabled\"> <i class=\"fa fa-floppy-o\"></i></span></td>"
        }else if(rule.persisted=='no'){
          rows +="<td style=\"text-align:center;\" class=\"loaded\"><span class=\"audit-rules-persisted-disable disabled\"> <i class=\"fa fa-floppy-o\"></i></span></td>";
        }else{
          rows +="<td style=\"text-align:center;\" class=\"loaded\">--</td>";
        }

        if(rule.rule_info){
          rows += "<td>" + JSON.stringify(rule.rule_info) + "</td>";
        }else{
          rows += "<td></td>";
        }
        rows += "<td>" + rule.persisted + "</td>";
        rows += "<td>" + rule.loaded + "</td></tr>";
      });
      $("#audit-rules-table tbody").html(rows);
    }

    var auditRulesTable = $("#audit-rules-table").DataTable({
        columnDefs: [
          {
            "width":"10%", "targets" : 0
          },
          {
            "width":"15%", "targets" : 1
          },
          {
            "width":"45%", "targets" : 2
          },
          {
            "width":"10%", "targets" : 3
          },
          {
            "width":"10%", "targets" : 4
          },
          {
            "width":"10%", "targets" : 5
          },
          {
            orderable: false, targets: [3,4,5]
          },
          {
            visible : false,  targets: [6,7,8]
          }
        ],
        autoWidth:false,
        "initComplete": function(settings, json) {
          wok.initCompleteDataTableCallback(settings);
        },
        "oLanguage": {
          "sEmptyTable": i18n['GINNET0063M']
        }
    });
     // Add event listener for opening and closing details
       $('#audit-rules-table tbody').on('click', 'td.details-control', function () {
         //,td span.fa
         var tr = $(this).closest('tr');
         var row = auditRulesTable.row( tr );
         var ruleInfo = (row.data()[6]!="")?JSON.parse(row.data()[6]):i18n['GINAUDIT0001M'];

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
            tr.removeClass('shown');
        }else{
            // Open this row
            ginger.ruleDetailsPopulation(ruleInfo,row);
            $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
            tr.addClass('shown');
            $('.audit-rules-details',$("#audit-rules-table tbody")).closest("tr").css("color","black");
        }
    });

    //Row selection
    $('#audit-rules-table tbody').on('click', 'tr', function () {
        $(this).toggleClass("selected");
    });

    $(".rules-loader").hide();
  },function(err){
    $(".rules-loader").hide();
    wok.message.error(err.responseJSON.reason, '#alert-modal-audit-rules-container');
  });
};
$('#audit-rule-add-btn').click(function() {
    wok.window.open('plugins/ginger/host-admin-addAuditRule.html');
});
$('#Audit-Rule-Configure-btn').click(function() {
    wok.window.open('plugins/ginger/host-admin-ConfigAuditRule.html');
});
$('#Audit-Rule-Import-btn').click(function() {
    wok.window.open('plugins/ginger/host-admin-ImportAuditRule.html');
});
$('#Audit-Rule-Edit-btn').click(function() {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0 || auditRulesTable.rows('.selected').data().length > 1) {
        var settings = {
            content: i18n["GINAUDIT0030M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var ruleName,ruleValue;
        var persistcheck;
        var ruleCheck = "";
        $.each(selectedRowsData, function(index, value) {
            ruleName = value[1];
            ruleValue = value[2];
            persistcheck = value[7];
        });
        for (var i = 0; i < ruleValue.length; i++) {
            if (ruleValue[i] != " ") {
                ruleCheck = ruleCheck + ruleValue[i];
            } else{
              break;
            }
          }
        if(ruleCheck == "-e" || ruleCheck == "-D"){
            wok.message.error("Cant edit these rules", "#audit-message", true);
          } else{
        if (persistcheck == "no") {
            var settings = {
                content: i18n["GINAUDIT0031M"],
                confirm: i18n["GINNET0015M"]
            };
            wok.confirm(settings, function() {}, function() {});
        } else {
            if (ruleName == "File System Rule") {
                wok.window.open('plugins/ginger/host-admin-EditAuditRule.html');
            } else if (ruleName == "Control Rule") {
                wok.window.open('plugins/ginger/host-admin-editControlRule.html');
            } else if (ruleName == "System Call Rule") {
                wok.window.open('plugins/ginger/host-admin-editSystemRule.html');
            }
        }
      }
    }
});
$('#Audit-Rule-refresh-btn').on('click', function() {
    $('#audit-rules-table tbody').off();
    $("#audit-rules-table tbody").html("");
    $("#audit-rules-table").DataTable().destroy();
    ginger.loadAuditRulesData();
});
//delete Audit rules
$('#audit-rule-delete-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0022M"] + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRowsData, function(key, value) {
              if(value[1] == "Control Rule" && value[7] == "no" && value[8] == "yes"){
                wok.message.error(i18n["GINAUDIT0036M"]+' '+value[2], '#audit-message', true);
              } else if(value[1] == "Control Rule" && (value[2] == "-D" || value[2].includes("-e"))){
                wok.message.error(i18n["GINAUDIT0039M"]+' '+value[2], '#audit-message', true);
              } else {
                ginger.deleteAuditRule(value[2], function(result) {
                  if(value[1] == "Control Rule"){
                    wok.message.success(i18n["GINAUDIT0037M"]+' '+value[2], '#audit-message');
                  } else{
                    wok.message.success(i18n["GINAUDIT0023M"]+' '+value[2], '#audit-message');
                  }
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                });
              }
            });
              setTimeout(function(){$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});
//audit load
$('#Audit-Rule-Load-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0024M"] + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRows, function(index, value) {
                ginger.LoadAuditRule(value.replace('&lt;','<').replace('&gt;','>'), function(result) {
                    wok.message.success(i18n["GINAUDIT0025M"]+' '+value, '#audit-message');
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                })
            });
            setTimeout(function(){$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});
//unload rule
$('#Audit-Rule-unload-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0026M"] + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRowsData, function(index, value) {
              if(value[1] == "Control Rule"){
                wok.message.error(i18n["GINAUDIT0038M"], '#audit-message', true);
              } else {
                ginger.UnLoadAuditRule(value[2].replace('&lt;','<').replace('&gt;','>'), function(result) {
                    wok.message.success(i18n["GINAUDIT0027M"]+' '+value[2], '#audit-message');
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                })
              }
            });
            setTimeout(function(){$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});
//persist audit
$('#Audit-Rule-Persist-btn').on('click', function(event) {
    var auditRulesTable = $('#audit-rules-table').DataTable();
    if (auditRulesTable.rows('.selected').data().length == 0) {
        var settings = {
            content: i18n["GINAUDIT0021M"],
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {}, function() {});
    } else {
        var selectedRowsData = auditRulesTable.rows('.selected').data();
        var selectedRows = [];
        $.each(selectedRowsData, function(key, value) {
            selectedRows.push(value[2]);
        });
        var settings = {
            content: i18n["GINAUDIT0028M"] + selectedRows,
            confirm: i18n["GINNET0015M"]
        };
        wok.confirm(settings, function() {
            $.each(selectedRows, function(key, value) {
                ginger.PersistAuditRule(value.replace('&lt;','<').replace('&gt;','>'), function(result) {
                    wok.message.success(i18n["GINAUDIT0029M"]+' '+value, '#audit-message');
                }, function(error) {
                    wok.message.error(error.responseJSON.reason, '#audit-message', true);
                })
            });
            setTimeout(function(){$('#Audit-Rule-refresh-btn').trigger('click')},500);
        });
    }
});

ginger.ruleDetailsPopulation = function(data , row){
    var text='';
    var value;
    var ruleDetails = '';
    if(typeof data === 'object'){
    $.each(data, function(key, obj) {
      value = obj;
      switch (key){
       case "action":
          text = i18n['GINAUDIT0002M'];
          break;
       case "filter":
          text = i18n['GINAUDIT0003M'];
          break;
       case "systemcall":
          text = i18n['GINAUDIT0004M'];
          if(value.length > 10) {
             value=value.toString().replace(/.{70}/g,"$&"+"\n");
          }
          break;
       case "field":
          text = i18n['GINAUDIT0005M'];
          if(value.length > 10) {
             value=value.toString().replace(/.{70}/g,"$&"+"\n");
          }
          break;
       case "key":
         text = i18n['GINAUDIT0006M'];
         break;
       default:
             text = key;
      }

  var detailsHtml = [
        '<div>',
          '<span class="column-'+key+'">',
             '<span class="header-'+key+'">'+text+'</span>',
             '<span class="row-'+key+'">'+value+'</span>',
          '</span>',
        '</div>'

   ].join('');
   ruleDetails+=detailsHtml;
  });
  row.child('<div class="audit-rules-details" style="display: block;"><div class="details-list">'+ruleDetails+'</div></div>').show();
}else{
  ruleDetails = data;
  row.child('<div class="audit-rules-details" style="display: block;"><div class="noRuleInfo">'+ruleDetails+'</div></div>').show();
}

};

ginger.loadAuditlogsData =  function(){
  $(".logs-loader").show();
  ginger.getAuditLogs(function(result) {
     ginger.createAuditLogsTable(result);
  },function(err){
    $(".logs-loader").hide();
    wok.message.error(err.responseJSON.reason, '#alert-modal-audit-logs-container');
  });

  ginger.initFilterInfo();
  ginger.initSummaryInfo();

};
ginger.createAuditLogsTable = function(data){
  var rows = "";
  if (data.length > 0) {
      $.each(data, function(index, log){
        var logDetails = log['record'+(index+1)];
        if(logDetails){
          rows += "<tr><td>" + logDetails['Date and Time'] + "</td>";
          rows += "<td>" + logDetails['TYPE'] + "</td>";
          rows += "<td class=\"content\">" + logDetails['MSG']+ "</td>";
          rows += "<td style=\"text-align:center;\" class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\"></span> </td></tr>";
        }
      });
    }
  $("#audit-logs-table tbody").html(rows);

  var auditLogsTable = $("#audit-logs-table").DataTable({
      columnDefs: [
        {
          "width":"15%", "targets" : 0
        },
        {
          "width":"15%", "targets" : 1
        },
        {
          "width":"60%", "targets" : 2
        },
        {
          "width":"10%", "targets" : 3
        },
        {
          orderable: false, targets: [3]
        }
      ],
      autoWidth:false,
      "dom": '<"row"<"log-report pull-left"><"log-filter pull-left"><"log-reset pull-left"><"col-sm-12 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
      "initComplete": function(settings, json) {
        wok.initCompleteDataTableCallback(settings);
        var reportButton = '<button class="btn btn-primary pull-left" id="log-report-btn" aria-expanded="false" data-toggle="modal" data-target="#auditlogReport"><i class="fa fa-file-archive-o">&nbsp;</i> ' + i18n['GINAUDIT0008M'] + '</button>';
        var filterButton = '<button class="btn btn-primary" id="log-filter-btn" aria-expanded="false" data-toggle="modal" data-target="#auditlogFilter"><i class="fa fa-filter">&nbsp;</i>' + i18n['GINAUDIT0007M']  + '</button>';
        var resetButton = '<button class="btn btn-primary" id="log-reset-btn" aria-expanded="false"><i class="fa fa-undo">&nbsp;</i>' + i18n['GINAUDIT0019M']  + '</button>';
        $(".log-report").html(reportButton);
        $(".log-filter").append(filterButton);
        $(".log-reset").html(resetButton);
      },
      "oLanguage": {
        "sEmptyTable": i18n['GINAUDIT0012M']
      }
  });

    // Add event listener for opening and closing details
    $('#audit-logs-table tbody').off();
    $('#audit-logs-table tbody').on('click', 'td.details-control', function () {
      var tr = $(this).closest('tr');
      var row = auditLogsTable.row( tr );
      var logMessage = (row.data()[2]!="")?row.data()[2]:i18n['GINAUDIT0001M'];
      var dateTime = (row.data()[0]!="")?row.data()[0]:'';
      var type = (row.data()[1]!="")?row.data()[1]:'';

      $('.audit-log-details',$('#audit-logs-table tbody')).parent().remove();
      $('.fa-chevron-up',$('#audit-logs-table tbody')).addClass('fa-chevron-down').removeClass('fa-chevron-up');
      if (row.child.isShown()) {
          // This row is already open - close it
          row.child.hide();
          $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
          tr.removeClass('shown');
      }else{
          // Open this row
          row.child('<div class="audit-log-details"><dl class="audit-log-info"><dt>'+dateTime+'</dt><dd>'+i18n['GINAUDIT0013M']+'</dd><dt>'+type+'</dt><dd>'+i18n['GINAUDIT0014M']+'</dd><dt>'+logMessage+'</dt><dd>'+i18n['GINAUDIT0015M']+'</dd></dl></div>').show();
          $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
          tr.addClass('shown');
          $('.audit-log-details',$('#audit-logs-table tbody')).closest("tr").css("color","black");
      }
  });

  //Row selection
  $('#audit-logs-table tbody').on('click', 'tr', function () {
    if($(this).hasClass("selected")){
      $(this).removeClass("selected");
    } else{
      auditLogsTable.$('tr.selected').removeClass('selected');
      $(this).addClass("selected");
   }
  });

  $('#log-reset-btn').on('click', function(e) {
    $(".logs-loader").show();
    ginger.getAuditLogs(function(result){
      $("#audit-logs-table tbody").empty();
      $("#audit-logs-table").DataTable().destroy();
      ginger.createAuditLogsTable(result);
    },function(error){
      wok.message.error(data.responseJSON.reason,"#alert-modal-audit-logs-container");
    });
  });
  $(".logs-loader").hide();
};
ginger.loadauditDispatcher = function(){
   ginger.getDispatcherPlugin(function(result){
     ginger.createDispatcherPluginTable(result);
   },function(error){
      wok.message.error(data.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
   });
   ginger.getDispatcherDetails();
   ginger.getPluginDetails();
};

ginger.createDispatcherPluginTable = function(data){
  var rows = "";
  if (data.length > 0) {
      $.each(data, function(index, log){
        if(log){
          rows += "<tr><td>" + log['name'] + "</td>";
          rows += "<td>" + log['details']['active'] + "</td>";
          rows += "<td style=\"text-align:center;\" class=\"details-control\"><span class=\"fa fa-chevron-down common-down fa-lg\"></span></td>";
          rows +="<td>" +JSON.stringify(log['details'])+"</td></tr>";
        }
      });
    }
  $("#audit-disp-plugin-table tbody").html(rows);

  var auditDispPluginTable = $("#audit-disp-plugin-table").DataTable({
      columnDefs: [
        {
          orderable: false, targets: [2]
        },
        {
          visible : false,  targets: [3]
        }
      ],
      autoWidth:false,
      "dom": '<"row"<"plugin-edit pull-left"><"#dispatcher.pull-left"><"refresh pull-left"><"status-value hidden"><"col-sm-12 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
      "initComplete": function(settings, json) {
        wok.initCompleteDataTableCallback(settings);
          var editButton = '<button class="btn btn-primary" id="plugin-edit-btn" aria-expanded="false"><i class="fa fa-pencil-square-o">&nbsp;</i>' + i18n['GINNET0074M']  + '</button>';
          var refreshButton = '<button class="btn btn-primary" id="disp-refresh-btn" aria-expanded="false"><i class="fa fa-refresh">&nbsp;</i>' + i18n['GINIS00001M']  + '</button>';

          var actionButton = [{
            id: 'dispatch-status-btn'
          },
          {
            id: 'disp-settings-btn',
            class: 'fa fa-cogs',
            label: i18n['GINNET0012M']
          }];

          var actionListSettings = {
            panelID: 'dispatcher',
            buttons: actionButton,
            type: 'action'
          };
        ginger.createActionButtons(actionListSettings);

        $(".plugin-edit").append(editButton);
        $(".refresh").html(refreshButton);
        $("#action-dropdown-button-dispatcher").empty().append('<i class="fa fa-angle-double-down" style="padding-right:7px;"></i>'+i18n['GINAUDITDISP0012M']);
        $("#action-dropdown-button-dispatcher").css({'height':'38.7px','font-weight':'500','width':'auto','background-color':'#3a393b'});

        ginger.getAuditStatus(function(result){
           if(result['dispatcher']!=undefined){
             $("#dispatch-status-btn").empty().html('<i class="fa fa-pause">&nbsp;</i>'+i18n['GINAUDITDISP0011M']);
             $(".status-value").text('enabled');
           }else{
             $("#dispatch-status-btn").empty().html('<i class="fa fa-play">&nbsp;</i>'+i18n['GINAUDITDISP0010M']);
             $(".status-value").text('disabled');
           }
        },function(error){
            wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
        })
      },
      "oLanguage": {
        "sEmptyTable": i18n['GINAUDIT0012M']
      }
  });

    // Add event listener for opening and closing details
    $('#audit-disp-plugin-table tbody').off();
    $('#audit-disp-plugin-table tbody').on('click', 'td.details-control', function () {
      var tr = $(this).closest('tr');
      var row = auditDispPluginTable.row( tr );
      var details = (row.data()[3]!="")?JSON.parse(row.data()[3]):i18n['GINAUDIT0001M'];

      $('.audit-log-details',$('#audit-disp-plugin-table tbody')).parent().remove();
      $('.fa-chevron-up',$('#audit-disp-plugin-table tbody')).addClass('fa-chevron-down').removeClass('fa-chevron-up');
      if (row.child.isShown()) {
          // This row is already open - close it
          row.child.hide();
          $("span",$(this)).addClass('fa-chevron-down').removeClass('fa-chevron-up');
          tr.removeClass('shown');
      }else{
          // Open this row
          var direction  = (details['direction']!=undefined)?details['direction']:'--';
          var format  = (details['format']!=undefined)?details['format']:'--';
          var args  = (details['args']!=undefined)?details['args']:'--';
          var active  = (details['active']!=undefined)?details['active']:'--';
          var path  = (details['path']!=undefined)?details['path']:'--';
          var type  = (details['type']!=undefined)?details['type']:'--';

          row.child('<div class="audit-log-details"><dl class="audit-log-info"><dt>'+
                direction+'</dt><dd>'+i18n['GINAUDITDISP0001M']+'</dd><dt>'+
                format+'</dt><dd>'+i18n['GINAUDITDISP0002M']+'</dd><dt>'+
                args+'</dt><dd>'+i18n['GINAUDITDISP0003M']+'</dd><dt>'+
                active+'</dt><dd>'+i18n['GINAUDITDISP0004M']+'</dd><dt>'+
                path+'</dt><dd>'+i18n['GINAUDITDISP0005M']+'</dd><dt>'+
                type+'</dt><dd>'+i18n['GINAUDITDISP0006M']+'</dd>'+
                '</dl></div>').show();
          $("span",$(this)).addClass('fa-chevron-up').removeClass('fa-chevron-down');
          tr.addClass('shown');
          $('.audit-log-details',$('#audit-disp-plugin-table tbody')).closest("tr").css('color','black');
        }
  });


  //Row selection
  $('#audit-disp-plugin-table tbody').on('click', 'tr', function () {
      if($(this).hasClass("selected")){
        $(this).removeClass("selected");
      }else{
        auditDispPluginTable.$('tr.selected').removeClass('selected');
        $(this).addClass("selected");
      }
  });

  $('#disp-refresh-btn').off();
  $('#disp-refresh-btn').on('click', function(e) {
    $(".dispatcher-loader").show();
    ginger.getDispatcherPlugin(function(result){
      $("#audit-disp-plugin-table tbody").empty();
      $("#audit-disp-plugin-table").DataTable().destroy();
      ginger.createDispatcherPluginTable(result);
    },function(error){
      wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
    });
  });

  $("#dispatch-status-btn").off();
  $("#dispatch-status-btn").on('click',function(e){
    var getCurrentStatus = $(".status-value").text();
    var action = (getCurrentStatus=='enabled')?'disable':'enable';
    ginger.changeAuditDispatcherStatus(action,function(result){
      if(result['dispatcher']!=undefined){
        $("#dispatch-status-btn").empty().append('<i class="fa fa-pause">&nbsp;</i>'+i18n['GINAUDITDISP0011M']);
        wok.message.success(i18n['GINAUDITDISP0013M'],"#alert-modal-audit-dispatcher-container");
        $(".status-value").text('enabled');
      }else{
        $("#dispatch-status-btn").empty().append('<i class="fa fa-play">&nbsp;</i>'+i18n['GINAUDITDISP0010M']);
        wok.message.success(i18n['GINAUDITDISP0014M'],"#alert-modal-audit-dispatcher-container");
        $(".status-value").text('disabled');
      }
    },function(error){
         wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
    });
  });

 $("#plugin-edit-btn").off();
 $("#plugin-edit-btn").on('click',function(){
   var selectedRowsData = $("#audit-disp-plugin-table").DataTable().rows('.selected').data();
   if(selectedRowsData.length>0){
     $("#auditPluginDetails").modal("show");
   }else{
     var settings = {
       content: i18n['GINAUDITDISP0009M'],
       confirm: i18n["GINNET0015M"]
     };
     wok.confirm(settings, function(){},function(){});
   }
 });

  $("#disp-settings-btn").off();
  $("#disp-settings-btn").on('click',function(){
    $("#auditDisprConf").modal("show");
  });
   $(".dispatcher-loader").hide();
};

ginger.getDispatcherDetails = function(){
  $('#auditDisprConf').on('show.bs.modal', function(event) {

    ginger.getDispatcherConfiguration(function(result){
      $("#overflowAction").val(result["overflow_action"]);
      $("#priorityBoost").val(result["priority_boost"]);
      $("#qDepth").val(result["q_depth"]);
      $("#maxRestarts").val(result["max_restarts"]);
      $("#nameFormat").val(result["name_format"]);
    },function(error){
       wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
    });

    $("#disp-conf-button-apply").on("click",function(){
      var params = {};
      params['overflow_action'] = $("#overflowAction").val();
      params['priority_boost']  = $("#priorityBoost").val();
      params['q_depth']         = $("#qDepth").val();
      params['max_restarts']    = $("#maxRestarts").val();
      params['name_format']     = $("#nameFormat").val();

      ginger.updateDispatcherConfiguration(params, function(result){
        $('#auditDisprConf').modal('hide');
        wok.message.success(i18n['GINAUDITDISP0007M'],"#alert-modal-audit-dispatcher-container");
      },function(error){
        wok.message.error(error.responseJSON.reason,"#alert-modal-disp-conf-container");
      });
    });
  });

  $('#auditDisprConf').on('hide.bs.modal', function(event) {
    $("#disp-conf-button-apply").off();
  });
};

ginger.getPluginDetails = function(){
  $('#auditPluginDetails').on('show.bs.modal', function(event) {
    var selectedRowsData = $("#audit-disp-plugin-table").DataTable().rows('.selected').data();
    var pluginDetails = selectedRowsData[0];
    var detailsInfo =  JSON.parse(pluginDetails[3]);
    var pluginName = pluginDetails[0];

    $("#direction").val(detailsInfo['direction']);
    $("#format").val(detailsInfo['format']);
    $("#args").val(detailsInfo['args']);
    $("#active").val(detailsInfo['active']);
    $("#path").val(detailsInfo['path']);
    $("#type").val(detailsInfo['type']);
    $("#active").selectpicker();



    $("#plugin-update-button-apply").on("click",function(){
      var params = {};
      params['direction'] = $("#direction").val();
      params['format']  = $("#format").val();
      params['args']         = $("#args").val();
      params['active']    = $("#active").val();
      params['path']     = $("#path").val();
      params['type']     = $("#type").val();

      ginger.updateDispatcherPlugin(pluginName, params, function(result){
        $('#auditPluginDetails').modal('hide');
        wok.message.success((i18n['GINAUDITDISP0008M']).replace("%1",pluginName),"#alert-modal-audit-dispatcher-container");
        $(".dispatcher-loader").show();
        ginger.getDispatcherPlugin(function(result){
          $("#audit-disp-plugin-table tbody").html("");
          $("#audit-disp-plugin-table").DataTable().destroy();
          ginger.createDispatcherPluginTable(result);
        },function(error){
           wok.message.error(error.responseJSON.reason,"#alert-modal-audit-dispatcher-container");
        });
      },function(error){
        wok.message.error(error.responseJSON.reason,"#alert-modal-plugin-container");
      });
    });
  });

  $('#auditPluginDetails').on('hide.bs.modal', function(event) {
    $("#plugin-update-button-apply").off();
  });
};

ginger.populateFilterOptions =  function(row){
  var optionsList =
  {'-a':i18n['GINAUDIFILTER0001M'],
  '--arch':i18n['GINAUDIFILTER0002M'],
  '-c':i18n['GINAUDIFILTER0003M'],
  '--debug':i18n['GINAUDIFILTER0004M'],
  '-e':i18n['GINAUDIFILTER0005M'],
  '-f':i18n['GINAUDIFILTER0006M'],
  '-gi':i18n['GINAUDIFILTER0007M'],
  '-hn':i18n['GINAUDIFILTER0008M'],
  '--just-one':i18n['GINAUDIFILTER0009M'],
  '-k':i18n['GINAUDIFILTER0010M'],
  '-m':i18n['GINAUDIFILTER0011M'],
  '-p':i18n['GINAUDIFILTER0012M'],
  '-pp':i18n['GINAUDIFILTER0013M'],
  '-r':i18n['GINAUDIFILTER0014M'],
  '-sc':i18n['GINAUDIFILTER0015M'],
  '--session':i18n['GINAUDIFILTER0016M'],
  '-sv':i18n['GINAUDIFILTER0017M'],
  '-te':i18n['GINAUDIFILTER0018M'],
  '-ts':i18n['GINAUDIFILTER0019M'],
  '-tm':i18n['GINAUDIFILTER0020M'],
  '-ui':i18n['GINAUDIFILTER0021M'],
  '-ul':i18n['GINAUDIFILTER0022M'],
  '-uu':i18n['GINAUDIFILTER0023M'],
  '-vm':i18n['GINAUDIFILTER0024M'],
  '-w':i18n['GINAUDIFILTER0025M'],
  '-x':i18n['GINAUDIFILTER0026M']};

  var filterField = $('.selectpicker',row);
   $.each(optionsList,function(key,value){
     filterField.append($("<option></option>")
     .attr("value", key.replace(/"/g, ""))
     .text(value.replace(/"/g, "")));
   });
   filterField.selectpicker();
};

ginger.populateReportOptions =  function(row){
  var detailReportOptionsList =
  {'-au':i18n['GINAUDIREPORT0001M'],
  '-a':i18n['GINAUDIREPORT0002M'],
  '--comm':i18n['GINAUDIREPORT0003M'],
  '-c':i18n['GINAUDIREPORT0004M'],
  '-cr':i18n['GINAUDIREPORT0005M'],
  '-e':i18n['GINAUDIREPORT0006M'],
  '-f':i18n['GINAUDIREPORT0007M'],
  '-h':i18n['GINAUDIREPORT0008M'],
  '--integrity':i18n['GINAUDIREPORT0009M'],
  '-k':i18n['GINAUDIREPORT0010M'],
  '-l':i18n['GINAUDIREPORT0011M'],
  '-m':i18n['GINAUDIREPORT0012M'],
  '-ma':i18n['GINAUDIREPORT0013M'],
  '-n':i18n['GINAUDIREPORT0014M'],
  '-p':i18n['GINAUDIREPORT0015M'],
  '-r':i18n['GINAUDIREPORT0016M'],
  '-s':i18n['GINAUDIREPORT0017M'],
  '--success':i18n['GINAUDIREPORT0018M'],
  '-t':i18n['GINAUDIREPORT0019M'],
  '--tty':i18n['GINAUDIREPORT0020M'],
  '-tm':i18n['GINAUDIREPORT0021M'],
  '-u':i18n['GINAUDIREPORT0022M'],
  '--virt':i18n['GINAUDIREPORT0023M'],
  '-x':i18n['GINAUDIREPORT0024M']};

  var summaryReportOptionList = {'--failed':i18n['GINAUDIREPORT0025M'],
    '-nc':i18n['GINAUDIREPORT0026M'],
    '-te':i18n['GINAUDIREPORT0027M'],
    '-ts':i18n['GINAUDIREPORT0028M']};

  var type = $('#reportType').val();

  var optionsList = (type=='detailed')?detailReportOptionsList:summaryReportOptionList;
  var filterField = $('#log-report-fields',row);

   $.each(optionsList,function(key,value){
     filterField.append($("<option></option>")
     .attr("value", key.replace(/"/g, ""))
     .text(value.replace(/"/g, "")));
   });
   filterField.selectpicker();
};

ginger.initFilterInfo = function(){
  $('#auditlogFilter').on('show.bs.modal', function(event) {
    $('#log-filter-title').text(i18n['GINAUDIT0011M']);
    $('#log-path-info','#auditlogFilter').val("/var/log/audit/audit.log");

    var attachEvent = function(row) {
        $(".delete", row).on("click", function() {
            row.remove();

            if($('#newRow').children().length===0)
             $("#filterList",'#auditlogFilter').addClass('hidden');
         });

        ginger.populateFilterOptions(row);

         $('.selectpicker',row).change(function(){
           var inputRequiredFieldsList = ['-a','--arch','-c','-e','-f','-ga','-ge','-gi','-hn','-k','-m','-n','-o','-p','-pp','-sc','-se','--session','-su','-sv','-tm','-ua','-ue','-ui','-ul','-uu','-vm','-x'];
           var selectedValue = $(this).val();

           if(selectedValue=="-te" || selectedValue=="-ts" ){
             var textField = $('input[type=text]',row);
             if(textField.length!=0){
               var parentDiv = textField.parent();
                textField.remove();
                parentDiv.show();
                var selectOptionHtml = $.parseHTML('<select class="selectpicker col-md-12 timeOption">'+
                '<option value="now">'+i18n['GINAUDIREPORT0029M']+'</option>'+
                '<option value="recent">'+i18n['GINAUDIREPORT0030M']+'</option>'+
                '<option value="today">'+i18n['GINAUDIREPORT0031M']+'</option>'+
                '<option value="yesterday">'+i18n['GINAUDIREPORT0032M']+'</option>'+
                '<option value="this-week">'+i18n['GINAUDIREPORT0033M']+'</option>'+
                '<option value="week-ago">'+i18n['GINAUDIREPORT0034M']+'</option>'+
                '<option value="this-month">'+i18n['GINAUDIREPORT0035M']+'</option>'+
                '<option value="this-year">'+i18n['GINAUDIREPORT0036M']+'</option>'+
               '</select>');
               parentDiv.append(selectOptionHtml);
               $('.selectpicker',parentDiv).selectpicker();
            }
           }else if(inputRequiredFieldsList.indexOf(selectedValue)===-1){
             var textField = $('input[type=text]',row);
             if(textField.length==0){
                if($('.timeOption',row).length!=0){
                  $('.timeOption',row).parent().append('<input type="text" class="form-control input"  placeholder="'+i18n['GINAUDIT0010M']+'" />');
                    $('.timeOption',row).remove();
                }
             }
             $('input[type=text]',row).val("").parent().hide();
           }else{
             var textField = $('input[type=text]',row);
             if(textField.length==0){
                if($('.timeOption',row).length!=0){
                  $('.timeOption',row).parent().append('<input type="text" class="form-control input"  placeholder="'+i18n['GINAUDIT0010M']+'" />');
                    $('.timeOption',row).remove();
                }
             }
             textField.attr("disabled",false);
             $('input[type=text]',row).val("").parent().show();
           }
         });
    };

    $(".add-filter",'#auditlogFilter').on("click", function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        $("#filterList").removeClass("hidden");

        var newNode = $.parseHTML('<div class="row" style="margin-bottom:5px;">'+
        '<div class="col-md-5">' +
         '<select class="selectpicker col-md-10" id="log-filter-fields">'+
         '</select>' +
            '</div>'+
            '<div class="col-md-5">'+
              '<input type="text" class="form-control input"  placeholder="'+i18n['GINAUDIT0010M']+'" style="height:40px;"/>' +
              '</div>'+
              '<div class="col-md-2">'+
              '<span class="column-delete btn btn-link delete del-label" style="float:right;">' +
               '<i class="fa fa-trash"></i></span>' +
              '</div>'+
              '</div>'+
            '</div>');

         $('#newRow','#auditlogFilter').append(newNode);
         attachEvent($(newNode));
      });

     $('#log-filter-button-apply').on('click',function(){
       $(".logs-loader").show();
      $('.Audit-log-loader').show();
       var filterarray = [];
       var filtervaluearray = [];
       var filterarray_len,sortarray_len;
       var valuecheck,filtercheck;
       $('#newRow div.row','#auditlogFilter').each(function(){
            filterarray.push($('.selectpicker',$(this)).val());
            filtercheck = $('.selectpicker',$(this)).val();
            if(filtercheck == "-te" || filtercheck =="-ts"){
               filtervaluearray.push("eventfilter");
            } else{
              filtervaluearray.push($('input[type=text]',$(this)).val());
            }
       });
       for (var i=0; i<filtervaluearray.length; i++){
         if(filtervaluearray[i].length == 0)
             valuecheck = 1;
       }
       filterarray_len = filterarray.length;
       var sortarray = $.unique(filterarray.sort()).sort();
       sortarray_len = sortarray.length;
       if(filterarray_len != sortarray_len){
         wok.message.error(i18n['GINAUDIFILTER0027M'],"#addfielderror-message");
         $('.Audit-log-loader').hide();
       } else if(valuecheck == 1){
         $('.Audit-log-loader').hide();
         wok.message.error(i18n['GINAUDIFILTER0028M'],"#addfielderror-message");
       } else {
       var params = '';
       var logFile= ($('#log-path-info',"#auditlogFilter").val()!='')?'-if '+ $('#log-path-info').val():'';
           params+=logFile;

       if($('input[type=checkbox]:checked',$('#auditlogFilter')).length!==0){
         params.length>0?params+=' -i':params+='-i';
       }

      $('#newRow div.row','#auditlogFilter').each(function(){
           var field = $('.selectpicker',$(this)).val();
           var value = "";

            if($('.timeOption',$(this)).length!=0){
              value = $('.timeOption',$(this)).find('option:selected').val();
            } else {
              value = $('input[type=text]',$(this)).val();
            }
             var inputRequiredFieldsList = ['-a','--arch','-c','-e','-f','-ga','-ge','-gi','-hn','-k','-m','-n','-o','-p','-pp','-sc','-se','--session','-su','-sv','-tm','-ua','-ue','-ui','-ul','-uu','-vm','-x'];
              if(inputRequiredFieldsList.indexOf(field)!=-1){
                if(value!=''){
                  if(params.length>0){
                     params+=" ";
                   }
                  params+=field+" "+value;
                }
              }else{
                if(params.length>0){
                   params+=" ";
                 }
                params+=field+(value!=''?(" "+value):'');
              }

        });

       if(params==''){
          ginger.getAuditLogs(function(result){
            reloadAuditLogs(result);
          },function(error){
            $('.Audit-log-loader').hide();
            wok.message.error(error.responseJSON.reason,"#alert-modal-audit-filter-container");
          });
       }else{
         ginger.filterAuditLogs(params,function(result){
           reloadAuditLogs(result);
         },function(error){
           $('.Audit-log-loader').hide();
           wok.message.error(error.responseJSON.reason,"#alert-modal-audit-filter-container");
         });
       }

       var reloadAuditLogs =  function(result){
         $('#auditlogFilter').modal('hide');
         wok.message.success(i18n['GINAUDIT0016M'],"#alert-modal-audit-logs-container");
         $("#audit-logs-table tbody").empty();
         $("#audit-logs-table").DataTable().destroy();
         ginger.createAuditLogsTable(result);
       }
      }
     });
  });

  $('#auditlogFilter').on('hide.bs.modal', function(event) {
       $(".logs-loader").hide();
       $('.Audit-log-loader').hide();
       $('#log-path-info',$(this)).val('');
       $('#newRow',$(this)).empty();
       $('#interpret',$(this)).attr('checked',false);
       $('#log-filter-button-apply').off();
       $("#addfielderror-message").empty();
       $("#alert-modal-audit-filter-container").empty();
   });
};

ginger.initSummaryInfo = function(){
  $('#auditlogReport').on('show.bs.modal', function(event) {
    $("#reportType").selectpicker();
    $('#log-path-info','#auditlogReport').val("/var/log/audit/audit.log");

    var attachEvent = function(row) {
        $(".delete", row).on("click", function() {
            row.remove();

            if($('#newRow','#auditlogReport').children().length===0)
             $("#filterList",'#auditlogReport').addClass('hidden');
          });

        ginger.populateReportOptions(row);

         $('#log-report-fields.selectpicker',row).change(function(){
           var selectedValue = $(this).val();
           if(selectedValue=="-te" || selectedValue=="-ts" ){

             var optionDropdown = $('select.timeOption',row);
             optionDropdown.empty();
             var selectOptionHtml = $.parseHTML('<option value="now">'+i18n['GINAUDIREPORT0029M']+'</option>'+
                '<option value="recent">'+i18n['GINAUDIREPORT0030M']+'</option>'+
                '<option value="today">'+i18n['GINAUDIREPORT0031M']+'</option>'+
                '<option value="yesterday">'+i18n['GINAUDIREPORT0032M']+'</option>'+
                '<option value="this-week">'+i18n['GINAUDIREPORT0033M']+'</option>'+
                '<option value="week-ago">'+i18n['GINAUDIREPORT0034M']+'</option>'+
                '<option value="this-month">'+i18n['GINAUDIREPORT0035M']+'</option>'+
                '<option value="this-year">'+i18n['GINAUDIREPORT0036M']+'</option>');
               optionDropdown.append(selectOptionHtml);
               optionDropdown.selectpicker();

           }else{
             var optionDropdown = $('.timeOption',row);
             optionDropdown.hide();
           }
         });
    };

    $(".add-filter",'#auditlogReport').on("click", function(e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        $("#filterList",'#auditlogReport').removeClass("hidden");

        var newNode = $.parseHTML('<div class="row" style="margin-bottom:5px;">'+
        '<div class="col-md-5">' +
         '<select class="selectpicker col-md-10" id="log-report-fields">'+
         '</select>' +
            '</div>'+
            '<div class="col-md-5">'+
            '<select class="selectpicker col-md-10 timeOption">'+
            '</select>' +
              '</div>'+
              '<div class="col-md-2">'+
              '<span class="column-delete btn btn-link delete del-label" style="float:right">' +
               '<i class="fa fa-trash"></i></span>' +
              '</div>'+
              '</div>'+
            '</div>');

         $('#newRow','#auditlogReport').append(newNode);
         attachEvent($(newNode));
    });

     $("#reportType").change(function(){
        $('#newRow','#auditlogReport').empty();
        $('#filterList','#auditlogReport').addClass('hidden');
     });

     $('#log-report-button-apply').on('click',function(e){
       e.preventDefault();
       e.stopImmediatePropagation();
       $('.report-loader').show();
       var reportarray = [];
       var reportarray_len,repsortarray_len;
       var filtercheck;
       $('#newRow div.row','#auditlogReport').each(function(){
            reportarray.push($('.selectpicker',$(this)).val());
       });
       reportarray_len = reportarray.length;
       var repsortarray = $.unique(reportarray.sort()).sort();
       repsortarray_len = repsortarray.length;
       if(reportarray_len != repsortarray_len){
         $('.report-loader').hide();
         wok.message.error(i18n['GINAUDIFILTER0029M'],"#Filterfielderror-message");
         $('#summaryreport').empty();
       } else {
      var params = '';
      var logFile= ($('#log-path-info','#auditlogReport').val()!='')?'-if '+ $('#log-path-info','#auditlogReport').val():'';
          params+=logFile;

      if($('input[type=checkbox]:checked',$('#auditlogReport')).length!==0){
        params.length>0?params+=' -i':params+='-i';
      }

       $('#newRow div.row','#auditlogReport').each(function(){
         if(params.length>0){
            params+=" ";
          }
          var field = $('.selectpicker',$(this)).val();
          var value = "";

           if($('.timeOption',$(this)).length!=0){
             value = $('.timeOption',$(this)).find('option:selected').val();
           }
            params+=field+(value!=undefined?(" "+value):'');
       });

      if(params==''){
        ginger.getAuditSummaryReport(function(result){
           populateReport(result);
        },function(error){
          $('.report-loader').hide();
          wok.message.error(error.responseJSON.reason,"#alert-modal-audit-report-container");
          $('#summaryreport').empty();
        })
      }else{
        ginger.getAuditReport(params,function(result){
           populateReport(result);
        },function(error){
          $('.report-loader').hide();
          wok.message.error(error.responseJSON.reason,"#alert-modal-audit-report-container");
          $('#summaryreport').empty();
        });
      }

       var populateReport = function(result){
         $('#report-details').removeClass("hidden").focus();
         $('#summaryreport').empty();
          var columnInfo = {};
          var summary = [];

         if(result.length>1){
          columnInfo  = result[0]["column_info"];
          summary   = result[1]["summary"];
            $("#report-graph-button").removeClass("hidden");
          }else{
           summary = result[0]["summary"];
            $("#report-graph-button").addClass("hidden");
          }

          var  details = "";
            $.each(summary,function(index,info){
              if(info!=""){
                details+=info+"<br>";
              }
            });

          ginger.initGraphDetails(columnInfo);
          $('#summaryreport').append(details);
          $("#summaryReportPathInfo").html(i18n['GINAUDIT0017M']).removeClass('hidden');
          $('.report-loader').hide();
        }
      }
    });

    $("#report-download-button").on("click",function(e){
      var reportFilePath = '/data/logs/audit_summary_report.txt';
      window.open(reportFilePath, '_blank');
    });
 });

   $('#auditlogReport').on('hide.bs.modal', function(event) {
     $('#log-path-info',$(this)).val('');
     $('#newRow',$(this)).empty();
     $('#interpret',$(this)).attr('checked',false);
     $('#log-report-button-apply').off();
     $("#report-download-button").off();
     $("#report-graph-button").off();
      $('#summaryreport').empty();
      $('#summaryReportPathInfo').empty().hide();
      $("#report-details").addClass("hidden");
     $("#Filterfielderror-message").empty();
     $("#alert-modal-audit-report-container").empty();
    });
};
ginger.initGraphDetails = function(columnInfo){
  $('#reportGraph').on('show.bs.modal', function(event) {
    $("#graphPathInfo").addClass("hidden");
    $("#graph-name").val(i18n['GINAUDIT0020M']);
    $("#generate-report-graph-button").addClass("hidden");
    var graphColumns = $("#graphColumns");
    graphColumns.empty().selectpicker('destroy');
    $.each(columnInfo,function(key,value){
      graphColumns.append($("<option></option>")
      .attr("value",value)
      .text(key.replace(/"/g, "")));
    });
    graphColumns.selectpicker();

    var checkFields  = function(){
      if($("#graphColumns").val()!=null && $("#graphColumns").val().length==2 && $("#graphFormat").val()!="" && $("#graph-name").val()!=""){
          $("#generate-report-graph-button").removeClass("hidden");
      }else{
          $("#generate-report-graph-button").addClass("hidden");
      }
    }

    $("#graphFormat").selectpicker();

    $("#graphColumns").change(function(e){
      checkFields();
    });

    $("#graph-name").keyup(function(e){
      checkFields();
    });

    $("#generate-report-graph-button").on('click',function(e){
      e.preventDefault();
      e.stopImmediatePropagation();
      $("#graph").empty();
      var columns = $("#graphColumns").val();
      var format = $("#graphFormat").val();
      var graphName = $("#graph-name").val();
      var params = graphName+","+columns.toString()+","+format;
      ginger.getReportGraph(params,function(result){
        var graphLocation = result[0]['Graph:'];
        $("#graphPathInfo").html(i18n['GINAUDIT0018M'].replace("%1",graphLocation).replace("data","var/lib/wok")).removeClass("hidden");
        window.open(graphLocation, '_blank');
      },function(error){
        wok.message.error(data.responseJSON.reason,"#alert-modal-audit-graph-container");
      });
    });
   });

     $('#reportGraph').on('hide.bs.modal', function(event) {
       $("#graphColumns").selectpicker('deselectAll');
       $("#graphColumns").selectpicker('destroy');
       $("#graphFormat").selectpicker('destroy');
       $("#graph-name").val('');
       $("#graph").empty();
       $("#generate-report-graph-button").off();
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
                    case "audit":
                        ginger.initAuditRules();
                        break;
                }
            } else {
                $("." + itemLowCase + "-ppc-enabled").hide();
            }
        });
    });
};
