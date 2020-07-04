from django.db.models import ForeignKey, OneToOneField, ImageField, FileField
from django.core import checks
from django.db import models
from image import form_fields
from django.core.files.storage import default_storage
from django import forms
from django.template.defaultfilters import filesizeformat
from image import utils
from image.validators import validate_file_size


class FreePathImageField(ImageField):
    '''
    A (model) ImageField that defaults to returning a (form) 
    FreePathImageField.
    FreePathImageField allows on input any length of file path.
    '''
    # We got choices:
    # don't do it
    # get the val after the class is built
    # somehow force the attr build during the build
    def __init__(self, 
        verbose_name=None, 
        name=None, 
        upload_to='', 
        storage=None, 
        max_upload_size=None,
        form_limit_filepath_length = True,
        **kwargs
    ):
        #print('init FreePathImageField')
        #print(str(kwargs))
        #if (hasattr(kwargs, 'max_length') and callable(kwargs['max_length'])):
        #    kwargs['max_length'] = max_length()
        self.form_limit_filepath_length = form_limit_filepath_length
        self.max_upload_size = max_upload_size
        super().__init__(verbose_name=None, name=None, upload_to='', storage=None, **kwargs)

    def deconstruct(self):
        print('deconstruct maxlen:')
        print(str(self.max_length))
        name, path, args, kwargs = super().deconstruct()
        kwargs['max_length'] = self.max_length
        kwargs['form_limit_filepath_length'] = self.form_limit_filepath_length
        kwargs['max_upload_size'] = self.max_upload_size
        return name, path, args, kwargs
        
    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        
        # Check filesize
        # Don't try if no max upload size declared
        if (self.max_upload_size):
            print('self.max_upload_size')
            print(str(self.max_upload_size))
            validate_file_size(self.max_upload_size, value)
        #? validate_image_file_extension

    def contribute_to_class(self, cls, name, private_only=False):
        # This is not contribute to class at all. It is class 
        # contribute to field. That said, Django does this for 
        # verbose names.
        # 
        # Point is, this method is run by the metaclass
        # way before the classes are constructed. And it is run on
        # every class in MRO. So class attributes referenced here
        # influence actions in an imitation of overriding.
        # Which Python cannot otherwise do.  
        super().contribute_to_class(cls, name, private_only=False)
        print('models contribute_to_class')
        print(str(cls))
        print(str(hasattr(cls, 'filepath_length')))
        if hasattr(cls, 'filepath_length') and cls.filepath_length:
            self.max_length = cls.filepath_length
        if hasattr(cls, 'form_limit_filepath_length'):
            self.form_limit_filepath_length = cls.form_limit_filepath_length
        if hasattr(cls, 'max_upload_size'):
            print(str(cls.max_upload_size))
            self.max_upload_size = utils.mb2bytes(cls.max_upload_size)
        
    # def save(self, name, content, save=True):
        # name = self.field.generate_filename(self.instance, name)
        # self.name = self.storage.save(name, content, max_length=self.max_length)
        # setattr(self.instance, self.field.name, self.name)
        # self._committed = True

        # # Save the object because it has changed, unless save is False
        # if save:
            # self.instance.save()
    # save.alters_data = True
    
    # This class exists because I can find no way of overriding this 
    # default on declaration.
    def formfield(self, **kwargs):
        max_length = None
        if (self.form_limit_filepath_length):
            max_length = self.max_length
        return super().formfield(**{
            #'form_class': form_fields.FreePathImageField,
            'form_class': forms.fields.ImageField,
            'max_length': max_length,
            **kwargs,
        })



class ReformFileField(FileField):
    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only=False)
        print('reform models contribute_to_class')
        print(str(cls))
        print(str(hasattr(cls, 'filepath_length')))
        if (
            hasattr(cls, 'image_model') and 
            hasattr(cls.image_model, 'filepath_length') and 
            cls.image_model.filepath_length
        ):
            print(str(cls.image_model.filepath_length))
            self.max_length = cls.image_model.filepath_length 



class ImageRelationFieldMixin():
    auto_delete = False
    
    def _check_relation_model_is_image_model(self):
        # These checks are run in 'show migrations' and 'runmigrations'.
        # By this check, the related model must exist.
        remote_class = self.remote_field.model

        # ...but that attribute may be by lazy string, which means
        # rooting about for a model class
        rel_is_string = isinstance(remote_class, str)
        if (rel_is_string):
            remote_class = self.opts.apps.all_models[remote_class]

        if (not(issubclass(remote_class, AbstractImage))):
            # More rooting about. Fun, huh? 
            model_name = self.remote_field.model if rel_is_string else self.remote_field.model._meta.object_name
            return [
                checks.Error(
                    "ImageSingleField defines a relation with model '%s', which is "
                    "not a subclass of AbstractImage." % model_name,
                    obj=self,
                    id='fields.E300',
                )
            ]
        return []



class ImageManyToOneField(ImageRelationFieldMixin, ForeignKey):
    '''
    A preconfigured ManyToOne model field for Images.

    This is a ForeignKey, so several models can refer to one image.
    It is suitable for referring to images intended as a pool e.g. 
    for gallery use.
    
    The field has some dafaults, which can be overridden,
    - The field is nullable
    - Deletion of the image sets the field to null
    - Deletion of the model will not delete the image 
    - The image can not refer back to the model
    
    auto_delete
        delete image model on deletion of a model with this field.
        Needs to be enabled in signals. Default False.
    '''
    def __init__(self, to, related_query_name=None,
                 limit_choices_to=None, parent_link=False,
                 db_constraint=True, **kwargs):
        if ('auto_delete' in kwargs):
            self.auto_delete = kwargs['auto_delete']

        # not kwrd, set a default
        on_delete = kwargs.get('on_delete', models.SET_NULL)
        kwargs['blank'] = kwargs.get('blank', True) 
        kwargs['null'] = kwargs.get('null', True) 
        related_name = kwargs.get('related_name', '+')           
        to_field = None
        super().__init__(to, on_delete, related_name, related_query_name,
                 limit_choices_to, parent_link, to_field,
                 db_constraint, **kwargs)
                         
    def check(self, **kwargs):
        #NB run after the core checks
        return [
            *super().check(**kwargs),
            *self._check_relation_model_is_image_model(),
            ]
            
            
            

class ImageOneToOneField(ImageRelationFieldMixin, OneToOneField):
    '''
    A preconfigured OneToOne model field for Images.
    
    This is a OneToOneField, so suitable when the model containing the 
    field is locked to one image (which other models can not use) e.g.
    'Sales product' -> 'Product image'.

    The field has some dafaults, which can be overridden,
    - The field is nullable
    - Deletion of the image sets the field to null
    - Deletion of the model deletes the image 
    - The image can not refer back to the model

    auto_delete
        delete image model on deletion of a model with this field.
        Needs to be enabled in signals. Default True
    '''
    auto_delete = True

    def __init__(self, to, **kwargs):
        if ('auto_delete' in kwargs):
            self.auto_delete = kwargs['auto_delete']
            
        # not kwrd, set a default
        on_delete = kwargs.get('on_delete', models.SET_NULL)
        kwargs['blank'] = kwargs.get('blank', True) 
        kwargs['null'] = kwargs.get('null', True) 
        kwargs['related_name'] = kwargs.get('related_name', '+') 
        kwargs['to_field'] = None
        super().__init__(to, on_delete, **kwargs)
        
    def check(self, **kwargs):
        #NB run after the core checks
        return [
            *super().check(**kwargs),
            *self._check_relation_model_is_image_model(),
            ]
