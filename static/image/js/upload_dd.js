
$(function($) {
    'use strict';
    var fInput = $('form').find('input[type="file"]');
    var dd = $('.filedrop');
    
    var canDDTransfer = function() {
        var div = document.createElement('div');
        return (
                ('draggable' in div) || ('ondragstart' in div && 'ondrop' in div)
            ) 
            // common
            && 'FormData' in window 
            // XMLHttpRequest not on ie9 
            && 'FileReader' in window;
        };

    //canDDTransfer = false;
    // auto-runs if capable
    if (canDDTransfer) {
        // setup drag and drop transfer from an area to the iHTML nput
        console.log('naw');
        dd.addClass("enabled");
        
        dd.on('drag dragstart dragend dragover dragenter dragleave drop', function(e) {
            e.preventDefault();
            //e.stopPropagation();
        })
        .on('dragover dragenter', function() {
            dd.addClass('in_dragover');
        })
        .on('dragleave dragend drop', function() {
            dd.removeClass('in_dragover');
        })
        .on('drop', function(e) {
            var files = e.originalEvent.dataTransfer.files;
            console.log(files);
            fInput.prop('drop' + files.length);
            if (files.length > 0) {
                fInput.prop('files', files);
                //fInput.triggerHandler( 'changed' );
                fInput.trigger( 'changed' );
            }
        });
    };
});

