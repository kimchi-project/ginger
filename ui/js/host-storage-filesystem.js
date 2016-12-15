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
ginger.initFileSystemMount = function(){
 var applyButton = $("#fs-mount-button-apply");
 var fsType = $('#fstype');
 var localMountPoint = $('#fs-mount-point-local');
 var fsMountPartition = $('#fs-mount-partition');
 var remoteMountPoint = $('input[name=nfsmountPoint]');
 var remoteMountPointServerIp = $('input[name=serverIP]');
 var remoteMountPointPath = $('#nfs-path');
 var nfsPathField = $('#nfsPathField');
 var nfsMountOptionType = $('input[name=nfs_mount_option_type]');
 var nfsTimeout = $('#nfs-mount-timeout');
 var nfsMountVersion = $('#nfs-mount-version');
 var isNetDevApplicable = $('#nfs-mount-netdev');
 var nfsMountOptionsButton= $('#nfs_mount_option_button');


  fsType.selectpicker();
  ginger.getPartition(function(result){
    if (result.length > 0) {
      for (var i = 0; i < result.length; i++) {
        fsMountPartition.append($("<option></option>")
          .attr("value", (result[i].path).replace(/"/g, ""))
          .text((result[i].path).replace(/"/g, "")));
      }
      applyButton.attr("disabled",false);
    }else{
      applyButton.attr("disabled",true);
    }
    fsMountPartition.selectpicker();
  });


  fsType.change(function(){
  var fsTypeSelected = fsType.val();

  if(fsTypeSelected=='local'){
    $('#form-fs-mount-local').removeClass('hidden');
    $('#form-fs-mount-remote').addClass('hidden');
    applyButton.attr('disabled',false);
  }else{
    $('#form-fs-mount-local').addClass('hidden');
    $('#form-fs-mount-remote').removeClass('hidden');
    applyButton.attr('disabled',true);
    nfsPathField.addClass('hidden');
    }
    $('#alert-fs-mount-modal-container').empty();
 });

 localMountPoint.keyup(function(){
   if($(this).val()!=''){
      $(this).toggleClass("invalid-field", false);
   }
 });

 remoteMountPoint.keyup(function(){
   if($(this).val()!=''){
      $(this).toggleClass("invalid-field", false);
   }
 });

 nfsTimeout.keypress(function(e){
   if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
           return false;
       }
  });

  applyButton.on('click',function(){
   var fsMountInputData = {};
   var mountOptions ="";
   fsTypeSelected = fsType.val();

   fsMountInputData['type']=fsTypeSelected;

    if(fsTypeSelected=='local'){
       fsMountInputData['blk_dev']= fsMountPartition.val();
       if(localMountPoint.val().length==0){
         localMountPoint.toggleClass("invalid-field", true);
         return false;
       }else{
          fsMountInputData['mount_point']= localMountPoint.val();
       }
    }else{
     fsMountInputData['server']= remoteMountPointServerIp.val();
     fsMountInputData['share']= remoteMountPointPath.val();

     if(remoteMountPoint.val().length==0){
       ginger.loadbasicnfsinfo();
       remoteMountPoint.toggleClass("invalid-field", true);
       return false;
     }else{
       fsMountInputData['mount_point']= remoteMountPoint.val();
     }

     if(nfsMountVersion.val()=='2' || nfsMountVersion.val()=='3'){
       mountOptions+='nfsvers='+nfsMountVersion.val();
     }else{
           if(nfsMountVersion.val()!=''){
           mountOptions+=nfsMountVersion.find('option:selected').text();
         }
     }

     var mountTimeout = nfsTimeout.val();

     if(mountTimeout!=""){
       mountOptions+=',timeo='+mountTimeout;
     }

     var nfsMountOptionType = $('input[name=nfs_mount_option_type]:checked').val();
     var mountType = (nfsMountOptionType!=undefined)?nfsMountOptionType:'';

      if(mountType!=""){
      mountOptions+=','+mountType;
     }

     if($('#nfs-mount-netdev:checked').length!==0){
          mountOptions+=','+'_netdev';
     }
        if(mountOptions!=""){
        fsMountInputData['mount_options']= mountOptions;
       }
   }
    ginger.mountFileSystem(fsMountInputData,function(){
      wok.message.success(i18n['GINFS0002M'].replace('%1',fsMountInputData['mount_point']), '#file-systems-alert-container');
      ginger.initFileSystemsGridData();
      wok.window.close();
    },function(error){
      wok.message.error(error.responseJSON.reason, '#alert-fs-mount-modal-container');
      ginger.initFileSystemsGridData();
    });
  });

  remoteMountPointServerIp.on('input propertychange',function(){
    if($(this).val()!=''){
      var isValid = ginger.validateIp($(this).val()) || ginger.validateHostName($(this).val());
      $('#nfs-path-search').attr("disabled",!isValid);
      $(this).toggleClass("invalid-field", !isValid);
    }else{
      $('#nfs-path-search').attr("disabled",true);
     }
  });

  $('#nfs-path-search').on('click',function(e){
     e.preventDefault();
     var nfsServerIp = remoteMountPointServerIp.val();
     $(this).attr("disabled",true);
     $('#alert-fs-mount-modal-container').empty();

     /*
     *rest api call for retrieving nfs path based on nfs server
     *
     */
     ginger.getNfsShare(nfsServerIp,function(result){
       var nfsshares =  result['NFSShares'];
       if(nfsshares.length > 0){
         $.each(nfsshares,function(index,data){
             remoteMountPointPath.append($("<option></option>")
             .attr("value", data.replace(/"/g, ""))
             .text(data.replace(/"/g, "")));
         });
          remoteMountPointPath.selectpicker();
          nfsPathField.removeClass('hidden');
          applyButton.attr("disabled",false);
       }else{
           wok.message.error(i18n['GINFS0009M'].replace("%1",nfsServerIp),'#alert-fs-mount-modal-container',true);
           nfsPathField.addClass('hidden');
           applyButton.attr("disabled",true);
       }
     },function(error){
        wok.message.error(i18n['GINFS0009M'].replace("%1",nfsServerIp),'#alert-fs-mount-modal-container',true);
        nfsPathField.addClass('hidden');
        applyButton.attr("disabled",true);
     });
  });

  nfsMountOptionsButton.on('click',function(e){
   e.preventDefault();
   $('#fs-mount-tabs').addClass('hidden');
   $('#fs-mount-button-apply').addClass('hidden');
   $('#nw-mount-button-cancel').addClass('hidden');
   $(this).addClass('hidden');
   $('#nfs_mount_option').removeClass('hidden');
   nfsMountVersion.selectpicker();
   $('#nfs-mount-button-back').removeClass('hidden');
   $('#nfs-mount-button-save').removeClass('hidden');

  });

  $('#nfs-mount-button-save').on('click',function(e){
   ginger.loadbasicnfsinfo();
  });

  $('#nfs-mount-button-back').on('click',function(e){
   ginger.loadbasicnfsinfo();
   $('#nfs_mount_option form').trigger('reset');
   $('#timeoutvalue').empty();
  });

  nfsTimeout.on('change',function(e){
      $('#timeoutvalue').text(wok.numberLocaleConverter(parseInt($(this).val()), wok.lang.get_locale()).toString().replace(/\s/g,' '));
  });

};

ginger.loadbasicnfsinfo = function(){
  $('#nfs-mount-button-back').addClass('hidden');
  $('#fs-mount-tabs').removeClass('hidden');
  $('#form-fs-mount-local').addClass('hidden');
  $('#nfs_mount_option').addClass('hidden');
  $('#nfs_mount_option_button').removeClass('hidden');
  $('#nfs-mount-button-save').addClass('hidden');
  $('#fs-mount-button-apply').removeClass('hidden');
  $('#nw-mount-button-cancel').removeClass('hidden');
};
