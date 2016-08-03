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
    setInterval(ginger.refreshSensors, 5000);

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
