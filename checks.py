from django.core import checks
from image.constants import IMAGE_FORMATS

## This app speccific
def check_filters(**kwargs):
    '''
    Check registered filters with Django static checks framework.
    '''
    from image import registry
    errors = []
    for f in registry.list.values():
        errors.extend(f.check())
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

## General
def check_is_subclass(setting_name, v, base_klass, eid, **kwargs):
    errors = []
    if (not(issubclass(v, base_klass))):
        errors.append(
            checks.Error(
                "''{}' value {} must be a subclass of {}.".format(
                setting_name,
                v,
                base_klass.__name__,
            ),
            id=eid,
        ))
    return errors
    
def check_type(setting_name, v, tpe, eid, **kwargs):
    errors = []
    if (v and (not(type(v)==tpe))):
        errors.append(
            checks.Error(
                "'{}' value '{}' must be type {}.".format(
                setting_name, 
                v,
                tpe
            ),
            id=eid,
        ))
    return errors 

#? or_none
def check_boolean(setting_name, v, eid, **kwargs):
    return check_type(setting_name, v, bool, eid, **kwargs)
    
def check_int(setting_name, v, eid, **kwargs):
    '''
    Does not allow None
    '''
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
    if (int(v) <= 0):
        errors.append(
            checks.Error(
            "'{}' value '{}' must be a positive number.".format(
            setting_name, 
            v
            ),
            id=eid,
        ))
    return errors 


def check_none_or_positive_float(setting_name, v, eid, **kwargs):
    errors = []
    if (v is None):
        return errors
    try:
        if (float(v) <= 0):
            raise TypeError
    except TypeError:    
        errors.append(
            checks.Error(
            "'{}' value '{}' must be None or a positive float.".format(
            setting_name, 
            v
            ),
            id=eid,
        ))
    return errors
             
def check_numeric_range(setting_name, v, imin, imax, eid):
    errors = []
    try:
        if (type(v) != int or v < imin or v > imax):
            raise TypeError
    except TypeError: 
        errors.append(
            checks.Error(
                "'{}' value '{}' must be > {} and < {}.".format(
                setting_name, 
                v,
                imin,
                imax,
                ),
                id=eid,
        ))
    return errors
        
# def check_boolean(setting_name, v, eid, **kwargs):
    # errors = []
    # if (v and (not(type(v)==bool))):
        # errors.append(
            # checks.Error(
            # "'{}' value '{}' must be a boolean.".format(
            # setting_name, 
            # v
            # ),
            # id=eid,
        # ))
    # return errors 


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

    # def _check_available_filelength(cls, **kwargs):
        # '''
        # Does filepath_length allow for filenames?
        # '''
        # errors = []
        # print(str(cls.filepath_length))
        # declared_len = int(cls.filepath_length)
        # path_len =  len(cls.upload_dir)
        # if (declared_len <= path_len):
            # errors.append(
                # Error(
                    # "'filepath_length' must exceed base path length. 'filepath_length' len: {}, 'upload_dir' len: {}".format(
                     # declared_len,
                     # path_len,
                     # ),
                    # id='image_model.E002',
                # )
            # )
        # elif (declared_len <= (path_len + 12)):
            # errors.append(
                # Warning(
                    # "Less than 12 chars avaiable for filenames. 'filepath_length' len: {}, 'upload_dir' len: {}".format(
                     # declared_len,
                     # path_len,
                     # ),
                    # id='image_model.W001',
                # )
            # )
        # return errors
