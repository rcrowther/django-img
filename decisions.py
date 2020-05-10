from image.settings import settings

print('decisions')

# methods that negociate with calling opinions and settings to decide
# or gain info for actions.
# These pieces of code do not sit happily in their associated objects,
# with external dependencies. Besides, they are also relatives of user 
# parameters and settings. So they are here. 



def reform_save_info(ifilter, src_format):
    '''
    Gather and choose between configs about how to save filter results.
    Probes into several settings. If present, settings file wins, 
    filter config wins, discovered state. 
    @ifilter instance of a Filter
    '''
    # defaults
    iformat = src_format
    jpeg_quality = settings.reforms.jpeg_quality
    
    # Overrides of output format. Settings first...
    if (settings.reforms.format_override):
        iformat = settings.reforms.format_override

    #,,,but Filter wins.
    if hasattr(ifilter, 'format') and ifilter.format:
        iformat = ifilter.format

    if iformat == 'jpg':
        # Overrides of JPEG compression quality. Filter wins.
        if hasattr(ifilter, 'jpeg_quality') and ifilter.jpeg_quality:
            jpeg_quality = ifilter.jpeg_quality
            
    return {'format': iformat, 'jpeg_quality': jpeg_quality}
    
        
        
def src_should_delete(image, calling_opinion):
    delete = calling_opinion
    
    # Settings can override...
    if (settings.auto_delete):
        delete = True

    #,,,but Model wins.
    if not(image.auto_delete == image.DELETE_UNSET):
        delete = image.delete_policies(image.auto_delete)
            
    return delete
