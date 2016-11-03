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

 ginger.initVolumeGroupAdd =  function(){

     ginger.pageContentMapping=[
       {
         "container":"vg-add-name",
         "validation":"ginger.validateVgName"
       },
       {
         "container":"pvDetails",
         "validation":"ginger.loadPartitionsList"
       },
       {
         "container":"partDetails",
         "validation":"ginger.getSelectedPvDetails",
         "previous":"ginger.getExistingPvDetails"
       },
       {
         "container":"pvSelection",
         "previous":"ginger.loadPartitionsList"
       }
     ];
      ginger.numPages = ginger.pageContentMapping.length;
      var stepDescription = [i18n['GINVG00046M'],i18n['GINVG00047M'],i18n['GINVG00048M'],i18n['GINVG00049M']];
      ginger.configurePageNavigation(ginger.numPages,ginger.pageContentMapping,"add-expand-vg",stepDescription);
      $("#vg-reduce").css("display","none");
      ginger.getCreateVgDetails("add-expand-vg");

      $('#vg-add-title').html(i18n['GINVG00043M']);

      $('#vg-create-button-apply').on('click',function(){
        var selectedPvlist = $("#selected-pv-table").DataTable().rows().data();

        var selectedPvpaths= [];
        $.each(selectedPvlist,function(index,pv){
           selectedPvpaths.push(pv[0]);
        });

        var vgCreateParams= {
          'vg_name':$('#vg-name-input').val(),
          'pv_paths': selectedPvpaths
        };

        var taskAccepted = false;
        var onTaskAccepted = function() {
          if (taskAccepted) {
            return;
          }
          taskAccepted = true;
        };
         ginger.createVolumeGroup(vgCreateParams,function(result){
            onTaskAccepted();
            wok.window.close();
            $("#volume-group-table tbody").html("");
            $("#volume-group-table").DataTable().destroy();
            ginger.initVolumeGroupGridData(); //refresh volume group list
            wok.message.success(i18n['GINVG0001M'].replace("%1", vgCreateParams['vg_name']), '#alert-vg-container');

         },function(result) {
           if (result['message']) { // Error message from Async Task status TODO
             var errText = result['message'];
           } else {
             var errText = result['responseJSON']['reason'];
           }
           result && wok.message.error(errText, '#alert-vg-create-modal-container');
           $("#volume-group-table tbody").html("");
           $("#volume-group-table").DataTable().destroy();
           ginger.initVolumeGroupGridData(); //refresh volume group list
           taskAccepted;
         },onTaskAccepted);
      });
};

ginger.configurePageNavigation = function(noOfPages,pageContentMapping,containerId,stepDetails){
  $('.pager').data("curr",0);

  var pageContainerId=pageContentMapping[0]["container"];
  $('#'+containerId).children().css('display','none');
  $('#'+pageContainerId,'#'+containerId).css('display','block');
  $("#vg-create-button-prev").addClass('disabled');

   for(var index=0;index < noOfPages; index++){
     var stepHtml = ['<div class="stepwizard-step">',
                     '<a href=\"#step-',(index),'\" type=\"button\" class=\"btn btn-default btn-circle\" disabled=\"disabled\">',(index+1),'</a>',
                     '<p class="desciption">',stepDetails[index],'</p>',
                     '</div>'].join('');
     $('.stepwizard-row').append(stepHtml);
   }

  var steps = $('div.setup-panel div a');
  $('div.setup-panel').find('div a:eq(0)').addClass('btn-primary').removeClass('btn-default').removeAttr('disabled');

  steps.click(function (e) {
      e.preventDefault();
  });

  $("#vg-create-button-prev").on('click',function(e){
    e.preventDefault();
    var currentPage = $('.pager').data("curr");
    var goToPage = parseInt(currentPage) - 1;
    var pageContainerId=pageContentMapping[goToPage]['container'];
    var currentStepWizard  = $('div.setup-panel div a[href="#step-' +currentPage + '"]');
    var previousStepWizard = currentStepWizard.parent().prev().children("a");

    if(goToPage===0){
      $("#vg-create-button-prev").addClass('disabled');
    }
     $("#vg-create-button-next").removeClass('disabled');
     $('.pager').data("curr",goToPage);
     $('#'+containerId).children().css('display','none');
     $('#'+pageContainerId,'#'+containerId).css('display','block');
     $('#vg-create-button-apply').addClass('hidden');
     $('#alert-vg-create-modal-container').empty();
     currentStepWizard.removeClass('btn-primary').addClass('btn-default')
     previousStepWizard.removeAttr('disabled').addClass('btn-primary').removeClass('btn-default');

     if(pageContentMapping[currentPage]["previous"]){
       eval(pageContentMapping[currentPage]["previous"]+"()");
     }
  });

  $("#vg-create-button-next").on('click',function(e){
    e.preventDefault();
    var currentPage = $('.pager').data("curr");
    var isValid = true;
    var currentStepWizard  = $('div.setup-panel div a[href="#step-' +currentPage + '"]');
    var nextStepWizard = currentStepWizard.parent().next().children("a");
    if(pageContentMapping[currentPage]["validation"]){
      isValid = eval(pageContentMapping[currentPage]["validation"]+"()");
    }

    if(isValid){
    var goToPage = parseInt(currentPage) + 1;
    var pageContainerId=pageContentMapping[goToPage]['container'];

    if(goToPage==(noOfPages-1)){
       $("#vg-create-button-next").addClass('disabled');
       if($("#selected-pv-table").DataTable().rows().data().length!=0){
         $('#vg-create-button-apply').removeClass('hidden');
       }
     }
     $("#vg-create-button-prev").removeClass('disabled');
     $('.pager').data("curr",goToPage);
     $('#'+containerId).children().css('display','none');
     $('#'+pageContainerId,'#'+containerId).css('display','block');
     $('#alert-vg-create-modal-container').empty();
     currentStepWizard.removeClass('btn-primary').addClass('btn-default')
     nextStepWizard.removeAttr('disabled').addClass('btn-primary').removeClass('btn-default');
    }
  });
};

ginger.getCreateVgDetails = function(containerId){
  ginger.initSelectedPvList();

  $('#vg-create-button-done').on('click',function(){
    var goToPage= ginger.pageContentMapping.length-1;
    var pageContainerId=ginger.pageContentMapping[goToPage]['container'];
    var currentPage = $('.pager').data("curr");

    var currentStepWizard  = $('div.setup-panel div a[href="#step-' +currentPage + '"]');
    var nextStepWizard = $('div.setup-panel div a[href="#step-' +goToPage + '"]');

    if(ginger.pageContentMapping[parseInt($('.pager').data("curr"))]['container']=='pvDetails'){
      var selectedRows = $('#physical-volumes-table').DataTable().rows('.selected').data();

      var selectedPvTable =  $("#selected-pv-table").DataTable();
      var selectedPvTableRows = selectedPvTable.rows().data();

       $.each(selectedRows,function(index,rows){
        var isAlreadyAdded  = false;
        for(var i=0;i< selectedPvTableRows.length;i++){
            if(selectedPvTableRows[i][0]==rows[0]){
             isAlreadyAdded  = true;
             break;
            }else{
             isAlreadyAdded  = false;
             }
          }
           if(!isAlreadyAdded)
           selectedPvTable.row.add([rows[0]]).draw();
        });
    }

    $('#vg-create-button-done').addClass('hidden');
    $('#vg-create-button-apply').removeClass('hidden');

    if(goToPage==ginger.numPages-1){
       $("#vg-create-button-next").addClass('disabled');
     }
     $("#vg-create-button-prev").removeClass('disabled');
     $('.pager').data("curr",goToPage);
     $('#'+containerId).children().css('display','none');
     $('#'+pageContainerId,'#'+containerId).css('display','block');
     currentStepWizard.removeClass('btn-primary').addClass('btn-default')
     nextStepWizard.removeAttr('disabled').addClass('btn-primary').removeClass('btn-default');
  });
};

ginger.loadPhysicalVolumeDetails = function(){
   $(".pv-loader").show();
   ginger.getPhysicalVolumes(function(data){
      if(data.length > 0) {
        var rows = "";
        $.each(data, function(index, pv){
          rows += "<tr><td>" + pv.PVName + "</td>";
          rows += "<td>" + wok.localeConverters["number-locale-converter"].to(Number((parseInt(pv.PVSize) / 1024).toFixed(2))) + "</td></tr>";
        });
        $("#physical-volumes-table tbody").html(rows);
      }

      var physicalVolumeTable = $("#physical-volumes-table").DataTable({
          "initComplete": function(settings, json) {
            wok.initCompleteDataTableCallback(settings);
            $('#vg-create-button-done').addClass('hidden');
          },
          "oLanguage": {
            "sEmptyTable": i18n['GINNET0063M']
          }
      });

      $('#physical-volumes-table tbody').off();
      $('#physical-volumes-table tbody').on('click', 'tr', function () {
          $(this).toggleClass("selected");

          if(physicalVolumeTable.rows('.selected').data().length>0){
            $('#vg-create-button-done').removeClass('hidden');
           }else{
              $('#vg-create-button-done').addClass('hidden');
           }
      });

      $(".pv-loader").hide();
  });
};
ginger.getExistingPvDetails =  function(){
  var selectedRows = $('#physical-volumes-table').DataTable().rows(".selected").data();
  if(selectedRows.length>0){
     $('#vg-create-button-done').removeClass('hidden');
  }
};

ginger.loadPartitionsList = function(){
   var type= 'part';
   $("#partition-table tbody").html("");
   $("#partition-table").DataTable().destroy();
   $('.partition-loader').show();

 ginger.getPartitionsDevices(type,function(data){
      if(data.length > 0) {
        var rows = "";
        var existingDeviceCheck = [];
        $.each(data, function(index, partition){
          if(!(partition.name.startsWith('dasd') && partition.pkname=="")){
            if(existingDeviceCheck.indexOf(partition.path)==-1){
            rows += "<tr><td>" + partition.path + "</td>";
            rows += "<td>" + wok.localeConverters["number-locale-converter"].to(Number((parseInt(partition.size) / 1024).toFixed(2))) + "</td>";
            rows += "<td>" + partition.type + "</td></tr>";
           }
          }
        });
        $("#partition-table tbody").html(rows);
      }
      var partitionTable = $("#partition-table").DataTable({
        "dom": '<"row"<"col-sm-3 partition-buttons"><"col-sm-9 filter"<"pull-left add"><"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
          "initComplete": function(settings, json) {
            wok.initCompleteDataTableCallback(settings);
            $('#vg-create-button-done').addClass('hidden');
          },
          "oLanguage": {
            "sEmptyTable": i18n['GINNET0063M']
          }
      });

      $('#partition-table tbody').off();
      $('#partition-table tbody').on('click', 'tr', function () {
          $(this).toggleClass("selected");
      });

      $('.partition-loader').hide();
  },function(){
      $('.partition-loader').hide();
  });
  return true;
};

ginger.createPV = function(selectedRows){
  if(selectedRows.length>0){
     $('.selectedPv-loader').show();
       var content = i18n['GINVG0004M'];
       var settings = {
        content: content,
        confirm: i18n["GINNET0015M"]
       };
      wok.confirm(settings,function(){
        $.each(selectedRows,function(index,row){
          var pvDetails = {'pv_name':row[0]};
          var taskAccepted = false;
          var onTaskAccepted = function() {
            if (taskAccepted) {
              return;
            }

            taskAccepted = true;
          };
           ginger.createPhysicalVolume(pvDetails,function(){
             onTaskAccepted();
              wok.message.success(i18n['GINVG0006M'], '#alert-vg-create-modal-container');
              $("#selected-pv-table").DataTable().row.add([row[0]]).draw();
              if(index==selectedRows.length-1){
                $('.selectedPv-loader').hide();
              }
           },function(error){
             if(index==selectedRows.length-1){
               $('.selectedPv-loader').hide();
             }
             wok.message.error(error.message, '#alert-vg-create-modal-container', true);
             taskAccepted;
           },onTaskAccepted);
        });
      });
  }else{
    var content = ((type=='part')?i18n['GINVG0007M']:i18n['GINVG0008M']);
    var settings = {
      content: content,
      confirm: i18n["GINNET0015M"]
     };
      wok.confirm(settings, function() {});
  }
};
ginger.initSelectedPvList =  function(){
  $("#selected-pv-table tbody").html("");
  var selectedPvTable = $("#selected-pv-table").DataTable({
       "initComplete": function(settings, json) {
        wok.initCompleteDataTableCallback(settings);
        $('.selectedPv-loader').hide();
        },
        "oLanguage": {
          "sEmptyTable": i18n['GINVG00042M']
        }
     });
};

ginger.validateVgName= function(){
  var vgName = $('#vg-name-input');

  if(vgName.val()==''){
    ginger.markInputInvalid(vgName, false);
    return false;
  }else{
    ginger.markInputInvalid(vgName, true);
    $("#physical-volumes-table tbody").html("");
    $("#physical-volumes-table").DataTable().destroy();
    ginger.loadPhysicalVolumeDetails();
    return true;
  }
};

ginger.getSelectedPvDetails = function(){
  ginger.getExistingPvSelection();
  $('#vg-create-button-done').addClass('hidden');

  var selectedPvs = $('#selected-pv-table').DataTable().rows().data();
  var partitionSelected = $("#partition-table").DataTable().rows('.selected').data();

  if(selectedPvs.length==0 && partitionSelected.length==0) {
    wok.message.warn(i18n['GINVG00045M'], '#alert-vg-create-modal-container');
    $('#alert-vg-container').focus();
    return false;
  }else {
    if(selectedPvs!=null && selectedPvs.length>0){
      $('#vg-create-button-apply').removeClass('hidden');
    }
    if(partitionSelected!=null && partitionSelected.length>0){
      ginger.createPV(partitionSelected);
    }
  }

   return true;
};

ginger.getExistingPvSelection =  function(){
  var selectedRows = $('#physical-volumes-table').DataTable().rows(".selected").data();
  if(selectedRows.length>0){
   var selectedPvTable =  $("#selected-pv-table").DataTable();
   var selectedPvTableRows = selectedPvTable.rows().data();

   $.each(selectedRows,function(index,rows){
    var isAlreadyAdded  = false;
    for(var i=0;i< selectedPvTableRows.length;i++){
        if(selectedPvTableRows[i][0]==rows[0]){
         isAlreadyAdded  = true;
         break;
        }else{
         isAlreadyAdded  = false;
         }
      }
       if(!isAlreadyAdded)
       selectedPvTable.row.add([rows[0]]).draw();
    });
  }
};

ginger.initVolumeGroupEdit =  function(){
   $("#vg-reduce").css('display','block');
   $("#add-expand-vg").css('display','none');
   $(".stepwizard").css('display','none');

   ginger.changeButtonStatus(['vg-create-button-prev','vg-create-button-next'],false);

   var volumeName = ($("#volume-group-table").DataTable().rows('.selected').data()[0])[0];
   $('#vg-add-title').html(i18n['GINVG00044M'].replace('%1',volumeName));
   ginger.getVolumeGroupDetails(volumeName,function(data){
   var pvList = data['pvNames'];

   var addedPvs = [];
   $.each(pvList,function(index,pv){
     var pvPath = {};
      pvPath['path']=pv;
      addedPvs.push(pvPath);
   });
    ginger.populateAddedPvList(addedPvs,volumeName);
  });


  $("#vg-create-button-apply").on('click',function(){
    var selectedPvpaths= [];
    var type = "extend";

    var newPvlist = $("#selected-pv-table").DataTable().rows().data();

    $.each(newPvlist,function(index,pv){
       selectedPvpaths.push(pv[0]);
    });

   if(newPvlist!=null && newPvlist.length>0){
     var settings = {
       content: i18n['GINVG00036M'].replace('%1',selectedPvpaths).replace('%2',volumeName),
       confirm: i18n["GINNET0015M"]
      };
       wok.confirm(settings,function(){

         var vgModifyParams= {
           'pv_paths': selectedPvpaths
         };

         ginger.editgetVolumeGroup(volumeName,vgModifyParams,type,function(result){
            wok.message.success(i18n['GINVG00035M'].replace("%1", volumeName), '#alert-vg-container');

            var pvList = result['pvNames'];
            var addedPvs = [];
            $.each(pvList,function(index,pv){
              var pvPath = {};
               pvPath['path']=pv;
               addedPvs.push(pvPath);
            });
            $("#addedPvList tbody").html("");
            $("#addedPvList").DataTable().destroy();
             ginger.populateAddedPvList(addedPvs,volumeName);

             $("#vg-reduce").css("display","block");
             $("#add-expand-vg").css("display","none");
             wok.window.close();
             ginger.changeButtonStatus(['vg-create-button-prev','vg-create-button-next','vg-create-button-apply'],false);
         },function(error){
           wok.message.error(error.responseJSON.reason,'#alert-vg-create-modal-container');
         });

       },function(){});
   }
  });
};

ginger.populateAddedPvList = function(data,volumeName){

  if (data.length > 0) {
    var rows = "";
    $.each(data, function(index, volumeGroup){
        rows += "<tr><td>" + volumeGroup.path + "</td></tr>";
    });
    $("#addedPvList tbody").html(rows);
  }
  var addedPvTable = $("#addedPvList").DataTable({
      "dom": '<"row"<"col-sm-3 vg-resize-buttons"><"col-sm-9 filter"<"pull-right"l><"pull-right"f>>><"row"<"col-sm-12"t>><"row"<"col-sm-6 pages"p><"col-sm-6 info"i>>',
      "initComplete": function(settings, json) {
        wok.initCompleteDataTableCallback(settings);
        var reduceButton = '<button class="btn btn-primary pull-left" id="vg-reduce-button" aria-expanded="false"><i class="fa fa-compress"></i> ' + i18n['GINVG00038M'] + '</button>';
        var extendButton = '<button class="btn btn-primary pull-right" id="vg-extend-button" aria-expanded="false"><i class="fa fa-expand">&nbsp;</i>' + i18n['GINVG00040M']  + '</button>';

        $(".vg-resize-buttons").html(reduceButton+""+extendButton);
      },
      "oLanguage": {
        "sEmptyTable": i18n['GINVG00042M']
      }
  });
 ((addedPvTable.rows().data().length==1 || addedPvTable.rows('.selected').data().length==0)?$('#vg-reduce-button').attr("disabled",true):$('#vg-reduce-button').attr("disabled",false));

   $('#addedPvList tbody').off();
   $('#addedPvList tbody').on('click', 'tr', function () {
      $(this).toggleClass("selected");

      var totalRows = addedPvTable.rows().data();
      var selectedRows = addedPvTable.rows('.selected').data();

      (selectedRows.length==totalRows.length || selectedRows.length==0)?($('#vg-reduce-button').attr("disabled",true)):($('#vg-reduce-button').attr("disabled",false));
   });

   $('#vg-reduce-button').on('click',function(){
       ginger.reduceVolumeGroup(volumeName);
   });

   $('#vg-extend-button').on('click',function(){
     $("#vg-reduce").css("display","none");
     $("#add-expand-vg").css("display","block");
     $(".stepwizard").css('display','table');
     $("#alert-vg-create-modal-container").empty();

     ginger.loadPhysicalVolumeDetails();

     ginger.pageContentMapping=[
       {
         "container":"pvDetails",
         "validation":"ginger.loadPartitionsList"
       },
       {
         "container":"partDetails",
         "validation":"ginger.getSelectedPvDetails",
         "previous":"ginger.getExistingPvDetails"
        },
        {
         "container":"pvSelection",
         "previous":"ginger.loadPartitionsList"
        }
     ];
      ginger.numPages = ginger.pageContentMapping.length;
      var stepDescription = [i18n['GINVG00047M'],i18n['GINVG00048M'],i18n['GINVG00049M']];
      ginger.configurePageNavigation(ginger.numPages,ginger.pageContentMapping,"add-expand-vg",stepDescription);
      ginger.changeButtonStatus(['vg-create-button-prev','vg-create-button-next'],true);
      ginger.getCreateVgDetails("add-expand-vg");
   });
};

ginger.reduceVolumeGroup = function(volumeName){
  var selectedRowsData = $('#addedPvList').DataTable().rows('.selected').data();

   if(selectedRowsData.length>0){
     var selectedrow = [];

     $.each(selectedRowsData,function(index,pv){
        selectedrow.push(pv[0]);
     });

    var settings = {
      content: i18n['GINVG00032M'].replace('%1',selectedrow).replace('%2',volumeName),
      confirm: i18n["GINNET0015M"]
     };
      wok.confirm(settings,function(){
        var type="reduce";

        var vgModifyParams = {
          'pv_paths': selectedrow
        };

        ginger.editgetVolumeGroup(volumeName,vgModifyParams,type,function(result){
           wok.message.success(i18n['GINVG00034M'].replace("%1", volumeName), '#alert-vg-create-modal-container');

           var pvList = result['pvNames'];
           var addedPvs = [];
           $.each(pvList,function(index,pv){
             var pvPath = {};
              pvPath['path']=pv;
              addedPvs.push(pvPath);
           });
           $("#addedPvList tbody").html("");
           $("#addedPvList").DataTable().destroy();
           ginger.populateAddedPvList(addedPvs,volumeName);

        },function(err){
            wok.message.error(err.responseJSON.reason,'#alert-vg-create-modal-container');
        });
      });
  }else{
    var settings = {
      content: i18n['GINVG00033M'],
      confirm: i18n["GINNET0015M"]
     };
    wok.confirm(settings,function(){});
  }
};
