from django import template
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt
from django.core.exceptions import ImproperlyConfigured
from django.template.base import kwarg_re

#from django.utils.functional import cached_property
#from image.models import Image
from image.shortcuts import get_reform_or_not_found
from image.registry import registry
from image import module_utils

register = template.Library()

def arg_unquote(a, token, arg_name):
    if not (a[0] == a[-1] and a[0] in ('"', "'")):
       raise template.TemplateSyntaxError(
            "image tag {} argument must be in quotes. tag:{{% {} %}} value:{}".format(
            arg_name,
            token.contents,
            a
       ))
       
    return a[1:-1]

def to_kwargs(token, kwlumps):
    kwargs = {}

    # Tag is tokenizing is from strings, and that depends on 
    # quotes for whitespace and separation.
    # However, the result must be quote-stripped for flatattr() to do
    # it's Django-compliant job in ImageNode.
    # (It might be nice to do further parsing on keyword values, to 
    # allow vars and so forth. But in this atmosphere...)   
    for kw in kwlumps:
        match = kwarg_re.match(kw)
        if not match:
            raise template.TemplateSyntaxError("Malformed arguments to image tag. tag:{{% {} %}} kw:{}".format(
               token.contents,
               kw
           ))
        k, v = match.groups()
        if not (v[0] == v[-1] and v[0] in ('"', "'")):
           raise template.TemplateSyntaxError(
               "image tag keyword arguments must be in quotes. tag:{{% {} %}} kw:{}".format(
               token.contents,
               kw
           ))
        kwargs[k] = v[1:-1]

    return kwargs

def get_app_name(context):
    view = context.get('view')

    # 'view' is present on any Django template view, so reasonably
    # safe to look for. In case there is some sly tampering, or edge 
    # usecase, though the message is unhelpful...
    if (not(view)):
        raise ImproperlyConfigured(
            "The template context has no view information to supply an app name"
        )
    return view.__module__.split('.', 1)[0]    

def filter_id_resolve(context, filter_id):
    '''
    Take a module path supplied by the coder, and return in a form
    usuable by the registry. 
    '''
    # NB: filter registry keys remove the 'image_filters' module part.
    # A coder will guess or be told this.
    # Cheap test works unless the coder buries the image_filters' file.
    # in which case, it's reasonable to ask for a full path.
    if (filter_id.find('.') == -1):
        # The path has been abreviated to assume the current app, which
        # must be derived from the context.
        view = context.get('view')

        # 'view' is present on any Django template view, so reasonably
        # safe to look for. In case there is some sly tampering, or edge 
        # usecase, though the message is unhelpful...
        if (not(view)):
            raise ImproperlyConfigured(
                "A short filter reference has been provided, but the template context has no view information to supply a full path. filter_id:{}".format(
                filter_id,
            ))
        app_name = view.__module__.split('.', 1)[0]
        filter_id = app_name + '.' + filter_id
    return filter_id



class ImgFromImageInstanceNode(template.Node):
    def __init__(self, instance, filter_id, kwargs):
        self.instance = instance
        self.filter_id = filter_id      
        self.kwargs = kwargs

    def render(self, context):
        try:
            ifilter = registry(filter_id_resolve(context, self.filter_id))      
            reform = get_reform_or_not_found(self.instance, ifilter)
            attrs = reform.attrs_dict.copy()
            attrs.update(self.kwargs)
            return mark_safe('<img {} />'.format(flatatt(attrs)))
        except template.VariableDoesNotExist:
            return ''


@register.tag(name="imagequery")
def query_tag(parser, token):
    '''
    Lookup an image by query (and filter).
    This is not a prefered method, It only works on the base image 
    model, and if a view has already generated a context with models, 
    it duplicates a database lookup. But it is useful for fixed images 
    and debugging.
    
    If you need to lookup by filepath, it is difficult, you need the
    media-relative filepath, not only the filename e.g.

        {% imagequery image.Image "pk=2" image.Thumb class="test-image" %}
        
    image_model 
        reference to an image model in dotted notation. Must be present 
        and full path e.g. page.Image.
    query
        in quotes
        e.g."pk=3"
    filter_id 
        string module path to a Filter e.g. "image.Format". If 
        the Filter is only named, the app location of the calling view is 
        added e.g. if "Large" is called from a view in 'page', the filter 
        become "page.Large"
     
    kwargs 
        added as attributes to the final tag.
    ''' 
    lumps = token.split_contents()

    if(len(lumps) < 4):
        raise template.TemplateSyntaxError(
            "Imagefromquery tag needs three arguments. tag:{{% {} %}}".format(
                token.contents,
            ))
            
    tag_name = lumps[0]
    model_path = lumps[1]
    query = arg_unquote(lumps[2], token, 'query')
    filter_id = lumps[3]
    kwargs = to_kwargs(token, lumps[4:])
    
    # Too much trouble to get the app, name, needs to do in context, so
    # request full path
    image_model = module_utils.get_image_model(model_path)
    
    # what a faff
    # fail is self.model.DoesNotExist. Which is ok.
    e = query.split('=',1)  
    image_object = image_model.objects.get(**{e[0]: e[1]})
    return ImgFromImageInstanceNode(image_object, filter_id, kwargs)
    

class ImageNode(template.Node):
    def __init__(self, image_obj, filter_id, kwargs):
        self.image = template.Variable(image_obj)
        self.filter_id = filter_id      
        self.kwargs = kwargs
        
    def render(self, context):
        try:
            im = self.image.resolve(context)
            ifilter = registry(filter_id_resolve(context, self.filter_id))      
            reform = get_reform_or_not_found(im, ifilter)
            attrs = reform.attrs_dict.copy()
            attrs.update(self.kwargs)
            return mark_safe('<img {} />'.format(flatatt(attrs)))
        except template.VariableDoesNotExist:
            return ''

                
@register.tag(name="image")
def image_tag(parser, token):
    '''
    Lookup and display an image. 
    Search is by image details, passed in a context, and filter id.
    If a view has already generated a context with models, this is the
    prefered method. The tag will also work for subclasses of the app
    models e.g.

        {% image page.img image.Thumb class="test-image" %}
    
    image_obj 
        reference to an image in the template context (NB: 
        the parameter can handle dotted notation e.g. page.image)
    
    filter_id 
        string module path to a Filter e.g. "image.Format". If 
        the Filter only is named, the app location of the calling view is 
        added e.g. if "Large" is called from a view in 'page', the filter 
        becomes "page.Large"
     
    kwargs 
        Will be added as attribut4es to the final tag.
    ''' 
    lumps = token.split_contents()

    if(len(lumps) < 3):
        raise template.TemplateSyntaxError(
            "Image tag needs two arguments. tag:{{% {} %}}".format(
                token.contents,
            ))
            
    tag_name = lumps[0]
    image_obj = lumps[1]
    filter_id = lumps[2]
    kwargs = to_kwargs(token, lumps[3:])

    return ImageNode(image_obj, filter_id, kwargs)

