from django.db.models import (
    ForeignKey, 
    OneToOneField, 
    ImageField, 
    FileField, 
    SET_NULL
)
from django.core import checks
from image import utils
from image import form_fields


class ImageFileField(ImageField):
    '''
    A (model) ImageField.
    ImageFileField allows any length of file path. It adds some
    extra parameters and associated verification.
    maxd_size
        in bytes
    '''
    # Class mainly exists for contibute_to options, faking real abstract
    # classes. But adds some init vals and it's formfield belongs to 
    # this app
    default_validators = []
    
    def __init__(self, 
        verbose_name=None,
        name=None, 
        accept_formats=None,
        form_limit_filepath_length = True,
        max_size=None,
        **kwargs
    ):
        self.accept_formats = accept_formats
        self.form_limit_filepath_length = form_limit_filepath_length
        self.max_size = max_size
        self.default_validators = []
        super().__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # upload_to and max_length handled by super()
        kwargs['max_size'] = self.max_size
        kwargs['form_limit_filepath_length'] = self.form_limit_filepath_length
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        # This is not contribute to class at all. It is class 
        # contribute to field. That said, Django does this for 
        # verbose names.
        # 
        # Point is, this method is run by the metaclass
        # way before the classes are constructed. And it is run on
        # every class in MRO, from base to subclasses. So class 
        # attributes referenced here can influence actions in an 
        # imitation of overriding. Which Python cannot otherwise do.  
        super().contribute_to_class(cls, name, private_only=False)

        # Since this predates init, and steps from base, we can simply
        # overwrite values
        # Must use hasattr() defence because migration builds 
        # '__fake__' classes
        if (hasattr(cls, 'filepath_length')):
            self.max_length = cls.filepath_length
        if (hasattr(cls, 'form_limit_filepath_length')):
            self.form_limit_filepath_length = cls.form_limit_filepath_length
        if (hasattr(cls, 'max_upload_size')):
            self.max_size = utils.mb2bytes(cls.max_upload_size)
        if (hasattr(cls, 'accept_formats')):
            self.accept_formats = cls.accept_formats
            
    def formfield(self, **kwargs):
        # if max_len is None, the formfield is unlimited length
        max_length = None
        if (self.form_limit_filepath_length):
            max_length = self.max_length
        return super().formfield(**{
            'form_class': form_fields.FreePathImageField,
            'max_length': max_length,
            'max_size': self.max_size,
            'accept_formats' : self.accept_formats,
            **kwargs,
        })



class ReformFileField(FileField):

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['max_length'] = self.max_length
        return name, path, args, kwargs
        
    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only=False)
        if (hasattr(cls, 'image_model') and hasattr(cls.image_model, 'filepath_length')):
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
        on_delete = kwargs.get('on_delete', SET_NULL)
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
        on_delete = kwargs.get('on_delete', SET_NULL)
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
