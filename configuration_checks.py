from django.core.exceptions import ImproperlyConfigured
from pathlib import Path
from image.constants import IMAGE_FORMATS




# These settings checks are used in filters, with the site-wide Django 
# settings, and this apps summary, Settings. So gathered here.

def check_media_subpath(class_name, setting_name, v):
    if (v and (len(v) > 24)):
        raise ImproperlyConfigured(
            "In {}, '{}' value '{}' exceeds 24 chars."
            "Reset or set TRUNCATE_PATHS = False"
            " Path len (in chars): {}".format(
            class_name,
            setting_name,
            v,
            len(v),
        ))     

def check_image_formats(class_name, setting_name, v):
    if (v and (not(v in IMAGE_FORMATS))):
        raise ImproperlyConfigured(
            "In {}, '{}' value '{}' is unrecognised."
            " Recognised image formats: '{}'".format(
            class_name,
            setting_name,
            v,
            "', '".join(IMAGE_FORMATS),
        ))
        

def check_jpeg_quality(class_name, setting_name, v):
    if (v and (v < 1 or v > 100)):
        raise ImproperlyConfigured(
            "In {}, '{}' smust be 1--100."
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        ))    
    
def check_value_range(class_name, setting_name, v, min, max):
    if (v and (v > min or v > max)):
        raise ValueError(
            "In {}, '{}' smust be {}--{}."
            " value: {}".format(
            class_name, 
            setting_name, 
            min,
            max,
            v
        )) 
         
def check_positive(class_name, setting_name, v):
    if (v and (v < 0)):
        raise ValueError(
            "In {}, '{}' must be a positive number."
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        )) 

def check_boolean(class_name, setting_name, v):
    if (v and (not(type(v)==bool))):
        raise ValueError(
            "In {}, '{}' must be a boolean value."
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        ))         

def check_file(class_name, setting_name, v):
    
    if (v and (not(Path(v).is_file()))):
        raise ValueError(
            "In {}, '{}' can not be deetected as an existing file"
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        ))  
