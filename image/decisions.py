from pathlib import Path
import os
from unidecode import unidecode
from django.utils.functional import cached_property

# methods that negociate with calling opinions and settings to decide
# or gain info for actions.
# These pieces of code do not sit happily in their calling objects. 
# Besides, they are also relative to user parameters and settings. 
# So they are here. 
def reform_save_info(ifilter, src_format, model_args):
    '''
    Gather and choose between configs about how to save filter results.
    Probes into several settings. 
    For output_format, if present, last of discovered state, model 
    setting, filter config. 
    For jpeg_quality, if present, last of default 85, model setting,
    filter config.
    
    ifilter 
        instance of a Filter
    model_args
        args from a an external call, usually attributes from a reform.    
    return
        {output_format, jpeg_quality}
    '''
    # defaults
    iformat = src_format
    
    # Overrides of output format. Model attributes first...
    if (model_args['file_format']):
        iformat = model_args['file_format']
    jpeg_quality = model_args['jpeg_quality']
    
    #,,,but Filter wins.
    if hasattr(ifilter, 'format') and ifilter.format:
        iformat = ifilter.format
    if iformat == 'jpg':
        if hasattr(ifilter, 'jpeg_quality') and ifilter.jpeg_quality:
            jpeg_quality = ifilter.jpeg_quality
    return {'format': iformat, 'jpeg_quality': jpeg_quality}
    
def filename_originals_maxlen(field_file, media_path):
    '''
    Length the settings will allow for filenames.
    '''
    truncate_len = field_file.field.max_length
    full_path = field_file.storage.path(media_path)
    
    # -1 for a connector
    return truncate_len - len(str(full_path)) - 1

def filename_reforms_maxlen(field_file, media_path):
    '''
    Length the settings will allow for filenames.
    '''
    truncate_len = field_file.field.max_length
    full_path = field_file.storage.path(media_path)
    # -1 for a connector
    return truncate_len - len(str(full_path)) - 1
    

def image_save_path(obj, filename):
    '''
    Get the save path from a source filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 

    obj
        An image model (unfinished)
    filename
        any kind of stringlike filename or path. Should have an extension. 
    '''
    # Info from field: length limit, mangling and path-build utilities
    field_file = obj.src
    media_path = obj.upload_dir
            
    # Quote:
    # Return the given string converted to a string that can be used for a clean
    # filename. Remove leading and trailing spaces; convert other spaces to
    # underscores; and remove anything that is not an alphanumeric, dash,
    # underscore, or dot.
    p = Path(field_file.field.storage.get_valid_name(filename))

    # Unidecode in the filename then replace non-ascii 
    # characters in filename with _ , to sidestep issues with filesystem encoding
    decoded_stem = "".join((i if ord(i) < 128 else '_') for i in unidecode(p.stem))  

    # make the end-tag
    tag = p.suffix
    
    # Find maxlen for the filename, then truncate
    # accounting for declared paths and filename extensions
    # https://code.djangoproject.com/ticket/9893
    stem_limit = filename_originals_maxlen(field_file,  media_path) - len(tag)
    stem = decoded_stem[:stem_limit]

    # return the /media relative path.
    return os.path.join(media_path, stem + tag)
    
def reform_save_path(obj, filename, app_namespace, lowercase):
    '''
    Get the save path from a source filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 

    obj
        An image model (unfinished)    
    filename
        any kind of stringlike filename or path. Should have an extension. 
    '''
    # Info from field: length limit, mangling and path-build utilities
    field_file = obj.src
    media_path = obj.upload_dir
    
    # Reform is internal, so we have an internal representation of
    # filename already
    p = Path(filename)        
    src_stem = p.stem
    
    # filterid is a dotted path
    filter_id = obj.filter_id
    
    # Some reduction of the filter_id
    # We loose a little of the id by reducing, but the file saving
    # gear will mangle if there is a clash, so rename affects 
    # no basic functionality. 
    
    # Is the appname requested?
    if (not app_namespace):
        filter_id = filter_id[filter_id.index('.') + 1:]
    else:
        # filter_id will be added to the reform file path, so make it url-like.
        #filter_id = obj.filter_id.lower().replace('.', '_')
        filter_id = filter_id.replace('.', '_')

    # make the end-tag
    # e.g. tag = "-image_thumb.png"
    tag = '-' + filter_id + p.suffix

    # Find maxlen for the filename, then truncate
    # accounting for declared paths and filename extensions
    stem_limit = filename_reforms_maxlen(field_file, media_path) - len(tag)
    stem = src_stem[:stem_limit]        

    # return the /media relative path.
    internal_path = stem + tag
    if (lowercase):
        internal_path = internal_path.lower()
    return os.path.join(media_path, internal_path)
