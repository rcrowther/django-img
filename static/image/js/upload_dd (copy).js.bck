
//function has_dd_support() {
    //'use strict';
    //var curleft = 0;
    //if (obj.offsetParent) {
        //while (obj.offsetParent) {
            //curleft += obj.offsetLeft - obj.scrollLeft;
            //obj = obj.offsetParent;
        //}
    //} else if (obj.x) {
        //curleft += obj.x;
    //}
    //return curleft;
//}


$(function($) {
    'use strict';
    var form = $('form');
    var fInput = $('form').find('input[type="file"]');
    var dd = $('.upload_dragndrop');
    var upload_msg = $('.upload_msg')
    var droppedFiles = false;
    
    var canDD = function() {
        var div = document.createElement('div');
        return (
                ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)
            ) 
            // common
            && 'FormData' in window 
            // XMLHttpRequest not on ie9 
            && 'FileReader' in window;
        };


    // auto-runs if capable
    if (canDD) {
        // setup drag and drop uploading
        console.log('naw');
        dd.addClass("upload_able");
      
        dd.on('drag dragstart dragend dragover dragenter dragleave drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
        })
        .on('dragover dragenter', function() {
            dd.addClass('dragover');
        })
        .on('dragleave dragend drop', function() {
            dd.removeClass('dragover');
            //dd.removeClass('drop');
        })
        .on('drop', function(e) {
            droppedFiles = e.originalEvent.dataTransfer.files;
            upload_msg.text(droppedFiles[0].name);
            console.log(droppedFiles);
        });
        
        form.on('submit', function(e) {
            if (dd.hasClass('uploading')) return false;
 
            // Prevent a non-AJAX file upload from starting
            e.preventDefault();
  
            //? not e.originalEvent.dataTransfer.files
            var formData = new FormData();

            var file = fileSelect.files[0];

            // Check the file type
            //if (!/image.*/.test(file.type)) {
            //    return;
            //}

            // Add the file to the form's data
            //formData.append('myfiles[]', file, file.name);
            //formData.append( fInput.attr('name'), file );

            if (fileSelect.files) {
                //file = droppedFiles[0]
                var file = fileSelect.files[0];
                formData.append('files', file, file.name );
            }
            
            //var xhr = new XMLHttpRequest();
            //dd.addClass('uploading').removeClass('error');
            $.ajax({
                url: form.attr('action'),
                type: form.attr('method'),
                data: formData,
                dataType: 'json',
                cache: false,
                contentType: false,
                processData: false,
                complete: function() {
                    //form.removeClass('uploading');
                    console.log('done');
                },
                success: function(data) {
                    //form.addClass( data.success == true ? 'success' : 'error' );
                    //if (!data.success) $errorMsg.text(data.error);
                    // something with the form or what?
                    console.log('success');
                },
                error: function() {
                    // Log the error, show an alert, whatever works for you
                    console.log('fail');
                },
            });
        });
    };
})(django.jQuery);

