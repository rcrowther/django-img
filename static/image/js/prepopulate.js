/*global URLify*/
(function($) {
    'use strict';
    $.fn.prepopulate = function(dependencies, maxLength, allowUnicode) {
        /*
            Depends on urlify.js
            Populates a selected field with the values of the dependent fields,
            URLifies and shortens the string.
            dependencies - array of dependent fields ids
            maxLength - maximum length of the URLify'd string
            allowUnicode - Unicode support of the URLify'd string
        */
        return this.each(function() {
            var prepopulatedField = $(this);

            var populate = function() {
                // Bail if the field's value has been changed by the user
                if (prepopulatedField.data('_changed')) {
                    return;
                }

                var values = [];
                var contains_file_input = false;
                $.each(dependencies, function(i, field) {
                    field = $(field);
                    if (field.val().length > 0) {
                        // Detect file inputs
                        if ((field.prop('tagName') == 'INPUT') && (field.attr('type') == 'file')) {
                            // get the 'files' property for a nice 
                            // filename
                            for (const e of field.prop('files')) { 
                                values.push(e.name);
                                contains_file_input = true;
                            }
                        }
                        else {
                            values.push(field.val());
                        }
                    }
                });
                if (contains_file_input == true) {
                    // Strip the extension
                    // Should work from FORMAT_EXTENSIONS_APP.keys(), 
                    // but tricky, so hardcoded.
                    var b = []
                    for (const e of values) {
                        b.push(e.replace(/\.(bmp|jpg|jpeg|png|gif|tiff|webp|svg)$/i, '')); 
                        // join, incase this is multi-file upload or 
                        // multi-field population
                        prepopulatedField.val(b.join('-'));
                    }
                }
                else {
                    prepopulatedField.val(URLify(values.join(' '), maxLength, allowUnicode));
                }
            };

            prepopulatedField.data('_changed', false);
            prepopulatedField.on('change', function() {
                prepopulatedField.data('_changed', true);
            });

            if (!prepopulatedField.val()) {
                $(dependencies.join(',')).on('keyup change focus', populate);
            }
        });
    };
})(django.jQuery);
