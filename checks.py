from django.core import checks
from image.constants import IMAGE_FORMATS

def check_filters(**kwargs):
    '''
    Check registered filters with Django static checks framework.
    '''
    from image import registry
    errors = []
    for f in registry.list.values():
        errors.extend(f.check())
    return errors
    
def check_is_subclass(klass, base_klass, eid, **kwargs):
    errors = []
    if (not(issubclass(klass, base_klass))):
        errors.append(
            checks.Error(
                "'class' value '%s' must be a subclass of {}.".format(
                 klass.__name__,
                 base_klass.__name__,
                id=eid,
            )
        ))
    return errors    
        
def check_image_format(image_format, eid, **kwargs):
    errors = []
    if (image_format and (not(image_format in IMAGE_FORMATS))):
        errors.append(
            checks.Error(
            "'format' value '{}' is unrecognised."
            " Recognised image formats: '{}'".format(
            image_format,
            "', '".join(IMAGE_FORMATS),
            ),
            id=eid,            
        ))
    return errors  

def check_jpeg_quality(jpeg_quality, eid, **kwargs):
    errors = []
    if (jpeg_quality and (jpeg_quality < 1 or jpeg_quality > 100)):
        errors.append(
            checks.Error(
            "'jpeg_quality' value '{}' must be 1--100.".format(
            jpeg_quality
            ),
            id=eid,
        ))   
    return errors  

def check_jpeg_legible(jpeg_quality, eid, **kwargs):
    errors = []
    if (jpeg_quality and (jpeg_quality < 12)):
        errors.append(
            checks.Warning(
            "'jpeg_quality' value '{}' is very low.".format(
            jpeg_quality
            ),
            id=eid,
        ))   
    return errors 

def check_int(setting_name, v, eid, **kwargs):
    errors = []
    try:
        int(v)
    except TypeError:
        errors.append(
            checks.Error(
            "'{}' value '{}' must be a number.".format(
            setting_name, 
            v
            ),
            id=eid,
        ))
    return errors 
        
def check_positive(setting_name, v, eid, **kwargs):
    errors = check_int(setting_name, v,  eid, **kwargs)
    if (v and (v < 0)):
        errors.append(
            checks.Error(
            "'{}' value '{}' must be a positive number.".format(
            setting_name, 
            v
            ),
            id=eid,
        ))
    return errors 

        
# def check_numeric_range(class_name, setting_name, v, min, max):
    # check_int(class_name, setting_name, v)
    # if (v and (v > min or v > max)):
        # raise ValueError(
            # "In {}, '{}' smust be {}--{}."
            # " value: {}".format(
            # class_name, 
            # setting_name, 
            # min,
            # max,
            # v
        # )) 
        
def check_boolean(setting_name, v, eid, **kwargs):
    errors = []
    if (v and (not(type(v)==bool))):
        errors.append(
            checks.Error(
            "'{}b' value '{}' must be a boolean.".format(
            setting_name, 
            v
            ),
            id=eid,
        ))
    return errors 

# def check_file_exists(setting_name, v, eid, **kwargs):    
    # errors = []
    # if (v and (not(Path(v).is_file()))):
        # errors.append(
            # checks.Error(
            # "'{}' value '{}' can not be deetected as an existing file".format(
            # setting_name, 
            # v
            # ),
            # id=eid,
        # ))
    # return errors 

